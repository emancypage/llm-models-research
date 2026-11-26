"""Judge A: label R, C or O from the judge model's next-token logits over the three letters.

usage: judge_a.py --report R --role stock|edited --spec S --model DIR --revision REV --codebook F --prompt-file F
                  [--prefill TEXT] [--no-prefill-field] --out OUT
"""
import argparse
import hashlib
import json
from pathlib import Path

LETTERS = ("R", "C", "O")
SEPARATOR = "----- prefill block -----\n"


def split_template(text):
    main, block = text.split(SEPARATOR)
    return main, block


def render(main, block, codebook, prompt, answer, prefill="", include_prefill=True):
    prefill_block = block.format(prefill=prefill) if include_prefill else ""
    return main.format(codebook=codebook, prompt=prompt, prefill_block=prefill_block, answer=answer)


def letter_ids(tokenizer):
    ids = []
    for letter in LETTERS:
        encoded = tokenizer.encode(letter, add_special_tokens=False)
        if len(encoded) != 1:
            raise SystemExit(f"{letter!r} is not one token in the judge tokenizer: {encoded}")
        ids.append(encoded[0])
    if len(set(ids)) != 3:
        raise SystemExit(f"R, C and O are not three different tokens: {ids}")
    return ids


def label_from_logits(logits, ids):
    import torch

    probs = torch.softmax(logits[ids].float(), dim=0).tolist()
    best = max(range(3), key=lambda k: probs[k])
    return LETTERS[best], [round(p, 6) for p in probs]


def score(rows, texts, next_logits, ids):
    """rows: dicts with 'invalid'; texts: judge input per row; next_logits(text) -> 1-D logits tensor."""
    labels, probs = [], []
    for row, text in zip(rows, texts):
        if row["invalid"]:
            labels.append(None)
            probs.append(None)
            continue
        label, p = label_from_logits(next_logits(text), ids)
        labels.append(label)
        probs.append(p)
    return labels, probs


def main():
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    from rows import harmful_prompts, load_rows

    ap = argparse.ArgumentParser()
    for name in ("--spec", "--model", "--revision", "--codebook", "--prompt-file"):
        ap.add_argument(name, required=True)
    ap.add_argument("--report")
    ap.add_argument("--role")
    ap.add_argument("--out")
    ap.add_argument("--prefill", default="")
    ap.add_argument("--no-prefill-field", action="store_true")
    ap.add_argument("--jobs", help="JSON list of {report, role, prefill, no_prefill_field, out}; loads the model once")
    ap.add_argument("--limit", type=int, help="score only the first N rows (load test)")
    args = ap.parse_args()
    jobs = json.loads(Path(args.jobs).read_text()) if args.jobs else [
        {"report": args.report, "role": args.role, "prefill": args.prefill,
         "no_prefill_field": args.no_prefill_field, "out": args.out}]
    prompt_raw = Path(args.prompt_file).read_bytes()
    codebook_raw = Path(args.codebook).read_bytes()
    main_t, block_t = split_template(prompt_raw.decode())
    prompts = harmful_prompts(args.spec)
    tokenizer = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    ids = letter_ids(tokenizer)
    model = AutoModelForCausalLM.from_pretrained(args.model, dtype=torch.bfloat16, local_files_only=True,
                                                 device_map="cuda").eval()

    def next_logits(text):
        chat = tokenizer.apply_chat_template([{"role": "user", "content": text}], add_generation_prompt=True,
                                             tokenize=False, enable_thinking=False)
        input_ids = tokenizer(chat, return_tensors="pt", add_special_tokens=False).input_ids.to("cuda")
        with torch.inference_mode():
            return model(input_ids).logits[0, -1]

    for job in jobs:
        rows = load_rows(job["report"], job["role"], prompts)
        if args.limit:
            rows = rows[:args.limit]
        texts = [render(main_t, block_t, codebook_raw.decode(), r["prompt"], r["completion"], job.get("prefill", ""),
                        not job.get("no_prefill_field", False)) for r in rows]
        labels, probs = score(rows, texts, next_logits, ids)
        out = {"report": job["report"], "role": job["role"], "prefill": job.get("prefill", ""),
               "prefill_field": not job.get("no_prefill_field", False), "label_a": labels, "probs_a": probs,
               "letters": list(LETTERS), "model_a_revision": args.revision,
               "prompt_sha256": hashlib.sha256(prompt_raw).hexdigest(),
               "codebook_sha256": hashlib.sha256(codebook_raw).hexdigest()}
        Path(job["out"]).write_text(json.dumps(out) + "\n")
        print(json.dumps({"out": job["out"], "rows": len(labels), "invalid": labels.count(None),
                          **{k: labels.count(k) for k in LETTERS}}), flush=True)


if __name__ == "__main__":
    main()
