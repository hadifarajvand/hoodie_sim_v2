from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .config import FEATURE_ID, READY_NEXT_FEATURE

ALLOWED_FINAL_VERDICTS = (
    "paper_default_pilot_training_passed",
    "feature_056_prerequisite_blocked",
    "pilot_scope_blocked",
    "replay_growth_blocked",
    "optimizer_progress_blocked",
    "loss_or_reward_blocked",
    "legal_action_blocked",
    "checkpoint_metadata_blocked",
    "behavior_drift_detected",
)


def _ensure_bool(value: Any, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{field_name} must be a boolean")
    return value


def _ensure_unique_names(entries: list[dict[str, Any]]) -> None:
    names = [str(entry.get("name")) for entry in entries]
    if len(names) != len(set(names)):
        raise ValueError("prerequisite_tags_verified names must be unique")


def _required_keys(summary: dict[str, Any], field_name: str, keys: tuple[str, ...]) -> None:
    missing = [key for key in keys if key not in summary]
    if missing:
        raise ValueError(f"{field_name} is missing required keys: {missing}")


@dataclass(frozen=True, slots=True)
class PaperDefaultPilotTrainingRunReport:
    feature_id: str
    prerequisite_tags_verified: list[dict[str, Any]]
    feature_056_validation_verified: bool
    pilot_scope: dict[str, Any]
    live_environment_training_used: bool
    fixture_training_used: bool
    episode_summary: dict[str, Any]
    replay_summary: dict[str, Any]
    optimizer_summary: dict[str, Any]
    target_update_summary: dict[str, Any]
    loss_summary: dict[str, Any]
    reward_summary: dict[str, Any]
    legal_action_summary: dict[str, Any]
    checkpoint_summary: dict[str, Any]
    train_eval_contract_verified: dict[str, Any]
    behavior_safety_summary: dict[str, Any]
    remaining_blockers: list[str] = field(default_factory=list)
    recommended_next_feature: str = ""
    final_verdict: str = "feature_056_prerequisite_blocked"

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must equal 057-paper-default-pilot-training-run")
        if self.final_verdict not in ALLOWED_FINAL_VERDICTS:
            raise ValueError("invalid final_verdict")

        _ensure_unique_names(self.prerequisite_tags_verified)

        feature_056_validation_verified = _ensure_bool(self.feature_056_validation_verified, "feature_056_validation_verified")
        live_environment_training_used = _ensure_bool(self.live_environment_training_used, "live_environment_training_used")
        fixture_training_used = _ensure_bool(self.fixture_training_used, "fixture_training_used")

        _required_keys(
            self.pilot_scope,
            "pilot_scope",
            ("pilot_episodes", "pilot_episode_length", "full_campaign", "baseline_comparison", "paper_reproduction_claim"),
        )
        _required_keys(
            self.episode_summary,
            "episode_summary",
            ("pilot_episodes", "pilot_episode_length", "episodes_requested", "episodes_completed", "completed_all_episodes"),
        )
        _required_keys(
            self.replay_summary,
            "replay_summary",
            (
                "feature_055_smoke_replay_size",
                "replay_size",
                "replay_growth_count",
                "replay_growth_validated",
                "sampled_batch_size",
                "replay_inserted",
                "sampled_field_coverage",
                "delayed_reward_semantics_preserved",
                "pending_at_horizon_preserved",
            ),
        )
        _required_keys(
            self.optimizer_summary,
            "optimizer_summary",
            (
                "feature_055_smoke_optimizer_step_count",
                "optimizer_step_count",
                "optimizer_step_growth_count",
                "optimizer_progress_validated",
                "optimizer_steps_executed",
            ),
        )
        _required_keys(
            self.target_update_summary,
            "target_update_summary",
            ("target_update_unit", "target_update_frequency", "target_sync_count", "target_sync_before_threshold_blocked"),
        )
        _required_keys(
            self.loss_summary,
            "loss_summary",
            ("loss_count", "all_losses_finite", "min_loss", "max_loss", "mean_loss"),
        )
        _required_keys(
            self.reward_summary,
            "reward_summary",
            ("reward_count", "reward_available_count", "delayed_reward_contract_preserved", "pending_at_horizon_preserved"),
        )
        _required_keys(
            self.legal_action_summary,
            "legal_action_summary",
            ("legal_action_only", "illegal_action_count"),
        )
        _required_keys(
            self.checkpoint_summary,
            "checkpoint_summary",
            ("checkpoint_schema_valid", "metadata_only", "model_checkpoint_written", "keys_present", "checkpoint_metadata"),
        )
        _required_keys(
            self.train_eval_contract_verified,
            "train_eval_contract_verified",
            ("train_eval_trace_banks_disjoint", "trace_bank_ids", "evaluation_on_training_traces"),
        )
        behavior_keys = (
            "no_full_campaign",
            "no_baseline_comparison",
            "no_paper_reproduction_claim",
            "no_performance_claim",
            "no_policy_drift",
            "no_dependency_drift",
            "no_environment_contract_drift",
            "no_reward_timing_change",
            "no_prior_artifact_rewrite",
        )
        _required_keys(self.behavior_safety_summary, "behavior_safety_summary", behavior_keys)

        pilot_episodes = int(self.pilot_scope.get("pilot_episodes", 0))
        pilot_episode_length = int(self.pilot_scope.get("pilot_episode_length", 0))
        pilot_scope_ok = (
            pilot_episodes > 1
            and pilot_episode_length == 110
            and self.pilot_scope.get("full_campaign") is False
            and self.pilot_scope.get("baseline_comparison") is False
            and self.pilot_scope.get("paper_reproduction_claim") is False
        )

        completed_all_episodes = _ensure_bool(self.episode_summary.get("completed_all_episodes"), "episode_summary.completed_all_episodes")
        episodes_completed = int(self.episode_summary.get("episodes_completed", 0))
        episodes_requested = int(self.episode_summary.get("episodes_requested", 0))
        replay_size = int(self.replay_summary.get("replay_size", 0))
        replay_growth_count = int(self.replay_summary.get("replay_growth_count", 0))
        replay_growth_validated = _ensure_bool(self.replay_summary.get("replay_growth_validated"), "replay_summary.replay_growth_validated")
        sampled_batch_size = int(self.replay_summary.get("sampled_batch_size", 0))
        replay_inserted = _ensure_bool(self.replay_summary.get("replay_inserted"), "replay_summary.replay_inserted")
        delayed_reward_semantics_preserved = _ensure_bool(
            self.replay_summary.get("delayed_reward_semantics_preserved"),
            "replay_summary.delayed_reward_semantics_preserved",
        )
        pending_at_horizon_preserved = _ensure_bool(
            self.replay_summary.get("pending_at_horizon_preserved"),
            "replay_summary.pending_at_horizon_preserved",
        )

        feature_055_smoke_replay_size = int(self.replay_summary.get("feature_055_smoke_replay_size", 0))
        feature_055_smoke_optimizer_step_count = int(self.optimizer_summary.get("feature_055_smoke_optimizer_step_count", 0))
        optimizer_step_count = int(self.optimizer_summary.get("optimizer_step_count", 0))
        optimizer_step_growth_count = int(self.optimizer_summary.get("optimizer_step_growth_count", 0))
        optimizer_progress_validated = _ensure_bool(self.optimizer_summary.get("optimizer_progress_validated"), "optimizer_summary.optimizer_progress_validated")
        optimizer_steps_executed = _ensure_bool(self.optimizer_summary.get("optimizer_steps_executed"), "optimizer_summary.optimizer_steps_executed")

        all_losses_finite = _ensure_bool(self.loss_summary.get("all_losses_finite"), "loss_summary.all_losses_finite")
        loss_count = int(self.loss_summary.get("loss_count", 0))
        legal_action_only = _ensure_bool(self.legal_action_summary.get("legal_action_only"), "legal_action_summary.legal_action_only")
        illegal_action_count = int(self.legal_action_summary.get("illegal_action_count", 0))
        checkpoint_schema_valid = _ensure_bool(self.checkpoint_summary.get("checkpoint_schema_valid"), "checkpoint_summary.checkpoint_schema_valid")
        model_checkpoint_written = _ensure_bool(self.checkpoint_summary.get("model_checkpoint_written"), "checkpoint_summary.model_checkpoint_written")
        train_eval_trace_banks_disjoint = _ensure_bool(
            self.train_eval_contract_verified.get("train_eval_trace_banks_disjoint"),
            "train_eval_contract_verified.train_eval_trace_banks_disjoint",
        )
        behavior_safe = all(_ensure_bool(self.behavior_safety_summary.get(key), f"behavior_safety_summary.{key}") for key in behavior_keys)

        ready = (
            feature_056_validation_verified
            and pilot_scope_ok
            and live_environment_training_used
            and not fixture_training_used
            and completed_all_episodes
            and episodes_completed == episodes_requested == pilot_episodes
            and replay_inserted
            and replay_size > feature_055_smoke_replay_size
            and replay_growth_count == replay_size - feature_055_smoke_replay_size
            and replay_growth_validated
            and sampled_batch_size > 0
            and optimizer_steps_executed
            and optimizer_step_count > feature_055_smoke_optimizer_step_count
            and optimizer_step_growth_count == optimizer_step_count - feature_055_smoke_optimizer_step_count
            and optimizer_progress_validated
            and all_losses_finite
            and loss_count > 0
            and legal_action_only
            and illegal_action_count == 0
            and checkpoint_schema_valid
            and not model_checkpoint_written
            and train_eval_trace_banks_disjoint
            and delayed_reward_semantics_preserved
            and pending_at_horizon_preserved
            and behavior_safe
            and not self.remaining_blockers
        )

        if ready:
            if self.feature_056_validation_verified is not True:
                raise ValueError("feature_056_validation_verified must be true on the pass path")
            if self.final_verdict != "paper_default_pilot_training_passed":
                raise ValueError("passing pilot reports must use the passed verdict")
            if self.recommended_next_feature != READY_NEXT_FEATURE:
                raise ValueError("passing pilot reports must route to Feature 058")
            return

        if self.final_verdict == "paper_default_pilot_training_passed":
            raise ValueError("blocked pilot reports cannot claim pass")
        if not self.remaining_blockers:
            raise ValueError("blocked pilot reports must include blockers")
        if self.recommended_next_feature == READY_NEXT_FEATURE:
            raise ValueError("blocked pilot reports must not route to Feature 058")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
