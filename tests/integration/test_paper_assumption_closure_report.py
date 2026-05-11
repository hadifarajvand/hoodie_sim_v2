from __future__ import annotations

import json
import unittest

from src.analysis.paper_assumption_closure_evidence_exhaustion.report import build_assumption_closure_report, write_assumption_closure_report


class PaperAssumptionClosureReportTests(unittest.TestCase):
    def test_report_schema_and_json_parse(self) -> None:
        report = build_assumption_closure_report()
        json_path, markdown_path = write_assumption_closure_report(report)
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        for key in (
            "feature_id",
            "schema_version",
            "source_gates",
            "inventory_summary",
            "items",
            "recovered_items",
            "partially_recovered_items",
            "contradicted_items",
            "assumption_backed_items",
            "unrecoverable_after_evidence_exhaustion_items",
            "out_of_scope_items",
            "manual_review_required_items",
            "runtime_dependency_decisions",
            "no_training_or_policy_drift",
            "no_dependency_drift",
            "final_verdict",
        ):
            self.assertIn(key, payload)
        self.assertTrue(markdown_path.exists())

