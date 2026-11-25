"""Capability, format and refusal analysis for several models and repair arms.

usage: analyze_multi.py <config.json> <output-dir>

The config maps each model code to its tokenizer, the evaluation directory of each arm,
an optional S-repeat directory, the verify-edit report of each arm and optional pairs.
"""
import glob
import json
import os
import re
import sys

import numpy as np
from scipy.stats import binomtest

TASKS = ("mmlu", "arc", "gsm8k", "ifeval")
MAX_GEN = {"gsm8k": 256, "ifeval": 1280}
DRAWS, SEED, MARGIN = 10_000, 42, 0.02
SEED_ARMS = ("R0", "R0-s43", "R0-s44")
SEED_MEAN = "R0x3"
ANSWER_END = re.compile(r"####\s*\$?-?[\d,\.]+\s*\$?\s*\Z")
# Models for which each endpoint is confirmatory (protocol, "Shortened plan", 23 November); others are exploratory.
CONFIRMATORY = {"1": ("q1", "q3"), "2": ("q1",), "3": ("q1", "q3"), "4": ("q1",), "5": ("q3",), "6": ("q3",)}
PAIRS = (("P", "S"), ("R0", "P"), ("R0", "S"), ("R0-s43", "P"), ("R0-s44", "P"), (SEED_MEAN, "P"),
         ("RK", "P"), ("RK", "R0"), ("RK", "S"), ("RB", "P"), ("RB", "R0"), ("RG", "P"), ("RG", "R0"),
         ("PS", "S"), ("RS", "PS"), ("RS", "S"), ("E", "S"), ("P", "E"), ("R0", "E"))


def samples(path, task):
    files = sorted(glob.glob(os.path.join(path, task, "**", "samples_*.jsonl"), recursive=True))
    if not files:
        raise SystemExit(f"missing samples in {path}/{task}")
    for name in files:
        subtask = os.path.basename(name).split("samples_", 1)[1].rsplit("_", 1)[0]
        with open(name, encoding="utf-8") as handle:
            for line in handle:
                yield subtask, json.loads(line)


def load_task(path, task):
    primary, secondary, texts, inst = {}, {}, {}, {}
    for subtask, row in samples(path, task):
        key = f"{subtask}:{row['doc_id']}"
        if task == "mmlu":
            primary[key] = float(row["acc"])
        elif task == "arc":
            primary[key] = float(row["acc_norm"])
        elif task == "gsm8k":
            target = primary if row["filter"] == "flexible-extract" else secondary
            target[key] = float(row["exact_match"])
            texts[key] = row["resps"][0][0]
        else:
            primary[key] = float(row["prompt_level_strict_acc"])
            levels = row["inst_level_strict_acc"]
            secondary[key] = sum(levels) / len(levels)
            inst[key] = (sum(levels), len(levels))
            texts[key] = row["resps"][0][0]
    return {"primary": primary, "secondary": secondary, "texts": texts, "inst": inst}


def paired(a, b):
    if a.keys() != b.keys():
        raise SystemExit("item sets differ between arms")
    keys = sorted(a)
    return np.array([a[k] for k in keys]), np.array([b[k] for k in keys])


def bootstrap_diffs(x, y, rng):
    # Resampling paired items is equivalent to a multinomial draw over the distinct differences.
    diff = y - x
    values, counts = np.unique(diff, return_counts=True)
    draws = rng.multinomial(len(diff), counts / counts.sum(), size=DRAWS)
    return draws @ values / len(diff)


def index_ci(x, y, rng):
    diff = y - x
    idx = rng.integers(0, len(diff), size=(DRAWS, len(diff)))
    means = diff[idx].mean(axis=1)
    lo, hi = np.percentile(means, [2.5, 97.5])
    return float(diff.mean()), [float(lo), float(hi)]


def ratio_ci(x, y, rng):
    if not np.array_equal(x[:, 1], y[:, 1]):
        raise SystemExit("instruction counts differ")
    diff, n = y[:, 0] - x[:, 0], x[:, 1]
    idx = rng.integers(0, len(diff), size=(DRAWS, len(diff)))
    means = diff[idx].sum(axis=1) / n[idx].sum(axis=1)
    lo, hi = np.percentile(means, [2.5, 97.5])
    return float(diff.sum() / n.sum()), [float(lo), float(hi)]


def mcnemar(x, y):
    only_a, only_b = int(((x == 1) & (y == 0)).sum()), int(((x == 0) & (y == 1)).sum())
    p = binomtest(min(only_a, only_b), only_a + only_b, 0.5).pvalue if only_a + only_b else 1.0
    return only_a, only_b, float(p)


def bootstrap_p(draws):
    return float(min(1.0, 2 * min(np.mean(draws <= 0), np.mean(draws >= 0))))


def verdict(lo, hi):
    if hi < 0:
        return "practically significant drop" if hi <= -MARGIN else "drop"
    if lo > -MARGIN:
        return "no drop"
    return "inconclusive"


def holm(pvalues):
    order = sorted(range(len(pvalues)), key=lambda i: pvalues[i])
    adjusted, running = [0.0] * len(pvalues), 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (len(pvalues) - rank) * pvalues[i]))
        adjusted[i] = running
    return adjusted


def token_counts(tokenizer, texts):
    return {k: len(tokenizer(t, add_special_tokens=False).input_ids) for k, t in texts.items()}


class Model:
    def __init__(self, code, spec):
        self.code, self.spec = code, spec
        from transformers import AutoTokenizer

        self.tokenizer = AutoTokenizer.from_pretrained(spec["tokenizer"])
        self.data = {arm: {task: load_task(path, task) for task in TASKS} for arm, path in spec["arms"].items()}
        for arm in self.data:
            for task in ("gsm8k", "ifeval"):
                self.data[arm][task]["tokens"] = token_counts(self.tokenizer, self.data[arm][task]["texts"])
        if all(arm in self.data for arm in SEED_ARMS):
            self.data[SEED_MEAN] = {task: {"primary": {
                key: float(np.mean([self.data[arm][task]["primary"][key] for arm in SEED_ARMS]))
                for key in self.data[SEED_ARMS[0]][task]["primary"]}} for task in TASKS}
        pairs = [tuple(p) for p in spec.get("pairs", PAIRS)]
        self.pairs = [(b, a) for b, a in pairs if a in self.data and b in self.data]

    def primary_draws(self, b, a, rng):
        return [bootstrap_diffs(*paired(self.data[a][t]["primary"], self.data[b][t]["primary"]), rng) for t in TASKS]

    def capability(self):
        report = {"arms": {}, "comparisons": {}, "settings": {"draws": DRAWS, "seed": SEED, "margin": MARGIN}}
        vectors = {}
        for arm, tasks in self.data.items():
            if arm == SEED_MEAN:
                continue
            report["arms"][arm] = {}
            for task in TASKS:
                d = tasks[task]
                entry = {"n": len(d["primary"]), "primary": float(np.mean(list(d["primary"].values())))}
                if d["secondary"]:
                    entry["secondary"] = float(np.mean(list(d["secondary"].values())))
                if d["texts"]:
                    entry["hit_max_gen_toks"] = sum(v >= MAX_GEN[task] - 1 for v in d["tokens"].values())
                report["arms"][arm][task] = entry
                vectors[f"{arm}/{task}"] = {k: d["primary"][k] for k in sorted(d["primary"])}
        for b, a in self.pairs:
            rng = np.random.default_rng(SEED)
            rows, task_draws, pvalues = {}, [], []
            for task in TASKS:
                x, y = paired(self.data[a][task]["primary"], self.data[b][task]["primary"])
                draws = bootstrap_diffs(x, y, rng)
                task_draws.append(draws)
                lo, hi = np.percentile(draws, [2.5, 97.5])
                row = {"diff": float((y - x).mean()), "ci95": [float(lo), float(hi)], "verdict": verdict(lo, hi)}
                if set(np.unique(np.concatenate([x, y]))) <= {0.0, 1.0}:
                    only_a, only_b, p = mcnemar(x, y)
                    row.update(only_baseline_correct=only_a, only_compared_correct=only_b)
                else:
                    p = None
                row["mcnemar_p"] = p
                pvalues.append(p)
                rows[task] = row
            if None not in pvalues:
                for task, adj in zip(TASKS, holm(pvalues)):
                    rows[task]["mcnemar_p_holm"] = adj
            mean_draws = np.mean(task_draws, axis=0)
            lo, hi = np.percentile(mean_draws, [2.5, 97.5])
            rows["mean_of_primary"] = {
                "diff": float(np.mean([rows[t]["diff"] for t in TASKS])),
                "ci95": [float(lo), float(hi)], "verdict": verdict(lo, hi),
                "project_margin_holds": bool(lo > -MARGIN), "bootstrap_p": bootstrap_p(mean_draws),
            }
            report["comparisons"][f"{b}-{a}"] = rows
        if all(arm in self.data for arm in SEED_ARMS):
            means = {arm: report["arms"][arm] for arm in SEED_ARMS}
            per_seed = {arm: float(np.mean([means[arm][t]["primary"] for t in TASKS])) for arm in SEED_ARMS}
            report["seed_spread"] = {"mean_of_primary": per_seed,
                                     "range": max(per_seed.values()) - min(per_seed.values()),
                                     "sd": float(np.std(list(per_seed.values()), ddof=1))}
        repeat = self.spec.get("repeat")
        if repeat and "S" in self.data:
            base = {row["doc_id"]: (row["resps"][0][0], row["exact_match"])
                    for _, row in samples(self.spec["arms"]["S"], "gsm8k") if row["filter"] == "flexible-extract"}
            rep = {row["doc_id"]: (row["resps"][0][0], row["exact_match"])
                   for _, row in samples(repeat, "gsm8k") if row["filter"] == "flexible-extract"}
            report["noise_gsm8k_first200"] = {
                "items": len(rep),
                "different_text": sum(rep[k][0] != base[k][0] for k in rep),
                "different_score": sum(rep[k][1] != base[k][1] for k in rep),
            }
        return report, vectors

    def secondary(self):
        report = {"arms": {}, "comparisons": {}}
        real = [arm for arm in self.data if arm != SEED_MEAN]
        for arm in real:
            g, i = self.data[arm]["gsm8k"], self.data[arm]["ifeval"]
            report["arms"][arm] = {
                "gsm8k_strict_match": float(np.mean(list(g["secondary"].values()))),
                "ifeval_inst_level_strict": float(sum(c for c, _ in i["inst"].values())
                                                  / sum(n for _, n in i["inst"].values())),
                "gsm8k_tokens_median": float(np.median(list(g["tokens"].values()))),
                "gsm8k_at_limit": int(sum(v >= MAX_GEN["gsm8k"] - 1 for v in g["tokens"].values())),
                "ifeval_tokens_median": float(np.median(list(i["tokens"].values()))),
                "ifeval_at_limit": int(sum(v >= MAX_GEN["ifeval"] - 1 for v in i["tokens"].values())),
                "gsm8k_ends_with_answer_marker": sum(_ends_with_marker(t) for t in g["texts"].values()),
            }
        for b, a in self.pairs:
            if SEED_MEAN in (a, b):
                continue
            rng = np.random.default_rng(SEED)
            entry = {}
            x, y = paired(self.data[a]["gsm8k"]["secondary"], self.data[b]["gsm8k"]["secondary"])
            diff, interval = index_ci(x, y, rng)
            only_a, only_b, p = mcnemar(x, y)
            entry["gsm8k_strict_match"] = {"diff": diff, "ci95": interval, "only_baseline_correct": only_a,
                                           "only_compared_correct": only_b, "mcnemar_p": p}
            x, y = paired(self.data[a]["ifeval"]["inst"], self.data[b]["ifeval"]["inst"])
            diff, interval = ratio_ci(x, y, rng)
            entry["ifeval_inst_level_strict"] = {"diff": diff, "ci95": interval}
            x, y = paired(self.data[a]["gsm8k"]["tokens"], self.data[b]["gsm8k"]["tokens"])
            xl, yl = (x >= MAX_GEN["gsm8k"] - 1).astype(float), (y >= MAX_GEN["gsm8k"] - 1).astype(float)
            only_a, only_b, p = mcnemar(xl, yl)
            entry["gsm8k_at_limit"] = {"only_baseline": only_a, "only_compared": only_b, "mcnemar_p": p,
                                       "median_token_diff": float(np.median(y - x))}
            report["comparisons"][f"{b}-{a}"] = entry
        return report

    def refusals(self):
        flags = {}
        for arm, path in self.spec.get("verify", {}).items():
            with open(path) as handle:
                measurement = json.load(handle)["measurement"]
            flags[arm] = measurement["edited"]
            flags.setdefault("S", measurement["stock"])
        report = {"arms": {}, "comparisons": {}}
        for arm, m in flags.items():
            report["arms"][arm] = {kind: {"refused": m[kind]["refused"], "valid": m[kind]["valid"],
                                          "invalid": m[kind]["invalid"]} for kind in ("harmful", "harmless")}
            report["arms"][arm]["harmless_valid_rate"] = m["harmless"]["valid"] / m["harmless"]["total"]
            report["arms"][arm]["anchored_coherence"] = m.get("anchored_coherence")
        for b, a in self.pairs:
            if a not in flags or b not in flags:
                continue
            entry = {}
            for kind in ("harmful", "harmless"):
                x = np.array(flags[a][kind]["refused_flags"], dtype=float)
                y = np.array(flags[b][kind]["refused_flags"], dtype=float)
                only_a, only_b, p = mcnemar(x, y)
                entry[kind] = {"only_baseline_refused": only_a, "only_compared_refused": only_b, "mcnemar_p": p}
            report["comparisons"][f"{b}-{a}"] = entry
        return report


def _ends_with_marker(text):
    return ANSWER_END.search(text.strip()) is not None


def recovered_fraction(model, rng):
    """(RS - PS) / (S - PS) on the mean of primary metrics, resampling items jointly per task."""
    vectors = {}
    for task in TASKS:
        keys = sorted(model.data["S"][task]["primary"])
        vectors[task] = [np.array([model.data[arm][task]["primary"][k] for k in keys]) for arm in ("S", "PS", "RS")]
    damage = np.mean([v[0].mean() - v[1].mean() for v in vectors.values()])
    gain = np.mean([v[2].mean() - v[1].mean() for v in vectors.values()])
    if damage < MARGIN:
        return {"damage": float(damage), "computed": False, "reason": "S - PS below 2 pp"}
    ratios = []
    for _ in range(DRAWS // 500):
        d, g = 0.0, 0.0
        for s, ps, rs in vectors.values():
            idx = rng.integers(0, len(s), size=(500, len(s)))
            d = d + (s[idx].mean(axis=1) - ps[idx].mean(axis=1)) / len(TASKS)
            g = g + (rs[idx].mean(axis=1) - ps[idx].mean(axis=1)) / len(TASKS)
        ratios.append(g / d)
    lo, hi = np.percentile(np.concatenate(ratios), [2.5, 97.5])
    return {"damage": float(damage), "gain": float(gain), "fraction": float(gain / damage),
            "ci95": [float(lo), float(hi)], "computed": True}


def endpoints(models, capability, secondary, refusals):
    out = {}

    def per_model(name, b, a, value):
        rows = {}
        for code, m in models.items():
            if (b, a) in m.pairs:
                try:
                    rows[code] = value(code)
                except KeyError:
                    pass
        confirmatory = CONFIRMATORY[name.split("_", 1)[0]]
        for code, row in rows.items():
            row["confirmatory"] = code in confirmatory
        tested = [code for code in rows if code in confirmatory]
        for code, adj in zip(tested, holm([rows[c]["p"] for c in tested]) if tested else []):
            rows[code]["p_holm"] = adj
        out[name] = {"comparison": f"{b}-{a}", "confirmatory_models": list(confirmatory), "models": rows}
        return rows

    def mean_row(b, a):
        return lambda code: {**capability[code]["comparisons"][f"{b}-{a}"]["mean_of_primary"],
                             "p": capability[code]["comparisons"][f"{b}-{a}"]["mean_of_primary"]["bootstrap_p"]}

    rows = per_model("1_repair_vs_projection_mean", "R0", "P", mean_row("R0", "P"))
    rows = {code: row for code, row in rows.items() if row["confirmatory"]}
    if rows:
        draws = []
        for i, code in enumerate(rows):
            rng = np.random.default_rng([SEED, i])
            draws.append(np.mean(models[code].primary_draws("R0", "P", rng), axis=0))
        pooled = np.mean(draws, axis=0)
        lo, hi = np.percentile(pooled, [2.5, 97.5])
        diffs = [r["diff"] for r in rows.values()]
        out["1_repair_vs_projection_mean"]["pooled_equal_weight"] = {
            "diff": float(np.mean(diffs)), "ci95": [float(lo), float(hi)], "verdict": verdict(lo, hi), "bootstrap_p": bootstrap_p(pooled),
            "models": len(diffs), "positive": sum(d > 0 for d in diffs), "negative": sum(d < 0 for d in diffs)}
    per_model("2_refusal_data_refusals", "RK", "P",
              lambda code: {**refusals[code]["comparisons"]["RK-P"]["harmful"],
                            "p": refusals[code]["comparisons"]["RK-P"]["harmful"]["mcnemar_p"],
                            "capability_RK_minus_R0": capability[code]["comparisons"].get("RK-R0", {}).get("mean_of_primary"),
                            "capability_RK_minus_P": capability[code]["comparisons"]["RK-P"]["mean_of_primary"]})
    per_model("3_repair_vs_projection_strict_match", "R0", "P",
              lambda code: {**secondary[code]["comparisons"]["R0-P"]["gsm8k_strict_match"],
                            "p": secondary[code]["comparisons"]["R0-P"]["gsm8k_strict_match"]["mcnemar_p"]})
    rows = per_model("4_recovery_after_strong_projection", "RS", "PS", mean_row("RS", "PS"))
    for code in rows:
        rows[code]["recovered_fraction"] = recovered_fraction(models[code], np.random.default_rng(SEED))
    per_model("5_repair_vs_projection_refusals", "R0", "P",
              lambda code: {**refusals[code]["comparisons"]["R0-P"]["harmful"],
                            "p": refusals[code]["comparisons"]["R0-P"]["harmful"]["mcnemar_p"]})
    per_model("6_repair_vs_projection_ifeval", "R0", "P",
              lambda code: {key: capability[code]["comparisons"]["R0-P"]["ifeval"][key]
                            for key in ("diff", "ci95", "only_baseline_correct", "only_compared_correct")}
              | {"p": capability[code]["comparisons"]["R0-P"]["ifeval"]["mcnemar_p"]})
    return out


def main():
    config_path, out = sys.argv[1], sys.argv[2]
    with open(config_path) as handle:
        config = json.load(handle)
    models = {code: Model(code, spec) for code, spec in config["models"].items()}
    capability, secondary, refusals = {}, {}, {}
    for code, model in models.items():
        target = os.path.join(out, code)
        os.makedirs(target, exist_ok=True)
        capability[code], vectors = model.capability()
        secondary[code] = model.secondary()
        refusals[code] = model.refusals()
        for name, payload in (("capability-summary", capability[code]), ("per-item-correctness", vectors),
                              ("secondary-summary", secondary[code]), ("refusal-summary", refusals[code])):
            with open(os.path.join(target, f"{name}.json"), "w") as handle:
                json.dump(payload, handle, indent=None if name == "per-item-correctness" else 2,
                          ensure_ascii=False, allow_nan=False)
    with open(os.path.join(out, "endpoints.json"), "w") as handle:
        json.dump(endpoints(models, capability, secondary, refusals), handle, indent=2, allow_nan=False)
    print("wrote", out)


if __name__ == "__main__":
    main()
