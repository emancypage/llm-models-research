"""Greedy responses (chat template, 128 new tokens, batches of 16) to the extraction prompts, for token discovery.

usage: gen_responses.py <model-dir> <out-dir>   writes harmful.jsonl and harmless.jsonl with id, prompt, response
"""
import json
import sys
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

model_dir, out = sys.argv[1], Path(sys.argv[2])
pairs = json.loads(Path("/work/runs/extraction-pairs.json").read_text())
tok = AutoTokenizer.from_pretrained(model_dir, local_files_only=True)
tok.padding_side = "left"
if tok.pad_token is None:
    tok.pad_token = tok.eos_token
model = AutoModelForCausalLM.from_pretrained(model_dir, dtype=torch.bfloat16, local_files_only=True, device_map="cuda").eval()
out.mkdir(parents=True, exist_ok=True)
for kind in ("harmful", "harmless"):
    prompts = pairs[kind]
    rendered = [tok.apply_chat_template([{"role": "user", "content": p}], add_generation_prompt=True, tokenize=False)
                for p in prompts]
    responses = []
    for start in range(0, len(rendered), 16):
        enc = tok(rendered[start:start + 16], return_tensors="pt", padding=True, add_special_tokens=False).to("cuda")
        with torch.inference_mode():
            gen = model.generate(**enc, max_new_tokens=128, do_sample=False, pad_token_id=tok.pad_token_id)
        responses += tok.batch_decode(gen[:, enc.input_ids.shape[1]:], skip_special_tokens=True)
    with open(out / f"{kind}.jsonl", "w") as handle:
        for i, (p, r) in enumerate(zip(prompts, responses)):
            handle.write(json.dumps({"id": f"{kind}-{i}", "prompt": p, "response": r if r.strip() else "."}) + "\n")
    print(kind, len(responses), "empty", sum(not r.strip() for r in responses), flush=True)
