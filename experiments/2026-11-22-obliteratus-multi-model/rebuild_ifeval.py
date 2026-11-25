"""Refresh the LoRA study's strict IFEval summaries and report tables."""
import argparse
import json
from pathlib import Path

import numpy as np

from ifeval_scores import encoded, from_items, save_outputs


STUDY = "2026-11-22-obliteratus-multi-model"
MODELS = {"q1": "Qwen/Qwen2.5-1.5B-Instruct", "q3": "Qwen/Qwen2.5-3B-Instruct", "z2": "Qwen/Qwen2.5-1.5B-Instruct"}


def format_table(group, arms, secondary):
    lines = [
        "| Arm | GSM8K strict (%) | Ends with `#### number` | At the 256-token limit | Median GSM8K tokens | IFEval strict instructions, passed / total (%) |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for arm, scores in arms.items():
        name = {"PS": "P_A", "RS": "R_A"}.get(arm, arm) if group == "z2" else arm
        i = scores["ifeval"]
        s = secondary["arms"][arm]
        lines.append(f"| {name} | {s['gsm8k_strict_match'] * 100:.2f} | {s['gsm8k_ends_with_answer_marker']} | "
                     f"{s['gsm8k_at_limit']} | {s['gsm8k_tokens_median']:g} | "
                     f"{i['instructions_passed']}/{i['instructions_total']} ({100 * i['secondary']:.2f}%) |")
    return "\n".join(lines)


def instruction_contrasts(cap, counts, secondary):
    pairs = {f"{arm}-{base}": (arm, base) for arm in counts for base in counts}
    for name, comparisons in secondary["comparisons"].items():
        arm, base = pairs[name]
        keys = sorted(counts[base])
        passed = np.array([counts[arm][k][0] - counts[base][k][0] for k in keys])
        total = np.array([counts[base][k][1] for k in keys])
        draws = cap["settings"]["draws"]
        rng = np.random.default_rng(cap["settings"]["seed"])
        gsm_n = cap["arms"][base]["gsm8k"]["n"]
        # The original joint analysis drew GSM8K pairs first from the same random stream.
        rng.integers(0, gsm_n, size=(draws, gsm_n))
        indices = rng.integers(0, len(keys), size=(draws, len(keys)))
        rates = passed[indices].sum(axis=1) / total[indices].sum(axis=1)
        comparisons["ifeval_inst_level_strict"] = {
            "diff": float(passed.sum() / total.sum()), "ci95": np.percentile(rates, [2.5, 97.5]).tolist(),
        }


def interpretation(models):
    q3 = models["q3"]["R0"]["ifeval"]
    comparisons = []
    for model in ("q3", "q1"):
        arms = models[model]
        diffs = [100 * (arms["R0"]["ifeval"][key] - arms["P"]["ifeval"][key]) for key in ("primary", "secondary")]
        comparisons.append(f"{diffs[0]:+.2f} pp per prompt and {diffs[1]:+.2f} pp per instruction")
    return (f"On Qwen2.5-3B after repair, {round(q3['n'] * q3['primary'])}/{q3['n']} prompts passed every strict check. "
            f"Across individual instructions, {q3['instructions_passed']}/{q3['instructions_total']} passed "
            f"({100 * q3['secondary']:.2f}%). The earlier calculation gave each prompt equal weight "
            f"and averaged its fraction of instructions passed ({100 * q3['historical_mean_prompt_fraction']:.2f}%). "
            f"Relative to the projected model, the repair changed the Qwen2.5-3B scores by {comparisons[0]}. "
            f"The corresponding exploratory changes for Qwen2.5-1.5B were {comparisons[1]}.").replace(" -", " −")


def replace_block(text, key, content):
    start = f"<!-- ifeval:{key} -->"
    end = f"<!-- /ifeval:{key} -->"
    if text.count(start) != 1 or text.count(end) != 1:
        raise ValueError(f"Missing or duplicate markers for {key}")
    before, body = text.split(start)
    _, after = body.split(end)
    return f"{before}{start}\n{content}\n{end}{after}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if a published value or table is stale")
    args = parser.parse_args()
    report = Path(__file__).resolve().parents[2] / "reports" / STUDY
    main_report = report / "results.md"
    outputs = {main_report: main_report.read_text()}
    models = {}
    for group, model in MODELS.items():
        directory = report / "data" / group
        cap_path, sec_path = (directory / f"{name}-summary.json" for name in ("capability", "secondary"))
        cap, counts = from_items(directory, model)
        sec = json.loads(sec_path.read_text())
        if cap["arms"].keys() != sec["arms"].keys():
            raise ValueError(f"{group}: different arms in the two summaries")
        for arm, scores in cap["arms"].items():
            sec["arms"][arm]["ifeval_inst_level_strict"] = scores["ifeval"]["secondary"]
        instruction_contrasts(cap, counts, sec)
        sec["ifeval_measurement"] = cap["settings"]["ifeval"]
        outputs[cap_path], outputs[sec_path] = encoded(cap_path, cap), encoded(sec_path, sec)
        models[group] = cap["arms"]
        table = format_table(group, cap["arms"], sec)
        pages = {"q1": [directory / "partial-results.md"], "q3": [main_report],
                 "z2": [main_report, directory / "tables.md"]}[group]
        for page in pages:
            text = outputs[page] if page in outputs else page.read_text()
            outputs[page] = replace_block(text, group, table)
    outputs[main_report] = replace_block(outputs[main_report], "interpretation", interpretation(models))
    save_outputs(outputs, args.check)


if __name__ == "__main__":
    main()
