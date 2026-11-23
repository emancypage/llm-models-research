#!/usr/bin/env bash
# usage: probe.sh <model-code> <version-name> <model-path-in-container|stock>
set -u
source "$(dirname "$(readlink -f "$0")")/common.sh"
model_env "$1"; NAME=$2; MODEL=$3
[ "$MODEL" = stock ] && MODEL=$STOCK
mkdir -p "$M/runs/$CODE"
dock "$CODE-probe-$NAME" "${BASE[@]}" "${UP[@]}" "${GPU[@]}" --entrypoint "$PY" "$IMG" /work/scripts/probe.py \
  /work/probe/items.json "$MODEL" "/work/runs/$CODE/probe-$NAME.json"
