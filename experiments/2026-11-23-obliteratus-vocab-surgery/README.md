# Vocabulary-row edit study: code and inputs

Code for the [vocabulary-row edit study](../../reports/2026-11-23-obliteratus-vocab-surgery/results.md). The [protocol](../../reports/2026-11-23-obliteratus-vocab-surgery/PROTOCOL.md) defines the conditions and the scoring.

## Requirements

- OBLITERATUS commit `1de580f7a13f185488dc31ff27f2e027545ad82d` (contains PR #595), mounted read-only at `/upstream`.
- A CUDA PyTorch container image with `transformers` 5.17.0; lm-eval 0.4.13 in a virtual environment at `/work/venv`; the OBLITERATUS runtime environment at `/state/venv`.
- Every container runs with `--network none`. Datasets and models must be cached in the study directory first.
- Set `STUDY_DIR`, `OBLITERATUS_DIR` and `IMAGE` before sourcing `scripts/common.sh`. The scripts expect `scripts/`, `configs/`, `probe/`, `judge/`, `runs/spec.json` and `models/` inside `STUDY_DIR`.

## Inputs in this directory

| Path | Content |
| --- | --- |
| `configs/` | edit configurations K1, K1o, K1i, K2, `k1o-tied`, `k2-tied` and the no-op write check S0 |
| `spec.json` | `verify-edit` specification: 200 built-in `final_test` pairs, greedy, 64 new tokens |
| `probe/items.json` | frozen word probe, 240 everyday sentences (SHA-256 in `probe/FROZEN.sha256`); `probe/make_items.py` builds it |
| `judge/codebook.md`, `judge/prompt-a.txt` | frozen label codebook and the prompt of judge A |
| `scripts/models/*.env` | model code, Hugging Face ID, revision and the model directory used as the unedited version |

The extraction prompt file named by `verify-edit` holds harmful prompts and is not published. The held-out prompts are built into OBLITERATUS (`builtin:qwen38-v1:final_test`).

## Steps

1. Model copies (on the host): `make_template_copy.py <source> <dest> --fix-date "23 Nov 2026"` for Llama-3.2-3B, and `--prefill "Sure, here are the details:"` for each prefill copy. Llama models use copies whose tokenizer has a pad token.
2. Edit: `apply.sh <model-code> <config>`. Scope check: `check_receipt.sh <unedited-dir> <edited-dir> --expect-input N --expect-output M` (or `--expect-shared K`).
3. Refusals: `KEEP_TEXTS=1 verify.sh <model-code> <version> <edited-dir>`; for runs with a prefill use the model code with the suffix `p`.
4. Capabilities: `screen.sh` (every 10th MMLU item, full ARC-Challenge, first 400 GSM8K items), `TASKS=ifeval eval.sh`, and `srepeat.sh` for the noise floor.
5. Word probe: `probe.sh <model-code> <version> <model-dir>`.
6. Manual review sheet: `review_sample.py`; score: `review_score.py`. LLM judges: `judge.sh`.
7. Analysis: `analyze_vocab.py <config> <outdir>`; capabilities with `analyze_multi.py` and a `pairs` entry such as `[["V-k1", "S"]]`.

Tests: `pytest test_judge.py test_review.py test_analyze_vocab.py` inside the container, with `scripts/` on `PYTHONPATH`.

The queue runner and the memory guard used to schedule the jobs are operational tools and are not included.
