from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isnan
from typing import Any


_ALLOWED_TERMINAL_STATUSES = {
    "completed_private",
    "completed_public",
    "completed_cloud",
    "dropped_timeout",
    "dropped_unavailable",
    "pending",
}
_ALLOWED_MODES = {"paper", "compatibility"}
_COMPLETED_STATUSES = {"completed_private", "completed_public", "completed_cloud"}
_DROPPED_STATUSES = {"dropped_timeout", "dropped_unavailable"}


def _deep_equal(left: Any, right: Any) -> bool:
    if isinstance(left, float) and isinstance(right, float):
        if isnan(left) and isnan(right):
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
class ControlledEvaluationTaskRecord:
    task_id: str
    source_agent_id: str
    action_type: str
    destination_agent_id: str
    arrival_slot: int
    phi: int
    completion_slot: int | None
    terminal_status: str
    reward_value: float | None
    delay: float | int | None
    illegal_action_rejected: bool
    compatibility_mode_used: bool
    mode: str = "paper"
    deadline_violation: bool = False
    topology_check_required: bool = False
    topology_final_legal: bool = True
    topology_reason: str = ""
    topology_neighbor_map_source: str = ""

    def __post_init__(self) -> None:
        if not self.task_id:
            raise ValueError("task_id must be non-empty")
        if not self.source_agent_id:
            raise ValueError("source_agent_id must be non-empty")
        if not self.action_type:
            raise ValueError("action_type must be non-empty")
        if not self.destination_agent_id:
            raise ValueError("destination_agent_id must be non-empty")
        if self.terminal_status not in _ALLOWED_TERMINAL_STATUSES:
            raise ValueError("terminal_status must be explicit and supported")
        if self.mode not in _ALLOWED_MODES:
            raise ValueError("mode must be one of {'paper', 'compatibility'}")
        if self.compatibility_mode_used != (self.mode == "compatibility"):
            raise ValueError("compatibility_mode_used must match mode")
        if self.terminal_status == "pending":
            if self.completion_slot is not None:
                raise ValueError("pending tasks must not have a completion_slot")
            if self.reward_value is not None:
                raise ValueError("pending tasks must not emit a reward value")
        else:
            if self.completion_slot is None:
                raise ValueError("terminal tasks require a completion_slot")
            if self.reward_value is None:
                raise ValueError("terminal tasks require an explicit reward value")
        if self.delay is not None and self.delay < 0:
            raise ValueError("delay must be non-negative when provided")
        if self.arrival_slot < 0:
            raise ValueError("arrival_slot must be non-negative")
        if self.phi <= 0:
            raise ValueError("phi must be positive")

    @property
    def is_terminal(self) -> bool:
        return self.terminal_status != "pending"

    @property
    def is_completed(self) -> bool:
        return self.terminal_status in _COMPLETED_STATUSES

    @property
    def is_dropped(self) -> bool:
        return self.terminal_status in _DROPPED_STATUSES

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ControlledEvaluationMetrics:
    completed_count: int
    dropped_timeout_count: int
    dropped_unavailable_count: int
    deadline_violation_count: int
    illegal_action_rejection_count: int
    average_delay: float
    average_reward: float
    paper_mode_success_count: int
    compatibility_mode_used: bool

    def __post_init__(self) -> None:
        for field_name in (
            "completed_count",
            "dropped_timeout_count",
            "dropped_unavailable_count",
            "deadline_violation_count",
            "illegal_action_rejection_count",
            "paper_mode_success_count",
        ):
            if getattr(self, field_name) < 0:
                raise ValueError(f"{field_name} must be non-negative")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ControlledEvaluationScenario:
    scenario_id: str
    name: str
    description: str
    tasks: tuple[ControlledEvaluationTaskRecord, ...]
    expected_metrics: ControlledEvaluationMetrics
    actual_metrics: ControlledEvaluationMetrics
    paper_mode_only: bool
    passed: bool

    def __post_init__(self) -> None:
        if not self.scenario_id:
            raise ValueError("scenario_id must be non-empty")
        if not self.name:
            raise ValueError("name must be non-empty")
        if not self.tasks:
            raise ValueError("ControlledEvaluationScenario requires at least one task record")
        if self.expected_metrics is self.actual_metrics:
            raise ValueError("expected_metrics and actual_metrics must be distinct objects")
        metrics_match = _deep_equal(self.expected_metrics, self.actual_metrics)
        if self.passed != metrics_match:
            raise ValueError("scenario passed flag must match expected_metrics vs actual_metrics equality")
        if self.paper_mode_only and any(task.mode != "paper" for task in self.tasks):
            raise ValueError("paper_mode_only scenarios must not use compatibility mode")

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "name": self.name,
            "description": self.description,
            "tasks": [task.to_dict() for task in self.tasks],
            "expected_metrics": self.expected_metrics.to_dict(),
            "actual_metrics": self.actual_metrics.to_dict(),
            "paper_mode_only": self.paper_mode_only,
            "passed": self.passed,
        }


@dataclass(frozen=True, slots=True)
class ControlledEvaluationRegressionEvidence:
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
class ControlledEvaluationBatchReport:
    feature_name: str
    status: str
    passed: bool
    changed_files: tuple[str, ...]
    scenarios: tuple[ControlledEvaluationScenario, ...]
    aggregate_metrics: ControlledEvaluationMetrics
    feature_068r_regression_status: ControlledEvaluationRegressionEvidence
    feature_069_regression_status: ControlledEvaluationRegressionEvidence
    feature_070_regression_status: ControlledEvaluationRegressionEvidence
    feature_071_regression_status: ControlledEvaluationRegressionEvidence
    feature_072_regression_status: ControlledEvaluationRegressionEvidence
    paper_claim_boundary: str
    recommended_next_feature: str

    def __post_init__(self) -> None:
        if self.feature_name != "Feature 073 - Controlled Evaluation Batch Readiness":
            raise ValueError("feature_name must match the Feature 073 contract")
        if self.passed and self.status != "controlled_evaluation_batch_readiness_ready":
            raise ValueError("passed reports must use the ready status")
        if self.passed and not self.scenarios:
            raise ValueError("passed reports require controlled scenarios")
        if self.aggregate_metrics != _aggregate_metrics_from_scenarios(self.scenarios):
            raise ValueError("aggregate_metrics must match the deterministic scenario aggregate")
        computed_pass = bool(
            self.scenarios
            and all(scenario.passed for scenario in self.scenarios)
            and self.feature_068r_regression_status.passed
            and self.feature_069_regression_status.passed
            and self.feature_070_regression_status.passed
            and self.feature_071_regression_status.passed
            and self.feature_072_regression_status.passed
            and not self.aggregate_metrics.compatibility_mode_used
        )
        if self.passed != computed_pass:
            raise ValueError("passed flag must match scenario/regression readiness state")

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_name": self.feature_name,
            "status": self.status,
            "passed": self.passed,
            "changed_files": list(self.changed_files),
            "scenarios": [scenario.to_dict() for scenario in self.scenarios],
            "aggregate_metrics": self.aggregate_metrics.to_dict(),
            "feature_068r_regression_status": self.feature_068r_regression_status.to_dict(),
            "feature_069_regression_status": self.feature_069_regression_status.to_dict(),
            "feature_070_regression_status": self.feature_070_regression_status.to_dict(),
            "feature_071_regression_status": self.feature_071_regression_status.to_dict(),
            "feature_072_regression_status": self.feature_072_regression_status.to_dict(),
            "paper_claim_boundary": self.paper_claim_boundary,
            "recommended_next_feature": self.recommended_next_feature,
        }


def _aggregate_metrics_from_scenarios(
    scenarios: tuple[ControlledEvaluationScenario, ...],
) -> ControlledEvaluationMetrics:
    from .report import compute_aggregate_metrics

    return compute_aggregate_metrics(scenarios)
