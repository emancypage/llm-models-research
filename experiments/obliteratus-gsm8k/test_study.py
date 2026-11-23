import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import study


def fixture_result(correct):
    samples = []
    for name in study.FILTERS:
        samples.extend(
            dict(doc_id=i, doc_hash=str(i), prompt_hash=str(i), target_hash=str(i), filter=name,
                 exact_match=int(i < correct), resps=[["private test answer"]])
            for i in range(5)
        )
    scores = {f"exact_match,{name}": correct / 5 for name in study.FILTERS}
    return {"samples": {"gsm8k": samples}, "results": {"gsm8k": scores},
            "higher_is_better": {"gsm8k": {"exact_match": True}}}


class StudyTest(unittest.TestCase):
    def test_capture_with_real_telemetry_and_export(self):
        source = study.HERE.parents[1] / "vendor" / "OBLITERATUS-7678d841"
        evaluations = iter([fixture_result(0), fixture_result(3)])
        lm_eval = SimpleNamespace(simple_evaluate=lambda **kwargs: next(evaluations))
        hub = SimpleNamespace(snapshot_download=lambda model, revision: model)
        with (
            tempfile.TemporaryDirectory() as tmp,
            patch.dict(os.environ, {"OBLITERATUS_TELEMETRY_REPO": "invalid-test-target"}),
            patch.dict("sys.modules", {"lm_eval": lm_eval, "huggingface_hub": hub}),
            patch("study.version", return_value="test"),
            patch("threading.Thread.start", side_effect=AssertionError("Unexpected background worker")),
        ):
            run = Path(tmp)
            study.run_comparison(source, run, 5)
            records = [json.loads(line) for line in (run / "private/telemetry.jsonl").read_text().splitlines()]
            self.assertEqual([r["extra"]["gsm8k_exact_match"]["strict-match"] for r in records], [0, 0.6])
            self.assertIn("private test answer", (run / "private/evaluation-1.json").read_text())
            self.assertEqual({p.name for p in (run / "share").iterdir()}, {"REPORT.md", "PROTOCOL.md", "results.json"})
            for path in (run / "share").iterdir():
                self.assertNotIn("private test answer", path.read_text())
                self.assertNotIn(tmp, path.read_text())
            report = json.loads((run / "share/results.json").read_text())
            self.assertEqual(report["headline_delta"], 0.6)
            self.assertEqual(report["stage"], "pilot")

    def test_mismatched_inputs_do_not_produce_a_share_bundle(self):
        with tempfile.TemporaryDirectory() as tmp:
            modified = fixture_result(3)
            for sample in modified["samples"]["gsm8k"]:
                sample["prompt_hash"] = "different"
            with self.assertRaisesRegex(ValueError, "different questions or prompts"):
                study.write_share_bundle(Path(tmp), [fixture_result(0), modified],
                                         {"original": 0, "abliterated": 0.6, "delta": 0.6}, 5, "test")
            self.assertFalse((Path(tmp) / "share").exists())


if __name__ == "__main__":
    unittest.main()
