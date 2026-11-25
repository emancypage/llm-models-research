import argparse
import csv
import json
import random
import statistics
from pathlib import Path

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


def read_model(root):
    data = {}
    for task, (base_path, *_) in TASKS.items():
        limit = {"gsm1024": 1024, "gsm256": 256, "ifeval": 1280}.get(task)
        for arm in ARMS:
            path = root / "quality-20261125" / arm / task
            if arm == "S" and task != "gsm1024":
                path = root / base_path
            elif arm == "D500" and task in ("gsm256", "arc", "mmlu"):
                path = root / base_path.replace("screen/S/", "screen/V-d500/")
            data[task, arm] = read_run(path, task, limit)
    return data


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


def model_comparisons(data):
    comparisons = {}
    for task in TASKS:
        if len(data[task, "S"]) != TASKS[task][3]:
            raise ValueError(f"Incomplete {task} sample")
        for base, candidate in (("S", "D500"), ("S", "KR500"), ("KR500", "D500")):
            comparisons[f"{task}:{candidate}-{base}"] = compare(data[task, base], data[task, candidate])
    for arm in ARMS:
        comparisons[f"{arm}:gsm1024-gsm256"] = compare(data["gsm256", arm], data["gsm1024", arm])
    return comparisons


def main():
    parser = argparse.ArgumentParser(description="Compute the 36 paired quality comparisons.")
    inputs = parser.add_mutually_exclusive_group()
    inputs.add_argument("--items", type=Path, help="Published per-item correctness CSV")
    inputs.add_argument("--work-dir", type=Path, help="Study directory with original lm-eval sample files")
    parser.add_argument("--output", type=Path, help="Write the summary JSON to this path")
    args = parser.parse_args()
    if args.items and not args.output:
        parser.error("--items needs --output")
    work = args.work_dir or Path(__file__).resolve().parents[1]
    data = read_score_table(args.items) if args.items else {c: read_model(work / "eval" / c) for c in MODELS}
    results = {c: model_comparisons(data[c]) for c in MODELS}
    target = args.output or work / "analysis" / "quality-20261125.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(results, indent=2) + "\n")
    temporary.replace(target)


if __name__ == "__main__":
    main()
