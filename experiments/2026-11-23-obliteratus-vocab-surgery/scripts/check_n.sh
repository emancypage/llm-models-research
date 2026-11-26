#!/usr/bin/env bash
# usage: check_n.sh <model-code> <config>; scope check with the expected output-row count taken from the config
set -u
source "$(dirname "$(readlink -f "$0")")/common.sh"
model_env "$1"; CFG=$2
N=$(python3 -c "import json;print(len(json.load(open('$M/configs/$CFG.json'))['operations']))")
bash "$M/scripts/check_receipt.sh" "$STOCK" "/work/runs/$CODE/$CFG/V" --expect-input 0 --expect-output "$N" --out "/work/runs/$CODE/$CFG/check.json"
