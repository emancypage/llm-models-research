"""Paired screening comparison (MMLU every 10th, ARC, first 400 GSM8K) of two arms: usage screen_compare.py <code> <armA> <armB> <out.json>"""
import glob
import json
import os
import sys

import numpy as np

code, arm_a, arm_b, out = sys.argv[1:5]
KEYS = {"mmlu": "acc", "arc": "acc_norm", "gsm8k": "exact_match"}


def vec(arm, task):
    d = {}
    for f in glob.glob(f"/work/eval/{code}/screen/{arm}/{task}/**/samples_*.jsonl", recursive=True):
        sub = os.path.basename(f).split("samples_", 1)[1].rsplit("_", 1)[0]
        for line in open(f):
            r = json.loads(line)
            if task == "gsm8k" and r.get("filter") != "flexible-extract":
                continue
            d[f"{sub}:{r['doc_id']}"] = float(r[KEYS[task]])
    return d


rng = np.random.default_rng(42)
res, draws = {}, []
for task in KEYS:
    a, b = vec(arm_a, task), vec(arm_b, task)
    assert a.keys() == b.keys(), (task, len(a), len(b))
    ks = sorted(a)
    x, y = np.array([a[k] for k in ks]), np.array([b[k] for k in ks])
    d = y - x
    dr = np.array([d[rng.integers(0, len(d), len(d))].mean() for _ in range(10000)])
    draws.append(dr)
    res[task] = {"n": len(d), "a": float(x.mean()), "b": float(y.mean()), "diff": float(d.mean()),
                 "ci95": [float(np.percentile(dr, 2.5)), float(np.percentile(dr, 97.5))]}
m = np.mean(draws, axis=0)
res["mean3"] = {"diff": float(np.mean([res[t]["diff"] for t in KEYS])),
                "ci95": [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]}
json.dump(res, open(out, "w"), indent=1)
print(code, json.dumps({k: {"diff_pp": round(v["diff"] * 100, 2), "ci_pp": [round(c * 100, 2) for c in v["ci95"]],
                            **({"S": round(v["a"], 4), "V": round(v["b"], 4)} if "a" in v else {})} for k, v in res.items()}))
