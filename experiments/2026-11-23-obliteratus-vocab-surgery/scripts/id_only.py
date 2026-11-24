"""Rewrites a discovered config with token IDs only (token strings may not round-trip, OBLITERATUS #600)."""
import json
import sys

config = json.load(open(sys.argv[1]))
for op in config["operations"]:
    if op.get("source_id") is not None:
        op["label"] = f"{op.get('label') or 'discovered'} {json.dumps(op.pop('source', None))}"
        op.pop("target", None)
        op.pop("target_id", None)
json.dump(config, open(sys.argv[2], "w"), indent=1)
print(sys.argv[2], "operations", len(config["operations"]),
      "ids unique", len({op["source_id"] for op in config["operations"]}) == len(config["operations"]))
