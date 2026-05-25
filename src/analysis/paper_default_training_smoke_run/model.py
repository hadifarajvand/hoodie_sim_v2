from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .config import READY_NEXT_FEATURE, FEATURE_ID

ALLOWED_FINAL_VERDICTS = (
    "paper_default_training_smoke_passed",
    "paper_default_training_smoke_blocked",
)


def _ensure_bool(value: Any, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{field_name} must be a boolean")
    return value


def _ensure_unique_names(entries: list[dict[str, Any]]) -> list[str]:
    names = [str(entry.get("name")) for entry in entries]
    if len(names) != len(set(names)):
        raise ValueError("prerequisite_tags_verified names must be unique")
    return names


def _summary_bool(summary: dict[str, Any], field_name: str, key: str) -> bool:
    return _ensure_bool(summary.get(key), f"{field_name}.{key}")


@dataclass(frozen=True, slots=True)
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
    final_verdict: str = "paper_default_training_smoke_blocked"

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must equal 055-paper-default-training-smoke-run")
        if self.final_verdict not in ALLOWED_FINAL_VERDICTS:
            raise ValueError("invalid final_verdict")

        _ensure_unique_names(self.prerequisite_tags_verified)
        feature_054_ready = _ensure_bool(self.feature_054_readiness_verified, "feature_054_readiness_verified")
        live_environment_training_used = _ensure_bool(self.live_environment_training_used, "live_environment_training_used")
        fixture_training_used = _ensure_bool(self.fixture_training_used, "fixture_training_used")

        replay_inserted = _summary_bool(self.replay_summary, "replay_summary", "replay_inserted")
        replay_size = int(self.replay_summary.get("replay_size", 0))
        optimizer_steps_executed = _summary_bool(self.optimizer_step_summary, "optimizer_step_summary", "optimizer_steps_executed")
        optimizer_step_count = int(self.optimizer_step_summary.get("optimizer_step_count", 0))
        loss_is_finite = _summary_bool(self.loss_summary, "loss_summary", "loss_is_finite")
        checkpoint_schema_valid = _summary_bool(self.checkpoint_summary, "checkpoint_summary", "checkpoint_schema_valid")
        model_checkpoint_written = _summary_bool(self.checkpoint_summary, "checkpoint_summary", "model_checkpoint_written")
        legal_action_only = _summary_bool(self.legal_action_summary, "legal_action_summary", "legal_action_only")
        delayed_reward_contract_preserved = _summary_bool(
            self.delayed_reward_contract_verified,
            "delayed_reward_contract_verified",
            "delayed_reward_contract_preserved",
        )
        train_eval_trace_banks_disjoint = _summary_bool(
            self.train_eval_contract_verified,
            "train_eval_contract_verified",
            "train_eval_trace_banks_disjoint",
        )
        behavior_gate_values = [
            _summary_bool(self.behavior_safety_summary, "behavior_safety_summary", key)
            for key in (
                "no_full_campaign",
                "no_baseline_comparison",
                "no_paper_reproduction_claim",
                "no_policy_drift",
                "no_dependency_drift",
                "no_environment_contract_drift",
            )
        ]
        all_behavior_safe = all(behavior_gate_values)

        ready = (
            feature_054_ready
            and live_environment_training_used
            and not fixture_training_used
            and replay_inserted
            and replay_size > 0
            and optimizer_steps_executed
            and optimizer_step_count > 0
            and loss_is_finite
            and legal_action_only
            and checkpoint_schema_valid
            and not model_checkpoint_written
            and delayed_reward_contract_preserved
            and train_eval_trace_banks_disjoint
            and all_behavior_safe
            and not self.remaining_blockers
        )

        if ready:
            if self.feature_054_readiness_verified is not True:
                raise ValueError("feature_054_readiness_verified must be true on the pass path")
            if self.final_verdict != "paper_default_training_smoke_passed":
                raise ValueError("passing smoke reports must use the passed verdict")
            if self.recommended_next_feature != READY_NEXT_FEATURE:
                raise ValueError("passing smoke reports must route to Feature 056")
            return

        if self.final_verdict != "paper_default_training_smoke_blocked":
            raise ValueError("blocked smoke reports must use the blocked verdict")
        if not self.remaining_blockers:
            raise ValueError("blocked smoke reports must report at least one blocker")
        if self.recommended_next_feature == READY_NEXT_FEATURE:
            raise ValueError("blocked smoke reports must not route to Feature 056")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
