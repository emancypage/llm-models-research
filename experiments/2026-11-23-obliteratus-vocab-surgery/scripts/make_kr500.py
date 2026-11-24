"""Random control KR500: as many random tokens as the D500 list, output_scale 0.1, seed 42.

usage: make_kr500.py <model-dir> <verify-report.json> <d500-config.json> <out-config.json>
Candidates: single tokens in the S answers to harmless prompts, not discovered, not on the PR list, not special.
"""
import json
import random
import sys
from pathlib import Path

from transformers import AutoTokenizer

from obliteratus.strategies.vocab_surgery import _default_operations

model_dir, report, d500, out = sys.argv[1:5]
tok = AutoTokenizer.from_pretrained(model_dir, local_files_only=True)
texts = json.loads(Path(report).read_text())["measurement"]["stock"]["harmless"]["texts"]
seen = set()
for t in texts:
    seen.update(tok.encode(t, add_special_tokens=False))
discovered = {op["source_id"] for op in json.loads(Path(d500).read_text())["operations"]}
listed = set()
for op in _default_operations():
    for s in (op.source, op.target):
        if s is not None:
            listed.update(tok.encode(s, add_special_tokens=False))
cand = sorted(t for t in seen - discovered - listed - set(tok.all_special_ids) if tok.decode([t]).strip())
n = len(discovered)
picked = random.Random(42).sample(cand, n)
config = {"schema": "obliteratus.vocab-surgery-config/v1", "include_defaults": False,
          "operations": [{"source_id": t, "output_scale": 0.1, "input_alpha": 0.0, "group": "kr500",
                          "label": json.dumps(tok.decode([t]))} for t in picked]}
Path(out).write_text(json.dumps(config, indent=1) + "\n")
print(json.dumps({"candidates": len(cand), "picked": n}))
