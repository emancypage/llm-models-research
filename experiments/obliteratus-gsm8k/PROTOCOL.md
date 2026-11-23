# Checking how OBLITERATUS scores GSM8K

This protocol can be shared before measurements are available. The study tests whether the reported score matches recorded answers on ordinary arithmetic problems. It compares two fixed, published checkpoints.

| Component | Version |
| --- | --- |
| Evaluation code | [OBLITERATUS, commit 7678d841](https://github.com/elder-plinius/OBLITERATUS/blob/7678d84196fe6c348dfd01078bbfb50857463647/obliteratus/evaluation/lm_eval_integration.py) |
| Original model | [Qwen/Qwen3-8B, b968826d](https://huggingface.co/Qwen/Qwen3-8B/tree/b968826d9c46dd6066d109eabc6255188de91218) |
| Modified model | [BabarAzaa/Test3, 73f58f9b](https://huggingface.co/BabarAzaa/Test3/tree/73f58f9b84443c8b5abbb90f7b5e5fd16804ef69) |
| Questions | [GSM8K](https://huggingface.co/datasets/openai/gsm8k), main configuration, test split |

1. Run five questions per model as a technical pilot. Run the first 100 test questions per model for the main measurement. Report the pilot separately.
2. Use the same five-shot GSM8K task, prompts, batch size of one and BF16 inference for both models. Record the evaluation library version and a fingerprint of the actual questions, prompts and answer keys.
3. Report the fraction correct using both the strict and flexible answer extraction rules. Record the headline score returned by OBLITERATUS separately. Verify the aggregates against per-question scores and report the difference between checkpoints in percentage points.
4. Before drawing conclusions, manually check a small sample including disputed cases. The main measurement describes these 100 questions and these two published checkpoints.

The shareable deliverables are this protocol, an aggregate JSON result and a Markdown table. Per-question answers and operational logs stay in the private run directory.
