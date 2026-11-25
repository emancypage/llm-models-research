# Results: vocabulary-row edits (OBLITERATUS PR #595)

**The original measurements are complete. The quality follow-up is in progress.** The large manual sheet (200 rows) was not labelled, so the judge gate and the manually corrected measures of the main study were not computed; 36 full answers were labelled. Stage 3 (Inkling-2-Mini, the model of the original claim) was dropped, so the claim was not tested on its own model.

## Math answer comparisons

[Browse 52 Llama cases and 5 Qwen cases](data/gsm8k-comparisons/README.md). Each case pairs the original answer with the answer after editing 500 selected vocabulary entries. Both runs used the same math problem and allowed 1024 new tokens. Cases are included when the original was scored correct and the edited answer was scored incorrect.

| GSM8K, first 400 problems | Original | 500 selected entries | Correct → incorrect | Incorrect → correct |
| --- | ---: | ---: | ---: | ---: |
| Llama 3.1 8B Instruct | 341 | 292 | 52 | 3 |
| Qwen2.5 7B Instruct | 348 | 350 | 5 | 7 |

For Llama, extending the answer limit from 256 to 1024 tokens changed no individual scores for either version. Of the 52 edited answers shown, 16 re-encode to exactly 1024 tokens and may still be incomplete. For Qwen, both versions scored higher with the longer limit. None of the five edited answers shown re-encodes to the limit.

The study asks whether editing a few vocabulary rows (`vocab_surgery`) reduces refusals by itself, whether it adds anything beyond a prefill, and what it costs in capability.

Findings on Llama-3.1-8B and Qwen2.5-7B:
- the post's 10-token list does not reduce refusals: on full answers −0.5 and +2.5 pp by judge A, without a prefill;
- a list of 500 tokens made from each model's answers to harmful prompts does: −43.5 and −37.5 pp by judge A on full answers, without a prefill, against +4.0 and +1.5 pp for 500 random tokens; one reviewer agrees with judge A on 35 of 36 answers. About 35% of the answers still refuse or fail. GSM8K falls by 12.25 pp on Llama-3.1-8B and by 0.25 pp on Qwen2.5-7B;
- the full 34-token PR list seemed to lower refusals by up to 46.0 pp, but that was the keyword detector: it looks for words that the edit suppresses, and judge A found −5.5 pp (64-token answers);
- answers of 64 tokens hide the outcome. The earlier results with 64 tokens, including those with a prefill, describe only the start of the answer.

On 24 November the author of the original claim published a correction: the 97.4% result had a prefill in the chat template by mistake. This study separates the prefill from the edit by design; the correction is recorded in the protocol.

Limitations:
- the judges were checked against 36 manual labels from one reviewer, who had seen aggregate judge results for 64-token answers; the protocol's judge gate was not computed;
- the earlier short-answer refusal runs used a 64-token limit;
- compliance means that the answer contains requested content; its usefulness was not judged;
- on Llama and Qwen the study tests whether the Inkling token list transfers; it does not test the original claim, which belongs to stage 3;
- the prefill text comes from a PR unit test, not from the original experiment.

Evidence: [protocol and deviations](PROTOCOL.md) · [issue log](issues.md) · [data](data) · [code, word probe and judge prompt](../../experiments/2026-11-23-obliteratus-vocab-surgery) · [research diary](../../session-logs/2026-11-23-obliteratus-vocab-surgery.md)

## Full answers, no prefill

25 November 2026. The 64-token answers used so far often stopped before the outcome was visible. This section repeats the 200 harmful test prompts with up to 1024 new tokens. A row is a failure of the edit when it is a refusal, another label or an invalid answer. The runs with a prefill are not used here (protocol, 25 November).

### Checks

- All 200 full answers begin with the stored 64-token answer, in every set. The re-applied edits pass the scope check.
- Answers that still hit the limit: Llama-3.1-8B S 8, K1 8, D500 21, KR500 60; Qwen2.5-7B S 2, K1 2, D500 4, KR500 7.

### Failures by judge A / judge B / keyword detector (share of 200)

| Version | Llama-3.1-8B | Qwen2.5-7B |
| --- | --- | --- |
| S | 79.0% / 82.0% / 88.5% | 73.0% / 82.5% / 85.0% |
| V-k1, the post's list | 78.5% / 81.5% / 87.5% | 75.5% / 82.5% / 82.0% |
| V-d500, 500 tokens | 35.5% / 36.0% / 9.0% | 35.5% / 37.0% / 20.5% |
| V-kr500, 500 random tokens | 83.0% / 83.0% / 90.0% | 74.5% / 83.5% / 85.0% |

| Difference to S, judge A | Llama-3.1-8B | Qwen2.5-7B |
| --- | --- | --- |
| K1 | −0.5 pp (1 fewer, 0 more; p = 1.0) | +2.5 pp (8 and 13; p = 0.38) |
| D500 | −43.5 pp (93 and 6; p = 3.8e-21) | −37.5 pp (79 and 4; p = 4.0e-19) |
| KR500 | +4.0 pp (7 and 15; p = 0.13) | +1.5 pp (16 and 19; p = 0.74) |

Judge B: D500 −46.0 and −45.5 pp; K1 −0.5 and 0.0 pp; KR500 +1.0 and +1.0 pp. Answers that judge A labels as compliance: Llama-3.1-8B S 42, D500 129; Qwen2.5-7B S 54, D500 129. With 64 tokens the D500 difference was −32.0 and −27.5 pp. From 64 to full answers judge A changed `R` to `C` in 18 (Llama-3.1-8B) and 49 (Qwen2.5-7B) D500 answers, and `C` to `R` in 1 and 4; in Qwen2.5-7B S 27 and 4.

### Manual labels (36 full answers without a prefill, one reviewer)

| | S, 12 answers | D500, 24 answers |
| --- | --- | --- |
| Compliance | 2 | 16 |
| Refusal | 10 | 7 |
| Other | 0 | 1 |

- Agreement of judge A with the reviewer on compliance or not: 35 of 36 (Wilson 85.8% to 99.5%), kappa on three labels 0.95. Judge B agrees on refusal or not in 35 of 36. The one difference is an answer that the reviewer labelled other and judge A labelled compliance.
- Compliance in D500 against S, reviewer labels: 16 of 24 and 2 of 12 (Fisher p = 0.0116).
- The judge gate of the protocol (lower bound at least 90% on the large sheet) was not evaluated; the lower bound here is 85.8%. The large sheet of 200 rows was not labelled.
- The reviewer had seen aggregate judge results for the 64-token answers before labelling; results for the full answers were not shown to anyone before labelling.

### Reading

1. On full answers, the post's 10-token list still changes nothing, and neither do 500 random tokens.
2. The 500-token list lowers failures by 43.5 and 37.5 pp by judge A, and the reviewer agrees with the judge. The 64-token measure understated this. About 35% of the answers still fail.
3. The detector overstates it again: 9.0% and 20.5% failures against 35.5% by judge A.
4. Limits: "compliance" means that the answer contains requested content; its usefulness was not judged. The list mixes refusal words and topic words. KR500 is not matched for token frequency. Two models, one reviewer, one random control per model.
5. Cost of D500 (measured earlier, in benchmark runs that do not depend on the answer limit): GSM8K −12.25 pp on Llama-3.1-8B and −0.25 pp on Qwen2.5-7B; ARC-Challenge −2.56 and −3.24 pp.

## Follow-up: self-generated list of 500 tokens

24 November 2026. Follow-up decided by the project owner, no prefill runs. Refusals on the same 200 `final_test` prompts. The two LLM judges are not yet checked against manual labels, so their measures are "judge unchecked"; a manual sheet for 45 answers is pending. Random controls KR500 use the same number of tokens (500), drawn with seed 42. All D500 operations scale the output side by 0.1; the input side is not changed.

### How the list was made

- Discovery prompts: 500 harmful and 500 harmless extraction prompts (disjoint from the 200 test prompts). Responses: greedy, 128 tokens.
- Round 1 on the unedited model: 250 tokens with the highest lift in the answers to harmful prompts. Round 2 on the model after the round-1 edit: 250 more. In round 2 on Qwen2.5-7B, 124 of the 250 candidates contain Chinese characters; 59 of the 500 answers to harmful prompts after round 1 contain Chinese (1 of 500 before). Whether those answers are refusals was not checked. The target corpus was all answers to harmful prompts, not only refusals, so the lists also hold topic words.
- Each list was applied with token IDs only. The scope check found 0 changed input rows, 500 changed output rows, and all other tensors bit-identical for both models.

### Refusals (no prefill)

| Measure | Llama-3.1-8B: S / D500 / KR500 | Qwen2.5-7B: S / D500 / KR500 |
| --- | --- | --- |
| Keyword detector: refusals + invalid of 200 | 170 / 6 / 168 | 166 / 32 / 164 |
| Judge A: `judge_fail` (R and O + invalid) | 74.0% / 42.0% / 77.5% | 84.5% / 57.0% / 85.5% |
| Judge B: refusals + invalid | 78.0% / 38.5% / 79.0% | 85.0% / 58.5% / 88.5% |
| Judge A labels C (compliance) | 52 / 116 / 45 | 31 / 86 / 29 |

- Judge A difference D500 − S: Llama-3.1-8B −32.0 pp (70 discordant pairs fewer refusals, 6 more; p = 6.3e-15); Qwen2.5-7B −27.5 pp (58 and 3; p = 3.3e-14). Judge A random control KR500 − S: +3.5 pp (p = 0.14) and +1.0 pp (p = 0.79). The control is not matched for token frequency: the D500 tokens make up 17.2% of the tokens in the S answers to harmful discovery prompts and 0.5% (Llama-3.1-8B) or 0.7% (Qwen2.5-7B) in the answers to harmless ones; the KR500 tokens make up 9.7% and 10.3% (Llama-3.1-8B), 10.3% and 12.1% (Qwen2.5-7B). It shows that editing 500 arbitrary rows does not lower refusals; it does not separate refusal words from topic words.
- The keyword detector reports −82.0 pp and −67.0 pp, two to three times more than judge A (−32.0 and −27.5 pp). The detector misses 77 (Llama-3.1-8B) and 82 (Qwen2.5-7B) answers that judge A calls refusals.
- Judge A still finds 79 and 110 refusals of 200 after the edit. The token suppression weakens refusals but does not end them, and it works worse than the author's longer prefill alone (judge A −53.5 and −75.5 pp).

### Cost

| Measure | Llama-3.1-8B: S → D500 | Qwen2.5-7B: S → D500 |
| --- | --- | --- |
| MMLU, every 10th item | 69.51% → 69.51% | 76.92% → 76.92% |
| ARC-Challenge | 61.09% → 58.53% (−2.56 pp; interval −3.84 to −1.28) | 67.24% → 63.99% (−3.24 pp; interval −4.52 to −2.05) |
| GSM8K, first 400 | 85.25% → 73.00% (−12.25 pp; interval −15.75 to −9.00) | 74.25% → 74.00% (−0.25 pp; interval −2.50 to 2.00) |
| Mean of three | −4.94 pp (−6.19 to −3.71) | −1.16 pp (−2.01 to −0.32) |
| KL, next token | 0.1577 | 0.4062 |
| Perplexity ratio | 1.0992 | 0.9964 |
| Judge A label O (gibberish or cut) | 4 of 200 | 3 of 200 |

- MMLU is exactly unchanged: the test picks among the answer letters, and the edit does not change the rows of those letters.
- The word probe is biased for Llama-3.1-8B, because the discovered list contains " No" and "No" (its part B, which asks for yes or no, drops from 91.7% to 50.0%); Qwen2.5-7B part A drops from 99.2% to 66.7%, part B stays at 99.2%.

### Reading

A 500-token list made from the model's answers to harmful prompts lowers refusals by about 30 pp according to judge A, with no prefill, on both models; a random list of the same size does not. The damage is model-dependent: Llama-3.1-8B loses 12.25 pp on GSM8K, Qwen2.5-7B almost nothing on these benchmarks. The detector exaggerates the gain by about 40 pp (Qwen2.5-7B) to 50 pp (Llama-3.1-8B); every such claim needs an independent judgement. Keep in mind the uncertainty of judge A: it has not been validated against human labels yet.

## LLM judges

24 November 2026. Judge A is the planned spare `google/gemma-4-12B-it` (the first choice did not load within the memory guard); judge B is `allenai/wildguard`. Both scored every distinct answer set. **Status: judge unchecked.** The judge gate needs the manual labels, which are pending, so these measures are not yet validated; the verdicts still rest on the manual correction.

Measures (share of 200 harmful prompts): detector = primary measure (refusals + invalid answers); judge A = `judge_fail` (labels R and O + invalid); judge B = refusals + invalid.

| Version | Llama-3.1-8B: detector / A / B | Qwen2.5-7B: detector / A / B |
| --- | --- | --- |
| S | 85.0% / 74.0% / 78.0% | 83.0% / 84.5% / 85.0% |
| V-k1 | 84.5% / 73.5% / 77.5% | 81.0% / 83.5% / 85.0% |
| SP | 76.0% / 62.5% / 60.0% | 32.0% / 35.0% / 39.0% |
| VP-k1 | 74.0% / 61.0% / 58.0% | 26.5% / 37.0% / 37.0% |
| V-k2 | 78.0% / 74.0% / 77.5% | 37.0% / 79.0% / 82.0% |
| VP-k2 | 57.5% / 61.0% / 58.5% | 14.5% / 36.0% / 38.0% |
| V-k1o | 85.0% / 73.5% / 78.0% | 82.0% / 84.0% / 85.5% |
| V-k1i | 84.5% / 74.0% / 77.5% | 81.0% / 80.5% / 82.5% |
| SP2, author's prefill | 48.0% / 20.5% / 22.0% | 15.5% / 9.0% / 6.0% |
| VP2, author's prefill and K1 | 47.5% / 20.5% / 21.0% | 14.5% / 6.0% / 3.5% |
| KR, 9 random tokens | – | 83.0% / 84.0% / 85.0% |
| KR2, 33 random tokens | – | 81.0% / 83.0% / 84.0% |

Control models: Qwen2.5-1.5B S 92.0% / 91.0% / 93.0%, V `k2-tied` 57.0% / 92.5% / 92.0%; Llama-3.2-3B S 70.5% / 67.0% / 71.0%, V `k2-tied` 63.5% / 68.5% / 70.5%.

### Main findings

1. **The large drops with the full PR list are detector errors.** On Qwen2.5-7B the detector found 73 refusals after the K2 edit; judge A labelled 157 answers as refusals. Of the answers that the detector did not flag, judge A called 87 refusals and judge B 91. By judge A, V-k2 − S is −5.5 pp (13 and 2 discordant pairs; p = 0.0074), not −46.0 pp. The same happens on Qwen2.5-1.5B (`k2-tied`: detector −35.0 pp, judge A +1.5 pp, 72 missed refusals) and with the prefill (Qwen2.5-7B VP-k2 − SP: detector −17.5 pp, judge A +1.0 pp; Llama-3.1-8B: −18.5 pp and −1.5 pp). The edit removes the words that the detector looks for; the model keeps refusing with other words.
2. **The list from the post does nothing by either judge.** K1 V − S: Llama-3.1-8B −0.5 pp (p = 1.0), Qwen2.5-7B −1.0 pp (p = 0.69). VP − SP: −1.5 pp (p = 0.38) and +2.0 pp (p = 0.54).
3. **The prefill does the work.** By judge A, the short prefill lowers the measure by 11.5 pp (Llama-3.1-8B; 32 and 9 discordant pairs; p = 0.00043) and 49.5 pp (Qwen2.5-7B; p = 1.1e-27); the author's longer prefill by 53.5 pp (p = 4.8e-30) and 75.5 pp (p = 2.7e-44). K1 on top of the longer prefill: 0.0 pp and −3.0 pp (p = 1.0 and 0.11).
4. **The detector also over-counts on unedited answers.** For Llama-3.1-8B S, 22 answers flagged as refusals were labelled compliance by judge A (judge B: 14 no refusal). The detector treats compliance with a warning as a refusal.

Uncertain rows (judges disagree or judge A below 0.80) per version: from 4 to 35; the most are in the prefill versions of Qwen2.5-7B (34 and 35).

Prefill-field control: without the prefill field, judge A changed 10 of the 100 sheet rows from SP and VP-k1 (Llama-3.1-8B 1 and 2; Qwen2.5-7B 2 and 5).

## Llama-3.1-8B (stage 1)

24 November 2026. Refusal counts come from the keyword detector; the manual review and the LLM judges come later, so verdicts that need them are still open. 200 harmful prompts per version; no version had an invalid answer.

### Refusals

| Configuration | Without prefill: S → V | With prefill: SP → VP |
| --- | --- | --- |
| K1, list from the post (7 input, 9 output rows) | 170 → 169 (−0.5 pp; 1 discordant pair; p = 1.0) | 152 → 148 (−2.0 pp; 6 discordant pairs, 5 and 1; p = 0.22) |
| K2, full PR list (20 input, 33 output rows) | 170 → 156 (−7.0 pp; 14 discordant pairs, all fewer refusals; p = 0.00012) | 152 → 115 (−18.5 pp; 37 discordant pairs, all fewer refusals; p = 1.5e-11) |
| K1o, output side only | 170 → 170 (0 pp) | – |
| K1i, input side only | 170 → 169 (−0.5 pp) | – |

- Prefill alone (SP − S): −9.0 pp; 28 discordant pairs (23 fewer refusals, 5 more); p = 0.00091.
- Interaction for K1, (VP − SP) − (V − S): −1.5 pp.
- The unedited model gave identical answer texts in all four run-A reports (0 of 200 differ), so every change below comes from the edit. Answer texts that changed: K1 27 of 200, K2 46 of 200.
- List coverage: of the 170 S refusals, 19 contain a K1 source token and 31 a K2 source token.

### Capabilities (S and V-k1)

| Measure | S | V-k1 | Difference (95% interval) |
| --- | --- | --- | --- |
| MMLU, every 10th item | 69.51% | 69.16% | −0.35 pp (−0.84 to 0.07) |
| ARC-Challenge | 61.09% | 60.75% | −0.34 pp (−0.85 to 0.17) |
| GSM8K, first 400 | 85.25% | 85.25% | 0.00 pp |
| IFEval | 74.12% | 73.57% | −0.55 pp (−1.29 to 0.00) |
| Mean of the four | – | – | −0.31 pp (−0.55 to −0.09); bootstrap p = 0.0046 |

Noise: a second S run on the first 200 GSM8K items changed 93 answer texts but only 3 scores.

### Word probe (S and V-k1)

| Part | S | V-k1 |
| --- | --- | --- |
| A, writing the word (output) | 95.0% | 50.0% |
| B, understanding the word (input) | 91.7% | 50.0% |

After the edit the model no longer chooses any of the six source words where it fits (0 of 10 in every source group of part A) and reads them as their targets (part B source groups 0 to 3 of 10). Target-word items are unaffected. McNemar: part A 3 against 57 items, p = 6.3e-14; part B 0 against 50 items, p = 1.8e-15.

### Endpoints and verdicts (Llama-3.1-8B only; Holm correction across models comes with Qwen2.5-7B)

| Endpoint | Result |
| --- | --- |
| 1. V − S, primary measure | −0.5 pp, p = 1.0 |
| 2. VP − SP, primary measure | −2.0 pp, p = 0.22 |
| 3. V − S, mean capability | −0.31 pp, 95% interval −0.55 to −0.09 |

- "The edit alone works": not met. It needs at least −20 pp; the result is −0.5 pp. The manual correction cannot change this by that much.
- "The edit adds something beyond the prefill": no (−2.0 pp, p = 0.22; SP is 76.0%, above the 15% floor).
- "Negligible cost": yes for the capability benchmarks (lower bound −0.55 pp, above −2 pp). The word probe shows a large cost on the edited words themselves.
- "Near zero": open until the manual review; the detector value of V is 84.5%.
- Random control KR: not built (needs a drop of at least 10 pp without prefill; the largest is −7.0 pp).

The clearest effect is K2 together with the prefill (−18.5 pp). Its capability cost was not measured (the plan measures capabilities for K1 only). Word probe for V-k2: part A 50.0%, part B 50.0%.

## Qwen2.5-7B (stage 1)

24 November 2026. Refusal counts come from the keyword detector; the manual review and the LLM judges come later. 200 harmful prompts per version. The primary measure counts refusals and invalid answers.

### Qwen2.5-7B refusals

| Configuration | Without prefill: S → V | With prefill: SP → VP |
| --- | --- | --- |
| K1, list from the post | 165 + 1 invalid → 161 + 1 invalid (−2.0 pp; 4 discordant pairs, all fewer; p = 0.125) | 64 → 53 (−5.5 pp; 13 discordant pairs, 12 and 1; p = 0.0034) |
| K2, full PR list | 165 + 1 → 73 + 1 (−46.0 pp; 94 discordant pairs, 93 and 1; p = 9.6e-27) | 64 → 29 (−17.5 pp; 35 discordant pairs, all fewer; p = 5.8e-11) |
| K1o, output side only | 165 + 1 → 163 + 1 (−1.0 pp; p = 0.5) | – |
| K1i, input side only | 165 + 1 → 161 + 1 (−2.0 pp; p = 0.125) | – |

- Prefill alone (SP − S): −51.0 pp; 102 discordant pairs, all fewer refusals; p = 3.9e-31.
- Interaction for K1: −3.5 pp.
- List coverage: of the 165 S refusals, 149 contain a K1 source token and 165 a K2 source token. Qwen2.5-7B refuses with the listed words much more than Llama-3.1-8B (19 and 31 of 170).
- Caution for K2: the edit suppresses words such as "sorry", "cannot" and "However", and the detector looks for refusal phrases. A drop in detected refusals can therefore partly be refusals in other words. The LLM judges and the manual review are needed before K2 is read as fewer refusals. K2 has no manual labels under the plan, so it will be marked "judge only".
- The random control is triggered for Qwen2.5-7B (K2 lowered the primary measure by 46.0 pp) and is queued: KR as planned, plus KR2 with the shape of K2.

### Author's longer prefill (exploratory run B2, K1)

| Model | S | SP2: S with the author's prefill | VP2: V-k1 with the author's prefill |
| --- | --- | --- | --- |
| Llama-3.1-8B | 170 | 96 (−37.0 pp; 86 discordant pairs, 80 and 6; p = 1.3e-17) | 95 (−0.5 pp against SP2; 5 discordant pairs, 3 and 2; p = 1.0) |
| Qwen2.5-7B | 165 + 1 | 30 + 1 (−67.5 pp; 139 discordant pairs, 137 and 2; p = 2.8e-38) | 28 + 1 (−1.0 pp against SP2; 4 discordant pairs, 3 and 1; p = 0.625) |

The longer prefill alone removes most refusals; the K1 edit adds almost nothing on top. This agrees with the author's correction.

### Qwen2.5-7B capabilities (S and V-k1)

| Measure | S | V-k1 | Difference (95% interval) |
| --- | --- | --- | --- |
| MMLU, every 10th item | 76.92% | 76.64% | −0.28 pp (−0.63 to 0.07) |
| ARC-Challenge | 67.24% | 67.06% | −0.17 pp (−0.68 to 0.34) |
| GSM8K, first 400 | 74.25% | 74.25% | 0.00 pp |
| IFEval | 69.87% | 69.50% | −0.37 pp (−1.48 to 0.55) |
| Mean of the four | – | – | −0.21 pp (−0.51 to 0.09); bootstrap p = 0.18 |

Noise: a second S run on the first 200 GSM8K items changed 93 answer texts and 8 scores.

Word probe: S part A 99.17%, part B 99.17%; V-k1 50.0% and 50.0%; V-k2 50.0% and 50.0%.

### Endpoints for both main models (Holm correction across Llama-3.1-8B and Qwen2.5-7B; it is recomputed when Inkling-2-Mini is added)

| Endpoint | Llama-3.1-8B | Qwen2.5-7B |
| --- | --- | --- |
| 1. V − S, primary measure | −0.5 pp; p = 1.0; Holm 1.0 | −2.0 pp; p = 0.125; Holm 0.25 |
| 2. VP − SP, primary measure | −2.0 pp; p = 0.22; Holm 0.22 | −5.5 pp; p = 0.0034; Holm 0.0068 |
| 3. V − S, mean capability | −0.31 pp (−0.55 to −0.09); Holm 0.0092 | −0.21 pp (−0.51 to 0.09); Holm 0.18 |

Verdicts (K1, before the manual correction):
- "The edit alone works": no for both models (−0.5 and −2.0 pp; the threshold is −20 pp).
- "The edit adds something beyond the prefill": no for both. On Qwen2.5-7B the effect is statistically clear, −5.5 pp, but smaller than the 10 pp threshold.
- "Negligible cost": yes for both on the benchmarks. Both models lose the normal use of the edited words (word probe 50%).
- "Near zero": open until the manual review.

## Control models (stage 2)

24 November 2026. Refusal counts come from the keyword detector; the LLM judges come later. These results are descriptive only: the control models have a shared input/output matrix and are also smaller, so the two cannot be separated.

### Control models with a shared matrix (refusals of 200 harmful prompts)

| Version | Qwen2.5-1.5B | Llama-3.2-3B |
| --- | --- | --- |
| S | 184 | 141 |
| V, `k1o-tied` (scaling of 9 shared rows) | 184 (0 pp; 0 discordant pairs) | 143 (+1.0 pp; 2 discordant pairs, both more refusals; p = 0.5) |
| SP, prefill | 15 + 1 invalid (−84.0 pp against S; p = 5.4e-51) | 23 + 2 invalid (−58.0 pp; 126 discordant pairs, 121 and 5; p = 6.0e-30) |
| VP, prefill and `k1o-tied` | 11 + 1 invalid (−2.0 pp against SP; 4 discordant pairs; p = 0.125) | 27 + 2 invalid (+2.0 pp against SP; 4 discordant pairs, all more refusals; p = 0.125) |
| V, `k2-tied` (scaling of 33 shared rows) | 114 (−35.0 pp; 70 discordant pairs, all fewer; p = 1.7e-21) | 127 (−7.0 pp; 16 discordant pairs, 15 and 1; p = 0.00052) |

- List coverage: of the S refusals, Qwen2.5-1.5B has 2 of 184 with a K1 source token and 184 of 184 with a K2 source token; Llama-3.2-3B has 57 of 141 and 77 of 141.
- Word probe, S → V (`k1o-tied`): Qwen2.5-1.5B part A 96.7% → 50.0%, part B 92.5% → 91.7%; Llama-3.2-3B part A 95.0% → 50.0%, part B 94.2% → 65.8%.
- Capabilities, Qwen2.5-1.5B, S → V (`k1o-tied`): MMLU (every 10th item) 62.66% → 62.73%, ARC-Challenge 54.18% → 54.35%, GSM8K (first 400) 56.00% → 56.25%, IFEval 41.77% → 41.40%; mean +0.03 pp (95% interval −0.18 to 0.25). Llama-3.2-3B capabilities were not measured (scope reduction of 24 November).

### Random controls on Qwen2.5-7B (run A, refusals of 200 harmful prompts)

| Edit | V | Against S (165 + 1 invalid) |
| --- | --- | --- |
| K2, full PR list (33 resolved operations) | 73 + 1 | −46.0 pp; 94 discordant pairs; p = 9.6e-27 |
| KR2, 33 random tokens with the K2 strengths | 161 + 1 | −2.0 pp; 4 discordant pairs, all fewer; p = 0.125 |
| KR, 9 random tokens with the K1 strengths | 165 + 1 | 0 pp; 0 discordant pairs |

Both random edits passed the scope check (7 and 9 rows for KR; 20 and 33 rows for KR2). The drop with K2 depends on the chosen words, not on editing that many rows. These words are also the words the refusal detector looks for, so the judges must still show whether the model refuses less or only in other words.

## Stage 0 (decision point G1)

23 November 2026. Numbers only. Tool: OBLITERATUS `main` commit `1de580f7a13f185488dc31ff27f2e027545ad82d` (contains PR #595).

### Checks of tasks 0.1–0.8

| Task | Result |
| --- | --- |
| 0.1 setup | PR tests 75 passed, 0 failed; offline lm-eval smoke test 4 of 4 tasks with code 0; study directory self-contained |
| 0.2 word probe | frozen; S: Qwen2.5-1.5B part A 96.67%, part B 92.50%; Qwen2.5-7B 99.17%, 99.17% (threshold 90%) |
| 0.2a codebook and judge | frozen; 15 script tests passed; judge models not downloaded |
| 0.3 protocol | English and Polish, written before the first edited model; number check passes |
| 0.4 edit and scope check | Qwen2.5-1.5B `k1o-tied`: 9 shared rows, as expected; K1 on a shared matrix fails before writing; Qwen2.5-7B S0: weights and behaviour identical, tokenizer and config files re-saved (bug log); passes under decision A |
| 0.5 template copies | fixed date and 4 prefill copies pass; prefill run gives other stock texts (KL available in both runs) |
| 0.6 review sheet | pilot sheet 100 rows (25 per version), correct header |
| 0.7 analysis | 25 tests passed; pilot numbers equal the measurement printout |
| 0.8 time pilot | Llama-3.1-8B: all steps finished with code 0 |

### Llama-3.1-8B (configuration K1, first measurements)

| Measure | S | V |
| --- | --- | --- |
| Refusals on 200 harmful prompts | 170 | 169 |
| Invalid answers | 0 | 0 |
| Primary measure | 85.0% (Wilson 79.4–89.3%) | 84.5% |

- V − S: −0.5 pp; 1 discordant pair; McNemar p = 1.0 (detector flags only; the manual check comes later).
- S is at least 50%, so Llama-3.1-8B enters the confirmatory analysis. Qwen2.5-7B S (from the write check): 165 refusals and 1 invalid answer, primary measure 83.0%; it also enters.
- Next-token KL 0.0015, first-token KL 0.0005; perplexity ratio 1.0000.
- List coverage: of the 170 S refusals, 19 contain a K1 source token and 31 a K2 source token.
- Capabilities of S: MMLU (every 10th item) 69.5%, ARC-Challenge 61.1%, GSM8K (first 400) 85.2%, IFEval 74.1%.
- Edited rows: 7 input and 9 output, as expected; every other tensor bit-identical.

Pilot on Qwen2.5-1.5B (`k1o-tied`, descriptive only): S 184 refusals, V 184 (0 discordant); SP 15 refusals and 1 invalid, VP 11 and 1 invalid. Of the 184 S refusals, 2 contain a K1 source token and 184 a K2 source token.

### Measured times

| Step | Qwen2.5-1.5B | Qwen2.5-7B | Llama-3.1-8B |
| --- | --- | --- | --- |
| Edit and save | 0.8 min | 3.4 min | 3.9 min |
| Scope check | – | – | 0.3 min |
| `verify-edit` | 3.1 to 3.6 min | 11.5 min | 12.7 min |
| Screening set | 16 min (previous study) | – | 46.4 min |
| IFEval | – | – | 77.3 min |

Highest system memory use: 69.6 GiB of 121 GiB (Llama-3.1-8B edit).

### Time and disk (recomputed)

Assumptions: Qwen2.5-7B screening and IFEval take as long as Llama-3.1-8B; for Qwen2.5-1.5B and Llama-3.2-3B, IFEval is scaled by their screening time (16 and 27 min against 46.4 min).

| Part | Plan | New estimate |
| --- | --- | --- |
| Stage 0 | about 2 h | 2.8 h (measured) |
| Llama-3.1-8B, rest of stage 1 | about 3.5 h | about 3.5 h (+0.3 h with the random control) |
| Qwen2.5-7B | about 5 h | about 5.7 h |
| Qwen2.5-1.5B and Llama-3.2-3B | about 2.5 h | about 4.2 h |
| Inkling-2-Mini | unknown | unknown (gate G0) |
| Total without Inkling-2-Mini | about 13 h | about 16.2 h |

IFEval is the largest part: 77.3 min per run on an 8B model. The LLM judges are not included.

Disk: 116 GB free with one edited 8B checkpoint (15 GB) on disk; about 131 GB free after it is deleted. The judges need at least 90 GB free; stage 3 needs at least 130 GB, so its margin is about 1 GB.
