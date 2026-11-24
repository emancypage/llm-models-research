#!/usr/bin/env bash
# usage: judge_all.sh [a|b|test]; builds job lists, then runs judge A (MEM 80g) or judge B on all of them, model loaded once.
set -u
source "$(dirname "$(readlink -f "$0")")/common.sh"
WHAT=${1:-a}
for j in a b; do [ -s "$M/models/judge-$j/REVISION" ] || { echo "missing models/judge-$j/REVISION"; exit 2; }; done
cd "$M" && python3 scripts/judge_jobs.py judge/jobs || exit 1
A=(--spec /work/runs/spec.json --model /work/models/judge-a --revision "$(cat "$M/models/judge-a/REVISION")"
   --codebook /work/judge/codebook.md --prompt-file /work/judge/prompt-a.txt)
B=(--spec /work/runs/spec.json --model /work/models/judge-b --revision "$(cat "$M/models/judge-b/REVISION")" --tokenizer /work/judge/tok-b)
run() { local name=$1; MEM=$2; shift 2
  source "$M/scripts/common.sh"
  dock "judge-$name" "${BASE[@]}" "${UP[@]}" "${GPU[@]}" -e PYTHONPATH=/upstream:/work/scripts --entrypoint "$PY" "$IMG" "$@"; }
case $WHAT in
  test)
    python3 - "$M/judge/jobs" <<'PY'
import json, sys
d = sys.argv[1]
a = [j for j in json.load(open(f"{d}/jobs-a.json")) if j["out"].endswith("/runs/l8/judge-VP-k1.a.json")]
a[0]["out"] = "/work/judge/test/judge-VP-k1.a.json"
json.dump(a, open(f"{d}/test-a.json", "w"))
json.dump([{"a_json": a[0]["out"], "out": "/work/judge/test/judge-VP-k1.json"}], open(f"{d}/test-b.json", "w"))
PY
    mkdir -p "$M/judge/test"
    s=$(date +%s); run test-a 80g /work/scripts/judge_a.py "${A[@]}" --jobs /work/judge/jobs/test-a.json --limit 5 || exit 1
    echo "judge A test seconds=$(( $(date +%s) - s ))"
    s=$(date +%s); run test-b 40g /work/scripts/judge_b.py "${B[@]}" --jobs /work/judge/jobs/test-b.json || exit 1
    echo "judge B test seconds=$(( $(date +%s) - s ))" ;;
  testb)
    s=$(date +%s); run test-b 40g /work/scripts/judge_b.py "${B[@]}" --jobs /work/judge/jobs/test-b.json || exit 1
    echo "judge B test seconds=$(( $(date +%s) - s ))" ;;
  a) run all-a 80g /work/scripts/judge_a.py "${A[@]}" --jobs /work/judge/jobs/jobs-a.json ;;
  b) run all-b 40g /work/scripts/judge_b.py "${B[@]}" --jobs /work/judge/jobs/jobs-b.json ;;
esac
