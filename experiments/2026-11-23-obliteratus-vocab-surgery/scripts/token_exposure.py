"""Post hoc analysis after closeout (26 November 2026, exploratory). CPU only."""

import argparse
import csv
import hashlib
import io
import json
import re
import unicodedata
from collections import Counter
from importlib.metadata import version
from pathlib import Path

from quality_followup_check import TASKS
from quality_followup_scores import read_score_table, run_path


STUDY = "2026-11-23-obliteratus-vocab-surgery"
HERE = Path(__file__).resolve().parent
PUBLICATION = HERE.parents[2] / "reports" / STUDY
CONFIGS = HERE.parent / "configs"
ARMS = ("D500", "KR500")
REVIEW_DIGITS = {"00", "26", "36", "64", "75"}
MODELS = {"l8": "llama-3.1-8b-instruct-pad", "q7": "qwen2.5-7b-instruct"}
REVISIONS = {"l8": "0e9e39f249a16976918f6564b8830bc894c89659", "q7": "a09a35458c702b33eeacc393d103063234e8bc28"}
REFERENCE_SHA256 = "3730d312f6e3440559ace48831e51066acaca737f6eabec99bccb9e4b3c39d14"
STATUS = "Post hoc analysis after closeout (26 November 2026, exploratory)."
CHOICE_FIELDS = ("model", "task", "subject", "doc_id", "gold", "S", "D500", "KR500", "D500_exposed", "KR500_exposed")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def json_text(value):
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def categories(text):
    stripped = text.strip()
    return {
        "digits": bool(stripped) and stripped.isascii() and stripped.isdecimal(),
        "contains_ascii_digit": any("0" <= c <= "9" for c in text),
        "answer_letters_trimmed": stripped in {"A", "B", "C", "D"},
        "punctuation": bool(stripped) and all(unicodedata.category(c).startswith("P") for c in stripped),
        "punctuation_or_symbols": bool(stripped) and all(unicodedata.category(c)[0] in "PS" and c != "\ufffd" for c in stripped),
        "whitespace": bool(text) and text.isspace(),
        "contains_newline": "\n" in text,
        "two_characters_or_fewer": len(text) <= 2,
        "alphabetic_word_or_piece": stripped.isalpha(),
    }


def source_ids(model, arm):
    ops = load_json(CONFIGS / f"{arm.lower()}-{model}.json")["operations"]
    ids = {op["source_id"] for op in ops}
    if len(ids) != 500 or len(ops) != 500 or any(op["input_alpha"] != 0 or op["output_scale"] != 0.1 for op in ops):
        raise ValueError(f"Unexpected output-only edit: {model} {arm}")
    return ids


def raw_samples(path, task, count):
    _, wanted_filter, metric, _ = TASKS[task]
    items = {}
    results = list(path.rglob("results_*.json"))
    if len(results) != 1:
        raise ValueError(f"Expected one lm-eval result: {path}")
    if task.startswith("gsm"):
        kwargs = load_json(results[0])["configs"]["gsm8k"]["generation_kwargs"]
        if kwargs.get("max_gen_toks", 256) != int(task[3:]):
            raise ValueError(f"Wrong answer limit: {path}")
    for file in sorted(path.rglob("samples_*.jsonl")):
        subject = file.stem.removeprefix("samples_").rsplit("_", 1)[0]
        with file.open(encoding="utf-8") as stream:
            for line in stream:
                row = json.loads(line)
                if row["filter"] != wanted_filter:
                    continue
                key = (subject, row["doc_id"])
                if key in items or row[metric] not in (0, 1):
                    raise ValueError(f"Duplicate item or invalid score: {subject} {key}")
                items[key] = row
    if len(items) != count:
        raise ValueError(f"{path}: {len(items)} scored items, expected {count}")
    return items


def paired(base, other):
    return all(base[name] == other[name] for name in ("doc_hash", "prompt_hash", "target_hash"))


def encoded(tokenizer, text):
    return tokenizer.encode(text, add_special_tokens=False)


def choice_tokens(tokenizer, arguments):
    options = [arguments[f"gen_args_{i}"] for i in range(len(arguments))]
    context = options[0]["arg_0"]
    if any(option["arg_0"] != context for option in options):
        raise ValueError("Choices have different contexts")
    prefix = context.rstrip()
    prefix_ids = encoded(tokenizer, prefix)
    ids = []
    for option in options:
        whole = encoded(tokenizer, context + option["arg_1"])
        if whole[:len(prefix_ids)] != prefix_ids or len(whole) == len(prefix_ids):
            raise ValueError("Ambiguous lm-eval continuation boundary")
        ids.append(whole[len(prefix_ids):])
    return ids


def choice_prediction(row, task):
    lengths = [len(t) for t in row["doc"]["choices"]["text"]] if task == "arc" else [1] * 4
    scores = [float(x[0]) for x in row["filtered_resps"]]
    if len(scores) != len(lengths) or not all(lengths):
        raise ValueError("Invalid multiple-choice scores")
    return max(range(len(scores)), key=lambda i: scores[i] / lengths[i])


def classified_tokens(tokenizer, model):
    return {arm: {str(i): tokenizer.decode([i], skip_special_tokens=False, clean_up_tokenization_spaces=False)
                  for i in sorted(source_ids(model, arm))} for arm in ARMS}


def counts_in(tokens, selected):
    return {str(i): n for i, n in Counter(tokens).items() if i in selected}


def reference_exposure(parts, selected, digits):
    flags = {}
    for part, ids in parts.items():
        hits = sorted(ids & selected)
        flags[part + "_source_ids"] = hits
        flags[part + "_any"] = bool(hits)
        flags[part + "_digits"] = bool(ids & digits)
    return flags


def study_runs(eval_dir, scores, task):
    _, _, metric, total = TASKS[task]
    runs = {arm: raw_samples(eval_dir / run_path(arm, task), task, total) for arm in ("S", *ARMS)}
    keys = scores[task, "S"].keys()
    for arm, run in runs.items():
        if run.keys() != keys:
            raise ValueError(f"Sample IDs differ from the publication: {eval_dir} {task} {arm}")
        for key, row in run.items():
            if not paired(runs["S"][key], row) or row[metric] != scores[task, arm][key][1]:
                raise ValueError(f"Unpaired or different score: {eval_dir} {task} {arm} {key}")
    return runs


def gsm_observations(model, tokenizer, runs, short_runs, golds, sets, digit_sets):
    items, examples = [], {}
    for key, stock in sorted(runs["S"].items()):
        doc_id = key[1]
        gold = golds[doc_id]
        for group in (runs, short_runs):
            for arm in ("S", *ARMS):
                row = group[arm][key]
                if row["doc"] != gold or row["target"] != gold["answer"] or not paired(stock, row):
                    raise ValueError(f"Reference, prompt or target differs across runs: {model} {key}")
        solution = gold["answer"]
        _, marker, final = solution.rpartition("####")
        if not marker or not final.strip():
            raise ValueError(f"Missing reference answer: {key}")
        refs = {"solution": set(encoded(tokenizer, solution)), "final": set(encoded(tokenizer, final.strip()))}
        outputs = {}
        for limit, group in ((256, short_runs), (1024, runs)):
            outputs[limit] = {arm: encoded(tokenizer, group[arm][key]["resps"][0][0]) for arm in ("S", *ARMS)}
        for arm, selected in sets.items():
            item = {"model": model, "arm": arm, "doc_id": doc_id, "final_answer": final.strip()}
            item.update(reference_exposure(refs, selected, digit_sets[arm]))
            for limit, ids in outputs.items():
                item[f"original_source_counts_{limit}"] = counts_in(ids["S"], selected)
                item[f"edited_source_counts_{limit}"] = counts_in(ids[arm], selected)
            items.append(item)
        if model == "l8" and doc_id in (5, 17):
            original_and_edited = {a: runs[a][key] for a in ("S", "D500")}
            examples[str(doc_id)] = {
                "reference_final": final.strip(),
                "extracted": {a: row["filtered_resps"][0] for a, row in original_and_edited.items()},
                "numerals_in_output": {a: sorted(set(re.findall(r"[0-9]+(?:,[0-9]{3})*", row["resps"][0][0])))
                                       for a, row in original_and_edited.items()},
            }
    return items, examples


def extract(publication, work, reference):
    from transformers import AutoTokenizer

    if digest(reference) != REFERENCE_SHA256:
        raise ValueError("Unexpected GSM8K test.jsonl revision")
    golds = [json.loads(line) for line in reference.read_text(encoding="utf-8").splitlines()]
    scores = read_score_table(publication / "data/quality-items.csv")
    provenance = {"analysis": STATUS, "gsm8k_test_jsonl_sha256": digest(reference),
                  "software": {pkg: version(pkg) for pkg in ("transformers", "tokenizers")}, "models": {}}
    inventory, gsm, choices, repeats, examples = {}, [], [], [], {}
    for model, folder in MODELS.items():
        model_dir = work / "models" / folder
        tokenizer = AutoTokenizer.from_pretrained(model_dir, local_files_only=True)
        inventory[model] = classified_tokens(tokenizer, model)
        sets = {arm: source_ids(model, arm) for arm in ARMS}
        digit_sets = {arm: {int(i) for i, t in inventory[model][arm].items() if categories(t)["digits"]} for arm in ARMS}
        info = {"checkpoint_revision": REVISIONS[model], "tokenizer_sha256": digest(model_dir / "tokenizer.json"),
                "tokenizer_config_sha256": digest(model_dir / "tokenizer_config.json"), "mmlu_letter_ids": {},
                "config_sha256": {arm: digest(CONFIGS / f"{arm.lower()}-{model}.json") for arm in ARMS}}
        provenance["models"][model] = info
        eval_dir = work / "eval" / model
        short_runs = study_runs(eval_dir, scores[model], "gsm256")
        items, cases = gsm_observations(model, tokenizer, study_runs(eval_dir, scores[model], "gsm1024"),
                                        short_runs, golds, sets, digit_sets)
        gsm.extend(items)
        examples.update(cases)
        for task in ("mmlu", "arc"):
            metric = TASKS[task][2]
            runs = study_runs(eval_dir, scores[model], task)
            for key, stock in sorted(runs["S"].items()):
                subject, doc_id = key
                rows = {arm: run[key] for arm, run in runs.items()}
                if any(row["arguments"] != stock["arguments"] for row in rows.values()):
                    raise ValueError(f"Different multiple-choice inputs: {key}")
                token_ids = choice_tokens(tokenizer, stock["arguments"])
                gold_index = int(stock["target"])
                item = {"model": model, "task": task, "subject": subject, "doc_id": doc_id, "gold": gold_index}
                for arm, row in rows.items():
                    pred = choice_prediction(row, task)
                    if int(pred == gold_index) != row[metric]:
                        raise ValueError(f"Choice scores disagree with logged {metric}: {model} {task} {key}")
                    item[arm] = pred
                for arm, selected in sets.items():
                    item[arm + "_exposed"] = "".join("1" if selected.intersection(ids) else "0" for ids in token_ids)
                if task == "mmlu":
                    letters = [stock["arguments"][f"gen_args_{i}"]["arg_1"] for i in range(len(token_ids))]
                    if letters != [" A", " B", " C", " D"] or any(len(ids) != 1 for ids in token_ids):
                        raise ValueError("MMLU is not a four-single-token test")
                    actual_ids = {letter: ids[0] for letter, ids in zip(letters, token_ids)}
                    if info["mmlu_letter_ids"] and actual_ids != info["mmlu_letter_ids"]:
                        raise ValueError("MMLU answer IDs vary across contexts")
                    info["mmlu_letter_ids"] = actual_ids
                choices.append(item)
        repeat = raw_samples(eval_dir / "S-repeat/gsm8k", "gsm256", 200)
        if set(repeat) != {("gsm8k", i) for i in range(200)}:
            raise ValueError("Unexpected repeat subset")
        for key in sorted(repeat):
            s, r = short_runs["S"][key], repeat[key]
            if not paired(s, r) or s["exact_match"] != scores[model]["gsm256", "S"][key][1]:
                raise ValueError(f"Unpaired repeat: {model} {key}")
            repeats.append({"model": model, "doc_id": key[1], "S": int(s["exact_match"]), "repeat": int(r["exact_match"])})
    return inventory, gsm, choices, repeats, examples, provenance


def empty_group():
    return {"items": 0, "original_correct": 0, "edited_correct": 0, "losses": 0, "gains": 0}


def record(groups, name, stock, edited):
    g = groups.setdefault(name, empty_group())
    g["items"] += 1
    g["original_correct"] += stock
    g["edited_correct"] += edited
    g["losses"] += stock > edited
    g["gains"] += edited > stock


def gsm_groups(rows, scores, arm, selected, digit_ids, review_ids, limit):
    groups = {}
    source_counts = {side: Counter() for side in ("original", "edited")}
    with_any = Counter()
    with_digits = Counter()
    kinds = ["any", "digits"]
    if review_ids:
        kinds.append("review_five")
    for part in ("solution", "final"):
        for kind in kinds:
            for status in ("exposed", "unexposed"):
                groups[f"{part}_{kind}_{status}"] = empty_group()
    task = f"gsm{limit}"
    for row in rows:
        key = ("gsm8k", row["doc_id"])
        stock, edited = (scores[task, a][key][1] for a in ("S", arm))
        record(groups, "all", stock, edited)
        for part in ("solution", "final"):
            ids = set(row[part + "_source_ids"])
            if not ids <= selected:
                raise ValueError("Reference exposure contains a non-source ID")
            flags = {"any": bool(ids), "digits": bool(ids & digit_ids)}
            if any(row[f"{part}_{kind}"] != exposed for kind, exposed in flags.items()):
                raise ValueError("Inconsistent exposure flag")
            if review_ids:
                flags["review_five"] = bool(ids & review_ids)
            for kind, exposed in flags.items():
                name = f"{part}_{kind}_{'exposed' if exposed else 'unexposed'}"
                record(groups, name, stock, edited)
        for side, counts in source_counts.items():
            hits = {int(i): count for i, count in row[f"{side}_source_counts_{limit}"].items()}
            if not set(hits) <= selected or any(n < 1 for n in hits.values()):
                raise ValueError("Invalid output token count")
            counts.update(hits)
            with_any[side] += bool(hits)
            with_digits[side] += bool(set(hits) & digit_ids)
    emissions = {side: {"with_any": with_any[side], "with_digits": with_digits[side],
                        "occurrences": sum(counts.values()), "distinct_source_ids": len(counts),
                        "source_occurrences_by_id": dict(sorted(counts.items())),
                        "digit_occurrences_by_id": {i: counts[i] for i in sorted(digit_ids)}}
                 for side, counts in source_counts.items()}
    return groups, emissions


def choice_groups(rows, scores, arm, task, letters):
    groups = {}
    for name in ("gold_exposed", "gold_unexposed", "gold_and_distractor", "gold_and_no_distractor",
                 "no_gold_and_distractor", "no_gold_and_no_distractor", "loss_to_exposed_option", "loss_to_unexposed_option"):
        groups[name] = empty_group()
    seen = set()
    changed = 0
    for row in rows:
        key = (row["subject"], int(row["doc_id"]))
        if key in seen:
            raise ValueError("Duplicate choice observation")
        seen.add(key)
        gold, baseline, choice = (int(row[k]) for k in ("gold", "S", arm))
        mask = row[arm + "_exposed"]
        if set(mask) - {"0", "1"} or not all(0 <= idx < len(mask) for idx in (gold, baseline, choice)):
            raise ValueError("Invalid choice exposure data")
        s, e = int(gold == baseline), int(gold == choice)
        if s != scores[task, "S"][key][1] or e != scores[task, arm][key][1]:
            raise ValueError("Choice predictions differ from published scores")
        changed += baseline != choice
        gold_hit = mask[gold] == "1"
        distractor_hit = "1" in mask[:gold] + mask[gold + 1:]
        record(groups, "all", s, e)
        record(groups, "gold_exposed" if gold_hit else "gold_unexposed", s, e)
        group = ("gold" if gold_hit else "no_gold") + ("_and_distractor" if distractor_hit else "_and_no_distractor")
        record(groups, group, s, e)
        if s and not e:
            record(groups, "loss_to_exposed_option" if mask[choice] == "1" else "loss_to_unexposed_option", s, e)
        if task == "mmlu":
            if mask != "".join("1" if " " + c in letters else "0" for c in "ABCD"):
                raise ValueError("Letter exposures do not match the tokenizer IDs")
            record(groups, "gold_" + "ABCD"[gold], s, e)
    if seen != scores[task, arm].keys():
        raise ValueError(f"Incomplete choice data: {task}")
    groups["changed_predictions"] = changed
    return groups


def summarize(publication, inventory, gsm, choices, repeats, examples, provenance):
    scores = read_score_table(publication / "data/quality-items.csv")
    scope = load_json(publication / "data/scope-checks/quality-restorations.json")
    result = {"analysis": STATUS, "gsm8k_examples": examples, "models": {}}
    for model in MODELS:
        out = result["models"][model] = {}
        letter_ids = provenance["models"][model]["mmlu_letter_ids"]
        for arm in ARMS:
            names = inventory[model][arm]
            selected = source_ids(model, arm)
            if set(map(int, names)) != selected or digest(CONFIGS / f"{arm.lower()}-{model}.json") != provenance["models"][model]["config_sha256"][arm]:
                raise ValueError("Token inventory does not match the published list")
            check = scope[model][arm]
            if not check["ok"] or check["input_rows"] != 0 or check["output_rows"] != 500 or not check["other_tensors_identical"]:
                raise ValueError("Unexpected weight-edit scope")
            digits = {int(i) for i, t in names.items() if categories(t)["digits"]}
            sums = {k: sum(categories(t)[k] for t in names.values()) for k in categories("")}
            letters = {k: v for k, v in letter_ids.items() if v in selected}
            entry = out[arm] = {"category_counts": sums, "digit_tokens": sorted(names[str(i)] for i in digits),
                                "edited_mmlu_letters": letters}
            review_ids = set()
            if model == "l8" and arm == "D500":
                review_ids = {int(i) for i, name in names.items() if name in REVIEW_DIGITS}
                if len(review_ids) != len(REVIEW_DIGITS):
                    raise ValueError("The five number tokens named in the review are not all present")
                entry["review_five_tokens"] = sorted(REVIEW_DIGITS)
            rows = [r for r in gsm if r["model"] == model and r["arm"] == arm]
            if len(rows) != 400 or {r["doc_id"] for r in rows} != set(range(400)):
                raise ValueError("Incomplete GSM8K exposure data")
            for limit in (256, 1024):
                groups, emissions = gsm_groups(rows, scores[model], arm, selected, digits, review_ids, limit)
                entry[f"gsm{limit}"] = groups
                entry[f"output_{limit}"] = emissions
            for task in ("mmlu", "arc"):
                rows = (r for r in choices if r["model"] == model and r["task"] == task)
                entry[task] = choice_groups(rows, scores[model], arm, task, letters)
        selected_rows = [r for r in gsm if r["model"] == model and r["arm"] == "D500"]
        exposure_sets = {"digits": {r["doc_id"] for r in selected_rows if r["solution_digits"]}}
        if model == "l8":
            five = {int(i) for i, t in inventory[model]["D500"].items() if t in REVIEW_DIGITS}
            exposure_sets["review_five"] = {r["doc_id"] for r in selected_rows if five.intersection(r["solution_source_ids"])}
        rows = [r for r in repeats if r["model"] == model]
        if len(rows) != 200 or {int(r["doc_id"]) for r in rows} != set(range(200)):
            raise ValueError("Incomplete repeat sample")
        groups = out["repeat256"] = {}
        for r in rows:
            key = ("gsm8k", int(r["doc_id"]))
            stock, repeated = int(r["S"]), int(r["repeat"])
            if stock != scores[model]["gsm256", "S"][key][1] or repeated not in (0, 1):
                raise ValueError("Invalid repeat score")
            record(groups, "all", stock, repeated)
            for kind, member_ids in exposure_sets.items():
                group = kind + ("_exposed" if key[1] in member_ids else "_unexposed")
                record(groups, group, stock, repeated)
                record(groups, "D500_" + group, stock, scores[model]["gsm256", "D500"][key][1])
    return result


def markdown_table(headers, rows):
    def line(cells):
        return "| " + " | ".join(str(cell) for cell in cells) + " |"
    return [line(headers), line(["---"] * len(headers)), *(line(row) for row in rows), ""]


def group_counts(group):
    return [group[k] for k in ("items", "original_correct", "losses", "gains")]


def render_tables(summary):
    lists = [(name, arm, summary["models"][code][arm]) for code, name in (("l8", "Llama"), ("q7", "Qwen"))
             for arm in ARMS]
    lines = ["# Token exposure in the quality benchmarks", "", STATUS, "",
             "D500 is the selected list and KR500 is the random list. Each contains 500 output token IDs. "
             "One loss means an originally correct item lost credit. One gain means an originally incorrect item gained credit. "
             "[Methods and file definitions](README.md) · [Machine-readable counts](summary.json)", "",
             "## Categories in each list", ""]
    categories_shown = ("digits", "punctuation", "whitespace", "contains_newline", "two_characters_or_fewer", "alphabetic_word_or_piece")
    rows = [[m, a, e["category_counts"]["answer_letters_trimmed"], ", ".join(k.strip() for k in e["edited_mmlu_letters"]) or "None",
             *(e["category_counts"][k] for k in categories_shown)] for m, a, e in lists]
    lines += markdown_table(["Model", "List", "A–D pieces", "Actual MMLU letters edited", "Digits", "Punctuation",
                             "Whitespace only", "Contains newline", "≤2 characters", "Alphabetic words or pieces"], rows)
    for limit in (1024, 256):
        lines += [f"## GSM8K at {limit} tokens", "",
                  "Each line partitions the same 400 reference answers into two groups. "
                  "Losses can occur only among originally correct items.", ""]
        rows = []
        for model, arm, entry in lists:
            for part, label in (("solution", "Whole solution"), ("final", "Final number")):
                for kind, tokens in (("any", "Any listed ID"), ("digits", "All digit IDs"), ("review_five", "Five review IDs")):
                    groups = entry[f"gsm{limit}"]
                    key = f"{part}_{kind}"
                    if key + "_exposed" in groups:
                        rows.append([model, arm, label, tokens, *group_counts(groups[key + "_exposed"]),
                                     *group_counts(groups[key + "_unexposed"])])
        lines += markdown_table(["Model", "List", "Reference text", "Token group", "Exposed", "Original correct (exposed)",
                                 "Losses (exposed)", "Gains (exposed)", "Unexposed", "Original correct (unexposed)",
                                 "Losses (unexposed)", "Gains (unexposed)"], rows)
    lines += ["## Listed IDs in re-tokenized GSM8K answers", ""]
    rows = []
    for m, a, e in lists:
        for limit in (1024, 256):
            original, edited = (e[f"output_{limit}"][side] for side in ("original", "edited"))
            rows.append([m, a, limit, original["with_any"], edited["with_any"], edited["with_digits"], edited["occurrences"]])
    lines += markdown_table(["Model", "List", "Token limit", "Original answers with a listed ID", "Edited answers with a listed ID",
                             "Edited answers with a listed digit", "Listed occurrences in edited answers"], rows)
    lines += ["## MMLU by correct letter", ""]
    rows = [[m, a, letter, "Yes" if " " + letter in e["edited_mmlu_letters"] else "No",
             *group_counts(e["mmlu"]["gold_" + letter])] for m, a, e in lists for letter in "ABCD"]
    lines += markdown_table(["Model", "List", "Correct letter", "Letter edited", "Items", "Original correct", "Losses", "Gains"], rows)
    lines += ["## ARC-Challenge by correct and incorrect option text", ""]
    rows = []
    for m, a, e in lists:
        for gold in (True, False):
            for distractor in (True, False):
                name = ("gold" if gold else "no_gold") + ("_and_distractor" if distractor else "_and_no_distractor")
                rows.append([m, a, "Yes" if gold else "No", "Yes" if distractor else "No", *group_counts(e["arc"][name])])
    lines += markdown_table(["Model", "List", "Correct option exposed", "Any incorrect option exposed", "Items",
                             "Original correct", "Losses", "Gains"], rows)
    lines += ["## GSM8K original repeat and selected edit at 256 tokens", "",
              "Each row uses the same original run and the same subset of the first 200 questions. "
              "Exposure refers to tokens in the full reference solution.", ""]
    rows = []
    for code, name in (("l8", "Llama"), ("q7", "Qwen")):
        repeat = summary["models"][code]["repeat256"]
        for key, group in repeat.items():
            if key == "all" or key.startswith("D500_"):
                continue
            candidate = repeat["D500_" + key]
            rows.append([name, key.replace("_", " "), *group_counts(group), candidate["losses"], candidate["gains"]])
    lines += markdown_table(["Model", "D500 reference group", "Items", "Original correct", "Repeat losses",
                             "Repeat gains", "D500 losses", "D500 gains"], rows)
    return "\n".join(lines)


def dump_csv(rows, fields):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--publication", type=Path, default=PUBLICATION)
    parser.add_argument("--output", type=Path, help="Destination for derived observations and summary")
    parser.add_argument("--work-dir", type=Path, help="Extract from the original study workspace")
    parser.add_argument("--gsm-reference", type=Path, help="Original public GSM8K test.jsonl")
    parser.add_argument("--check", action="store_true", help="Verify the saved summary; with inputs, also check every observation")
    args = parser.parse_args()
    if bool(args.work_dir) != bool(args.gsm_reference):
        parser.error("--work-dir and --gsm-reference are required together")
    target = args.output or args.publication / "data/analysis/token-exposure"
    files = {}
    if args.work_dir:
        inventory, gsm, choices, repeats, examples, provenance = extract(args.publication, args.work_dir, args.gsm_reference)
        files = {"inventory.json": json_text(inventory), "provenance.json": json_text(provenance),
                 "gsm8k-items.jsonl": "".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in gsm),
                 "choice-items.csv": dump_csv(choices, CHOICE_FIELDS), "repeat-items.csv": dump_csv(repeats, ("model", "doc_id", "S", "repeat")),
                 "examples.json": json_text(examples)}
    else:
        inventory, provenance, examples = (load_json(target / f"{k}.json") for k in ("inventory", "provenance", "examples"))
        gsm = [json.loads(line) for line in (target / "gsm8k-items.jsonl").read_text(encoding="utf-8").splitlines()]
        choices, repeats = (read_csv(target / f"{name}-items.csv") for name in ("choice", "repeat"))
    summary = summarize(args.publication, inventory, gsm, choices, repeats, examples, provenance)
    files["summary.json"] = json_text(summary)
    files["tables.md"] = render_tables(summary)
    if args.check:
        for name, content in files.items():
            if (target / name).read_bytes() != content.encode("utf-8"):
                raise SystemExit(f"Mismatch in {name}")
        print(f"Verified {len(files)} file(s) against published item scores.")
    else:
        target.mkdir(parents=True, exist_ok=True)
        for name, content in files.items():
            (target / name).write_text(content, encoding="utf-8")


if __name__ == "__main__":
    main()
