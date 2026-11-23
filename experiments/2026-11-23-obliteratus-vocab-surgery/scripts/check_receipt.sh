#!/usr/bin/env bash
# usage: check_receipt.sh <S-dir-in-container> <V-dir-in-container> <check_receipt.py options...>
source "$(dirname "$(readlink -f "$0")")/common.sh"
docker run --rm --network none --user 1000:1000 -v "$M:/work" --env-file "$M/scripts/docker.env" -e HF_HUB_OFFLINE=1 \
  -e TRANSFORMERS_OFFLINE=1 "${UP[@]}" --entrypoint "$PY" "$IMG" /work/scripts/check_receipt.py "$@" 2> >(grep -vE "^W1123|register_constant" >&2)
