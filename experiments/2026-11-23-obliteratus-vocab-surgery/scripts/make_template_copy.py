"""Model copy with a changed chat template; weights are hard links, every other file is a real copy.

usage: make_template_copy.py <source> <dest> [--prefill TEXT] [--fix-date DATE]
--prefill appends TEXT after the generation prompt; --fix-date replaces the strftime_now(...) call with DATE.
The template may live in chat_template.jinja, in tokenizer_config.json, or in both; all copies are changed.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
from pathlib import Path

STRFTIME = re.compile(r"strftime_now\([^)]*\)")


def change(template, prefill, date):
    if date is not None:
        template, n = STRFTIME.subn(json.dumps(date), template)
        if n == 0:
            raise SystemExit("template has no strftime_now(...) call")
    if prefill is not None:
        if "'" in prefill or "\\" in prefill:
            raise SystemExit("prefill must not contain quotes or backslashes")
        template += "{%- if add_generation_prompt %}{{- '" + prefill + "' }}{%- endif %}"
    return template


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", type=Path)
    ap.add_argument("dest", type=Path)
    ap.add_argument("--prefill")
    ap.add_argument("--fix-date")
    args = ap.parse_args()
    if args.prefill is None and args.fix_date is None:
        ap.error("give --prefill or --fix-date")
    if args.dest.exists():
        raise SystemExit(f"{args.dest} exists")
    jinja = args.source / "chat_template.jinja"
    config_path = args.source / "tokenizer_config.json"
    config = json.loads(config_path.read_text())
    in_config = isinstance(config.get("chat_template"), str)
    if not jinja.exists() and not in_config:
        raise SystemExit("no chat template (string) in chat_template.jinja or tokenizer_config.json")
    effective = jinja.read_text() if jinja.exists() else config["chat_template"]
    before = sha(effective)
    args.dest.mkdir(parents=True)
    for path in sorted(args.source.iterdir()):
        if path.is_dir():
            raise SystemExit(f"unexpected directory {path}")
        if path.name.endswith(".safetensors"):
            os.link(path.resolve(), args.dest / path.name)
        elif path.name == "chat_template.jinja":
            (args.dest / path.name).write_text(change(path.read_text(), args.prefill, args.fix_date))
        elif path.name == "tokenizer_config.json" and in_config:
            changed = dict(config, chat_template=change(config["chat_template"], args.prefill, args.fix_date))
            (args.dest / path.name).write_text(json.dumps(changed, indent=2, ensure_ascii=False) + "\n")
        else:
            shutil.copy2(path.resolve(), args.dest / path.name)
    after_text = (args.dest / "chat_template.jinja").read_text() if jinja.exists() else \
        json.loads((args.dest / "tokenizer_config.json").read_text())["chat_template"]
    record = {"source": str(args.source), "prefill": args.prefill, "fixed_date": args.fix_date,
              "template_files": [n for n, present in (("chat_template.jinja", jinja.exists()),
                                                      ("tokenizer_config.json", in_config)) if present],
              "template_sha256_before": before, "template_sha256_after": sha(after_text)}
    (args.dest / "template-change.json").write_text(json.dumps(record, indent=1) + "\n")
    print(json.dumps(record))


if __name__ == "__main__":
    main()
