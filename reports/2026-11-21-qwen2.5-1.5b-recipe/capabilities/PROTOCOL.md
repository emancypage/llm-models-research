# Protocol: do the recipe and LoRA repair lower the capabilities of Qwen2.5-1.5B?

> English translation, made on 22 November 2026 after the results. The original was written in Polish before the measurements. The dates of the deviations are the same as in the original.

Written on 21 November 2026, before the capability measurements. Changes after the first results are reported as deviations.

## Questions

1. Does the accepted recipe `qwen2.5-1.5b-mid10-18-dim1` lower the model's capabilities?
2. Does the new technique `adapter.lora_repair` (OBLITERATUS #578, 20 November 2026) recover lost capabilities, and does it restore refusals?

## Model versions

| Version | Description |
| --- | --- |
| S | `Qwen/Qwen2.5-1.5B-Instruct` @ `989aa7980e4cf806f80c7fef2b1adb7bc71aa306` |
| E | S after the recipe; checkpoint from an earlier run, file checksums in `../recipe-resolution.json` |
| R | E after LoRA repair, built by one v2 recipe: `abliteration.projection` with the accepted recipe's parameters, then `adapter.lora_repair`, `merge: true` |

R is built on CPU in float32, because the technique requires it. Before the evaluation I will compare the weights of the projection step with E. If the difference exceeds bf16 rounding, the reference for R will be the projection from the same run, and the report will say so.

Repair settings:
- layers 10–18, modules `attn_out` and `mlp_out`;
- rank 8, alpha 16, learning rate 2e-4, 1 epoch, batch 1, gradient accumulation 8, max_length 768, seed 42.

The repair data (self-distillation) is made like this:
- S answers greedily, up to 512 tokens, to harmless prompts from the `train` split of the `qwen38-v1` protocol;
- answers with a refusal are removed (policy `drop`).

I will choose the number of prompts, 500 or 250 evenly selected, after measuring generation speed and before training. The report will also give how many teacher answers were cut at the token limit. No question from the capability tests goes into the repair data.

## Capability tests

Tool: lm-eval 0.4.13, HF backend, bf16, CUDA, batch 32, default lm-eval seeds, `--log_samples`. The same settings for S, E and R. Full test sets.

| Test | Questions | Settings | Primary metric |
| --- | ---: | --- | --- |
| MMLU (`mmlu`) | 14,042 | 5-shot, no chat template | accuracy over all items (micro) |
| ARC-Challenge | 1,172 | 25-shot, no chat template | `acc_norm` |
| GSM8K | 1,319 | 5-shot, chat template, `--fewshot_as_multiturn`, greedy, 256 tokens | `flexible-extract`; `strict-match` as secondary |
| IFEval | 541 | 0-shot, chat template | `prompt_level_strict_acc`; `inst_level_strict_acc` as secondary |

The multiple-choice tests run without the chat template, because that is the standard setup. The generation tests run with the template, because the refusal direction was found with the chat template and the model is used that way.

The project uses the same four tests with a margin of 2 percentage points on the mean. My evaluation is a deviation from the recipe profile. The profile uses matric-eval at the `quick` level through vLLM. I use lm-eval on the full sets.

Fallback rule, set before the pilot: if the pilot predicts more than 4 hours for S and E together, MMLU and ARC switch to 0-shot.

## Statistics and verdicts

- Comparisons: E−S, R−S and R−E. Questions are paired by `doc_id`, and the question sets of both versions must be identical.
- 95% confidence interval for the difference from a paired bootstrap (10,000 draws, seed 42). In addition, an exact McNemar test with Holm correction over the four tests in each comparison.
- Verdicts for each test:
  - "drop": the whole interval is below 0;
  - "practically significant drop": a drop of at least 2 percentage points;
  - "no drop": the interval excludes −2 percentage points;
  - "inconclusive": all other cases.
- The mean of the four primary metrics, with a bootstrap interval, compared with the project margin (2 percentage points).
- Expected half-width of the intervals: MMLU ±0.5, ARC ±1.5–2, GSM8K ±1.5–2, IFEval ±3–4 percentage points. IFEval may not resolve a difference of 2 points.

## Checks

- Generation noise: a second S run on the first 200 GSM8K questions. The number of answers that differ is the noise floor.
- Signs of degeneration: the number of GSM8K and IFEval answers that reached the token limit, for each version.
- For R: `verify-edit` with the same `spec.json` as for E (refusals, over-refusals, KL, perplexity).

## Deviations recorded during the work, before the R results

- 21 November, before distillation: a distillation pilot on 10 prompts took 9.5 s per prompt, with the GPU shared with the S and E evaluation. I chose 250 prompts, as the protocol rule says.
- 21 November, before distillation: in the pilot, 3 of 10 teacher answers were cut at the 512-token limit. Training on cut answers could teach the model to stop mid-answer. I raised the teacher answer limit to 1024 tokens and the repair `max_length` to 1152.

- 21 November, before the first full result: the first S run with batch 32 used almost all of the shared CPU and GPU memory on the longest MMLU examples. The vocabulary logits of Qwen (152k tokens) for whole sequences take tens of GB there. I stopped it before MMLU finished and deleted its results. The batch size is now 4 for MMLU and ARC and 16 for GSM8K and IFEval, including the S repeat on GSM8K. The same settings apply to S, E and R. A separate guard stops the study containers when available memory drops below 16 GiB.

- 21 November, before building R: I add version P. P is the checkpoint after the projection step from the same run as R, before LoRA repair, evaluated in bf16 with the same tests. I always compute both comparisons: R−P and R−E. I record the rule for choosing the primary comparison before comparing the weights. E is saved in float16, and all versions are evaluated in bf16. So I cast P and E to bf16, as in evaluation, and compare them element by element. If in any matrix more than 0.1% of the elements differ by more than 1 bf16 step, the difference exceeds bf16 rounding. Then the primary comparison for the repair is R−P. Otherwise, R−E is primary. The report will also give the relative difference of the edits: ‖(P−S)−(E−S)‖ / ‖E−S‖.

- 22 November, before building R: the refusal filter (`refusal-heuristic-v1`, policy `drop`) removed 13 of 250 teacher answers. The manifest from `recovery-distill` required 250 rows (`take: 250`), so `recovery-data` rejected the corpus as incomplete. I used a copy of the manifest with `take: 237`. So the repair trains on 237 answers. 1 of 250 answers reached the 1024-token limit, and the median length is 452 tokens.

## Exploratory additions, set before their results

- Recipe search v2 (`obliteratus recipe search`) on the `tune` split of the `qwen38-v1` protocol (142 pairs). Five variants with the accepted recipe's parameters, which differ only in layers and number of directions: 10–18 (control), 12–16, 8–20, 14–22, and 10–18 with 2 directions. Selection by the project rule: fewest refusals, then lowest KL. No `recipe confirm`, because the `final-test` split was already used in test 1. (Translator's note: this means the earlier `verify-edit` runs on `final_test`.)
- Version E2: the 12–16 variant from this search, evaluated with the same four capability tests. Comparisons E2−S and E2−E. This is not exactly the historical candidate `qwen2.5-1.5b-mid12-16`, because it uses the accepted recipe's settings.
- These results are exploratory and do not change the answers to questions 1 and 2.

## Deviation recorded after the search results, before the E2 results

- 22 November: the search ended with no winner, because every variant, including the 10–18 control, failed the KL threshold (next-token KL 0.15–0.31 against a limit of 0.05). The cause is in my search profile. It did not set `kl_policy`, so KL became a required gate. The accepted recipe's profile treats KL as advisory only, and E itself has a KL of about 0.16. The protocol said "the project rule". So I re-ranked the saved candidate results with the OBLITERATUS ranking function, using the required gates from the accepted recipe's spec. I did not run the search again. The report gives both results: the as-run result (no winner) and the re-ranked result.
- E2 stays the 12–16 variant, as recorded before the results, even though this variant fails the refusal threshold.

## Changes after the S, E, P, R and E2 results

- 22 November, before the E3 results: I add version E3. E3 is the 14–22 variant, selected by the re-ranking of the search. I evaluate it with the same four tests and settings. Comparisons: E3−S and E3−E. E3 is exploratory and does not change the answers to questions 1 and 2. No `recipe confirm`.
- 22 November, after the results: the analysis of the GSM8K answer format was added after the results. It was not planned. It covers intervals and the McNemar test for `strict-match`, the McNemar test for answers at the token limit, counting `####` endings and reading a few answers.
- 22 November, after an independent review of the results: the secondary IFEval instruction-level metric was computed as an average over prompts, not over instructions as lm-eval's `inst_level_strict_acc` does. I fixed the script and recomputed this metric. The other numbers did not change. The review also corrected several numbers and phrasings in the results report. Conclusions 1 and 2 did not change.
- 22 November: the verdict labels in the JSON files are in English ("no drop", "drop", "practically significant drop", "inconclusive"). The numbers did not change.

## Results to share

- This protocol, the aggregate JSON files and the per-item correctness vectors without text.
- The results report. The public reports are in English. The English protocol is a translation made after the results. The version written before the results is the Polish one.

Question texts, answers and logs stay on the machine where they were computed.
