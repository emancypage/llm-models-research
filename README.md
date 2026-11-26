# LLM model research

Independent measurements of what changes when open-weight language models are edited. The experiments run Qwen, Bielik and selected Llama checkpoints locally with OBLITERATUS. Each study records its evaluation questions, results, comparison conditions and known failures. The studies answer different questions and use different model versions.

This repository covers experiments on model behavior and capabilities, along with the protocols, evaluation code, results and errors needed to interpret them.

| Study | Main finding | Evidence |
| --- | --- | --- |
| Vocabulary-row edits from OBLITERATUS PR #595 | The selected 500-entry edit reduced judge A’s full-answer failure rate by 43.5 percentage points on Llama and 37.5 on Qwen. The exploratory post hoc analysis after closeout (26 November 2026) found that Llama’s edited answers omitted the selected number tokens, which appeared in the reference solutions for 45 of its 52 lost GSM8K items. Qwen’s selected list contained no digits, and both intervals for its math score change included zero. | [Final report](reports/2026-11-23-obliteratus-vocab-surgery/results.md) · [Protocol](reports/2026-11-23-obliteratus-vocab-surgery/PROTOCOL.md) · [Paired quality scores](reports/2026-11-23-obliteratus-vocab-surgery/data/quality-paired.json) · [Reproduce the results](experiments/2026-11-23-obliteratus-vocab-surgery/README.md#reproduce-the-final-quality-comparisons) · [Issue log](reports/2026-11-23-obliteratus-vocab-surgery/issues.md) |
| LoRA repair after editing Qwen2.5 | At 1.5B, the strict GSM8K score fell 9.86 percentage points after repair while flexible scoring changed by +0.61. At 3B, the flexible score gained 6.14 points. Among the 735 items where both answers finished below the length limit, the change was −0.41 points. | [Results](reports/2026-11-22-obliteratus-multi-model/results.md) · [Protocol and amendments](reports/2026-11-22-obliteratus-multi-model/PROTOCOL.md) · [Issue log](reports/2026-11-22-obliteratus-multi-model/issues.md) |
| Qwen2.5-1.5B recipe and capability evaluation | The earlier study documents how the recipe was chosen, how the published selection rule differed from the run, and which capability scores changed. | [Recipe study](reports/2026-11-21-qwen2.5-1.5b-recipe/results.md) · [Capability results](reports/2026-11-21-qwen2.5-1.5b-recipe/data/capabilities/results.md) |
| How OBLITERATUS scores GSM8K | On the first 100 test items, the reported scores were 92% and 88% for two published Qwen3-8B checkpoints. Both scores matched the strict answer-extraction rule. The pilot covers five items per model. | [Main comparison](reports/2026-11-21-obliteratus-gsm8k/results.md) · [Pilot](reports/2026-11-21-obliteratus-gsm8k/data/pilot/results.md) · [Evaluation code](experiments/2026-11-21-obliteratus-gsm8k) |
| Polish verb tense in Bielik 11B | All 128 held-out answers stayed the same after the edit, including one wrong answer. The Polish Belebele reading score changed from 782 to 781 out of 900. | [Unsuccessful first attempt](reports/2026-11-21-bielik-11b-polish-tense/issues.md) · [Held-out results](reports/2026-11-21-bielik-11b-polish-tense/results.md) · [Safety repeats](reports/2026-11-21-bielik-11b-polish-tense/data/variant-2/safety/128-token-repeats/report.md) |
| Single-layer edit in Bielik 11B | The model matched 7 of 8 reference answers before the edit and 6 after it. Restoring the weights reproduced the original control logits exactly. | [Results](reports/2026-11-21-bielik-11b-compatibility/results.md) · [Protocol](reports/2026-11-21-bielik-11b-compatibility/PROTOCOL.md) |

## Reading the evidence

Start with the protocol and results in the same study directory. The accompanying JSON files contain aggregate measurements and, where recorded, per-item correctness or refusal flags. The [interim research diary](session-logs/2026-11-22-obliteratus-multi-model.md) records decisions made while the multi-model study was running. Its final protocol and report identify which planned experiments ran. [Evaluation scripts](experiments) are included for the GSM8K and Bielik studies.

The public files retain measurements and methodological limitations. Identifying operational details have been removed. Historical hashes and byte counts describe the original artifacts before redaction. [Bielik publication notes](reports/2026-11-21-bielik-11b-polish-tense/publication-notes.md) document the scope of that dataset and its offline checks.

### Disclaimer

All reports in this repository were written by AI under my supervision. I can't verify every claim, but I and other collaborators always check the main conclusions. If you spot any inconsistencies, contradictions, or illogical assumptions or conclusions, please open an issue. I'd really appreciate your help.

AI is moving fast, and I believe open collaboration is the only way we can keep up.
