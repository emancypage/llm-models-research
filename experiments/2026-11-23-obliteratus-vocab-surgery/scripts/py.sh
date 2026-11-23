#!/usr/bin/env bash
# usage: py.sh [extra docker args...] -- [python args]; stdin is passed to python
source "$(dirname "$(readlink -f "$0")")/common.sh"
extra=(); while [ $# -gt 0 ] && [ "$1" != "--" ]; do extra+=("$1"); shift; done; shift
exec docker run --rm -i --network none --user 1000:1000 -v "$M:/work" --env-file "$M/scripts/docker.env" \
  -e HF_HUB_OFFLINE=1 -e HF_DATASETS_OFFLINE=1 -e TRANSFORMERS_OFFLINE=1 \
  "${UP[@]}" "${extra[@]}" --entrypoint "$PY" "$IMG" "$@"
