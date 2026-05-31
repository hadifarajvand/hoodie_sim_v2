from __future__ import annotations

from functools import lru_cache
from math import isnan
from pathlib import Path
import json
from typing import Any, Sequence

from src.analysis.end_to_end_hoodie_golden_trace_validation.report import build_feature_072_report
from src.analysis.full_hoodie_mechanism_fidelity_batch.report import build_feature_069_report
from src.analysis.runtime_paper_faithful_semantics_alignment.report import build_feature_071_report
from src.analysis.topology_timeout_reward_fidelity.report import build_feature_070_report
from src.environment.deadline_rules import has_expired
from src.environment.paper_timeout import compute_absolute_deadline, is_success_before_deadline, terminal_status_from_completion
from src.environment.reward_timing import (
    can_emit_reward,
    phi_private,
    phi_public,
    reward_for_terminal_task,
    reward_from_terminal_state,
    reward_slot_for_terminal,
    select_phi,
)
from src.environment.task import Task

from .config import DEFAULT_CHANGED_FILES, DEFAULT_OUTPUT_DIR, VALIDATION_COMMANDS, validate_scope
from .model import (
    ControlledEvaluationBatchReport,
    ControlledEvaluationMetrics,
    ControlledEvaluationRegressionEvidence,
    ControlledEvaluationScenario,
    ControlledEvaluationTaskRecord,
)


FEATURE_073_STATUS_READY = "controlled_evaluation_batch_readiness_ready"
FEATURE_073_STATUS_WITH_BLOCKERS = "controlled_evaluation_batch_readiness_with_blockers"
FEATURE_074_RECOMMENDATION = "Feature 074 - Baseline Policy Comparative Evaluation Readiness"
FIGURE_7_SOURCE = "specs/070-topology-timeout-reward-fidelity/evidence/figure-7-topology-extraction.md"
PAPER_DROP_PENALTY = 40.0


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


@lru_cache(maxsize=1)
def _feature_070_report():
    return build_feature_070_report()


@lru_cache(maxsize=1)
def _feature_071_report():
    return build_feature_071_report()


@lru_cache(maxsize=1)
def _feature_072_report():
    return build_feature_072_report()


def _topology_map() -> dict[str, tuple[str, ...]]:
    return _feature_070_report().topology_evidence.neighbor_map


def _is_horizontal_neighbor(source_agent_id: str, destination_agent_id: str) -> bool:
    return destination_agent_id in _topology_map().get(source_agent_id, ())


def _local_task_record(
    *,
    task_id: str,
    arrival_slot: int,
    phi: int,
    completion_slot: int,
    reward_value: float | None = None,
    delay: float | int | None = None,
    deadline_violation: bool = False,
) -> ControlledEvaluationTaskRecord:
    deadline_slot = compute_absolute_deadline(arrival_slot, phi)
    success_before_deadline = is_success_before_deadline(completion_slot, arrival_slot, phi)
    local_phi = phi_private(psi_priv=completion_slot, t=arrival_slot)
    task = Task(
        task_id=int(task_id.split("-")[-1]) if task_id.split("-")[-1].isdigit() else 1,
        source_agent_id=1,
        arrival_slot=arrival_slot,
        size=1.0,
        processing_density=1.0,
        timeout_length=phi,
        absolute_deadline_slot=deadline_slot,
        completion_slot=completion_slot,
        terminal_outcome="completed" if success_before_deadline else "dropped",
        reward_emitted=True,
    )
    reward_can_emit = can_emit_reward("completed_private" if success_before_deadline else "dropped_timeout")
    if not reward_can_emit:
        raise ValueError("terminal tasks in the controlled batch must be able to emit reward")
    return ControlledEvaluationTaskRecord(
        task_id=task_id,
        source_agent_id="1",
        action_type="local",
        destination_agent_id="private",
        arrival_slot=arrival_slot,
        phi=phi,
        completion_slot=completion_slot,
        terminal_status="completed_private" if success_before_deadline else "dropped_timeout",
        reward_value=reward_value if reward_value is not None else (
            reward_for_terminal_task(task) if success_before_deadline else reward_from_terminal_state(True, "dropped_timeout", None, PAPER_DROP_PENALTY)
        ),
        delay=delay if delay is not None else local_phi,
        illegal_action_rejected=False,
        compatibility_mode_used=False,
        mode="paper",
        deadline_violation=deadline_violation or not success_before_deadline,
        topology_check_required=False,
        topology_final_legal=True,
        topology_reason="local_private_execution",
        topology_neighbor_map_source="local_private_execution",
    )


def _horizontal_task_record(
    *,
    task_id: str,
    source_agent_id: str,
    destination_agent_id: str,
    arrival_slot: int,
    phi: int,
    completion_slot: int,
) -> ControlledEvaluationTaskRecord:
    success_before_deadline = is_success_before_deadline(completion_slot, arrival_slot, phi)
    is_neighbor = _is_horizontal_neighbor(source_agent_id, destination_agent_id)
    is_self_destination = source_agent_id == destination_agent_id
    topology_final_legal = is_neighbor and not is_self_destination
    if topology_final_legal:
        terminal_status = terminal_status_from_completion(completion_slot, arrival_slot, phi, completion_kind="public")
        terminal_outcome = "completed"
        reward_value = reward_from_terminal_state(
            True,
            terminal_status,
            select_phi(
                False,
                phi_private(psi_priv=completion_slot, t=arrival_slot),
                phi_public(((1, 6), (0, 9)), t=arrival_slot),
            ),
            PAPER_DROP_PENALTY,
        )
        illegal_action_rejected = False
    else:
        terminal_status = "dropped_unavailable"
        terminal_outcome = "dropped"
        reward_value = reward_from_terminal_state(True, terminal_status, None, PAPER_DROP_PENALTY)
        illegal_action_rejected = True
    return ControlledEvaluationTaskRecord(
        task_id=task_id,
        source_agent_id=source_agent_id,
        action_type="horizontal",
        destination_agent_id=destination_agent_id,
        arrival_slot=arrival_slot,
        phi=phi,
        completion_slot=completion_slot,
        terminal_status=terminal_status,
        reward_value=reward_value,
        delay=reward_slot_for_terminal(completion_slot) - arrival_slot,
        illegal_action_rejected=illegal_action_rejected,
        compatibility_mode_used=False,
        mode="paper",
        deadline_violation=not success_before_deadline if topology_final_legal else False,
        topology_check_required=True,
        topology_final_legal=topology_final_legal,
        topology_reason="figure7_neighbor_map" if topology_final_legal else "figure7_non_neighbor_or_self_destination",
        topology_neighbor_map_source=FIGURE_7_SOURCE,
    )


def _cloud_task_record(
    *,
    task_id: str,
    arrival_slot: int,
    phi: int,
    completion_slot: int,
    reward_value: float | None = None,
) -> ControlledEvaluationTaskRecord:
    if not can_emit_reward("completed_cloud"):
        raise ValueError("terminal tasks in the controlled batch must be able to emit reward")
    success_before_deadline = is_success_before_deadline(completion_slot, arrival_slot, phi)
    terminal_status = terminal_status_from_completion(completion_slot, arrival_slot, phi, completion_kind="cloud")
    cloud_phi = phi_private(psi_priv=completion_slot, t=arrival_slot)
    reward_value = (
        reward_for_terminal_task(
            Task(
                task_id=int(task_id.split("-")[-1]) if task_id.split("-")[-1].isdigit() else 1,
                source_agent_id=1,
                arrival_slot=arrival_slot,
                size=1.0,
                processing_density=1.0,
                timeout_length=phi,
                absolute_deadline_slot=compute_absolute_deadline(arrival_slot, phi),
                completion_slot=completion_slot,
                terminal_outcome="completed" if success_before_deadline else "dropped",
                reward_emitted=True,
            )
        )
        if terminal_status.startswith("completed")
        else reward_from_terminal_state(True, terminal_status, None, PAPER_DROP_PENALTY)
    )
    return ControlledEvaluationTaskRecord(
        task_id=task_id,
        source_agent_id="1",
        action_type="cloud",
        destination_agent_id="cloud",
        arrival_slot=arrival_slot,
        phi=phi,
        completion_slot=completion_slot,
        terminal_status=terminal_status,
        reward_value=reward_value if reward_value is not None else reward_from_terminal_state(True, terminal_status, cloud_phi, PAPER_DROP_PENALTY),
        delay=reward_slot_for_terminal(completion_slot) - arrival_slot,
        illegal_action_rejected=False,
        compatibility_mode_used=False,
        mode="paper",
        deadline_violation=not success_before_deadline,
        topology_check_required=False,
        topology_final_legal=True,
        topology_reason="cloud_vertical_path",
        topology_neighbor_map_source="cloud_vertical_path",
    )


def _timeout_task_record(
    *,
    task_id: str,
    arrival_slot: int,
    phi: int,
    completion_slot: int,
) -> ControlledEvaluationTaskRecord:
    deadline_slot = compute_absolute_deadline(arrival_slot, phi)
    task = Task(
        task_id=int(task_id.split("-")[-1]) if task_id.split("-")[-1].isdigit() else 1,
        source_agent_id=1,
        arrival_slot=arrival_slot,
        size=1.0,
        processing_density=1.0,
        timeout_length=phi,
        absolute_deadline_slot=deadline_slot,
        completion_slot=completion_slot,
        terminal_outcome="dropped",
        reward_emitted=True,
    )
    if not can_emit_reward("dropped_timeout"):
        raise ValueError("terminal tasks in the controlled batch must be able to emit reward")
    return ControlledEvaluationTaskRecord(
        task_id=task_id,
        source_agent_id="1",
        action_type="local",
        destination_agent_id="private",
        arrival_slot=arrival_slot,
        phi=phi,
        completion_slot=completion_slot,
        terminal_status=terminal_status_from_completion(completion_slot, arrival_slot, phi, completion_kind="private"),
        reward_value=reward_from_terminal_state(True, "dropped_timeout", None, PAPER_DROP_PENALTY),
        delay=reward_slot_for_terminal(completion_slot) - arrival_slot,
        illegal_action_rejected=False,
        compatibility_mode_used=False,
        mode="paper",
        deadline_violation=has_expired(task, completion_slot),
        topology_check_required=False,
        topology_final_legal=True,
        topology_reason="local_private_execution",
        topology_neighbor_map_source="local_private_execution",
    )


def _scenario_metrics(
    *,
    completed_count: int,
    dropped_timeout_count: int,
    dropped_unavailable_count: int,
    deadline_violation_count: int,
    illegal_action_rejection_count: int,
    average_delay: float,
    average_reward: float,
    paper_mode_success_count: int,
    compatibility_mode_used: bool,
) -> ControlledEvaluationMetrics:
    return ControlledEvaluationMetrics(
        completed_count=completed_count,
        dropped_timeout_count=dropped_timeout_count,
        dropped_unavailable_count=dropped_unavailable_count,
        deadline_violation_count=deadline_violation_count,
        illegal_action_rejection_count=illegal_action_rejection_count,
        average_delay=average_delay,
        average_reward=average_reward,
        paper_mode_success_count=paper_mode_success_count,
        compatibility_mode_used=compatibility_mode_used,
    )


def compute_scenario_metrics(task_records: Sequence[ControlledEvaluationTaskRecord]) -> ControlledEvaluationMetrics:
    completed_count = sum(1 for task in task_records if task.terminal_status in {"completed_private", "completed_public", "completed_cloud"})
    dropped_timeout_count = sum(1 for task in task_records if task.terminal_status == "dropped_timeout")
    dropped_unavailable_count = sum(1 for task in task_records if task.terminal_status == "dropped_unavailable")
    deadline_violation_count = sum(1 for task in task_records if task.deadline_violation or task.terminal_status == "dropped_timeout")
    illegal_action_rejection_count = sum(1 for task in task_records if task.illegal_action_rejected)
    delay_values = [float(task.delay) for task in task_records if task.delay is not None]
    reward_values = [float(task.reward_value) for task in task_records if task.reward_value is not None and not (isinstance(task.reward_value, float) and isnan(task.reward_value))]
    average_delay = sum(delay_values) / len(delay_values) if delay_values else 0.0
    average_reward = sum(reward_values) / len(reward_values) if reward_values else 0.0
    paper_mode_success_count = sum(1 for task in task_records if task.mode == "paper" and task.terminal_status in {"completed_private", "completed_public", "completed_cloud"})
    compatibility_mode_used = any(task.compatibility_mode_used or task.mode == "compatibility" for task in task_records)
    return ControlledEvaluationMetrics(
        completed_count=completed_count,
        dropped_timeout_count=dropped_timeout_count,
        dropped_unavailable_count=dropped_unavailable_count,
        deadline_violation_count=deadline_violation_count,
        illegal_action_rejection_count=illegal_action_rejection_count,
        average_delay=average_delay,
        average_reward=average_reward,
        paper_mode_success_count=paper_mode_success_count,
        compatibility_mode_used=compatibility_mode_used,
    )


def compute_aggregate_metrics(scenarios: Sequence[ControlledEvaluationScenario]) -> ControlledEvaluationMetrics:
    all_tasks = [task for scenario in scenarios for task in scenario.tasks]
    return compute_scenario_metrics(all_tasks)


def _build_light_load_no_deadline_pressure() -> ControlledEvaluationScenario:
    task = _local_task_record(task_id="073-1", arrival_slot=2, phi=4, completion_slot=4)
    expected = _scenario_metrics(
        completed_count=1,
        dropped_timeout_count=0,
        dropped_unavailable_count=0,
        deadline_violation_count=0,
        illegal_action_rejection_count=0,
        average_delay=3.0,
        average_reward=-3.0,
        paper_mode_success_count=1,
        compatibility_mode_used=False,
    )
    actual = compute_scenario_metrics((task,))
    return ControlledEvaluationScenario(
        scenario_id="light_load_no_deadline_pressure",
        name="Light Load No Deadline Pressure",
        description="A local/private completion before the deadline succeeds in paper mode and emits the expected reward.",
        tasks=(task,),
        expected_metrics=expected,
        actual_metrics=actual,
        paper_mode_only=True,
        passed=expected == actual,
    )


def _build_tight_deadline_pressure() -> ControlledEvaluationScenario:
    task = _timeout_task_record(task_id="073-2", arrival_slot=2, phi=4, completion_slot=5)
    expected = _scenario_metrics(
        completed_count=0,
        dropped_timeout_count=1,
        dropped_unavailable_count=0,
        deadline_violation_count=1,
        illegal_action_rejection_count=0,
        average_delay=4.0,
        average_reward=-40.0,
        paper_mode_success_count=0,
        compatibility_mode_used=False,
    )
    actual = compute_scenario_metrics((task,))
    return ControlledEvaluationScenario(
        scenario_id="tight_deadline_pressure",
        name="Tight Deadline Pressure",
        description="Equality at the paper deadline must fail and produce a timeout drop.",
        tasks=(task,),
        expected_metrics=expected,
        actual_metrics=actual,
        paper_mode_only=True,
        passed=expected == actual,
    )


def _build_legal_horizontal_offload() -> ControlledEvaluationScenario:
    private_phi = phi_private(psi_priv=4, t=2)
    public_phi = phi_public(((1, 6), (0, 9)), t=2)
    selected_phi = select_phi(False, private_phi, public_phi)
    task = _horizontal_task_record(
        task_id="073-3",
        source_agent_id="1",
        destination_agent_id="6",
        arrival_slot=2,
        phi=5,
        completion_slot=5,
    )
    expected = _scenario_metrics(
        completed_count=1,
        dropped_timeout_count=0,
        dropped_unavailable_count=0,
        deadline_violation_count=0,
        illegal_action_rejection_count=0,
        average_delay=4.0,
        average_reward=-5.0,
        paper_mode_success_count=1,
        compatibility_mode_used=False,
    )
    actual = compute_scenario_metrics((task,))
    return ControlledEvaluationScenario(
        scenario_id="legal_horizontal_offload",
        name="Legal Horizontal Offload",
        description="A Figure 7 neighbor hop from 1 to 6 is legal and succeeds in paper mode.",
        tasks=(task,),
        expected_metrics=expected,
        actual_metrics=actual,
        paper_mode_only=True,
        passed=expected == actual,
    )


def _build_illegal_horizontal_destination_attempt() -> ControlledEvaluationScenario:
    task = _horizontal_task_record(
        task_id="073-4",
        source_agent_id="1",
        destination_agent_id="2",
        arrival_slot=2,
        phi=4,
        completion_slot=4,
    )
    expected = _scenario_metrics(
        completed_count=0,
        dropped_timeout_count=0,
        dropped_unavailable_count=1,
        deadline_violation_count=0,
        illegal_action_rejection_count=1,
        average_delay=3.0,
        average_reward=-40.0,
        paper_mode_success_count=0,
        compatibility_mode_used=False,
    )
    actual = compute_scenario_metrics((task,))
    return ControlledEvaluationScenario(
        scenario_id="illegal_horizontal_destination_attempt",
        name="Illegal Horizontal Destination Attempt",
        description="A non-neighbor horizontal destination is rejected and counted as unavailable.",
        tasks=(task,),
        expected_metrics=expected,
        actual_metrics=actual,
        paper_mode_only=True,
        passed=expected == actual,
    )


def _build_cloud_vertical_fallback() -> ControlledEvaluationScenario:
    task = _cloud_task_record(task_id="073-5", arrival_slot=2, phi=4, completion_slot=4)
    expected = _scenario_metrics(
        completed_count=1,
        dropped_timeout_count=0,
        dropped_unavailable_count=0,
        deadline_violation_count=0,
        illegal_action_rejection_count=0,
        average_delay=3.0,
        average_reward=-3.0,
        paper_mode_success_count=1,
        compatibility_mode_used=False,
    )
    actual = compute_scenario_metrics((task,))
    return ControlledEvaluationScenario(
        scenario_id="cloud_vertical_fallback",
        name="Cloud Vertical Fallback",
        description="Cloud execution is a vertical path and is not governed by Figure 7 horizontal adjacency.",
        tasks=(task,),
        expected_metrics=expected,
        actual_metrics=actual,
        paper_mode_only=True,
        passed=expected == actual,
    )


def _build_timeout_drop_case() -> ControlledEvaluationScenario:
    task = _timeout_task_record(task_id="073-6", arrival_slot=2, phi=4, completion_slot=6)
    expected = _scenario_metrics(
        completed_count=0,
        dropped_timeout_count=1,
        dropped_unavailable_count=0,
        deadline_violation_count=1,
        illegal_action_rejection_count=0,
        average_delay=5.0,
        average_reward=-40.0,
        paper_mode_success_count=0,
        compatibility_mode_used=False,
    )
    actual = compute_scenario_metrics((task,))
    return ControlledEvaluationScenario(
        scenario_id="timeout_drop_case",
        name="Timeout Drop Case",
        description="Completion after the paper deadline drops with the timeout penalty.",
        tasks=(task,),
        expected_metrics=expected,
        actual_metrics=actual,
        paper_mode_only=True,
        passed=expected == actual,
    )


def _build_mixed_local_horizontal_cloud_candidates() -> ControlledEvaluationScenario:
    local_task = _local_task_record(task_id="073-7a", arrival_slot=2, phi=4, completion_slot=4)
    private_phi = phi_private(psi_priv=4, t=2)
    public_phi = phi_public(((1, 6), (0, 9)), t=2)
    horizontal_task = _horizontal_task_record(
        task_id="073-7b",
        source_agent_id="1",
        destination_agent_id="6",
        arrival_slot=2,
        phi=5,
        completion_slot=5,
    )
    cloud_task = _cloud_task_record(task_id="073-7c", arrival_slot=2, phi=4, completion_slot=4)
    tasks = (local_task, horizontal_task, cloud_task)
    expected = _scenario_metrics(
        completed_count=3,
        dropped_timeout_count=0,
        dropped_unavailable_count=0,
        deadline_violation_count=0,
        illegal_action_rejection_count=0,
        average_delay=10.0 / 3.0,
        average_reward=-11.0 / 3.0,
        paper_mode_success_count=3,
        compatibility_mode_used=False,
    )
    actual = compute_scenario_metrics(tasks)
    return ControlledEvaluationScenario(
        scenario_id="mixed_local_horizontal_cloud_candidates",
        name="Mixed Local Horizontal Cloud Candidates",
        description="A deterministic batch of local, horizontal, and cloud successes confirms the aggregate metrics pipeline.",
        tasks=tasks,
        expected_metrics=expected,
        actual_metrics=actual,
        paper_mode_only=True,
        passed=expected == actual,
    )


def build_controlled_evaluation_scenarios() -> tuple[ControlledEvaluationScenario, ...]:
    return (
        _build_light_load_no_deadline_pressure(),
        _build_tight_deadline_pressure(),
        _build_legal_horizontal_offload(),
        _build_illegal_horizontal_destination_attempt(),
        _build_cloud_vertical_fallback(),
        _build_timeout_drop_case(),
        _build_mixed_local_horizontal_cloud_candidates(),
    )


def _feature_068r_regression_status() -> ControlledEvaluationRegressionEvidence:
    feature_069_report = build_feature_069_report()
    evidence = feature_069_report.feature_068r_regression_status
    return ControlledEvaluationRegressionEvidence(
        name="Feature 068R regression",
        passed=evidence.passed,
        summary="Feature 068R regression remains green and continues to satisfy the baseline policy contract.",
        validation_commands=evidence.validation_commands,
    )


def _feature_069_regression_status() -> ControlledEvaluationRegressionEvidence:
    feature_069_report = build_feature_069_report()
    return ControlledEvaluationRegressionEvidence(
        name="Feature 069 regression",
        passed=feature_069_report.passed,
        summary="Feature 069 mechanism fidelity batch remains green and reusable as regression evidence.",
        validation_commands=feature_069_report.validation_commands,
    )


def _feature_070_regression_status() -> ControlledEvaluationRegressionEvidence:
    feature_070_report = _feature_070_report()
    return ControlledEvaluationRegressionEvidence(
        name="Feature 070 regression",
        passed=feature_070_report.passed and feature_070_report.status == "blocker_resolution_readiness_with_runtime_divergence",
        summary="Feature 070 remains green, keeps runtime divergence visible, and does not claim full paper reproduction.",
        validation_commands=VALIDATION_COMMANDS[2:3],
    )


def _feature_071_regression_status() -> ControlledEvaluationRegressionEvidence:
    feature_071_report = _feature_071_report()
    return ControlledEvaluationRegressionEvidence(
        name="Feature 071 regression",
        passed=feature_071_report.passed and feature_071_report.status == "runtime_paper_faithful_semantics_alignment_ready",
        summary="Feature 071 remains green, keeps paper mode default, and preserves explicit compatibility mode.",
        validation_commands=VALIDATION_COMMANDS[3:5],
    )


def _feature_072_regression_status() -> ControlledEvaluationRegressionEvidence:
    feature_072_report = _feature_072_report()
    return ControlledEvaluationRegressionEvidence(
        name="Feature 072 regression",
        passed=feature_072_report.passed and feature_072_report.status == "end_to_end_golden_trace_validation_ready",
        summary="Feature 072 golden trace validation remains green and its independent expected/actual trace contract is consumed here.",
        validation_commands=VALIDATION_COMMANDS[5:7],
    )


def _batch_report_claim_boundary() -> str:
    return (
        "No final evaluation claim is made. No performance superiority claim is made. No full paper reproduction claim "
        "is made. This layer only proves controlled evaluation batch readiness with paper-mode default semantics, "
        "compatibility mode is excluded from the default batch, and deterministic batch metrics. Horizontal legality is computed from "
        "Feature 070 Figure 7 neighbor map. Local/private metrics are computed from Feature 071 helpers. Cloud "
        "terminal status respects paper-mode deadline semantics. Feature 074 is the next comparative baseline "
        "evaluation readiness step."
    )


def build_feature_073_report(
    changed_files: Sequence[str] | None = None,
    validation_commands: Sequence[str] | None = None,
) -> ControlledEvaluationBatchReport:
    checked_changed_files = tuple(validate_scope(DEFAULT_CHANGED_FILES if changed_files is None else changed_files))
    scenarios = build_controlled_evaluation_scenarios()
    aggregate_metrics = compute_aggregate_metrics(scenarios)
    regression_068r = _feature_068r_regression_status()
    regression_069 = _feature_069_regression_status()
    regression_070 = _feature_070_regression_status()
    regression_071 = _feature_071_regression_status()
    regression_072 = _feature_072_regression_status()
    passed = bool(
        scenarios
        and all(scenario.passed for scenario in scenarios)
        and not aggregate_metrics.compatibility_mode_used
        and regression_068r.passed
        and regression_069.passed
        and regression_070.passed
        and regression_071.passed
        and regression_072.passed
    )
    status = FEATURE_073_STATUS_READY if passed else FEATURE_073_STATUS_WITH_BLOCKERS
    return ControlledEvaluationBatchReport(
        feature_name="Feature 073 - Controlled Evaluation Batch Readiness",
        status=status,
        passed=passed,
        changed_files=checked_changed_files,
        scenarios=scenarios,
        aggregate_metrics=aggregate_metrics,
        feature_068r_regression_status=regression_068r,
        feature_069_regression_status=regression_069,
        feature_070_regression_status=regression_070,
        feature_071_regression_status=regression_071,
        feature_072_regression_status=regression_072,
        paper_claim_boundary=_batch_report_claim_boundary(),
        recommended_next_feature=FEATURE_074_RECOMMENDATION,
    )


def render_feature_073_report(report: ControlledEvaluationBatchReport) -> str:
    payload = report.to_dict()
    scenario_sections = []
    for scenario in payload["scenarios"]:
        scenario_sections.append(
            "\n".join(
                [
                    f"### {scenario['scenario_id']}",
                    _json_dump(scenario).rstrip(),
                ]
            )
        )
    regression_sections = []
    for name in (
        "feature_068r_regression_status",
        "feature_069_regression_status",
        "feature_070_regression_status",
        "feature_071_regression_status",
        "feature_072_regression_status",
    ):
        regression_sections.append(f"### {payload[name]['name']}\n{_json_dump(payload[name]).rstrip()}")
    return "\n".join(
        [
            "# Feature 073 Controlled Evaluation Batch Readiness Report",
            "",
            f"- feature_name: `{payload['feature_name']}`",
            f"- status: `{payload['status']}`",
            f"- passed: `{payload['passed']}`",
            f"- recommended_next_feature: {payload['recommended_next_feature']}",
            "",
            "## Claim Boundary",
            payload["paper_claim_boundary"],
            "",
            "## Prerequisite Evidence",
            "Feature 072 report is consumed here to verify deterministic golden trace readiness before the batch layer is built.",
            "Expected outputs are independent scenario constants.",
            "Actual outputs are computed from Feature 070 and Feature 071 helpers.",
            "Horizontal legality is computed from Feature 070 Figure 7 neighbor map.",
            "Local/private metrics are computed from Feature 071 helpers.",
            "Cloud terminal status respects paper-mode deadline semantics.",
            "Compatibility mode is excluded from the default batch.",
            "",
            "## Aggregate Metrics",
            _json_dump(payload["aggregate_metrics"]).rstrip(),
            "",
            "## Scenarios",
            *scenario_sections,
            "",
            "## Regression Evidence",
            *regression_sections,
            "",
        ]
    )


def write_feature_073_report(output_dir: Path | str = DEFAULT_OUTPUT_DIR) -> Path:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    report = build_feature_073_report()
    markdown_path = output_path / "feature-073-controlled-evaluation-batch-readiness-report.md"
    json_path = output_path / "feature-073-controlled-evaluation-batch-readiness-report.json"
    markdown_path.write_text(render_feature_073_report(report), encoding="utf-8")
    json_path.write_text(_json_dump(report.to_dict()), encoding="utf-8")
    return markdown_path
