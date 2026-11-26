import json

import pytest

import analyze_vocab as av


def write_report(tmp_path, name, stock, edited):
    def flags(refused, invalid):
        return {"refused_flags": refused, "invalid_flags": invalid}
    report = {"measurement": {"stock": {"harmful": flags(*stock)}, "edited": {"harmful": flags(*edited)}}}
    path = tmp_path / f"{name}.json"
    path.write_text(json.dumps(report))
    return str(path)


def fails(k, n=200):
    return [i < k for i in range(n)], [False] * n


def config_for(tmp_path, s, v, sp, vp):
    a = write_report(tmp_path, "a", s, v)
    b = write_report(tmp_path, "b", sp, vp)
    return {"main_models": ["l8"], "models": {"l8": {"versions": {
        "S": {"report": a, "role": "stock"}, "V": {"report": a, "role": "edited"},
        "SP": {"report": b, "role": "stock"}, "VP": {"report": b, "role": "edited"}}}}}


def test_one_direction_mcnemar(tmp_path):
    rows = av.refusals(config_for(tmp_path, fails(180), fails(120), fails(180), fails(120)))
    c = rows["l8"]["comparisons"]["V-S"]
    assert round(c["diff"] * 100, 1) == -30.0 and c["discordant"] == 60 and c["mcnemar_p"] < 1e-15


def test_interaction_zero(tmp_path):
    rows = av.refusals(config_for(tmp_path, fails(150), fails(90), fails(150), fails(90)))
    assert rows["l8"]["interaction"] == 0


def test_rate_valid_and_objective():
    refused = [i < 100 for i in range(200)]
    invalid = [100 <= i < 120 for i in range(200)]
    summary, fail = av.version_summary({"refused_flags": refused, "invalid_flags": invalid})
    assert round(summary["rate_valid"], 4) == 0.5556 and summary["objective"] == pytest.approx(0.60)
    assert sum(fail) == 120


def test_floor_effect(tmp_path):
    rows = av.refusals(config_for(tmp_path, fails(180), fails(150), fails(20), fails(5)))
    assert rows["l8"]["versions"]["SP"]["objective"] == pytest.approx(0.10)
    v = av.verdicts(rows["l8"], None, None, "l8", {"1": 0.001, "2": 0.001})
    assert v["adds_beyond_prefill"] == av.FLOOR_VERDICT


def test_judge_gate():
    def rows(agree_edited, agree_base):
        out = []
        for group, agree in (("edited", agree_edited), ("base", agree_base)):
            out += [(group, "zgoda", "C")] * agree + [(group, "zgoda", "R")] * (150 - agree)
        return out
    passed = av.gate(rows(141, 140))
    failed = av.gate(rows(140, 140))
    assert passed["agree"] == 281 and passed["passed"] is True
    assert failed["agree"] == 280 and failed["passed"] is False
