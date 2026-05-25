from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .config import FEATURE_ID, READY_NEXT_FEATURE

ALLOWED_FINAL_VERDICTS = (
    "target_update_replay_validation_passed",
    "feature_055_prerequisite_blocked",
    "replay_insertion_blocked",
    "replay_sampling_blocked",
    "optimizer_step_counter_blocked",
    "target_update_contract_blocked",
    "checkpoint_metadata_blocked",
    "behavior_drift_detected",
)

REPAIR_ROUTING = {
    "feature_055_prerequisite_blocked": "Feature 055 smoke repair",
    "replay_insertion_blocked": "replay insertion repair",
    "replay_sampling_blocked": "replay sampling repair",
    "optimizer_step_counter_blocked": "optimizer step counter repair",
    "target_update_contract_blocked": "target-update contract repair",
    "checkpoint_metadata_blocked": "checkpoint metadata repair",
    "behavior_drift_detected": "behavior drift repair",
}


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
class TargetUpdateReplayValidationReport:
    feature_id: str
    prerequisite_tags_verified: list[dict[str, Any]]
    feature_055_smoke_verified: bool
    replay_insertion_validated: bool
    replay_sampling_validated: bool
    optimizer_step_counter_validated: bool
    target_update_contract_validated: bool
    target_sync_schedule_validated: bool
    target_sync_before_threshold_blocked: bool
    target_sync_at_threshold_validated: bool
    checkpoint_metadata_validated: bool
    replay_summary: dict[str, Any]
    optimizer_step_summary: dict[str, Any]
    target_update_summary: dict[str, Any]
    checkpoint_metadata_summary: dict[str, Any]
    behavior_safety_summary: dict[str, Any]
    remaining_blockers: list[str] = field(default_factory=list)
    recommended_next_feature: str = ""
    final_verdict: str = "feature_055_prerequisite_blocked"

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must equal 056-target-update-and-replay-training-validation")
        if self.final_verdict not in ALLOWED_FINAL_VERDICTS:
            raise ValueError("invalid final_verdict")

        _ensure_unique_names(self.prerequisite_tags_verified)
        feature_055_ready = _ensure_bool(self.feature_055_smoke_verified, "feature_055_smoke_verified")
        replay_insertion_validated = _ensure_bool(self.replay_insertion_validated, "replay_insertion_validated")
        replay_sampling_validated = _ensure_bool(self.replay_sampling_validated, "replay_sampling_validated")
        optimizer_step_counter_validated = _ensure_bool(self.optimizer_step_counter_validated, "optimizer_step_counter_validated")
        target_update_contract_validated = _ensure_bool(self.target_update_contract_validated, "target_update_contract_validated")
        target_sync_schedule_validated = _ensure_bool(self.target_sync_schedule_validated, "target_sync_schedule_validated")
        target_sync_before_threshold_blocked = _ensure_bool(self.target_sync_before_threshold_blocked, "target_sync_before_threshold_blocked")
        target_sync_at_threshold_validated = _ensure_bool(self.target_sync_at_threshold_validated, "target_sync_at_threshold_validated")
        checkpoint_metadata_validated = _ensure_bool(self.checkpoint_metadata_validated, "checkpoint_metadata_validated")

        _required_keys(
            self.replay_summary,
            "replay_summary",
            (
                "replay_size",
                "replay_inserted",
                "sampled_batch_size",
                "sampled_field_coverage",
                "delayed_reward_semantics_preserved",
            ),
        )
        _required_keys(
            self.optimizer_step_summary,
            "optimizer_step_summary",
            (
                "optimizer_step_count",
                "optimizer_step_sequence",
                "optimizer_step_monotonic",
                "optimizer_steps_executed",
            ),
        )
        _required_keys(
            self.target_update_summary,
            "target_update_summary",
            (
                "target_update_unit",
                "target_update_frequency",
                "no_sync_before_threshold",
                "sync_at_threshold",
                "threshold_step",
                "simulation_deterministic",
            ),
        )
        _required_keys(
            self.checkpoint_metadata_summary,
            "checkpoint_metadata_summary",
            (
                "target_update_unit",
                "optimizer_step_count",
                "replay_size",
                "config_hash",
                "train_trace_bank_id",
                "eval_trace_bank_id",
                "seed_bundle",
            ),
        )

        replay_size = int(self.replay_summary.get("replay_size", 0))
        sampled_batch_size = int(self.replay_summary.get("sampled_batch_size", 0))
        optimizer_step_count = int(self.optimizer_step_summary.get("optimizer_step_count", 0))
        optimizer_step_sequence = list(self.optimizer_step_summary.get("optimizer_step_sequence", []))
        optimizer_step_monotonic = _ensure_bool(self.optimizer_step_summary.get("optimizer_step_monotonic"), "optimizer_step_summary.optimizer_step_monotonic")
        optimizer_steps_executed = _ensure_bool(self.optimizer_step_summary.get("optimizer_steps_executed"), "optimizer_step_summary.optimizer_steps_executed")
        replay_inserted = _ensure_bool(self.replay_summary.get("replay_inserted"), "replay_summary.replay_inserted")
        delayed_reward_semantics_preserved = _ensure_bool(
            self.replay_summary.get("delayed_reward_semantics_preserved"),
            "replay_summary.delayed_reward_semantics_preserved",
        )
        sampled_field_coverage = dict(self.replay_summary.get("sampled_field_coverage", {}))
        coverage_expected = ("state", "action", "legal_action_mask", "next_state", "reward", "terminal", "reward_available", "pending_at_horizon")
        coverage_ok = all(bool(sampled_field_coverage.get(name)) for name in coverage_expected)
        target_update_unit = self.target_update_summary.get("target_update_unit")
        target_update_frequency = int(self.target_update_summary.get("target_update_frequency", 0))
        no_sync_before_threshold = _ensure_bool(self.target_update_summary.get("no_sync_before_threshold"), "target_update_summary.no_sync_before_threshold")
        sync_at_threshold = _ensure_bool(self.target_update_summary.get("sync_at_threshold"), "target_update_summary.sync_at_threshold")
        threshold_step = int(self.target_update_summary.get("threshold_step", 0))
        simulation_deterministic = _ensure_bool(self.target_update_summary.get("simulation_deterministic"), "target_update_summary.simulation_deterministic")

        checkpoint_target_unit = self.checkpoint_metadata_summary.get("target_update_unit")
        checkpoint_optimizer_step_count = int(self.checkpoint_metadata_summary.get("optimizer_step_count", 0))
        checkpoint_replay_size = int(self.checkpoint_metadata_summary.get("replay_size", 0))

        behavior_keys = (
            "no_full_campaign",
            "no_baseline_comparison",
            "no_paper_reproduction_claim",
            "no_policy_drift",
            "no_dependency_drift",
            "no_environment_contract_drift",
            "no_reward_timing_change",
            "no_prior_artifact_rewrite",
        )
        behavior_values = {key: _ensure_bool(self.behavior_safety_summary.get(key), f"behavior_safety_summary.{key}") for key in behavior_keys}
        behavior_safe = all(behavior_values.values())

        ready = (
            feature_055_ready
            and replay_insertion_validated
            and replay_sampling_validated
            and optimizer_step_counter_validated
            and target_update_contract_validated
            and target_sync_schedule_validated
            and target_sync_before_threshold_blocked
            and target_sync_at_threshold_validated
            and checkpoint_metadata_validated
            and behavior_safe
            and not self.remaining_blockers
        )

        if ready:
            if self.final_verdict != "target_update_replay_validation_passed":
                raise ValueError("passing reports must use the passed verdict")
            if self.recommended_next_feature != READY_NEXT_FEATURE:
                raise ValueError("passing reports must route to Feature 057")
            if replay_size <= 0 or sampled_batch_size <= 0:
                raise ValueError("passing reports must show positive replay evidence")
            if optimizer_step_count <= 0:
                raise ValueError("passing reports must show positive optimizer steps")
            if not optimizer_step_monotonic or not optimizer_steps_executed:
                raise ValueError("passing reports must validate optimizer-step monotonicity")
            if target_update_unit != "optimizer_step" or target_update_frequency != 2000:
                raise ValueError("passing reports must preserve the approved target-update contract")
            if not no_sync_before_threshold or not sync_at_threshold or threshold_step != 2000 or not simulation_deterministic:
                raise ValueError("passing reports must validate the target-sync threshold schedule")
            if not replay_inserted or not delayed_reward_semantics_preserved or not coverage_ok:
                raise ValueError("passing reports must validate replay insertion and sampling semantics")
            if checkpoint_target_unit != "optimizer_step" or checkpoint_optimizer_step_count != optimizer_step_count or checkpoint_replay_size != replay_size:
                raise ValueError("passing reports must validate checkpoint metadata")
            return

        if self.final_verdict == "target_update_replay_validation_passed":
            raise ValueError("blocked reports cannot claim pass")
        if not self.remaining_blockers:
            raise ValueError("blocked reports must include blockers")
        if self.recommended_next_feature == READY_NEXT_FEATURE:
            raise ValueError("blocked reports must not route to Feature 057")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
