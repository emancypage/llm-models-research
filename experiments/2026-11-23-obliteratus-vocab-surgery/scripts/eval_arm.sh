#!/usr/bin/env bash
# usage: eval_arm.sh <arm-name> <model-dir> <out-root> [limit]; EXTRA_MODEL_ARGS adds ",key=value" model args;
# TASKS selects a subset of "mmlu arc gsm8k ifeval"; GSM8K_ARGS adds lm-eval arguments to the GSM8K run
set -u
ARM=$1; MODEL=$2; OUT=$3; LIMIT=${4:-}
LIM=""; [ -n "$LIMIT" ] && LIM="--limit $LIMIT"
L="/work/venv/bin/lm_eval --model hf --model_args pretrained=$MODEL,dtype=bfloat16${EXTRA_MODEL_ARGS:-} --device cuda --log_samples $LIM"
TASKS=${TASKS:-mmlu arc gsm8k ifeval}
want() { [[ " $TASKS " == *" $1 "* ]]; }
mkdir -p $OUT/$ARM
run() { local t=$1; shift; local s=$(date +%s); "$@" --output_path $OUT/$ARM/$t > $OUT/$ARM/$t.log 2>&1; local rc=$?; echo "$ARM $t rc=$rc seconds=$(( $(date +%s) - s ))"; }
want mmlu && run mmlu   $L --batch_size 4 --tasks mmlu --num_fewshot 5
want arc && run arc    $L --batch_size 4 --tasks arc_challenge --num_fewshot 25
want gsm8k && run gsm8k  $L --batch_size 16 --tasks gsm8k --num_fewshot 5 --apply_chat_template --fewshot_as_multiturn ${GSM8K_ARGS:-}
want ifeval && run ifeval $L --batch_size 16 --tasks ifeval --apply_chat_template
