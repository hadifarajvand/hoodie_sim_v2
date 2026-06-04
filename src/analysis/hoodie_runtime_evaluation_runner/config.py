from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

FEATURE_ID = "085-hoodie-paper-baseline-fidelity-audit"
FEATURE_NAME = "HOODIE Baseline Fidelity Audit and Formula Mapping"

POLICY_HOODIE = "HOODIE"
POLICY_RO = "RO"
POLICY_FLC = "FLC"
POLICY_VO = "VO"
POLICY_HO = "HO"
POLICY_BCO = "BCO"
POLICY_MLEO = "MLEO"

# Deprecated aliases retained only for compatibility with older local code paths.
POLICY_HOODIE_PROPOSED = POLICY_HOODIE
POLICY_ORIGINAL_HOODIE_BASELINE = "ORIGINAL_HOODIE_BASELINE"
POLICY_RANDOM_POLICY = POLICY_RO
POLICY_LOCAL_ONLY = POLICY_FLC
POLICY_CLOUD_ONLY = POLICY_VO

REQUIRED_POLICIES = (
    POLICY_HOODIE,
    POLICY_RO,
    POLICY_FLC,
    POLICY_VO,
    POLICY_HO,
    POLICY_BCO,
    POLICY_MLEO,
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
DEFAULT_OUTPUT_DIR = Path("artifacts/feature_085_full_audit")

VALIDATION_COMMANDS = (
    "git diff --check",
    "src/.venvmac/bin/python -m unittest discover tests/unit -p 'test_hoodie_runtime_evaluation_*.py'",
    "src/.venvmac/bin/python -m unittest discover tests/integration -p 'test_hoodie_runtime_evaluation_*.py'",
    "src/.venvmac/bin/python -m analysis.hoodie_runtime_evaluation_runner --validate-artifacts --artifact-dir artifacts/feature_085_full_audit",
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
