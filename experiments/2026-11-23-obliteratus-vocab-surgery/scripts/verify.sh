#!/usr/bin/env bash
# usage: verify.sh <model-code> <arm> <edited-path-in-container>; KEEP_TEXTS=1 keeps completions in the report
set -u
source "$(dirname "$(readlink -f "$0")")/common.sh"
model_env "$1"; ARM=$2; EDITED=$3
[ "$EDITED" = stock ] && EDITED=$STOCK
OUT=runs/$CODE/verify-$ARM
mkdir -p "$M/$OUT"; rm -f "$M/$OUT/report.json"
dock "$CODE-verify-$ARM" "${BASE[@]}" "${UP[@]}" "${GPU[@]}" -e "KEEP_TEXTS=${KEEP_TEXTS:-0}" --entrypoint "$PY" "$IMG" /work/scripts/verify_flags.py \
  verify-edit --stock "$STOCK" --edited "$EDITED" --spec /work/runs/spec.json --spec-sha256 "$(cat "$M/runs/spec.sha256")" \
  --extraction-prompts /work/runs/extraction-pairs.json --device cuda --dtype bfloat16 --batch-size 8 --output "/work/$OUT/report.json"
echo "verify-edit exit=$?"
python3 - "$M/$OUT/report.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))
for role in ("stock", "edited"):
    m = r["measurement"][role]
    for kind in ("harmful", "harmless"):
        f = m[kind]
        assert len(f["refused_flags"]) == f["total"] and sum(f["refused_flags"]) == f["refused"], (role, kind)
        print(role, kind, f"{f['refused']}/{f['valid']}", "invalid", f["invalid"])
print("verdict", r["verdict"], "coherence", r["measurement"]["edited"]["anchored_coherence"])
PY
