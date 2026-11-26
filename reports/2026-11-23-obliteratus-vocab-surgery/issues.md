# PR #595 bug log (vocabulary-row edits)

PR head `5e55cdae09f1ae0213c13869842bdbfaae138ce6`, merged into `main` on 23 November 2026 as `1de580f7a13f185488dc31ff27f2e027545ad82d` with no change to the vocabulary-edit code. Each entry: date, what was checked, result.

## 2026-11-23, code read for safety (task 0.1)

Files read: `obliteratus/strategies/vocab_surgery.py`, `obliteratus/strategies/vocab_surgery_discovery.py`, `obliteratus/vocab_surgery_cli.py`, `obliteratus/recipes/techniques_vocab_surgery.py`, and the changes in `runner.py`, `cli.py` and `abliterate.py`.

- No network calls in the new code. Models load through the existing loader; with `--local-files-only` nothing is fetched.
- Remote model code runs only with `--trust-remote-code`; the study never passes it.
- `vocab-surgery apply` refuses an existing output directory. It writes a staging directory and a lock next to the output directory, then renames the staging directory. No other writes.
- `vocab-surgery discover` writes only the files given in `--output` and `--config-output` (not used in this study).
- The row edit itself is pure tensor work on the input and output matrices; it writes a receipt with row hashes before and after.
- Result: no blocker. The code still runs only in a container without network.

## 2026-11-23, PR unit tests (task 0.1)

`tests/test_vocab_surgery.py` and `tests/test_strategies.py`: 75 passed, 0 failed. The PR configuration adds coverage options that need `pytest-cov`; the tests ran without coverage.

## 2026-11-23, export does not copy the source files (task 0.4)

Check: `vocab-surgery apply` with a no-op config (S0: one operation with `output_scale` 1.0) on Qwen2.5-7B-Instruct, then a file and tensor comparison with the source (`check_receipt.py`).

- Weights: all tensors bit-identical; 0 changed input rows, 0 changed output rows. The receipt still reports 1 changed output row, because it counts operations, not changed rows.
- The tool always saves the tokenizer and the config again with the installed `transformers` (5.17.0) instead of copying the source files. Result for S0:
  - the tokenizer file set changes: `vocab.json` and `merges.txt` are gone, `chat_template.jinja` is new; `tokenizer.json` and `tokenizer_config.json` differ in content (in `tokenizer.json`: the decoder settings `add_prefix_space`, `trim_offsets`, `use_regex`, the pre-tokenizer and the model section);
  - `config.json` differs: `sliding_window` 131072 → `null`, new `layer_types`, `pad_token_id: null`, `rope_theta` moved into `rope_parameters`, new `dtype`, `transformers_version` 4.43.1 → 5.17.0. `generation_config.json` differs only in `transformers_version`.
- Behaviour measured so far is the same: chat-template SHA-256 equal; token IDs equal on 640 texts (240 probe items and 400 held-out prompts) and on 400 chat-rendered prompts; decoding equal on 640 texts; no differences in pad, BOS, EOS, padding side or maximum length; word-probe logits on 240 items exactly equal (largest difference 0.0).
- Effect on the study: the plan requires the tokenizer files of V to be the same as in S, and treats a failed S0 check as "the write itself changes the model". The byte check fails for every exported checkpoint, also on Qwen2.5-1.5B (`k1o-tied` pilot). The stage was stopped on this point and reported.
- For the PR author: an export that only edits rows could copy the source tokenizer and config files and write only the changed weights; otherwise a no-op edit is not a no-op at the file level.
- Diagnostic run in the real pipeline: `verify-edit` with stock = S and edited = S0 on Qwen2.5-7B-Instruct (691.5 s). Refusal flags, invalid flags and all 400 answer texts (200 harmful, 200 harmless) are identical; KL: first-token mean 0.0, next-token mean 6.2e-20; perplexity ratio 1.0. So the re-saved files do not change behaviour in this pipeline; only the byte check fails.

## 2026-11-23, merged version (`1de580f7a13f185488dc31ff27f2e027545ad82d`)

The merge adds no change to the files checked above. The export behaviour from the S0 check is the same on `main`: the checkpoint writer did not change. PR tests on `main`: 75 passed, 0 failed.

## 2026-11-24, export changes the weight-file layout

The edited Llama-3.1-8B checkpoint is written as one `model.safetensors` file without an index, while the source has 4 shards and `model.safetensors.index.json`. The tensors are the same (scope check), but tools that read the index file to find a tensor fail on the export. This adds to the entry above: the export does not keep the source file layout.

## 2026-11-24, study environment: Gemma 4 26B-A4B does not load within memory limits

Not an OBLITERATUS issue. With `transformers` 5.17.0 and `AutoModelForCausalLM.from_pretrained(..., dtype=bfloat16, device_map="cuda")` on a machine where the GPU shares 121 GiB with the system, loading `google/gemma-4-26B-A4B-it` (51.6 GB of weights, 128 experts) kept allocating past the weight size until 16 GiB remained. The study used the planned spare judge instead.

## 2026-11-24, detector and judge disagreements after a vocabulary edit

On Qwen2.5-7B, the keyword detector flagged 165 original answers and 73 answers after the full PR-list edit, out of 200 in each condition. Among valid answers it did not flag, judge A classified 6/34 before the edit and 87/126 afterwards as refusals. Judge B classified 91 of those 126 edited answers as refusals. In the other direction, A classified 22 flagged answers from the original Llama as compliant. The 200-row manual check was omitted. These counts establish disagreement with the judges, whose labels have no formal validation on this short-answer dataset.

## 25 November · Study data export

During a read-only check, the study exporter treated the quality follow-up directory as a single version. This would have combined the original Llama math score with the selected-list instruction-following score. The local exporter was corrected before publication. The final data have one entry for each of the 16 new model/version/test combinations. This was an issue in the study’s reporting code.

## 25 November · Two GSM8K extraction errors

Qwen’s selected-list answers to items 19 and 109 both state the expected result. On item 19 the flexible extractor chose the later number 4 after the answer gave 6 miles per hour. On item 109 it returned `$28.00.`, which did not match the reference `28` under the benchmark rule. Both count as losses in the published scores. These cases limit the interpretation of score changes as errors in the model’s mathematical reasoning. [Saved answers and extracted values](data/gsm8k-comparisons/qwen-01-05.md)

## Post hoc analysis after closeout (26 November 2026)

**Exploratory finding about number tokens and the random controls.** The selected Llama list includes ten digit-only tokens. With a 1024-token allowance, 45 of its 52 GSM8K losses had at least one in the reference solution. In the 400 re-tokenized edited answers their count was zero. Qwen's selected list contains no digits. Both random lists included digits, an MMLU answer letter, and punctuation. For Qwen, all 207 originally correct math answers whose reference final number contained a random-list digit lost credit. In the Llama and Qwen random MMLU runs, the edited answer letter lost all its originally correct items. The large gaps between selected and random arms include this difference in the tokens each benchmark uses. A single random draw cannot estimate variation across lists. [Token inventories and group definitions](data/analysis/token-exposure/README.md) · [Grouped counts](data/analysis/token-exposure/summary.json)
