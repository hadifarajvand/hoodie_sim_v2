from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

BreakpointClassification = Literal[
    "completion_lifecycle_valid",
    "completion_lifecycle_counter_bug_detected",
    "completion_lifecycle_runtime_bug_detected",
    "completion_absence_explained_by_queue_pressure",
    "formula_mismatch_detected",
    "audit_inconclusive_requires_runtime_trace_instrumentation",
    "prerequisite_blocked",
]


@dataclass(frozen=True, slots=True)
class LifecycleTraceCounters:
    generated_count: int
    admitted_count: int
    transmission_started_count: int
    transmission_completed_count: int
    finalized_task_count: int
    finalized_completion_count: int
    finalized_drop_count: int
    observed_execution_started_count: int | None
    observed_execution_completed_count: int | None
    pending_at_horizon_count: int
    reward_count: int
    terminal_count: int
    legal_action_count: int
    illegal_action_count: int

    def to_dict(self) -> dict[str, int]:
        return {
            "generated_count": self.generated_count,
            "admitted_count": self.admitted_count,
            "transmission_started_count": self.transmission_started_count,
            "transmission_completed_count": self.transmission_completed_count,
            "finalized_task_count": self.finalized_task_count,
            "finalized_completion_count": self.finalized_completion_count,
            "finalized_drop_count": self.finalized_drop_count,
            "observed_execution_started_count": self.observed_execution_started_count,
            "observed_execution_completed_count": self.observed_execution_completed_count,
            "pending_at_horizon_count": self.pending_at_horizon_count,
            "reward_count": self.reward_count,
            "terminal_count": self.terminal_count,
            "legal_action_count": self.legal_action_count,
            "illegal_action_count": self.illegal_action_count,
        }


@dataclass(frozen=True, slots=True)
class LifecycleTraceEvidence:
    strategy: str
    seed: int
    available_metadata: list[str]
    counters: LifecycleTraceCounters
    runtime_trace_available: bool
    metadata_insufficient: bool
    note: str

    def to_dict(self) -> dict[str, object]:
        return {
            "strategy": self.strategy,
            "seed": self.seed,
            "available_metadata": list(self.available_metadata),
            "counters": self.counters.to_dict(),
            "runtime_trace_available": self.runtime_trace_available,
            "metadata_insufficient": self.metadata_insufficient,
            "note": self.note,
        }
