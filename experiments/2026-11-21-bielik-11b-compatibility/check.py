import hashlib
import json
import math
import os
from pathlib import Path
import time

import torch
import transformers
from huggingface_hub import snapshot_download
from obliteratus import telemetry
from obliteratus.abliterate import AbliterationPipeline
from obliteratus.strategies.ffn_ablation import FFNAblationStrategy
from obliteratus.strategies.utils import get_ffn_module, get_layer_modules


MODEL = "speakleash/Bielik-11B-v2.3-Instruct"
REV = "73f5f7fb9a79a4409d02740155a3868c1ff0d2bc"
HERE = Path(__file__).resolve().parent
QUESTIONS = HERE / "polish-questions.json"


def accepted(answer, reference):
    if isinstance(reference, dict):
        try:
            return json.loads(answer) == reference
        except ValueError:
            return False
    return answer.strip().strip('„”"').removesuffix(".").strip().casefold() == reference.casefold()


@torch.inference_mode()
def main():
    started = time.monotonic()
    cases = json.loads(QUESTIONS.read_text())
    snapshot = snapshot_download(MODEL, revision=REV, local_files_only=True)
    pipeline = AbliterationPipeline(model_name=snapshot, output_dir=str(Path(os.environ.get("BIELIK_WORK_DIR", "work")) / "technical-check"),
                                   device="cuda", dtype="float16", trust_remote_code=False,
                                   snapshot_enabled=False)
    pipeline._summon()
    h = pipeline.handle
    h.model.eval()
    summary = h.summary()
    del summary["model_name"]
    devices = {str(p.device) for p in h.model.parameters()}
    if not all(device.startswith("cuda") for device in devices):
        raise RuntimeError(f"Expected GPU-resident weights, got {devices}")
    print("Model ready:", summary, devices, flush=True)
    prompts = []
    for case in cases:
        messages = [{"role": "system", "content": "Odpowiadaj po polsku i przestrzegaj wskazanego formatu odpowiedzi."},
                    {"role": "user", "content": case["pytanie"]}]
        prompt = h.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        prompts.append(h.tokenizer(prompt, add_special_tokens=False, return_tensors="pt").to("cuda"))

    def probe():
        logits = h.model(**prompts[0], use_cache=False).logits[0, -1].float().cpu()
        if not torch.isfinite(logits).all():
            raise RuntimeError("Non-finite logits")
        return logits

    def answers(stage):
        rows = []
        for case, prompt in zip(cases, prompts, strict=True):
            output = h.model.generate(**prompt, do_sample=False, max_new_tokens=40,
                                      pad_token_id=h.tokenizer.eos_token_id)
            new_ids = output[0, prompt.input_ids.shape[-1]:]
            answer = h.tokenizer.decode(new_ids, skip_special_tokens=True).strip()
            rows.append({"id": case["id"], "odpowiedz": answer,
                         "zgodna_ze_wzorcem": accepted(answer, case["wzorzec"]),
                         "wygenerowane_tokeny": len(new_ids)})
        print(stage, sum(r["zgodna_ze_wzorcem"] for r in rows), "/", len(rows), flush=True)
        return rows

    strategy = FFNAblationStrategy()
    specs = strategy.enumerate(h)
    if len(specs) != h.num_layers or not specs:
        raise RuntimeError("Layer enumeration failed")
    index = len(specs) // 2
    ffn = get_ffn_module(get_layer_modules(h)[index], h.architecture)
    original_params = {k: p.detach().cpu().clone() for k, p in ffn.named_parameters()}
    if not original_params or not any(torch.count_nonzero(v).item() for v in original_params.values()):
        raise RuntimeError("No nonzero weights in selected module")
    original_logits = probe()
    baseline = answers("before")
    try:
        strategy.apply(h, specs[index])
        if any(torch.count_nonzero(p).item() for p in ffn.parameters()):
            raise RuntimeError("OBLITERATUS did not zero the selected module")
        edited_logits = probe()
        delta = (original_logits - edited_logits).abs().max().item()
        if not math.isfinite(delta) or delta <= 0:
            raise RuntimeError("No measurable change in the control forward pass")
        modified = answers("after")
    finally:
        for k, param in ffn.named_parameters():
            param.copy_(original_params[k])
    restored = probe()
    if not torch.equal(original_logits, restored):
        raise RuntimeError("Control logits did not return exactly to baseline")
    quality = {"before": sum(r["zgodna_ze_wzorcem"] for r in baseline),
               "after": sum(r["zgodna_ze_wzorcem"] for r in modified)}
    tool_revision = os.environ["OBLITERATUS_GIT_REVISION"]
    if not telemetry.is_enabled() or not telemetry.log_benchmark(telemetry.BenchmarkRecord(
        model_id=MODEL, method="ffn_ablation_single_layer_compatibility", compute_dtype="float16",
        model_family=summary["architecture"], model_size_b=summary["total_params"] / 1e9,
        dataset="pl-compat-v1", n_prompts=len(cases), time_seconds=time.monotonic() - started,
        extra={"revision": REV, "obliteratus_revision": tool_revision, "layer_index": index, "exact_answers": quality,
               "max_abs_logit_change": delta, "restored_logits_identical": True},
    )):
        raise RuntimeError("Local telemetry record was not written")
    result = {"model": MODEL, "revision": REV, "obliteratus_revision": tool_revision,
              "torch": str(torch.__version__),
              "transformers": transformers.__version__, "cuda": torch.version.cuda,
              "architecture": summary, "devices": sorted(devices),
              "dtype": str(next(h.model.parameters()).dtype), "questions_sha256": hashlib.sha256(QUESTIONS.read_bytes()).hexdigest(),
              "stage": "pristine summon + structural FFN ablation + restore",
              "layer_index": index, "enumerated_layers": len(specs), "score": quality,
              "max_abs_logit_change": delta, "restored_logits_identical": True,

              "wall_seconds": time.monotonic()-started, "before": baseline, "after": modified}
    (HERE / "results.json").write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
    print("PASS", flush=True)


if __name__ == "__main__":
    main()
