"""Counterbalance word order and the queried position for each Polish verb lemma."""

from collections import Counter, defaultdict
import hashlib
import json
import subprocess

from obliteratus.concepts.target import ConceptTarget, ExtractionRecipe
from tense_study import SEED, UD, UD_REV, WORK, read_forms, run_study, sample_pairs

OUT = WORK / "tense-v2"
CONCEPT = "user/polish-tense-paired-position"
PREFILL = "\nOdpowiedź: wskazana forma jest w czasie"


def paired_items(forms):
    by_lemma = defaultdict(dict)
    for form in forms:
        by_lemma[form["lemma"]][form["tense"]] = form

    items = []
    for lemma_index, (lemma, pair) in enumerate(by_lemma.items()):
        quartet = []
        for order in (("Past", "Pres"), ("Pres", "Past")):
            first, second = [pair[tense] for tense in order]
            for index, position in enumerate(("pierwsza", "druga")):
                question = (f"Podano dwie formy czasownika: „{first['text']}” i „{second['text']}”. "
                            f"Jaki czas wyraża {position} forma?")
                quartet.append({
                    "id": f"{first['id']}:{second['id']}:{index + 1}",
                    "text": question + PREFILL, "question": question, "lemma": lemma,
                    "lemma_index": lemma_index, "tense": order[index],
                    "order": list(order), "position": index + 1,
                })
        past = [r for r in quartet if r["tense"] == "Past"]
        present = [r for r in quartet if r["tense"] == "Pres"]
        for rows in (past, present):
            if {tuple(r["order"]) for r in rows} != {("Past", "Pres"), ("Pres", "Past")}:
                raise ValueError(f"Unbalanced presentation order for {lemma}")
            if sorted(r["position"] for r in rows) != [1, 2]:
                raise ValueError(f"Unbalanced position for {lemma}")
        if Counter(w for r in past for w in r["text"].split()) != Counter(w for r in present for w in r["text"].split()):
            raise ValueError(f"Lexical imbalance for {lemma}")
        items.extend(quartet)
    if len({r["text"] for r in items}) != len(items) or len({r["id"] for r in items}) != len(items):
        raise ValueError("Duplicate prompts or record IDs")
    return items


def prepare():
    revision = subprocess.check_output(["git", "-C", str(UD), "rev-parse", "HEAD"], text=True).strip()
    if revision != UD_REV:
        raise ValueError("Corpus revision mismatch")
    holdout_forms = sample_pairs(read_forms("test"), 32)
    fit_forms = sample_pairs(read_forms("train"), 64, {r["lemma"] for r in holdout_forms})
    if {r["text"] for r in fit_forms} & {r["text"] for r in holdout_forms}:
        raise ValueError("Overlapping attested forms across fit and holdout")
    fit = paired_items(fit_forms)
    held = paired_items(holdout_forms)
    past = [r for r in fit if r["tense"] == "Past"]
    present = [r for r in fit if r["tense"] == "Pres"]
    recipe = ExtractionRecipe(method="diff_means", use_chat_template=False,
                              layer_select={"strategy": "cv_auc", "folds": 5, "group_by": "lemma"})
    target = ConceptTarget(
        id=CONCEPT, version="2.0.0", positive=[r["text"] for r in past],
        controls={"present": [r["text"] for r in present]}, records={"positive": past, "control:present": present},
        # This target is constructed from source records, not imported from a ConceptPack.
        # The native exporter derives its identity from id/version. The protocol pins the corpus.
        recipe=recipe,
        caveats=["The task is to identify the tense at a specified position within a pair of verb forms."],
    )
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = {"ud_commit": UD_REV, "seed": SEED, "fit_lemma_pairs": 64, "holdout_lemma_pairs": 32,
                "fit_items": len(fit), "holdout_items": len(held), "fit_per_class": len(past),
                "positions_and_word_orders_balanced_per_lemma": True, "prefill": PREFILL,
                "original_belebele_baseline": "782/900; same checkpoint, dataset revision and scoring",
                "folds": 5, "group_by": "lemma", "outcome": "stop on native gate failure; no override"}
    for name, rows in [("fit", fit), ("holdout", held)]:
        content = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows)
        encoded = content.encode("utf-8")
        manifest[name + "_sha256"] = hashlib.sha256(encoded).hexdigest()
        (OUT / (name + ".jsonl")).write_bytes(encoded)
    return target, held, manifest


if __name__ == "__main__":
    run_study(*prepare(), OUT, after_path=OUT / "belebele-after.json",
              telemetry_method="polish_tense_paired_position_diff_means")
