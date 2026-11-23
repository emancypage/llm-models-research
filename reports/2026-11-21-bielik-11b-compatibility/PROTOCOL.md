# Bielik 11B compatibility protocol

Study ID: `2026-11-21-bielik-11b-compatibility`.

The procedure was reconstructed from the run recorded on 21 November 2026. [Report](results.md) · [Code and reproduction](../../experiments/2026-11-21-bielik-11b-compatibility/README.md)

## Question and conditions

Can OBLITERATUS enumerate Bielik's layers, zero one feed-forward module, produce a measurable change, and restore the original control logits exactly? This is a structural compatibility check. The eight Polish questions provide a small descriptive quality check; they do not establish general model quality or safety.

The model is `speakleash/Bielik-11B-v2.3-Instruct`, revision `73f5f7fb9a79a4409d02740155a3868c1ff0d2bc`. The final record pins OBLITERATUS to `7678d84196fe6c348dfd01078bbfb50857463647`, PyTorch to `2.13.0a0+9186a08b2c.nv26.07`, Transformers to `5.17.0`, and CUDA to `13.3`. Weights were on one CUDA device in `float16`. The first measurement does not record all tool versions; do not infer them from the later record. [Final record](data/results.json) · [First measurement](data/first-measurement.json)

## Procedure and scoring

The [script](../../experiments/2026-11-21-bielik-11b-compatibility/check.py) loads the cached pinned checkpoint with remote code disabled and puts it in evaluation mode. It renders the same eight questions with the model's chat template, a Polish system instruction, greedy decoding and a limit of 40 new tokens. [Original prompts and targets](../../experiments/2026-11-21-bielik-11b-compatibility/polish-questions.json)

The script records the first question's final-token logits, saves the selected module's parameters, and scores all eight answers. It enumerates 50 layers and selects index 25. It zeroes that module, requires every parameter to be zero, checks that the logits remain finite and change, and scores the same questions again. A `finally` block restores the saved parameters. Success requires exact equality between the restored and original control logits.

For text targets, scoring strips surrounding whitespace and selected quotation marks, removes a final period, and compares without letter case. For a JSON target, the answer must parse and equal the reference object. The denominator is eight in each condition. Polish prompts, scoring keys and answers are preserved unchanged. The question-file SHA-256 is `15fb4cdf76328a42c68612aba9ab8105e7bf027507688b15031e57b082c089f6`.

## Evidence and limits

Keep the two measurements separate. Both record 7/8 before and 6/8 after, a maximum absolute logit change of `1.404296875`, and exact restoration. The final record also links the measurement to the tool revision; [telemetry](data/telemetry.jsonl) is supporting evidence. These are recorded outcomes, not advance predictions. Exact restoration concerns one control forward pass, and the eight questions are a convenience sample. No concept direction or refusal intervention was tested here.
