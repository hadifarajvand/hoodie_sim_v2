from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

FEATURE_ID = "082-runtime-evaluation"
FEATURE_NAME = "HOODIE Runtime Evaluation"

POLICY_HOODIE_PROPOSED = "HOODIE_PROPOSED"
POLICY_ORIGINAL_HOODIE_BASELINE = "ORIGINAL_HOODIE_BASELINE"
POLICY_RANDOM_POLICY = "RANDOM_POLICY"
POLICY_LOCAL_ONLY = "LOCAL_ONLY"
POLICY_CLOUD_ONLY = "CLOUD_ONLY"

REQUIRED_POLICIES = (
    POLICY_HOODIE_PROPOSED,
    POLICY_ORIGINAL_HOODIE_BASELINE,
    POLICY_RANDOM_POLICY,
    POLICY_LOCAL_ONLY,
    POLICY_CLOUD_ONLY,
)

REQUIRED_SCENARIOS = (
    "light_load_no_deadline_pressure",
    "tight_deadline_pressure",
    "legal_horizontal_offload",
    "illegal_horizontal_destination_attempt",
    "cloud_vertical_fallback",
    "timeout_drop_case",
    "mixed_local_horizontal_cloud_candidates",
)

WORKLOAD_LEVELS = ("low", "medium", "high")
DEADLINE_PRESSURE_LEVELS = ("relaxed", "moderate", "tight")
WORKLOAD_TASK_COUNTS = {"low": 4, "medium": 8, "high": 12}
WORKLOAD_SCENARIO_DURATION = {"low": 12, "medium": 14, "high": 16}
RUNTIME_SEEDS = (7, 13, 21)
TOPOLOGY_MODE_PAPER_FIGURE_7 = "paper_figure_7"
RUNTIME_MODE_PAPER = "paper"
DEFAULT_OUTPUT_DIR = Path("artifacts/feature_082_full_runtime_eval")

VALIDATION_COMMANDS = (
    "git diff --check",
    "src/.venvmac/bin/python -m unittest discover tests/unit -p 'test_hoodie_runtime_evaluation_*.py'",
    "src/.venvmac/bin/python -m unittest discover tests/integration -p 'test_hoodie_runtime_evaluation_*.py'",
    "src/.venvmac/bin/python -m analysis.hoodie_runtime_evaluation_runner --validate-artifacts",
)


@dataclass(slots=True)
class EvaluationConfig:
    policies: tuple[str, ...] = REQUIRED_POLICIES
    scenarios: tuple[str, ...] = REQUIRED_SCENARIOS
    workloads: tuple[str, ...] = WORKLOAD_LEVELS
    deadline_pressures: tuple[str, ...] = DEADLINE_PRESSURE_LEVELS
    seeds: tuple[int, ...] = RUNTIME_SEEDS
    output_dir: Path = DEFAULT_OUTPUT_DIR
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

