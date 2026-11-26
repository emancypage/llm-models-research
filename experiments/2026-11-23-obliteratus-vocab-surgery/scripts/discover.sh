#!/usr/bin/env bash
# usage: discover.sh <model-code> <round> <model-dir-in-container> [base-config-name]; 250 tokens per round
set -u
source "$(dirname "$(readlink -f "$0")")/common.sh"
model_env "$1"; R=$2; MODEL=$3; BASE_CFG=${4:-}
[ "$MODEL" = stock ] && MODEL=$STOCK
D=runs/$CODE/d500; mkdir -p "$M/$D"
extra=(); [ -n "$BASE_CFG" ] && extra=(--base-config "/work/configs/$BASE_CFG.json")
dock "$CODE-discover-r$R" "${BASE[@]}" "${UP[@]}" "${GPU[@]}" --entrypoint "$PY" "$IMG" -m obliteratus vocab-surgery discover "$MODEL" \
  --target "/work/$D/gen-r$R/harmful.jsonl" --control "/work/$D/gen-r$R/harmless.jsonl" \
  --output "/work/$D/discover-r$R.json" --config-output "/work/$D/config-r$R.raw.json" \
  --limit 250 --min-target-count 2 --template-output-scale 0.1 --dtype bfloat16 --local-files-only "${extra[@]}" || exit 1
python3 "$M/scripts/id_only.py" "$M/$D/config-r$R.raw.json" "$M/configs/d500-$CODE$( [ "$R" = 1 ] && echo -r1 ).json"
