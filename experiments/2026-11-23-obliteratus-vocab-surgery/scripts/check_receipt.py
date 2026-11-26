"""Scope check of a vocabulary-row edit: only receipt rows may differ, all other tensors bit-identical.

usage: check_receipt.py <S-dir> <V-dir> (--expect-input N --expect-output M | --expect-shared K) [--out OUT.json]
Exit 1 when anything outside the receipt rows differs, or the counts differ from the expected ones.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import torch
from safetensors import safe_open
from transformers import AutoTokenizer

TOKENIZER_FILES = ("tokenizer.json", "tokenizer_config.json", "special_tokens_map.json", "vocab.json", "merges.txt",
                   "chat_template.jinja", "tokenizer.model", "added_tokens.json")


def tensors(directory):
    handles = {}
    for path in sorted(Path(directory).glob("*.safetensors")):
        handle = safe_open(str(path), framework="pt")
        for name in handle.keys():
            handles[name] = handle
    return handles


def differing_rows(a, b):
    if a.shape != b.shape or a.dtype != b.dtype:
        raise SystemExit(f"vocabulary matrix shape or dtype differs: {a.shape} {a.dtype} vs {b.shape} {b.dtype}")
    return set((a.view(torch.int16) != b.view(torch.int16)).any(dim=1).nonzero().flatten().tolist()) \
        if a.dtype == torch.bfloat16 else set((a != b).any(dim=1).nonzero().flatten().tolist())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def template_digest(tokenizer):
    template = getattr(tokenizer, "chat_template", None)
    if isinstance(template, dict):
        template = template.get("default")
    return hashlib.sha256(template.encode()).hexdigest() if isinstance(template, str) else None


def config_differences(stock, edited):
    a = json.loads(Path(stock, "config.json").read_text())
    b = json.loads(Path(edited, "config.json").read_text())
    return sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))


def tokenizer_behaviour(tok_s, tok_e):
    """Same token IDs on the study inputs: held-out prompts (plain and chat-rendered) and the word probe."""
    texts = [item["text"] for item in json.loads(Path("/work/probe/items.json").read_text())]
    try:
        from obliteratus.verify_edit.heldout import load_heldout

        spec = json.loads(Path("/work/runs/spec.json").read_text())
        heldout = load_heldout(spec["heldout"], None)
        prompts = list(heldout["harmful"]) + list(heldout["harmless"])
    except ImportError:
        prompts = []
    plain = sum(tok_s(t).input_ids != tok_e(t).input_ids for t in texts + prompts)
    chat = sum(tok_s.apply_chat_template([{"role": "user", "content": t}], add_generation_prompt=True, tokenize=False)
               != tok_e.apply_chat_template([{"role": "user", "content": t}], add_generation_prompt=True, tokenize=False)
               or tok_s(tok_s.apply_chat_template([{"role": "user", "content": t}], add_generation_prompt=True,
                                                  tokenize=False), add_special_tokens=False).input_ids
               != tok_e(tok_e.apply_chat_template([{"role": "user", "content": t}], add_generation_prompt=True,
                                                  tokenize=False), add_special_tokens=False).input_ids
               for t in prompts)
    attrs = ("pad_token_id", "bos_token_id", "eos_token_id", "padding_side", "truncation_side", "model_max_length")
    attr_diff = {a: [getattr(tok_s, a, None), getattr(tok_e, a, None)] for a in attrs
                 if getattr(tok_s, a, None) != getattr(tok_e, a, None)}
    return {"texts_checked": len(texts) + len(prompts), "plain_mismatches": plain, "chat_prompts_checked": len(prompts),
            "chat_mismatches": chat, "attribute_differences": attr_diff,
            "identical": plain == 0 and chat == 0 and not attr_diff and len(prompts) == 400}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stock")
    ap.add_argument("edited")
    ap.add_argument("--expect-input", type=int)
    ap.add_argument("--expect-output", type=int)
    ap.add_argument("--expect-shared", type=int)
    ap.add_argument("--out")
    args = ap.parse_args()
    if (args.expect_shared is None) == (args.expect_input is None or args.expect_output is None):
        ap.error("give --expect-input and --expect-output, or --expect-shared")
    receipt_path = Path(args.edited, "vocab-surgery-receipt.json")
    receipt = json.loads(receipt_path.read_text()) if receipt_path.exists() else None
    ref, cand = tensors(args.stock), tensors(args.edited)
    problems = []
    if set(ref) != set(cand):
        problems.append({"only_stock": sorted(set(ref) - set(cand)), "only_edited": sorted(set(cand) - set(ref))})
    if receipt:
        names = receipt["tensors"]
    else:
        config = json.loads(Path(args.stock, "config.json").read_text())
        config = config.get("text_config", config)
        vocab = [n for n in ref if len(ref[n].get_slice(n).get_shape()) == 2
                 and ref[n].get_slice(n).get_shape()[0] == config["vocab_size"]]
        names = {"input": next((n for n in vocab if "embed" in n), None),
                 "output": next((n for n in vocab if "embed" not in n), None),
                 "tied": bool(config.get("tie_word_embeddings", False))}
    tied = bool(names["tied"])
    vocab_names = {n for n in (names["input"], names["output"]) if n in ref}
    allowed = {"input": set(), "output": set(), "shared_input": set()}
    for op in (receipt or {}).get("operations", []):
        for side in op["after"]:
            allowed[side].add(op["source_id"])
    rows = {}
    other_identical = True
    for name in sorted(set(ref) & set(cand)):
        a, b = ref[name].get_tensor(name), cand[name].get_tensor(name)
        if name in vocab_names:
            rows[name] = differing_rows(a, b)
        elif a.shape != b.shape or a.dtype != b.dtype or not torch.equal(a.view(torch.uint8) if a.dtype != torch.bool else a,
                                                                          b.view(torch.uint8) if b.dtype != torch.bool else b):
            other_identical = False
            problems.append({"tensor_differs": name})
    if tied:
        shared = rows.get(names["input"], set())
        result_rows = {"input_rows": None, "output_rows": None, "shared_rows": len(shared)}
        if not shared <= allowed["shared_input"]:
            problems.append({"rows_outside_receipt": sorted(shared - allowed["shared_input"])})
    else:
        inp, out = rows.get(names["input"], set()), rows.get(names["output"], set())
        result_rows = {"input_rows": len(inp), "output_rows": len(out), "shared_rows": None}
        if not inp <= allowed["input"]:
            problems.append({"input_rows_outside_receipt": sorted(inp - allowed["input"])})
        if not out <= allowed["output"]:
            problems.append({"output_rows_outside_receipt": sorted(out - allowed["output"])})
    files = {}
    for name in TOKENIZER_FILES:
        s, e = digest(Path(args.stock, name)), digest(Path(args.edited, name))
        if s or e:
            files[name] = {"stock": s, "edited": e, "same": s == e}
    tok_s = AutoTokenizer.from_pretrained(args.stock, local_files_only=True)
    tok_e = AutoTokenizer.from_pretrained(args.edited, local_files_only=True)
    semantic = (tok_s.get_vocab() == tok_e.get_vocab() and tok_s.all_special_tokens == tok_e.all_special_tokens
                and tok_s.pad_token == tok_e.pad_token and tok_s.bos_token == tok_e.bos_token
                and tok_s.eos_token == tok_e.eos_token)
    behaviour = tokenizer_behaviour(tok_s, tok_e)
    result = {
        "stock": args.stock, "edited": args.edited, **result_rows,
        "receipt_rows": {k: len(v) for k, v in allowed.items()},
        "receipt_skipped": (receipt or {}).get("skipped"),
        "receipt_summary": (receipt or {}).get("summary"),
        "weights_tied": tied,
        "other_tensors_identical": other_identical and not any("only_stock" in p for p in problems),
        "tokenizer_identical": all(f["same"] for f in files.values()),
        "tokenizer_files": files,
        "tokenizer_semantically_identical": semantic,
        "tokenizer_behaviour": behaviour,
        "chat_template_identical": template_digest(tok_s) == template_digest(tok_e),
        "chat_template_sha256": {"stock": template_digest(tok_s), "edited": template_digest(tok_e)},
        "config_differences": config_differences(args.stock, args.edited),
        "problems": problems,
    }
    expected = ({"shared_rows": args.expect_shared} if args.expect_shared is not None
                else {"input_rows": args.expect_input, "output_rows": args.expect_output})
    result["expected"] = expected
    result["counts_match"] = all(result[k] == v for k, v in expected.items())
    # Decision A (study owner, 23 Nov): the tool always re-saves tokenizer and config files, so byte identity is reported
    # but the pass rule requires identical tokenizer behaviour instead.
    ok = (result["counts_match"] and result["other_tensors_identical"] and behaviour["identical"]
          and result["tokenizer_semantically_identical"] and result["chat_template_identical"] and not problems)
    result["ok"] = ok
    text = json.dumps(result, indent=1)
    if args.out:
        Path(args.out).write_text(text + "\n")
    print(text)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
