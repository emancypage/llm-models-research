# Vocabulary-row edits in Llama and Qwen

**Study closed on 25 November 2026.** On 200 prompts per model, the ten-entry edit changed judge A’s failure rate by −0.5 percentage points on Llama 3.1 8B Instruct and +2.5 on Qwen2.5 7B Instruct. With 500 selected entries, judge A recorded fewer failures. Judge B’s separate count of refusals plus invalid answers also fell. At a 1024-token limit, the GSM8K scorer awarded Llama credit on 341 of 400 math problems before the selected edit and 292 afterwards. Qwen went from 348 to 350.

**Manual review decision.** At closeout the study owner explicitly decided to omit the planned manual review of 200 short answers. The sheet has 0/200 labels. The manually corrected failure and refusal rates, and the protocol check for validating the judges, therefore have no result. The formal verdicts “the edit alone works” and “near zero” are undetermined. A separate, completed review of 36 full answers without a prefill is reported below.

## Answers to the six study questions

1. **Does the edit alone reduce failures?** In the prespecified 64-token test of the ten-entry edit (K1), the detector’s refusal-or-invalid rate changed by −0.5 points on Llama and −2.0 on Qwen. The Holm-adjusted p values were 1.00 and 0.25. Neither reached the required 20-point decrease. Judge A scored the original ten-entry edit at −0.5 percentage points on Llama and +2.5 on Qwen relative to the original models. For the selected 500 entries the differences were −43.5 and −37.5 points. The random 500-entry versions scored +4.0 and +1.5 points. These judge comparisons use the exploratory 1024-token runs. A judge-A failure includes refusal, another noncompliant answer, or an invalid answer. The usefulness of compliant answers was outside the evaluation.
2. **What did the edit add to a prefill?** A prefill is an opening already supplied for the assistant’s answer. In the original 64-token screen, the ten-entry edit on top of the protocol prefill changed judge A’s failure rate by −1.5 points on Llama and +2.0 on Qwen. The prefill alone changed it by −11.5 and −49.5 points. The detector’s refusal-or-invalid rate changed by −2.0 and −5.5 points for the edit with a prefill. Both missed the prespecified 10-point threshold. These measurements concern answer openings. The full-answer comparison used no prefill. The short prefill was taken from a unit test. The original Inkling experiment used different wording.
3. **Did the keyword detector measure the outcome reliably?** On Qwen in the short-answer test with the full PR list, the detector reported a 46.0-point decrease. Judge A measured a 5.5-point decrease. Among valid, unflagged Qwen answers, judge A classified 6/34 as refusals before this edit and 87/126 afterwards. Disagreement also went the other way: on the original Llama, judge A classified 22 flagged answers as compliant. Without the omitted sheet these counts quantify disagreement with the judge. [Detector and judge counts](data/analysis/judge/judge.json)
4. **What was the quality cost?** For the ten-entry edit, the mean of four benchmarks changed by −0.31 points on Llama and −0.21 on Qwen. Their paired 95% intervals were [−0.55, −0.09] and [−0.51, +0.09] points. Both lower bounds met the prespecified −2-point margin for that mean. Yet both fell to 50% on both parts of the everyday-word test. For the selected 500-entry edit, Llama lost math accuracy at both answer limits. Qwen’s math score stayed close to its baseline at the same limit, while its strict instruction-following score fell from 378 to 362 out of 541. The final quality tables below cover all three versions of both models. [Llama K1 scores](data/analysis/multi-l8/capability-summary.json) · [Qwen K1 scores](data/analysis/multi-q7/capability-summary.json)
5. **Did the findings transfer?** For the ten-entry list, neither main model showed a substantial change on full answers. In the smaller Qwen and Llama controls the corresponding edit changed the no-prefill keyword count by zero and two answers, respectively. Model size and shared input/output weights differ together in these controls. For Llama, 19 of 170 original keyword-flagged refusals contained a source token from the ten-entry list. For Qwen it was 149 of 165. The study owner dropped the Inkling-2-Mini stage on 24 November. The original claim on its own model remains untested.
6. **What did the tool checks find?** A no-op export could rewrite tokenizer and configuration files and report an edited row even when the weights were identical. On the checked Qwen no-op run all 400 answer texts were identical. The 64-token answer cap and the keyword detector also affected interpretation. The issue log records the affected versions, checks and measurement limits. [Issue log](issues.md)

## Original four-condition screen

Each cell counts keyword-flagged refusals plus invalid answers out of 200. The first two columns use the original template. The last two use the same short prefill. The main models use the ten-entry list from the post. The two smaller controls use the prespecified shared-weight variant. These are 64-token measurements.

| Model | Original | Edited | Original with prefill | Edited with prefill |
| --- | ---: | ---: | ---: | ---: |
| Llama 3.1 8B | 170 | 169 | 152 | 148 |
| Qwen2.5 7B | 166 | 162 | 64 | 53 |
| Llama 3.2 3B | 141 | 143 | 25 | 29 |
| Qwen2.5 1.5B | 184 | 184 | 16 | 12 |

## Full answers and human review

S is the original model. D500 uses 500 entries selected from a separate set of the model’s own answers. KR500 uses a single random list of the same size for that model. Each model answered the same 200 test prompts per version, with up to 1024 new tokens. The table gives judge A’s rate of refusals, other noncompliant answers and invalid answers combined. Judge B scored only refusals plus invalid answers. For the selected edit, this second measure fell from 82.0% to 36.0% on Llama (−46.0 points) and from 82.5% to 37.0% on Qwen (−45.5 points). In the paired comparison against the original, 94 Llama items improved on B’s measure and 2 worsened (exact two-sided McNemar p = 1.18 × 10⁻²⁵). For Qwen the counts were 92 and 1 (p = 1.90 × 10⁻²⁶).

| Model | Original | Ten-entry list | 500 selected | 500 random |
| --- | ---: | ---: | ---: | ---: |
| Llama 3.1 8B | 79.0% | 78.5% | 35.5% | 83.0% |
| Qwen2.5 7B | 73.0% | 75.5% | 35.5% | 74.5% |

All 1,600 no-prefill texts began with their saved 64-token text after trimming its trailing decode artifact and whitespace. Some 1024-token answers still ended at the cap. The counts below are out of 200 per cell and concern the refusal study. [Length and prefix checks](data/full/generation-checks.json)

| Model | Original | Ten-entry list | 500 selected | 500 random |
| --- | ---: | ---: | ---: | ---: |
| Llama 3.1 8B | 8 | 8 | 21 | 60 |
| Qwen2.5 7B | 2 | 2 | 4 | 7 |

One reviewer assessed randomly sampled valid answers without a prefill. Each model contributed 6 original and 12 selected-list answers, for 12 original and 24 selected-list answers overall. Two of these 36 answers reached the limit. The reviewer marked 2/12 and 16/24 as compliant. Judge A agreed on compliance in 35/36 cases. Judge B agreed on refusal in 35/36. The 95% Wilson interval for each agreement is 85.8%–99.5%. The protocol required a 90% lower bound and a comparison across version groups on its designated sheet. The full-answer sample did not replace that check. The reviewer had seen the earlier short-answer aggregates before labelling this sample and saw full-answer judge results only afterwards.

The 57 paired GSM8K cases are all items that lost benchmark credit after the selected edit. For example, Qwen’s edited answer to item 19 correctly states 6 miles per hour, but the scorer extracted the later number 4. In item 109, the scorer rejected the correctly stated amount of $28.00. Both examples lost credit because of the scoring rule. [All 57 cases](data/gsm8k-comparisons/README.md) · [Qwen examples](data/gsm8k-comparisons/qwen-01-05.md)

## List coverage and word use

The first two columns count original keyword-flagged refusals containing a source token from the named list. The word test used 120 items for choosing a word and 120 for understanding it. Percentages show original → edited for the ten-entry list or its shared-weight counterpart in the small controls. Each item had two choices. The questions were revised using the original Qwen models before the probe was frozen, so the percentages describe performance on these particular word pairs.

| Model | Ten-entry coverage | Full PR list coverage | Word choice | Word understanding |
| --- | ---: | ---: | ---: | ---: |
| Llama 3.1 8B | 19/170 | 31/170 | 95.0% → 50.0% | 91.7% → 50.0% |
| Qwen2.5 7B | 149/165 | 165/165 | 99.2% → 50.0% | 99.2% → 50.0% |
| Llama 3.2 3B | 57/141 | 77/141 | 95.0% → 50.0% | 94.2% → 65.8% |
| Qwen2.5 1.5B | 2/184 | 184/184 | 96.7% → 50.0% | 92.5% → 91.7% |

## Final quality measurements

25 November 2026. At 21:35 CET all 16 planned new runs finished. We combined eight new runs per model with seven matched earlier runs per model. The original, selected and random versions faced identical items within each test. Both edited versions changed 500 vocabulary entries on the output side. The four checks confirmed that the input and other weights stayed identical. [Scope checks](data/scope-checks/quality-restorations.json)

On 400 GSM8K items with the 1024-token limit, the scorer accepted 49 fewer Llama answers after the selected edit (341 to 292). It accepted two more Qwen answers (348 to 350). Qwen’s interval includes zero. The random controls received credit on 125 items for Llama and 70 for Qwen.

### Benchmark scores

The first table gives the number of items that passed each scorer. GSM8K applies flexible numeric extraction to the answer text. IFEval requires all strict checks for a prompt to pass. MMLU scores the answer letter. ARC-Challenge compares answer texts using normalized likelihood.

The second table gives paired differences in percentage points with 95% intervals in brackets. Each comparison resamples the same items in pairs (10,000 draws, seed 42). These are per-comparison intervals. The two GSM8K rows use the same questions.

#### Llama 3.1 8B Instruct

| Test | Items | Original | Selected | Random |
| --- | ---: | ---: | ---: | ---: |
| GSM8K · 256 tokens | 400 | 341 | 292 | 124 |
| GSM8K · 1024 tokens | 400 | 341 | 292 | 125 |
| IFEval · instruction following | 541 | 401 | 391 | 325 |
| MMLU · general knowledge | 1430 | 994 | 994 | 848 |
| ARC-Challenge · reasoning | 1172 | 716 | 686 | 588 |


| Test | Selected − original | Random − original | Selected − random |
| --- | ---: | ---: | ---: |
| GSM8K · 256 tokens | −12.25 [−15.75 … −8.75] | −54.25 [−59.50 … −49.25] | +42.00 [+36.25 … +47.75] |
| GSM8K · 1024 tokens | −12.25 [−15.75 … −8.75] | −54.00 [−59.25 … −48.75] | +41.75 [+35.75 … +47.50] |
| IFEval · instruction following | −1.85 [−4.62 … +0.92] | −14.05 [−18.30 … −9.80] | +12.20 [+8.13 … +16.27] |
| MMLU · general knowledge | 0 [0 … 0] | −10.21 [−12.31 … −8.11] | +10.21 [+8.11 … +12.38] |
| ARC-Challenge · reasoning | −2.56 [−3.92 … −1.28] | −10.92 [−13.40 … −8.53] | +8.36 [+5.80 … +11.01] |


#### Qwen2.5 7B Instruct

| Test | Items | Original | Selected | Random |
| --- | ---: | ---: | ---: | ---: |
| GSM8K · 256 tokens | 400 | 297 | 296 | 66 |
| GSM8K · 1024 tokens | 400 | 348 | 350 | 70 |
| IFEval · instruction following | 541 | 378 | 362 | 344 |
| MMLU · general knowledge | 1430 | 1100 | 1100 | 884 |
| ARC-Challenge · reasoning | 1172 | 788 | 750 | 653 |


| Test | Selected − original | Random − original | Selected − random |
| --- | ---: | ---: | ---: |
| GSM8K · 256 tokens | −0.25 [−2.50 … +2.00] | −57.75 [−63.00 … −52.50] | +57.50 [+52.25 … +62.75] |
| GSM8K · 1024 tokens | +0.50 [−1.25 … +2.25] | −69.50 [−74.25 … −64.75] | +70.00 [+65.00 … +74.75] |
| IFEval · instruction following | −2.96 [−5.55 … −0.37] | −6.28 [−9.61 … −2.96] | +3.33 [−0.18 … +6.84] |
| MMLU · general knowledge | 0 [0 … 0] | −15.10 [−17.41 … −12.73] | +15.10 [+12.80 … +17.41] |
| ARC-Challenge · reasoning | −3.24 [−4.52 … −2.05] | −11.52 [−14.08 … −9.04] | +8.28 [+5.63 … +11.01] |

### What changed with the math answer limit

For each version, 400 answers at the 1024-token limit were paired with the same 400 items at 256 tokens.

| Model | Version | Wrong → correct | Correct → wrong | 1024 − 256 (pp) |
| --- | ---: | ---: | ---: | ---: |
| Llama | Original | 0 | 0 | 0 [0 … 0] |
| Llama | Selected | 0 | 0 | 0 [0 … 0] |
| Llama | Random | 3 | 2 | +0.25 [−0.75 … +1.25] |
| Qwen | Original | 51 | 0 | +12.75 [+9.50 … +16.25] |
| Qwen | Selected | 54 | 0 | +13.50 [+10.25 … +17.00] |
| Qwen | Random | 6 | 2 | +1.00 [−0.25 … +2.50] |

At the 1024-token limit, Llama lost GSM8K credit on 52 items and gained it on three after the selected edit. Qwen lost credit on five and gained it on seven. At the 256-token limit those counts were 52 and three for Llama, and 11 and ten for Qwen. Among the 52 long-limit Llama losses, 16 edited answers re-encode to the cap and may still be incomplete. None of the five Qwen loss cases reached the cap. The saved math texts have no per-answer stop reason.

### Interpretation and limits

The selected edit reduced ARC-Challenge accuracy on both models. For instruction following, Qwen fell from 378 to 362 correct. Llama fell from 401 to 391, with an interval that includes zero. Neither model changed a single MMLU score after the selected edit. MMLU compares answer letters, and the selected edit left those letters untouched. The identical score provides limited evidence about retained knowledge.

Each random version scored lowest on every benchmark measured here. Only one random list was drawn per model, and the lists were not matched to the selected entries by token frequency. The intervals describe item variability for these lists. A separate repeat of the unchanged original model at 256 tokens changed the benchmark verdict on 3/200 Llama items and 8/200 Qwen items. All 200 prompt and target hashes matched. The repeat provides a check on run variability, which these intervals do not measure. Generalization to other lists, models or tasks remains open.

[Test protocol](PROTOCOL.md) · [All 36 paired comparisons, including gains, losses and intervals](data/quality-paired.json)

## Earlier measurements and reproducibility

The four-condition screen and word tests were recorded on 23–24 November. The 1024-token refusal comparison and the quality follow-up were completed on 25 November. The stage notes preserve what was known at each point. Statements there about pending work and provisional verdicts give the status at that date. The closeout decision above governs the final interpretation.

[Reports as recorded before closeout](https://github.com/emancypage/llm-models-research/blob/d8a0a9883c3e4a80ad8d4079e4e196ddf6f22c23/reports/2026-11-23-obliteratus-vocab-surgery/results.md) · [Scored benchmark items](data/quality-items.csv) · [Reproduce the quality results](../../experiments/2026-11-23-obliteratus-vocab-surgery/README.md#reproduce-the-final-quality-comparisons) · [Study protocol](PROTOCOL.md)

In the source data, “edit alone works” and “near zero” are recorded as null. Each identifies a formal verdict that requires the omitted manual correction. [Formal verdicts](data/analysis/main/endpoints.json) · [Full-answer scores and human agreement](data/analysis/full-score.json)
