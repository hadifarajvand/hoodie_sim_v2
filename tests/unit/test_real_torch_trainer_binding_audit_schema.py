from __future__ import annotations

import unittest

from src.analysis.real_torch_trainer_binding_audit import build_real_torch_trainer_binding_audit_report
from src.analysis.real_torch_trainer_binding_audit.config import FEATURE_ID, REQUIRED_TOP_LEVEL_FIELDS
from src.analysis.real_torch_trainer_binding_audit.model import RealTorchTrainerBindingAuditReport


def _base_report_kwargs() -> dict:
    payload = build_real_torch_trainer_binding_audit_report().to_dict()
    return {key: payload[key] for key in REQUIRED_TOP_LEVEL_FIELDS}


class RealTorchTrainerBindingAuditSchemaTests(unittest.TestCase):
    def test_report_contains_required_top_level_fields(self) -> None:
        payload = build_real_torch_trainer_binding_audit_report().to_dict()
        for key in REQUIRED_TOP_LEVEL_FIELDS:
            self.assertIn(key, payload)
        self.assertEqual(payload["feature_id"], FEATURE_ID)

    def test_expected_current_verdict_routes_to_feature_060b(self) -> None:
        payload = build_real_torch_trainer_binding_audit_report().to_dict()
        self.assertEqual(payload["final_verdict"], "audit_scope_blocked")
        self.assertEqual(payload["recommended_next_feature"], "Repair Feature 060A audit scope hygiene")
        self.assertGreater(len(payload["remaining_blockers"]), 0)

    def test_verified_verdict_cannot_have_blockers(self) -> None:
        kwargs = _base_report_kwargs()
        kwargs["final_verdict"] = "real_torch_trainer_binding_verified"
        kwargs["recommended_next_feature"] = "Feature 061 — Campaign Result Integrity and Comparison Readiness Audit"
        kwargs["binding_audit_summary"]["real_binding_verified"] = True
        kwargs["binding_audit_summary"]["feature_060_claim_supported"] = True
        kwargs["remaining_blockers"] = ["feature_060_runner_missing_torch_import"]
        with self.assertRaises(ValueError):
            RealTorchTrainerBindingAuditReport(**kwargs)

    def test_missing_binding_cannot_route_to_feature_061(self) -> None:
        kwargs = _base_report_kwargs()
        kwargs["final_verdict"] = "real_torch_trainer_binding_missing_repair_required"
        kwargs["recommended_next_feature"] = "Feature 061 — Campaign Result Integrity and Comparison Readiness Audit"
        with self.assertRaises(ValueError):
            RealTorchTrainerBindingAuditReport(**kwargs)


if __name__ == "__main__":
    unittest.main()
