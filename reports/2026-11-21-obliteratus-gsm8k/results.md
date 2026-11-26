# GSM8K comparison (main)

Automated scoring and verification are complete for 100 questions per model. The available study record contains no completed human review of this comparison. Review status checked on 26 November 2026 after closeout. [Main measurement record](data/main/results.json)

| Model | Strict | Flexible | OBLITERATUS |
| --- | ---: | ---: | ---: |
| Qwen/Qwen3-8B | 92.0% | 93.0% | 92.0% |
| BabarAzaa/Test3 | 88.0% | 86.0% | 88.0% |

OBLITERATUS score difference (modified minus original): -4.0 percentage points.

## Verification against saved answers

Each scoring rule was recomputed from the raw text and the reference answers. All 400 per-answer scores matched the evaluation library. Both local telemetry records matched the reported aggregates.

| Paired outcomes | Strict | Flexible |
| --- | ---: | ---: |
| Both correct | 86 | 85 |
| Only original correct | 6 | 8 |
| Only modified correct | 2 | 1 |
| Both incorrect | 6 | 6 |

The reported differences describe the first 100 GSM8K test examples for these two published checkpoints. Both were evaluated in BF16.

Dataset revision: `740312add88f781978c0658806c59bc2815b9866`. The strict rule expects the final number to follow the GSM8K answer marker. The flexible rule extracts the last matching number.

## Post hoc analysis after closeout (26 November 2026)

The exploratory exact two-sided McNemar test used the strict scores on the same 100 questions. Six items changed from correct to incorrect and two from incorrect to correct. The observed difference was −4 percentage points (92 to 88 correct). Under equal probabilities for the two directions, an imbalance at least this large among eight discordant pairs has probability 0.2890625. This sample gives no clear evidence of a difference under the strict rule. Run `python3.12 experiments/2026-11-21-obliteratus-gsm8k/strict_mcnemar.py --check` from the repository root to reproduce the result. [100 paired scores](data/analysis/post-hoc-strict-pairs.csv) · [Exact test result](data/analysis/post-hoc-strict-mcnemar.json) · [Analysis script](../../experiments/2026-11-21-obliteratus-gsm8k/strict_mcnemar.py)

[Protocol](PROTOCOL.md) · [Main measurement data](data/main/results.json) · [Pilot results](data/pilot/results.md) · [Code and instructions](../../experiments/2026-11-21-obliteratus-gsm8k/README.md)
