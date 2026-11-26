import os
import sys

import obliteratus.verify_edit.measure as measure
import obliteratus.verify_edit.runner as runner


def keep_flags(observation):
    return {key: value for key, value in observation.items() if key not in ("kl_capture", "kl")}


# verify-edit drops per-prompt refusal flags before writing; keep them for paired tests.
runner._strip = keep_flags

# KEEP_TEXTS=1 also stores the 64-token completions the detector judged (for the manual refusal check).
if os.environ.get("KEEP_TEXTS") == "1":
    flags = measure._flags
    measure._flags = lambda completions: {**flags(completions), "texts": list(completions)}
sys.argv[0] = "obliteratus"
from obliteratus.cli import main

main()
