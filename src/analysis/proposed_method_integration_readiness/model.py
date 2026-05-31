from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from src.analysis.controlled_evaluation_batch_readiness.model import ControlledEvaluationMetrics


PROPOSED_METHOD_POLICY_ID = "PROPOSED_DCQ"
PROPOSED_METHOD_POLICY_FAMILY = "proposed_deadline_queueing"
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
class ProposedMethodDescriptor:
    policy_id: str
    policy_family: str
    registry_key: str
    available: bool
    decision_trace_supported: bool

    def __post_init__(self) -> None:
        if self.policy_id != PROPOSED_METHOD_POLICY_ID:
            raise ValueError("policy_id must be PROPOSED_DCQ")
        if self.policy_family != PROPOSED_METHOD_POLICY_FAMILY:
            raise ValueError("policy_family must be proposed_deadline_queueing")
        if not self.registry_key:
            raise ValueError("registry_key must be non-empty")
        if self.available not in {True, False}:
            raise ValueError("available must be boolean")
        if self.decision_trace_supported not in {True, False}:
            raise ValueError("decision_trace_supported must be boolean")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ProposedMethodCandidate:
    action_id: str
    action_family: str
    legal: bool
    estimated_delay: float
    deadline_slack: float
    queue_or_load_value: float
    reward_risk_value: float
    ranking_score: float
    selected: bool

    def __post_init__(self) -> None:
        if not self.action_id:
            raise ValueError("action_id must be non-empty")
        if not self.action_family:
            raise ValueError("action_family must be non-empty")
        if self.estimated_delay < 0:
            raise ValueError("estimated_delay must be non-negative")
        if self.ranking_score != self.ranking_score:
            raise ValueError("ranking_score must be a real number")
        if self.selected and not self.legal:
            raise ValueError("selected candidate must be legal")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ProposedMethodScenarioEvaluation:
    scenario_id: str
    candidate_evidence: tuple[ProposedMethodCandidate, ...]
    candidate_ranking_trace: tuple[str, ...]
    candidate_ranking_trace_present: bool
    deadline_slack_evidence_present: bool
    queue_or_load_evidence_present: bool
    topology_legality_enforced: bool
    action_legality: str
    selected_action_id: str
    selected_action_family: str
    action_bound_terminal_status: str
    action_bound_reward_value: float | None
    action_bound_metrics_derived: bool
    metrics: ControlledEvaluationMetrics
    compatibility_mode_used: bool
    passed: bool

    def __post_init__(self) -> None:
        if not self.scenario_id:
            raise ValueError("scenario_id must be non-empty")
        if not self.candidate_evidence:
            raise ValueError("candidate_evidence must be non-empty")
        if self.candidate_ranking_trace_present != bool(self.candidate_ranking_trace):
            raise ValueError("candidate_ranking_trace_present must match candidate_ranking_trace presence")
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
            if not self.candidate_ranking_trace_present:
                raise ValueError("passed rows must have candidate ranking evidence")
            if not self.deadline_slack_evidence_present:
                raise ValueError("passed rows must have deadline slack evidence")
            if not self.queue_or_load_evidence_present:
                raise ValueError("passed rows must have queue/load evidence")
            if not self.topology_legality_enforced:
                raise ValueError("passed rows must enforce topology legality")
            if not self.action_bound_terminal_status:
                raise ValueError("passed rows must have action_bound_terminal_status")
            if self.action_bound_reward_value is None:
                raise ValueError("passed rows must have action_bound_reward_value")
            if not self.action_bound_metrics_derived:
                raise ValueError("passed rows must have action_bound_metrics_derived set")
            if self.compatibility_mode_used:
                raise ValueError("passed rows must not use compatibility mode")

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "candidate_evidence": [candidate.to_dict() for candidate in self.candidate_evidence],
            "candidate_ranking_trace": list(self.candidate_ranking_trace),
            "candidate_ranking_trace_present": self.candidate_ranking_trace_present,
            "deadline_slack_evidence_present": self.deadline_slack_evidence_present,
            "queue_or_load_evidence_present": self.queue_or_load_evidence_present,
            "topology_legality_enforced": self.topology_legality_enforced,
            "action_legality": self.action_legality,
            "selected_action_id": self.selected_action_id,
            "selected_action_family": self.selected_action_family,
            "action_bound_terminal_status": self.action_bound_terminal_status,
            "action_bound_reward_value": self.action_bound_reward_value,
            "action_bound_metrics_derived": self.action_bound_metrics_derived,
            "metrics": self.metrics.to_dict(),
            "compatibility_mode_used": self.compatibility_mode_used,
            "passed": self.passed,
        }


@dataclass(frozen=True, slots=True)
class ProposedMethodAggregateComparison:
    policy_id: str
    policy_family: str
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
    candidate_ranking_trace_present: bool
    deadline_slack_evidence_present: bool
    queue_or_load_evidence_present: bool
    topology_legality_enforced: bool
    action_bound_metrics_derived: bool

    def __post_init__(self) -> None:
        if self.policy_id != PROPOSED_METHOD_POLICY_ID:
            raise ValueError("policy_id must be PROPOSED_DCQ")
        if self.policy_family != PROPOSED_METHOD_POLICY_FAMILY:
            raise ValueError("policy_family must be proposed_deadline_queueing")
        if self.scenario_count <= 0:
            raise ValueError("scenario_count must be positive")
        if any(not family for family in self.distinct_selected_action_families):
            raise ValueError("distinct_selected_action_families must contain explicit labels")

    def to_dict(self) -> dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "policy_family": self.policy_family,
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
            "candidate_ranking_trace_present": self.candidate_ranking_trace_present,
            "deadline_slack_evidence_present": self.deadline_slack_evidence_present,
            "queue_or_load_evidence_present": self.queue_or_load_evidence_present,
            "topology_legality_enforced": self.topology_legality_enforced,
            "action_bound_metrics_derived": self.action_bound_metrics_derived,
        }


@dataclass(frozen=True, slots=True)
class ProposedMethodRegressionEvidence:
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
class ProposedMethodIntegrationReadinessReport:
    feature_name: str
    status: str
    passed: bool
    changed_files: tuple[str, ...]
    proposed_method_descriptor: ProposedMethodDescriptor
    scenario_evaluations: tuple[ProposedMethodScenarioEvaluation, ...]
    policy_aggregate_metrics: tuple[ProposedMethodAggregateComparison, ...]
    feature_068r_regression_status: ProposedMethodRegressionEvidence
    feature_069_regression_status: ProposedMethodRegressionEvidence
    feature_070_regression_status: ProposedMethodRegressionEvidence
    feature_071_regression_status: ProposedMethodRegressionEvidence
    feature_072_regression_status: ProposedMethodRegressionEvidence
    feature_073_regression_status: ProposedMethodRegressionEvidence
    feature_074_regression_status: ProposedMethodRegressionEvidence
    paper_claim_boundary: str
    recommended_next_feature: str

    def __post_init__(self) -> None:
        if self.feature_name != "Feature 075 - Proposed Method Integration Readiness":
            raise ValueError("feature_name must match the Feature 075 contract")
        if self.status not in {
            "proposed_method_integration_readiness_ready",
            "proposed_method_integration_readiness_with_blockers",
        }:
            raise ValueError("status must be explicit and recognized")
        if not self.recommended_next_feature:
            raise ValueError("recommended_next_feature must be non-empty")
        if not _claim_boundary_is_explicit(self.paper_claim_boundary):
            raise ValueError("paper_claim_boundary must explicitly state the claim boundary")

        scenario_ids = [evaluation.scenario_id for evaluation in self.scenario_evaluations]
        if len(scenario_ids) != len(REQUIRED_SCENARIO_IDS):
            raise ValueError("scenario_evaluations must cover every required scenario")
        if set(scenario_ids) != set(REQUIRED_SCENARIO_IDS):
            raise ValueError("scenario_evaluations must cover the full required scenario set")

        aggregate_ids = [aggregate.policy_id for aggregate in self.policy_aggregate_metrics]
        if aggregate_ids != [PROPOSED_METHOD_POLICY_ID]:
            raise ValueError("policy_aggregate_metrics must contain the proposed method aggregate only")

        computed_aggregate = _aggregate_rows(self.scenario_evaluations)
        if self.policy_aggregate_metrics[0] != computed_aggregate:
            raise ValueError("policy_aggregate_metrics must match the deterministic scenario rows")

        expected_pass = bool(
            self.proposed_method_descriptor.available
            and self.proposed_method_descriptor.decision_trace_supported
            and all(evaluation.passed for evaluation in self.scenario_evaluations)
            and all(evaluation.candidate_ranking_trace_present for evaluation in self.scenario_evaluations)
            and all(evaluation.deadline_slack_evidence_present for evaluation in self.scenario_evaluations)
            and all(evaluation.queue_or_load_evidence_present for evaluation in self.scenario_evaluations)
            and all(evaluation.topology_legality_enforced for evaluation in self.scenario_evaluations)
            and all(evaluation.action_bound_metrics_derived for evaluation in self.scenario_evaluations)
            and all(not evaluation.compatibility_mode_used for evaluation in self.scenario_evaluations)
            and self.feature_068r_regression_status.passed
            and self.feature_069_regression_status.passed
            and self.feature_070_regression_status.passed
            and self.feature_071_regression_status.passed
            and self.feature_072_regression_status.passed
            and self.feature_073_regression_status.passed
            and self.feature_074_regression_status.passed
        )
        if self.passed != expected_pass:
            raise ValueError("passed must match the readiness gates")

        expected_status = (
            "proposed_method_integration_readiness_ready"
            if expected_pass
            else "proposed_method_integration_readiness_with_blockers"
        )
        if self.status != expected_status:
            raise ValueError("status must match the computed readiness state")

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_name": self.feature_name,
            "status": self.status,
            "passed": self.passed,
            "changed_files": list(self.changed_files),
            "proposed_method_descriptor": self.proposed_method_descriptor.to_dict(),
            "scenario_evaluations": [evaluation.to_dict() for evaluation in self.scenario_evaluations],
            "policy_aggregate_metrics": [aggregate.to_dict() for aggregate in self.policy_aggregate_metrics],
            "feature_068r_regression_status": self.feature_068r_regression_status.to_dict(),
            "feature_069_regression_status": self.feature_069_regression_status.to_dict(),
            "feature_070_regression_status": self.feature_070_regression_status.to_dict(),
            "feature_071_regression_status": self.feature_071_regression_status.to_dict(),
            "feature_072_regression_status": self.feature_072_regression_status.to_dict(),
            "feature_073_regression_status": self.feature_073_regression_status.to_dict(),
            "feature_074_regression_status": self.feature_074_regression_status.to_dict(),
            "paper_claim_boundary": self.paper_claim_boundary,
            "recommended_next_feature": self.recommended_next_feature,
        }


def _claim_boundary_is_explicit(paper_claim_boundary: str) -> bool:
    boundary = paper_claim_boundary.lower()
    required_phrases = (
        "no training claim is made",
        "no final evaluation claim is made",
        "no performance superiority claim is made",
        "no full paper reproduction claim is made",
    )
    return all(phrase in boundary for phrase in required_phrases)


def _aggregate_rows(rows: tuple[ProposedMethodScenarioEvaluation, ...]) -> ProposedMethodAggregateComparison:
    if not rows:
        raise ValueError("proposed method aggregate requires at least one scenario evaluation")
    policy_id = PROPOSED_METHOD_POLICY_ID
    scenario_count = len(rows)
    completed_count = sum(row.metrics.completed_count for row in rows)
    dropped_timeout_count = sum(row.metrics.dropped_timeout_count for row in rows)
    dropped_unavailable_count = sum(row.metrics.dropped_unavailable_count for row in rows)
    deadline_violation_count = sum(row.metrics.deadline_violation_count for row in rows)
    illegal_action_rejection_count = sum(row.metrics.illegal_action_rejection_count for row in rows)
    mean_delay = sum(row.metrics.average_delay for row in rows) / scenario_count
    mean_reward = sum(row.metrics.average_reward for row in rows) / scenario_count
    compatibility_mode_used = any(row.compatibility_mode_used for row in rows)
    distinct_selected_action_families = tuple(sorted({row.selected_action_family for row in rows}))
    candidate_ranking_trace_present = all(row.candidate_ranking_trace_present for row in rows)
    deadline_slack_evidence_present = all(row.deadline_slack_evidence_present for row in rows)
    queue_or_load_evidence_present = all(row.queue_or_load_evidence_present for row in rows)
    topology_legality_enforced = all(row.topology_legality_enforced for row in rows)
    action_bound_metrics_derived = all(row.action_bound_metrics_derived for row in rows)
    return ProposedMethodAggregateComparison(
        policy_id=policy_id,
        policy_family=PROPOSED_METHOD_POLICY_FAMILY,
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
        candidate_ranking_trace_present=candidate_ranking_trace_present,
        deadline_slack_evidence_present=deadline_slack_evidence_present,
        queue_or_load_evidence_present=queue_or_load_evidence_present,
        topology_legality_enforced=topology_legality_enforced,
        action_bound_metrics_derived=action_bound_metrics_derived,
    )


def aggregate_proposed_method_rows(
    rows: tuple[ProposedMethodScenarioEvaluation, ...],
) -> ProposedMethodAggregateComparison:
    return _aggregate_rows(rows)
