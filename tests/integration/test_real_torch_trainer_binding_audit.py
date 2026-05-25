from __future__ import annotations

import unittest

from src.analysis.real_torch_trainer_binding_audit import build_real_torch_trainer_binding_audit_report


class RealTorchTrainerBindingAuditIntegrationTests(unittest.TestCase):
    def test_build_report_returns_expected_repair_verdict(self) -> None:
        report = build_real_torch_trainer_binding_audit_report()
        payload = report.to_dict()
        self.assertEqual(payload["final_verdict"], "real_torch_trainer_binding_missing_repair_required")
        self.assertEqual(payload["recommended_next_feature"], "Feature 060B — Bind Full Campaign Execution to Real Torch Trainer")
        self.assertTrue(payload["binding_audit_summary"]["repair_required"])
        self.assertEqual(payload["binding_audit_summary"]["repair_feature"], "Feature 060B — Bind Full Campaign Execution to Real Torch Trainer")

    def test_report_does_not_claim_verified_binding_while_runner_is_scalar(self) -> None:
        payload = build_real_torch_trainer_binding_audit_report().to_dict()
        self.assertFalse(payload["binding_audit_summary"]["real_binding_verified"])
        self.assertNotEqual(payload["final_verdict"], "real_torch_trainer_binding_verified")
        self.assertNotEqual(payload["recommended_next_feature"], "Feature 061 — Campaign Result Integrity and Comparison Readiness Audit")


if __name__ == "__main__":
    unittest.main()
