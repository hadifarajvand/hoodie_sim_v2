from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

FEATURE_ID = "045-completion-root-cause-diagnosis"

TraceStrategy = Literal[
    "environment_default_policy_probe",
    "force_local_legal_probe",
    "force_horizontal_legal_probe",
    "force_vertical_legal_probe",
    "mixed_legal_round_robin_probe",
]

TRACE_STRATEGIES: tuple[TraceStrategy, ...] = (
    "environment_default_policy_probe",
    "force_local_legal_probe",
    "force_horizontal_legal_probe",
    "force_vertical_legal_probe",
    "mixed_legal_round_robin_probe",
)

ROOT_CAUSE_CLASSES: tuple[str, ...] = (
    "queue_pressure",
    "task_generation_admission_overload",
    "action_exposure_bias",
    "local_private_queue_blockage",
    "public_cloud_queue_blockage",
    "transmission_delay_admission_mismatch",
    "execution_progress_deadline_expires_first",
    "completion_emitted_but_reward_or_counter_path_wrong",
    "deadline_drop_ordering_issue",
    "formula_unit_mismatch",
    "no_completion_problem_detected",
    "inconclusive_trace_evidence",
)

FEATURE_044_REPORT_PATH = "artifacts/analysis/passive-runtime-lifecycle-trace-instrumentation/lifecycle-trace-instrumentation-report.json"


@dataclass(slots=True)
class CompletionRootCauseConfig:
    feature_id: str = FEATURE_ID
    episode_length: int = 110
    timeout_slots: int = 20
    node_count: int = 20
    arrival_probability: float = 0.5
    seeds: list[int] = field(default_factory=lambda: [0, 1, 2])
    strategies: tuple[TraceStrategy, ...] = TRACE_STRATEGIES
    no_runtime_repair: bool = True
    no_training: bool = True
    slot_duration_seconds: float = 0.1
    task_size_range_mbits: tuple[float, float] = (2.0, 5.0)
    processing_density_gcycles_per_mbit: float = 0.297
    cpu_private_gcycles_per_slot: float = 0.5
    cpu_public_gcycles_per_slot: float = 0.5
    cpu_cloud_gcycles_per_slot: float = 3.0
    horizontal_rate_mbps: float = 30.0
    vertical_rate_mbps: float = 10.0
    feature_044_report_path: str = FEATURE_044_REPORT_PATH

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("CompletionRootCauseConfig.feature_id must equal 045-completion-root-cause-diagnosis.")
        if self.episode_length != 110:
            raise ValueError("CompletionRootCauseConfig.episode_length must equal 110.")
        if self.timeout_slots != 20:
            raise ValueError("CompletionRootCauseConfig.timeout_slots must equal 20.")
        if self.node_count != 20:
            raise ValueError("CompletionRootCauseConfig.node_count must equal 20.")
        if self.arrival_probability != 0.5:
            raise ValueError("CompletionRootCauseConfig.arrival_probability must equal 0.5.")
        if list(self.seeds) != [0, 1, 2]:
            raise ValueError("CompletionRootCauseConfig.seeds must equal [0, 1, 2].")
        if tuple(self.strategies) != TRACE_STRATEGIES:
            raise ValueError("CompletionRootCauseConfig.strategies must match the approved probe strategies.")
        if self.no_runtime_repair is not True or self.no_training is not True:
            raise ValueError("CompletionRootCauseConfig diagnostic-only flags must remain true.")
        if self.slot_duration_seconds != 0.1:
            raise ValueError("CompletionRootCauseConfig.slot_duration_seconds must equal 0.1.")
        if tuple(self.task_size_range_mbits) != (2.0, 5.0):
            raise ValueError("CompletionRootCauseConfig.task_size_range_mbits must equal (2.0, 5.0).")
        if self.processing_density_gcycles_per_mbit != 0.297:
            raise ValueError("CompletionRootCauseConfig.processing_density_gcycles_per_mbit must equal 0.297.")
        if self.cpu_private_gcycles_per_slot != 0.5 or self.cpu_public_gcycles_per_slot != 0.5 or self.cpu_cloud_gcycles_per_slot != 3.0:
            raise ValueError("CompletionRootCauseConfig.cpu capacities must equal 0.5/0.5/3.0.")
        if self.horizontal_rate_mbps != 30.0 or self.vertical_rate_mbps != 10.0:
            raise ValueError("CompletionRootCauseConfig.transmission rates must equal 30.0/10.0.")
