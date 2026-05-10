from __future__ import annotations

import unittest

from src.audits.differential_environment import (
    ComparisonClassification,
    FindingCause,
    ToyCaseScenario,
    build_default_toy_cases,
)
from src.audits.differential_environment.audit import DifferentialEnvironmentAudit
from src.audits.differential_environment.cases import ToyCase, ToyCaseScenario
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

    def test_timeout_drop_without_dropped_terminal_outcome_is_divergence(self) -> None:
        class _NoDropEnv:
            def reset(self, seed=None):
                self.current_task = object()
                return {"observation": True}, {}

            def legal_action_mask(self, current_task):
                return {"local": True}

            def step(self, action):
                return {"observation": True}, 0.0, True, False, {
                    "finalized_tasks": [{"task_id": "case-timeout-drop-task", "terminal_outcome": "completed"}]
                }

        audit = DifferentialEnvironmentAudit(environment_factory=_NoDropEnv)
        case = ToyCase(
            case_id="case-timeout-drop",
            scenario_type=ToyCaseScenario.TIMEOUT_DROP,
            task_id="case-timeout-drop-task",
            source_agent_id="edge-1",
            destination_target="cloud",
            action="local",
            timeout_slot=2,
            seed=7,
            expected_comparison_context="timeout-drop",
        )
        run = audit._run_case(case)
        self.assertEqual(run.comparison_result.classification, ComparisonClassification.DIVERGENCE)
        self.assertEqual(run.comparison_result.finding_cause, FindingCause.LIKELY_ENVIRONMENT_BUG)

    def test_offload_cases_remain_unsupported_when_environment_cannot_inject_trace(self) -> None:
        class _UnsupportedEnv:
            def reset(self, seed=None):
                self.current_task = object()
                return {"observation": True}, {}

            def legal_action_mask(self, current_task):
                return {"local": True, "horizontal": False, "vertical": False}

        audit = DifferentialEnvironmentAudit(environment_factory=_UnsupportedEnv)
        cases = build_default_toy_cases()
        horizontal = cases[1]
        vertical = cases[2]
        horizontal_run = audit._run_case(horizontal)
        vertical_run = audit._run_case(vertical)
        self.assertEqual(horizontal_run.comparison_result.classification, ComparisonClassification.UNSUPPORTED_BY_ENVIRONMENT_TRACE)
        self.assertEqual(horizontal_run.comparison_result.finding_cause, FindingCause.INSTRUMENTATION_GAP)
        self.assertEqual(vertical_run.comparison_result.classification, ComparisonClassification.UNSUPPORTED_BY_ENVIRONMENT_TRACE)
        self.assertEqual(vertical_run.comparison_result.finding_cause, FindingCause.INSTRUMENTATION_GAP)


if __name__ == "__main__":
    unittest.main()
