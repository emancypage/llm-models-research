# Reproduce the strict IFEval scores

Q1 and Z2 use Qwen2.5-1.5B-Instruct. Q3 uses Qwen2.5-3B-Instruct. Each version received the same 541 prompts with up to 1280 new tokens. A prompt passes if it satisfies all its instructions. Strict instruction accuracy gives each of the 834 instructions one vote.

Each CSV gives the zero-based prompt ID, the number of instructions and how many instructions each version passed. These are the integer counts from the evaluation harness’s per-prompt strict checks. The adjacent `per-item-correctness.json` gives the whole-prompt verdicts. Z2 uses the stored keys `PS` and `RS` for its level A variants labelled P_A and R_A in the tables. Q1 uses those keys for its own variants. [Q1 items](../../reports/2026-11-22-obliteratus-multi-model/data/q1/ifeval-items.csv) · [Q3 items](../../reports/2026-11-22-obliteratus-multi-model/data/q3/ifeval-items.csv) · [Z2 items](../../reports/2026-11-22-obliteratus-multi-model/data/z2/ifeval-items.csv)

From the repository root, run the following command with Python 3.12 and NumPy 2.1.0. The recomputation includes the instruction-level paired differences and their 95% intervals (10,000 draws with seed 42, resampling whole prompts). Remove `--check` to regenerate both JSON summaries in each group and the marked tables and text in the reports.

```sh
python3 experiments/2026-11-22-obliteratus-multi-model/rebuild_ifeval.py --check
```

In `capability-summary.json`, `ifeval.primary` is the fraction of prompts that pass every check. The `secondary` field is `instructions_passed / instructions_total`, the same measurement as `ifeval_inst_level_strict` in `secondary-summary.json`. The earlier mean of the per-prompt instruction fractions is preserved under `historical_mean_prompt_fraction`. The settings identify the checkpoint, token limit and both scoring rules.
