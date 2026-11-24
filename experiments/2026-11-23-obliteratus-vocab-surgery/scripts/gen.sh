#!/usr/bin/env bash
# usage: gen.sh <model-code> <round> <model-dir-in-container|stock>; responses for token discovery
set -u
source "$(dirname "$(readlink -f "$0")")/common.sh"
model_env "$1"; R=$2; MODEL=$3
[ "$MODEL" = stock ] && MODEL=$STOCK
mkdir -p "$M/runs/$CODE/d500"
dock "$CODE-gen-r$R" "${BASE[@]}" "${UP[@]}" "${GPU[@]}" --entrypoint "$PY" "$IMG" /work/scripts/gen_responses.py "$MODEL" "/work/runs/$CODE/d500/gen-r$R"
