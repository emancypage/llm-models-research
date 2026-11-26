import argparse
import csv
import json
import random
import statistics
from pathlib import Path
from tempfile import NamedTemporaryFile

from quality_followup_check import TASKS, read_run


def compare(base, candidate):
    if base.keys() != candidate.keys() or any(base[k][0] != candidate[k][0] for k in base):
        raise ValueError("Comparison samples do not match")
    n = len(base)
    gains = sum(candidate[k][1] > base[k][1] for k in base)
    losses = sum(candidate[k][1] < base[k][1] for k in base)
    rng = random.Random(42)
    deltas = []
    for _ in range(10_000):
        # Resampling the three possible paired score differences is an item bootstrap.
        up = rng.binomialvariate(n, gains / n)
        down = rng.binomialvariate(n - up, losses / (n - gains)) if gains < n else 0
        deltas.append(100 * (up - down) / n)
    percentiles = statistics.quantiles(deltas, n=1000, method="inclusive")
    return {
        "items": n, "baseline_correct": sum(v[1] for v in base.values()),
        "candidate_correct": sum(v[1] for v in candidate.values()),
        "wrong_to_right": gains, "right_to_wrong": losses,
        "difference_pp": 100 * (gains - losses) / n,
        "ci95_pp": [percentiles[24], percentiles[974]],
    }


MODELS = ("l8", "q7")
ARMS = ("S", "D500", "KR500")


def run_path(arm, task):
    base = Path(TASKS[task][0])
    if arm == "S" and task != "gsm1024":
        return base
    if arm == "D500" and task in ("gsm256", "arc", "mmlu"):
        return Path("screen/V-d500") / base.name
    return Path("quality-20261125") / arm / task


def read_model(root):
    return {(task, arm): read_run(root / run_path(arm, task), task, LIMITS.get(task))
            for task in TASKS for arm in ARMS}


def read_score_table(path):
    data = {code: {(task, arm): {} for task in TASKS for arm in ARMS} for code in MODELS}
    with path.open(newline="") as stream:
        for row in csv.DictReader(stream):
            model = data[row["model"]]
            task = row["test"]
            item = (row["subject"], int(row["doc_id"]))
            for arm in ARMS:
                samples = model[task, arm]
                if item in samples or row[arm] not in ("0", "1"):
                    raise ValueError(f"Invalid or duplicate score: {row['model']} {task} {item} {arm}")
                samples[item] = (item, int(row[arm]))
    return data


MODEL_IDS = {"q1": "Qwen/Qwen2.5-1.5B-Instruct", "l8": "meta-llama/Llama-3.1-8B-Instruct", "q7": "Qwen/Qwen2.5-7B-Instruct"}
LIMITS = {"gsm256": 256, "gsm1024": 1024, "ifeval": 1280}
TASK_NAMES = {"gsm256": "gsm8k", "gsm1024": "gsm8k", "ifeval": "ifeval", "arc": "arc_challenge", "mmlu": "mmlu"}
LABELS = {"gsm256": "GSM8K · 256 tokens", "gsm1024": "GSM8K · 1024 tokens", "ifeval": "IFEval · strict prompt, 1280 tokens",
          "mmlu": "MMLU · general knowledge", "arc": "ARC-Challenge · reasoning"}
VERSIONS = {"S": "Original", "D500": "Selected", "KR500": "Random"}
PAIRS = (("S", "D500"), ("S", "KR500"), ("KR500", "D500"))


def model_comparisons(code, data):
    comparisons = {}

    def record(key, base_arm, base_task, candidate_arm, candidate_task):
        _, row_filter, metric, _ = TASKS[base_task]
        scores = compare(data[base_task, base_arm], data[candidate_task, candidate_arm])
        scores.update(model=MODEL_IDS[code], task=TASK_NAMES[base_task], scoring_rule=f"{metric},{row_filter}",
                      baseline={"variant": base_arm, "max_new_tokens": LIMITS.get(base_task)},
                      candidate={"variant": candidate_arm, "max_new_tokens": LIMITS.get(candidate_task)})
        comparisons[key] = scores

    for task in TASKS:
        if len(data[task, "S"]) != TASKS[task][3]:
            raise ValueError(f"Incomplete {task} sample")
        for base, candidate in PAIRS:
            record(f"{task}:{candidate}-{base}", base, task, candidate, task)
    for arm in ARMS:
        record(f"{arm}:gsm1024-gsm256", arm, "gsm256", arm, "gsm1024")
    return comparisons


def signed(value):
    return f"{value:+.2f}".replace("-", "−") if value else "0"


def interval(row):
    lo, hi = row["ci95_pp"]
    return f"{signed(row['difference_pp'])} [{signed(lo)} … {signed(hi)}]"


def table(headers, rows):
    lines = [headers, ["---", *(["---:"] * (len(headers) - 1))], *rows]
    return "\n".join("| " + " | ".join(map(str, row)) + " |" for row in lines)


def score_tables(comparisons):
    counts, deltas = [], []
    for task, label in LABELS.items():
        edited, random, between = [comparisons[f"{task}:{b}-{a}"] for a, b in PAIRS]
        counts.append([label, edited["items"], edited["baseline_correct"], edited["candidate_correct"], random["candidate_correct"]])
        deltas.append([label, interval(edited), interval(random), interval(between)])
    return (table(["Test", "Items", *VERSIONS.values()], counts) + "\n\n"
            + table(["Test", "Selected − original", "Random − original", "Selected − random"], deltas))


def quality_sections(results):
    limits = []
    for code, name in (("l8", "Llama"), ("q7", "Qwen")):
        for arm, label in VERSIONS.items():
            row = results[code][f"{arm}:gsm1024-gsm256"]
            limits.append([name, label, row["wrong_to_right"], row["right_to_wrong"], interval(row)])
    qwen = [results["q7"][f"{task}:D500-S"] for task in ("gsm256", "gsm1024")]
    size = qwen[0]["items"]
    clauses = [f"{x['baseline_correct']} to {x['candidate_correct']} ({signed(x['difference_pp'])} pp) "
               f"at {x['candidate']['max_new_tokens']} tokens" for x in qwen]
    summary = (f"On the same {size} GSM8K problems, Qwen2.5-7B went from " + clauses[0] + " and from " + clauses[1]
               + " after the selected 500-entry edit.")
    if all(x["ci95_pp"][0] <= 0 <= x["ci95_pp"][1] for x in qwen):
        summary += " Both paired 95% intervals include zero. This sample gives no clear evidence that the edit changed Qwen’s math score."
    return {"qwen-math": summary, "scores-l8": score_tables(results["l8"]), "scores-q7": score_tables(results["q7"]),
            "limits": table(["Model", "Version", "Wrong → correct", "Correct → wrong", "1024 − 256 (pp)"], limits)}


def render_report(text, results):
    for name, content in quality_sections(results).items():
        start, end = f"<!-- quality:{name} -->", f"<!-- /quality:{name} -->"
        if text.count(start) != 1 or text.count(end) != 1:
            raise ValueError(f"Missing or duplicate quality report markers for {name}")
        before, block = text.split(start)
        _, after = block.split(end)
        text = f"{before}{start}\n{content}\n{end}{after}"
    return text


def update_capabilities(native, results):
    for code, comparisons in results.items():
        for task in TASKS:
            for arm in ARMS:
                path = run_path(arm, task)
                if path.parts[0] == "quality-20261125":
                    name = path.as_posix()
                elif path.parts[0] == "screen":
                    name = "screen-" + path.parts[1]
                else:
                    name = path.parts[0]
                key = "KR500-S" if arm == "KR500" else "D500-S"
                row = comparisons[f"{task}:{key}"]
                correct = row["baseline_correct" if arm == "S" else "candidate_correct"]
                entry = native[f"{code}/{name}"][row["task"]]
                if row["scoring_rule"] not in entry:
                    raise ValueError(f"Missing native score for {code}/{name}/{task}")
                entry[row["scoring_rule"]] = correct / row["items"]
    return native


def k1_instruction_outputs(data_dir, native):
    from ifeval_scores import encoded, from_items

    outputs = {}
    for code, model in MODEL_IDS.items():
        directory = data_dir / "analysis" / f"multi-{code}"
        cap, _ = from_items(directory, model)
        path = directory / "capability-summary.json"
        outputs[path] = encoded(path, cap)
        for arm, scores in cap["arms"].items():
            target = native[f"{code}/{arm}"]["ifeval"]
            target["inst_level_strict_acc,none"] = scores["ifeval"]["secondary"]
    return outputs


def main():
    parser = argparse.ArgumentParser(description="Compute the 36 paired quality comparisons.")
    inputs = parser.add_mutually_exclusive_group()
    inputs.add_argument("--items", type=Path, help="Published per-item correctness CSV")
    inputs.add_argument("--work-dir", type=Path, help="Study directory with original lm-eval sample files")
    inputs.add_argument("--publication", type=Path, help="Study report directory with data/ and results.md")
    parser.add_argument("--output", type=Path, help="Write a standalone summary JSON to this path")
    parser.add_argument("--check", action="store_true", help="Check the publication without modifying it")
    args = parser.parse_args()
    if args.items and not args.output:
        parser.error("--items needs --output")
    if (args.check and not args.publication) or (args.publication and args.output):
        parser.error("--check requires --publication, which writes to the study’s own paths")
    work = args.work_dir or Path(__file__).resolve().parents[1]
    items = args.publication / "data/quality-items.csv" if args.publication else args.items
    data = read_score_table(items) if items else {code: read_model(work / "eval" / code) for code in MODELS}
    results = {code: model_comparisons(code, data[code]) for code in MODELS}
    target = (args.publication / "data/quality-paired.json" if args.publication else
              args.output or work / "analysis/quality-20261125.json")
    outputs = {target: json.dumps(results, indent=2) + "\n"}
    if args.publication:
        native_path = args.publication / "data/capabilities.json"
        native = update_capabilities(json.loads(native_path.read_text()), results)
        outputs.update(k1_instruction_outputs(args.publication / "data", native))
        outputs[native_path] = json.dumps(native, indent=1, ensure_ascii=False) + "\n"
        report_path = args.publication / "results.md"
        outputs[report_path] = render_report(report_path.read_text(), results)
    stale = [path for path, content in outputs.items() if not path.exists() or path.read_text() != content]
    if args.check and stale:
        raise SystemExit("Out of date: " + ", ".join(map(str, stale)))
    for path in stale:
        path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile("w", dir=path.parent, delete=False) as temporary:
            temporary.write(outputs[path])
        temporary_path = Path(temporary.name)
        temporary_path.chmod(path.stat().st_mode & 0o777 if path.exists() else 0o644)
        temporary_path.replace(path)


if __name__ == "__main__":
    main()
