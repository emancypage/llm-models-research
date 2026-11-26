# Vocabulary-row edits in Llama and Qwen

**Study closed on 25 November 2026.** On 200 prompts per model, the ten-entry edit changed judge A’s failure rate by −0.5 percentage points on Llama 3.1 8B Instruct and +2.5 on Qwen2.5 7B Instruct. With 500 selected entries, judge A recorded fewer failures. Judge B’s separate count of refusals plus invalid answers also fell. At a 1024-token limit, the GSM8K scorer awarded Llama credit on 341 of 400 math problems before the selected edit and 292 afterwards. Most of the lost items had reference solutions containing a number token the edit suppressed, according to the [post hoc analysis after closeout](#post-hoc-analysis-after-closeout-26-november-2026).

<!-- quality:qwen-math -->
On the same 400 GSM8K problems, Qwen2.5-7B went from 297 to 296 (−0.25 pp) at 256 tokens and from 348 to 350 (+0.50 pp) at 1024 tokens after the selected 500-entry edit. Both paired 95% intervals include zero. This sample gives no clear evidence that the edit changed Qwen’s math score.
<!-- /quality:qwen-math -->

**Manual review decision.** At closeout the study owner explicitly decided to omit the planned manual review of 200 short answers. The sheet has 0/200 labels. The manually corrected failure and refusal rates, and the protocol check for validating the judges, therefore have no result. The formal verdicts “the edit alone works” and “near zero” are undetermined. A separate, completed review of 36 full answers without a prefill is reported below.

## Answers to the six study questions

1. **Does the edit alone reduce failures?** In the prespecified 64-token test of the ten-entry edit (K1), the detector’s refusal-or-invalid rate changed by −0.5 points on Llama and −2.0 on Qwen. The Holm-adjusted p values were 1.00 and 0.25. Neither reached the required 20-point decrease. Judge A scored the original ten-entry edit at −0.5 percentage points on Llama and +2.5 on Qwen relative to the original models. For the selected 500 entries the differences were −43.5 and −37.5 points. The random 500-entry versions scored +4.0 and +1.5 points. These judge comparisons use the exploratory 1024-token runs. A judge-A failure includes refusal, another noncompliant answer, or an invalid answer. The usefulness of compliant answers was outside the evaluation.
2. **What did the edit add to a prefill?** A prefill is an opening already supplied for the assistant’s answer. In the original 64-token screen, the ten-entry edit on top of the protocol prefill changed judge A’s failure rate by −1.5 points on Llama and +2.0 on Qwen. The prefill alone changed it by −11.5 and −49.5 points. The detector’s refusal-or-invalid rate changed by −2.0 and −5.5 points for the edit with a prefill. Both missed the prespecified 10-point threshold. These measurements concern answer openings. The full-answer comparison used no prefill. The short prefill was taken from a unit test. The original Inkling experiment used different wording.
3. **Did the keyword detector measure the outcome reliably?** On Qwen in the short-answer test with the full PR list, the detector reported a 46.0-point decrease. Judge A measured a 5.5-point decrease. Among valid, unflagged Qwen answers, judge A classified 6/34 as refusals before this edit and 87/126 afterwards. Disagreement also went the other way: on the original Llama, judge A classified 22 flagged answers as compliant. Without the omitted sheet these counts quantify disagreement with the judge. [Detector and judge counts](data/analysis/judge/judge.json)
4. **What was the quality cost?** For the ten-entry edit, the mean of four benchmarks (GSM8K at 256 tokens and strict whole-prompt IFEval at 1280) changed by −0.31 points on Llama and −0.21 on Qwen. Their paired 95% intervals were [−0.55, −0.09] and [−0.51, +0.09] points. Both lower bounds met the prespecified −2-point margin for that mean. Yet both fell to 50% on both parts of the everyday-word test. For the selected 500-entry edit, GSM8K credited 49 fewer Llama answers at each limit. The exploratory analysis after closeout on 26 November traced most lost items to reference solutions containing suppressed number tokens. The score alone cannot isolate a change in reasoning. For Qwen, the paired GSM8K intervals include zero at both 256 and 1024 tokens. Its strict whole-prompt IFEval score at 1280 tokens fell from 378 to 362 out of 541. The final quality tables below cover all three versions of both models. [Llama K1 scores](data/analysis/multi-l8/capability-summary.json) · [Qwen K1 scores](data/analysis/multi-q7/capability-summary.json)
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

On 400 GSM8K items with the 1024-token limit, the scorer accepted 49 fewer Llama answers after the selected edit (341 to 292). The random controls received credit on 125 items for Llama and 70 for Qwen.

### Benchmark scores

The first table gives the number of items that passed each scorer. GSM8K applies flexible numeric extraction to the answer text. IFEval uses a 1280-token limit and awards a point when every strict instruction in the prompt passes. MMLU scores the answer letter. ARC-Challenge compares answer texts using normalized likelihood.

The second table gives paired differences in percentage points with 95% intervals in brackets. Each comparison resamples the same items in pairs (10,000 draws, seed 42). These are per-comparison intervals. The two GSM8K rows use the same questions.

#### Llama 3.1 8B Instruct

<!-- quality:scores-l8 -->
| Test | Items | Original | Selected | Random |
| --- | ---: | ---: | ---: | ---: |
| GSM8K · 256 tokens | 400 | 341 | 292 | 124 |
| GSM8K · 1024 tokens | 400 | 341 | 292 | 125 |
| IFEval · strict prompt, 1280 tokens | 541 | 401 | 391 | 325 |
| MMLU · general knowledge | 1430 | 994 | 994 | 848 |
| ARC-Challenge · reasoning | 1172 | 716 | 686 | 588 |

| Test | Selected − original | Random − original | Selected − random |
| --- | ---: | ---: | ---: |
| GSM8K · 256 tokens | −12.25 [−15.75 … −8.75] | −54.25 [−59.50 … −49.25] | +42.00 [+36.25 … +47.75] |
| GSM8K · 1024 tokens | −12.25 [−15.75 … −8.75] | −54.00 [−59.25 … −48.75] | +41.75 [+35.75 … +47.50] |
| IFEval · strict prompt, 1280 tokens | −1.85 [−4.62 … +0.92] | −14.05 [−18.30 … −9.80] | +12.20 [+8.13 … +16.27] |
| MMLU · general knowledge | 0 [0 … 0] | −10.21 [−12.31 … −8.11] | +10.21 [+8.11 … +12.38] |
| ARC-Challenge · reasoning | −2.56 [−3.92 … −1.28] | −10.92 [−13.40 … −8.53] | +8.36 [+5.80 … +11.01] |
<!-- /quality:scores-l8 -->


#### Qwen2.5 7B Instruct

<!-- quality:scores-q7 -->
| Test | Items | Original | Selected | Random |
| --- | ---: | ---: | ---: | ---: |
| GSM8K · 256 tokens | 400 | 297 | 296 | 66 |
| GSM8K · 1024 tokens | 400 | 348 | 350 | 70 |
| IFEval · strict prompt, 1280 tokens | 541 | 378 | 362 | 344 |
| MMLU · general knowledge | 1430 | 1100 | 1100 | 884 |
| ARC-Challenge · reasoning | 1172 | 788 | 750 | 653 |

| Test | Selected − original | Random − original | Selected − random |
| --- | ---: | ---: | ---: |
| GSM8K · 256 tokens | −0.25 [−2.50 … +2.00] | −57.75 [−63.00 … −52.50] | +57.50 [+52.25 … +62.75] |
| GSM8K · 1024 tokens | +0.50 [−1.25 … +2.25] | −69.50 [−74.25 … −64.75] | +70.00 [+65.00 … +74.75] |
| IFEval · strict prompt, 1280 tokens | −2.96 [−5.55 … −0.37] | −6.28 [−9.61 … −2.96] | +3.33 [−0.18 … +6.84] |
| MMLU · general knowledge | 0 [0 … 0] | −15.10 [−17.41 … −12.73] | +15.10 [+12.80 … +17.41] |
| ARC-Challenge · reasoning | −3.24 [−4.52 … −2.05] | −11.52 [−14.08 … −9.04] | +8.28 [+5.63 … +11.01] |
<!-- /quality:scores-q7 -->

### What changed with the math answer limit

For each version, 400 answers at the 1024-token limit were paired with the same 400 items at 256 tokens.

<!-- quality:limits -->
| Model | Version | Wrong → correct | Correct → wrong | 1024 − 256 (pp) |
| --- | ---: | ---: | ---: | ---: |
| Llama | Original | 0 | 0 | 0 [0 … 0] |
| Llama | Selected | 0 | 0 | 0 [0 … 0] |
| Llama | Random | 3 | 2 | +0.25 [−0.75 … +1.25] |
| Qwen | Original | 51 | 0 | +12.75 [+9.50 … +16.25] |
| Qwen | Selected | 54 | 0 | +13.50 [+10.25 … +17.00] |
| Qwen | Random | 6 | 2 | +1.00 [−0.25 … +2.50] |
<!-- /quality:limits -->

At the 1024-token limit, Llama lost GSM8K credit on 52 items and gained it on three after the selected edit. Qwen lost credit on five and gained it on seven. At the 256-token limit those counts were 52 and three for Llama, and 11 and ten for Qwen. Among the 52 long-limit Llama losses, 16 edited answers re-encode to the cap and may still be incomplete. None of the five Qwen loss cases reached the cap. The saved math texts have no per-answer stop reason.

## Post hoc analysis after closeout (26 November 2026)

This exploratory analysis used the two original tokenizers and the saved benchmark answers. A **loss** is an item scored correct for the original model and incorrect after editing. **Exposed** means the tokenizer found a listed token ID in the specified text. A reference solution is one way to write a solution. Its token choices do not establish what a model must use to solve the problem. [Per-item observations, definitions and replay](data/analysis/token-exposure/README.md)

**Llama GSM8K, 1024 tokens.** The five number tokens named in the review (`00`, `26`, `36`, `64`, `75`) occurred in the reference solutions of 42 of the 52 lost items. When the final reference number contained one of the five, 15 of 16 originally correct answers lost credit (23 exposed items in total). The selected list actually contains ten number tokens. Across all ten, 45 of the 52 losses occurred on exposed solutions. The 318 unexposed items included 277 originally correct answers, seven losses and two gains. With the selected edit, the saved answers for both models contained zero listed token IDs when re-tokenized. In two Llama losses the edited answer gave 68 for 40 + 24, and 3,500 and 2,250 for amounts originally written as 35,000 and 22,500. [Grouped counts](data/analysis/token-exposure/summary.json) · [Both saved examples](data/gsm8k-comparisons/llama-01-08.md)

**Qwen and the random controls.** Qwen's selected list contained no digits. Its GSM8K change was −0.25 percentage points at 256 tokens and +0.50 at 1024. Both paired intervals include zero. Qwen's random list contained `0`, `5` and `7`. At 1024 tokens, 228 of 400 reference final answers contained one of them. All 207 originally correct answers in that group lost credit. For Llama's random list the corresponding count was 24 losses among 24 originally correct answers (26 exposed). On MMLU these lists edited the actual answer token for A on Llama and B on Qwen. All 200 originally correct A items on Llama and all 268 originally correct B items on Qwen lost credit. The random comparisons therefore include the cost of editing symbols used to give benchmark answers. [Token categories and model comparisons](data/analysis/token-exposure/tables.md) · [Item counts](data/analysis/token-exposure/summary.json)

**ARC-Challenge.** Of the selected edit's losses, 42/45 on Llama and 47/48 on Qwen had an edited token in the correct answer text. When only incorrect options contained edited tokens, Llama had zero losses and 14 gains across 136 questions. Qwen had zero losses and ten gains across 118. The wrong option actually chosen contained an edited token in just 2/45 Llama losses and 5/48 Qwen losses. These groups locate the score changes in a test that compares answer texts. [Option-level data](data/analysis/token-exposure/choice-items.csv) · [All groups, including random controls](data/analysis/token-exposure/summary.json)

### Interpretation and limits

The exploratory check on 26 November found that MMLU scored the single tokens for A, B, C and D on every item. The output-only selected edit left all four rows and the hidden state for each fixed prompt unchanged. Each letter therefore has the same logit as before, and the softmax subtracts the same log normalizer from all four when computing log probabilities. Their ranking is invariant by construction. The saved predictions confirm zero changed letters in 1,430 items on each model. This MMLU format cannot measure the cost of these selected edits. ARC scores multi-token answer texts, and its losses concentrated on exposed correct options. GSM8K requires the model to write a number that the scorer accepts. Neither score separates difficulty producing particular tokens from a broader change in reasoning. For instruction following, Qwen fell from 378 to 362 correct. Llama fell from 401 to 391, with an interval that includes zero. [Weight-scope checks](data/scope-checks/quality-restorations.json) · [Token and prediction counts](data/analysis/token-exposure/summary.json)

Each random version scored lowest on every benchmark here. There was one random list per model. The lists were unmatched on token frequency and included answer symbols absent from the selected lists. The paired bootstrap intervals capture item variability for these fixed runs and lists. They exclude run-to-run variability. On the first 200 GSM8K items at 256 tokens, repeating the original changed three Llama scores (two losses, one gain) and eight Qwen scores (five losses, three gains). On the same 162 Llama items with none of its ten selected number tokens in the reference, the edit had four losses and two gains, and the original repeat had two losses and one gain. This matched comparison applies at 256 tokens. The study has no original-model repeat at 1024. [Repeat items](data/analysis/token-exposure/repeat-items.csv) · [Grouped repeat comparison](data/analysis/token-exposure/summary.json)

[Test protocol](PROTOCOL.md) · [All 36 paired comparisons, including gains, losses and intervals](data/quality-paired.json)

## Earlier measurements and reproducibility

The four-condition screen and word tests were recorded on 23–24 November. The 1024-token refusal comparison and the quality follow-up were completed on 25 November. The stage notes preserve what was known at each point. Statements there about pending work and provisional verdicts give the status at that date. The closeout decision above governs the final interpretation.

[Reports as recorded before closeout](https://github.com/emancypage/llm-models-research/blob/d8a0a9883c3e4a80ad8d4079e4e196ddf6f22c23/reports/2026-11-23-obliteratus-vocab-surgery/results.md) · [Scored benchmark items](data/quality-items.csv) · [Reproduce the quality results](../../experiments/2026-11-23-obliteratus-vocab-surgery/README.md#reproduce-the-final-quality-comparisons) · [Study protocol](PROTOCOL.md)

In the source data, “edit alone works” and “near zero” are recorded as null. Each identifies a formal verdict that requires the omitted manual correction. [Formal verdicts](data/analysis/main/endpoints.json) · [Full-answer scores and human agreement](data/analysis/full-score.json)
