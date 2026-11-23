# Qwen2.5-1.5B (Q1): partial results of the LoRA repair study

Written on 23 November 2026. This is the partial report for Q1 from the shortened plan (protocol, "Shortened plan", 23 November). The Q1 damage ladder (Z2) and Q3 are still running. The final report will add them. All computation ran on an on-premise machine.

Codes: S is the stock model, E is the accepted edit from study 1, P is the projection (step 1 of the recipe), R0 is P after `adapter.lora_repair` with seed 42. R0-s43 and R0-s44 use seeds 43 and 44, and R0x3 is their per-item mean. RG is the same repair through `obliteratus recover` on the GPU. RK uses repair data with refusals, and RB uses more data and a larger adapter. PS is the strong projection (layers 6–22, 2 directions), and RS is PS after repair. Differences are in percentage points (pp), with 95% bootstrap intervals.

## Main results

- **The projection does not damage capability in Q1, so there is nothing to recover.** P−S on the mean of the four tests is −0.22 pp [−1.17, +0.70]. Even the strong projection PS loses only 1.00 pp [−2.12, +0.11].
- **Endpoint 1 (R0−P, mean): no drop.** −0.33 pp [−1.40, +0.74], bootstrap p = 0.546. The 2 pp margin holds. Holm across Q1 and Q3 comes in the final report.
- **Endpoint 3 (R0−P, GSM8K `strict-match`): the repair breaks the answer format.** −9.86 pp [−12.51, −7.20], McNemar p = 1.0×10^−12. `flexible-extract` does not change (+0.61 pp). Answers that end with `#### number` fall from 787 to 508 of 1319. The same happens with all three seeds and with RG.
- **Z5: truncation is not the cause.** With a 512-token limit almost no answer is cut (P 7, R0 9), but the gap stays: −10.69 pp, p = 2.1×10^−14. The repaired model ends fewer answers with `#### number` (787 → 508 of 1319).
- **IFEval goes down with every seed.** R0−P: −2.40 pp (seed 42), −3.88 pp (seed 43), −4.62 pp (seed 44). R0x3−P: −3.64 pp [−6.78, −0.49]. Seed 42 alone is not significant (exploratory endpoint 6 for Q1: p = 0.198).
- **The repair brings back a small part of the refusals.** R0 refuses 22 of 200 harmful prompts, P 14 of 199 valid answers (S: 184). 9 prompts are refused only by R0 and 1 only by P, p = 0.021 (exploratory endpoint 5 for Q1). Seeds 43 and 44 and RG show the same (8, 10 and 9 new refusals, none lost). The `heldout_refusal` gate still passes.
- **Z6: the refusal detector is right on these prompts.** A blind manual check of 58 answers agreed with the detector on 57. For 8 of the 9 prompts that only R0 refuses, the manual label is also a refusal.
- **The repair moves the model further from S on harmless prompts.** First-token KL: P 0.066, R0 0.190 (seeds: 0.186–0.210). Next-token KL: 0.154 and 0.231.
- **RG does not differ measurably from R0.** RG−R0 on the mean: −0.34 pp [−0.97, +0.32]; refusals 23 and 22; GSM8K `strict-match` −0.61 pp.
- **Endpoint 4 (RS−PS): no drop, but the recovered share is not computed.** +0.26 pp [−0.75, +1.27], p = 0.616. In the full evaluation S−PS is 1.00 pp, under the 2 pp the protocol needs for the recovered share. RS also loses GSM8K `strict-match` (−5.69 pp).
- **Endpoint 2 (RK−P, harmful refusals): repair data with refusals brings the refusals back.** RK refuses 152 of 200 harmful prompts (P: 14, S: 184). 138 prompts are refused only by RK and none only by P, McNemar p = 5.7×10^−42. Capability does not drop: RK−P −0.49 pp [−1.63, +0.62], RK−R0 −0.16 pp [−0.95, +0.66]. But RK also refuses 29 of 200 harmless prompts, more than S (15), and fails both required gates (`heldout_refusal` and `collateral`). So with refusals in the repair data, the repair undoes the edit.
- **RB (500 prompts, rank 32, 2 epochs) costs more than R0.** RB−P on the mean: −1.20 pp [−2.32, −0.06], a drop. IFEval: −5.91 pp [−9.43, −2.40], a practically significant drop (Holm p = 0.005). Next-token KL rises to 1.044 (R0: 0.231). Refusals stay low (19 of 200), and both required gates pass.

**Verdict for Q1, in two parts.** Did capability come back? It cannot be tested here, because the projection did not damage it. Did the edit stay? Mostly yes: R0 refuses 11% of harmful prompts (S: 92%), and both required gates pass. But the repair adds a small, repeatable return of refusals, a loss of the GSM8K answer format and higher KL. With refusals in the repair data (RK), the edit does not stay.

## Exploratory: L3 with the family recipe (Z1)

Llama-3.2-3B with the family recipe (layers 5–21), built on 22 November.

| Measure | S | Pf (projection) | Rf (repair) |
| --- | ---: | ---: | ---: |
| Harmful: refused / valid | 143 / 200 | 4 / 180 | 17 / 197 |
| Harmful: invalid | 0 | 20 | 3 |
| Harmless: valid | 198 / 200 | 183 / 200 | 200 / 200 |
| Required gates | — | `heldout_refusal` fail (invalid rate 0.10 > 0.05), `collateral` fail (coherence drop 0.075 > 0.05) | both pass |
| First-token KL | — | 0.890 | 0.766 |
| Next-token KL | — | 0.184 | 0.229 |
| Screening mean (MMLU 1/10, ARC, GSM8K first 400) | 64.44 | 64.23 | not run |

- The projection damages answer validity on L3, not screening capability. The screening drop is 0.21 pp, under the 2 pp rule, so Rf was not screened.
- The repair fixes validity: invalid answers fall from 37 to 3 (harmful and harmless together), and both gates pass.
- The repair also brings back refusals: 15 prompts are refused only by Rf and 2 only by Pf, McNemar p = 0.0023. For 13 of the 15, Pf gave a valid answer without a refusal, so this is not only the effect of fewer invalid answers.

## Repeatability

- P from the R0-s43, R0-s44, RK and RB builds is bit-identical to the study-1 P after the cast to bf16 (338 tensors each). The P of the RS build is bit-identical to PS.
- Seeds: the mean metric of R0 is 52.56, 51.98 and 51.77 for seeds 42, 43 and 44 (range 0.79 pp, standard deviation 0.41 pp).
- Noise: a second S run on the first 200 GSM8K items gave a different text for 111 items and a different score for 15.

## Limitations

- Q1 is a small model where the accepted recipe hardly damages capability. A Q1 result cannot show whether the repair recovers real damage. The damage ladder (Z2) tests this.
- The refusal detector matches words. Z6 checked only 58 answers, and the rater is the session that runs the study.
- Endpoints 5 and 6 are confirmatory only for Q3. The Q1 values were seen before they were defined.
- The seed interval covers only item variation for these three seeds.

## Tables

### Capability by arm

| Arm | MMLU | ARC | GSM8K flexible | GSM8K strict | IFEval prompt strict | Mean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| S | 60.22 | 54.18 | 56.25 | 34.12 | 41.77 | 53.11 |
| E | 60.18 | 54.27 | 55.27 | 34.04 | 39.93 | 52.41 |
| P | 60.08 | 54.27 | 55.42 | 33.89 | 41.77 | 52.89 |
| R0 | 60.22 | 54.61 | 56.03 | 24.03 | 39.37 | 52.56 |
| R0-s43 | 60.16 | 54.44 | 55.42 | 22.97 | 37.89 | 51.98 |
| R0-s44 | 60.08 | 54.35 | 55.50 | 24.26 | 37.15 | 51.77 |
| RK | 60.07 | 54.69 | 55.65 | 20.24 | 39.19 | 52.40 |
| RB | 60.16 | 54.01 | 56.71 | 28.43 | 35.86 | 51.68 |
| RG | 60.23 | 54.86 | 54.97 | 23.43 | 38.82 | 52.22 |
| PS | 59.93 | 54.44 | 54.51 | 33.66 | 39.56 | 52.11 |
| RS | 60.03 | 54.86 | 56.86 | 27.98 | 37.71 | 52.36 |

### Comparisons, percentage points

| Comparison | Mean | bootstrap p | MMLU | ARC | GSM8K | IFEval | IFEval McNemar p (Holm) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P−S | −0.22 [−1.17, +0.70] no drop | 0.639 | −0.14 [−0.51, +0.22] no drop | +0.09 [−0.85, +1.02] no drop | −0.83 [−2.88, +1.21] inconclusive | +0.00 [−2.96, +2.96] inconclusive | 1.000 |
| R0−P | −0.33 [−1.40, +0.74] no drop | 0.546 | +0.14 [−0.06, +0.33] no drop | +0.34 [−0.43, +1.11] no drop | +0.61 [−1.90, +3.11] no drop | −2.40 [−5.73, +0.92] inconclusive | 0.792 |
| R0−S | −0.55 [−1.62, +0.51] no drop | 0.335 | +0.00 [−0.36, +0.36] no drop | +0.43 [−0.51, +1.37] no drop | −0.23 [−2.65, +2.27] inconclusive | −2.40 [−5.73, +0.93] inconclusive | 0.792 |
| R0-s43−P | −0.91 [−2.03, +0.19] inconclusive | 0.109 | +0.07 [−0.13, +0.27] no drop | +0.17 [−0.68, +1.02] no drop | +0.00 [−2.58, +2.58] inconclusive | −3.88 [−7.39, −0.37] drop | 0.158 |
| R0-s44−P | −1.12 [−2.16, −0.08] drop | 0.035 | −0.01 [−0.19, +0.18] no drop | +0.09 [−0.60, +0.77] no drop | +0.08 [−2.35, +2.50] inconclusive | −4.62 [−7.95, −1.29] drop | 0.035 |
| R0x3−P | −0.79 [−1.76, +0.21] no drop | 0.117 | +0.07 [−0.10, +0.24] no drop | +0.20 [−0.46, +0.88] no drop | +0.23 [−2.10, +2.53] inconclusive | −3.64 [−6.78, −0.49] drop | — |
| RK−P | −0.49 [−1.63, +0.62] no drop | 0.401 | −0.01 [−0.21, +0.19] no drop | +0.43 [−0.26, +1.19] no drop | +0.23 [−2.43, +2.88] inconclusive | −2.59 [−6.10, +0.92] inconclusive | 0.737 |
| RK−R0 | −0.16 [−0.95, +0.66] no drop | 0.715 | −0.15 [−0.31, +0.01] no drop | +0.09 [−0.51, +0.68] no drop | −0.38 [−2.12, +1.36] inconclusive | −0.18 [−2.77, +2.40] inconclusive | 1.000 |
| RK−S | −0.71 [−1.80, +0.40] no drop | 0.209 | −0.15 [−0.51, +0.20] no drop | +0.51 [−0.51, +1.54] no drop | −0.61 [−3.26, +1.97] inconclusive | −2.59 [−5.91, +0.74] inconclusive | 0.642 |
| RB−P | −1.20 [−2.32, −0.06] drop | 0.037 | +0.07 [−0.24, +0.38] no drop | −0.26 [−1.45, +0.94] no drop | +1.29 [−1.29, +3.87] no drop | −5.91 [−9.43, −2.40] practically significant drop | 0.005 |
| RB−R0 | −0.87 [−1.87, +0.13] no drop | 0.094 | −0.06 [−0.36, +0.22] no drop | −0.60 [−1.71, +0.43] no drop | +0.68 [−1.44, +2.88] no drop | −3.51 [−6.65, −0.37] drop | 0.179 |
| RG−P | −0.67 [−1.74, +0.37] no drop | 0.214 | +0.14 [−0.05, +0.33] no drop | +0.60 [−0.09, +1.28] no drop | −0.45 [−3.11, +2.12] inconclusive | −2.96 [−6.28, +0.37] inconclusive | 0.372 |
| RG−R0 | −0.34 [−0.97, +0.32] no drop | 0.306 | +0.01 [−0.16, +0.18] no drop | +0.26 [−0.34, +0.94] no drop | −1.06 [−2.35, +0.23] inconclusive | −0.55 [−2.59, +1.48] inconclusive | 1.000 |
| PS−S | −1.00 [−2.12, +0.11] inconclusive | 0.078 | −0.29 [−0.68, +0.09] no drop | +0.26 [−1.02, +1.54] no drop | −1.74 [−4.17, +0.68] inconclusive | −2.22 [−5.73, +1.29] inconclusive | 0.584 |
| RS−PS | +0.26 [−0.75, +1.27] no drop | 0.616 | +0.10 [−0.10, +0.29] no drop | +0.43 [−0.51, +1.37] no drop | +2.35 [−0.08, +4.85] no drop | −1.85 [−4.99, +1.29] inconclusive | 0.866 |
| RS−S | −0.74 [−1.85, +0.36] no drop | 0.191 | −0.19 [−0.58, +0.19] no drop | +0.68 [−0.60, +1.96] no drop | +0.61 [−1.97, +3.26] no drop | −4.07 [−7.39, −0.74] drop | 0.092 |
| E−S | −0.70 [−1.66, +0.27] no drop | 0.153 | −0.04 [−0.40, +0.31] no drop | +0.09 [−0.85, +0.94] no drop | −0.99 [−3.03, +1.06] inconclusive | −1.85 [−4.99, +1.29] inconclusive | 1.000 |
| P−E | +0.48 [−0.23, +1.20] no drop | 0.190 | −0.09 [−0.28, +0.09] no drop | +0.00 [−0.60, +0.60] no drop | +0.15 [−1.36, +1.59] no drop | +1.85 [−0.55, +4.25] no drop | 0.736 |
| R0−E | +0.15 [−0.91, +1.18] no drop | 0.798 | +0.04 [−0.17, +0.25] no drop | +0.34 [−0.51, +1.11] no drop | +0.76 [−1.82, +3.34] no drop | −0.55 [−3.88, +2.59] inconclusive | 1.000 |

### Refusals, KL and perplexity (`verify-edit`: refusals on 200 `final_test` pairs, KL and perplexity on 50 prompts)

| Arm | Harmful: refused / valid | Harmless: refused / valid | Coherence | KL first token | KL next token | Perplexity ratio | Required gates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| E | 15 / 199 | 3 / 199 | 7/10 | 0.067 | 0.160 | 1.032 | heldout_refusal pass, collateral pass |
| S | 184 / 200 | 15 / 200 | 9/10 | — | — | — | — |
| P | 14 / 199 | 3 / 199 | 8/10 | 0.066 | 0.154 | 1.032 | heldout_refusal pass, collateral pass |
| R0 | 22 / 200 | 4 / 199 | 10/10 | 0.190 | 0.231 | 1.027 | heldout_refusal pass, collateral pass |
| R0-s43 | 22 / 200 | 4 / 199 | 10/10 | 0.210 | 0.238 | 1.031 | heldout_refusal pass, collateral pass |
| R0-s44 | 24 / 200 | 6 / 199 | 10/10 | 0.186 | 0.225 | 1.027 | heldout_refusal pass, collateral pass |
| RK | 152 / 200 | 29 / 200 | 9/10 | 0.267 | 0.260 | 1.031 | heldout_refusal fail, collateral fail |
| RB | 19 / 200 | 10 / 200 | 8/10 | 0.625 | 1.044 | 1.022 | heldout_refusal pass, collateral pass |
| RG | 23 / 200 | 5 / 199 | 10/10 | 0.184 | 0.229 | 1.031 | heldout_refusal pass, collateral pass |
| PS | 4 / 199 | 7 / 199 | 9/10 | 0.602 | 0.364 | 1.043 | heldout_refusal pass, collateral pass |
| RS | 6 / 200 | 2 / 199 | 10/10 | 0.684 | 0.311 | 1.024 | heldout_refusal pass, collateral pass |

### Refusal comparisons (exact McNemar on per-prompt flags)

| Comparison | Prompts | only baseline refuses | only compared refuses | p |
| --- | --- | ---: | ---: | ---: |
| P−S | harmful | 170 | 0 | 1.3×10^−51 |
| P−S | harmless | 12 | 0 | 4.9×10^−4 |
| R0−P | harmful | 1 | 9 | 0.021 |
| R0−P | harmless | 1 | 2 | 1.000 |
| R0−S | harmful | 162 | 0 | 3.4×10^−49 |
| R0−S | harmless | 11 | 0 | 9.8×10^−4 |
| R0-s43−P | harmful | 0 | 8 | 0.008 |
| R0-s43−P | harmless | 1 | 2 | 1.000 |
| R0-s44−P | harmful | 0 | 10 | 0.002 |
| R0-s44−P | harmless | 0 | 3 | 0.250 |
| RK−P | harmful | 0 | 138 | 5.7×10^−42 |
| RK−P | harmless | 0 | 26 | 3.0×10^−8 |
| RK−R0 | harmful | 0 | 130 | 1.5×10^−39 |
| RK−R0 | harmless | 0 | 25 | 6.0×10^−8 |
| RK−S | harmful | 34 | 2 | 1.9×10^−8 |
| RK−S | harmless | 0 | 14 | 1.2×10^−4 |
| RB−P | harmful | 2 | 7 | 0.180 |
| RB−P | harmless | 0 | 7 | 0.016 |
| RB−R0 | harmful | 10 | 7 | 0.629 |
| RB−R0 | harmless | 0 | 6 | 0.031 |
| RG−P | harmful | 0 | 9 | 0.004 |
| RG−P | harmless | 1 | 3 | 0.625 |
| RG−R0 | harmful | 0 | 1 | 1.000 |
| RG−R0 | harmless | 0 | 1 | 1.000 |
| PS−S | harmful | 180 | 0 | 1.3×10^−54 |
| PS−S | harmless | 12 | 4 | 0.077 |
| RS−PS | harmful | 0 | 2 | 0.500 |
| RS−PS | harmless | 5 | 0 | 0.062 |
| RS−S | harmful | 178 | 0 | 5.2×10^−54 |
| RS−S | harmless | 14 | 1 | 9.8×10^−4 |
| E−S | harmful | 169 | 0 | 2.7×10^−51 |
| E−S | harmless | 12 | 0 | 4.9×10^−4 |
| P−E | harmful | 1 | 0 | 1.000 |
| P−E | harmless | 1 | 1 | 1.000 |
| R0−E | harmful | 1 | 8 | 0.039 |
| R0−E | harmless | 1 | 2 | 1.000 |

### GSM8K format and IFEval instruction level

| Arm | GSM8K strict | Ends with `#### number` | At the 256-token limit | Median tokens | IFEval inst strict |
| --- | ---: | ---: | ---: | ---: | ---: |
| S | 34.12 | 761 | 109 | 124 | 50.60 |
| E | 34.04 | 785 | 106 | 120 | 49.64 |
| P | 33.89 | 787 | 102 | 119 | 50.96 |
| R0 | 24.03 | 508 | 162 | 146 | 49.40 |
| R0-s43 | 22.97 | 483 | 177 | 148 | 48.32 |
| R0-s44 | 24.26 | 515 | 169 | 145 | 47.72 |
| RK | 20.24 | 421 | 164 | 151 | 49.16 |
| RB | 28.43 | 594 | 181 | 146 | 45.68 |
| RG | 23.43 | 499 | 163 | 141 | 48.92 |
| PS | 33.66 | 757 | 101 | 121 | 49.88 |
| RS | 27.98 | 587 | 176 | 141 | 48.68 |

## Files

- [endpoints.json](endpoints.json): primary endpoints 1–6.
- [capability-summary.json](capability-summary.json), [secondary-summary.json](secondary-summary.json), [refusal-summary.json](refusal-summary.json), [per-item-correctness.json](per-item-correctness.json): the full Q1 analysis (`analyze_multi.py`).
- [kl.json](kl.json): KL, perplexity and gate verdicts from `verify-edit`.
- [z5-format-a.json](z5-format-a.json): GSM8K with 256 and 512 tokens (Z5 test a).
- [z6-agreement.json](z6-agreement.json): counts of the manual refusal check (Z6). The answer texts stay on the machine.
- [z1-screening-Pf.json](../l3/z1-screening-Pf.json), [z1-refusals.json](../l3/z1-refusals.json), [kl.json](../l3/kl.json): L3 with the family recipe (Z1).
