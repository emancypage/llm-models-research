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

| Arm | GSM8K strict | Ends with `#### number` | At the 256-token limit | Median tokens | IFEval inst strict |
| --- | ---: | ---: | ---: | ---: | ---: |
| S | 34.12 | 761 | 109 | 124 | 50.60 |
| P_A | 8.11 | 298 | 525 | 206 | 41.97 |
| R_A | 32.60 | 790 | 125 | 122 | 49.88 |
