# Reproducing the Bielik compatibility check

Study ID: `2026-11-21-bielik-11b-compatibility`.

[Protocol](../../reports/2026-11-21-bielik-11b-compatibility/PROTOCOL.md) · [Report](../../reports/2026-11-21-bielik-11b-compatibility/results.md) · [Recorded measurements](../../reports/2026-11-21-bielik-11b-compatibility/data/results.json)

`check.py` performs a benign eight-question evaluation, zeroes one feed-forward module, and restores its parameters in memory. `polish-questions.json` supplies the original Polish prompts and targets.

## Offline checks

Run from the repository root. Python 3 is enough for these checks; they do not load the model or contact a service.

```sh
python -m json.tool experiments/2026-11-21-bielik-11b-compatibility/polish-questions.json > /dev/null
python - <<'PYCODE'
import hashlib, json
from pathlib import Path
root = Path('reports/2026-11-21-bielik-11b-compatibility/data')
questions = Path('experiments/2026-11-21-bielik-11b-compatibility/polish-questions.json')
for name in ('first-measurement.json', 'results.json'):
    row = json.loads((root / name).read_text())
    assert row['questions_sha256'] == hashlib.sha256(questions.read_bytes()).hexdigest()
    for stage in ('before', 'after'):
        assert len(row[stage]) == 8
        assert sum(item['zgodna_ze_wzorcem'] for item in row[stage]) == row['score'][stage]
    assert row['restored_logits_identical'] is True
    print(name, row['score'])
PYCODE
```

These checks reconcile stored fields. They do not repeat GPU execution or prove that the stored answers were scored correctly. No live harmful-content test is required.

## Model reproduction requirements

Use the model, tool and runtime revisions in the protocol. Required Python packages include PyTorch, Transformers, `huggingface_hub`, and the pinned OBLITERATUS checkout. The checkpoint must already be in the Hugging Face cache: the script uses `local_files_only=True`. A CUDA device must hold all model weights in `float16` plus inference memory.

Work from an external run directory containing copies of `check.py` and `polish-questions.json`; `check.py` writes `results.json` beside itself and would otherwise add a result to the code directory. Set `BIELIK_WORK_DIR` to an external scratch directory and `OBLITERATUS_GIT_REVISION` to the pinned tool commit. From that run directory, the entry point is `python check.py`.

The script requires local OBLITERATUS telemetry to be enabled and `log_benchmark` to succeed. Configure telemetry storage and transport in the pinned tool before running; this guide does not enable a remote destination. Without that setup the script can fail after restoring weights. The repository contains the historical telemetry file, but not a complete runtime lockfile or environment image.
