from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class AuditRecord:
    paper_expected: str
    repo_current: str
    status: str
    evidence: str
    repair_needed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "paper_expected": self.paper_expected,
            "repo_current": self.repo_current,
            "status": self.status,
            "evidence": self.evidence,
            "repair_needed": self.repair_needed,
        }


@dataclass(slots=True)
class PolicyComparison:
    policy_name: str
    completed_count: int
    dropped_count: int
    pending_count: int
    completion_ratio: float
    drop_ratio: float
    reward_per_task: float
    reward_per_decision: float
    action_distribution: dict[str, int]
    selected_action_feasible_ratio: float
    reward_reconciled: bool
    terminal_reconciled: bool
    raw_vs_canonical_reward_delta: float
    terminal_event_coverage_ratio: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "policy_name": self.policy_name,
            "completed_count": self.completed_count,
            "dropped_count": self.dropped_count,
            "pending_count": self.pending_count,
            "completion_ratio": self.completion_ratio,
            "drop_ratio": self.drop_ratio,
            "reward_per_task": self.reward_per_task,
            "reward_per_decision": self.reward_per_decision,
            "action_distribution": dict(self.action_distribution),
            "selected_action_feasible_ratio": self.selected_action_feasible_ratio,
            "reward_reconciled": self.reward_reconciled,
            "terminal_reconciled": self.terminal_reconciled,
            "raw_vs_canonical_reward_delta": self.raw_vs_canonical_reward_delta,
            "terminal_event_coverage_ratio": self.terminal_event_coverage_ratio,
        }
