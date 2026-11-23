# Qwen2.5-1.5B-Instruct: reproduction of the recipe `qwen2.5-1.5b-mid10-18-dim1`

On 21 November 2026 I reproduced the accepted OBLITERATUS recipe on an on-premise machine (aarch64, CUDA 13). Four of the five verdicts agree with the project's evidence. I did not measure capabilities here, because the matric-eval tool is missing. The weight edit shifts the answers to ordinary prompts more than a random edit of the same size. Even the strongest of 10 random edits gave about 3 times lower next-token KL and 4.6 times lower first-token KL.

Capabilities were measured later with lm-eval: see [data/capabilities/results.md](data/capabilities/results.md).

## Versions

| Item | Value |
| --- | --- |
| OBLITERATUS | `7678d84196fe6c348dfd01078bbfb50857463647`, clean checkout |
| Model | `Qwen/Qwen2.5-1.5B-Instruct` @ `989aa7980e4cf806f80c7fef2b1adb7bc71aa306` |
| Recipe | `qwen2.5-1.5b-mid10-18-dim1` 1.0.0, status `accepted` |
| Evaluation profile | `profiles/qwen2.5-1.5b-mid10-18-dim1.json`; resolved spec [spec.json](data/spec.json), SHA-256 `ff1b4ea2…a49c` |
| Environment | torch `2.13.0a0+9186a08b2c.nv26.07`, transformers 5.17.0, bfloat16, batch 8, no network, telemetry off |

## `verify-edit` verdicts (200 `final_test` pairs)

| Endpoint | My result | Project evidence |
| --- | --- | --- |
| `heldout_refusal` | pass: refusals 92.0% → 7.5% (15/199), Wilson upper bound 12.1% against a 20% threshold | pass |
| `collateral` | pass: over-refusals 7.5% → 1.5%; coherence 100% → 99.5% | pass |
| `kl` (advisory) | fail: first-token 0.0665 (threshold 0.10), next-token 0.1601 (threshold 0.05) | fail |
| `perplexity` (advisory) | pass: ratio 1.032 against a threshold of 1.25 | pass |
| `capability` | untested: no `matric-eval` | pass |
| Overall | `INCOMPLETE` (exit code 3) | `PASS` |

The project publishes only verdicts. The numbers from its run cannot be compared.

## KL on the same 50 `tune` prompts

The noise check, the random control and the extra measurement of the edit use the same 50 harmless prompts. Hash of the prompt list: `e8f26354…84c0`.

| Measurement | first-token KL | next-token KL |
| --- | ---: | ---: |
| Noise: the same model loaded again, batch 8 | 0.00137 | 0.00613 |
| 10 random edits: mean | 0.00529 | 0.02914 |
| 10 random edits: 0.95 quantile | 0.01185 | 0.04730 |
| 10 random edits: maximum | 0.01488 | 0.05385 |
| **Recipe edit** | **0.06818** | **0.15854** |

- The recipe edit gives 5.8 times more first-token KL and 3.4 times more next-token KL than the 0.95 quantile of the random edits.
- With one prompt at a time (batch 1), the noise is zero. All measured noise appears only with 8 prompts at once.
- The recipe edit gives almost the same KL on `final_test` prompts (0.0665 and 0.1601) and on `tune` prompts (0.0682 and 0.1585).
- Thresholds from the random control (0.0118 and 0.0473), used as a hard gate, would reject this edit.

Interpretation: a direction chosen on purpose should change the model more than a random direction, because random directions usually land where the model hardly looks. So the random control is a lower reference point, not a border between a harmless and a harmful edit. The project documentation calls such thresholds material for the operator's judgment. The result shows that the edit is clearly stronger than chance. It does not show a loss of capabilities. Two weak signals point to a small degradation: perplexity rose by 3.2%, and answer coherence dropped to 99.5%.

## Not measured here

- Capabilities (ARC, GSM8K, IFEval, MMLU). The profile needs the matric-eval options `--temperature` and `--generation-seed`. I did not find them in `src/matric_eval/cli.py` of the public copy of `jmagly/matric-eval` (last commit on 14 September).
- Harmfulness of the answers. The refusal detector matches words and does not judge content.
- Reproducibility of the weight edit itself. The project's weight checksums are not published.

## Files

- [spec.json](data/spec.json): the resolved recipe profile.
- [spec-tune-kl.json](data/spec-tune-kl.json): the same profile with `tune` prompts and without capability evaluation.
- [recipe-resolution.json](data/recipe-resolution.json), [abliteration_metadata.json](data/abliteration_metadata.json): record of the applied edit.
- [calibration.json](data/calibration.json): noise.
- [random-control.json](data/random-control.json): 10 random edits.
- [verify-edit-final-test.json](data/verify-edit-final-test.json): full verification.
- [verify-edit-tune-kl.json](data/verify-edit-tune-kl.json): KL of the edit on `tune` prompts. Only the KL numbers matter. The `PASS` verdict in this file means nothing: capability evaluation was turned off, and the `tune` prompts were used to choose the recipe.

The reports contain no prompt or answer texts. In the copies of `data/verify-edit-*.json`, the `cuda_device` field is replaced with `redacted`. The edited weights and logs stayed on the machine where they were computed.

[Protocol for the subsequent capability evaluation](PROTOCOL.md) · [Capability results](data/capabilities/results.md)
