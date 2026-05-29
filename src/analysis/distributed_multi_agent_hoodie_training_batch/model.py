from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class DistributedMultiAgentHOODIETrainingBatchReport:
    feature_id: str
    batch_items_covered: list[str]
    feature_065_verified: bool
    per_agent_model_summary: dict[str, Any]
    per_agent_replay_summary: dict[str, Any]
    per_agent_policy_summary: dict[str, Any]
    per_agent_optimizer_summary: dict[str, Any]
    per_agent_target_network_summary: dict[str, Any]
    epsilon_schedule_summary: dict[str, Any]
    shared_environment_interaction_summary: dict[str, Any]
    delayed_reward_assignment_summary: dict[str, Any]
    migration_summary: dict[str, Any]
    safety_summary: dict[str, Any]
    remaining_blockers: list[str] = field(default_factory=list)
    recommended_next_feature: str = ""
    final_verdict: str = "feature_065_prerequisite_blocked"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

