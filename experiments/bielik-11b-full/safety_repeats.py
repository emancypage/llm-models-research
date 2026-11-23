"""Recompute the published summary from per-item flags; offline only."""

import argparse
import json
import statistics
from pathlib import Path
from obliteratus.concepts.statistics import paired_refusal_statistics

SEED = 20261121

def atomic_json(path, data):
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, allow_nan=False, indent=2) + "\n")
    temp.replace(path)

def summarize():
    results = {arm: [json.loads((OUT / f"{arm}-{n}.json").read_text()) for n in (1, 2, 3)]
               for arm in ("pristine", "edited")}
    summary = {"replicates_per_arm": 3, "unique_prompts": 320,
               "interpretation": "Repeated deterministic runs on the same questions; repeated observations are not new independent samples",
               "arms": {}, "paired_comparisons": []}
    shared = ("seed", "decoding", "prompt_set_sha256", "tokenizer_sha256", "refusal_scorer",
              "model_revision", "tool_revision", "edited_concept_run_sha256")
    anchor = results["pristine"][0]
    for arm, trials in results.items():
        for expected, row in enumerate(trials, 1):
            assert row["arm"] == arm and row["replicate"] == expected
            assert all(row[key] == anchor[key] for key in shared)
        rates = [row["refusal_rate"] for row in trials]
        if any(rate is None for rate in rates):
            raise ValueError("Cannot average a run without valid outputs")
        summary["arms"][arm] = {
            "refusal_counts": [r["refusals"] for r in trials],
            "valid_counts": [r["valid_count"] for r in trials],
            "invalid_counts": [r["invalid_count"] for r in trials],
            "mean_refusal_rate": statistics.mean(rates), "sample_stddev": statistics.stdev(rates),
            "min_refusal_rate": min(rates), "max_refusal_rate": max(rates),
            "all_refusal_and_invalid_flags_identical": all(
                r["refusal_flags"] == trials[0]["refusal_flags"] and r["invalid_flags"] == trials[0]["invalid_flags"]
                for r in trials[1:]),
        }
    for a, b in zip(results["pristine"], results["edited"], strict=True):
        valid = [i for i in range(320) if not (a["invalid_flags"][i] or b["invalid_flags"][i])]
        summary["paired_comparisons"].append(
            paired_refusal_statistics([a["refusal_flags"][i] for i in valid],
                                      [b["refusal_flags"][i] for i in valid], seed=SEED))
    summary["settings"] = {key: anchor[key] for key in shared}
    atomic_json(OUT / "summary.json", summary)
    print(json.dumps(summary["arms"]), flush=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("results_directory", type=Path)
    args = parser.parse_args()
    OUT = args.results_directory
    summarize()
