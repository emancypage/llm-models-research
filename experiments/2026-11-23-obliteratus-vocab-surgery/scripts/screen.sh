#!/usr/bin/env bash
# usage: screen.sh <model-code> <arm> <model-path-in-container>
# PS screening set: every 10th item of each MMLU subject, full ARC-Challenge, first 400 GSM8K items.
set -u
source "$(dirname "$(readlink -f "$0")")/common.sh"
model_env "$1"; ARM=$2; MODEL=$3
[ "$MODEL" = stock ] && MODEL=$STOCK
OUT=eval/$CODE/screen/$ARM
[ -e "$M/$OUT" ] && { echo "$OUT exists"; exit 1; }
mkdir -p "$M/$OUT"
L=(--model hf --model_args "pretrained=$MODEL,dtype=bfloat16" --device cuda --log_samples)
run() { local t=$1; shift; local s; s=$(date +%s)
  dock "$CODE-screen-$ARM-$t" "${BASE[@]}" "${GPU[@]}" --entrypoint /work/venv/bin/lm_eval "$IMG" "${L[@]}" "$@" \
    --output_path "/work/$OUT/$t" > "$M/$OUT/$t.log" 2>&1
  local rc=$?; echo "$ARM $t rc=$rc seconds=$(( $(date +%s) - s ))"; [ $rc = 0 ]; }
run mmlu --batch_size 4 --tasks mmlu --num_fewshot 5 --samples "$(cat "$M/scripts/mmlu-every10.json")" || exit 1
run arc --batch_size 4 --tasks arc_challenge --num_fewshot 25 || exit 1
run gsm8k --batch_size 16 --tasks gsm8k --num_fewshot 5 --apply_chat_template --fewshot_as_multiturn --limit 400 || exit 1
