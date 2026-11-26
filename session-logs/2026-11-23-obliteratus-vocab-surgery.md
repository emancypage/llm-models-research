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

### Qwen2.5-7B complete (detector counts)

All four edits passed the scope check. The full PR list lowered detected refusals by 46.0 pp without the prefill, which met the rule for the random control. Two controls were written into the protocol before their runs: KR as planned, and an exploratory KR2 with the shape of the full list, because that is where the effect appeared. The full list suppresses words that the refusal detector looks for, so this result waits for the LLM judges. Judge A is available; judge B needs the model terms accepted on Hugging Face.

### Scope reduction, control models and random controls

The study owner shortened the study: Llama-3.2-3B kept only its refusal runs and word probe, and the Inkling-2-Mini stage was dropped. The random controls ran before the small models finished. 33 random tokens with the full-list strengths changed 4 of 200 refusals; the full list changed 94. Among the control models, Qwen2.5-1.5B showed a large drop with the full list and Llama-3.2-3B a small one.

### LLM judges

Judge A (`gemma-4-26B-A4B-it`) did not load within the memory guard, so the planned spare (`gemma-4-12B-it`) replaced it. Judge B ships only a SentencePiece tokenizer file, which the study environment could not read without a new package; a fast tokenizer was built from it with installed packages and checked (no text changed in an encode–decode round trip). Both changes were recorded before any judge result. In the 5-row load test both judges ran and agreed on all 5 rows.

### Judge results

Both judges scored all answer sets. Both classified many answers missed by the detector as refusals after the full PR-list edit. The formal human validation of the short answers was still pending at this point. The judge gate waits for the manual labels, so the judge measures are marked "judge unchecked" until then.

### Follow-up with a self-generated list of 500 tokens

At the owner's decision, the study added a list of 500 tokens built from each model's answers to harmful prompts, with two discovery rounds on separate prompts; no prefill runs. In round 2 on Qwen2.5-7B, 124 of the 250 candidates contained Chinese characters, as did 59 of the 500 answers to harmful prompts. Judge A measured a drop of 32.0 pp (Llama-3.1-8B) and 27.5 pp (Qwen2.5-7B). The 500-token random control increased judge A’s failure rate by 3.5 and 1.0 points respectively. The detector claimed two to three times as much. On Llama-3.1-8B the list also cost 12.25 pp on GSM8K at the 256-token limit. Manual sheet for this follow-up: 45 answers, pending.

## 25 November 2026

### Full answers

The owner pointed out that answers cut at 64 tokens hide whether a model refused in the end. Counting confirmed it: on Qwen2.5-7B nearly all answers were cut. The 200 prompts were answered again with up to 1024 tokens, without using the earlier prefill versions in the conclusions. The result grew: the 500-token list lowers failures by 43.5 and 37.5 pp by judge A, and the owner's 36 labels agree with judge A on 35. The judge results for the full answers stayed unread until the labelling was complete.

The agent had put a prefill version back into this follow-up against an earlier instruction; the owner noticed, and it was excluded and recorded.

## 25 November · Quality follow-up and closeout

The study owner requested the two-model quality follow-up. The protocol was updated before the new measurements. All 16 new runs finished at 21:35 CET, eight on each model. Four checks confirmed that the restored edits changed exactly 500 output rows and left all other weights intact. Fourteen earlier runs supplied the other comparison cells. The scorer matched the question, prompt and target for each item and produced 36 paired comparisons.

During the follow-up the owner requested publication of the 57 paired GSM8K cases where GSM8K awarded credit to the original model and zero to the selected-list model at the 1024-token limit. An export check found that treating the entire follow-up directory as a model version would mix scores from different versions. The exporter was corrected before those scores were published. The final capability data identify the model, version, task and math limit separately.

After the quality results were available, the owner explicitly decided to omit the 200-answer manual review and close the study. There are 0/200 labels on that sheet. The 36 existing full-answer labels are retained as a separate descriptive check. The manually corrected rates, formal judge validation and both verdicts that depend on those rates remain unassessed. The final report records these limits alongside the measured endpoints.

### Post-closeout verification

The 7,886 rows in the public quality table were checked against the original evaluation samples. The 36 paired results and all 57 published math pairs matched. Two Qwen answers (items 19 and 109) gave the expected mathematical result and still lost credit under the benchmark’s extraction rule. The final report records the two judges’ distinct outcomes and the answer-length checks. The capability data now link to the measured K1 comparisons for each model. Formal verdicts that depend on the omitted manual sheet remain undetermined.

On 25 November the published quality summaries were reconciled with the per-item scores. The K1 capability files retain the earlier prompt-weighted instruction fractions under a named historical field. Their current secondary IFEval score gives each instruction equal weight.

## Post hoc analysis after closeout (26 November 2026)

The owner requested an exploratory check of an external review against the original tokenizers and saved benchmark answers. The analysis retained two Llama groups: the five number tokens named in the review and all ten digit-only tokens in D500. It counted an item as a loss only when the original was correct. The five-token group had ten losses among 283 originally correct unexposed items. ARC and MMLU used the exact answer continuations scored by lm-eval, including leading spaces. The original quality scores and the 25 November closeout remain the basis for the formal study conclusions. [Post hoc definitions and counts](../reports/2026-11-23-obliteratus-vocab-surgery/data/analysis/token-exposure/README.md) · [Results](../reports/2026-11-23-obliteratus-vocab-surgery/results.md#post-hoc-analysis-after-closeout-26-november-2026)

**Proposal for the owner.** To estimate whether the selected list has a distinctive effect beyond the words and symbols it contains, draw several independent 500-token controls per model. Match the selected list on baseline token frequency measured on a separate corpus and on token category, including digits, actual MMLU answer letters, punctuation, whitespace and length. Freeze the rules, frequency bins and seeds before scoring. The present data show why an unmatched draw can fail tasks that rely on these symbols. Running this proposed comparison requires the owner's decision. [Inventories](../reports/2026-11-23-obliteratus-vocab-surgery/data/analysis/token-exposure/inventory.json) · [Random control results](../reports/2026-11-23-obliteratus-vocab-surgery/data/analysis/token-exposure/summary.json)
