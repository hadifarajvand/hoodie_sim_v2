from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isnan
from typing import Any


REQUIRED_TRACE_STEP_NAMES = (
    "task_arrival",
    "action_selection",
    "topology_legality",
    "deadline_computation",
    "terminal_state_assignment",
    "reward_emission",
    "expected_actual_comparison",
)


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
class GoldenTraceStep:
    step_name: str
    input_snapshot: dict[str, Any]
    expected_output: Any
    actual_output: Any
    passed: bool
    evidence_source: str

    def __post_init__(self) -> None:
        if not self.step_name:
            raise ValueError("step_name must be non-empty")
        if not self.evidence_source:
            raise ValueError("evidence_source must be non-empty")
        if self.passed != _deep_equal(self.expected_output, self.actual_output):
            raise ValueError("passed must match comparison of expected_output and actual_output")

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_name": self.step_name,
            "input_snapshot": self.input_snapshot,
            "expected_output": self.expected_output,
            "actual_output": self.actual_output,
            "passed": self.passed,
            "evidence_source": self.evidence_source,
        }


@dataclass(frozen=True, slots=True)
class GoldenTraceScenario:
    scenario_id: str
    name: str
    description: str
    inputs: dict[str, Any]
    expected_outputs: Any
    actual_outputs: Any
    steps: tuple[GoldenTraceStep, ...]

    def __post_init__(self) -> None:
        if not self.scenario_id:
            raise ValueError("scenario_id must be non-empty")
        if not self.name:
            raise ValueError("name must be non-empty")
        if not self.steps:
            raise ValueError("golden trace scenarios require at least one step")

    @property
    def passed(self) -> bool:
        step_names = {step.step_name for step in self.steps}
        return (
            set(REQUIRED_TRACE_STEP_NAMES).issubset(step_names)
            and len(step_names) == len(self.steps)
            and all(step.passed for step in self.steps)
            and _deep_equal(self.expected_outputs, self.actual_outputs)
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "name": self.name,
            "description": self.description,
            "inputs": self.inputs,
            "expected_outputs": self.expected_outputs,
            "actual_outputs": self.actual_outputs,
            "steps": [step.to_dict() for step in self.steps],
            "passed": self.passed,
        }


@dataclass(frozen=True, slots=True)
class TopologyTraceEvidence:
    source_agent_id: str
    destination_agent_id: str
    neighbor_map_source: str
    is_neighbor: bool
    is_self_destination: bool
    final_legal: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class DeadlineTraceEvidence:
    arrival_slot: int
    phi: int
    absolute_deadline_slot: int
    completion_slot: int | None
    mode: str
    success_before_deadline: bool
    terminal_status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RewardTraceEvidence:
    x_active: bool
    terminal_status: str
    phi_value: int | float | None
    drop_penalty: int | float
    reward_value: float | None
    reward_slot: int | None
    mode: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class Feature072RegressionEvidence:
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
class Feature072Report:
    feature_name: str
    status: str
    passed: bool
    changed_files: tuple[str, ...]
    scenarios: tuple[GoldenTraceScenario, ...]
    feature_068r_regression_status: Feature072RegressionEvidence
    feature_069_regression_status: Feature072RegressionEvidence
    feature_070_regression_status: Feature072RegressionEvidence
    feature_071_regression_status: Feature072RegressionEvidence
    paper_claim_boundary: str
    recommended_next_feature: str

    def __post_init__(self) -> None:
        if self.feature_name != "Feature 072 - End-to-End HOODIE Golden Trace Validation":
            raise ValueError("feature_name must match the Feature 072 contract")
        if self.passed and self.status != "end_to_end_golden_trace_validation_ready":
            raise ValueError("passed reports must use the ready status")
        if self.passed and not all(
            (
                self.scenarios,
                all(scenario.passed for scenario in self.scenarios),
                self.feature_068r_regression_status.passed,
                self.feature_069_regression_status.passed,
                self.feature_070_regression_status.passed,
                self.feature_071_regression_status.passed,
            )
        ):
            raise ValueError("passed reports require all scenarios and prior regressions to pass")

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_name": self.feature_name,
            "status": self.status,
            "passed": self.passed,
            "changed_files": list(self.changed_files),
            "scenarios": [scenario.to_dict() for scenario in self.scenarios],
            "feature_068r_regression_status": self.feature_068r_regression_status.to_dict(),
            "feature_069_regression_status": self.feature_069_regression_status.to_dict(),
            "feature_070_regression_status": self.feature_070_regression_status.to_dict(),
            "feature_071_regression_status": self.feature_071_regression_status.to_dict(),
            "paper_claim_boundary": self.paper_claim_boundary,
            "recommended_next_feature": self.recommended_next_feature,
        }
