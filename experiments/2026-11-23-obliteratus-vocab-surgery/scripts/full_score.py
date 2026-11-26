"""FULL follow-up: manual labels (rows without prefill) against both judges, and judge measures on full answers.

usage: full_score.py <out.json>   SP2 is excluded (protocol entry 2026-11-25). Prints numbers only.
"""
import csv
import json
import sys
from pathlib import Path

from analyze_vocab import kappa, mcnemar, wilson

W = Path("/work")
NAME = {"R": "odmowa", "C": "zgoda", "O": "inne"}
VERSIONS = ("S", "V-k1", "V-d500", "V-kr500")
key = json.loads((W / "review/key-full.json").read_text())
human = {r["row_id"]: r["label"] for r in csv.DictReader(open(W / "review/sheet-full.csv", newline="", encoding="utf-8")) if not r["prefill"]}
missing = [k for k, v in human.items() if not v]
out = {"rows": len(human), "missing": len(missing)}
assert not missing and len(human) == 36, (len(human), len(missing))
judge = {(c, v): json.loads((W / f"runs/{c}/judge-full-{v}.json").read_text()) for c in ("l8", "q7") for v in VERSIONS}
rows = [(key[k]["model"], key[k]["version"], h, judge[key[k]["model"], key[k]["version"]]["label_a"][key[k]["index"]],
         judge[key[k]["model"], key[k]["version"]]["refusal_b"][key[k]["index"]]) for k, h in human.items()]
out["human"] = {f"{c}:{v}": {l: sum(r[0] == c and r[1] == v and r[2] == l for r in rows) for l in NAME.values()} for c in ("l8", "q7") for v in ("S", "V-d500")}


def agreement(sel):
    k = sum((r[2] == "zgoda") == (r[3] == "C") for r in sel)
    return {"n": len(sel), "compliance_agree": k, "wilson95": wilson(k, len(sel)), "three_label_agree": sum(r[2] == NAME[r[3]] for r in sel),
            "judge_b_refusal_agree": sum((r[2] == "odmowa") == r[4] for r in sel),
            "table_human_x_judge_a": {h: {l: sum(r[2] == h and r[3] == l for r in sel) for l in NAME} for h in NAME.values()}}


out["agreement_all"] = agreement(rows)
out["kappa"] = kappa([(r[2], NAME[r[3]]) for r in rows], tuple(NAME.values()))
for label, sel in (("l8", [r for r in rows if r[0] == "l8"]), ("q7", [r for r in rows if r[0] == "q7"]),
                   ("S", [r for r in rows if r[1] == "S"]), ("V-d500", [r for r in rows if r[1] == "V-d500"])):
    out[f"agreement_{label}"] = agreement(sel)
out["judges"] = {}
for c in ("l8", "q7"):
    fails, refusals_b = {}, {}
    for v in VERSIONS:
        d = judge[c, v]; la, b = d["label_a"], d["refusal_b"]; inv = la.count(None)
        rep = json.loads((W / f"runs/{c}/full/{v}.json").read_text())["measurement"]["edited"]["harmful"]
        if len(la) != 200 or len(b) != 200 or any((a is None) != (rb is None) for a, rb in zip(la, b)):
            raise ValueError(f"{c}/{v}: missing or mismatched judge labels")
        fails[v] = [x != "C" for x in la]
        refusals_b[v] = [label is None or refused for label, refused in zip(la, b)]
        out["judges"][f"{c}:{v}"] = {"R": la.count("R"), "C": la.count("C"), "O": la.count("O"), "invalid": inv,
                                     "judge_fail": sum(fails[v]) / 200, "b_fail": sum(refusals_b[v]) / 200,
                                     "uncertain": sum(x is True for x in d["uncertain"]), "detector_fail": (rep["refused"] + rep["invalid"]) / 200,
                                     "cut_at_limit": sum(not f for f in rep["finished"]), "prompt_sha256": d["prompt_sha256"][:8], "codebook_sha256": d["codebook_sha256"][:8]}
    for v in VERSIONS[1:]:
        fewer, more, p = mcnemar(fails["S"], fails[v])
        fewer_b, more_b, p_b = mcnemar(refusals_b["S"], refusals_b[v])
        out["judges"][f"{c}:{v}-S"] = {"diff": out["judges"][f"{c}:{v}"]["judge_fail"] - out["judges"][f"{c}:S"]["judge_fail"], "fewer": fewer, "more": more, "p": p,
                                       "diff_b": out["judges"][f"{c}:{v}"]["b_fail"] - out["judges"][f"{c}:S"]["b_fail"],
                                       "fewer_b": fewer_b, "more_b": more_b, "p_b": p_b}
    short = {v: json.loads((W / f"runs/{c}/judge-{n}.json").read_text())["label_a"] for v, n in (("S", "S"), ("V-k1", "V-k1"), ("V-d500", f"V-d500-{c}"), ("V-kr500", f"V-kr500-{c}"))}
    for v in VERSIONS:
        t = {}
        for x, y in zip(short[v], judge[c, v]["label_a"]):
            t[f"{x}->{y}"] = t.get(f"{x}->{y}", 0) + 1
        out["judges"][f"{c}:{v}"]["short_to_full"] = t
Path(sys.argv[1]).write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps(out, indent=1))
