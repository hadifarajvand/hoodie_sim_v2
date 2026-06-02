from __future__ import annotations

import unittest

from src.analysis.hoodie_proposed_method.config import FEATURE_ID, TARGET_METHOD_ID, validate_scope
from src.analysis.hoodie_proposed_method.model import ComponentCoverageEntry, HoodieProposedMethodReport
from src.analysis.hoodie_proposed_method.report import build_feature_080_report


class HoodieProposedMethodModelTests(unittest.TestCase):
    def test_report_exposes_component_counts_readiness_and_formula_registry(self) -> None:
        report = build_feature_080_report(
            changed_files=(
                "specs/080-evaluation-ranking/plan.md",
                "src/analysis/hoodie_proposed_method/report.py",
                "tests/unit/test_hoodie_proposed_method_model.py",
            )
        )
        self.assertEqual(report.feature_id, FEATURE_ID)
        self.assertEqual(report.component_count, 14)
        self.assertEqual(report.implemented_count, 7)
        self.assertEqual(report.partial_count, 7)
        self.assertEqual(report.missing_count, 0)
        self.assertEqual(report.readiness_level, "mostly_implemented")
        self.assertFalse(report.passed)
        self.assertEqual(report.status, "hoodie_proposed_method_blocked")
        self.assertEqual(len(report.formula_registry), 12)
        self.assertEqual(len(report.remaining_gaps), 7)
        self.assertEqual(TARGET_METHOD_ID, "HOODIE_PROPOSED")

        payload = report.to_dict()
        self.assertEqual(payload["feature_id"], FEATURE_ID)
        self.assertEqual(payload["component_count"], 14)
        self.assertEqual(len(payload["component_coverage"]), 14)

    def test_component_entry_rejects_invalid_status_and_unknown_component(self) -> None:
        with self.assertRaises(ValueError):
            ComponentCoverageEntry(
                component_id="unknown",
                component_name="Unknown component",
                paper_requirement="unsupported",
                current_implementation="unsupported",
                implementation_reference="src/analysis/hoodie_proposed_method/report.py",
                status="implemented",
                gap="none",
                required_repair="none",
            )

        with self.assertRaises(ValueError):
            ComponentCoverageEntry(
                component_id="hybrid_action_model",
                component_name="Hybrid action model",
                paper_requirement="paper requirement",
                current_implementation="current implementation",
                implementation_reference="src/analysis/hoodie_proposed_method/report.py",
                status="done",
                gap="none",
                required_repair="none",
            )

    def test_report_object_requires_consistent_counts(self) -> None:
        report = build_feature_080_report(
            changed_files=(
                "specs/080-evaluation-ranking/plan.md",
                "src/analysis/hoodie_proposed_method/report.py",
                "tests/unit/test_hoodie_proposed_method_model.py",
            )
        )
        with self.assertRaises(ValueError):
            HoodieProposedMethodReport(
                feature_id=report.feature_id,
                status=report.status,
                passed=report.passed,
                component_count=report.component_count,
                implemented_count=report.implemented_count + 1,
                partial_count=report.partial_count,
                missing_count=report.missing_count,
                formula_registry=report.formula_registry,
                component_coverage=report.component_coverage,
                remaining_gaps=report.remaining_gaps,
                readiness_level=report.readiness_level,
                claim_boundary=report.claim_boundary,
                scope_evidence=report.scope_evidence,
            )

    def test_validate_scope_accepts_feature_scope_only(self) -> None:
        self.assertEqual(
            validate_scope(
                [
                    "specs/080-evaluation-ranking/plan.md",
                    "src/analysis/hoodie_proposed_method/model.py",
                    "tests/unit/test_hoodie_proposed_method_model.py",
                ]
            ),
            [
                "specs/080-evaluation-ranking/plan.md",
                "src/analysis/hoodie_proposed_method/model.py",
                "tests/unit/test_hoodie_proposed_method_model.py",
            ],
        )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
