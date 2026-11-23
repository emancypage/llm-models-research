"""Harmful-prompt rows of one verify-edit report role, with prompts fetched like verify-edit does."""
import json
from pathlib import Path


def harmful_prompts(spec_path):
    from obliteratus.verify_edit.heldout import load_heldout

    spec = json.loads(Path(spec_path).read_text())
    return load_heldout(spec["heldout"], None)["harmful"]


def load_rows(report_path, role, prompts):
    """Returns [{index, prompt, completion, refused, invalid}] in flag order; checks prompts against the report."""
    from obliteratus.verify_edit.heldout import prompts_sha256

    report = json.loads(Path(report_path).read_text())
    if report["datasets"]["heldout"]["harmful_sha256"] != prompts_sha256(prompts):
        raise SystemExit(f"{report_path}: harmful prompts differ from the spec")
    flags = report["measurement"][role]["harmful"]
    n = len(flags["refused_flags"])
    if len(prompts) != n or len(flags["invalid_flags"]) != n:
        raise SystemExit(f"{report_path}: {len(prompts)} prompts but {n} refused_flags")
    if len(flags.get("texts", [])) != n:
        raise SystemExit(f"{report_path}: report has no texts for role {role} (run with KEEP_TEXTS=1)")
    return [{"index": i, "prompt": prompts[i], "completion": flags["texts"][i],
             "refused": bool(flags["refused_flags"][i]), "invalid": bool(flags["invalid_flags"][i])}
            for i in range(n)]
