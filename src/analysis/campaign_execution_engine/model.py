from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .config import (
    BLOCKED_STATUS,
    DEADLINE_PRESSURE_LEVELS,
    DEPENDENCY_FEATURES,
    FEATURE_NAME,
    READY_STATUS,
    REQUIRED_POLICY_IDS,
    REQUIRED_SCENARIO_IDS,
    RUNTIME_MODE,
    SEED_IDS,
    TOPOLOGY_MODE,
    WORKLOAD_LEVELS,
)


ALLOWED_ACTION_LEGALITIES: tuple[str, ...] = ("legal", "illegal_unavailable", "illegal_self_destination", "unmapped")
ALLOWED_SELECTED_ACTION_FAMILIES: tuple[str, ...] = ("local", "horizontal", "vertical")
ALLOWED_TERMINAL_STATUSES: tuple[str, ...] = (
    "completed_private",
    "completed_public",
    "completed_cloud",
    "dropped_timeout",
    "dropped_unavailable",
)
ALLOWED_FEATURE_IDS: tuple[str, ...] = ("076", "077")


def _is_non_negative_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _is_numeric(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _claim_boundary_is_explicit(claim_boundary: tuple[str, ...]) -> bool:
    combined = " ".join(claim_boundary).lower()
    required_phrases = (
        "no training claim",
        "no superiority claim",
        "no final evaluation claim",
        "no statistical significance claim",
        "no full paper reproduction claim",
        "no statistical summary claim",
        "no ranking claim",
        "no winner claim",
    )
    return all(phrase in combined for phrase in required_phrases)


@dataclass(frozen=True, slots=True)
class CampaignExecutionSeed:
    seed_id: str
    seed_value: int
    source: str

    def __post_init__(self) -> None:
        if not self.seed_id:
            raise ValueError("seed_id must be non-empty")
        if not _is_non_negative_int(self.seed_value):
            raise ValueError("seed_value must be a non-negative integer")
        if not self.source:
            raise ValueError("source must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class CampaignExecutionGridCell:
    policy_id: str
    scenario_id: str
    seed_id: str
    workload_level: str
    deadline_pressure_level: str
    topology_mode: str
    runtime_mode: str

    def __post_init__(self) -> None:
        if self.policy_id not in REQUIRED_POLICY_IDS:
            raise ValueError("policy_id must be one of the required policies")
        if self.scenario_id not in REQUIRED_SCENARIO_IDS:
            raise ValueError("scenario_id must be one of the required scenarios")
        if self.seed_id not in SEED_IDS:
            raise ValueError("seed_id must be one of the deterministic campaign seeds")
        if self.workload_level not in WORKLOAD_LEVELS:
            raise ValueError("workload_level must be one of the required workload levels")
        if self.deadline_pressure_level not in DEADLINE_PRESSURE_LEVELS:
            raise ValueError("deadline_pressure_level must be one of the required deadline levels")
        if self.topology_mode != TOPOLOGY_MODE:
            raise ValueError("topology_mode must be paper_figure_7")
        if self.runtime_mode != RUNTIME_MODE:
            raise ValueError("runtime_mode must be paper")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class CampaignExecutionResultRow:
    policy_id: str
    scenario_id: str
    seed_id: str
    workload_level: str
    deadline_pressure_level: str
    topology_mode: str
    runtime_mode: str
    selected_action_id: str
    selected_action_family: str
    action_legality: str
    terminal_status: str
    completed_count: int
    dropped_timeout_count: int
    dropped_unavailable_count: int
    deadline_violation_count: int
    illegal_action_rejection_count: int
    average_delay: float
    average_reward: float
    total_reward: float
    completion_rate: float
    timeout_drop_rate: float
    unavailable_drop_rate: float
    deadline_violation_rate: float
    compatibility_mode_used: bool
    execution_runtime_path_used: str
    scenario_source: str
    policy_source: str
    workload_modifier_state: str
    deadline_modifier_state: str
    execution_provenance: str

    def __post_init__(self) -> None:
        if self.policy_id not in REQUIRED_POLICY_IDS:
            raise ValueError("policy_id must be one of the required policies")
        if self.scenario_id not in REQUIRED_SCENARIO_IDS:
            raise ValueError("scenario_id must be one of the required scenarios")
        if self.seed_id not in SEED_IDS:
            raise ValueError("seed_id must be one of the deterministic campaign seeds")
        if self.workload_level not in WORKLOAD_LEVELS:
            raise ValueError("workload_level must be one of the required workload levels")
        if self.deadline_pressure_level not in DEADLINE_PRESSURE_LEVELS:
            raise ValueError("deadline_pressure_level must be one of the required deadline levels")
        if self.topology_mode != TOPOLOGY_MODE:
            raise ValueError("topology_mode must be paper_figure_7")
        if self.runtime_mode != RUNTIME_MODE:
            raise ValueError("runtime_mode must be paper")
        if not self.selected_action_id:
            raise ValueError("selected_action_id must be non-empty")
        if self.selected_action_family not in ALLOWED_SELECTED_ACTION_FAMILIES:
            raise ValueError("selected_action_family must be a recognized action family")
        if self.action_legality not in ALLOWED_ACTION_LEGALITIES:
            raise ValueError("action_legality must be explicit and supported")
        if self.terminal_status not in ALLOWED_TERMINAL_STATUSES:
            raise ValueError("terminal_status must be a supported terminal status")
        for field_name in (
            "completed_count",
            "dropped_timeout_count",
            "dropped_unavailable_count",
            "deadline_violation_count",
            "illegal_action_rejection_count",
        ):
            if not _is_non_negative_int(getattr(self, field_name)):
                raise ValueError(f"{field_name} must be a non-negative integer")
        for field_name in (
            "average_delay",
            "average_reward",
            "total_reward",
            "completion_rate",
            "timeout_drop_rate",
            "unavailable_drop_rate",
            "deadline_violation_rate",
        ):
            if not _is_numeric(getattr(self, field_name)):
                raise ValueError(f"{field_name} must be numeric")
        if self.compatibility_mode_used:
            raise ValueError("compatibility_mode_used must be false")
        if not self.execution_runtime_path_used:
            raise ValueError("execution_runtime_path_used must be non-empty")
        if not self.scenario_source:
            raise ValueError("scenario_source must be non-empty")
        if not self.policy_source:
            raise ValueError("policy_source must be non-empty")
        if not self.workload_modifier_state:
            raise ValueError("workload_modifier_state must be non-empty")
        if not self.deadline_modifier_state:
            raise ValueError("deadline_modifier_state must be non-empty")
        if not self.execution_provenance:
            raise ValueError("execution_provenance must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class CampaignExecutionReport:
    feature_id: str
    status: str
    passed: bool
    dependency_features: tuple[str, ...]
    seed_count: int
    expected_row_count: int
    actual_row_count: int
    result_rows: tuple[CampaignExecutionResultRow, ...]
    scope_evidence: tuple[str, ...]
    validation_summary: tuple[str, ...]
    claim_boundary: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.feature_id != "078-campaign-execution-engine":
            raise ValueError("feature_id must be 078-campaign-execution-engine")
        if self.status not in {READY_STATUS, BLOCKED_STATUS}:
            raise ValueError("status must be explicit and recognized")
        if tuple(self.dependency_features) != DEPENDENCY_FEATURES:
            raise ValueError("dependency_features must include Feature 076 and Feature 077")
        if self.seed_count <= 0:
            raise ValueError("seed_count must be positive")
        if self.expected_row_count != len(REQUIRED_POLICY_IDS) * len(REQUIRED_SCENARIO_IDS) * self.seed_count * len(WORKLOAD_LEVELS) * len(DEADLINE_PRESSURE_LEVELS):
            raise ValueError("expected_row_count must match the campaign grid formula")
        if self.actual_row_count != len(self.result_rows):
            raise ValueError("actual_row_count must equal the number of emitted rows")
        if self.passed and self.status != READY_STATUS:
            raise ValueError("passed reports must use the ready status")
        if not self.scope_evidence:
            raise ValueError("scope_evidence must be non-empty")
        if not self.validation_summary:
            raise ValueError("validation_summary must be non-empty")
        if not self.claim_boundary:
            raise ValueError("claim_boundary must be non-empty")
        if not _claim_boundary_is_explicit(self.claim_boundary):
            raise ValueError("claim_boundary must contain all required claim boundaries")
        if self.passed and self.actual_row_count != self.expected_row_count:
            raise ValueError("passed reports must have matching expected and actual row counts")
        if not all(row.topology_mode == TOPOLOGY_MODE for row in self.result_rows):
            raise ValueError("every row must use paper_figure_7 topology")
        if not all(row.runtime_mode == RUNTIME_MODE for row in self.result_rows):
            raise ValueError("every row must use paper runtime mode")
        if any(row.compatibility_mode_used for row in self.result_rows):
            raise ValueError("compatibility mode must remain false for every row")
        if len({(row.policy_id, row.scenario_id, row.seed_id, row.workload_level, row.deadline_pressure_level) for row in self.result_rows}) != len(self.result_rows):
            raise ValueError("every campaign cell must emit exactly one unique row")
        expected_keys = {
            (policy_id, scenario_id, seed_id, workload_level, deadline_level)
            for policy_id in REQUIRED_POLICY_IDS
            for scenario_id in REQUIRED_SCENARIO_IDS
            for seed_id in SEED_IDS
            for workload_level in WORKLOAD_LEVELS
            for deadline_level in DEADLINE_PRESSURE_LEVELS
        }
        actual_keys = {
            (row.policy_id, row.scenario_id, row.seed_id, row.workload_level, row.deadline_pressure_level)
            for row in self.result_rows
        }
        if actual_keys != expected_keys:
            raise ValueError("result_rows must cover the complete campaign grid exactly once")

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "status": self.status,
            "passed": self.passed,
            "dependency_features": list(self.dependency_features),
            "seed_count": self.seed_count,
            "expected_row_count": self.expected_row_count,
            "actual_row_count": self.actual_row_count,
            "result_rows": [row.to_dict() for row in self.result_rows],
            "scope_evidence": list(self.scope_evidence),
            "validation_summary": list(self.validation_summary),
            "claim_boundary": list(self.claim_boundary),
        }
