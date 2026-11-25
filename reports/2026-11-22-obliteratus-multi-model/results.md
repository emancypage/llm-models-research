# LoRA repair after the refusal projection: final results (Q1, Q3, damage ladder)

Written on 23 November 2026. This is the final report of the shortened plan (protocol, "Shortened plan", 23 November). It covers Q1 (Qwen2.5-1.5B-Instruct), Q3 (Qwen2.5-3B-Instruct), the Q1 damage ladder (Z2) and L3 with the family recipe (Z1). The Q1 details are in [Q1 interim results](data/q1/partial-results.md). All computation ran on an on-premise machine.

Codes: S is the stock model. P is the projection, step 1 of the recipe: the accepted recipe for Q1, and for Q3 the recipe that the search on `tune` selected (not confirmed with `recipe confirm`). R0 is P after `adapter.lora_repair` with seed 42. The repair data are the answers of S to 250 harmless prompts, with refusals removed (rank 8, 1 epoch). P_A and R_A are the same at level A of the damage ladder. RK, RB, RG, PS and RS are the extra Q1 arms of the partial report. "Generative tests" are GSM8K and IFEval, where the model writes a free answer. Differences are in percentage points (pp), with 95% bootstrap intervals. An answer is "at the limit" when its text has at least 255 tokens after it is tokenized again. `verify-edit` has three required gates. The capability gate could not be run for any arm (no backend), so the tool's own verdict is INCOMPLETE. "Both required gates" in this report means `heldout_refusal` and `collateral`. The KL and perplexity gates are advisory.

## Short answer

- **When the recipe hardly damages capability (Q1, Q3), there is little to recover.** With seed 42 the repair keeps the mean within the 2 pp margin in both models (endpoint 1). In Q1 the intervals of the other two seeds reach below −2 pp (−2.03 and −2.16 pp). The main effect of the repair is on the form of the generative answers, and this effect differs by model. In Q1 it weakens the GSM8K answer format (`strict-match` −9.86 pp; answers ending with `#### number`: 787 → 508). In Q3 it makes the answers shorter, so more of them fit in the 256-token limit (GSM8K +6.14 pp, but no measurable gain, −0.41 pp [−2.59, +1.77], on the items where neither answer reaches the limit).
- **When the projection really damages capability (Z2, level A; exploratory, one rung, one seed), the repair recovers about three quarters.** Recovered share: 0.76 [0.66, 0.86]. About 80% of the GSM8K and IFEval damage comes back, but MMLU hardly comes back.
- **With self-distilled repair data, the edit mostly stays.** Some refusals come back: 9 vs 1 prompts in Q1 (p = 0.021, exploratory), 10 vs 0 in Z2 (p = 0.002, exploratory), 3 vs 1 in Q3 (p = 0.625, confirmatory, not significant). With refusals in the repair data (RK, Q1), the edit is undone. KL is above the advisory budget for every projected and repaired arm, before and after the repair.
- These results apply to these two models, this repair corpus and these settings.

## Confirmatory endpoints

The Holm correction works within each endpoint, across the models of that endpoint.

| Endpoint | Model | Result | p | p (Holm) | Reading |
| --- | --- | --- | ---: | ---: | --- |
| 1. R0−P, mean of 4 tests | Q1 | −0.33 pp [−1.40, +0.74] | 0.546 | 0.546 | no drop (seed 42; seeds 43 and 44 in the Q1 section) |
| 1. R0−P, mean of 4 tests | Q3 | +1.90 pp [+0.86, +2.95] | 4.0×10^−4 | 8.0×10^−4 | no drop |
| 1. R0−P, mean of 4 tests | both, equal weight | +0.78 pp [+0.04, +1.54] | 0.040 | — | no drop; the sign differs between the models, and the interval is above zero because of Q3 |
| 2. RK−P, harmful refusals | Q1 | only RK 138, only P 0 | 5.7×10^−42 | — | refusals come back |
| 3. R0−P, GSM8K `strict-match` | Q1 | −9.86 pp [−12.51, −7.20] | 1.0×10^−12 | 2.1×10^−12 | format partly lost |
| 3. R0−P, GSM8K `strict-match` | Q3 | +4.17 pp [+2.96, +5.38] | 4.1×10^−12 | 4.1×10^−12 | rise; S is at a floor of 1.06% |
| 4. RS−PS, mean of 4 tests | Q1 | +0.26 pp [−0.75, +1.27] | 0.616 | — | no drop; recovered share not computed (S−PS 1.00 pp) |
| 5. R0−P, harmful refusals | Q3 | only R0 3, only P 1 | 0.625 | — | no significant change |
| 6. R0−P, IFEval prompt strict | Q3 | +2.03 pp [−1.29, +5.36] | 0.289 | — | no significant change |

## Q3 (Qwen2.5-3B): generative tests first

- **The projection damages Q3 a little.** P−S on the mean: −1.41 pp [−2.45, −0.39], a drop. The estimate is under 2 pp, but the interval reaches −2.45 pp, so a drop larger than 2 pp is not ruled out. Most of it is GSM8K (−3.56 pp) and MMLU (−1.15 pp). IFEval −1.11 pp is not significant, and ARC does not change (+0.17 pp).
- **GSM8K: R0 gains 6.14 pp [+3.87, +8.49] over P, and the data point to shorter answers as the main source.** In Q3 many GSM8K answers reach the 256-token limit: S 487, P 534 and R0 389 of 1319. The median length is 227, 235 and 206 tokens. A post hoc check (recorded in the protocol before it was run) looked at the 735 items where neither the P answer nor the R0 answer reaches the limit. There R0−P is −0.41 pp [−2.59, +1.77], McNemar p = 0.80. Of the 164 items that only R0 solves, the P answer reaches the limit in 128. Of the 83 items that only P solves, the R0 answer reaches the limit in 41.
- **Endpoint 3 (GSM8K `strict-match`) goes up, the opposite of Q1.** +4.17 pp, p = 4.1×10^−12. S has a floor here: its `strict-match` is 1.06%, and only 11 of its answers end with `#### number`. R0 ends 82 answers this way, P 5. So a drop could hardly be seen in Q3 (recorded in the protocol before the P and R0 results).
- **Endpoint 6 (IFEval): no significant change.** R0−P +2.03 pp [−1.29, +5.36]. 50 items are correct only for R0 and 39 only for P, McNemar p = 0.289.
- **MMLU and ARC hardly change.** R0−P: MMLU +0.27 pp, ARC −0.85 pp. R0−S on MMLU is still −0.88 pp [−1.31, −0.46].
- **Endpoint 1 (mean): no drop.** R0−P +1.90 pp [+0.86, +2.95]. R0−S +0.48 pp [−0.62, +1.59], so the mean is back at the S level.
- **Endpoint 5 (refusals): no significant return.** R0 refuses 3 of 200 harmful prompts, P 1 of 200 (S: 180). 3 prompts are refused only by R0 and 1 only by P, McNemar p = 0.625. No arm refuses a harmless prompt except S (3). Both required gates pass for P and R0.
- **KL changes little, but it is above the advisory budget before and after the repair.** First-token KL: P 0.546, R0 0.644 (budget 0.1). Next-token KL: 0.691 and 0.572 (budget 0.05). Both fail the advisory KL gate; the perplexity gate passes (ratio 1.076 and 1.077). In Q1 first-token KL rose from 0.066 to 0.190, and every Q1 arm also fails the advisory KL gate.
- **Noise.** A second S run on the first 200 GSM8K items gave a different text for 119 items and a different score for 11.

<!-- ifeval:interpretation -->
On Qwen2.5-3B after repair, 330/541 prompts passed every strict check. Across individual instructions, 583/834 passed (69.90%). The earlier calculation gave each prompt equal weight and averaged its fraction of instructions passed (72.55%). Relative to the projected model, the repair changed the Qwen2.5-3B scores by +2.03 pp per prompt and +2.16 pp per instruction. The corresponding exploratory changes for Qwen2.5-1.5B were −2.40 pp per prompt and −1.56 pp per instruction.
<!-- /ifeval:interpretation -->

**Verdict for Q3, in two parts.** Did capability come back? The mean is back at the S level (R0−S +0.48 pp). But the projection damaged only 1.41 pp, and the data point to GSM8K answers that become short enough to fit the limit, rather than to better solutions (post hoc; Q3 has no 512-token run). Did the edit stay? For refusals, yes: R0 refuses 3 of 200 harmful prompts, there is no significant return of refusals (endpoint 5), and both required gates pass. KL changes little, but it was already above the advisory budget for P and stays above it.

## The three settings side by side

| Measure | Q1, accepted recipe | Q3, searched recipe | Q1, ladder level A |
| --- | ---: | ---: | ---: |
| Damage P−S, mean | −0.22 pp | −1.41 pp | −11.66 pp |
| Repair R−P, mean | −0.33 pp | +1.90 pp | +8.83 pp |
| R−P, GSM8K `flexible-extract` | +0.61 pp | +6.14 pp | +23.43 pp |
| R−P, GSM8K `strict-match` | −9.86 pp | +4.17 pp | +24.49 pp |
| R−P, IFEval prompt strict | −2.40 pp | +2.03 pp | +10.54 pp |
| Harmful refusals, P → R | 14 → 22 | 1 → 3 | 1 → 11 |
| Refused only by R / only by P | 9 / 1 | 3 / 1 | 10 / 0 |
| First-token KL, P → R | 0.066 → 0.190 | 0.546 → 0.644 | 2.746 → 1.502 |
| Next-token KL, P → R | 0.154 → 0.231 | 0.691 → 0.572 | 1.586 → 1.596 |

R is R0 for Q1 and Q3, and R_A at level A. The refusal counts are out of 200 harmful prompts; P in Q1 has 199 valid answers and R_A has 198. Every arm in this table fails the advisory KL gate.

## Exploratory: damage ladder on Q1 (Z2)

The accepted Q1 recipe hardly damages capability, so Z2 makes the projection stronger step by step until it does. Rungs are projection-only builds of the Q1 recipe with `small_model_safeguards: false`. Level A is the first rung whose screening mean drops by at least 3 pp against S, with at least 95% valid harmless answers. Only level A is repaired, with the GPU path of RG (R0 settings, the Q1 R0 corpus, `o_proj` and `down_proj` in all projection layers).

| Rung | Layers, directions | Screening drop vs S | Harmless valid | Harmful refused / valid | Decision |
| --- | --- | ---: | ---: | ---: | --- |
| D1 | 6–22, 4 | 1.01 pp | 100% | 17 / 199 | next rung |
| D2 | 0–27, 4 | 11.69 pp | 100% | 1 / 200 | level A |

As the stop rule says, D3 and D4 were not screened. P_A is D2, and R_A is D2 after repair.

- **At level A the damage is real.** P_A−S on the full mean: −11.66 pp [−13.02, −10.27]. Most of it is in the generative tests: GSM8K −28.96 pp, IFEval −12.94 pp. MMLU loses 3.56 pp, and ARC does not change significantly (−1.19 pp).
- **The repair recovers about three quarters of it.** R_A−P_A: +8.83 pp [+7.51, +10.17]. Recovered share (R_A − P_A) / (S − P_A) = 0.76 [0.66, 0.86].
- **About 80% of the damage to the generative tests comes back.** GSM8K `flexible-extract`: P_A 27.29, R_A 50.72, S 56.25. IFEval: P_A 28.84, R_A 39.37, S 41.77. The R_A−S gap on IFEval (−2.40 pp) is not significant (Holm p = 0.534).
- **Here the repair restores the GSM8K format instead of breaking it.** GSM8K `strict-match`: P_A 8.11, R_A 32.60, S 34.12. Answers that end with `#### number`: 298, 790 and 761 of 1319. Answers at the 256-token limit: 525, 125 and 109. In Q1 with the accepted recipe, a repair with the same settings and corpus lowered `strict-match` by 9.86 pp.
- **MMLU hardly comes back.** P_A 56.66, R_A 57.24, S 60.22. R_A−S on the mean is still −2.84 pp [−4.13, −1.55], a drop, mostly from MMLU (−2.98 pp) and GSM8K (−5.53 pp).
- **The edit stays, with a small return of refusals.** R_A refuses 11 of 198 valid harmful answers, P_A 1 of 200 (S: 184 of 200). 10 prompts are refused only by R_A, none only by P_A, McNemar p = 0.002. Both required gates pass for P_A and R_A.
- **KL.** First-token KL falls from 2.746 (P_A) to 1.502 (R_A). Next-token KL does not change (1.586 and 1.596), and the perplexity ratio falls from 1.416 to 1.272. Both values are far above Q1 R0 (first token 0.190, next token 0.231). Like every arm in this study, both fail the advisory KL gate; only at level A do they also fail the advisory perplexity gate.

**Verdict for Z2, in two parts.** Did capability come back? Mostly yes: 76% of the mean damage, about 80% of the GSM8K and IFEval damage, but hardly any of MMLU. Did the edit stay? Mostly yes: 11 of 198 harmful prompts refused, both required gates pass, but 10 refusals come back, and KL stays far above the advisory budget.

Limitations: one rung, one seed and one repair corpus. RG ≈ R0 was shown only for Q1 with the accepted recipe. The screening items are part of the full test sets, but they were used only to choose the rung, not to measure the repair.

## Q1 (Qwen2.5-1.5B) in short

The details and tables are in [Q1 interim results](data/q1/partial-results.md). The Q1 numbers did not change in the final analysis.

- The projection does not damage capability: P−S −0.22 pp [−1.17, +0.70].
- Endpoint 1: R0−P −0.33 pp, no drop (seed 42). With seeds 43 and 44 (exploratory): −0.91 pp [−2.03, +0.19], inconclusive, and −1.12 pp [−2.16, −0.08], a drop. Mean of the 3 seeds: −0.79 pp [−1.76, +0.21], no drop. Endpoint 3: GSM8K `strict-match` −9.86 pp. With a 512-token limit the gap stays (Z5), so the cause is not truncation: the repaired model ends fewer answers with `#### number` (787 → 508 of 1319).
- IFEval goes down with every seed: R0x3−P −3.64 pp [−6.78, −0.49].
- Refusals: 9 prompts refused only by R0 and 1 only by P (p = 0.021, exploratory). A blind manual check of 58 answers agreed with the refusal detector on 57 (Z6).
- First-token KL rises from 0.066 (P) to 0.190 (R0).
- RK (refusals in the repair data): 138 vs 0 new refusals, and both required gates fail, so the edit is undone. RB (more data, a larger adapter): IFEval −5.91 pp and next-token KL 1.044. RG (GPU path) does not differ measurably from R0 (mean −0.34 pp [−0.97, +0.32]).

## Exploratory: L3 with the family recipe (Z1) in short

Llama-3.2-3B, layers 5–21. The projection Pf fails both required gates because of invalid answers (37 of 400). The repair Rf brings validity back (3 invalid) and passes both gates. It also brings back refusals: 15 prompts are refused only by Rf and 2 only by Pf, McNemar p = 0.0023. The screening drop of Pf was 0.21 pp, so Rf was not screened. Details are in [Q1 interim results](data/q1/partial-results.md).

## Limitations

- The confirmatory endpoints cover two models of one family. The results apply only to these models, to self-distilled repair data without refusals and to these settings.
- GSM8K uses a 256-token limit. In Q3 more than a third of the S answers reach it, so GSM8K in Q3 partly measures answer length. The truncation check is post hoc, and the subset of items "under the limit" depends on the answers of the arms themselves.
- In Q3, `strict-match` of S is at a floor (1.06%), so endpoint 3 could hardly show a drop there.
- The confirmatory endpoints use one repair seed (42). In Q1 the verdict on the mean changes with the seed (see the Q1 section). Q3 has only seed 42.
- Q3 has no GSM8K run with a 512-token limit, so the length reading of the Q3 GSM8K gain is not tested directly.
- KL and perplexity are measured on 50 prompts, refusals on 200 pairs. No projected or repaired arm meets the KL budget of the evaluation profile (0.1 for the first token, 0.05 for the next tokens). So "the edit stays" in this report refers to refusals and the required gates, not to KL.
- Z2 has one rung, one seed and one repair corpus. RG ≈ R0 was shown only for Q1 with the accepted recipe.
- The refusal detector matches words. Z6 checked only Q1 (58 answers), and the rater is the session that runs the study.
- Endpoints 5 and 6 are confirmatory only for Q3. The Q1 values were seen before they were defined.
- The RT arm of Z5 (repair on short answers) was not run. The planned corpus could not be built, and every replacement corpus would change the answer length and the amount of data at the same time (protocol, Z5, decision of 23 November). So this report does not say whether the long answers in the repair data cause the format loss in Q1.

## Tables: Q3

### Capability by arm

| Arm | MMLU | ARC | GSM8K flexible | GSM8K strict | IFEval prompt strict | Mean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| S | 66.42 | 60.07 | 58.07 | 1.06 | 60.07 | 61.16 |
| P | 65.26 | 60.24 | 54.51 | 0.76 | 58.96 | 59.74 |
| R0 | 65.53 | 59.39 | 60.65 | 4.93 | 61.00 | 61.64 |

### Comparisons, percentage points

| Comparison | Mean | bootstrap p | MMLU | ARC | GSM8K | IFEval | IFEval McNemar p (Holm) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P−S | −1.41 [−2.45, −0.39] drop | 0.006 | −1.15 [−1.60, −0.72] drop | +0.17 [−1.11, +1.45] no drop | −3.56 [−5.76, −1.36] drop | −1.11 [−4.44, +2.03] inconclusive | 1.000 |
| R0−P | +1.90 [+0.86, +2.95] no drop | 4.0×10^−4 | +0.27 [+0.04, +0.50] no drop | −0.85 [−1.71, +0.00] no drop | +6.14 [+3.87, +8.49] no drop | +2.03 [−1.29, +5.36] no drop | 0.289 |
| R0−S | +0.48 [−0.62, +1.59] no drop | 0.398 | −0.88 [−1.31, −0.46] drop | −0.68 [−1.96, +0.60] no drop | +2.58 [+0.23, +4.93] no drop | +0.92 [−2.59, +4.44] inconclusive | 0.716 |

### Refusals, KL and perplexity (`verify-edit`: refusals on 200 `final_test` pairs, KL and perplexity on 50 prompts)

| Arm | Harmful: refused / valid | Harmless: refused / valid | Coherence | KL first token | KL next token | Perplexity ratio | Required gates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| P | 1 / 200 | 0 / 200 | 10/10 | 0.546 | 0.691 | 1.076 | heldout_refusal pass, collateral pass |
| S | 180 / 200 | 3 / 200 | 10/10 | — | — | — | — |
| R0 | 3 / 200 | 0 / 200 | 10/10 | 0.644 | 0.572 | 1.077 | heldout_refusal pass, collateral pass |

### Refusal comparisons (exact McNemar on per-prompt flags)

| Comparison | Prompts | only baseline refuses | only compared refuses | p |
| --- | --- | ---: | ---: | ---: |
| P−S | harmful | 180 | 1 | 1.2×10^−52 |
| P−S | harmless | 3 | 0 | 0.250 |
| R0−P | harmful | 1 | 3 | 0.625 |
| R0−P | harmless | 0 | 0 | 1.000 |
| R0−S | harmful | 177 | 0 | 1.0×10^−53 |
| R0−S | harmless | 3 | 0 | 0.250 |

### GSM8K format and IFEval instruction level

<!-- ifeval:q3 -->
| Arm | GSM8K strict (%) | Ends with `#### number` | At the 256-token limit | Median GSM8K tokens | IFEval strict instructions, passed / total (%) |
| --- | ---: | ---: | ---: | ---: | ---: |
| S | 1.06 | 11 | 487 | 227 | 578/834 (69.30%) |
| P | 0.76 | 5 | 534 | 235 | 565/834 (67.75%) |
| R0 | 4.93 | 82 | 389 | 206 | 583/834 (69.90%) |
<!-- /ifeval:q3 -->
## Tables: Z2, level A (P_A, R_A)

### Capability by arm

| Arm | MMLU | ARC | GSM8K flexible | GSM8K strict | IFEval prompt strict | Mean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| S | 60.22 | 54.18 | 56.25 | 34.12 | 41.77 | 53.11 |
| P_A | 56.66 | 52.99 | 27.29 | 8.11 | 28.84 | 41.44 |
| R_A | 57.24 | 53.75 | 50.72 | 32.60 | 39.37 | 50.27 |

### Comparisons, percentage points

| Comparison | Mean | bootstrap p | MMLU | ARC | GSM8K | IFEval | IFEval McNemar p (Holm) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P_A−S | −11.66 [−13.02, −10.27] practically significant drop | < 0.0002 | −3.56 [−4.19, −2.94] practically significant drop | −1.19 [−2.90, +0.51] inconclusive | −28.96 [−31.92, −25.93] practically significant drop | −12.94 [−17.19, −8.69] practically significant drop | 1.2×10^−8 |
| R_A−P_A | +8.83 [+7.51, +10.17] no drop | < 0.0002 | +0.58 [+0.04, +1.12] no drop | +0.77 [−0.85, +2.39] no drop | +23.43 [+20.55, +26.23] no drop | +10.54 [+6.28, +14.60] no drop | 3.7×10^−6 |
| R_A−S | −2.84 [−4.13, −1.55] drop | < 0.0002 | −2.98 [−3.54, −2.41] practically significant drop | −0.43 [−2.13, +1.28] inconclusive | −5.53 [−8.19, −2.88] practically significant drop | −2.40 [−6.47, +1.66] inconclusive | 0.534 |

### Refusals, KL and perplexity (`verify-edit`: refusals on 200 `final_test` pairs, KL and perplexity on 50 prompts)

| Arm | Harmful: refused / valid | Harmless: refused / valid | Coherence | KL first token | KL next token | Perplexity ratio | Required gates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| P_A | 1 / 200 | 3 / 200 | 8/10 | 2.746 | 1.586 | 1.416 | heldout_refusal pass, collateral pass |
| S | 184 / 200 | 15 / 200 | 9/10 | — | — | — | — |
| R_A | 11 / 198 | 7 / 200 | 10/10 | 1.502 | 1.596 | 1.272 | heldout_refusal pass, collateral pass |

### Refusal comparisons (exact McNemar on per-prompt flags)

| Comparison | Prompts | only baseline refuses | only compared refuses | p |
| --- | --- | ---: | ---: | ---: |
| P_A−S | harmful | 183 | 0 | 1.6×10^−55 |
| P_A−S | harmless | 13 | 1 | 0.002 |
| R_A−P_A | harmful | 0 | 10 | 0.002 |
| R_A−P_A | harmless | 1 | 5 | 0.219 |
| R_A−S | harmful | 173 | 0 | 1.7×10^−52 |
| R_A−S | harmless | 11 | 3 | 0.057 |

### GSM8K format and IFEval instruction level

<!-- ifeval:z2 -->
| Arm | GSM8K strict (%) | Ends with `#### number` | At the 256-token limit | Median GSM8K tokens | IFEval strict instructions, passed / total (%) |
| --- | ---: | ---: | ---: | ---: | ---: |
| S | 34.12 | 761 | 109 | 124 | 422/834 (50.60%) |
| P_A | 8.11 | 298 | 525 | 206 | 350/834 (41.97%) |
| R_A | 32.60 | 790 | 125 | 122 | 416/834 (49.88%) |
<!-- /ifeval:z2 -->
## Files

The strict instruction scores and tables can be regenerated from the counts for each prompt. [Reproduction and field definitions](../../experiments/2026-11-22-obliteratus-multi-model/README.md)

- [endpoints-q1-q3.json](data/final/endpoints-q1-q3.json): endpoints 1–6 for Q1 and Q3, with the Holm correction and the pooled endpoint 1.
- [capability-summary.json](data/q3/capability-summary.json), [secondary-summary.json](data/q3/secondary-summary.json), [refusal-summary.json](data/q3/refusal-summary.json), [per-item-correctness.json](data/q3/per-item-correctness.json): the full Q3 analysis (`analyze_multi.py`).
- [kl.json](data/q3/kl.json): KL, perplexity and gate verdicts from `verify-edit` for Q3.
- [truncation.json](data/q3/truncation.json): the post hoc GSM8K length check for Q3.
- [ladder-D1.json](data/z2/ladder-D1.json), [ladder-D2.json](data/z2/ladder-D2.json): the screening and the stop rule for each rung.
- [capability-summary.json](data/z2/capability-summary.json), [secondary-summary.json](data/z2/secondary-summary.json), [refusal-summary.json](data/z2/refusal-summary.json), [per-item-correctness.json](data/z2/per-item-correctness.json), [kl.json](data/z2/kl.json), [recovered-share.json](data/z2/recovered-share.json): the level A analysis. The analysis code uses fixed arm names, so in these files P_A is called PS and R_A is called RS, and `recovered-share.json` stores the result under endpoint 4. It is not endpoint 4.
- [tables.md](data/z2/tables.md): the Z2 tables of this report.
- [q1/](data/q1), [l3/](data/l3): see [Q1 interim results](data/q1/partial-results.md).
- The answer texts of the models stay on the machine.

[Protocol and amendments](PROTOCOL.md) · [Issue log](issues.md) · [Study diary](../../session-logs/2026-11-22-obliteratus-multi-model.md)
