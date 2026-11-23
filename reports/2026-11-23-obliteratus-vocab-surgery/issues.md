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
