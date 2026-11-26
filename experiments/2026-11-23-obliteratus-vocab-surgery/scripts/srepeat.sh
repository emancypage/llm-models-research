#!/usr/bin/env bash
# usage: srepeat.sh <model-code>; second S run on the first 200 GSM8K items (noise floor)
set -u
source "$(dirname "$(readlink -f "$0")")/common.sh"
model_env "$1"
OUT=eval/$CODE/S-repeat
[ -e "$M/$OUT" ] && { echo "$OUT exists"; exit 1; }
mkdir -p "$M/$OUT"
dock "$CODE-srepeat" "${BASE[@]}" "${GPU[@]}" --entrypoint /work/venv/bin/lm_eval "$IMG" --model hf \
  --model_args "pretrained=$STOCK,dtype=bfloat16" --device cuda --batch_size 16 --log_samples --limit 200 \
  --tasks gsm8k --num_fewshot 5 --apply_chat_template --fewshot_as_multiturn --output_path "/work/$OUT/gsm8k"
