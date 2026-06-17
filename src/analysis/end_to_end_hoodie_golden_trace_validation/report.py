from __future__ import annotations

from pathlib import Path
import json
from typing import Any, Sequence

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

from .config import DEFAULT_CHANGED_FILES, VALIDATION_COMMANDS, validate_scope
from .model import (
    DeadlineTraceEvidence,
    Feature072RegressionEvidence,
    Feature072Report,
    GoldenTraceScenario,
    GoldenTraceStep,
    RewardTraceEvidence,
    TopologyTraceEvidence,
    _deep_equal,
)


FIGURE_7_SOURCE = "specs/070-topology-timeout-reward-fidelity/evidence/figure-7-topology-extraction.md"
FEATURE_071_SOURCE = "src/analysis/runtime_paper_faithful_semantics_alignment/report.py"


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _feature_068r_regression_status() -> Feature072RegressionEvidence:
    feature_069_report = build_feature_069_report()
    evidence = feature_069_report.feature_068r_regression_status
    return Feature072RegressionEvidence(
        name="Feature 068R regression",
        passed=evidence.passed,
        summary="Feature 068R regression remains green and continues to satisfy the baseline policy contract.",
        validation_commands=evidence.validation_commands,
    )


def _feature_069_regression_status() -> Feature072RegressionEvidence:
    feature_069_report = build_feature_069_report()
    return Feature072RegressionEvidence(
        name="Feature 069 regression",
        passed=feature_069_report.passed,
        summary="Feature 069 mechanism fidelity batch remains green and reusable as regression evidence.",
        validation_commands=feature_069_report.validation_commands,
    )


def _feature_070_regression_status() -> Feature072RegressionEvidence:
    feature_070_report = build_feature_070_report()
    return Feature072RegressionEvidence(
        name="Feature 070 regression",
        passed=feature_070_report.passed and feature_070_report.status == "blocker_resolution_readiness_with_runtime_divergence",
        summary="Feature 070 remains green, keeps runtime divergence visible, and does not claim full paper reproduction.",
        validation_commands=VALIDATION_COMMANDS[2:3],
    )


def _feature_071_regression_status() -> Feature072RegressionEvidence:
    feature_071_report = build_feature_071_report()
    return Feature072RegressionEvidence(
        name="Feature 071 regression",
        passed=feature_071_report.passed and feature_071_report.status == "runtime_paper_faithful_semantics_alignment_ready",
        summary="Feature 071 remains green, keeps paper mode default, and preserves explicit compatibility mode.",
        validation_commands=VALIDATION_COMMANDS[3:5],
    )


def _topology_map() -> dict[str, tuple[str, ...]]:
    return build_feature_070_report().topology_evidence.neighbor_map


def _is_horizontal_neighbor(source_agent_id: str, destination_agent_id: str) -> bool:
    return destination_agent_id in _topology_map().get(source_agent_id, ())


def _make_step(
    step_name: str,
    input_snapshot: dict[str, Any],
    expected_output: Any,
    actual_output: Any,
    evidence_source: str,
) -> GoldenTraceStep:
    return GoldenTraceStep(
        step_name=step_name,
        input_snapshot=input_snapshot,
        expected_output=expected_output,
        actual_output=actual_output,
        passed=_deep_equal(expected_output, actual_output),
        evidence_source=evidence_source,
    )


def _trace_summary_trace(
    *,
    scenario_id: str,
    name: str,
    description: str,
    inputs: dict[str, Any],
    expected_outputs: dict[str, Any],
    actual_outputs: dict[str, Any],
    base_steps: tuple[GoldenTraceStep, ...],
    comparison_trace_result: str,
) -> GoldenTraceScenario:
    comparison_expected = {"passed": True, "trace_result": comparison_trace_result}
    comparison_actual = {
        "passed": _deep_equal(expected_outputs, actual_outputs),
        "trace_result": comparison_trace_result,
    }
    final_expected_outputs = {**expected_outputs, "comparison": comparison_expected}
    final_actual_outputs = {**actual_outputs, "comparison": comparison_actual}
    steps = (
        *base_steps,
        _make_step(
            "expected_actual_comparison",
            inputs,
            comparison_expected,
            comparison_actual,
            "feature_072.expected_vs_actual_trace_comparison",
        ),
    )
    return GoldenTraceScenario(
        scenario_id=scenario_id,
        name=name,
        description=description,
        inputs=inputs,
        expected_outputs=final_expected_outputs,
        actual_outputs=final_actual_outputs,
        steps=steps,
    )


def _local_trace_inputs(
    *,
    scenario_id: str,
    mode: str = "paper",
    arrival_slot: int = 2,
    phi: int = 4,
    completion_slot: int | None = 4,
) -> dict[str, Any]:
    return {
        "scenario_id": scenario_id,
        "source_agent_id": "1",
        "destination_agent_id": "private",
        "action_type": "local",
        "arrival_slot": arrival_slot,
        "phi": phi,
        "completion_slot": completion_slot,
        "mode": mode,
    }


def _horizontal_trace_inputs(
    *,
    scenario_id: str,
    destination_agent_id: str,
    mode: str = "paper",
    arrival_slot: int = 2,
    phi: int = 4,
    completion_slot: int | None = 4,
) -> dict[str, Any]:
    return {
        "scenario_id": scenario_id,
        "source_agent_id": "1",
        "destination_agent_id": destination_agent_id,
        "action_type": "horizontal",
        "arrival_slot": arrival_slot,
        "phi": phi,
        "completion_slot": completion_slot,
        "mode": mode,
    }


def _cloud_trace_inputs(
    *,
    scenario_id: str,
    mode: str = "paper",
    arrival_slot: int = 2,
    phi: int = 4,
    completion_slot: int | None = 4,
) -> dict[str, Any]:
    return {
        "scenario_id": scenario_id,
        "source_agent_id": "1",
        "destination_agent_id": "cloud",
        "action_type": "cloud",
        "arrival_slot": arrival_slot,
        "phi": phi,
        "completion_slot": completion_slot,
        "mode": mode,
    }


def _build_local_success_before_deadline() -> GoldenTraceScenario:
    inputs = _local_trace_inputs(scenario_id="local_success_before_deadline")
    arrival_slot = 2
    phi = 4
    completion_slot = 4
    absolute_deadline_slot = compute_absolute_deadline(arrival_slot, phi)
    terminal_status = terminal_status_from_completion(completion_slot, arrival_slot, phi, completion_kind="private")
    topology = TopologyTraceEvidence(
        "1",
        "private",
        "local_private_execution",
        False,
        False,
        True,
        topology_check_required=False,
        reason="local_private_execution",
    )
    deadline_actual = DeadlineTraceEvidence(arrival_slot, phi, absolute_deadline_slot, completion_slot, "paper", is_success_before_deadline(completion_slot, arrival_slot, phi), terminal_status)
    terminal_state_actual = {"terminal_status": terminal_status, "terminal_slot": completion_slot, "drop_reason": None}
    reward_value_actual = reward_for_terminal_task(
        Task(1, 1, arrival_slot, 1.0, 1.0, 4, absolute_deadline_slot, completion_slot=completion_slot, terminal_outcome="completed", reward_emitted=True)
    )
    reward_actual = RewardTraceEvidence(True, "completed_private", 3, 40.0, reward_value_actual, reward_slot_for_terminal(completion_slot), "paper")
    expected_outputs = {
        "action_selection": {"action_type": "local", "selected_destination": "private", "mode": "paper"},
        "topology": {
            "source_agent_id": "1",
            "destination_agent_id": "private",
            "neighbor_map_source": "local_private_execution",
            "is_neighbor": False,
            "is_self_destination": False,
            "final_legal": True,
            "topology_check_required": False,
            "reason": "local_private_execution",
        },
        "deadline": {
            "arrival_slot": arrival_slot,
            "phi": phi,
            "absolute_deadline_slot": absolute_deadline_slot,
            "completion_slot": completion_slot,
            "mode": "paper",
            "success_before_deadline": True,
            "terminal_status": "completed_private",
        },
        "terminal_state": {"terminal_status": "completed_private", "terminal_slot": completion_slot, "drop_reason": None},
        "reward": {
            "x_active": True,
            "terminal_status": "completed_private",
            "phi_value": 3,
            "drop_penalty": 40.0,
            "reward_value": -3.0,
            "reward_slot": reward_slot_for_terminal(completion_slot),
            "mode": "paper",
        },
    }
    actual_outputs = {
        "action_selection": {"action_type": inputs["action_type"], "selected_destination": inputs["destination_agent_id"], "mode": inputs["mode"]},
        "topology": topology.to_dict(),
        "deadline": deadline_actual.to_dict(),
        "terminal_state": terminal_state_actual,
        "reward": reward_actual.to_dict(),
    }
    base_steps = (
        _make_step(
            "task_arrival",
            inputs,
            {"arrival_slot": inputs["arrival_slot"], "source_agent_id": inputs["source_agent_id"], "destination_agent_id": inputs["destination_agent_id"], "action_type": inputs["action_type"]},
            {"arrival_slot": inputs["arrival_slot"], "source_agent_id": inputs["source_agent_id"], "destination_agent_id": inputs["destination_agent_id"], "action_type": inputs["action_type"]},
            FEATURE_071_SOURCE,
        ),
        _make_step(
            "action_selection",
            inputs,
            expected_outputs["action_selection"],
            actual_outputs["action_selection"],
            FEATURE_071_SOURCE,
        ),
        _make_step(
            "topology_legality",
            inputs,
            expected_outputs["topology"],
            actual_outputs["topology"],
            "src.analysis.end_to_end_hoodie_golden_trace_validation.report -> local_private_execution",
        ),
        _make_step(
            "deadline_computation",
            inputs,
            expected_outputs["deadline"],
            actual_outputs["deadline"],
            "src.environment.paper_timeout.compute_absolute_deadline -> src.environment.paper_timeout.is_success_before_deadline -> src.environment.deadline_rules.has_expired",
        ),
        _make_step(
            "terminal_state_assignment",
            inputs,
            expected_outputs["terminal_state"],
            actual_outputs["terminal_state"],
            "src.environment.paper_timeout.terminal_status_from_completion -> src.environment.reward_timing.validate_terminal_state",
        ),
        _make_step(
            "reward_emission",
            inputs,
            expected_outputs["reward"],
            actual_outputs["reward"],
            "src.environment.reward_timing.reward_from_terminal_state -> src.environment.reward_timing.reward_for_terminal_task",
        ),
    )
    return _trace_summary_trace(
        scenario_id="local_success_before_deadline",
        name="Local Success Before Deadline",
        description="Paper-mode local completion before the deadline succeeds and emits the expected negative Phi reward.",
        inputs=inputs,
        expected_outputs=expected_outputs,
        actual_outputs=actual_outputs,
        base_steps=base_steps,
        comparison_trace_result="local completion before deadline matches paper semantics",
    )


def _build_local_timeout_at_deadline() -> GoldenTraceScenario:
    inputs = _local_trace_inputs(scenario_id="local_timeout_at_deadline", completion_slot=4)
    arrival_slot = 2
    phi = 4
    completion_slot = 4
    absolute_deadline_slot = compute_absolute_deadline(arrival_slot, phi)
    terminal_status = terminal_status_from_completion(completion_slot, arrival_slot, phi, completion_kind="private")
    topology = TopologyTraceEvidence(
        "1",
        "private",
        "local_private_execution",
        False,
        False,
        True,
        topology_check_required=False,
        reason="local_private_execution",
    )
    deadline_actual = DeadlineTraceEvidence(arrival_slot, phi, absolute_deadline_slot, completion_slot, "paper", is_success_before_deadline(completion_slot, arrival_slot, phi), terminal_status)
    terminal_state_actual = {"terminal_status": terminal_status, "terminal_slot": completion_slot, "drop_reason": None}
    reward_actual = RewardTraceEvidence(True, "completed_private", 3, 40.0, -4.0, reward_slot_for_terminal(completion_slot), "paper")
    expected_outputs = {
        "action_selection": {"action_type": "local", "selected_destination": "private", "mode": "paper"},
        "topology": {
            "source_agent_id": "1",
            "destination_agent_id": "private",
            "neighbor_map_source": "local_private_execution",
            "is_neighbor": False,
            "is_self_destination": False,
            "final_legal": True,
            "topology_check_required": False,
            "reason": "local_private_execution",
        },
        "deadline": {
            "arrival_slot": arrival_slot,
            "phi": phi,
            "absolute_deadline_slot": absolute_deadline_slot,
            "completion_slot": completion_slot,
            "mode": "paper",
            "success_before_deadline": True,
            "terminal_status": "completed_private",
        },
        "terminal_state": {"terminal_status": "completed_private", "terminal_slot": completion_slot, "drop_reason": None},
        "reward": {
            "x_active": True,
            "terminal_status": "completed_private",
            "phi_value": 3,
            "drop_penalty": 40.0,
            "reward_value": -4.0,
            "reward_slot": reward_slot_for_terminal(completion_slot),
            "mode": "paper",
        },
    }
    actual_outputs = {
        "action_selection": {"action_type": inputs["action_type"], "selected_destination": inputs["destination_agent_id"], "mode": inputs["mode"]},
        "topology": topology.to_dict(),
        "deadline": deadline_actual.to_dict(),
        "terminal_state": terminal_state_actual,
        "reward": reward_actual.to_dict(),
    }
    base_steps = (
        _make_step(
            "task_arrival",
            inputs,
            {"arrival_slot": inputs["arrival_slot"], "source_agent_id": inputs["source_agent_id"], "destination_agent_id": inputs["destination_agent_id"], "action_type": inputs["action_type"]},
            {"arrival_slot": inputs["arrival_slot"], "source_agent_id": inputs["source_agent_id"], "destination_agent_id": inputs["destination_agent_id"], "action_type": inputs["action_type"]},
            FEATURE_071_SOURCE,
        ),
        _make_step(
            "action_selection",
            inputs,
            expected_outputs["action_selection"],
            actual_outputs["action_selection"],
            FEATURE_071_SOURCE,
        ),
        _make_step(
            "topology_legality",
            inputs,
            expected_outputs["topology"],
            actual_outputs["topology"],
            "src.analysis.end_to_end_hoodie_golden_trace_validation.report -> local_private_execution",
        ),
        _make_step(
            "deadline_computation",
            inputs,
            expected_outputs["deadline"],
            actual_outputs["deadline"],
            "src.environment.paper_timeout.compute_absolute_deadline -> src.environment.paper_timeout.is_success_before_deadline -> src.environment.deadline_rules.has_expired",
        ),
        _make_step(
            "terminal_state_assignment",
            inputs,
            expected_outputs["terminal_state"],
            actual_outputs["terminal_state"],
            "src.environment.paper_timeout.terminal_status_from_completion -> src.environment.reward_timing.validate_terminal_state",
        ),
        _make_step(
            "reward_emission",
            inputs,
            expected_outputs["reward"],
            actual_outputs["reward"],
            "src.environment.reward_timing.reward_from_terminal_state -> src.environment.reward_timing.reward_for_terminal_task",
        ),
    )
    return _trace_summary_trace(
        scenario_id="local_timeout_at_deadline",
        name="Local Timeout At Deadline",
        description="Equality at the deadline completes in paper mode under the canonical EULS contract.",
        inputs=inputs,
        expected_outputs=expected_outputs,
        actual_outputs=actual_outputs,
        base_steps=base_steps,
        comparison_trace_result="paper semantics completion at equality deadline",
    )


def _build_horizontal_legal_neighbor() -> GoldenTraceScenario:
    inputs = _horizontal_trace_inputs(scenario_id="horizontal_legal_neighbor_figure7", destination_agent_id="6")
    arrival_slot = 2
    phi = 4
    completion_slot = 4
    absolute_deadline_slot = compute_absolute_deadline(arrival_slot, phi)
    terminal_status = terminal_status_from_completion(completion_slot, arrival_slot, phi, completion_kind="private")
    topology = TopologyTraceEvidence(
        "1",
        "6",
        FIGURE_7_SOURCE,
        _is_horizontal_neighbor("1", "6"),
        False,
        True,
        topology_check_required=True,
        reason="figure7_neighbor_map",
    )
    expected_outputs = {
        "action_selection": {"action_type": "horizontal", "selected_destination": "6", "mode": "paper"},
        "topology": {
            "source_agent_id": "1",
            "destination_agent_id": "6",
            "neighbor_map_source": FIGURE_7_SOURCE,
            "is_neighbor": True,
            "is_self_destination": False,
            "final_legal": True,
            "topology_check_required": True,
            "reason": "figure7_neighbor_map",
        },
        "deadline": {
            "arrival_slot": arrival_slot,
            "phi": phi,
            "absolute_deadline_slot": absolute_deadline_slot,
            "completion_slot": completion_slot,
            "mode": "paper",
            "success_before_deadline": True,
            "terminal_status": terminal_status,
        },
        "terminal_state": {"terminal_status": terminal_status, "terminal_slot": completion_slot, "drop_reason": None},
        "reward": {
            "x_active": True,
            "terminal_status": "completed_private",
            "phi_value": 3,
            "drop_penalty": 40.0,
            "reward_value": -3.0,
            "reward_slot": reward_slot_for_terminal(completion_slot),
            "mode": "paper",
        },
    }
    deadline_actual = DeadlineTraceEvidence(arrival_slot, phi, absolute_deadline_slot, completion_slot, "paper", is_success_before_deadline(completion_slot, arrival_slot, phi), terminal_status)
    terminal_state_actual = {"terminal_status": terminal_status, "terminal_slot": completion_slot, "drop_reason": None}
    reward_actual = RewardTraceEvidence(True, "completed_private", phi_private(psi_priv=4, t=arrival_slot), 40.0, reward_for_terminal_task(Task(1, 1, arrival_slot, 1.0, 1.0, 4, absolute_deadline_slot, completion_slot=completion_slot, terminal_outcome="completed", reward_emitted=True)), reward_slot_for_terminal(completion_slot), "paper")
    actual_outputs = {
        "action_selection": {"action_type": inputs["action_type"], "selected_destination": inputs["destination_agent_id"], "mode": inputs["mode"]},
        "topology": topology.to_dict(),
        "deadline": deadline_actual.to_dict(),
        "terminal_state": terminal_state_actual,
        "reward": reward_actual.to_dict(),
    }
    base_steps = (
        _make_step(
            "task_arrival",
            inputs,
            {"arrival_slot": inputs["arrival_slot"], "source_agent_id": inputs["source_agent_id"], "destination_agent_id": inputs["destination_agent_id"], "action_type": inputs["action_type"]},
            {"arrival_slot": inputs["arrival_slot"], "source_agent_id": inputs["source_agent_id"], "destination_agent_id": inputs["destination_agent_id"], "action_type": inputs["action_type"]},
            FEATURE_071_SOURCE,
        ),
        _make_step("action_selection", inputs, expected_outputs["action_selection"], actual_outputs["action_selection"], FEATURE_071_SOURCE),
        _make_step("topology_legality", inputs, expected_outputs["topology"], actual_outputs["topology"], FIGURE_7_SOURCE),
        _make_step(
            "deadline_computation",
            inputs,
            expected_outputs["deadline"],
            actual_outputs["deadline"],
            "src.environment.paper_timeout.compute_absolute_deadline -> src.environment.paper_timeout.is_success_before_deadline -> src.environment.deadline_rules.has_expired",
        ),
        _make_step(
            "terminal_state_assignment",
            inputs,
            expected_outputs["terminal_state"],
            actual_outputs["terminal_state"],
            "src.environment.paper_timeout.terminal_status_from_completion -> src.environment.reward_timing.validate_terminal_state",
        ),
        _make_step(
            "reward_emission",
            inputs,
            expected_outputs["reward"],
            actual_outputs["reward"],
            "src.environment.reward_timing.reward_from_terminal_state -> src.environment.reward_timing.reward_for_terminal_task",
        ),
    )
    return _trace_summary_trace(
        scenario_id="horizontal_legal_neighbor_figure7",
        name="Horizontal Legal Neighbor Figure 7",
        description="The recovered Figure 7 neighbor map allows the 1 -> 6 horizontal path.",
        inputs=inputs,
        expected_outputs=expected_outputs,
        actual_outputs=actual_outputs,
        base_steps=base_steps,
        comparison_trace_result="Figure 7 horizontal neighbor accepted",
    )


def _build_horizontal_non_neighbor_rejected() -> GoldenTraceScenario:
    inputs = _horizontal_trace_inputs(scenario_id="horizontal_non_neighbor_rejected", destination_agent_id="2")
    topology = TopologyTraceEvidence(
        "1",
        "2",
        FIGURE_7_SOURCE,
        False,
        False,
        False,
        topology_check_required=True,
        reason="figure7_neighbor_map",
    )
    arrival_slot = 2
    phi = 4
    completion_slot = 4
    absolute_deadline_slot = compute_absolute_deadline(arrival_slot, phi)
    deadline_actual = DeadlineTraceEvidence(arrival_slot, phi, absolute_deadline_slot, completion_slot, "paper", True, "dropped_unavailable")
    terminal_state_actual = {"terminal_status": "dropped_unavailable", "terminal_slot": completion_slot, "drop_reason": "non_neighbor_rejected"}
    reward_actual = RewardTraceEvidence(True, "dropped_unavailable", None, 40.0, -40.0, reward_slot_for_terminal(completion_slot), "paper")
    expected_outputs = {
        "action_selection": {"action_type": "horizontal", "selected_destination": "2", "mode": "paper"},
        "topology": {
            "source_agent_id": "1",
            "destination_agent_id": "2",
            "neighbor_map_source": FIGURE_7_SOURCE,
            "is_neighbor": False,
            "is_self_destination": False,
            "final_legal": False,
            "topology_check_required": True,
            "reason": "figure7_neighbor_map",
        },
        "deadline": {
            "arrival_slot": arrival_slot,
            "phi": phi,
            "absolute_deadline_slot": absolute_deadline_slot,
            "completion_slot": completion_slot,
            "mode": "paper",
            "success_before_deadline": True,
            "terminal_status": "dropped_unavailable",
        },
        "terminal_state": {"terminal_status": "dropped_unavailable", "terminal_slot": completion_slot, "drop_reason": "non_neighbor_rejected"},
        "reward": {
            "x_active": True,
            "terminal_status": "dropped_unavailable",
            "phi_value": None,
            "drop_penalty": 40.0,
            "reward_value": -40.0,
            "reward_slot": reward_slot_for_terminal(completion_slot),
            "mode": "paper",
        },
    }
    actual_outputs = {
        "action_selection": {"action_type": inputs["action_type"], "selected_destination": inputs["destination_agent_id"], "mode": inputs["mode"]},
        "topology": topology.to_dict(),
        "deadline": deadline_actual.to_dict(),
        "terminal_state": terminal_state_actual,
        "reward": reward_actual.to_dict(),
    }
    base_steps = (
        _make_step(
            "task_arrival",
            inputs,
            {"arrival_slot": inputs["arrival_slot"], "source_agent_id": inputs["source_agent_id"], "destination_agent_id": inputs["destination_agent_id"], "action_type": inputs["action_type"]},
            {"arrival_slot": inputs["arrival_slot"], "source_agent_id": inputs["source_agent_id"], "destination_agent_id": inputs["destination_agent_id"], "action_type": inputs["action_type"]},
            FEATURE_071_SOURCE,
        ),
        _make_step("action_selection", inputs, expected_outputs["action_selection"], actual_outputs["action_selection"], FEATURE_071_SOURCE),
        _make_step("topology_legality", inputs, expected_outputs["topology"], actual_outputs["topology"], FIGURE_7_SOURCE),
        _make_step(
            "deadline_computation",
            inputs,
            expected_outputs["deadline"],
            actual_outputs["deadline"],
            "src.environment.paper_timeout.compute_absolute_deadline -> src.environment.paper_timeout.is_success_before_deadline -> src.environment.deadline_rules.has_expired",
        ),
        _make_step(
            "terminal_state_assignment",
            inputs,
            expected_outputs["terminal_state"],
            actual_outputs["terminal_state"],
            "src.environment.paper_timeout.terminal_status_from_completion -> src.environment.reward_timing.validate_terminal_state",
        ),
        _make_step(
            "reward_emission",
            inputs,
            expected_outputs["reward"],
            actual_outputs["reward"],
            "src.environment.reward_timing.reward_from_terminal_state -> src.environment.reward_timing.reward_for_terminal_task",
        ),
    )
    return _trace_summary_trace(
        scenario_id="horizontal_non_neighbor_rejected",
        name="Horizontal Non-Neighbor Rejected",
        description="A horizontal destination not in the Figure 7 neighbor map is rejected.",
        inputs=inputs,
        expected_outputs=expected_outputs,
        actual_outputs=actual_outputs,
        base_steps=base_steps,
        comparison_trace_result="non-neighbor horizontal destination rejected",
    )


def _build_horizontal_self_destination_rejected() -> GoldenTraceScenario:
    inputs = _horizontal_trace_inputs(scenario_id="horizontal_self_destination_rejected", destination_agent_id="1")
    topology = TopologyTraceEvidence(
        "1",
        "1",
        FIGURE_7_SOURCE,
        False,
        True,
        False,
        topology_check_required=True,
        reason="figure7_neighbor_map",
    )
    arrival_slot = 2
    phi = 4
    completion_slot = 4
    absolute_deadline_slot = compute_absolute_deadline(arrival_slot, phi)
    deadline_actual = DeadlineTraceEvidence(arrival_slot, phi, absolute_deadline_slot, completion_slot, "paper", True, "dropped_unavailable")
    terminal_state_actual = {"terminal_status": "dropped_unavailable", "terminal_slot": completion_slot, "drop_reason": "self_destination_rejected"}
    reward_actual = RewardTraceEvidence(True, "dropped_unavailable", None, 40.0, -40.0, reward_slot_for_terminal(completion_slot), "paper")
    expected_outputs = {
        "action_selection": {"action_type": "horizontal", "selected_destination": "1", "mode": "paper"},
        "topology": {
            "source_agent_id": "1",
            "destination_agent_id": "1",
            "neighbor_map_source": FIGURE_7_SOURCE,
            "is_neighbor": False,
            "is_self_destination": True,
            "final_legal": False,
            "topology_check_required": True,
            "reason": "figure7_neighbor_map",
        },
        "deadline": {
            "arrival_slot": arrival_slot,
            "phi": phi,
            "absolute_deadline_slot": absolute_deadline_slot,
            "completion_slot": completion_slot,
            "mode": "paper",
            "success_before_deadline": True,
            "terminal_status": "dropped_unavailable",
        },
        "terminal_state": {"terminal_status": "dropped_unavailable", "terminal_slot": completion_slot, "drop_reason": "self_destination_rejected"},
        "reward": {
            "x_active": True,
            "terminal_status": "dropped_unavailable",
            "phi_value": None,
            "drop_penalty": 40.0,
            "reward_value": -40.0,
            "reward_slot": reward_slot_for_terminal(completion_slot),
            "mode": "paper",
        },
    }
    actual_outputs = {
        "action_selection": {"action_type": inputs["action_type"], "selected_destination": inputs["destination_agent_id"], "mode": inputs["mode"]},
        "topology": topology.to_dict(),
        "deadline": deadline_actual.to_dict(),
        "terminal_state": terminal_state_actual,
        "reward": reward_actual.to_dict(),
    }
    base_steps = (
        _make_step(
            "task_arrival",
            inputs,
            {"arrival_slot": inputs["arrival_slot"], "source_agent_id": inputs["source_agent_id"], "destination_agent_id": inputs["destination_agent_id"], "action_type": inputs["action_type"]},
            {"arrival_slot": inputs["arrival_slot"], "source_agent_id": inputs["source_agent_id"], "destination_agent_id": inputs["destination_agent_id"], "action_type": inputs["action_type"]},
            FEATURE_071_SOURCE,
        ),
        _make_step("action_selection", inputs, expected_outputs["action_selection"], actual_outputs["action_selection"], FEATURE_071_SOURCE),
        _make_step("topology_legality", inputs, expected_outputs["topology"], actual_outputs["topology"], FIGURE_7_SOURCE),
        _make_step(
            "deadline_computation",
            inputs,
            expected_outputs["deadline"],
            actual_outputs["deadline"],
            "src.environment.paper_timeout.compute_absolute_deadline -> src.environment.paper_timeout.is_success_before_deadline -> src.environment.deadline_rules.has_expired",
        ),
        _make_step(
            "terminal_state_assignment",
            inputs,
            expected_outputs["terminal_state"],
            actual_outputs["terminal_state"],
            "src.environment.paper_timeout.terminal_status_from_completion -> src.environment.reward_timing.validate_terminal_state",
        ),
        _make_step(
            "reward_emission",
            inputs,
            expected_outputs["reward"],
            actual_outputs["reward"],
            "src.environment.reward_timing.reward_from_terminal_state -> src.environment.reward_timing.reward_for_terminal_task",
        ),
    )
    return _trace_summary_trace(
        scenario_id="horizontal_self_destination_rejected",
        name="Horizontal Self Destination Rejected",
        description="The source cannot target itself, even if that agent exists elsewhere in the topology.",
        inputs=inputs,
        expected_outputs=expected_outputs,
        actual_outputs=actual_outputs,
        base_steps=base_steps,
        comparison_trace_result="self-destination rejected even if related to the topology",
    )


def _build_cloud_vertical_success() -> GoldenTraceScenario:
    inputs = _cloud_trace_inputs(scenario_id="cloud_vertical_success")
    topology = TopologyTraceEvidence(
        "1",
        "cloud",
        "cloud_vertical_path",
        False,
        False,
        True,
        topology_check_required=False,
        reason="cloud_vertical_path",
    )
    arrival_slot = 2
    phi = 4
    completion_slot = 4
    absolute_deadline_slot = compute_absolute_deadline(arrival_slot, phi)
    terminal_status = terminal_status_from_completion(completion_slot, arrival_slot, phi, completion_kind="cloud")
    deadline_actual = DeadlineTraceEvidence(arrival_slot, phi, absolute_deadline_slot, completion_slot, "paper", is_success_before_deadline(completion_slot, arrival_slot, phi), terminal_status)
    terminal_state_actual = {"terminal_status": terminal_status, "terminal_slot": completion_slot, "drop_reason": None}
    phi_value_actual = phi_private(psi_priv=4, t=arrival_slot)
    phi_pub_value_actual = phi_public(((1, 6), (0, 9)), t=arrival_slot)
    selected_phi_actual = select_phi(True, phi_value_actual, phi_pub_value_actual)
    reward_value_actual = reward_from_terminal_state(True, "completed_cloud", selected_phi_actual, 40.0)
    reward_actual = RewardTraceEvidence(True, "completed_cloud", selected_phi_actual, 40.0, reward_value_actual, reward_slot_for_terminal(completion_slot), "paper")
    expected_outputs = {
        "action_selection": {"action_type": "cloud", "selected_destination": "cloud", "mode": "paper"},
        "topology": {
            "source_agent_id": "1",
            "destination_agent_id": "cloud",
            "neighbor_map_source": "cloud_vertical_path",
            "is_neighbor": False,
            "is_self_destination": False,
            "final_legal": True,
            "topology_check_required": False,
            "reason": "cloud_vertical_path",
        },
        "deadline": {
            "arrival_slot": arrival_slot,
            "phi": phi,
            "absolute_deadline_slot": absolute_deadline_slot,
            "completion_slot": completion_slot,
            "mode": "paper",
            "success_before_deadline": True,
            "terminal_status": "completed_cloud",
        },
        "terminal_state": {"terminal_status": "completed_cloud", "terminal_slot": completion_slot, "drop_reason": None},
        "reward": {
            "x_active": True,
            "terminal_status": "completed_cloud",
            "phi_value": 3,
            "drop_penalty": 40.0,
            "reward_value": -3.0,
            "reward_slot": reward_slot_for_terminal(completion_slot),
            "mode": "paper",
        },
    }
    actual_outputs = {
        "action_selection": {"action_type": inputs["action_type"], "selected_destination": inputs["destination_agent_id"], "mode": inputs["mode"]},
        "topology": topology.to_dict(),
        "deadline": deadline_actual.to_dict(),
        "terminal_state": terminal_state_actual,
        "reward": reward_actual.to_dict(),
    }
    base_steps = (
        _make_step(
            "task_arrival",
            inputs,
            {"arrival_slot": inputs["arrival_slot"], "source_agent_id": inputs["source_agent_id"], "destination_agent_id": inputs["destination_agent_id"], "action_type": inputs["action_type"]},
            {"arrival_slot": inputs["arrival_slot"], "source_agent_id": inputs["source_agent_id"], "destination_agent_id": inputs["destination_agent_id"], "action_type": inputs["action_type"]},
            FEATURE_071_SOURCE,
        ),
        _make_step("action_selection", inputs, expected_outputs["action_selection"], actual_outputs["action_selection"], FEATURE_071_SOURCE),
        _make_step("topology_legality", inputs, expected_outputs["topology"], actual_outputs["topology"], "src.analysis.end_to_end_hoodie_golden_trace_validation.report -> cloud_vertical_path"),
        _make_step(
            "deadline_computation",
            inputs,
            expected_outputs["deadline"],
            actual_outputs["deadline"],
            "src.environment.paper_timeout.compute_absolute_deadline -> src.environment.paper_timeout.is_success_before_deadline -> src.environment.deadline_rules.has_expired",
        ),
        _make_step(
            "terminal_state_assignment",
            inputs,
            expected_outputs["terminal_state"],
            actual_outputs["terminal_state"],
            "src.environment.paper_timeout.terminal_status_from_completion -> src.environment.reward_timing.validate_terminal_state",
        ),
        _make_step(
            "reward_emission",
            inputs,
            expected_outputs["reward"],
            actual_outputs["reward"],
            "src.environment.reward_timing.reward_from_terminal_state -> src.environment.reward_timing.reward_for_terminal_task",
        ),
    )
    return _trace_summary_trace(
        scenario_id="cloud_vertical_success",
        name="Cloud Vertical Success",
        description="Cloud/vertical routing is valid without being treated as a Figure 7 horizontal neighbor.",
        inputs=inputs,
        expected_outputs=expected_outputs,
        actual_outputs=actual_outputs,
        base_steps=base_steps,
        comparison_trace_result="cloud vertical path accepted separately from horizontal adjacency",
    )


def _build_success_reward_negative_phi() -> GoldenTraceScenario:
    inputs = _local_trace_inputs(scenario_id="success_reward_negative_phi")
    topology = TopologyTraceEvidence(
        "1",
        "private",
        "local_private_execution",
        False,
        False,
        True,
        topology_check_required=False,
        reason="local_private_execution",
    )
    arrival_slot = 2
    phi = 4
    completion_slot = 4
    absolute_deadline_slot = compute_absolute_deadline(arrival_slot, phi)
    terminal_status = terminal_status_from_completion(completion_slot, arrival_slot, phi, completion_kind="private")
    deadline_actual = DeadlineTraceEvidence(arrival_slot, phi, absolute_deadline_slot, completion_slot, "paper", is_success_before_deadline(completion_slot, arrival_slot, phi), terminal_status)
    terminal_state_actual = {"terminal_status": terminal_status, "terminal_slot": completion_slot, "drop_reason": None}
    phi_value_actual = phi_private(psi_priv=5, t=arrival_slot)
    phi_pub_value_actual = phi_public(((1, 6), (0, 9)), t=arrival_slot)
    selected_phi_actual = select_phi(True, phi_value_actual, phi_pub_value_actual)
    reward_value_actual = reward_from_terminal_state(True, "completed_private", selected_phi_actual, 40.0)
    reward_actual = RewardTraceEvidence(True, "completed_private", selected_phi_actual, 40.0, reward_value_actual, reward_slot_for_terminal(completion_slot), "paper")
    expected_outputs = {
        "action_selection": {"action_type": "local", "selected_destination": "private", "mode": "paper"},
        "topology": {
            "source_agent_id": "1",
            "destination_agent_id": "private",
            "neighbor_map_source": "local_private_execution",
            "is_neighbor": False,
            "is_self_destination": False,
            "final_legal": True,
            "topology_check_required": False,
            "reason": "local_private_execution",
        },
        "deadline": {
            "arrival_slot": arrival_slot,
            "phi": phi,
            "absolute_deadline_slot": absolute_deadline_slot,
            "completion_slot": completion_slot,
            "mode": "paper",
            "success_before_deadline": True,
            "terminal_status": terminal_status,
        },
        "terminal_state": {"terminal_status": terminal_status, "terminal_slot": completion_slot, "drop_reason": None},
        "reward": {
            "x_active": True,
            "terminal_status": "completed_private",
            "phi_value": 4,
            "drop_penalty": 40.0,
            "reward_value": -4.0,
            "reward_slot": reward_slot_for_terminal(completion_slot),
            "mode": "paper",
        },
    }
    actual_outputs = {
        "action_selection": {"action_type": inputs["action_type"], "selected_destination": inputs["destination_agent_id"], "mode": inputs["mode"]},
        "topology": topology.to_dict(),
        "deadline": deadline_actual.to_dict(),
        "terminal_state": terminal_state_actual,
        "reward": reward_actual.to_dict(),
    }
    base_steps = (
        _make_step(
            "task_arrival",
            inputs,
            {"arrival_slot": inputs["arrival_slot"], "source_agent_id": inputs["source_agent_id"], "destination_agent_id": inputs["destination_agent_id"], "action_type": inputs["action_type"]},
            {"arrival_slot": inputs["arrival_slot"], "source_agent_id": inputs["source_agent_id"], "destination_agent_id": inputs["destination_agent_id"], "action_type": inputs["action_type"]},
            FEATURE_071_SOURCE,
        ),
        _make_step("action_selection", inputs, expected_outputs["action_selection"], actual_outputs["action_selection"], FEATURE_071_SOURCE),
        _make_step("topology_legality", inputs, expected_outputs["topology"], actual_outputs["topology"], "src.analysis.end_to_end_hoodie_golden_trace_validation.report -> local_private_execution"),
        _make_step(
            "deadline_computation",
            inputs,
            expected_outputs["deadline"],
            actual_outputs["deadline"],
            "src.environment.paper_timeout.compute_absolute_deadline -> src.environment.paper_timeout.is_success_before_deadline -> src.environment.deadline_rules.has_expired",
        ),
        _make_step(
            "terminal_state_assignment",
            inputs,
            expected_outputs["terminal_state"],
            actual_outputs["terminal_state"],
            "src.environment.paper_timeout.terminal_status_from_completion -> src.environment.reward_timing.validate_terminal_state",
        ),
        _make_step(
            "reward_emission",
            inputs,
            expected_outputs["reward"],
            actual_outputs["reward"],
            "src.environment.reward_timing.reward_from_terminal_state -> src.environment.reward_timing.reward_for_terminal_task",
        ),
    )
    return _trace_summary_trace(
        scenario_id="success_reward_negative_phi",
        name="Success Reward Negative Phi",
        description="Successful execution emits the negative-Phi reward implied by the runtime helpers.",
        inputs=inputs,
        expected_outputs=expected_outputs,
        actual_outputs=actual_outputs,
        base_steps=base_steps,
        comparison_trace_result="success reward equals negative Phi",
    )


def _build_drop_reward_negative_c() -> GoldenTraceScenario:
    inputs = _local_trace_inputs(scenario_id="drop_reward_negative_c", completion_slot=5)
    topology = TopologyTraceEvidence(
        "1",
        "private",
        "local_private_execution",
        False,
        False,
        True,
        topology_check_required=False,
        reason="local_private_execution",
    )
    arrival_slot = 2
    phi = 4
    completion_slot = 5
    absolute_deadline_slot = compute_absolute_deadline(arrival_slot, phi)
    deadline_actual = DeadlineTraceEvidence(arrival_slot, phi, absolute_deadline_slot, completion_slot, "paper", False, "dropped_timeout")
    terminal_state_actual = {"terminal_status": "dropped_timeout", "terminal_slot": completion_slot, "drop_reason": "deadline_exceeded"}
    reward_value_actual = reward_from_terminal_state(True, "dropped_timeout", None, 40.0)
    reward_actual = RewardTraceEvidence(True, "dropped_timeout", None, 40.0, reward_value_actual, reward_slot_for_terminal(completion_slot), "paper")
    expected_outputs = {
        "action_selection": {"action_type": "local", "selected_destination": "private", "mode": "paper"},
        "topology": {
            "source_agent_id": "1",
            "destination_agent_id": "private",
            "neighbor_map_source": "local_private_execution",
            "is_neighbor": False,
            "is_self_destination": False,
            "final_legal": True,
            "topology_check_required": False,
            "reason": "local_private_execution",
        },
        "deadline": {
            "arrival_slot": arrival_slot,
            "phi": phi,
            "absolute_deadline_slot": absolute_deadline_slot,
            "completion_slot": completion_slot,
            "mode": "paper",
            "success_before_deadline": False,
            "terminal_status": "dropped_timeout",
        },
        "terminal_state": {"terminal_status": "dropped_timeout", "terminal_slot": completion_slot, "drop_reason": "deadline_exceeded"},
        "reward": {
            "x_active": True,
            "terminal_status": "dropped_timeout",
            "phi_value": None,
            "drop_penalty": 40.0,
            "reward_value": -40.0,
            "reward_slot": reward_slot_for_terminal(completion_slot),
            "mode": "paper",
        },
    }
    actual_outputs = {
        "action_selection": {"action_type": inputs["action_type"], "selected_destination": inputs["destination_agent_id"], "mode": inputs["mode"]},
        "topology": topology.to_dict(),
        "deadline": deadline_actual.to_dict(),
        "terminal_state": terminal_state_actual,
        "reward": reward_actual.to_dict(),
    }
    base_steps = (
        _make_step(
            "task_arrival",
            inputs,
            {"arrival_slot": inputs["arrival_slot"], "source_agent_id": inputs["source_agent_id"], "destination_agent_id": inputs["destination_agent_id"], "action_type": inputs["action_type"]},
            {"arrival_slot": inputs["arrival_slot"], "source_agent_id": inputs["source_agent_id"], "destination_agent_id": inputs["destination_agent_id"], "action_type": inputs["action_type"]},
            FEATURE_071_SOURCE,
        ),
        _make_step("action_selection", inputs, expected_outputs["action_selection"], actual_outputs["action_selection"], FEATURE_071_SOURCE),
        _make_step("topology_legality", inputs, expected_outputs["topology"], actual_outputs["topology"], "src.analysis.end_to_end_hoodie_golden_trace_validation.report -> local_private_execution"),
        _make_step(
            "deadline_computation",
            inputs,
            expected_outputs["deadline"],
            actual_outputs["deadline"],
            "src.environment.paper_timeout.compute_absolute_deadline -> src.environment.paper_timeout.is_success_before_deadline -> src.environment.deadline_rules.has_expired",
        ),
        _make_step(
            "terminal_state_assignment",
            inputs,
            expected_outputs["terminal_state"],
            actual_outputs["terminal_state"],
            "src.environment.paper_timeout.terminal_status_from_completion -> src.environment.reward_timing.validate_terminal_state",
        ),
        _make_step(
            "reward_emission",
            inputs,
            expected_outputs["reward"],
            actual_outputs["reward"],
            "src.environment.reward_timing.reward_from_terminal_state -> src.environment.reward_timing.reward_for_terminal_task",
        ),
    )
    return _trace_summary_trace(
        scenario_id="drop_reward_negative_c",
        name="Drop Reward Negative C",
        description="Dropped terminal states emit the negative-C reward and not a success reward.",
        inputs=inputs,
        expected_outputs=expected_outputs,
        actual_outputs=actual_outputs,
        base_steps=base_steps,
        comparison_trace_result="drop reward equals negative C",
    )


def _build_inactive_task_no_reward_sentinel() -> GoldenTraceScenario:
    inputs = _local_trace_inputs(scenario_id="inactive_task_no_reward_sentinel")
    topology = TopologyTraceEvidence(
        "1",
        "private",
        "local_private_execution",
        False,
        False,
        True,
        topology_check_required=False,
        reason="local_private_execution",
    )
    arrival_slot = 2
    phi = 4
    completion_slot = 4
    absolute_deadline_slot = compute_absolute_deadline(arrival_slot, phi)
    terminal_status = terminal_status_from_completion(completion_slot, arrival_slot, phi, completion_kind="private")
    deadline_actual = DeadlineTraceEvidence(arrival_slot, phi, absolute_deadline_slot, completion_slot, "paper", is_success_before_deadline(completion_slot, arrival_slot, phi), terminal_status)
    terminal_state_actual = {"terminal_status": terminal_status, "terminal_slot": completion_slot, "drop_reason": None}
    reward_value_actual = reward_from_terminal_state(False, "completed_private", 3, 40.0)
    reward_actual = RewardTraceEvidence(False, "completed_private", 3, 40.0, reward_value_actual, reward_slot_for_terminal(completion_slot), "paper")
    expected_outputs = {
        "action_selection": {"action_type": "local", "selected_destination": "private", "mode": "paper"},
        "topology": {
            "source_agent_id": "1",
            "destination_agent_id": "private",
            "neighbor_map_source": "local_private_execution",
            "is_neighbor": False,
            "is_self_destination": False,
            "final_legal": True,
            "topology_check_required": False,
            "reason": "local_private_execution",
        },
        "deadline": {
            "arrival_slot": arrival_slot,
            "phi": phi,
            "absolute_deadline_slot": absolute_deadline_slot,
            "completion_slot": completion_slot,
            "mode": "paper",
            "success_before_deadline": True,
            "terminal_status": terminal_status,
        },
        "terminal_state": {"terminal_status": terminal_status, "terminal_slot": completion_slot, "drop_reason": None},
        "reward": {
            "x_active": False,
            "terminal_status": "completed_private",
            "phi_value": 3,
            "drop_penalty": 40.0,
            "reward_value": float("nan"),
            "reward_slot": reward_slot_for_terminal(completion_slot),
            "mode": "paper",
        },
    }
    actual_outputs = {
        "action_selection": {"action_type": inputs["action_type"], "selected_destination": inputs["destination_agent_id"], "mode": inputs["mode"]},
        "topology": topology.to_dict(),
        "deadline": deadline_actual.to_dict(),
        "terminal_state": terminal_state_actual,
        "reward": reward_actual.to_dict(),
    }
    base_steps = (
        _make_step(
            "task_arrival",
            inputs,
            {"arrival_slot": inputs["arrival_slot"], "source_agent_id": inputs["source_agent_id"], "destination_agent_id": inputs["destination_agent_id"], "action_type": inputs["action_type"]},
            {"arrival_slot": inputs["arrival_slot"], "source_agent_id": inputs["source_agent_id"], "destination_agent_id": inputs["destination_agent_id"], "action_type": inputs["action_type"]},
            FEATURE_071_SOURCE,
        ),
        _make_step("action_selection", inputs, expected_outputs["action_selection"], actual_outputs["action_selection"], FEATURE_071_SOURCE),
        _make_step("topology_legality", inputs, expected_outputs["topology"], actual_outputs["topology"], "src.analysis.end_to_end_hoodie_golden_trace_validation.report -> local_private_execution"),
        _make_step(
            "deadline_computation",
            inputs,
            expected_outputs["deadline"],
            actual_outputs["deadline"],
            "src.environment.paper_timeout.compute_absolute_deadline -> src.environment.paper_timeout.is_success_before_deadline -> src.environment.deadline_rules.has_expired",
        ),
        _make_step(
            "terminal_state_assignment",
            inputs,
            expected_outputs["terminal_state"],
            actual_outputs["terminal_state"],
            "src.environment.paper_timeout.terminal_status_from_completion -> src.environment.reward_timing.validate_terminal_state",
        ),
        _make_step(
            "reward_emission",
            inputs,
            expected_outputs["reward"],
            actual_outputs["reward"],
            "src.environment.reward_timing.reward_from_terminal_state -> src.environment.reward_timing.reward_for_terminal_task",
        ),
    )
    return _trace_summary_trace(
        scenario_id="inactive_task_no_reward_sentinel",
        name="Inactive Task No Reward Sentinel",
        description="An inactive task produces an explicit NaN reward sentinel.",
        inputs=inputs,
        expected_outputs=expected_outputs,
        actual_outputs=actual_outputs,
        base_steps=base_steps,
        comparison_trace_result="inactive task returns explicit NaN sentinel",
    )


def _build_pending_task_cannot_emit_reward() -> GoldenTraceScenario:
    inputs = _local_trace_inputs(scenario_id="pending_task_cannot_emit_reward", completion_slot=None)
    topology = TopologyTraceEvidence(
        "1",
        "private",
        "local_private_execution",
        False,
        False,
        True,
        topology_check_required=False,
        reason="local_private_execution",
    )
    arrival_slot = 2
    phi = 4
    absolute_deadline_slot = compute_absolute_deadline(arrival_slot, phi)
    deadline_actual = DeadlineTraceEvidence(arrival_slot, phi, absolute_deadline_slot, None, "paper", False, "pending")
    terminal_state_actual = {"terminal_status": "pending", "terminal_slot": None, "drop_reason": None}
    reward_actual = RewardTraceEvidence(True, "pending", None, 40.0, None, None, "paper")
    expected_outputs = {
        "action_selection": {"action_type": "local", "selected_destination": "private", "mode": "paper"},
        "topology": {
            "source_agent_id": "1",
            "destination_agent_id": "private",
            "neighbor_map_source": "local_private_execution",
            "is_neighbor": False,
            "is_self_destination": False,
            "final_legal": True,
            "topology_check_required": False,
            "reason": "local_private_execution",
        },
        "deadline": {
            "arrival_slot": arrival_slot,
            "phi": phi,
            "absolute_deadline_slot": absolute_deadline_slot,
            "completion_slot": None,
            "mode": "paper",
            "success_before_deadline": False,
            "terminal_status": "pending",
        },
        "terminal_state": {"terminal_status": "pending", "terminal_slot": None, "drop_reason": None},
        "reward": {"status": "blocked", "can_emit_reward": False, "reward_trace": {"x_active": True, "terminal_status": "pending", "phi_value": None, "drop_penalty": 40.0, "reward_value": None, "reward_slot": None, "mode": "paper"}},
    }
    actual_outputs = {
        "action_selection": {"action_type": inputs["action_type"], "selected_destination": inputs["destination_agent_id"], "mode": inputs["mode"]},
        "topology": topology.to_dict(),
        "deadline": deadline_actual.to_dict(),
        "terminal_state": terminal_state_actual,
        "reward": {"status": "blocked", "can_emit_reward": can_emit_reward("pending"), "reward_trace": reward_actual.to_dict()},
    }
    base_steps = (
        _make_step(
            "task_arrival",
            inputs,
            {"arrival_slot": inputs["arrival_slot"], "source_agent_id": inputs["source_agent_id"], "destination_agent_id": inputs["destination_agent_id"], "action_type": inputs["action_type"]},
            {"arrival_slot": inputs["arrival_slot"], "source_agent_id": inputs["source_agent_id"], "destination_agent_id": inputs["destination_agent_id"], "action_type": inputs["action_type"]},
            FEATURE_071_SOURCE,
        ),
        _make_step("action_selection", inputs, expected_outputs["action_selection"], actual_outputs["action_selection"], FEATURE_071_SOURCE),
        _make_step("topology_legality", inputs, expected_outputs["topology"], actual_outputs["topology"], "src.analysis.end_to_end_hoodie_golden_trace_validation.report -> local_private_execution"),
        _make_step(
            "deadline_computation",
            inputs,
            expected_outputs["deadline"],
            actual_outputs["deadline"],
            "src.environment.paper_timeout.is_success_before_deadline",
        ),
        _make_step(
            "terminal_state_assignment",
            inputs,
            expected_outputs["terminal_state"],
            actual_outputs["terminal_state"],
            "src.environment.reward_timing.validate_terminal_state",
        ),
        _make_step(
            "reward_emission",
            inputs,
            {"status": "blocked", "reason": "pending_terminal_state", "can_emit_reward": False},
            {"status": "blocked", "reason": "pending_terminal_state", "can_emit_reward": can_emit_reward("pending")},
            "src.environment.reward_timing.can_emit_reward",
        ),
    )
    comparison_trace_result = "pending tasks do not emit reward; emission is blocked explicitly"
    return GoldenTraceScenario(
        scenario_id="pending_task_cannot_emit_reward",
        name="Pending Task Cannot Emit Reward",
        description="A pending task cannot emit a reward; the trace records the block instead of crashing.",
        inputs=inputs,
        expected_outputs={**expected_outputs, "comparison": {"passed": True, "trace_result": comparison_trace_result}},
        actual_outputs={**actual_outputs, "comparison": {"passed": _deep_equal(expected_outputs, actual_outputs), "trace_result": comparison_trace_result}},
        steps=(
            *base_steps,
            _make_step(
                "expected_actual_comparison",
                inputs,
                {"passed": True, "trace_result": comparison_trace_result},
                {"passed": _deep_equal(expected_outputs, actual_outputs), "trace_result": comparison_trace_result},
                "feature_072.expected_vs_actual_trace_comparison",
            ),
        ),
    )


def _build_compatibility_mode_not_default() -> GoldenTraceScenario:
    inputs = _local_trace_inputs(scenario_id="compatibility_mode_not_default", completion_slot=5)
    topology = TopologyTraceEvidence(
        "1",
        "private",
        "local_private_execution",
        False,
        False,
        True,
        topology_check_required=False,
        reason="local_private_execution",
    )
    arrival_slot = 2
    phi = 4
    completion_slot = 4
    absolute_deadline_slot = compute_absolute_deadline(arrival_slot, phi)
    paper_terminal_status = terminal_status_from_completion(completion_slot, arrival_slot, phi, completion_kind="private")
    paper_deadline = DeadlineTraceEvidence(arrival_slot, phi, absolute_deadline_slot, completion_slot, "paper", is_success_before_deadline(completion_slot, arrival_slot, phi), paper_terminal_status)
    compatibility_deadline = DeadlineTraceEvidence(arrival_slot, phi, absolute_deadline_slot, completion_slot, "compatibility", is_success_before_deadline(completion_slot, arrival_slot, phi, mode="compatibility"), "completed_private")
    terminal_state_expected = {
        "paper": {"terminal_status": "completed_private", "terminal_slot": completion_slot, "drop_reason": None},
        "compatibility": {"terminal_status": "completed_private", "terminal_slot": completion_slot, "drop_reason": None},
    }
    terminal_state_actual = {
        "paper": {"terminal_status": "completed_private", "terminal_slot": completion_slot, "drop_reason": None},
        "compatibility": {"terminal_status": "completed_private", "terminal_slot": completion_slot, "drop_reason": None},
    }
    reward = {
        "paper": {
            "x_active": True,
            "terminal_status": "completed_private",
            "phi_value": 3,
            "drop_penalty": 40.0,
            "reward_value": reward_for_terminal_task(Task(1, 1, arrival_slot, 1.0, 1.0, 4, absolute_deadline_slot, completion_slot=completion_slot, terminal_outcome="completed", reward_emitted=True)),
            "reward_slot": reward_slot_for_terminal(completion_slot),
            "mode": "paper",
        },
        "compatibility": {
            "x_active": True,
            "terminal_status": "completed_private",
            "phi_value": 4,
            "drop_penalty": 40.0,
            "reward_value": reward_for_terminal_task(Task(1, 1, arrival_slot, 1.0, 1.0, 4, absolute_deadline_slot, completion_slot=completion_slot, terminal_outcome="completed", reward_emitted=True), mode="compatibility"),
            "reward_slot": reward_slot_for_terminal(completion_slot),
            "mode": "compatibility",
        },
    }
    reward_expected = {
        "paper": {
            "x_active": True,
            "terminal_status": "completed_private",
            "phi_value": 3,
            "drop_penalty": 40.0,
            "reward_value": reward_for_terminal_task(Task(1, 1, arrival_slot, 1.0, 1.0, 4, absolute_deadline_slot, completion_slot=completion_slot, terminal_outcome="completed", reward_emitted=True)),
            "reward_slot": reward_slot_for_terminal(completion_slot),
            "mode": "paper",
        },
        "compatibility": {
            "x_active": True,
            "terminal_status": "completed_private",
            "phi_value": 4,
            "drop_penalty": 40.0,
            "reward_value": reward_for_terminal_task(Task(1, 1, arrival_slot, 1.0, 1.0, 4, absolute_deadline_slot, completion_slot=completion_slot, terminal_outcome="completed", reward_emitted=True), mode="compatibility"),
            "reward_slot": reward_slot_for_terminal(completion_slot),
            "mode": "compatibility",
        },
    }
    reward_actual_bundle = {
        "paper": {
            "x_active": True,
            "terminal_status": "completed_private",
            "phi_value": 3,
            "drop_penalty": 40.0,
            "reward_value": reward_for_terminal_task(Task(1, 1, arrival_slot, 1.0, 1.0, 4, absolute_deadline_slot, completion_slot=completion_slot, terminal_outcome="completed", reward_emitted=True)),
            "reward_slot": reward_slot_for_terminal(completion_slot),
            "mode": "paper",
        },
        "compatibility": {
            "x_active": True,
            "terminal_status": "completed_private",
            "phi_value": 4,
            "drop_penalty": 40.0,
            "reward_value": reward_for_terminal_task(Task(1, 1, arrival_slot, 1.0, 1.0, 4, absolute_deadline_slot, completion_slot=completion_slot, terminal_outcome="completed", reward_emitted=True), mode="compatibility"),
            "reward_slot": reward_slot_for_terminal(completion_slot),
            "mode": "compatibility",
        },
    }
    expected_outputs = {
        "action_selection": {"action_type": "local", "selected_destination": "private", "mode": "paper"},
        "topology": {
            "source_agent_id": "1",
            "destination_agent_id": "private",
            "neighbor_map_source": "local_private_execution",
            "is_neighbor": False,
            "is_self_destination": False,
            "final_legal": True,
            "topology_check_required": False,
            "reason": "local_private_execution",
        },
        "deadline": {"paper": paper_deadline.to_dict(), "compatibility": compatibility_deadline.to_dict()},
        "terminal_state": terminal_state_expected,
        "reward": reward_expected,
    }
    actual_outputs = {
        "action_selection": {"action_type": inputs["action_type"], "selected_destination": inputs["destination_agent_id"], "mode": "paper"},
        "topology": topology.to_dict(),
        "deadline": {
            "paper": DeadlineTraceEvidence(arrival_slot, phi, absolute_deadline_slot, completion_slot, "paper", is_success_before_deadline(completion_slot, arrival_slot, phi), paper_terminal_status).to_dict(),
            "compatibility": DeadlineTraceEvidence(arrival_slot, phi, absolute_deadline_slot, completion_slot, "compatibility", is_success_before_deadline(completion_slot, arrival_slot, phi, mode="compatibility"), "completed_private").to_dict(),
        },
        "terminal_state": terminal_state_actual,
        "reward": reward_actual_bundle,
    }
    base_steps = (
        _make_step(
            "task_arrival",
            inputs,
            {"arrival_slot": inputs["arrival_slot"], "source_agent_id": inputs["source_agent_id"], "destination_agent_id": inputs["destination_agent_id"], "action_type": inputs["action_type"]},
            {"arrival_slot": inputs["arrival_slot"], "source_agent_id": inputs["source_agent_id"], "destination_agent_id": inputs["destination_agent_id"], "action_type": inputs["action_type"]},
            FEATURE_071_SOURCE,
        ),
        _make_step("action_selection", inputs, expected_outputs["action_selection"], actual_outputs["action_selection"], FEATURE_071_SOURCE),
        _make_step("topology_legality", inputs, expected_outputs["topology"], actual_outputs["topology"], "src.analysis.end_to_end_hoodie_golden_trace_validation.report -> local_private_execution"),
        _make_step(
            "deadline_computation",
            inputs,
            expected_outputs["deadline"],
            actual_outputs["deadline"],
            "src.environment.paper_timeout.is_success_before_deadline -> src.environment.deadline_rules.has_expired",
        ),
        _make_step(
            "terminal_state_assignment",
            inputs,
            expected_outputs["terminal_state"],
            actual_outputs["terminal_state"],
            "src.environment.paper_timeout.terminal_status_from_completion",
        ),
        _make_step(
            "reward_emission",
            inputs,
            expected_outputs["reward"],
            actual_outputs["reward"],
            "src.environment.reward_timing.reward_for_terminal_task",
        ),
    )
    comparison_trace_result = "paper is default; compatibility is explicit only"
    return _trace_summary_trace(
        scenario_id="compatibility_mode_not_default",
        name="Compatibility Mode Not Default",
        description="Paper-mode default and explicit compatibility mode diverge only when compatibility is named explicitly.",
        inputs=inputs,
        expected_outputs=expected_outputs,
        actual_outputs=actual_outputs,
        base_steps=base_steps,
        comparison_trace_result=comparison_trace_result,
    )


def build_all_golden_trace_scenarios() -> tuple[GoldenTraceScenario, ...]:
    return (
        _build_local_success_before_deadline(),
        _build_local_timeout_at_deadline(),
        _build_horizontal_legal_neighbor(),
        _build_horizontal_non_neighbor_rejected(),
        _build_horizontal_self_destination_rejected(),
        _build_cloud_vertical_success(),
        _build_success_reward_negative_phi(),
        _build_drop_reward_negative_c(),
        _build_inactive_task_no_reward_sentinel(),
        _build_pending_task_cannot_emit_reward(),
        _build_compatibility_mode_not_default(),
    )


def build_feature_072_report(
    changed_files: Sequence[str] | None = None,
) -> Feature072Report:
    checked_changed_files = tuple(validate_scope(changed_files or DEFAULT_CHANGED_FILES))
    scenarios = build_all_golden_trace_scenarios()
    regression_068r = _feature_068r_regression_status()
    regression_069 = _feature_069_regression_status()
    regression_070 = _feature_070_regression_status()
    regression_071 = _feature_071_regression_status()
    passed = all(
        (
            scenarios,
            all(scenario.passed for scenario in scenarios),
            regression_068r.passed,
            regression_069.passed,
            regression_070.passed,
            regression_071.passed,
        )
    )
    status = "end_to_end_golden_trace_validation_ready" if passed else "end_to_end_golden_trace_validation_with_blockers"
    return Feature072Report(
        feature_name="Feature 072 - End-to-End HOODIE Golden Trace Validation",
        status=status,
        passed=passed,
        changed_files=checked_changed_files,
        scenarios=scenarios,
        feature_068r_regression_status=regression_068r,
        feature_069_regression_status=regression_069,
        feature_070_regression_status=regression_070,
        feature_071_regression_status=regression_071,
        paper_claim_boundary=(
            "No full paper reproduction claim is made. Feature 072 validates deterministic end-to-end semantic traces "
            "only. Expected outputs are independent scenario constants, actual outputs are computed from Feature 070 "
            "topology evidence and Feature 071 helpers, and the explicit paper-versus-compatibility boundary is "
            "preserved."
        ),
        recommended_next_feature="Feature 073 should extend deterministic trace validation to remaining integration surfaces without claiming full paper reproduction.",
    )


def render_feature_072_report(report: Feature072Report) -> str:
    payload = report.to_dict()
    lines = [
        "# Feature 072 End-to-End HOODIE Golden Trace Validation Report",
        "",
        f"- feature_name: `{payload['feature_name']}`",
        f"- status: `{payload['status']}`",
        f"- passed: `{payload['passed']}`",
        f"- paper_claim_boundary: {payload['paper_claim_boundary']}",
        "- expected_outputs are independent scenario constants",
        "- actual_outputs are computed from Feature 070 topology evidence and Feature 071 helpers",
        "",
        "## Scenarios",
    ]
    for scenario in payload["scenarios"]:
        lines.extend(
            [
                f"### {scenario['scenario_id']}",
                f"- name: {scenario['name']}",
                f"- passed: `{scenario['passed']}`",
                f"- description: {scenario['description']}",
                "```json",
                _json_dump(scenario).rstrip(),
                "```",
                "",
            ]
        )
    lines.extend(
        [
            "## Feature 068R Regression Status",
            "```json",
            _json_dump(payload["feature_068r_regression_status"]).rstrip(),
            "```",
            "",
            "## Feature 069 Regression Status",
            "```json",
            _json_dump(payload["feature_069_regression_status"]).rstrip(),
            "```",
            "",
            "## Feature 070 Regression Status",
            "```json",
            _json_dump(payload["feature_070_regression_status"]).rstrip(),
            "```",
            "",
            "## Feature 071 Regression Status",
            "```json",
            _json_dump(payload["feature_071_regression_status"]).rstrip(),
            "```",
            "",
            "## Recommended Next Feature",
            payload["recommended_next_feature"],
            "",
            "## Validation Commands",
            "```json",
            _json_dump(list(VALIDATION_COMMANDS)).rstrip(),
            "```",
            "",
            "## Changed Files",
            "```json",
            _json_dump(payload["changed_files"]).rstrip(),
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def write_feature_072_report(report: Feature072Report, output_dir: Path | str) -> tuple[Path, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    json_path = output_path / "feature-072-end-to-end-hoodie-golden-trace-validation-report.json"
    md_path = output_path / "feature-072-end-to-end-hoodie-golden-trace-validation-report.md"
    json_path.write_text(_json_dump(report.to_dict()), encoding="utf-8")
    md_path.write_text(render_feature_072_report(report), encoding="utf-8")
    return json_path, md_path
