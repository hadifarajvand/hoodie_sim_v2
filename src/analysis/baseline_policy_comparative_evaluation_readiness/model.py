from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from src.analysis.controlled_evaluation_batch_readiness.model import ControlledEvaluationMetrics


REQUIRED_POLICY_IDS: tuple[str, ...] = ("FLC", "VO", "HO", "RO", "BCO", "MLEO")
REQUIRED_SCENARIO_IDS: tuple[str, ...] = (
    "light_load_no_deadline_pressure",
    "tight_deadline_pressure",
    "legal_horizontal_offload",
    "illegal_horizontal_destination_attempt",
    "cloud_vertical_fallback",
    "timeout_drop_case",
    "mixed_local_horizontal_cloud_candidates",
)
ALLOWED_ACTION_LEGALITIES: tuple[str, ...] = (
    "legal",
    "illegal_unavailable",
    "illegal_self_destination",
    "unmapped",
)


def _deep_equal(left: Any, right: Any) -> bool:
    if isinstance(left, float) and isinstance(right, float):
        if left != left and right != right:
            return True
    if isinstance(left, dict) and isinstance(right, dict):
        if left.keys() != right.keys():
            return False
        return all(_deep_equal(left[key], right[key]) for key in left)
    if isinstance(left, (list, tuple)) and isinstance(right, (list, tuple)):
        if len(left) != len(right):
            return False
        return all(_deep_equal(lv, rv) for lv, rv in zip(left, right))
    return left == right


@dataclass(frozen=True, slots=True)
class PolicyActionBoundOutcome:
    policy_id: str
    scenario_id: str
    selected_action_id: str
    selected_action_family: str
    action_legality: str
    terminal_status: str
    reward_value: float | None
    delay: float | None
    action_bound_metrics_derived: bool
    metrics: ControlledEvaluationMetrics
    evidence_source: str

    def __post_init__(self) -> None:
        if not self.policy_id:
            raise ValueError("policy_id must be non-empty")
        if not self.scenario_id:
            raise ValueError("scenario_id must be non-empty")
        if self.action_legality not in ALLOWED_ACTION_LEGALITIES:
            raise ValueError("action_legality must be explicit and supported")
        if self.action_legality == "unmapped" and self.action_bound_metrics_derived:
            raise ValueError("unmapped action outcomes must not report derived metrics")
        if self.action_legality != "unmapped" and not self.action_bound_metrics_derived:
            raise ValueError("mapped action outcomes must report derived metrics")
        if self.action_legality != "unmapped":
            if not self.selected_action_id:
                raise ValueError("mapped action outcomes require selected_action_id")
            if not self.selected_action_family:
                raise ValueError("mapped action outcomes require selected_action_family")
            if not self.terminal_status:
                raise ValueError("mapped action outcomes require terminal_status")
            if self.reward_value is None:
                raise ValueError("mapped action outcomes require reward_value")
            if self.delay is None:
                raise ValueError("mapped action outcomes require delay")
        if not self.evidence_source:
            raise ValueError("evidence_source must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "scenario_id": self.scenario_id,
            "selected_action_id": self.selected_action_id,
            "selected_action_family": self.selected_action_family,
            "action_legality": self.action_legality,
            "terminal_status": self.terminal_status,
            "reward_value": self.reward_value,
            "delay": self.delay,
            "action_bound_metrics_derived": self.action_bound_metrics_derived,
            "metrics": self.metrics.to_dict(),
            "evidence_source": self.evidence_source,
        }


def _aggregate_rows(rows: tuple["PolicyScenarioComparison", ...]) -> "PolicyAggregateComparison":
    if not rows:
        raise ValueError("policy aggregates require at least one scenario comparison")
    policy_id = rows[0].policy_id
    scenario_count = len(rows)
    completed_count = sum(row.metrics.completed_count for row in rows)
    dropped_timeout_count = sum(row.metrics.dropped_timeout_count for row in rows)
    dropped_unavailable_count = sum(row.metrics.dropped_unavailable_count for row in rows)
    deadline_violation_count = sum(row.metrics.deadline_violation_count for row in rows)
    illegal_action_rejection_count = sum(row.metrics.illegal_action_rejection_count for row in rows)
    mean_delay = sum(row.metrics.average_delay for row in rows) / scenario_count
    mean_reward = sum(row.metrics.average_reward for row in rows) / scenario_count
    compatibility_mode_used = any(row.compatibility_mode_used for row in rows)
    distinct_selected_action_families = tuple(
        sorted({row.selected_action_family or "unmapped" for row in rows})
    )
    action_bound_metrics_derived = all(row.action_bound_metrics_derived for row in rows)
    return PolicyAggregateComparison(
        policy_id=policy_id,
        scenario_count=scenario_count,
        completed_count=completed_count,
        dropped_timeout_count=dropped_timeout_count,
        dropped_unavailable_count=dropped_unavailable_count,
        deadline_violation_count=deadline_violation_count,
        illegal_action_rejection_count=illegal_action_rejection_count,
        mean_delay=mean_delay,
        mean_reward=mean_reward,
        compatibility_mode_used=compatibility_mode_used,
        distinct_selected_action_families=distinct_selected_action_families,
        action_bound_metrics_derived=action_bound_metrics_derived,
    )


@dataclass(frozen=True, slots=True)
class BaselinePolicyDescriptor:
    policy_id: str
    policy_family: str
    registry_key: str
    available: bool
    decision_trace_supported: bool

    def __post_init__(self) -> None:
        if not self.policy_id:
            raise ValueError("policy_id must be non-empty")
        if not self.policy_family:
            raise ValueError("policy_family must be non-empty")
        if not self.registry_key:
            raise ValueError("registry_key must be non-empty")
        if self.available not in {True, False}:
            raise ValueError("available must be boolean")
        if self.decision_trace_supported not in {True, False}:
            raise ValueError("decision_trace_supported must be boolean")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PolicyScenarioComparison:
    policy_id: str
    scenario_id: str
    policy_action_family: str
    policy_decision_trace_present: bool
    decision_trace: tuple[str, ...]
    selected_action_id: str
    selected_action_family: str
    action_legality: str
    action_bound_terminal_status: str
    action_bound_reward_value: float | None
    action_bound_metrics_derived: bool
    metrics: ControlledEvaluationMetrics
    compatibility_mode_used: bool
    passed: bool

    def __post_init__(self) -> None:
        if not self.policy_id:
            raise ValueError("policy_id must be non-empty")
        if not self.scenario_id:
            raise ValueError("scenario_id must be non-empty")
        if not self.policy_action_family:
            raise ValueError("policy_action_family must be non-empty")
        if self.policy_decision_trace_present != bool(self.decision_trace):
            raise ValueError("policy_decision_trace_present must match decision_trace presence")
        if self.action_legality not in ALLOWED_ACTION_LEGALITIES:
            raise ValueError("action_legality must be explicit and supported")
        if self.metrics.compatibility_mode_used != self.compatibility_mode_used:
            raise ValueError("metrics.compatibility_mode_used must match comparison compatibility flag")
        if self.passed:
            if not self.selected_action_id:
                raise ValueError("passed rows must have selected_action_id")
            if not self.selected_action_family:
                raise ValueError("passed rows must have selected_action_family")
            if self.action_legality == "unmapped":
                raise ValueError("passed rows must derive from a mapped selected action")
            if not self.action_bound_terminal_status:
                raise ValueError("passed rows must have action_bound_terminal_status")
            if self.action_bound_reward_value is None:
                raise ValueError("passed rows must have action_bound_reward_value")
            if not self.action_bound_metrics_derived:
                raise ValueError("passed rows must have action_bound_metrics_derived set")
            if self.compatibility_mode_used:
                raise ValueError("passed rows must not use compatibility mode")
            if not self.policy_decision_trace_present:
                raise ValueError("passed rows must have a policy decision trace")

    def to_dict(self) -> dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "scenario_id": self.scenario_id,
            "policy_action_family": self.policy_action_family,
            "policy_decision_trace_present": self.policy_decision_trace_present,
            "decision_trace": list(self.decision_trace),
            "selected_action_id": self.selected_action_id,
            "selected_action_family": self.selected_action_family,
            "action_legality": self.action_legality,
            "action_bound_terminal_status": self.action_bound_terminal_status,
            "action_bound_reward_value": self.action_bound_reward_value,
            "action_bound_metrics_derived": self.action_bound_metrics_derived,
            "metrics": self.metrics.to_dict(),
            "compatibility_mode_used": self.compatibility_mode_used,
            "passed": self.passed,
        }


@dataclass(frozen=True, slots=True)
class PolicyAggregateComparison:
    policy_id: str
    scenario_count: int
    completed_count: int
    dropped_timeout_count: int
    dropped_unavailable_count: int
    deadline_violation_count: int
    illegal_action_rejection_count: int
    mean_delay: float
    mean_reward: float
    compatibility_mode_used: bool
    distinct_selected_action_families: tuple[str, ...]
    action_bound_metrics_derived: bool

    def __post_init__(self) -> None:
        if not self.policy_id:
            raise ValueError("policy_id must be non-empty")
        if self.scenario_count <= 0:
            raise ValueError("scenario_count must be positive")
        for field_name in (
            "completed_count",
            "dropped_timeout_count",
            "dropped_unavailable_count",
            "deadline_violation_count",
            "illegal_action_rejection_count",
        ):
            if getattr(self, field_name) < 0:
                raise ValueError(f"{field_name} must be non-negative")
        if any(not family for family in self.distinct_selected_action_families):
            raise ValueError("distinct_selected_action_families must contain explicit labels")

    def to_dict(self) -> dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "scenario_count": self.scenario_count,
            "completed_count": self.completed_count,
            "dropped_timeout_count": self.dropped_timeout_count,
            "dropped_unavailable_count": self.dropped_unavailable_count,
            "deadline_violation_count": self.deadline_violation_count,
            "illegal_action_rejection_count": self.illegal_action_rejection_count,
            "mean_delay": self.mean_delay,
            "mean_reward": self.mean_reward,
            "compatibility_mode_used": self.compatibility_mode_used,
            "distinct_selected_action_families": list(self.distinct_selected_action_families),
            "action_bound_metrics_derived": self.action_bound_metrics_derived,
        }


@dataclass(frozen=True, slots=True)
class BaselinePolicyComparativeRegressionEvidence:
    name: str
    passed: bool
    summary: str
    validation_commands: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "passed": self.passed,
            "summary": self.summary,
            "validation_commands": list(self.validation_commands),
        }


@dataclass(frozen=True, slots=True)
class BaselineComparativeReadinessReport:
    feature_name: str
    status: str
    passed: bool
    changed_files: tuple[str, ...]
    policy_descriptors: tuple[BaselinePolicyDescriptor, ...]
    scenario_comparisons: tuple[PolicyScenarioComparison, ...]
    policy_aggregate_metrics: tuple[PolicyAggregateComparison, ...]
    feature_068r_regression_status: BaselinePolicyComparativeRegressionEvidence
    feature_069_regression_status: BaselinePolicyComparativeRegressionEvidence
    feature_070_regression_status: BaselinePolicyComparativeRegressionEvidence
    feature_071_regression_status: BaselinePolicyComparativeRegressionEvidence
    feature_072_regression_status: BaselinePolicyComparativeRegressionEvidence
    feature_073_regression_status: BaselinePolicyComparativeRegressionEvidence
    paper_claim_boundary: str
    recommended_next_feature: str

    def __post_init__(self) -> None:
        if self.feature_name != "Feature 074 - Baseline Policy Comparative Evaluation Readiness":
            raise ValueError("feature_name must match the Feature 074 contract")
        if self.status not in {
            "baseline_policy_comparative_evaluation_readiness_ready",
            "baseline_policy_comparative_evaluation_readiness_with_blockers",
        }:
            raise ValueError("status must be explicit and recognized")
        if not self.recommended_next_feature:
            raise ValueError("recommended_next_feature must be non-empty")
        if not _claim_boundary_is_explicit(self.paper_claim_boundary):
            raise ValueError("paper_claim_boundary must explicitly state the claim boundary")

        descriptor_ids = [descriptor.policy_id for descriptor in self.policy_descriptors]
        if len(descriptor_ids) != len(set(descriptor_ids)):
            raise ValueError("policy_descriptors must not contain duplicates")
        if set(descriptor_ids) != set(REQUIRED_POLICY_IDS):
            raise ValueError("policy_descriptors must cover every required baseline policy")

        scenario_ids = [comparison.scenario_id for comparison in self.scenario_comparisons]
        if len(scenario_ids) != len(REQUIRED_POLICY_IDS) * len(REQUIRED_SCENARIO_IDS):
            raise ValueError("scenario_comparisons must cover every policy/scenario pair")
        comparison_keys = {(comparison.policy_id, comparison.scenario_id) for comparison in self.scenario_comparisons}
        expected_keys = {
            (policy_id, scenario_id)
            for policy_id in REQUIRED_POLICY_IDS
            for scenario_id in REQUIRED_SCENARIO_IDS
        }
        if comparison_keys != expected_keys:
            raise ValueError("scenario_comparisons must cover the full required policy/scenario matrix")

        aggregate_ids = [aggregate.policy_id for aggregate in self.policy_aggregate_metrics]
        if len(aggregate_ids) != len(set(aggregate_ids)):
            raise ValueError("policy_aggregate_metrics must not contain duplicates")
        if set(aggregate_ids) != set(REQUIRED_POLICY_IDS):
            raise ValueError("policy_aggregate_metrics must cover every required baseline policy")

        computed_aggregates = {
            policy_id: _aggregate_rows(
                tuple(row for row in self.scenario_comparisons if row.policy_id == policy_id)
            )
            for policy_id in REQUIRED_POLICY_IDS
        }
        for aggregate in self.policy_aggregate_metrics:
            if aggregate != computed_aggregates[aggregate.policy_id]:
                raise ValueError("policy_aggregate_metrics must match the deterministic policy rows")

        expected_pass = bool(
            all(descriptor.available for descriptor in self.policy_descriptors)
            and all(descriptor.decision_trace_supported for descriptor in self.policy_descriptors)
            and all(comparison.passed for comparison in self.scenario_comparisons)
            and all(comparison.action_bound_metrics_derived for comparison in self.scenario_comparisons)
            and all(aggregate.action_bound_metrics_derived for aggregate in self.policy_aggregate_metrics)
            and all(aggregate.compatibility_mode_used is False for aggregate in self.policy_aggregate_metrics)
            and self.feature_068r_regression_status.passed
            and self.feature_069_regression_status.passed
            and self.feature_070_regression_status.passed
            and self.feature_071_regression_status.passed
            and self.feature_072_regression_status.passed
            and self.feature_073_regression_status.passed
        )
        if self.passed != expected_pass:
            raise ValueError("passed must match the readiness gates")

        expected_status = (
            "baseline_policy_comparative_evaluation_readiness_ready"
            if expected_pass
            else "baseline_policy_comparative_evaluation_readiness_with_blockers"
        )
        if self.status != expected_status:
            raise ValueError("status must match the computed readiness state")

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_name": self.feature_name,
            "status": self.status,
            "passed": self.passed,
            "changed_files": list(self.changed_files),
            "policy_descriptors": [descriptor.to_dict() for descriptor in self.policy_descriptors],
            "scenario_comparisons": [comparison.to_dict() for comparison in self.scenario_comparisons],
            "policy_aggregate_metrics": [aggregate.to_dict() for aggregate in self.policy_aggregate_metrics],
            "feature_068r_regression_status": self.feature_068r_regression_status.to_dict(),
            "feature_069_regression_status": self.feature_069_regression_status.to_dict(),
            "feature_070_regression_status": self.feature_070_regression_status.to_dict(),
            "feature_071_regression_status": self.feature_071_regression_status.to_dict(),
            "feature_072_regression_status": self.feature_072_regression_status.to_dict(),
            "feature_073_regression_status": self.feature_073_regression_status.to_dict(),
            "paper_claim_boundary": self.paper_claim_boundary,
            "recommended_next_feature": self.recommended_next_feature,
        }


def _claim_boundary_is_explicit(paper_claim_boundary: str) -> bool:
    boundary = paper_claim_boundary.lower()
    required_phrases = (
        "no final evaluation claim is made",
        "no performance superiority claim is made",
        "no statistical significance claim is made",
        "no full paper reproduction claim is made",
    )
    return all(phrase in boundary for phrase in required_phrases)


def aggregate_policy_rows(rows: tuple[PolicyScenarioComparison, ...]) -> PolicyAggregateComparison:
    return _aggregate_rows(rows)
