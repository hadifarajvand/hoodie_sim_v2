from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import json
from typing import Any

from src.analysis.controlled_evaluation_batch_readiness.report import build_feature_073_report
from src.analysis.end_to_end_hoodie_golden_trace_validation.report import build_feature_072_report
from src.analysis.full_hoodie_mechanism_fidelity_batch.report import build_feature_069_report
from src.analysis.runtime_paper_faithful_semantics_alignment.report import build_feature_071_report
from src.analysis.topology_timeout_reward_fidelity.report import build_feature_070_report
from src.evaluation.policy_registry import PolicyRegistry
from src.environment.paper_timeout import compute_absolute_deadline, is_success_before_deadline, terminal_status_from_completion
from src.environment.reward_timing import (
    phi_private,
    phi_public,
    reward_for_terminal_task,
    reward_from_terminal_state,
    reward_slot_for_terminal,
    select_phi,
)
from src.environment.task import Task
from src.policies import (
    BalancedCooperationOffloadingPolicy,
    FullLocalComputingPolicy,
    HorizontalOffloadingPolicy,
    MinimumLatencyEstimateOffloadingPolicy,
    PolicyContext,
    RandomOffloadingPolicy,
    VerticalOffloadingPolicy,
)
from src.policies.common import action_family as runtime_action_family

from .config import DEFAULT_CHANGED_FILES, DEFAULT_OUTPUT_DIR, VALIDATION_COMMANDS, validate_scope
from .model import (
    BaselineComparativeReadinessReport,
    BaselinePolicyComparativeRegressionEvidence,
    BaselinePolicyDescriptor,
    PolicyActionBoundOutcome,
    PolicyAggregateComparison,
    PolicyScenarioComparison,
    REQUIRED_POLICY_IDS,
    REQUIRED_SCENARIO_IDS,
    aggregate_policy_rows,
)


FEATURE_074_STATUS_READY = "baseline_policy_comparative_evaluation_readiness_ready"
FEATURE_074_STATUS_WITH_BLOCKERS = "baseline_policy_comparative_evaluation_readiness_with_blockers"
FEATURE_074_RECOMMENDATION = "Feature 075 - Proposed Deadline-Aware Method Integration Readiness"
PAPER_DROP_PENALTY = 40.0
FIGURE_7_SOURCE = "specs/070-topology-timeout-reward-fidelity/evidence/figure-7-topology-extraction.md"

COMPLETED_STATUSES = {"completed_private", "completed_public", "completed_cloud"}


@dataclass(frozen=True, slots=True)
class ScenarioActionProfile:
    scenario_id: str
    arrival_slot: int
    phi: int
    local_completion_slot: int
    horizontal_completion_slot: int
    cloud_completion_slot: int
    horizontal_source: str
    legal_horizontal_destination: str
    illegal_horizontal_destination: str
    drop_penalty: float = PAPER_DROP_PENALTY


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


@lru_cache(maxsize=1)
def _feature_073_report():
    return build_feature_073_report()


def _policy_family_label(policy_id: str) -> str:
    return {
        "FLC": "fixed-local / local-first family",
        "VO": "vertical-offload family",
        "HO": "horizontal-offload family",
        "RO": "random-offload family",
        "BCO": "balanced-cloud-offload family",
        "MLEO": "minimum-latency-estimation-offload family",
    }[policy_id]


def _expected_policy_type(policy_id: str):
    return {
        "FLC": FullLocalComputingPolicy,
        "VO": VerticalOffloadingPolicy,
        "HO": HorizontalOffloadingPolicy,
        "RO": RandomOffloadingPolicy,
        "BCO": BalancedCooperationOffloadingPolicy,
        "MLEO": MinimumLatencyEstimateOffloadingPolicy,
    }[policy_id]


def _scenario_action_profiles() -> dict[str, ScenarioActionProfile]:
    return {
        "light_load_no_deadline_pressure": ScenarioActionProfile(
            scenario_id="light_load_no_deadline_pressure",
            arrival_slot=2,
            phi=4,
            local_completion_slot=4,
            horizontal_completion_slot=4,
            cloud_completion_slot=4,
            horizontal_source="1",
            legal_horizontal_destination="6",
            illegal_horizontal_destination="2",
        ),
        "tight_deadline_pressure": ScenarioActionProfile(
            scenario_id="tight_deadline_pressure",
            arrival_slot=2,
            phi=4,
            local_completion_slot=5,
            horizontal_completion_slot=5,
            cloud_completion_slot=5,
            horizontal_source="1",
            legal_horizontal_destination="6",
            illegal_horizontal_destination="2",
        ),
        "legal_horizontal_offload": ScenarioActionProfile(
            scenario_id="legal_horizontal_offload",
            arrival_slot=2,
            phi=5,
            local_completion_slot=4,
            horizontal_completion_slot=5,
            cloud_completion_slot=4,
            horizontal_source="1",
            legal_horizontal_destination="6",
            illegal_horizontal_destination="2",
        ),
        "illegal_horizontal_destination_attempt": ScenarioActionProfile(
            scenario_id="illegal_horizontal_destination_attempt",
            arrival_slot=2,
            phi=4,
            local_completion_slot=4,
            horizontal_completion_slot=4,
            cloud_completion_slot=4,
            horizontal_source="1",
            legal_horizontal_destination="6",
            illegal_horizontal_destination="2",
        ),
        "cloud_vertical_fallback": ScenarioActionProfile(
            scenario_id="cloud_vertical_fallback",
            arrival_slot=2,
            phi=4,
            local_completion_slot=4,
            horizontal_completion_slot=5,
            cloud_completion_slot=4,
            horizontal_source="1",
            legal_horizontal_destination="6",
            illegal_horizontal_destination="2",
        ),
        "timeout_drop_case": ScenarioActionProfile(
            scenario_id="timeout_drop_case",
            arrival_slot=2,
            phi=4,
            local_completion_slot=6,
            horizontal_completion_slot=6,
            cloud_completion_slot=6,
            horizontal_source="1",
            legal_horizontal_destination="6",
            illegal_horizontal_destination="2",
        ),
        "mixed_local_horizontal_cloud_candidates": ScenarioActionProfile(
            scenario_id="mixed_local_horizontal_cloud_candidates",
            arrival_slot=2,
            phi=4,
            local_completion_slot=4,
            horizontal_completion_slot=5,
            cloud_completion_slot=4,
            horizontal_source="1",
            legal_horizontal_destination="6",
            illegal_horizontal_destination="2",
        ),
    }


def _scenario_profile(scenario_id: str) -> ScenarioActionProfile:
    profiles = _scenario_action_profiles()
    if scenario_id not in profiles:
        raise KeyError(f"unsupported scenario_id: {scenario_id}")
    return profiles[scenario_id]


def _topology_map() -> dict[str, tuple[str, ...]]:
    return _feature_070_report().topology_evidence.neighbor_map


def _is_horizontal_neighbor(source_agent_id: str, destination_agent_id: str) -> bool:
    return destination_agent_id in _topology_map().get(source_agent_id, ())


def _normalize_action_id(selected_action: object) -> str:
    if isinstance(selected_action, str):
        return selected_action.strip()
    if isinstance(selected_action, int):
        return str(selected_action)
    return ""


def _task_reward(policy_action: str, profile: ScenarioActionProfile, completion_slot: int, terminal_status: str) -> float:
    task = Task(
        task_id=1,
        source_agent_id=1,
        arrival_slot=profile.arrival_slot,
        size=1.0,
        processing_density=1.0,
        timeout_length=profile.phi,
        absolute_deadline_slot=compute_absolute_deadline(profile.arrival_slot, profile.phi),
        completion_slot=completion_slot,
        terminal_outcome="completed" if terminal_status in COMPLETED_STATUSES else "dropped",
        reward_emitted=True,
    )
    if policy_action == "local":
        return reward_for_terminal_task(task)
    if policy_action == "vertical":
        return reward_for_terminal_task(task)
    raise ValueError("task_reward only supports local or vertical actions")


def _horizontal_reward(profile: ScenarioActionProfile, destination_agent_id: str, completion_slot: int, terminal_status: str) -> float:
    if terminal_status in COMPLETED_STATUSES:
        selected_phi = select_phi(
            False,
            phi_private(psi_priv=completion_slot, t=profile.arrival_slot),
            phi_public(((1, int(destination_agent_id)), (0, 9)), t=profile.arrival_slot),
        )
        return reward_from_terminal_state(True, terminal_status, selected_phi, profile.drop_penalty)
    return reward_from_terminal_state(True, terminal_status, None, profile.drop_penalty)


def _metrics_from_outcome(
    *,
    terminal_status: str,
    reward_value: float | None,
    delay: float | None,
    action_legality: str,
    compatibility_mode_used: bool = False,
) -> tuple[int, int, int, int, int, float, float, int, bool]:
    completed_count = 1 if terminal_status in COMPLETED_STATUSES else 0
    dropped_timeout_count = 1 if terminal_status == "dropped_timeout" else 0
    dropped_unavailable_count = 1 if terminal_status == "dropped_unavailable" else 0
    deadline_violation_count = 1 if terminal_status == "dropped_timeout" else 0
    illegal_action_rejection_count = 1 if action_legality in {"illegal_unavailable", "illegal_self_destination"} else 0
    average_delay = float(delay if delay is not None else 0.0)
    average_reward = float(reward_value if reward_value is not None else 0.0)
    paper_mode_success_count = 1 if terminal_status in COMPLETED_STATUSES else 0
    return (
        completed_count,
        dropped_timeout_count,
        dropped_unavailable_count,
        deadline_violation_count,
        illegal_action_rejection_count,
        average_delay,
        average_reward,
        paper_mode_success_count,
        compatibility_mode_used,
    )


def _build_zero_metrics() -> tuple[int, int, int, int, int, float, float, int, bool]:
    return (0, 0, 0, 0, 0, 0.0, 0.0, 0, False)


def _to_metrics(values: tuple[int, int, int, int, int, float, float, int, bool]):
    from src.analysis.controlled_evaluation_batch_readiness.model import ControlledEvaluationMetrics

    return ControlledEvaluationMetrics(
        completed_count=values[0],
        dropped_timeout_count=values[1],
        dropped_unavailable_count=values[2],
        deadline_violation_count=values[3],
        illegal_action_rejection_count=values[4],
        average_delay=values[5],
        average_reward=values[6],
        paper_mode_success_count=values[7],
        compatibility_mode_used=values[8],
    )


def _unmapped_outcome(policy_id: str, scenario_id: str, selected_action_id: str) -> PolicyActionBoundOutcome:
    return PolicyActionBoundOutcome(
        policy_id=policy_id,
        scenario_id=scenario_id,
        selected_action_id=selected_action_id,
        selected_action_family="unmapped",
        action_legality="unmapped",
        terminal_status="",
        reward_value=None,
        delay=None,
        action_bound_metrics_derived=False,
        metrics=_to_metrics(_build_zero_metrics()),
        evidence_source="unmapped_selected_action",
    )


def _local_outcome(policy_id: str, scenario_id: str, selected_action_id: str, profile: ScenarioActionProfile) -> PolicyActionBoundOutcome:
    completion_slot = profile.local_completion_slot
    success_before_deadline = is_success_before_deadline(completion_slot, profile.arrival_slot, profile.phi)
    terminal_status = terminal_status_from_completion(
        completion_slot,
        profile.arrival_slot,
        profile.phi,
        completion_kind="private",
    )
    reward_value = (
        _task_reward("local", profile, completion_slot, terminal_status)
        if success_before_deadline
        else reward_from_terminal_state(True, "dropped_timeout", None, profile.drop_penalty)
    )
    delay = float(reward_slot_for_terminal(completion_slot) - profile.arrival_slot)
    action_legality = "legal"
    metrics = _to_metrics(
        _metrics_from_outcome(
            terminal_status=terminal_status,
            reward_value=reward_value,
            delay=delay,
            action_legality=action_legality,
        )
    )
    return PolicyActionBoundOutcome(
        policy_id=policy_id,
        scenario_id=scenario_id,
        selected_action_id=selected_action_id,
        selected_action_family="local",
        action_legality=action_legality,
        terminal_status=terminal_status,
        reward_value=reward_value,
        delay=delay,
        action_bound_metrics_derived=True,
        metrics=metrics,
        evidence_source="feature_071.paper_timeout_and_reward_timing.local_private_path",
    )


def _vertical_outcome(policy_id: str, scenario_id: str, selected_action_id: str, profile: ScenarioActionProfile) -> PolicyActionBoundOutcome:
    completion_slot = profile.cloud_completion_slot
    success_before_deadline = is_success_before_deadline(completion_slot, profile.arrival_slot, profile.phi)
    terminal_status = terminal_status_from_completion(
        completion_slot,
        profile.arrival_slot,
        profile.phi,
        completion_kind="cloud",
    )
    reward_value = (
        _task_reward("vertical", profile, completion_slot, terminal_status)
        if success_before_deadline
        else reward_from_terminal_state(True, "dropped_timeout", None, profile.drop_penalty)
    )
    delay = float(reward_slot_for_terminal(completion_slot) - profile.arrival_slot)
    action_legality = "legal"
    metrics = _to_metrics(
        _metrics_from_outcome(
            terminal_status=terminal_status,
            reward_value=reward_value,
            delay=delay,
            action_legality=action_legality,
        )
    )
    return PolicyActionBoundOutcome(
        policy_id=policy_id,
        scenario_id=scenario_id,
        selected_action_id=selected_action_id,
        selected_action_family="vertical",
        action_legality=action_legality,
        terminal_status=terminal_status,
        reward_value=reward_value,
        delay=delay,
        action_bound_metrics_derived=True,
        metrics=metrics,
        evidence_source="feature_071.paper_timeout_and_reward_timing.cloud_vertical_path",
    )


def _horizontal_destination(
    selected_action_id: str,
    context: PolicyContext,
    profile: ScenarioActionProfile,
) -> str | None:
    if selected_action_id.isdigit():
        return selected_action_id
    if selected_action_id in {"horizontal", "offload_horizontal"}:
        return profile.legal_horizontal_destination
    legal_destinations = context.observation.get("horizontal_destinations")
    if isinstance(legal_destinations, (tuple, list)) and legal_destinations:
        for destination in legal_destinations:
            if isinstance(destination, str) and destination:
                return destination
    return None


def _horizontal_action_legality(
    *,
    selected_action_id: str,
    source_agent_id: str,
    destination_agent_id: str,
    context: PolicyContext,
) -> str:
    if not selected_action_id:
        return "unmapped"
    if destination_agent_id == source_agent_id:
        return "illegal_self_destination"
    mask_value = context.legal_action_mask.get(selected_action_id)
    if mask_value is False:
        return "illegal_unavailable"
    if not _is_horizontal_neighbor(source_agent_id, destination_agent_id):
        return "illegal_unavailable"
    return "legal"


def _horizontal_outcome(
    policy_id: str,
    scenario_id: str,
    selected_action_id: str,
    context: PolicyContext,
    profile: ScenarioActionProfile,
) -> PolicyActionBoundOutcome:
    destination_agent_id = _horizontal_destination(selected_action_id, context, profile)
    if destination_agent_id is None:
        return _unmapped_outcome(policy_id, scenario_id, selected_action_id)

    source_agent_id = profile.horizontal_source
    action_legality = _horizontal_action_legality(
        selected_action_id=selected_action_id,
        source_agent_id=source_agent_id,
        destination_agent_id=destination_agent_id,
        context=context,
    )
    if action_legality == "unmapped":
        return _unmapped_outcome(policy_id, scenario_id, selected_action_id)

    completion_slot = profile.horizontal_completion_slot
    success_before_deadline = is_success_before_deadline(completion_slot, profile.arrival_slot, profile.phi)
    if action_legality == "legal":
        terminal_status = terminal_status_from_completion(
            completion_slot,
            profile.arrival_slot,
            profile.phi,
            completion_kind="public",
        )
        reward_value = (
            _horizontal_reward(profile, destination_agent_id, completion_slot, terminal_status)
            if success_before_deadline
            else reward_from_terminal_state(True, "dropped_timeout", None, profile.drop_penalty)
        )
    else:
        terminal_status = "dropped_unavailable"
        reward_value = reward_from_terminal_state(True, terminal_status, None, profile.drop_penalty)

    delay = float(reward_slot_for_terminal(completion_slot) - profile.arrival_slot)
    metrics = _to_metrics(
        _metrics_from_outcome(
            terminal_status=terminal_status,
            reward_value=reward_value,
            delay=delay,
            action_legality=action_legality,
        )
    )
    return PolicyActionBoundOutcome(
        policy_id=policy_id,
        scenario_id=scenario_id,
        selected_action_id=selected_action_id,
        selected_action_family="horizontal",
        action_legality=action_legality,
        terminal_status=terminal_status,
        reward_value=reward_value,
        delay=delay,
        action_bound_metrics_derived=True,
        metrics=metrics,
        evidence_source="feature_070.figure_7_topology + feature_071.paper_timeout_and_reward_timing.horizontal_path",
    )


def build_action_bound_outcome(
    policy_id: str,
    scenario_id: str,
    selected_action: object,
    context: PolicyContext,
) -> PolicyActionBoundOutcome:
    selected_action_id = _normalize_action_id(selected_action)
    if not selected_action_id:
        return _unmapped_outcome(policy_id, scenario_id, selected_action_id)

    selected_action_family = runtime_action_family(selected_action_id)
    profile = _scenario_profile(scenario_id)
    if selected_action_family == "local":
        return _local_outcome(policy_id, scenario_id, selected_action_id, profile)
    if selected_action_family == "vertical":
        return _vertical_outcome(policy_id, scenario_id, selected_action_id, profile)
    if selected_action_family == "horizontal":
        return _horizontal_outcome(policy_id, scenario_id, selected_action_id, context, profile)
    return _unmapped_outcome(policy_id, scenario_id, selected_action_id)


def _scenario_context(policy_id: str, scenario_id: str) -> PolicyContext:
    profile = _scenario_profile(scenario_id)
    horizontal_destinations = ("6", "11", "16")
    if scenario_id == "illegal_horizontal_destination_attempt":
        horizontal_destinations = (profile.illegal_horizontal_destination, "6", "11", "16")

    legal_action_mask = {
        "local": True,
        "compute_local": True,
        "horizontal": True,
        "offload_horizontal": True,
        "vertical": True,
        "offload_vertical": True,
        "cloud": True,
        "6": True,
        "11": True,
        "16": True,
        "2": scenario_id != "illegal_horizontal_destination_attempt",
    }
    observation = {
        "scenario_id": scenario_id,
        "source_agent_id": profile.horizontal_source,
        "local_action": "local",
        "cloud_action": "cloud",
        "horizontal_destinations": horizontal_destinations,
        "edge_agent_ids": horizontal_destinations,
        "placement_actions": {
            "local": "local",
            "vertical": "cloud",
            "horizontal": horizontal_destinations,
        },
        "fallback_hints": {"local": 1.0, "horizontal": 2.0, "vertical": 3.0},
        "balance_hint": {"local": 1.0, "horizontal": 2.0, "vertical": 3.0},
        "mleo_delay_candidates": {
            "local": {"total_delay": 3.0},
            "horizontal": {"total_delay": 4.0},
            "vertical": {"total_delay": 5.0},
        },
        "mleo_placement_candidates": [
            {"action_id": "local", "action_family": "local", "total_delay": 3.0},
            {"action_id": "cloud", "action_family": "vertical", "total_delay": 5.0},
            {"action_id": "6", "action_family": "horizontal", "total_delay": 4.0},
        ],
        "policy_id": policy_id,
    }
    return PolicyContext(observation=observation, legal_action_mask=legal_action_mask, trace_history=(policy_id, scenario_id))


def build_required_policy_descriptors() -> tuple[BaselinePolicyDescriptor, ...]:
    descriptors: list[BaselinePolicyDescriptor] = []
    for policy_id in REQUIRED_POLICY_IDS:
        try:
            policy = PolicyRegistry.resolve(policy_id)
        except Exception:
            descriptors.append(
                BaselinePolicyDescriptor(
                    policy_id=policy_id,
                    policy_family=_policy_family_label(policy_id),
                    registry_key=policy_id,
                    available=False,
                    decision_trace_supported=False,
                )
            )
            continue
        expected_type = _expected_policy_type(policy_id)
        available = isinstance(policy, expected_type)
        descriptors.append(
            BaselinePolicyDescriptor(
                policy_id=policy_id,
                policy_family=_policy_family_label(policy_id),
                registry_key=policy_id,
                available=available,
                decision_trace_supported=available and hasattr(policy, "choose_action"),
            )
        )
    return tuple(descriptors)


def build_policy_scenario_comparisons() -> tuple[PolicyScenarioComparison, ...]:
    _feature_073_report()
    descriptors = {descriptor.policy_id: descriptor for descriptor in build_required_policy_descriptors()}
    comparisons: list[PolicyScenarioComparison] = []
    for policy_id in REQUIRED_POLICY_IDS:
        descriptor = descriptors[policy_id]
        policy = PolicyRegistry.resolve(policy_id) if descriptor.available else None
        for scenario_id in REQUIRED_SCENARIO_IDS:
            context = _scenario_context(policy_id, scenario_id)
            selected_action_id = ""
            selected_action_family = "unmapped"
            decision_trace: tuple[str, ...] = ()
            policy_decision_trace_present = False
            passed = False
            if descriptor.available and policy is not None:
                try:
                    selected_action = policy.choose_action(context)
                    selected_action_id = _normalize_action_id(selected_action)
                    selected_action_family = runtime_action_family(selected_action_id) if selected_action_id else "unmapped"
                    outcome = build_action_bound_outcome(policy_id, scenario_id, selected_action, context)
                    decision_trace = (
                        f"policy_id={policy_id}",
                        f"scenario_id={scenario_id}",
                        f"selected_action_id={outcome.selected_action_id}",
                        f"selected_action_family={outcome.selected_action_family}",
                        f"action_legality={outcome.action_legality}",
                        f"action_bound_terminal_status={outcome.terminal_status}",
                    )
                    policy_decision_trace_present = True
                    passed = bool(
                        outcome.action_legality != "unmapped"
                        and outcome.action_bound_metrics_derived
                        and not outcome.metrics.compatibility_mode_used
                        and policy_decision_trace_present
                    )
                except Exception:
                    outcome = _unmapped_outcome(policy_id, scenario_id, selected_action_id)
            else:
                outcome = _unmapped_outcome(policy_id, scenario_id, selected_action_id)
            comparisons.append(
                PolicyScenarioComparison(
                    policy_id=policy_id,
                    scenario_id=scenario_id,
                    policy_action_family=_policy_family_label(policy_id),
                    policy_decision_trace_present=policy_decision_trace_present,
                    decision_trace=decision_trace,
                    selected_action_id=outcome.selected_action_id,
                    selected_action_family=outcome.selected_action_family,
                    action_legality=outcome.action_legality,
                    action_bound_terminal_status=outcome.terminal_status,
                    action_bound_reward_value=outcome.reward_value,
                    action_bound_metrics_derived=outcome.action_bound_metrics_derived,
                    metrics=outcome.metrics,
                    compatibility_mode_used=False,
                    passed=passed,
                )
            )
    return tuple(comparisons)


def compute_policy_aggregate_metrics(
    policy_id: str,
    scenario_comparisons: Sequence[PolicyScenarioComparison],
) -> PolicyAggregateComparison:
    rows = tuple(scenario_comparisons)
    if not rows:
        raise ValueError("policy aggregates require at least one scenario comparison")
    if any(row.policy_id != policy_id for row in rows):
        raise ValueError("scenario comparisons must belong to the requested policy")
    return aggregate_policy_rows(rows)


def _feature_068r_regression_evidence() -> BaselinePolicyComparativeRegressionEvidence:
    report = build_feature_069_report()
    evidence = report.feature_068r_regression_status
    return BaselinePolicyComparativeRegressionEvidence(
        name="Feature 068R regression",
        passed=evidence.passed,
        summary="Feature 068R baseline policy fidelity remains green and continues to cover the required policy registry contract.",
        validation_commands=evidence.validation_commands,
    )


def _feature_069_regression_evidence() -> BaselinePolicyComparativeRegressionEvidence:
    report = build_feature_069_report()
    return BaselinePolicyComparativeRegressionEvidence(
        name="Feature 069 regression",
        passed=report.passed,
        summary="Feature 069 full HOODIE mechanism fidelity batch remains green and continues to serve as prerequisite evidence.",
        validation_commands=report.validation_commands,
    )


def _feature_070_regression_evidence() -> BaselinePolicyComparativeRegressionEvidence:
    report = _feature_070_report()
    return BaselinePolicyComparativeRegressionEvidence(
        name="Feature 070 regression",
        passed=report.passed and report.status == "blocker_resolution_readiness_with_runtime_divergence",
        summary="Feature 070 topology, timeout/drop, and reward evidence remains green with runtime divergence still explicit.",
        validation_commands=(VALIDATION_COMMANDS[2],),
    )


def _feature_071_regression_evidence() -> BaselinePolicyComparativeRegressionEvidence:
    report = _feature_071_report()
    return BaselinePolicyComparativeRegressionEvidence(
        name="Feature 071 regression",
        passed=report.passed and report.status == "runtime_paper_faithful_semantics_alignment_ready",
        summary="Feature 071 runtime helper alignment remains green with paper mode default and explicit compatibility mode only.",
        validation_commands=tuple(VALIDATION_COMMANDS[3:5]),
    )


def _feature_072_regression_evidence() -> BaselinePolicyComparativeRegressionEvidence:
    report = _feature_072_report()
    return BaselinePolicyComparativeRegressionEvidence(
        name="Feature 072 regression",
        passed=report.passed and report.status == "end_to_end_golden_trace_validation_ready",
        summary="Feature 072 deterministic golden trace validation remains green and is consumed as prerequisite evidence.",
        validation_commands=tuple(VALIDATION_COMMANDS[5:7]),
    )


def _feature_073_regression_evidence() -> BaselinePolicyComparativeRegressionEvidence:
    report = _feature_073_report()
    return BaselinePolicyComparativeRegressionEvidence(
        name="Feature 073 regression",
        passed=report.passed and report.status == "controlled_evaluation_batch_readiness_ready",
        summary="Feature 073 controlled evaluation batch readiness remains green and provides the scenario universe for Feature 074.",
        validation_commands=tuple(VALIDATION_COMMANDS[7:9]),
    )


def _claim_boundary() -> str:
    return (
        "No final evaluation claim is made. No performance superiority claim is made. No statistical significance claim "
        "is made. No full paper reproduction claim is made. Feature 073 controlled scenarios are used as fixtures, not "
        "copied final metrics. Selected policy actions are bound to controlled outcomes. Local/private actions map to "
        "local/private outcome semantics. Vertical/cloud actions map to cloud outcome semantics. Horizontal actions are "
        "checked against Feature 070 Figure 7 topology before public outcome metrics are assigned. Feature 071 helpers "
        "provide the paper-mode terminal and reward behavior. Compatibility mode is excluded from the default "
        "comparison. Feature 075 is the next proposed deadline-aware method integration readiness step, not training."
    )


def build_feature_074_report(
    changed_files: Sequence[str] | None = None,
    validation_commands: Sequence[str] | None = None,
) -> BaselineComparativeReadinessReport:
    checked_changed_files = tuple(validate_scope(DEFAULT_CHANGED_FILES if changed_files is None else changed_files))
    descriptors = build_required_policy_descriptors()
    comparisons = build_policy_scenario_comparisons()
    aggregates = tuple(
        compute_policy_aggregate_metrics(policy_id, tuple(row for row in comparisons if row.policy_id == policy_id))
        for policy_id in REQUIRED_POLICY_IDS
    )
    feature_068r = _feature_068r_regression_evidence()
    feature_069 = _feature_069_regression_evidence()
    feature_070 = _feature_070_regression_evidence()
    feature_071 = _feature_071_regression_evidence()
    feature_072 = _feature_072_regression_evidence()
    feature_073 = _feature_073_regression_evidence()
    passed = bool(
        all(descriptor.available for descriptor in descriptors)
        and all(descriptor.decision_trace_supported for descriptor in descriptors)
        and all(comparison.passed for comparison in comparisons)
        and all(comparison.action_bound_metrics_derived for comparison in comparisons)
        and all(aggregate.action_bound_metrics_derived for aggregate in aggregates)
        and all(not aggregate.compatibility_mode_used for aggregate in aggregates)
        and feature_068r.passed
        and feature_069.passed
        and feature_070.passed
        and feature_071.passed
        and feature_072.passed
        and feature_073.passed
    )
    status = FEATURE_074_STATUS_READY if passed else FEATURE_074_STATUS_WITH_BLOCKERS
    regression_commands = tuple(validation_commands) if validation_commands is not None else tuple(VALIDATION_COMMANDS)
    return BaselineComparativeReadinessReport(
        feature_name="Feature 074 - Baseline Policy Comparative Evaluation Readiness",
        status=status,
        passed=passed,
        changed_files=checked_changed_files,
        policy_descriptors=descriptors,
        scenario_comparisons=comparisons,
        policy_aggregate_metrics=aggregates,
        feature_068r_regression_status=feature_068r,
        feature_069_regression_status=feature_069,
        feature_070_regression_status=feature_070,
        feature_071_regression_status=feature_071,
        feature_072_regression_status=feature_072,
        feature_073_regression_status=feature_073,
        paper_claim_boundary=_claim_boundary(),
        recommended_next_feature=FEATURE_074_RECOMMENDATION,
    )


def render_feature_074_report(report: BaselineComparativeReadinessReport) -> str:
    payload = report.to_dict()
    descriptor_sections = [
        "\n".join(
            [
                f"### {descriptor['policy_id']}",
                _json_dump(descriptor).rstrip(),
            ]
        )
        for descriptor in payload["policy_descriptors"]
    ]
    scenario_sections = [
        "\n".join(
            [
                f"### {comparison['policy_id']} / {comparison['scenario_id']}",
                _json_dump(comparison).rstrip(),
            ]
        )
        for comparison in payload["scenario_comparisons"]
    ]
    aggregate_sections = [
        "\n".join(
            [
                f"### {aggregate['policy_id']}",
                _json_dump(aggregate).rstrip(),
            ]
        )
        for aggregate in payload["policy_aggregate_metrics"]
    ]
    regression_sections = []
    for name in (
        "feature_068r_regression_status",
        "feature_069_regression_status",
        "feature_070_regression_status",
        "feature_071_regression_status",
        "feature_072_regression_status",
        "feature_073_regression_status",
    ):
        regression_sections.append(f"### {payload[name]['name']}\n{_json_dump(payload[name]).rstrip()}")
    return "\n".join(
        [
            "# Feature 074 Baseline Policy Comparative Evaluation Readiness Report",
            "",
            f"- feature_name: `{payload['feature_name']}`",
            f"- status: `{payload['status']}`",
            f"- passed: `{payload['passed']}`",
            f"- recommended_next_feature: {payload['recommended_next_feature']}",
            "",
            "## Claim Boundary",
            payload["paper_claim_boundary"],
            "",
            "## Comparative Scope",
            "Feature 072 report is consumed as prerequisite evidence.",
            "Feature 073 controlled scenarios are used as fixtures, not copied final metrics.",
            "Selected policy actions are bound to controlled outcomes.",
            "Local/private selected actions map to local/private controlled outcomes.",
            "Vertical/cloud selected actions map to cloud/vertical controlled outcomes.",
            "Horizontal selected actions use Feature 070 Figure 7 topology.",
            "Feature 071 helpers are used for paper-mode terminal and reward behavior.",
            "Compatibility mode is excluded from the default comparison.",
            "No final evaluation claim is made.",
            "No performance superiority claim is made.",
            "No statistical significance claim is made.",
            "No full paper reproduction claim is made.",
            "",
            "## Policy Descriptors",
            *descriptor_sections,
            "",
            "## Scenario Comparisons",
            *scenario_sections,
            "",
            "## Policy Aggregate Metrics",
            *aggregate_sections,
            "",
            "## Regression Evidence",
            *regression_sections,
            "",
        ]
    )


def write_feature_074_report(output_dir: Path | str = DEFAULT_OUTPUT_DIR) -> Path:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    report = build_feature_074_report()
    markdown_path = output_path / "feature-074-baseline-policy-comparative-evaluation-readiness-report.md"
    json_path = output_path / "feature-074-baseline-policy-comparative-evaluation-readiness-report.json"
    markdown_path.write_text(render_feature_074_report(report), encoding="utf-8")
    json_path.write_text(_json_dump(report.to_dict()), encoding="utf-8")
    return markdown_path
