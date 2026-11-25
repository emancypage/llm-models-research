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

## Reproduce the final quality comparisons

From the repository root, use Python 3.12 to replay the published scores. This takes a few seconds, uses only the standard library and requires no model weights. Each CSV row identifies a model, test, subject and zero-based item number. The last three columns are 0/1 correctness for the original (S), the selected 500 entries (D500) and the random 500 entries (KR500). The file has 7,886 rows, one per item at each tested limit per model.

~~~bash
study=2026-11-23-obliteratus-vocab-surgery
code_dir="experiments/$study/scripts"
data_dir="reports/$study/data"
replay_dir=$(mktemp -d)
python3.12 "$code_dir/quality_followup_scores.py" --items "$data_dir/quality-items.csv" --output "$replay_dir/paired.json"
cmp "$replay_dir/paired.json" "$data_dir/quality-paired.json"
~~~

The 36 comparisons consist of three version pairs for each of five test settings on each model, plus the long-versus-short math comparison within each of three versions on each model. A positive difference means more correct answers for the first version named in the JSON key. Intervals use paired resampling of the item score differences with 10,000 draws and seed 42. A zero exit from the last command means the generated JSON is byte-identical to the published result.

### Repeat the benchmark measurements from prepared model versions

The follow-up ran eight new tests per model and reused seven earlier tests with matching question, prompt and target hashes. The 1024 setting below is the maximum number of new tokens in a GSM8K answer. The two GSM8K runs use the same first 400 problems and the same flexible numeric extraction. Strict IFEval uses all 541 prompts at its original 1280-token limit. ARC-Challenge uses all 1172 questions and normalized answer likelihood. MMLU uses the recorded evenly spaced sample of 1430 questions.

| Version | Newly measured | Reused from earlier runs |
| --- | --- | --- |
| S | GSM8K 1024 | GSM8K 256, IFEval, MMLU, ARC-Challenge |
| D500 | GSM8K 1024, IFEval | GSM8K 256, MMLU, ARC-Challenge |
| KR500 | GSM8K 1024, IFEval, MMLU, ARC-Challenge, GSM8K 256 | None |

In the offline evaluation environment, set MODEL_DIR to the existing checkpoint and MODEL_CODE to l8 or q7. Set ARM to S, D500 or KR500. The model revisions are in the [protocol](../../reports/2026-11-23-obliteratus-vocab-surgery/PROTOCOL.md). Run this Bash block for each combination. Use a new output directory for any repeat.

~~~bash
out="/work/eval/$MODEL_CODE/quality-20261125/$ARM"
common=(--model hf --model_args "pretrained=$MODEL_DIR,dtype=bfloat16" --device cuda --log_samples)
math=(--tasks gsm8k --batch_size 16 --num_fewshot 5 --apply_chat_template --fewshot_as_multiturn --limit 400)
bench() {
    local name=$1
    shift
    /work/venv/bin/lm_eval "${common[@]}" "$@" --output_path "$out/$name"
}
set -e
bench gsm1024 "${math[@]}" --gen_kwargs max_gen_toks=1024
if [[ "$ARM" == D500 || "$ARM" == KR500 ]]; then
    bench ifeval --tasks ifeval --batch_size 16 --apply_chat_template
fi
if [[ "$ARM" == KR500 ]]; then
    bench mmlu --tasks mmlu --batch_size 4 --num_fewshot 5 --samples "$(cat /work/scripts/mmlu-every10.json)"
    bench arc --tasks arc_challenge --batch_size 4 --num_fewshot 25
    bench gsm256 "${math[@]}"
fi
~~~

For a full replay from lm-eval sample files, put earlier MMLU, ARC and 256-token GSM8K output in the model's screen/S and screen/V-d500 directories, in subdirectories named mmlu, arc and gsm8k. Put original IFEval output in S/ifeval. The full model roots are eval/l8 and eval/q7 under the study directory. Use the same task definitions and item selection shown above when collecting any missing earlier samples. Then run the following command with the study directory available at /work. It checks sample counts, answer limits and per-item question, prompt and target hashes before comparing scores.

~~~bash
python3.12 /work/scripts/quality_followup_scores.py --work-dir /work --output /tmp/quality-from-runs.json
~~~

The study owner omitted the planned 200-answer manual sheet at closeout. Step 6 above describes the original protocol. The published quality replay uses benchmark correctness only.
