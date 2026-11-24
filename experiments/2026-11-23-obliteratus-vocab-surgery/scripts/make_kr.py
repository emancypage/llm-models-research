"""Random-control edit configs (plan KR, and the K2-shaped exploratory KR2), seed 42.

usage: make_kr.py <model-dir> <verify-report.json> <out-dir>
Candidates: single tokens that occur in the stock answers to harmless prompts and are not a source or a target
on the PR list; special tokens and pure-whitespace tokens are excluded. Writes kr.json, kr2.json and kr-tokens.json.
"""
import json
import random
import sys
from pathlib import Path

from transformers import AutoTokenizer

from obliteratus.strategies.vocab_surgery import VocabSurgeryConfig, VocabSurgeryStrategy, _default_operations

model_dir, report_path, out = sys.argv[1], sys.argv[2], Path(sys.argv[3])
tok = AutoTokenizer.from_pretrained(model_dir, local_files_only=True)
texts = json.loads(Path(report_path).read_text())["measurement"]["stock"]["harmless"]["texts"]
seen = set()
for text in texts:
    seen.update(tok.encode(text, add_special_tokens=False))
listed = set()
for op in _default_operations():
    for text in (op.source, op.target):
        if text is not None:
            listed.update(tok.encode(text, add_special_tokens=False))
special = set(tok.all_special_ids)
candidates = sorted(t for t in seen - listed - special if tok.decode([t]).strip())
rng = random.Random(42)


class Handle:
    tokenizer = tok


k2 = [op for op in _default_operations()
      if len(tok.encode(op.source, add_special_tokens=False)) == 1]
assert len(k2) == 33, len(k2)
picked = rng.sample(candidates, 9 + 7 + 33 + sum(op.target is not None for op in k2))
src1, tgt1, src2, tgt2 = picked[:9], picked[9:16], picked[16:49], picked[49:]
kr = [{"source_id": s, "target_id": t, "output_scale": 0.1, "input_alpha": 0.9, "group": "kr"} for s, t in zip(src1, tgt1)]
kr += [{"source_id": s, "output_scale": 0.1, "input_alpha": 0.0, "group": "kr-output-only"} for s in src1[7:]]
tier = {"tier1": (0.1, 0.9), "tier2": (0.2, 0.7), "tier3": (0.5, 0.0), "tier4": (0.6, 0.0)}
kr2, targets = [], iter(tgt2)
for op, s in zip(k2, src2):
    scale, alpha = tier[op.group]
    entry = {"source_id": s, "output_scale": scale, "input_alpha": alpha, "group": f"kr2-{op.group}"}
    if op.target is not None:
        entry["target_id"] = next(targets)
    kr2.append(entry)
schema = "obliteratus.vocab-surgery-config/v1"
out.mkdir(parents=True, exist_ok=True)
for name, ops in (("kr", kr), ("kr2", kr2)):
    config = {"schema": schema, "include_defaults": False, "operations": ops}
    VocabSurgeryConfig.from_value(config)
    (out / f"{name}.json").write_text(json.dumps(config, indent=1) + "\n")
record = {"candidates": len(candidates), "seed": 42,
          "kr": {"sources": [[t, tok.decode([t])] for t in src1], "targets": [[t, tok.decode([t])] for t in tgt1]},
          "kr2": {"sources": [[t, tok.decode([t])] for t in src2], "targets": [[t, tok.decode([t])] for t in tgt2]}}
(out / "kr-tokens.json").write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n")
print(json.dumps({"candidates": len(candidates), "kr_ops": len(kr), "kr2_ops": len(kr2),
                  "kr2_input": sum(o["input_alpha"] > 0 for o in kr2)}))
