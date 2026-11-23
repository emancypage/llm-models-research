# Reproducing the Bielik tense study

Study ID: `2026-11-21-bielik-11b-polish-tense`.

[Protocol](../../reports/2026-11-21-bielik-11b-polish-tense/PROTOCOL.md) · [Report](../../reports/2026-11-21-bielik-11b-polish-tense/results.md) · [Initial failure](../../reports/2026-11-21-bielik-11b-polish-tense/issues.md)

`tense_study.py` defines source selection, the initial isolated-form design and the shared pipeline. `paired_tense.py` builds the revised balanced design. `belebele.py` scores reading comprehension. `compose.yaml` provides a container entry point; it requires a user-supplied image and external data directory. The `safety_*` scripts and `run_safety_repeats.sh` document a separate historical follow-up; this guide gives no live commands for that follow-up.

## Offline evidence check

Run from the repository root with Python 3. This checks saved counts without loading weights or contacting a service. No live harmful-content test is required.

```sh
python - <<'PYCODE'
import json
from pathlib import Path
root = Path('reports/2026-11-21-bielik-11b-polish-tense/data')
for name in ('belebele-before.json', 'variant-2/belebele-after.json'):
    row = json.loads((root / name).read_text())
    assert row['questions'] == 900
    assert len(row['predictions_in_dataset_order']) == 900
    assert len(row['correct_in_dataset_order']) == 900
    assert sum(row['correct_in_dataset_order']) == row['correct']
    print(name, row['correct'], '/', row['questions'])
row = json.loads((root / 'variant-2/heldout-tense.json').read_text())
for stage in ('before', 'after'):
    part = row[stage]
    assert len(part['trials']) == part['n'] == 128
    assert sum(t['predicted'] == t['expected'] for t in part['trials']) == part['correct']
    print(stage, part['correct'], '/', part['n'])
assert row['before']['trials'] == row['after']['trials']
PYCODE
```

This does not independently establish benchmark ground truth or repeat checkpoint verification.

## Reconstructing the benign inputs

Use Python 3 with PyTorch, Transformers, `huggingface_hub`, and OBLITERATUS at the protocol's pinned revision. Set `BIELIK_WORK_DIR` to an absolute external scratch directory. Place a Git checkout of UD Polish-LFG at `$BIELIK_WORK_DIR/ud-lfg`, checked out at the pinned commit. The `.conllu` training and test files must be present. From this experiment directory:

```sh
python tense_study.py --check-data
python paired_tense.py --check-data
```

These commands build the neutral grammar inputs and write manifests under `tense-v1/` and `tense-v2/` in the scratch directory. The revised command also writes `fit.jsonl` and `holdout.jsonl`; compare their hashes with the saved revised manifest. Imports require the model libraries even though this mode does not load weights. Do not use an existing results directory for a new reconstruction.

## Reading-comprehension evaluation

For GPU evaluation, prepare the pinned model snapshot and cache the pinned `facebook/belebele` file `data/pol_Latn.jsonl` beforehand. The benchmark uses offline cache lookup. All weights must fit on CUDA in `float16`, with extra inference memory. From this experiment directory, set `MODEL_SNAPSHOT` to the pinned checkpoint directory and run:

```sh
python belebele.py "$MODEL_SNAPSHOT" "$BIELIK_WORK_DIR/belebele/before.json" --batch-size 8
```

A full revised intervention also needs that baseline at the exact path shown and the model at `$BIELIK_WORK_DIR/hf/hub/models--speakleash--Bielik-11B-v2.3-Instruct/snapshots/73f5f7fb9a79a4409d02740155a3868c1ff0d2bc`. `paired_tense.py` is its entry point. Its final telemetry call must succeed; the supplied Compose configuration disables telemetry, so it is suitable for `--check-data` but does not provide a complete successful full-run setup. Configure local telemetry separately without enabling remote publication. The script writes a local contribution and an edited checkpoint under the external scratch directory.

The repository does not supply the image, model weights, corpus checkout, full dependency lock or a standalone checkpoint-verification command. The saved verification record documents the historical reload.
