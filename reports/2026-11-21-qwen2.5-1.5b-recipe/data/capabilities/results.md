# Qwen2.5-1.5B-Instruct: do the recipe and LoRA repair lower capabilities?

Measured on 21–22 November 2026. The plan and all deviations are in the [capability evaluation protocol](../../PROTOCOL.md).

## Answers

1. **The recipe `qwen2.5-1.5b-mid10-18-dim1` does not lower the mean capability score by 2 percentage points.** The mean of the four tests dropped by 0.70 pp, 95% interval from −1.66 to +0.27. For MMLU and ARC the intervals exclude a 2 pp drop. GSM8K and IFEval are inconclusive on their own: their intervals reach −3.0 and −5.0 pp.
2. **LoRA repair showed no improvement in capabilities.** The primary comparison is R−P: the model after repair against the model after the projection from the same run. The mean changed by −0.33 pp, interval from −1.40 to +0.74. The largest change is in IFEval: −2.40 pp [−5.73, 0.92], inconclusive. There was also no shown loss to recover. P did not lose 2 pp on the mean against S: −0.22 [−1.17, 0.70]. GSM8K and IFEval on their own are inconclusive for P−S.
   - Refusals: 22/200 for R and 14/199 for P. This difference is undetermined. The reports do not store refusals per prompt, so a paired test cannot be computed. Depending on whether both models refused the same prompts, an exact McNemar test would give p between 0.008 and 0.24.

   The repair changed how the model answers GSM8K:
   - `strict-match` accuracy, which needs the few-shot format, dropped by 9.9 pp;
   - answers ending with the few-shot `#### number` pattern: 508 of 1319 for R against 787 for P; answers containing `####`: 537 against 833. That is about 21–22 pp fewer;
   - answers cut at the 256-token limit: 162 instead of 102;
   - accuracy based on the last number in the answer (`flexible-extract`) did not drop by 2 pp: +0.61 [−1.90, 3.11].

   I added the format analysis after the results.

Exploratory addition, added after the other results: the 14–22 variant (E3) also does not lower the mean by 2 pp: −0.60 pp [−1.58, 0.36]. It removed refusals most strongly in the search, but this was measured only on the `tune` split, which was used to select it.

All comparisons come from one run of each version. Generation noise is large (see "Noise").

## Versions

| Version | Description |
| --- | --- |
| S | `Qwen/Qwen2.5-1.5B-Instruct` @ `989aa79…a306` |
| E | S after the accepted recipe; checkpoint from an earlier run, saved in float16 |
| P | S after the projection step from the same run as R, before repair; computed on CPU in float32 |
| R | P after `adapter.lora_repair` (OBLITERATUS #578), with merged weights (`merge: true`) |
| E2 | Recipe variant with layers 12–16 from the recipe search; exploratory |
| E3 | Variant 14–22, the search winner after re-ranking; exploratory, added to the protocol before its results |

Repair: layers 10–18, modules `attn_out` and `mlp_out`, rank 8, alpha 16, learning rate 2e-4, 1 epoch, batch 1, gradient accumulation 8, `max_length` 1152, seed 42. Data: 237 answers from S (up to 1024 tokens) to harmless prompts from the `train` split. The refusal filter removed 13 of 250 answers. Building R took 71 minutes on CPU.

Tests: lm-eval 0.4.13, HF backend, bf16, full sets. MMLU 5-shot and ARC-Challenge 25-shot without the chat template. GSM8K 5-shot and IFEval 0-shot with the chat template.

## Main results (%)

| Version | MMLU | ARC (`acc_norm`) | GSM8K (`flexible-extract`) | IFEval (prompt, strict) | Mean |
| --- | ---: | ---: | ---: | ---: | ---: |
| S | 60.22 | 54.18 | 56.25 | 41.77 | 53.11 |
| E | 60.18 | 54.27 | 55.27 | 39.93 | 52.41 |
| P | 60.08 | 54.27 | 55.42 | 41.77 | 52.89 |
| R | 60.22 | 54.61 | 56.03 | 39.37 | 52.56 |
| E2 | 59.88 | 55.03 | 56.63 | 39.74 | 52.82 |
| E3 | 60.28 | 54.35 | 56.03 | 39.37 | 52.51 |

## Comparisons (percentage points)

Difference with a 95% interval from a paired bootstrap (10,000 draws, seed 42). Verdicts:
- "no drop": the interval excludes −2 pp;
- "drop": the whole interval is below 0;
- "practically significant drop": a drop of at least 2 pp (did not occur);
- "inconclusive": all other cases.

Verdicts can overlap. An interval can lie fully below 0 and still exclude −2 pp. In that case I write "drop" and note that it is smaller than 2 pp.

| Comparison | MMLU | ARC | GSM8K | IFEval | Mean |
| --- | --- | --- | --- | --- | --- |
| **E−S** (question 1) | −0.04 [−0.40, 0.31] no drop | +0.09 [−0.85, 0.94] no drop | −0.99 [−3.03, 1.06] inconcl. | −1.85 [−4.99, 1.29] inconcl. | **−0.70 [−1.66, 0.27] no drop** |
| **R−P** (question 2) | +0.14 [−0.06, 0.33] no drop | +0.34 [−0.43, 1.11] no drop | +0.61 [−1.90, 3.11] no drop | −2.40 [−5.73, 0.92] inconcl. | **−0.33 [−1.40, 0.74] no drop** |
| R−E | +0.04 [−0.17, 0.25] no drop | +0.34 [−0.51, 1.11] no drop | +0.76 [−1.82, 3.34] no drop | −0.55 [−3.88, 2.59] inconcl. | +0.15 [−0.91, 1.18] no drop |
| R−S | 0.00 [−0.36, 0.36] no drop | +0.43 [−0.51, 1.37] no drop | −0.23 [−2.65, 2.27] inconcl. | −2.40 [−5.73, 0.93] inconcl. | −0.55 [−1.62, 0.51] no drop |
| P−S | −0.14 [−0.51, 0.22] no drop | +0.09 [−0.85, 1.02] no drop | −0.83 [−2.88, 1.21] inconcl. | 0.00 [−2.96, 2.96] inconcl. | −0.22 [−1.17, 0.70] no drop |
| P−E | −0.09 [−0.28, 0.09] no drop | 0.00 [−0.60, 0.60] no drop | +0.15 [−1.36, 1.59] no drop | +1.85 [−0.55, 4.25] no drop | +0.48 [−0.23, 1.20] no drop |

- The exact McNemar test with Holm correction showed no significant difference in any test of any comparison. The smallest p was 0.79 for the primary comparisons and 0.11 overall.
- By the protocol rule, the primary comparison for the repair is R−P, not R−E. In layer 10 (`mlp.down_proj`), 2.6% of the values of P differ from E by more than 1 bf16 step. The threshold was 0.1%. The weight edit of P differs from the edit of E by only 0.9% (relative norm). P−E shows no difference in capabilities, and R−E and R−P lead to the same conclusion.

## LoRA repair: refusals, KL and answer format

`verify-edit` on 200 `final_test` pairs. Each pair has a harmful and a harmless prompt. "Over-refusals" are refusals of harmless prompts.

| Version | Refusals | Wilson upper bound | Over-refusals | first-token KL | next-token KL | Perplexity relative to S |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| S | 92% | — | 15/200 | — | — | — |
| E | 15/199 | 12.1% | 3/199 | 0.067 | 0.160 | 1.032 |
| P | 14/199 | 11.5% | 3/199 | 0.066 | 0.154 | 1.032 |
| R | 22/200 | 16.1% | 4/199 | 0.190 | 0.231 | 1.027 |

- The difference in refusals between R and P (22/200 against 14/199) is undetermined. Both models got the same prompts, so a paired test would be the right one. But the `verify-edit` reports do not store refusals per prompt. Depending on whether the refusals were on the same prompts, an exact McNemar test would give p between 0.008 and 0.24. Wilson intervals: P from 4.2% to 11.5%, R from 7.4% to 16.1%. The fact that they overlap does not replace a test.
- KL is computed on 50 prompts and has no interval.

Secondary metrics from the capability tests. `strict-match` and the count of cut answers were in the protocol. Their intervals and tests, the `####` counts and the reading of answers were added after the results.

| Version | GSM8K `strict-match` | GSM8K: ending with `#### number` | GSM8K: answers at the 256-token limit | GSM8K: median length (tokens) | IFEval `inst_level_strict_acc` |
| --- | ---: | ---: | ---: | ---: | ---: |
| S | 34.12% | 761 | 109 | 124 | 50.60% |
| E | 34.04% | 785 | 106 | 120 | 49.64% |
| P | 33.89% | 787 | 102 | 119 | 50.96% |
| R | 24.03% | 508 | 162 | 146 | 49.40% |
| E2 | 37.15% | 830 | 108 | 122 | 49.88% |
| E3 | 33.81% | 772 | 106 | 123 | 49.16% |

IFEval at the instruction level: R−P −1.56 pp [−4.23, 1.20], E−S −0.96 [−3.56, 1.69]. The first version of this report computed this column as an average over prompts, not over instructions as lm-eval does. An independent review found this error. I fixed it, and the values now match the lm-eval result files. No conclusion was based on this column.

- R−P for `strict-match`: −9.86 pp, interval from −12.51 to −7.20. 233 questions are correct only for P, and 103 only for R. McNemar p ≈ 1·10⁻¹².
- More R answers reach the token limit: 101 only for R against 41 only for P, p ≈ 5·10⁻⁷.
- The cause is visible in the answers: R more often leaves out the few-shot `#### number` ending (508 of 1319 answers end with it, 787 for P). Instead, it writes in its own chat style, with LaTeX formulas. `flexible-extract` takes the last number, so this accuracy does not drop by 2 pp. `strict-match` needs the few-shot format, so it drops.
- first-token KL to S rose almost 3 times after the repair (0.066 → 0.190), and next-token KL rose from 0.154 to 0.231. Perplexity relative to S moved slightly closer to S (1.032 → 1.027). By KL, the repair did not bring the model closer to S. This is an observation from 50 prompts without an interval, not a test.
- Hypothesis, not tested: the repair data are greedy S answers without few-shot examples in the context. Training on them may strengthen the model's own style and weaken how it follows examples in the prompt.

If the repair restores refusals, it does so only a little. R still passes the recipe threshold (20%). At the same time, the repair changes behavior that the primary metrics do not see.

## Noise

A second S run on the first 200 GSM8K questions, with the same settings, gave 111 different texts and 15 different scores (7.5% of questions). The likely cause is bf16 computation that depends on batch composition. I did not test this cause separately. In the E−S comparison, GSM8K has 189 discordant questions out of 1319 (14%), so about half of the discordance may be noise alone. The paired bootstrap includes this noise in the interval width, but it cannot separate it from the effect of the recipe.

## Recipe search (exploratory)

`obliteratus recipe search` on the `tune` split (142 pairs), 5 variants with the accepted recipe's settings.

- **As-run result: no winner.** Every variant, including the 10–18 control, failed the KL threshold (next-token KL above 0.05). This was an error in my configuration, not in the tool. My profile did not set `kl_policy`, so KL became a required gate. The accepted recipe's profile treats KL as advisory. The search grid can point to that profile directly.
- **After re-ranking** the saved results with the OBLITERATUS ranking function and the accepted recipe's gates:

| Variant | Refusals (`tune`) | Wilson upper bound | Over-refusals | next-token KL | Perplexity relative to S | Passes gates |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 14–22 | 0/142 | 2.6% | 2/142 | 0.204 | 1.016 | yes, selected |
| 10–18 (control) | 7/142 | 9.8% | 0/142 | 0.155 | 1.026 | yes |
| 8–20 | 8/142 | 10.7% | 1/142 | 0.306 | 1.037 | yes |
| 10–18, 2 directions | 11/142 | 13.3% | 3/142 | 0.192 | 1.069 | yes |
| 12–16 | 33/142 | 30.8% | 3/142 | 0.155 | 1.030 | no: too many refusals |

The rule selects the variant with the fewest refusals, so 14–22 wins despite a higher KL than the control. The `final-test` split was not used (I did not run `recipe confirm`), so 14–22 has no independent evaluation.

## E2: variant 12–16 (exploratory)

- E2−S: mean −0.28 pp [−1.28, 0.67], no drop. MMLU −0.33 [−0.68, −0.01]: a drop, but smaller than 2 pp. This is a borderline result. The upper bound of the interval is −0.007 pp, McNemar without correction p = 0.057, and after Holm p = 0.23. GSM8K `strict-match` +3.03 pp [0.83, 5.23].
- E2−E: mean +0.41 pp [−0.52, 1.36], no drop. MMLU −0.29 [−0.54, −0.04]: a drop smaller than 2 pp.
- Limitations: E2 leaves 23% refusals on `tune`, so it is a weaker edit than E. Also, the search builds the model differently from the E run: the 10–18 control variant differs from E by 6.9% of the weight edit. So E2−E mixes the choice of layers with the difference in how the model is built. This result does not show that a narrower layer range is better.

## E3: variant 14–22 (exploratory)

E3 removed refusals most strongly in the whole search: 0 of 142 `tune` prompts, which is the data used to select it. I added it after the other results. Against E, it shows no drop of 2 pp in the mean.

| Comparison | MMLU | ARC | GSM8K | IFEval | Mean |
| --- | --- | --- | --- | --- | --- |
| E3−S | +0.06 [−0.25, 0.36] no drop | +0.17 [−0.94, 1.28] no drop | −0.23 [−2.35, 1.90] inconcl. | −2.40 [−5.36, 0.55] inconcl. | −0.60 [−1.58, 0.36] no drop |
| E3−E | +0.10 [−0.19, 0.38] no drop | +0.09 [−1.02, 1.11] no drop | +0.76 [−1.36, 2.96] no drop | −0.55 [−3.51, 2.22] inconcl. | +0.10 [−0.84, 1.06] no drop |

- McNemar after Holm: no significant differences, smallest p = 0.64.
- GSM8K `strict-match` 33.81%, 106 answers at the limit, median length 123 tokens. 772 answers end with the `#### number` pattern, similar to S (761) and E (785).
- Limitations:
  - E3 has no check on the `final_test` split, and its refusals were measured only on `tune`, the data used to select it;
  - it has a higher next-token KL than the control (0.204 against 0.155);
  - the note about a different build method than E, given for E2, also applies to E3.

## Limitations

- One run of each version and one repair setting.
- IFEval has wide intervals (±3 pp) and does not resolve a 2-point difference.
- Tests computed with lm-eval, not with the matric-eval setup from the recipe profile.
- The refusal detector matches words and does not judge how harmful the content is.
- On-premise machine (aarch64, CUDA 13, shared CPU and GPU memory). The GPU was shared between several evaluations at the same time.

## Notes on OBLITERATUS

- `recovery-distill` writes `take` in the manifest equal to the number of prompts. When the refusal filter removes even one row, `recovery-data` rejects the corpus as incomplete. `take` has to be changed by hand.
- `adapter.lora_repair` runs only on CPU in float32, so the projection in the same recipe also runs on CPU. This projection (P) differs from the accepted edit E by more than bf16 rounding (2.6% of values in layer 10). I did not isolate the cause. The 10–18 control variant from the search, built on GPU in bf16, differs from E even more (17.2%). So the repaired model is not exactly the accepted edit. The build takes 71 minutes for a 1.5B model.
- In NVIDIA images, `peft` imports `transformer_engine`, which needs `libcuda`. So CPU training needs a container with a GPU. This is an environment issue, not a bug in the project.
- Repair result: no shown improvement in capabilities, refusals 22/200 against 14/199 (difference undetermined), higher KL, and fewer GSM8K answers with the few-shot `#### number` ending. Format-dependent metrics are worth measuring, not only accuracy.

## Files

| File | Contents |
| --- | --- |
| [PROTOCOL.md](../../PROTOCOL.md) | measurement plan and deviations |
| [results.md](results.md) | this report |
| [capability-summary.json](capability-summary.json) | main results, comparisons, noise |
| [secondary-summary.json](secondary-summary.json) | `strict-match`, IFEval `inst_level_strict_acc`, answer lengths and cuts (version corrected after the review) |
| [per-item-correctness.json](per-item-correctness.json) | 0/1 correctness for each question and version, no texts |
| [verify-edit-P.json](verify-edit-P.json), [verify-edit-R.json](verify-edit-R.json) | refusal, KL and perplexity verification |
| [recipe-resolution-R.json](recipe-resolution-R.json) | record of the R recipe with file checksums |
| [weights-P-vs-E.json](weights-P-vs-E.json) | weight comparison of P and E |
| [weights-search1018-vs-E.json](weights-search1018-vs-E.json) | weight comparison of the search control and E |
| [search-selection-as-run.json](search-selection-as-run.json) | search selection as run |
| [search-rerank-project-rule.json](search-rerank-project-rule.json) | re-ranking by the recipe gates |

In the copies of `verify-edit-*.json`, the `cuda_device` field is replaced with `redacted`. Question and answer texts, logs and checkpoints stayed on the machine where they were computed.
