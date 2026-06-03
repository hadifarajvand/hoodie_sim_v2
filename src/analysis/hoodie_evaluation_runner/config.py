from __future__ import annotations

from dataclasses import dataclass


POLICY_HOODIE_PROPOSED = "HOODIE_PROPOSED"
POLICY_ORIGINAL_HOODIE_BASELINE = "ORIGINAL_HOODIE_BASELINE"
POLICY_RANDOM = "RANDOM_POLICY"
POLICY_LOCAL_ONLY = "LOCAL_ONLY"
POLICY_CLOUD_ONLY = "CLOUD_ONLY"

REQUIRED_POLICIES: tuple[str, ...] = (
    POLICY_HOODIE_PROPOSED,
    POLICY_ORIGINAL_HOODIE_BASELINE,
    POLICY_RANDOM,
    POLICY_LOCAL_ONLY,
    POLICY_CLOUD_ONLY,
)

REQUIRED_SCENARIOS: tuple[str, ...] = (
    "light_load_no_deadline_pressure",
    "tight_deadline_pressure",
    "legal_horizontal_offload",
    "illegal_horizontal_destination_attempt",
    "cloud_vertical_fallback",
    "timeout_drop_case",
    "mixed_local_horizontal_cloud_candidates",
)

WORKLOAD_LEVELS: tuple[str, ...] = ("low", "medium", "high")
DEADLINE_PRESSURE_LEVELS: tuple[str, ...] = ("relaxed", "moderate", "tight")
TOPOLOGY_MODE_PAPER_FIGURE_7 = "paper_figure_7"
RUNTIME_MODE_PAPER = "paper"

VALIDATION_COMMANDS: tuple[str, ...] = (
    "git diff --check",
    "src/.venvmac/bin/python -m unittest discover tests/unit -p 'test_hoodie_evaluation_runner_*.py'",
    "src/.venvmac/bin/python -m unittest discover tests/integration -p 'test_hoodie_evaluation_runner_*.py'",
    "src/.venvmac/bin/python -m analysis.hoodie_evaluation_runner",
)


@dataclass(frozen=True, slots=True)
class EvaluationConfig:
    policies: tuple[str, ...] = REQUIRED_POLICIES
    scenarios: tuple[str, ...] = REQUIRED_SCENARIOS
    workloads: tuple[str, ...] = WORKLOAD_LEVELS
    deadline_pressures: tuple[str, ...] = DEADLINE_PRESSURE_LEVELS
    seeds: tuple[int, ...] = (7, 13)
    topology_mode: str = TOPOLOGY_MODE_PAPER_FIGURE_7
    runtime_mode: str = RUNTIME_MODE_PAPER

    def __post_init__(self) -> None:
        if not self.policies:
            raise ValueError("policies must be non-empty")
        if not self.scenarios:
            raise ValueError("scenarios must be non-empty")
        if not self.workloads:
            raise ValueError("workloads must be non-empty")
        if not self.deadline_pressures:
            raise ValueError("deadline_pressures must be non-empty")
        if not self.seeds:
            raise ValueError("seeds must be non-empty")
