from __future__ import annotations

import json
import unittest

from src.analysis.real_torch_trainer_binding_audit import generate_real_torch_trainer_binding_audit_artifacts
from src.analysis.real_torch_trainer_binding_audit.config import REPORT_JSON, REPORT_MD, REQUIRED_TOP_LEVEL_FIELDS


class RealTorchTrainerBindingAuditReportTests(unittest.TestCase):
    def test_report_artifacts_are_written(self) -> None:
        report, json_path, md_path = generate_real_torch_trainer_binding_audit_artifacts()
        self.assertEqual(json_path, REPORT_JSON)
        self.assertEqual(md_path, REPORT_MD)
        self.assertTrue(json_path.exists())
        self.assertTrue(md_path.exists())
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertEqual(payload, report.to_dict())

    def test_json_report_has_required_fields_and_internal_routing(self) -> None:
        generate_real_torch_trainer_binding_audit_artifacts()
        payload = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        for key in REQUIRED_TOP_LEVEL_FIELDS:
            self.assertIn(key, payload)
        self.assertEqual(payload["final_verdict"], "real_torch_trainer_binding_missing_repair_required")
        self.assertGreater(len(payload["remaining_blockers"]), 0)
        self.assertEqual(payload["recommended_next_feature"], "Feature 060B — Bind Full Campaign Execution to Real Torch Trainer")

    def test_markdown_report_contains_verdict_and_blockers(self) -> None:
        generate_real_torch_trainer_binding_audit_artifacts()
        text = REPORT_MD.read_text(encoding="utf-8")
        self.assertIn("real_torch_trainer_binding_missing_repair_required", text)
        self.assertIn("feature_060_runner_missing_torch_import", text)
        self.assertIn("Feature 060B", text)


if __name__ == "__main__":
    unittest.main()
