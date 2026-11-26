"""Post hoc analysis after closeout (26 November 2026, exploratory)."""

import argparse
import csv
import json
from collections import Counter
from math import comb
from pathlib import Path


REPORT = Path(__file__).resolve().parents[2] / "reports/2026-11-21-obliteratus-gsm8k"
STATUS = "Post hoc analysis after closeout (26 November 2026, exploratory)."


def strict_items(path, revision):
    data = json.loads(path.read_text())
    if revision not in data["config"]["model_args"]:
        raise ValueError(f"Wrong checkpoint: {path}")
    rows = [r for r in data["samples"]["gsm8k"] if r["filter"] == "strict-match"]
    if len(rows) != 100 or {r["doc_id"] for r in rows} != set(range(100)):
        raise ValueError("Expected the first 100 unique test items")
    return {r["doc_id"]: r for r in rows}


def summarize(rows, published):
    if len(rows) != 100 or {int(row["doc_id"]) for row in rows} != set(range(100)):
        raise ValueError("Incomplete strict score pairs")
    pairs = Counter((int(row["original"]), int(row["modified"])) for row in rows)
    if any(a not in (0, 1) or b not in (0, 1) for a, b in pairs):
        raise ValueError("Expected binary scores")
    losses, gains = pairs[1, 0], pairs[0, 1]
    correct = [pairs[1, 1] + losses, pairs[1, 1] + gains]
    if [n / len(rows) for n in correct] != [m["strict-match"] for m in published["models"]]:
        raise ValueError("Strict scores differ from the published measurements")
    n = losses + gains
    p = min(1.0, 2 * sum(comb(n, i) for i in range(min(losses, gains) + 1)) / 2**n)
    return {"analysis": STATUS, "items": len(rows), "scoring_rule": "strict-match",
            "original_correct": correct[0], "modified_correct": correct[1],
            "both_correct": pairs[1, 1], "both_incorrect": pairs[0, 0],
            "losses": losses, "gains": gains, "difference_pp": 100 * (gains - losses) / len(rows),
            "two_sided_exact_mcnemar_p": p}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private", type=Path, help="Original directory containing the two evaluation JSONs")
    parser.add_argument("--publication", type=Path, default=REPORT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = args.publication / "data"
    published = json.loads((data / "main/results.json").read_text())
    target = data / "analysis"
    pairs_file = target / "post-hoc-strict-pairs.csv"
    if args.private:
        samples = [strict_items(args.private / f"evaluation-{n}.json", model["revision"])
                   for n, model in enumerate(published["models"], 1)]
        rows = []
        for idx in range(100):
            a, b = (s[idx] for s in samples)
            if any(a[k] != b[k] for k in ("doc_hash", "prompt_hash", "target_hash")):
                raise ValueError(f"Different question, prompt or target at item {idx}")
            rows.append({"doc_id": idx, "original": int(a["exact_match"]), "modified": int(b["exact_match"])})
        summarize(rows, published)
        if not args.check:
            target.mkdir(parents=True, exist_ok=True)
            with pairs_file.open("w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=("doc_id", "original", "modified"), lineterminator="\n")
                writer.writeheader()
                writer.writerows(rows)
    with pairs_file.open(newline="") as stream:
        saved = [{k: int(v) for k, v in row.items()} for row in csv.DictReader(stream)]
    if args.private and rows != saved:
        raise ValueError("Strict pairs differ from the original evaluations")
    result = json.dumps(summarize(saved, published), indent=2) + "\n"
    summary = target / "post-hoc-strict-mcnemar.json"
    if args.check:
        if summary.read_text() != result:
            raise SystemExit("Stale McNemar result")
        print("Verified 100 paired strict scores and the exact McNemar result.")
    else:
        summary.write_text(result)


if __name__ == "__main__":
    main()
