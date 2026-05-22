from __future__ import annotations

import unittest

from src.analysis.completion_root_cause_diagnosis import run_completion_root_cause_diagnosis


class CompletionRootCauseDiagnosisIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = run_completion_root_cause_diagnosis()

    def test_report_recommends_next_feature_without_repair(self) -> None:
        payload = self.report.to_dict()
        self.assertEqual(payload["final_verdict"], "root_cause_identified_configuration_or_load_explanation")
        self.assertTrue(payload["no_runtime_repair_performed"])
        self.assertEqual(payload["recommended_next_feature"], "load/admission/action-exposure review")

    def test_prerequisite_and_prior_feature_gates_verified(self) -> None:
        payload = self.report.to_dict()
        self.assertTrue(all(entry["verified"] for entry in payload["prerequisite_tags_verified"]))
        self.assertTrue(all(entry["verified"] for entry in payload["prior_feature_gates_verified"]))
        self.assertTrue(next(entry for entry in payload["prerequisite_tags_verified"] if entry["name"] == "no_unrelated_dirty_files")["verified"])

    def test_dominant_root_causes_are_ranked(self) -> None:
        dominant = self.report.dominant_root_causes
        self.assertTrue(dominant)
        evidence_counts = [item["evidence_count"] for item in dominant]
        self.assertEqual(evidence_counts, sorted(evidence_counts, reverse=True))

    def test_report_mentions_feature_044_trace_source(self) -> None:
        payload = self.report.to_dict()
        sources = payload["trace_input_sources"]
        self.assertTrue(any("passive-runtime-lifecycle-trace-instrumentation" in item["path"] for item in sources))
        self.assertTrue(payload["paper_default_runtime_verified"]["paper_default_probe"])


if __name__ == "__main__":
    unittest.main()
