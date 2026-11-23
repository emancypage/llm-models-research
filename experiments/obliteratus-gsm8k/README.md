# GSM8K checkpoint comparison

This experiment compares two published Qwen3-8B checkpoints on arithmetic problems. It records both GSM8K scoring rules and the headline score returned by OBLITERATUS. The [protocol](PROTOCOL.md) specifies the checkpoints, question selection and scoring rules. The [main report](../../reports/2026-11-21-obliteratus-gsm8k/REPORT.md) contains the historical results.

## Check the setup

From the repository root, check out the version of OBLITERATUS used for the study:

```sh
git clone https://github.com/elder-plinius/OBLITERATUS.git vendor/OBLITERATUS-7678d841
git -C vendor/OBLITERATUS-7678d841 checkout --detach 7678d84196fe6c348dfd01078bbfb50857463647
cd experiments/obliteratus-gsm8k
python3 -m unittest
python3 study.py check
```

The integration test uses the pinned telemetry implementation and substitutes fixtures for model loading and generation. The diagnostic command writes a telemetry record to a temporary directory and reads it back. It does not download model weights. Use `--source` to point the script to a different checkout of the same revision.

## Run the pilot and main comparison

Install a CUDA-enabled PyTorch build, Transformers with Qwen3 support, and `lm_eval[hf]==0.4.13`. If the public checkpoints or the dataset are missing from the cache, the evaluation libraries need network access.

```sh
python3 study.py pilot
python3 study.py main
```

The pilot measures five questions per model and the main comparison measures 100. Each run prints the path of its new directory under `./runs/` before measurement starts. The script calls `compare_models` and saves a local `BenchmarkRecord` after each model evaluation. Both GSM8K scores are recorded in `extra.gsm8k_exact_match`. Synchronization with Hugging Face is disabled.

The `private/` directory contains the telemetry log and full responses for verification. Once both models finish, the script writes the protocol, a results table and `results.json` to `share/`. The table and JSON are marked as awaiting human review. The script does not publish the files.
