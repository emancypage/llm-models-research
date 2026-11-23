"""Polish Belebele zero-shot comprehension with deterministic A/B/C/D scoring."""

import argparse
import hashlib
import json
from pathlib import Path
import time

import torch
from huggingface_hub import hf_hub_download
from obliteratus.models.loader import load_model

DATA_REV = "7899cdfa4e1e0d733fd77c848e2c273cb1d32be2"
LETTERS = "ABCD"


def encode_items(tokenizer, rows):
    items = []
    labels = None
    for index, row in enumerate(rows):
        options = [f"{c}. {row[f'mc_answer{n}']}" for n, c in enumerate(LETTERS, 1)]
        text = "\n".join([row["flores_passage"], "", row["question"], *options,
                         "", "Wybierz poprawną odpowiedź. Podaj tylko literę A, B, C lub D."])
        rendered = tokenizer.apply_chat_template([{"role": "user", "content": text}],
                                                tokenize=False, add_generation_prompt=True)
        ids = tokenizer.encode(rendered, add_special_tokens=False)
        if labels is None:
            completed = [tokenizer.encode(rendered + c, add_special_tokens=False) for c in LETTERS]
            if not all(seq[:-1] == ids for seq in completed):
                raise ValueError("Answer labels are not single-token continuations of the chat template")
            labels = [seq[-1] for seq in completed]
            if len(set(labels)) != len(LETTERS):
                raise ValueError("Answer labels must have distinct token IDs")
        items.append((index, ids))
    return sorted(items, key=lambda item: len(item[1])), labels


@torch.inference_mode()
def run(model_path, output_path, batch_size, handle=None):
    started = time.monotonic()
    data = Path(hf_hub_download("facebook/belebele", "data/pol_Latn.jsonl", repo_type="dataset",
                                revision=DATA_REV, local_files_only=True))
    rows = [json.loads(line) for line in data.read_text().splitlines()]
    keys = [(r["link"], r["ds"], r["question_number"]) for r in rows]
    if (len(rows) != 900 or len(set(keys)) != 900 or any(
        r["dialect"] != "pol_Latn" or int(r["correct_answer_num"]) not in (1, 2, 3, 4) for r in rows
    )):
        raise ValueError("Unexpected Polish test set")
    print(f"Loading {model_path}. Verified {len(rows)} Polish examples.", flush=True)
    h = handle or load_model(str(model_path), device="cuda", dtype="float16", trust_remote_code=False, skip_snapshot=True)
    h.model.eval()
    if not all(p.device.type == "cuda" for p in h.model.parameters()):
        raise RuntimeError("Weights are not fully on the GPU")
    items, labels = encode_items(h.tokenizer, rows)
    predictions = [None] * len(rows)
    pad_id = h.tokenizer.eos_token_id
    print(f"Labels {labels}. Max input {len(items[-1][1])} tokens.", flush=True)
    for start in range(0, len(items), batch_size):
        batch = items[start:start + batch_size]
        width = len(batch[-1][1])
        # Right padding with an explicit gather gives the score at each true prompt end.
        tokens = torch.tensor([ids + [pad_id] * (width - len(ids)) for _, ids in batch], device="cuda")
        lengths = torch.tensor([len(ids) for _, ids in batch], device="cuda")
        mask = torch.arange(width, device="cuda")[None, :] < lengths[:, None]
        hidden = h.model.model(input_ids=tokens, attention_mask=mask, use_cache=False).last_hidden_state
        logits = h.model.lm_head(hidden[torch.arange(len(batch), device="cuda"), lengths - 1]).float()
        scores = logits[:, labels]
        if not torch.isfinite(scores).all():
            raise RuntimeError("Non-finite answer scores")
        for (idx, _), pred in zip(batch, scores.argmax(1).tolist()):
            predictions[idx] = pred + 1
        done = min(start + batch_size, len(items))
        if done % (10 * batch_size) == 0 or done == len(items):
            print(f"Scored {done}/{len(items)}", flush=True)
    correct = [pred == int(r["correct_answer_num"]) for pred, r in zip(predictions, rows, strict=True)]
    assert all(pred in (1, 2, 3, 4) for pred in predictions)
    result = {"dataset": "facebook/belebele", "split": "pol_Latn", "revision": DATA_REV,
              "file_sha256": hashlib.sha256(data.read_bytes()).hexdigest(), "questions": len(rows),
              "correct": sum(correct), "accuracy": sum(correct) / len(rows), "batch_size": batch_size,
              "protocol": "zero-shot chat; forced A/B/C/D next-token score; no answer text generation",
              "labels": labels, "predictions_in_dataset_order": predictions, "correct_in_dataset_order": correct,

              "duration_seconds": time.monotonic() - started}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp = output_path.with_suffix(".tmp")
    temp.write_text(json.dumps(result, allow_nan=False) + "\n")
    temp.replace(output_path)
    print(f"Completed: {sum(correct)}/{len(rows)}", flush=True)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("model_path", type=Path)
    parser.add_argument("output_path", type=Path)
    parser.add_argument("--batch-size", type=int, default=8)
    args = parser.parse_args()
    run(args.model_path, args.output_path, args.batch_size)
