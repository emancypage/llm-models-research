"""Full answers (up to 1024 new tokens) to the 200 held-out harmful prompts, with the verify-edit generation code.

usage: gen_full.py <model-dir> <out.json> [earlier-report.json role]
Output has the shape of a verify-edit report (role "edited"), so the judge scripts can read it. Prints counts only.
"""
import json
import sys
from pathlib import Path

from obliteratus.verify_edit.heldout import prompts_sha256
from obliteratus.verify_edit.measure import ModelRunner, _flags
from rows import harmful_prompts

LIMIT = 1024
model_dir, out = sys.argv[1], Path(sys.argv[2])
prompts = harmful_prompts("/work/runs/spec.json")
runner = ModelRunner(model_dir, revision=None, device="cuda", dtype="bfloat16")
eos = runner.model.generation_config.eos_token_id
eos = set(eos if isinstance(eos, list) else [eos])
lengths, original = [], runner.model.generate


def recording(**kwargs):
    output = original(**kwargs)
    for row in getattr(output, "sequences", output)[:, kwargs["input_ids"].shape[1]:].tolist():
        lengths.append(next((i for i, t in enumerate(row) if t in eos), -1))
    return output


runner.model.generate = recording
texts = runner.generate(prompts, max_new_tokens=LIMIT, max_input_tokens=512, batch_size=8)
assert len(texts) == len(lengths) == len(prompts)
flags = {**_flags(texts), "texts": texts, "finished": [n >= 0 for n in lengths], "new_tokens": [n if n >= 0 else LIMIT for n in lengths]}
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps({"datasets": {"heldout": {"harmful_sha256": prompts_sha256(prompts)}}, "limit": LIMIT,
                           "model": model_dir, "measurement": {"edited": {"harmful": flags}}}) + "\n")
summary = {"n": len(texts), "cut_at_limit": sum(not f for f in flags["finished"]), "invalid": flags["invalid"],
           "median_tokens": sorted(flags["new_tokens"])[len(texts) // 2]}
if len(sys.argv) > 4:
    old = json.loads(Path(sys.argv[3]).read_text())["measurement"][sys.argv[4]]["harmful"]["texts"]
    summary["begins_with_64_token_answer"] = sum(n.startswith(o.rstrip("�").rstrip()) for n, o in zip(texts, old))
print(json.dumps(summary))
