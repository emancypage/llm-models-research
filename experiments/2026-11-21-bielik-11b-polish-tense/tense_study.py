"""Full OBLITERATUS concept run on attested Polish past/present verb forms."""

from collections import defaultdict
import os
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import torch
from obliteratus import telemetry
from obliteratus.abliterate import AbliterationPipeline
from obliteratus.community import save_contribution, validate_contribution
from obliteratus.concepts.target import ConceptTarget, ExtractionRecipe

from belebele import DATA_REV, run as score_belebele

WORK = Path(os.environ.get("BIELIK_WORK_DIR", "work")).resolve()
UD = WORK / "ud-lfg"
UD_REV = "9a0be46202ce87f0a507f427c52594c863a197e2"
MODEL = "speakleash/Bielik-11B-v2.3-Instruct"
MODEL_REV = "73f5f7fb9a79a4409d02740155a3868c1ff0d2bc"
UPSTREAM_REV = "7678d84196fe6c348dfd01078bbfb50857463647"
SNAPSHOT = WORK / "hf/hub/models--speakleash--Bielik-11B-v2.3-Instruct/snapshots" / MODEL_REV
CONCEPT = "polish-verb-past-vs-present"
OUT = WORK / "tense-v1"
SEED = 20261121


def stable_order(value):
    return hashlib.sha256(f"{SEED}:{value}".encode()).hexdigest()


def read_forms(partition):
    corpus = UD / f"pl_lfg-ud-{partition}.conllu"
    forms = defaultdict(lambda: defaultdict(dict))
    sent_id = None
    for line in corpus.read_text().splitlines():
        if line.startswith("# sent_id = "):
            sent_id = line.removeprefix("# sent_id = ")
            continue
        cols = line.split("\t")
        if len(cols) != 10 or cols[3] != "VERB" or cols[7] != "root":
            continue
        features = set(cols[5].split("|"))
        if not {"Aspect=Imp", "Number=Sing", "VerbForm=Fin", "Voice=Act"} <= features:
            continue
        word, lemma = cols[1].lower(), cols[2].lower()
        if not word.isalpha():
            continue
        for tense in ("Past", "Pres"):
            if f"Tense={tense}" in features:
                forms[lemma][tense].setdefault(word, sent_id)
    return {k: v for k, v in forms.items() if set(v) == {"Past", "Pres"}}


def sample_pairs(bank, size, excluded=()):
    lemmas = sorted(set(bank) - set(excluded), key=stable_order)
    if len(lemmas) < size:
        raise ValueError(f"Insufficient matched verb lemmas: {len(lemmas)}")
    rows = []
    for lemma in lemmas[:size]:
        for tense in ("Past", "Pres"):
            forms = bank[lemma][tense]
            word = min(forms, key=stable_order)
            rows.append({"text": word, "lemma": lemma, "tense": tense, "id": forms[word]})
    return rows


def make_target():
    revision = subprocess.check_output(["git", "-C", str(UD), "rev-parse", "HEAD"], text=True).strip()
    if revision != UD_REV:
        raise ValueError("Unexpected corpus revision")
    held = sample_pairs(read_forms("test"), 32)
    fit = sample_pairs(read_forms("train"), 64, {r["lemma"] for r in held})
    if {r["text"] for r in fit} & {r["text"] for r in held}:
        raise ValueError("A surface form leaked across partitions")
    past = [r for r in fit if r["tense"] == "Past"]
    present = [r for r in fit if r["tense"] == "Pres"]
    digest = hashlib.sha256(json.dumps(fit, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    target = ConceptTarget(
        id=CONCEPT, version="1.0.0", positive=[r["text"] for r in past],
        controls={"present": [r["text"] for r in present]}, records={"positive": past, "control:present": present},
        recipe=ExtractionRecipe(method="diff_means", use_chat_template=False,
                                layer_select={"strategy": "cv_auc", "folds": 5, "group_by": "lemma"}),
        pack_provenance={"source": "UniversalDependencies/UD_Polish-LFG", "source_commit": UD_REV},
        caveats=["Isolated attested verb forms; grammatical endings are part of the contrast."],
    )
    return target, held, {"ud_commit": UD_REV, "fit_sha256": digest,
                          "fit_lemma_pairs": 64, "holdout_lemma_pairs": 32, "seed": SEED}


@torch.inference_mode()
def tense_accuracy(h, held):
    hits = 0
    trials = []
    for n, row in enumerate(held):
        # Reverse label order between lemma pairs, keeping both classes balanced.
        lemma_index = row.get("lemma_index", n // 2)
        order = ("Past", "Pres") if lemma_index % 2 == 0 else ("Pres", "Past")
        names = {"Past": "przeszły", "Pres": "teraźniejszy"}
        question = row.get("question", f"Jaki czas wyraża forma czasownika „{row['text']}”?")
        query = f"{question} A. {names[order[0]]}. B. {names[order[1]]}. Odpowiedz tylko A albo B."
        template = h.tokenizer.apply_chat_template([{"role": "user", "content": query}],
                                                  tokenize=False, add_generation_prompt=True)
        base = h.tokenizer.encode(template, add_special_tokens=False)
        complete = [h.tokenizer.encode(template+c, add_special_tokens=False) for c in "AB"]
        if not all(seq[:-1] == base for seq in complete):
            raise ValueError("Tense labels are not single-token continuations")
        ids = torch.tensor([base], device="cuda")
        scores = h.model(ids, use_cache=False, logits_to_keep=1).logits[0, -1, [seq[-1] for seq in complete]]
        if not torch.isfinite(scores).all():
            raise ValueError("Non-finite tense classification scores")
        prediction = order[int(scores.argmax())]
        hits += prediction == row["tense"]
        trials.append({"source_id": row["id"], "expected": row["tense"], "predicted": prediction})
    return {"correct": hits, "n": len(held), "trials": trials}


def run_study(target, held, manifest, out_dir, *, after_path, telemetry_method):
    target.sample_groups()
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest.update(model=MODEL, model_revision=MODEL_REV, tool_revision=UPSTREAM_REV,
                    concept=target.id, independent_benchmark_revision=DATA_REV,
                    validation="enforce", collateral="Polish Belebele, 900 held-out questions; safety battery not measured")
    (out_dir / "protocol.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    if "--check-data" in sys.argv:
        print(json.dumps(manifest))
        return
    pristine = json.loads((WORK / "belebele/before.json").read_text())
    if pristine["revision"] != DATA_REV or pristine["questions"] != 900:
        raise ValueError("Missing complete pinned Belebele baseline")
    behaviour = {}

    def observe(stage):
        print(stage.stage, stage.status, stage.message, flush=True)
        if stage.stage == "excise" and stage.status == "running":
            # Exercise the native export identity check on the actual validated direction.
            from obliteratus.concepts.runs import run_record
            run_record(pipeline._concept_direction, mode="orthogonalize", parameters={},
                       validation=pipeline.validation_report)
        if stage.stage == "baseline" and stage.status == "running" and "before" not in behaviour:
            behaviour["before"] = tense_accuracy(pipeline.handle, held)
            (out_dir / "heldout-before.json").write_text(json.dumps(behaviour["before"], indent=2) + "\n")
            print("Held-out tense baseline:", behaviour["before"]["correct"], "/", len(held), flush=True)

    held_prompts = {t: [r.get("question", f"Jaki czas wyraża forma „{r['text']}”?") for r in held if r["tense"] == t]
                    for t in ("Past", "Pres")}
    pipeline = AbliterationPipeline(
        model_name=str(SNAPSHOT), output_dir=str(out_dir / "model"), concept=target,
        method="basic", seed=SEED, device="cuda", dtype="float16", trust_remote_code=False,
        gate_mode="enforce", snapshot_enabled=False, skip_collateral=True,
        evaluation_harmful_prompts=held_prompts["Past"], evaluation_harmless_prompts=held_prompts["Pres"],
        on_stage=observe, on_log=lambda s: print(s, flush=True),
    )
    checkpoint = pipeline.run()
    if "before" not in behaviour:
        raise RuntimeError("Pristine tense baseline missing")
    behaviour["after"] = tense_accuracy(pipeline.handle, held)
    (out_dir / "heldout-tense.json").write_text(json.dumps(behaviour, indent=2) + "\n")
    edited = score_belebele(checkpoint, after_path, 8, handle=pipeline.handle)
    counts = {"belebele_before": pristine["correct"], "belebele_after": edited["correct"],
              "tense_before": behaviour["before"]["correct"], "tense_after": behaviour["after"]["correct"]}
    notes = (f"{target.id}; safety not assessed. on premise; {manifest['fit_lemma_pairs']} fit lemma pairs. "
             f"Held-out tense {counts['tense_before']}->{counts['tense_after']}/{len(held)}; "
             f"Belebele PL {counts['belebele_before']}->{counts['belebele_after']}/900. "
             f"Model {MODEL_REV[:8]}, tool {UPSTREAM_REV[:8]}, UD-LFG {UD_REV[:8]}, Belebele {DATA_REV[:8]}.")
    contribution = save_contribution(pipeline, model_name=MODEL, notes=notes,
                                     output_dir=out_dir / "community_results")
    if not validate_contribution(json.loads(contribution.read_text())):
        raise RuntimeError("Invalid native community contribution")
    # Use a concept-specific method label so a neutral linguistic experiment is identifiable on the Hub.
    record = telemetry.BenchmarkRecord(model_id=MODEL, model_family="mistral", model_size_b=11.168796672,
        method=telemetry_method, compute_dtype="float16", dataset="facebook/belebele:pol_Latn",
        n_prompts=900, extra={"model_revision": MODEL_REV, "tool_revision": UPSTREAM_REV,
                              "ud_revision": UD_REV, "belebele_revision": DATA_REV, **counts})
    if not telemetry.log_benchmark(record):
        raise RuntimeError("Failed to persist aggregate telemetry")
    (out_dir / "completed.json").write_text(json.dumps({"contribution": str(contribution), **counts}, indent=2) + "\n")
    print("COMPLETED", contribution, counts, flush=True)


if __name__ == "__main__":
    run_study(*make_target(), OUT, after_path=WORK / "belebele/after.json",
              telemetry_method="concept_polish_tense_diff_means")
