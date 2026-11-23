# GSM8K comparison (main)

Awaiting human review. 100 questions per model.

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

[Protocol](PROTOCOL.md) · [Main measurement data](data/main/results.json) · [Pilot results](data/pilot/results.md) · [Code and instructions](../../experiments/2026-11-21-obliteratus-gsm8k/README.md)
