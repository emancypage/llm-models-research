#!/usr/bin/env bash
# usage: judge.sh <model-code> <version-name> <report.json relative to W> <role> [--prefill "<text>"] [--no-prefill-field]
# Writes runs/<code>/judge-<version>.json (A and B) or, with --no-prefill-field, runs/<code>/judge-<version>-noprefill.json (A only).
set -u
MEM=${MEM:-80g}
source "$(dirname "$(readlink -f "$0")")/common.sh"
model_env "$1"; NAME=$2; REPORT=/work/${3#/work/}; ROLE=$4; shift 4
PREFILL=""; NOFIELD=0
while [ $# -gt 0 ]; do case $1 in --prefill) PREFILL=$2; shift 2;; --no-prefill-field) NOFIELD=1; shift;; *) echo "bad arg $1"; exit 2;; esac; done
for j in a b; do [ -s "$M/models/judge-$j/REVISION" ] || { echo "missing models/judge-$j/REVISION"; exit 2; }; done
OUT=runs/$CODE/judge-$NAME; A=(); [ $NOFIELD = 1 ] && { OUT=$OUT-noprefill; A=(--no-prefill-field); }
run() { dock "$CODE-judge-$NAME-$1" "${BASE[@]}" "${UP[@]}" "${GPU[@]}" -e PYTHONPATH=/upstream:/work/scripts --entrypoint "$PY" "$IMG" "${@:2}"; }
run a /work/scripts/judge_a.py --report "$REPORT" --role "$ROLE" --spec /work/runs/spec.json --model /work/models/judge-a \
  --revision "$(cat "$M/models/judge-a/REVISION")" --codebook /work/judge/codebook.md --prompt-file /work/judge/prompt-a.txt \
  --prefill "$PREFILL" "${A[@]}" --out "/work/$OUT.a.json" || exit 1
[ $NOFIELD = 1 ] && { mv "$M/$OUT.a.json" "$M/$OUT.json"; exit 0; }
run b /work/scripts/judge_b.py --a-json "/work/$OUT.a.json" --spec /work/runs/spec.json --model /work/models/judge-b \
  --revision "$(cat "$M/models/judge-b/REVISION")" --out "/work/$OUT.json" || exit 1
rm -f "${M:?}/${OUT:?}.a.json"
