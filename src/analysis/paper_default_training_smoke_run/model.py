from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class PaperDefaultTrainingSmokeReport:
    feature_id: str
    prerequisite_tags_verified: list[dict[str, Any]]
    feature_054_readiness_verified: bool
    paper_default_smoke_scope: dict[str, Any]
    live_environment_training_used: bool
    fixture_training_used: bool
    replay_summary: dict[str, Any]
    optimizer_step_summary: dict[str, Any]
    loss_summary: dict[str, Any]
    checkpoint_summary: dict[str, Any]
    legal_action_summary: dict[str, Any]
    delayed_reward_contract_verified: dict[str, Any]
    train_eval_contract_verified: dict[str, Any]
    behavior_safety_summary: dict[str, Any]
    remaining_blockers: list[str] = field(default_factory=list)
    recommended_next_feature: str = ""
    final_verdict: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
