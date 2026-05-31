from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


REQUIRED_POLICY_IDS: tuple[str, ...] = ("FLC", "VO", "HO", "RO", "BCO", "MLEO", "PROPOSED_DCQ")
REQUIRED_SCENARIO_IDS: tuple[str, ...] = (
    "light_load_no_deadline_pressure",
    "tight_deadline_pressure",
    "legal_horizontal_offload",
    "illegal_horizontal_destination_attempt",
    "cloud_vertical_fallback",
    "timeout_drop_case",
    "mixed_local_horizontal_cloud_candidates",
)
ALLOWED_FEATURE_IDS: tuple[str, ...] = ("068R", "069", "070", "071", "072", "073", "074", "075")


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


def _is_non_negative_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


@dataclass(frozen=True, slots=True)
class CombinedPolicyRow:
    policy_id: str
    policy_family: str
    scenario_id: str
    selected_action_id: str
    selected_action_family: str
    action_legality: str
    action_bound_terminal_status: str
    action_bound_reward_value: float | None
    action_bound_metrics_derived: bool
    compatibility_mode_used: bool
    decision_trace_present: bool
    completed_count: int
    dropped_timeout_count: int
    dropped_unavailable_count: int
    deadline_violation_count: int
    illegal_action_rejection_count: int
    average_delay: float | None
    average_reward: float | None
    source_feature: str
    source_report_status: str

    def __post_init__(self) -> None:
        if not self.policy_id:
            raise ValueError("policy_id must be non-empty")
        if not self.policy_family:
            raise ValueError("policy_family must be non-empty")
        if self.scenario_id not in REQUIRED_SCENARIO_IDS:
            raise ValueError("scenario_id must be one of the required controlled scenarios")
        if not self.selected_action_id:
            raise ValueError("selected_action_id must be non-empty")
        if not self.selected_action_family:
            raise ValueError("selected_action_family must be non-empty")
        if not self.action_legality:
            raise ValueError("action_legality must be non-empty")
        if not self.action_bound_terminal_status:
            raise ValueError("action_bound_terminal_status must be non-empty")
        if not self.action_bound_metrics_derived:
            raise ValueError("action_bound_metrics_derived must be true for readiness-valid rows")
        if self.compatibility_mode_used:
            raise ValueError("compatibility_mode_used must be false for readiness-valid rows")
        if not self.decision_trace_present:
            raise ValueError("decision_trace_present must be true for readiness-valid rows")
        for field_name in (
            "completed_count",
            "dropped_timeout_count",
            "dropped_unavailable_count",
            "deadline_violation_count",
            "illegal_action_rejection_count",
        ):
            if not _is_non_negative_int(getattr(self, field_name)):
                raise ValueError(f"{field_name} must be a non-negative integer")
        if self.source_feature not in {"074", "075"}:
            raise ValueError("source_feature must be either 074 or 075")
        if not self.source_report_status:
            raise ValueError("source_report_status must be non-empty")
        if self.average_delay is not None and not isinstance(self.average_delay, (int, float)):
            raise ValueError("average_delay must be numeric when provided")
        if self.average_reward is not None and not isinstance(self.average_reward, (int, float)):
            raise ValueError("average_reward must be numeric when provided")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class CombinedPolicyAggregate:
    policy_id: str
    policy_family: str
    scenario_count: int
    completed_count: int
    dropped_timeout_count: int
    dropped_unavailable_count: int
    deadline_violation_count: int
    illegal_action_rejection_count: int
    mean_delay: float | None
    mean_reward: float | None
    all_rows_action_bound: bool
    compatibility_mode_used: bool
    decision_trace_present: bool

    def __post_init__(self) -> None:
        if not self.policy_id:
            raise ValueError("policy_id must be non-empty")
        if not self.policy_family:
            raise ValueError("policy_family must be non-empty")
        if self.scenario_count != 7:
            raise ValueError("scenario_count must equal 7")
        for field_name in (
            "completed_count",
            "dropped_timeout_count",
            "dropped_unavailable_count",
            "deadline_violation_count",
            "illegal_action_rejection_count",
        ):
            if not _is_non_negative_int(getattr(self, field_name)):
                raise ValueError(f"{field_name} must be a non-negative integer")
        if not self.all_rows_action_bound:
            raise ValueError("all_rows_action_bound must be true")
        if self.compatibility_mode_used:
            raise ValueError("compatibility_mode_used must be false")
        if not self.decision_trace_present:
            raise ValueError("decision_trace_present must be true")
        if self.mean_delay is not None and not isinstance(self.mean_delay, (int, float)):
            raise ValueError("mean_delay must be numeric when provided")
        if self.mean_reward is not None and not isinstance(self.mean_reward, (int, float)):
            raise ValueError("mean_reward must be numeric when provided")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class CombinedRegressionEvidence:
    feature_id: str
    status: str
    passed: bool
    command_hint: str
    scope: str

    def __post_init__(self) -> None:
        if self.feature_id not in ALLOWED_FEATURE_IDS:
            raise ValueError("feature_id must be one of the required upstream feature IDs")
        if not self.status:
            raise ValueError("status must be non-empty")
        if not self.command_hint:
            raise ValueError("command_hint must be non-empty")
        if not self.scope:
            raise ValueError("scope must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _claim_boundary_is_explicit(claim_boundary: tuple[str, ...]) -> bool:
    combined = " ".join(claim_boundary).lower()
    required_phrases = (
        "no training claim",
        "no superiority claim",
        "no final evaluation claim",
        "no statistical significance claim",
        "no full paper reproduction claim",
    )
    return all(phrase in combined for phrase in required_phrases)


@dataclass(frozen=True, slots=True)
class CombinedComparativeReadinessReport:
    feature_name: str
    status: str
    passed: bool
    rows: tuple[CombinedPolicyRow, ...]
    aggregates: tuple[CombinedPolicyAggregate, ...]
    regression_evidence: tuple[CombinedRegressionEvidence, ...]
    required_policy_ids: tuple[str, ...]
    required_scenario_ids: tuple[str, ...]
    claim_boundary: tuple[str, ...]
    scope_evidence: tuple[str, ...]
    source_features: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.feature_name != "Feature 076 - Combined Baseline + Proposed Comparative Readiness":
            raise ValueError("feature_name must match the Feature 076 contract")
        if self.status not in {
            "combined_baseline_proposed_comparative_readiness_ready",
            "combined_baseline_proposed_comparative_readiness_with_blockers",
        }:
            raise ValueError("status must be explicit and recognized")
        if not self.claim_boundary:
            raise ValueError("claim_boundary must be non-empty")
        if not self.scope_evidence:
            raise ValueError("scope_evidence must be non-empty")
        if tuple(self.required_policy_ids) != REQUIRED_POLICY_IDS:
            raise ValueError("required_policy_ids must equal the required seven IDs")
        if tuple(self.required_scenario_ids) != REQUIRED_SCENARIO_IDS:
            raise ValueError("required_scenario_ids must equal the required seven scenarios")
        if len(self.source_features) != 2 or tuple(sorted(set(self.source_features))) != ("074", "075"):
            raise ValueError("source_features must include Feature 074 and Feature 075")
        if len(self.rows) != 49:
            raise ValueError("rows must contain exactly 49 rows")
        if len(self.aggregates) != 7:
            raise ValueError("aggregates must contain exactly 7 rows")
        if len(self.regression_evidence) != len(ALLOWED_FEATURE_IDS):
            raise ValueError("regression_evidence must cover every required upstream feature")
        evidence_ids = [evidence.feature_id for evidence in self.regression_evidence]
        if len(evidence_ids) != len(set(evidence_ids)):
            raise ValueError("regression_evidence must not contain duplicate feature IDs")
        if set(evidence_ids) != set(ALLOWED_FEATURE_IDS):
            raise ValueError("regression_evidence must cover the full upstream feature set")
        if not _claim_boundary_is_explicit(self.claim_boundary):
            raise ValueError("claim_boundary must contain all required claim boundaries")

        row_keys = {(row.policy_id, row.scenario_id) for row in self.rows}
        expected_keys = {
            (policy_id, scenario_id)
            for policy_id in self.required_policy_ids
            for scenario_id in self.required_scenario_ids
        }
        if len(row_keys) != len(self.rows):
            raise ValueError("rows must not contain duplicate policy/scenario pairs")
        if row_keys != expected_keys:
            raise ValueError("rows must cover every required policy/scenario pair exactly once")

        if not all(row.action_bound_metrics_derived for row in self.rows):
            raise ValueError("all rows must be action-bound")
        if any(row.compatibility_mode_used for row in self.rows):
            raise ValueError("no row may use compatibility mode")
        if not all(row.decision_trace_present for row in self.rows):
            raise ValueError("every row must expose decision trace evidence")

        computed_aggregates = {
            policy_id: _aggregate_rows(tuple(row for row in self.rows if row.policy_id == policy_id))
            for policy_id in self.required_policy_ids
        }
        aggregate_ids = [aggregate.policy_id for aggregate in self.aggregates]
        if len(aggregate_ids) != len(set(aggregate_ids)):
            raise ValueError("aggregates must not contain duplicate policy IDs")
        if set(aggregate_ids) != set(self.required_policy_ids):
            raise ValueError("aggregates must cover every required policy/method")
        for aggregate in self.aggregates:
            if aggregate != computed_aggregates[aggregate.policy_id]:
                raise ValueError("aggregates must match the row-level sums")

        if not all(evidence.passed for evidence in self.regression_evidence):
            raise ValueError("all upstream regression evidence must pass")

        expected_pass = bool(
            len(self.rows) == 49
            and len(self.aggregates) == 7
            and len(self.regression_evidence) == len(ALLOWED_FEATURE_IDS)
            and all(evidence.passed for evidence in self.regression_evidence)
            and all(aggregate.all_rows_action_bound for aggregate in self.aggregates)
            and all(not aggregate.compatibility_mode_used for aggregate in self.aggregates)
            and all(aggregate.decision_trace_present for aggregate in self.aggregates)
            and _claim_boundary_is_explicit(self.claim_boundary)
        )
        if self.passed != expected_pass:
            raise ValueError("passed must match the readiness gates")

        expected_status = (
            "combined_baseline_proposed_comparative_readiness_ready"
            if expected_pass
            else "combined_baseline_proposed_comparative_readiness_with_blockers"
        )
        if self.status != expected_status:
            raise ValueError("status must match the computed readiness state")

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_name": self.feature_name,
            "status": self.status,
            "passed": self.passed,
            "rows": [row.to_dict() for row in self.rows],
            "aggregates": [aggregate.to_dict() for aggregate in self.aggregates],
            "regression_evidence": [evidence.to_dict() for evidence in self.regression_evidence],
            "required_policy_ids": list(self.required_policy_ids),
            "required_scenario_ids": list(self.required_scenario_ids),
            "claim_boundary": list(self.claim_boundary),
            "scope_evidence": list(self.scope_evidence),
            "source_features": list(self.source_features),
        }


def _aggregate_rows(rows: tuple[CombinedPolicyRow, ...]) -> CombinedPolicyAggregate:
    if not rows:
        raise ValueError("aggregate rows require at least one combined row")
    policy_id = rows[0].policy_id
    policy_family = rows[0].policy_family
    scenario_count = len(rows)
    completed_count = sum(row.completed_count for row in rows)
    dropped_timeout_count = sum(row.dropped_timeout_count for row in rows)
    dropped_unavailable_count = sum(row.dropped_unavailable_count for row in rows)
    deadline_violation_count = sum(row.deadline_violation_count for row in rows)
    illegal_action_rejection_count = sum(row.illegal_action_rejection_count for row in rows)
    delay_values = [row.average_delay for row in rows if row.average_delay is not None]
    reward_values = [row.average_reward for row in rows if row.average_reward is not None]
    mean_delay = sum(delay_values) / len(delay_values) if delay_values else None
    mean_reward = sum(reward_values) / len(reward_values) if reward_values else None
    all_rows_action_bound = all(row.action_bound_metrics_derived for row in rows)
    compatibility_mode_used = any(row.compatibility_mode_used for row in rows)
    decision_trace_present = all(row.decision_trace_present for row in rows)
    return CombinedPolicyAggregate(
        policy_id=policy_id,
        policy_family=policy_family,
        scenario_count=scenario_count,
        completed_count=completed_count,
        dropped_timeout_count=dropped_timeout_count,
        dropped_unavailable_count=dropped_unavailable_count,
        deadline_violation_count=deadline_violation_count,
        illegal_action_rejection_count=illegal_action_rejection_count,
        mean_delay=mean_delay,
        mean_reward=mean_reward,
        all_rows_action_bound=all_rows_action_bound,
        compatibility_mode_used=compatibility_mode_used,
        decision_trace_present=decision_trace_present,
    )


def aggregate_combined_rows(rows: tuple[CombinedPolicyRow, ...]) -> CombinedPolicyAggregate:
    return _aggregate_rows(rows)
