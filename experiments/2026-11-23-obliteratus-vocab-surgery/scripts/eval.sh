#!/usr/bin/env bash
# usage: eval.sh <model-code> <arm> <model-path-in-container> [peft-adapter-path]; env TASKS, GSM8K_ARGS (see eval_arm.sh)
set -u
source "$(dirname "$(readlink -f "$0")")/common.sh"
model_env "$1"; ARM=$2; MODEL=$3; ADAPTER=${4:-}
[ "$MODEL" = stock ] && MODEL=$STOCK
[ -f "$M/${ADAPTER#/work/}" ] && ADAPTER=$(cat "$M/${ADAPTER#/work/}")
[ -e "$M/eval/$CODE/$ARM" ] && { echo "eval/$CODE/$ARM exists"; exit 1; }
mkdir -p "$M/eval/$CODE"
TASKS=${TASKS:-mmlu arc gsm8k ifeval}
extra=(-e "TASKS=$TASKS" -e "GSM8K_ARGS=${GSM8K_ARGS:-}"); [ -n "$ADAPTER" ] && extra+=(-e "EXTRA_MODEL_ARGS=,peft=$ADAPTER")
dock "$CODE-eval-$ARM" "${BASE[@]}" "${UP[@]}" "${GPU[@]}" "${extra[@]}" --entrypoint bash "$IMG" \
  /work/scripts/eval_arm.sh "$ARM" "$MODEL" "/work/eval/$CODE" | tee "$M/eval/$CODE/$ARM.status"
[ "$(grep -c -E "^$ARM (mmlu|arc|gsm8k|ifeval) rc=0 " "$M/eval/$CODE/$ARM.status")" -eq "$(wc -w <<< "$TASKS")" ]
