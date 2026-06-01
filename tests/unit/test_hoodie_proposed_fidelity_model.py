from __future__ import annotations

import unittest

from src.analysis.hoodie_proposed_fidelity.config import READY_STATUS, REQUIRED_COMPONENT_IDS
from src.analysis.hoodie_proposed_fidelity.model import (
    ALLOWED_COMPONENT_STATUSES,
    HoodieProposedComponent,
    HoodieProposedFidelityReport,
    HoodieProposedRepairPlanEntry,
)
from src.analysis.hoodie_proposed_fidelity.report import build_feature_081_report


class HoodieProposedFidelityModelTests(unittest.TestCase):
    def _component(self, **overrides) -> HoodieProposedComponent:
        component = HoodieProposedComponent(
            component_id="action_space",
            component_name="action_space",
            paper_definition="The paper action space is hybrid.",
            paper_source="paper",
            current_implementation="The active path exposes local, horizontal, and vertical action families.",
            implementation_reference="src/analysis/proposed_method_integration_readiness/report.py",
            status="implemented",
            gap="none",
            required_repair="No repair required.",
        )
        return component if not overrides else HoodieProposedComponent(**{**component.to_dict(), **overrides})

    def test_component_accepts_required_fields(self) -> None:
        component = self._component()
        self.assertEqual(component.component_id, "action_space")
        self.assertIn(component.status, ALLOWED_COMPONENT_STATUSES)

    def test_component_rejects_empty_required_text(self) -> None:
        with self.assertRaises(ValueError):
            self._component(component_name="")

    def test_repair_plan_entry_requires_non_empty_targets(self) -> None:
        with self.assertRaises(ValueError):
            HoodieProposedRepairPlanEntry(
                component_id="dqn_training",
                gap_type="missing_training",
                repair_action="Add training loop.",
                target_files=(),
                tests_needed=("tests/unit/test_hoodie_proposed_fidelity_report.py",),
            )

    def test_report_rejects_missing_claim_boundary_or_scope(self) -> None:
        report = build_feature_081_report()
        with self.assertRaises(ValueError):
            HoodieProposedFidelityReport(
                feature_id=report.feature_id,
                status=READY_STATUS,
                passed=True,
                source_pdf=report.source_pdf,
                source_ocr=report.source_ocr,
                component_count=report.component_count,
                implemented_count=report.implemented_count,
                partial_count=report.partial_count,
                missing_count=report.missing_count,
                not_applicable_count=report.not_applicable_count,
                components=report.components,
                gap_summary=report.gap_summary,
                repair_plan=report.repair_plan,
                validation_summary=report.validation_summary,
                claim_boundary=(),
                scope_evidence=report.scope_evidence,
            )

    def test_report_passes_with_honest_gaps(self) -> None:
        report = build_feature_081_report()
        self.assertTrue(report.passed)
        self.assertEqual(report.status, READY_STATUS)
        self.assertEqual(report.component_count, len(REQUIRED_COMPONENT_IDS))
        self.assertGreater(report.partial_count, 0)
        self.assertGreater(report.missing_count, 0)
        self.assertIn("HOODIE_PROPOSED is the base-paper target.", report.validation_summary)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
