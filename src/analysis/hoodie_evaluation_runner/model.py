from __future__ import annotations

from dataclasses import asdict, dataclass, field
from math import isnan
from typing import Any

from .config import DEADLINE_PRESSURE_LEVELS, REQUIRED_POLICIES, REQUIRED_SCENARIOS, WORKLOAD_LEVELS


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
class TaskBlueprint:
    task_id: str
    arrival_time: int
    source_agent_id: str
    local_completion_time: int
    horizontal_completion_time: int
    vertical_completion_time: int
    absolute_deadline_time: int
    scenario_duration: int
    legal_horizontal_destinations: tuple[str, ...]
    illegal_horizontal_destinations: tuple[str, ...]
    cloud_available: bool
    local_available: bool = True
    horizontal_available: bool = True
    vertical_available: bool = True
    queue_length_snapshot: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        if not self.task_id:
            raise ValueError("task_id must be non-empty")
        if self.arrival_time < 0:
            raise ValueError("arrival_time must be non-negative")
        if self.absolute_deadline_time < self.arrival_time:
            raise ValueError("absolute_deadline_time must not precede arrival_time")
        if self.scenario_duration <= 0:
            raise ValueError("scenario_duration must be positive")

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "arrival_time": self.arrival_time,
            "source_agent_id": self.source_agent_id,
            "local_completion_time": self.local_completion_time,
            "horizontal_completion_time": self.horizontal_completion_time,
            "vertical_completion_time": self.vertical_completion_time,
            "absolute_deadline_time": self.absolute_deadline_time,
            "scenario_duration": self.scenario_duration,
            "legal_horizontal_destinations": list(self.legal_horizontal_destinations),
            "illegal_horizontal_destinations": list(self.illegal_horizontal_destinations),
            "cloud_available": self.cloud_available,
            "local_available": self.local_available,
            "horizontal_available": self.horizontal_available,
            "vertical_available": self.vertical_available,
            "queue_length_snapshot": list(self.queue_length_snapshot),
        }


@dataclass(frozen=True, slots=True)
class ScenarioContext:
    scenario_name: str
    workload: str
    deadline_pressure: str
    seed: int
    vehicle_count: int
    task_type_count: int
    task_count: int
    scenario_duration: int
    local_available: bool
    horizontal_destinations: tuple[str, ...]
    illegal_horizontal_destinations: tuple[str, ...]
    cloud_available: bool
    deadline_slots: tuple[int, ...]
    network_condition: str
    queue_initial_state: tuple[int, ...]
    tasks: tuple[TaskBlueprint, ...]
    topology_mode: str
    runtime_mode: str

    def __post_init__(self) -> None:
        if self.scenario_name not in REQUIRED_SCENARIOS:
            raise ValueError("scenario_name must be one of the required Feature 081 scenarios")
        if self.workload not in WORKLOAD_LEVELS:
            raise ValueError("workload must be one of the required workload levels")
        if self.deadline_pressure not in DEADLINE_PRESSURE_LEVELS:
            raise ValueError("deadline_pressure must be one of the required deadline pressure levels")
        if self.task_count <= 0:
            raise ValueError("task_count must be positive")
        if self.scenario_duration <= 0:
            raise ValueError("scenario_duration must be positive")
        if not self.tasks:
            raise ValueError("tasks must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_name": self.scenario_name,
            "workload": self.workload,
            "deadline_pressure": self.deadline_pressure,
            "seed": self.seed,
            "vehicle_count": self.vehicle_count,
            "task_type_count": self.task_type_count,
            "task_count": self.task_count,
            "scenario_duration": self.scenario_duration,
            "local_available": self.local_available,
            "horizontal_destinations": list(self.horizontal_destinations),
            "illegal_horizontal_destinations": list(self.illegal_horizontal_destinations),
            "cloud_available": self.cloud_available,
            "deadline_slots": list(self.deadline_slots),
            "network_condition": self.network_condition,
            "queue_initial_state": list(self.queue_initial_state),
            "tasks": [task.to_dict() for task in self.tasks],
            "topology_mode": self.topology_mode,
            "runtime_mode": self.runtime_mode,
        }


@dataclass(frozen=True, slots=True)
class PolicyDecision:
    policy: str
    task_id: str
    action_type: str
    destination: str
    is_legal: bool
    decision_trace: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ExecutionOutcome:
    task_id: str
    completed: bool
    dropped_timeout: bool
    dropped_unavailable: bool
    deadline_violation: bool
    illegal_action_rejected: bool
    arrival_time: int
    completion_time: int | None
    delay: float | None
    reward: float | None
    queue_length_observations: tuple[int, ...]
    policy: str
    scenario_name: str
    workload: str
    deadline_pressure: str
    seed: int
    selected_action: str
    resolved_destination: str
    compatibility_mode_used: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class MetricRow:
    policy: str
    scenario: str
    workload: str
    deadline_pressure: str
    seed: int | None
    completed_count: int
    dropped_timeout_count: int
    dropped_unavailable_count: int
    deadline_violation_count: int
    illegal_action_rejection_count: int
    average_delay: float | None
    average_reward: float
    total_reward: float
    completion_rate: float
    timeout_drop_rate: float
    unavailable_drop_rate: float
    deadline_violation_rate: float
    throughput: float
    queue_stability_score: float
    compatibility_mode_used: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RankingRow:
    metric: str
    rank: int
    policy: str
    value: float
    direction: str
    tie_break_trace: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "metric": self.metric,
            "rank": self.rank,
            "policy": self.policy,
            "value": self.value,
            "direction": self.direction,
            "tie_break_trace": list(self.tie_break_trace),
        }


@dataclass(frozen=True, slots=True)
class PolicyCoverageRow:
    policy: str
    status: str
    implementation_mode: str
    evidence: str
    compatibility_mode_used: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ScenarioCoverageRow:
    scenario: str
    status: str
    evidence: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class MetricCoverageRow:
    metric: str
    status: str
    formula: str
    evidence: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class Feature081Report:
    status: str
    passed: bool
    readiness_level: str
    policy_coverage: tuple[PolicyCoverageRow, ...]
    scenario_coverage: tuple[ScenarioCoverageRow, ...]
    metric_coverage: tuple[MetricCoverageRow, ...]
    ranking_coverage: tuple[MetricCoverageRow, ...]
    summary_rows: tuple[MetricRow, ...]
    ranking_tables: dict[str, tuple[RankingRow, ...]]
    claim_boundary: tuple[str, ...]
    scope_proof: tuple[str, ...]
    remaining_gaps: tuple[str, ...]
    scenario_tables: tuple[MetricRow, ...] = ()
    aggregate_summaries: tuple[MetricRow, ...] = ()
    compatibility_mode_used: bool = False

    def __post_init__(self) -> None:
        if not self.claim_boundary:
            raise ValueError("claim_boundary must be non-empty")
        if not self.scope_proof:
            raise ValueError("scope_proof must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "passed": self.passed,
            "readiness_level": self.readiness_level,
            "policy_coverage": [row.to_dict() for row in self.policy_coverage],
            "scenario_coverage": [row.to_dict() for row in self.scenario_coverage],
            "metric_coverage": [row.to_dict() for row in self.metric_coverage],
            "ranking_coverage": [row.to_dict() for row in self.ranking_coverage],
            "summary_rows": [row.to_dict() for row in self.summary_rows],
            "ranking_tables": {metric: [row.to_dict() for row in rows] for metric, rows in self.ranking_tables.items()},
            "claim_boundary": list(self.claim_boundary),
            "scope_proof": list(self.scope_proof),
            "remaining_gaps": list(self.remaining_gaps),
            "scenario_tables": [row.to_dict() for row in self.scenario_tables],
            "aggregate_summaries": [row.to_dict() for row in self.aggregate_summaries],
            "compatibility_mode_used": self.compatibility_mode_used,
        }
