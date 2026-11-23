"""Local OBLITERATUS telemetry and reviewable exports for the GSM8K comparison."""

import argparse
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
from importlib.metadata import version
from pathlib import Path
from unittest.mock import patch


REVISION = "7678d84196fe6c348dfd01078bbfb50857463647"
MODELS = (
    ("Qwen/Qwen3-8B", "b968826d9c46dd6066d109eabc6255188de91218"),
    ("BabarAzaa/Test3", "73f58f9b84443c8b5abbb90f7b5e5fd16804ef69"),
)
FILTERS = ("strict-match", "flexible-extract")
HERE = Path(__file__).resolve().parent


def open_telemetry(source, private):
    revision = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    if revision != REVISION:
        raise ValueError(f"Expected OBLITERATUS {REVISION}, found {revision}")
    os.environ["OBLITERATUS_TELEMETRY"] = "1"
    os.environ["OBLITERATUS_TELEMETRY_REPO"] = ""
    os.environ["OBLITERATUS_DATA_DIR"] = str(private)
    sys.path.insert(0, str(source.resolve()))
    from obliteratus import telemetry

    if not telemetry.is_enabled() or telemetry.TELEMETRY_FILE.parent.resolve() != private.resolve():
        raise RuntimeError("Cannot record telemetry in the experiment directory")
    return telemetry


def summarize(results, count):
    samples = results["samples"]["gsm8k"]
    metrics = results["results"]["gsm8k"]
    scores = {}
    input_set = None
    for name in FILTERS:
        rows = [s for s in samples if s["filter"] == name]
        inputs = sorted((s["doc_id"], s["doc_hash"], s["prompt_hash"], s["target_hash"]) for s in rows)
        if len(rows) != count or len({s["doc_id"] for s in rows}) != count:
            raise ValueError(f"Incomplete or duplicate samples for {name}")
        if input_set is not None and input_set != inputs:
            raise ValueError("Inputs differ between scoring rules")
        input_set = inputs
        hits = [s["exact_match"] for s in rows]
        if any(hit not in (0, 1) for hit in hits):
            raise ValueError(f"Invalid per-sample scores for {name}")
        score = metrics[f"exact_match,{name}"]
        if not math.isclose(sum(hits) / count, score, abs_tol=1e-12):
            raise ValueError(f"Per-sample scores disagree with the aggregate for {name}")
        scores[name] = float(score)
    fingerprint = hashlib.sha256(json.dumps(input_set).encode()).hexdigest()
    return scores, fingerprint


def write_share_bundle(run_dir, results, comparison, count, harness_version):
    records = []
    fingerprints = []
    for label, (model, revision), result in zip(("original", "abliterated"), MODELS, results, strict=True):
        scores, fingerprint = summarize(result, count)
        fingerprints.append(fingerprint)
        headline = comparison[label]
        if headline is None or not math.isfinite(headline) or not 0 <= headline <= 1:
            raise ValueError(f"Missing or invalid OBLITERATUS score for {model}")
        records.append(dict(model=model, revision=revision, **scores, headline=headline))
    if fingerprints[0] != fingerprints[1]:
        raise ValueError("The compared models received different questions or prompts")
    delta = comparison["delta"]
    if delta is None or not math.isclose(delta, records[1]["headline"] - records[0]["headline"], abs_tol=1e-12):
        raise ValueError("Invalid OBLITERATUS delta")

    stage = "pilot" if count == 5 else "main"
    report = dict(stage=stage, review="awaiting human review", dataset="openai/gsm8k",
                  subset="main/test", tasks_per_model=count, input_set_sha256=fingerprints[0],
                  obliteratus_revision=REVISION, lm_eval_version=harness_version,
                  fewshot=5, batch_size=1, compute_dtype="bfloat16", models=records, headline_delta=delta)
    table = ["| Model | Strict | Flexible | OBLITERATUS |", "| --- | ---: | ---: | ---: |"]
    for r in records:
        table.append(f"| {r['model']} | {r['strict-match']:.1%} | {r['flexible-extract']:.1%} | {r['headline']:.1%} |")
    draft = run_dir / "private" / "draft"
    draft.mkdir()
    (draft / "results.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    (draft / "REPORT.md").write_text(
        f"# GSM8K comparison ({stage})\n\nAwaiting human review. {count} questions per model.\n\n"
        + "\n".join(table) + f"\n\nOBLITERATUS score difference (modified minus original): {100*delta:+.1f} percentage points.\n"
    )
    protocol = HERE.parents[1] / "reports" / HERE.name / "PROTOCOL.md"
    shutil.copyfile(protocol, draft / "PROTOCOL.md")
    draft.rename(run_dir / "share")


def run_comparison(source, run_dir, count):
    private = run_dir / "private"
    private.mkdir(mode=0o700)
    telemetry = open_telemetry(source, private)
    import lm_eval
    from huggingface_hub import snapshot_download
    from obliteratus.evaluation.lm_eval_integration import compare_models

    paths = [snapshot_download(model, revision=revision) for model, revision in MODELS]
    captured = []
    original_evaluate = lm_eval.simple_evaluate

    def record_evaluation(**kwargs):
        kwargs["model_args"] += ",dtype=bfloat16"
        result = original_evaluate(**kwargs, log_samples=True)
        index = len(captured)
        (private / f"evaluation-{index + 1}.json").write_text(json.dumps(result, default=str) + "\n")
        scores, _ = summarize(result, count)
        model, revision = MODELS[index]
        record = telemetry.BenchmarkRecord(model_id=model, method="published-checkpoint-evaluation",
                                           dataset="openai/gsm8k", n_prompts=count, compute_dtype="bfloat16",
                                           extra={"revision": revision, "gsm8k_exact_match": scores})
        if not telemetry.log_benchmark(record):
            raise RuntimeError("Local telemetry write failed")
        captured.append(result)
        return result

    with patch.object(lm_eval, "simple_evaluate", record_evaluation):
        comparison = compare_models(*paths, tasks=["gsm8k"], batch_size=1, num_fewshot=5, limit=count)
    write_share_bundle(run_dir, captured, comparison["gsm8k"], count, version("lm_eval"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("check", "pilot", "main"))
    parser.add_argument("--source", type=Path, default=HERE.parents[1] / "vendor" / "OBLITERATUS-7678d841")
    parser.add_argument("--runs", type=Path, default=Path.cwd() / "runs")
    args = parser.parse_args()
    if args.action == "check":
        with tempfile.TemporaryDirectory() as directory:
            telemetry = open_telemetry(args.source, Path(directory))
            record = telemetry.BenchmarkRecord(model_id="diagnostic", method="telemetry-check", gpu_name="unused")
            if not telemetry.log_benchmark(record):
                raise RuntimeError("Diagnostic record was not saved")
            saved = json.loads(telemetry.TELEMETRY_FILE.read_text())
            if saved["method"] != "telemetry-check":
                raise RuntimeError("Unexpected diagnostic record")
            print("OBLITERATUS telemetry enabled, local record verified, Hub sync disabled.")
        return
    args.runs.mkdir(parents=True, exist_ok=True)
    run_dir = Path(tempfile.mkdtemp(prefix=args.action + "-", dir=args.runs)).resolve()
    print(f"Run directory: {run_dir}", flush=True)
    run_comparison(args.source, run_dir, 5 if args.action == "pilot" else 100)
    print(f"Draft for review: {run_dir / 'share'}")


if __name__ == "__main__":
    main()
