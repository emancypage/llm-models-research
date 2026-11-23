"""Validate published refusal flags offline; no prompts or model outputs are loaded."""

import argparse
import json
from pathlib import Path

def validate(path):
    row = json.loads(path.read_text())
    flags, invalid = row["refusal_flags"], row["invalid_flags"]
    assert len(flags) == len(invalid) == row["questions"] == 320
    assert all(type(v) is bool for v in flags + invalid)
    valid = sum(not v for v in invalid)
    refused = sum(f and not bad for f, bad in zip(flags, invalid, strict=True))
    assert valid == row["valid_count"]
    assert sum(invalid) == row["invalid_count"]
    assert refused == row["refusals"]
    assert refused / valid == row["refusal_rate"]
    return row

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("files", type=Path, nargs="+")
    args = parser.parse_args()
    for path in args.files:
        validate(path)
    print(f"Validated {len(args.files)} result files")
