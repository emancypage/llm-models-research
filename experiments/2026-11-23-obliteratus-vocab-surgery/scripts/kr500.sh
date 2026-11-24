#!/usr/bin/env bash
# usage: kr500.sh <model-code>; builds configs/kr500-<code>.json from the S harmless answers of run A for K1
set -u
source "$(dirname "$(readlink -f "$0")")/common.sh"
model_env "$1"
docker run --rm --network none --user 1000:1000 -v "$M:/work" --env-file "$M/scripts/docker.env" "${UP[@]}" \
  -e PYTHONPATH=/upstream:/work/scripts --entrypoint "$PY" "$IMG" /work/scripts/make_kr500.py "$STOCK" \
  "/work/runs/$CODE/verify-V-k1/report.json" "/work/configs/d500-$CODE.json" "/work/configs/kr500-$CODE.json"
