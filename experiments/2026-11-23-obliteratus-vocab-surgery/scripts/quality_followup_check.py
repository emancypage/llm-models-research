import argparse
import json
from pathlib import Path

TASKS = {
    "mmlu": ("screen/S/mmlu", "none", "acc", 1430),
    "arc": ("screen/S/arc", "none", "acc_norm", 1172),
    "gsm256": ("screen/S/gsm8k", "flexible-extract", "exact_match", 400),
    "gsm1024": ("screen/S/gsm8k", "flexible-extract", "exact_match", 400),
    "ifeval": ("S/ifeval", "none", "prompt_level_strict_acc", 541),
}


def read_run(path, task, expected_limit):
    _, row_filter, metric, count = TASKS[task]
    results = list(path.rglob("results_*.json"))
    if len(results) != 1:
        raise ValueError(f"{path}: expected one result file")
    result = json.loads(results[0].read_text())
    if expected_limit is not None:
        task_name = "ifeval" if task == "ifeval" else "gsm8k"
        generation = result["configs"][task_name]["generation_kwargs"]
        if generation.get("max_gen_toks", 256) != expected_limit:
            raise ValueError(f"{path}: unexpected generation limit")
    items = {}
    for file in sorted(path.rglob("samples_*.jsonl")):
        subject = file.stem.removeprefix("samples_").rsplit("_", 1)[0]
        with file.open() as stream:
            for line in stream:
                row = json.loads(line)
                if row["filter"] != row_filter:
                    continue
                key = (subject, row["doc_id"])
                hashes = tuple(row[name] for name in ("doc_hash", "prompt_hash", "target_hash"))
                if key in items or not all(hashes) or row[metric] not in (0, 1):
                    raise ValueError(f"{path}: invalid sample {key}")
                items[key] = hashes, int(row[metric])
    if len(items) != count:
        raise ValueError(f"{path}: expected {count} scored samples, got {len(items)}")
    return items


def check(model_root, candidate, task):
    base_path = model_root / TASKS[task][0]
    base_limit = 1280 if task == "ifeval" else 256 if task.startswith("gsm") else None
    base = read_run(base_path, task, base_limit)
    actual = read_run(candidate, task, 1024 if task == "gsm1024" else base_limit)
    if base.keys() != actual.keys() or any(base[k][0] != actual[k][0] for k in base):
        raise ValueError(f"{candidate}: items, prompts or targets differ from the baseline")
    gains = sum(actual[k][1] > base[k][1] for k in base)
    losses = sum(actual[k][1] < base[k][1] for k in base)
    print(f"{task} n={len(base)} correct={sum(score for _, score in actual.values())} "
          f"baseline_correct={sum(score for _, score in base.values())} gains={gains} losses={losses}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("model_root", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("task", choices=TASKS)
    args = parser.parse_args()
    check(args.model_root, args.candidate, args.task)
