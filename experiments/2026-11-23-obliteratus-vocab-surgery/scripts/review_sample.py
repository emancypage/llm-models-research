"""Blinded manual-review sheet (plan task 0.6).

usage: review_sample.py --report CODE:VERSION:ROLE:REPORT.json [...] --negative 15 --positive 10 --seed 42
                        --prefill TEXT --sheet review/sheet.csv --key review/key.json [--spec runs/spec.json]
Sheet columns: row_id,prompt,prefill,completion,label (random order; no model or version names).
The prefill column holds --prefill for versions SP and VP* and is empty for S and V*.
"""
import argparse
import csv
import json
import random
from pathlib import Path

LABELS = ("odmowa", "zgoda", "inne")


def has_prefill(version):
    return version.split("-")[0] in ("SP", "VP")


def build(entries, negative, positive, seed, prefill):
    """entries: [(code, version, role, report, rows)]; returns (sheet rows, key)."""
    picked, versions = [], {}
    for code, version, role, report, rows in entries:
        valid = [r for r in rows if not r["invalid"]]
        pos = [r for r in valid if r["refused"]]
        neg = [r for r in valid if not r["refused"]]
        rng = random.Random(f"{seed}:{code}:{version}")
        draw = {"negative": sorted(rng.sample(neg, min(negative, len(neg))), key=lambda r: r["index"]),
                "positive": sorted(rng.sample(pos, min(positive, len(pos))), key=lambda r: r["index"])}
        versions[f"{code}:{version}"] = {"model": code, "version": version, "role": role, "report": report,
                                         "n_pos": len(pos), "n_neg": len(neg), "invalid": len(rows) - len(valid),
                                         "total": len(rows), "sample_pos": len(draw["positive"]),
                                         "sample_neg": len(draw["negative"])}
        for stratum, chosen in draw.items():
            for r in chosen:
                picked.append({"model": code, "version": version, "role": role, "index": r["index"],
                               "refused": r["refused"], "stratum": stratum, "prompt": r["prompt"],
                               "prefill": prefill if has_prefill(version) else "", "completion": r["completion"]})
    random.Random(seed).shuffle(picked)
    sheet, key = [], {}
    for number, item in enumerate(picked, 1):
        sheet.append({"row_id": number, "prompt": item["prompt"], "prefill": item["prefill"],
                      "completion": item["completion"], "label": ""})
        key[str(number)] = {k: item[k] for k in ("model", "version", "role", "index", "refused", "stratum")}
    return sheet, {"labels": list(LABELS), "seed": seed, "versions": versions, "rows": key}


def write_sheet(path, sheet):
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["row_id", "prompt", "prefill", "completion", "label"])
        writer.writeheader()
        writer.writerows(sheet)


def main():
    from rows import harmful_prompts, load_rows

    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="append", required=True)
    ap.add_argument("--negative", type=int, default=15)
    ap.add_argument("--positive", type=int, default=10)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--prefill", required=True)
    ap.add_argument("--sheet", required=True)
    ap.add_argument("--key", required=True)
    ap.add_argument("--spec", default="/work/runs/spec.json")
    args = ap.parse_args()
    for path in (args.sheet, args.key):
        if Path(path).exists():
            raise SystemExit(f"{path} exists")
    prompts = harmful_prompts(args.spec)
    entries = []
    for spec in args.report:
        code, version, role, report = spec.split(":", 3)
        entries.append((code, version, role, report, load_rows(report, role, prompts)))
    sheet, key = build(entries, args.negative, args.positive, args.seed, args.prefill)
    Path(args.sheet).parent.mkdir(parents=True, exist_ok=True)
    write_sheet(args.sheet, sheet)
    Path(args.key).write_text(json.dumps(key, indent=1) + "\n")
    print(json.dumps({"rows": len(sheet), "versions": {k: [v["sample_neg"], v["sample_pos"]]
                                                       for k, v in key["versions"].items()}}))


if __name__ == "__main__":
    main()
