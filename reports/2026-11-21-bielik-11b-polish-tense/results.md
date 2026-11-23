# Bielik 11B and the tense of a specified verb form

On 21 November 2026, a full OBLITERATUS procedure finished on premise. It tested whether changing weights along a direction extracted from Polish verb forms changes answers about the tense of a specified form. On held-out verbs, all 128 answers were identical before and after editing.

| Measurement | Before | After |
| --- | ---: | ---: |
| Tense of the specified form, 128 cases | 127 (99.2%) | 127 (99.2%) |
| Reading comprehension, 900 Polish Belebele questions | 782 (86.9%) | 781 (86.8%) |

For each of 64 verbs used to extract the direction, the model saw four combinations of form order and queried position. Both classes contained the same words for each verb. Five-fold validation grouped examples by verb. The direction selected at layer index 16 achieved AUC 1.000; a word and character-trigram classifier achieved 0.497. OBLITERATUS returned `pass` with `enforce` enabled and no overrides. [Protocol](data/variant-2/protocol.json) · [OBLITERATUS report](data/variant-2/concept_run.json)

The tense test used 32 separate verbs with four questions each. Bielik made the same single error before and after. In Belebele, two correct answers became incorrect and one incorrect answer became correct. These findings concern answer selection on these test sets. [Grammar answers](data/variant-2/heldout-tense.json) · [Belebele before](data/belebele-before.json) · [Belebele after](data/variant-2/belebele-after.json)

OBLITERATUS saved a local contribution in the project's format and a separate telemetry record. This was a grammar experiment. Refusal fields in the standard schema refer here to neutral language questions. [Contribution](data/variant-2/bielik-11b-v2-3-instruct_basic_20261121_175414.json) · [Telemetry](data/variant-2/telemetry.jsonl)

The first two export attempts stopped on the custom concept identifier. After correcting metadata, the procedure restarted from original weights with the same examples, split, seed and validation thresholds. The exported model was stored on premise at the portable equivalent `work/tense-v2/model/`. Model, corpus, benchmark and tool revisions are recorded in the protocol.

All 12 weight shards were reloaded. The saved model reproduced every one of the 128 recorded post-edit answers. Native OBLITERATUS validators accepted both the run record and the contribution. [Verification](data/variant-2/checkpoint-verification.json)

[Protocol for both attempts](PROTOCOL.md) · [Unsuccessful first attempt](issues.md) · [Repeated refusal measurements](data/variant-2/safety/128-token-repeats/report.md) · [Code and instructions](../../experiments/2026-11-21-bielik-11b-polish-tense/README.md)
