#!/usr/bin/env bash
# usage: apply.sh <model-code> <config>; writes runs/<code>/<config>/V (the tool refuses an existing V)
set -u
source "$(dirname "$(readlink -f "$0")")/common.sh"
model_env "$1"; CFG=$2
[ -f "$M/configs/$CFG.json" ] || { echo "no configs/$CFG.json"; exit 2; }
mkdir -p "$M/runs/$CODE/$CFG"
s=$(date +%s)
dock "$CODE-apply-$CFG" "${BASE[@]}" "${UP[@]}" "${GPU[@]}" --entrypoint "$PY" "$IMG" -m obliteratus vocab-surgery apply "$STOCK" \
  --config "/work/configs/$CFG.json" --output-dir "/work/runs/$CODE/$CFG/V" --dtype bfloat16 --local-files-only
rc=$?
echo "apply $CODE $CFG rc=$rc seconds=$(( $(date +%s) - s ))" | tee -a "$M/runs/$CODE/$CFG/apply.status"
exit $rc
