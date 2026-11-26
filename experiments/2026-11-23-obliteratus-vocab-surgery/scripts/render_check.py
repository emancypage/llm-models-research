"""Renders one harmless chat; exit 0 when it ends with the prefill (if given) and contains the date (if given).

usage: render_check.py <model-dir> [--prefill TEXT] [--date DATE]
"""
import argparse
import hashlib
import json
import sys

from transformers import AutoTokenizer

ap = argparse.ArgumentParser()
ap.add_argument("model")
ap.add_argument("--prefill")
ap.add_argument("--date")
args = ap.parse_args()
tokenizer = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
text = tokenizer.apply_chat_template([{"role": "user", "content": "What is the capital of France?"}],
                                     add_generation_prompt=True, tokenize=False)
checks = {}
if args.prefill is not None:
    checks["ends_with_prefill"] = text.endswith(args.prefill)
if args.date is not None:
    checks["contains_date"] = args.date in text
ok = all(checks.values())
print(json.dumps({"model": args.model, "rendered_sha256": hashlib.sha256(text.encode()).hexdigest(), **checks, "ok": ok}))
sys.exit(0 if ok else 1)
