"""Rebuild strict IFEval scores from the instruction counts for each prompt."""
import argparse
import csv
import json
from math import isclose
from pathlib import Path

import numpy as np


def metric_settings(model):
    return {
        "model": model,
        "max_new_tokens": 1280,
        "primary_metric": "prompt_level_strict_acc",
        "secondary_metric": "inst_level_strict_acc",
        "secondary_aggregation": "passed instructions divided by all instructions",
        "historical_mean_prompt_fraction": "mean of each prompt's fraction of passed instructions",
    }


def instruction_scores(counts):
    rows = list(counts)
    if not rows or any(n <= 0 or not 0 <= k <= n for k, n in rows):
        raise ValueError("Invalid or missing IFEval instruction counts")
    passed = sum(k for k, _ in rows)
    total = sum(n for _, n in rows)
    return {
        "secondary": passed / total,
        "instructions_passed": passed,
        "instructions_total": total,
        "historical_mean_prompt_fraction": float(np.mean([k / n for k, n in rows])),
    }


def from_items(directory, model):
    cap = json.loads((directory / "capability-summary.json").read_text())
    primary = json.loads((directory / "per-item-correctness.json").read_text())
    arms = list(cap["arms"])
    counts = {arm: {} for arm in arms}
    with (directory / "ifeval-items.csv").open(newline="") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames != ["doc_id", "instructions", *arms]:
            raise ValueError(f"{directory}: unexpected IFEval columns")
        for row in reader:
            item = f"ifeval:{int(row['doc_id'])}"
            total = int(row["instructions"])
            for arm in arms:
                passed = int(row[arm])
                if item in counts[arm] or (passed == total) != primary[f"{arm}/ifeval"][item]:
                    raise ValueError(f"{arm}/{item}: duplicate or inconsistent prompt score")
                counts[arm][item] = (passed, total)
    for arm, items in counts.items():
        entry = cap["arms"][arm]["ifeval"]
        expected = primary[f"{arm}/ifeval"]
        if (items.keys() != expected.keys() or len(items) != entry["n"]
                or not isclose(sum(expected.values()) / len(items), entry["primary"])):
            raise ValueError(f"{arm}: prompt items differ from the capability summary")
        entry.update(instruction_scores(items.values()))
    cap["settings"]["ifeval"] = metric_settings(model)
    return cap


def encoded(path, value):
    original = path.read_text()
    indent = len(original.splitlines()[1]) - len(original.splitlines()[1].lstrip())
    return json.dumps(value, indent=indent, ensure_ascii=False, allow_nan=False) + ("\n" if original.endswith("\n") else "")


def save_outputs(outputs, check):
    stale = [path for path, content in outputs.items() if path.read_text() != content]
    if check and stale:
        raise SystemExit("Out of date: " + ", ".join(map(str, stale)))
    for path in stale:
        path.write_text(outputs[path])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="Directory containing the scored items and capability summary")
    parser.add_argument("--model", required=True, help="Checkpoint ID")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    path = args.directory / "capability-summary.json"
    save_outputs({path: encoded(path, from_items(args.directory, args.model))}, args.check)
