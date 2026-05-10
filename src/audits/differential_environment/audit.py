from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.environment.gym_adapter import HoodieGymEnvironment
from src.reference_model import ActionInput, ActionType, ReferenceLifecycleKernel, TaskIdentity, TaskWorkload

from .cases import ToyCase, ToyCaseScenario, build_default_toy_cases
from .classify import ComparisonClassification, FindingCause, classify_comparison
from .report import (
    AuditObservationSummary,
    AuditReport,
    ComparisonResult,
    Finding,
    stable_report_hash,
)


@dataclass(slots=True)
class AuditCaseRun:
    case: ToyCase
    reference_summary: AuditObservationSummary
    environment_summary: AuditObservationSummary
    comparison_result: ComparisonResult
    finding: Finding
    assumption_text: str | None = None
    instrumentation_gap_text: str | None = None
    unsupported_text: str | None = None


class DifferentialEnvironmentAudit:
    def __init__(
        self,
        *,
        reference_kernel: ReferenceLifecycleKernel | None = None,
        environment_factory: Any | None = None,
        output_dir: Path | None = None,
    ) -> None:
        self.reference_kernel = reference_kernel or ReferenceLifecycleKernel()
        self.environment_factory = environment_factory or self._default_environment_factory
        self.output_dir = Path(output_dir or "artifacts/analysis/differential-environment-audit")

    @staticmethod
    def _default_environment_factory() -> HoodieGymEnvironment:
        return HoodieGymEnvironment(episode_length=6)

    def run(self, toy_cases: tuple[ToyCase, ...] | None = None) -> AuditReport:
        cases = toy_cases or build_default_toy_cases()
        case_runs = [self._run_case(case) for case in cases]
        report = self._build_report(case_runs)
        report.write(self.output_dir)
        return report

    def _run_case(self, case: ToyCase) -> AuditCaseRun:
        reference_summary = self._run_reference_case(case)
        environment_summary, environment_supported, assumption_text, instrumentation_gap_text, unsupported_text = self._probe_environment_case(case)
        classification, cause = classify_comparison(
            reference_summary=reference_summary.to_dict(),
            environment_summary=environment_summary.to_dict(),
            environment_supported=environment_supported,
        )
        comparison_result = ComparisonResult(
            case_id=case.case_id,
            classification=classification,
            finding_cause=cause,
            reference_summary=reference_summary,
            environment_summary=environment_summary,
            notes=self._case_notes(case, classification, cause),
        )
        finding = Finding(
            finding_id=f"F-{case.case_id}",
            case_id=case.case_id,
            classification=classification,
            cause=cause,
            evidence=self._finding_evidence(case, classification, cause, environment_supported),
        )
        return AuditCaseRun(
            case=case,
            reference_summary=reference_summary,
            environment_summary=environment_summary,
            comparison_result=comparison_result,
            finding=finding,
            assumption_text=assumption_text,
            instrumentation_gap_text=instrumentation_gap_text,
            unsupported_text=unsupported_text,
        )

    def _run_reference_case(self, case: ToyCase) -> AuditObservationSummary:
        identity, workload, action = self._convert_case(case)
        if case.scenario_type is ToyCaseScenario.TIMEOUT_DROP:
            ledger = self.reference_kernel.process_timeout(identity, workload, action)
        else:
            ledger = self.reference_kernel.process(identity, workload, action)
        event_sequence = tuple(event.event_type.value for event in ledger.events)
        reward_timing = "terminal" if ledger.reward_emitted else "decision"
        return AuditObservationSummary(
            case_id=case.case_id,
            event_sequence=event_sequence,
            terminal_status=ledger.terminal_status.value if ledger.terminal_status else None,
            reward_timing=reward_timing,
            notes="reference kernel",
        )

    def _probe_environment_case(
        self,
        case: ToyCase,
    ) -> tuple[AuditObservationSummary, bool, str | None, str | None, str | None]:
        env = self.environment_factory()
        observation, info = env.reset(seed=case.seed)
        step_records: list[str] = []
        selected_action: str | None = None
        environment_supported = False
        assumption_text = None
        instrumentation_gap_text = None
        unsupported_text = None

        if not isinstance(observation, dict):
            instrumentation_gap_text = "Environment reset did not return an observation dictionary."
            return (
                AuditObservationSummary(case.case_id, tuple(), None, None, notes="unsupported observation"),
                False,
                assumption_text,
                instrumentation_gap_text,
                unsupported_text,
            )

        current_task = getattr(env, "current_task", None)
        if current_task is None:
            unsupported_text = "Environment did not expose a current task after reset."
            return (
                AuditObservationSummary(case.case_id, tuple(), None, None, notes="no current task"),
                False,
                assumption_text,
                instrumentation_gap_text,
                unsupported_text,
            )

        try:
            selected_action = self._select_environment_action(case, current_task, env)
        except ValueError as exc:
            unsupported_text = str(exc)
            return (
                AuditObservationSummary(case.case_id, tuple(), None, None, notes="action unavailable"),
                False,
                assumption_text,
                instrumentation_gap_text,
                unsupported_text,
            )

        max_steps = max(3, case.timeout_slot + 3)
        reward_total = 0.0
        terminated = truncated = False
        info_payload = info
        step_error: ValueError | None = None
        for _ in range(max_steps):
            step_records.append(f"selected_action:{selected_action}")
            try:
                observation, reward, terminated, truncated, info_payload = env.step(selected_action)
            except ValueError as exc:
                step_error = exc
                instrumentation_gap_text = str(exc)
                break
            reward_total += float(reward)
            finalized = info_payload.get("finalized_tasks", [])
            if finalized:
                step_records.extend(
                    f"finalized:{task['task_id']}:{task.get('terminal_outcome')}" for task in finalized
                )
                terminal_outcome = finalized[0].get("terminal_outcome")
                reward_timing = "terminal" if reward_total != 0.0 and terminal_outcome in {"completed", "dropped"} else None
                environment_supported = True
                if case.scenario_type is ToyCaseScenario.TIMEOUT_DROP and terminal_outcome != "dropped":
                    instrumentation_gap_text = "Environment did not produce a timeout drop on the configured toy case."
                break
            if terminated or truncated:
                break

        if not environment_supported:
            instrumentation_gap_text = (
                instrumentation_gap_text
                or "Environment public interface did not expose enough trace evidence for full lifecycle comparison."
            )

        terminal_status = None
        if info_payload.get("finalized_tasks"):
            terminal_status = info_payload["finalized_tasks"][0].get("terminal_outcome")
        reward_timing = "terminal" if reward_total != 0.0 and terminal_status in {"completed", "dropped"} else None
        if step_error is not None:
            unsupported_text = unsupported_text or str(step_error)
        summary = AuditObservationSummary(
            case_id=case.case_id,
            event_sequence=tuple(step_records),
            terminal_status=terminal_status,
            reward_timing=reward_timing,
            notes="environment public interface",
        )
        return summary, environment_supported, assumption_text, instrumentation_gap_text, unsupported_text

    def _select_environment_action(self, case: ToyCase, current_task: Any, env: HoodieGymEnvironment) -> str:
        action = case.action
        legal_mask = env.legal_action_mask(current_task)
        if action in {"local", "compute_local"} and legal_mask.get("local", False):
            return "local"
        if action in {"horizontal", "offload_horizontal"} and legal_mask.get("horizontal", False):
            return "horizontal"
        if action in {"vertical", "offload_vertical"} and legal_mask.get("vertical", False):
            return "vertical"
        if action in {"local", "compute_local"}:
            return "local"
        if action in {"horizontal", "offload_horizontal"}:
            raise ValueError("Environment did not expose a legal horizontal offload path through the public interface.")
        if action in {"vertical", "offload_vertical"}:
            raise ValueError("Environment did not expose a legal vertical offload path through the public interface.")
        raise ValueError(f"Unsupported toy case action: {action}")

    def _convert_case(self, case: ToyCase) -> tuple[TaskIdentity, TaskWorkload, ActionInput]:
        identity = TaskIdentity(task_id=case.task_id, origin_edge_agent=case.source_agent_id, destination_target=case.destination_target)
        current_slot = case.timeout_slot if case.scenario_type is ToyCaseScenario.TIMEOUT_DROP else 0
        workload = TaskWorkload(task_size=1, timeout_slot=case.timeout_slot, current_slot=current_slot)
        action_type = {
            "local": ActionType.LOCAL_COMPUTE,
            "compute_local": ActionType.LOCAL_COMPUTE,
            "horizontal": ActionType.HORIZONTAL_OFFLOAD,
            "offload_horizontal": ActionType.HORIZONTAL_OFFLOAD,
            "vertical": ActionType.VERTICAL_OFFLOAD,
            "offload_vertical": ActionType.VERTICAL_OFFLOAD,
        }.get(case.action, ActionType.LOCAL_COMPUTE)
        action = ActionInput(action_type=action_type, destination_target=case.destination_target)
        return identity, workload, action

    def _finding_evidence(
        self,
        case: ToyCase,
        classification: ComparisonClassification,
        cause: FindingCause,
        environment_supported: bool,
    ) -> str:
        return (
            f"{case.case_id}: {classification.value} / {cause.value} "
            f"({'environment supported' if environment_supported else 'environment trace unsupported'})"
        )

    def _case_notes(self, case: ToyCase, classification: ComparisonClassification, cause: FindingCause) -> str:
        return f"{case.scenario_type.value}: {classification.value} / {cause.value}"

    def _build_report(self, case_runs: list[AuditCaseRun]) -> AuditReport:
        toy_cases = [case_run.case.to_dict() for case_run in case_runs]
        reference_summary = [case_run.reference_summary.to_dict() for case_run in case_runs]
        environment_summary = [case_run.environment_summary.to_dict() for case_run in case_runs]
        comparison_results = [case_run.comparison_result.to_dict() for case_run in case_runs]
        findings = [case_run.finding.to_dict() for case_run in case_runs]

        assumptions = [
            {"case_id": case_run.case.case_id, "text": case_run.assumption_text}
            for case_run in case_runs
            if case_run.assumption_text
        ]
        instrumentation_gaps = [
            {"case_id": case_run.case.case_id, "text": case_run.instrumentation_gap_text}
            for case_run in case_runs
            if case_run.instrumentation_gap_text
        ]
        unsupported_cases = [
            {"case_id": case_run.case.case_id, "text": case_run.unsupported_text}
            for case_run in case_runs
            if case_run.unsupported_text
        ]
        metadata = {
            "feature_id": "018",
            "generated_by": "DifferentialEnvironmentAudit",
            "deterministic": True,
            "source_refs": [
                "specs/018-differential-environment-audit/spec.md",
                "src/reference_model",
                "src/environment/gym_adapter.py",
            ],
        }
        reproducibility = {
            "output_root": self.output_dir.as_posix(),
            "approved_python": "/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python",
            "case_count": len(case_runs),
            "report_hash": stable_report_hash(
                {
                    "metadata": metadata,
                    "toy_cases": toy_cases,
                    "reference_summary": reference_summary,
                    "environment_summary": environment_summary,
                    "comparison_results": comparison_results,
                    "findings": findings,
                    "assumptions": assumptions,
                    "instrumentation_gaps": instrumentation_gaps,
                    "unsupported_cases": unsupported_cases,
                    "overall_status": "pass" if not any(item["classification"] != "match" for item in comparison_results) else "diagnostic",
                }
            ),
        }
        no_fix_disclaimer = (
            "No fixes were applied to HoodieGymEnvironment, SlotEngine, simulator lifecycle code, policies, "
            "baselines, metric formulas, campaign orchestration, or dependencies."
        )
        overall_status = "diagnostic"
        if all(item["classification"] == ComparisonClassification.MATCH.value for item in comparison_results):
            overall_status = "match"
        return AuditReport(
            metadata=metadata,
            toy_cases=toy_cases,
            reference_summary=reference_summary,
            environment_summary=environment_summary,
            comparison_results=comparison_results,
            findings=findings,
            assumptions=assumptions,
            instrumentation_gaps=instrumentation_gaps,
            unsupported_cases=unsupported_cases,
            no_fix_disclaimer=no_fix_disclaimer,
            reproducibility=reproducibility,
            overall_status=overall_status,
        )
