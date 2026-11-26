#!/usr/bin/env bash
# usage: full.sh <model-code> <version> <model-dir-in-container> <earlier report relative to W> <role>
set -u
source "$(dirname "$(readlink -f "$0")")/common.sh"
model_env "$1"; V1=$2; MODEL=$3
mkdir -p "$M/runs/$CODE/full"
dock "$CODE-full-$V1" "${BASE[@]}" "${UP[@]}" "${GPU[@]}" -e PYTHONPATH=/upstream:/work/scripts --entrypoint "$PY" "$IMG" \
  /work/scripts/gen_full.py "$MODEL" "/work/runs/$CODE/full/$V1.json" "/work/$4" "$5"
