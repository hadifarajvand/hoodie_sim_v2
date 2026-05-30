from __future__ import annotations

import unittest

from src.analysis.full_hoodie_mechanism_fidelity_batch.report import build_feature_069_report


class FullHoodieMechanismFidelityBatchReportTests(unittest.TestCase):
    def test_report_schema_contains_required_fields(self) -> None:
        report = build_feature_069_report(
            changed_files=(
                "specs/069-full-hoodie-mechanism-fidelity-batch/spec.md",
                "src/analysis/full_hoodie_mechanism_fidelity_batch/report.py",
                "tests/unit/test_full_hoodie_mechanism_fidelity_batch_report.py",
            )
        )
        payload = report.to_dict()
        required = {
            "feature_name",
            "status",
            "passed",
            "changed_files",
            "mechanism_contracts",
            "blockers",
            "validation_commands",
            "feature_068r_regression_status",
            "paper_claim_boundary",
            "recommended_next_feature",
        }
        self.assertTrue(required.issubset(payload))
        self.assertEqual(payload["feature_name"], "Feature 069 - Full HOODIE Mechanism Fidelity Batch")
        self.assertTrue(payload["passed"])
        self.assertTrue(payload["feature_068r_regression_status"]["passed"])
        self.assertGreaterEqual(len(payload["mechanism_contracts"]), 6)
        for contract in payload["mechanism_contracts"]:
            self.assertTrue(
                {"name", "category", "status", "verified_behavior", "compatibility_fallback", "assumption_backed_behavior", "blockers", "evidence_files"}.issubset(contract)
            )

    def test_contracts_expose_required_mechanism_evidence(self) -> None:
        report = build_feature_069_report()
        coordination = report.coordination_graph_contract
        synchronization = report.synchronization_contract
        delayed = report.delayed_reward_contract
        congestion = report.congestion_control_contract
        timeout_drop = report.timeout_drop_evidence
        reward_pipeline = report.reward_pipeline_evidence

        self.assertEqual(coordination.assumption_status, "blocked")
        self.assertEqual(len(coordination.blockers), 1)
        self.assertIn("structured artifact", coordination.blockers[0].description)
        self.assertEqual(
            (
                synchronization.decision_phase,
                synchronization.action_application_phase,
                synchronization.queue_update_phase,
                synchronization.terminal_accounting_phase,
                synchronization.reward_emission_phase,
            ),
            ("decision", "action_application", "queue_update", "terminal_accounting", "reward_emission"),
        )
        self.assertEqual(delayed.reward_equation_status, "assumption_backed")
        self.assertEqual(delayed.reward_emitted_at, "terminal_resolution")
        self.assertIn("Feature 068R", congestion.compatibility_fallback)
        self.assertEqual(congestion.private_queue_pressure.queue_type, "private")
        self.assertEqual(congestion.public_queue_pressure.queue_type, "public")
        self.assertEqual(congestion.cloud_queue_pressure.queue_type, "cloud")
        self.assertEqual(timeout_drop.blocker_status, "blocking")
        self.assertEqual(reward_pipeline.equation_source, "src/environment/reward_timing.py + src/environment/environment.py")

    def test_feature_068r_regression_gate_is_green(self) -> None:
        report = build_feature_069_report()
        regression = report.feature_068r_regression_status
        self.assertTrue(regression.registry_coverage_passed)
        self.assertTrue(regression.legal_mask_authority_passed)
        self.assertTrue(regression.family_fallback_passed)
        self.assertTrue(regression.seeded_ro_passed)
        self.assertTrue(regression.bco_balance_hint_passed)
        self.assertTrue(regression.mleo_candidate_metadata_passed)
        self.assertTrue(regression.passed)

    def test_validation_commands_are_recorded(self) -> None:
        report = build_feature_069_report()
        self.assertGreaterEqual(len(report.validation_commands), 4)
        self.assertTrue(report.validation_commands[0].endswith("tests.unit.test_baseline_policy_fidelity tests.unit.test_mleo_policy tests.integration.test_baseline_policy_fidelity_flow"))


if __name__ == "__main__":
    unittest.main()
