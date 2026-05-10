from __future__ import annotations

import unittest

from src.audits.differential_environment import (
    ComparisonClassification,
    FindingCause,
    ToyCaseScenario,
    build_default_toy_cases,
)
from src.audits.differential_environment.classify import classify_comparison
from src.audits.differential_environment.report import AuditObservationSummary


class DifferentialEnvironmentAuditUnitTest(unittest.TestCase):
    def test_toy_cases_are_deterministic(self) -> None:
        cases = build_default_toy_cases()
        self.assertEqual(len(cases), 6)
        self.assertEqual(cases[0].scenario_type, ToyCaseScenario.LOCAL_COMPUTE)
        self.assertEqual(cases[-1].scenario_type, ToyCaseScenario.DETERMINISTIC_ORDERING)
        self.assertEqual([case.case_id for case in cases], [case.case_id for case in build_default_toy_cases()])

    def test_classification_logic_match(self) -> None:
        summary = AuditObservationSummary("case-1", ("created", "selected_action"), "completed", "terminal")
        classification, cause = classify_comparison(
            reference_summary=summary.to_dict(),
            environment_summary=summary.to_dict(),
            environment_supported=True,
        )
        self.assertEqual(classification, ComparisonClassification.MATCH)
        self.assertEqual(cause, FindingCause.EXPECTED_SCOPE_DIFFERENCE)

    def test_classification_logic_unsupported_trace(self) -> None:
        summary = AuditObservationSummary("case-1", tuple(), None, None)
        classification, cause = classify_comparison(
            reference_summary={"event_sequence": ("created",), "terminal_status": "completed", "reward_timing": "terminal"},
            environment_summary=summary.to_dict(),
            environment_supported=False,
        )
        self.assertEqual(classification, ComparisonClassification.UNSUPPORTED_BY_ENVIRONMENT_TRACE)
        self.assertEqual(cause, FindingCause.INSTRUMENTATION_GAP)

    def test_classification_logic_divergence(self) -> None:
        reference = AuditObservationSummary("case-1", ("created", "selected_action"), "completed", "terminal")
        environment = AuditObservationSummary("case-1", ("created",), "dropped", "terminal")
        classification, cause = classify_comparison(
            reference_summary=reference.to_dict(),
            environment_summary=environment.to_dict(),
            environment_supported=True,
        )
        self.assertEqual(classification, ComparisonClassification.DIVERGENCE)
        self.assertEqual(cause, FindingCause.LIKELY_ENVIRONMENT_BUG)


if __name__ == "__main__":
    unittest.main()
