"""Word probe: compares the logits of two exact tokens at the next position (plan task 0.2).

usage: probe.py <items.json> <model-dir> <out.json>
Text goes to the model without a chat template; tokenizer special tokens (BOS) are added as usual.
"""
import hashlib
import json
import sys
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

items_path, model_dir, out_path = sys.argv[1:4]
raw = Path(items_path).read_bytes()
items = json.loads(raw)
tokenizer = AutoTokenizer.from_pretrained(model_dir, local_files_only=True)


def single(token):
    ids = tokenizer.encode(token, add_special_tokens=False)
    if len(ids) != 1:
        raise SystemExit(f"{token!r} is not one token in {model_dir}: {ids}")
    return ids[0]


pairs = [(single(i["correct_token"]), single(i["other_token"])) for i in items]
model = AutoModelForCausalLM.from_pretrained(model_dir, dtype=torch.bfloat16, local_files_only=True).to("cuda").eval()
correct, margins = [], []
with torch.inference_mode():
    for item, (right, wrong) in zip(items, pairs):
        ids = tokenizer(item["text"], return_tensors="pt").input_ids.to("cuda")
        logits = model(ids).logits[0, -1].float()
        margin = float(logits[right] - logits[wrong])
        margins.append(round(margin, 4))
        correct.append(margin > 0)


def accuracy(part):
    flags = [c for c, i in zip(correct, items) if i["part"] == part]
    return sum(flags) / len(flags)


result = {"model_dir": model_dir, "items_sha256": hashlib.sha256(raw).hexdigest(), "n": len(items),
          "correct": correct, "margin": margins, "accuracy_A": accuracy("A"), "accuracy_B": accuracy("B")}
Path(out_path).parent.mkdir(parents=True, exist_ok=True)
Path(out_path).write_text(json.dumps(result) + "\n")
print(json.dumps({k: result[k] for k in ("items_sha256", "n", "accuracy_A", "accuracy_B")}))
