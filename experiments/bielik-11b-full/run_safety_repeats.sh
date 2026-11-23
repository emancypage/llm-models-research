#!/usr/bin/env bash
set -euo pipefail
python3 "$(dirname "$0")/safety_repeats.py" "${1:?Pass the directory containing published repeat result JSON files}"
