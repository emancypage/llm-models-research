# Vocabulary-row edit study: research diary

Dated decisions that explain changes to the [protocol](../reports/2026-11-23-obliteratus-vocab-surgery/PROTOCOL.md). Measurements are in the [results](../reports/2026-11-23-obliteratus-vocab-surgery/results.md); tool problems are in the [issue log](../reports/2026-11-23-obliteratus-vocab-surgery/issues.md).

## 23 November 2026

### Plan and protocol

The study plan was approved with decisions D1–D6, then extended by change P1 (a local LLM judge and the label `inne`, decisions D7–D13). The protocol was written before the first run of an edited model. The word probe, the label codebook and the judge prompt were frozen before that run; their SHA-256 values are in the protocol.

### Stage 0 setup

The tool was first pinned to the PR head `5e55cdae`. The container image has no `pytest`, so the PR unit tests ran with a local copy of `pytest` and without coverage options: 75 passed. The offline lm-eval smoke test passed on all four tasks. A memory guard and a disk guard ran during all GPU work.

### Word probe

The probe was built in three rounds on unedited models only. In the first round 8 of the 10 `cannot` items in the output part failed in both Qwen models: in Llama and Qwen tokenizers ` can` also begins "can't", so informal contexts favour ` can`. Formal-register items fixed this. Indirect yes/no questions were made direct, and items that failed in both models were replaced. Items that failed in only one model were also replaced in round 2, because the plan's rule alone could not reach the planned 90% on one part; this is a recorded deviation.

### Export check and decision A

A no-op edit on Qwen2.5-7B left every weight bit-identical. The tool still wrote new tokenizer and configuration files, so the planned byte check of the tokenizer failed and the stage stopped. Diagnostics on that no-op copy showed identical token IDs, identical decoding, identical probe logits, and an identical `verify-edit` run (all 400 answer texts equal, KL 0). The study owner chose option A: the scope check requires identical tokenizer behaviour instead of identical bytes, and reports byte differences separately. The rejected option was to copy the source files into each edited checkpoint.

### Merged tool version

PR #595 was merged into `main` the same day. Compared with the PR head, `main` adds only a migration of old projection recipes. The vocabulary-edit code, the checkpoint writer, the loader, `verify-edit` and the refusal detector are unchanged. The study switched to the merged commit. Under the protocol rule, no earlier measurement was repeated. PR tests on the merged commit: 75 passed.

### Decision point G1

All stage-0 checks passed. On Llama-3.1-8B the post's token list changed one of 200 refusal flags. The time estimate for stages 0–2 rose from about 13 h to about 16.2 h, mostly because IFEval takes 77 min per 8B run. Stages 1 and 2 were queued to run without a pause between models. The pilot runs on Qwen2.5-1.5B were kept as pilot data, and stage 2 repeats them.

## 24 November 2026

### Correction by the original author

The author of the original claim reported that the 97.4% result came from a model whose chat template held a prefill from an earlier experiment, and put the method on hold. The protocol records this as context. The study already separates the prefill from the edit, so its method did not change. An exploratory run with the author's longer prefill text was added for Llama-3.1-8B and Qwen2.5-7B, before its measurement.

### Llama-3.1-8B complete (detector counts)

All four edits passed the scope check. The unedited model gave identical texts in every report, so the refusal tool is deterministic and each changed answer comes from the edit. The post's list changed almost nothing; the full PR list had a clear effect, mostly together with the prefill. The random control was not triggered, because its rule needs a 10 pp drop without the prefill and the largest drop was 7.0 pp. A word probe for the full list was added, before its measurement, because that list is where the effect is.
