# Bielik 11B Polish tense protocol

Study ID: `2026-11-21-bielik-11b-polish-tense`.

The two manifests record the conditions used on 21 November 2026. This protocol reconstructs the procedure from those manifests, the code and the run reports. [Initial manifest](data/protocol.json) · [Revised manifest](data/variant-2/protocol.json) · [Report](results.md) · [Initial failure](issues.md) · [Reproduction](../../experiments/2026-11-21-bielik-11b-polish-tense/README.md)

## Question and pinned inputs

Does an OBLITERATUS weight intervention along a direction extracted from Polish past/present verb forms change tense answer selection, and how does Polish reading comprehension change?

| Input | Recorded revision |
| --- | --- |
| `speakleash/Bielik-11B-v2.3-Instruct` | `73f5f7fb9a79a4409d02740155a3868c1ff0d2bc` |
| OBLITERATUS | `7678d84196fe6c348dfd01078bbfb50857463647` |
| `UniversalDependencies/UD_Polish-LFG` | `9a0be46202ce87f0a507f427c52594c863a197e2` |
| `facebook/belebele` | `7899cdfa4e1e0d733fd77c848e2c273cb1d32be2` |

Both designs use seed `20261121`, 64 fit lemma pairs from the UD training partition and 32 held-out lemma pairs from the test partition. Selection uses a seeded hash order. The code excludes shared lemmas and surface forms across fit and holdout. It selects attested root verbs marked imperfective, singular, finite and active. [Source selection code](../../experiments/2026-11-21-bielik-11b-polish-tense/tense_study.py)

## Initial design and revision

The initial contrast uses isolated past and present forms. Difference of means extracts a direction; five-fold validation grouped by lemma selects a layer using area under the receiver operating characteristic curve (AUC). Validation is enforced. The saved run failed the lexical-confound gate before editing weights; the AUC gap of `0.033` fell below `0.05`. It has a 64-item tense baseline, not a completed before/after intervention. [Validation evidence](data/isolated-form-validation.json)

The revised design presents both forms and asks about the first or second form. Each verb supplies four order/position combinations. There are 256 fit items, 128 per class, and 128 held-out items. Within each lemma the classes have the same words, with order and queried position balanced. The extraction prefill is preserved in the manifest. Five folds remain grouped by lemma. The intended rule is to stop on a native gate failure without overriding it. [Revised construction](../../experiments/2026-11-21-bielik-11b-polish-tense/paired_tense.py)

## Intervention and evaluation

The revised run uses the native `basic` intervention, CUDA, `float16`, no remote model code, and validation mode `enforce`. A direction that predicts the class well is not proof that editing along it changes answers. The held-out tense task chooses between A/B next-token scores, with answer-label order alternating between lemma pairs. Its outcome is an answer selection, not a generated explanation.

The collateral benchmark scores all 900 Polish Belebele items by forced A/B/C/D next-token scores, using the same pinned checkpoint and benchmark revision before and after. The custom benchmark is separate from native collateral checks, which the script skips. [Benchmark code](../../experiments/2026-11-21-bielik-11b-polish-tense/belebele.py) · [Baseline](data/belebele-before.json)

The revised validation selected layer 16 and returned `pass`. Recorded tense scores were 127/128 before and after, with every prediction unchanged. Reading scores were 782/900 and 781/900. Reload verification covered 12 shards and reproduced all 128 edited predictions. These are observed results, not protocol predictions. [Run](data/variant-2/concept_run.json) · [Tense predictions](data/variant-2/heldout-tense.json) · [Reading predictions](data/variant-2/belebele-after.json) · [Reload verification](data/variant-2/checkpoint-verification.json)

## Separate follow-up and limits

Later refusal measurements are separate follow-up evidence under [safety](data/variant-2/safety/report.md), including [128-token repeats](data/variant-2/safety/128-token-repeats/report.md). The historical grammar manifests say safety was not measured at that stage; preserve that timing. Neutral grammar prompts occupy standard schema fields whose names refer to harmful/harmless prompts. Those fields alone do not measure safety.

The study concerns one model revision, one intervention and fixed samples. Predictive separation of activations did not produce a change in the measured tense answers. Stored checkpoint verification is available, but the model weights, full execution environment and raw runtime logs are outside this repository.
