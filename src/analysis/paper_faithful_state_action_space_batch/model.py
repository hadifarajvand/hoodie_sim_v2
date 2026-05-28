from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .config import FEATURE_ID, READY_NEXT_FEATURE, REQUIRED_TOP_LEVEL_FIELDS

ALLOWED_FINAL_VERDICTS = (
    "paper_faithful_state_action_space_batch_passed",
    "feature_064_prerequisite_blocked",
    "paper_state_contract_blocked",
    "waiting_time_contract_blocked",
    "public_queue_vector_blocked",
    "load_history_contract_blocked",
    "forecast_input_contract_blocked",
    "destination_action_space_blocked",
    "legal_mask_contract_blocked",
    "compatibility_blocked",
    "behavior_drift_detected",
)


def _required_keys(summary: dict[str, Any], field_name: str, keys: tuple[str, ...]) -> None:
    missing = [key for key in keys if key not in summary]
    if missing:
        raise ValueError(f"{field_name} missing keys: {missing}")


def _unique_names(entries: list[dict[str, Any]]) -> None:
    names = [str(entry.get("name")) for entry in entries]
    if len(names) != len(set(names)):
        raise ValueError("prerequisite tag names must be unique")


@dataclass(frozen=True, slots=True)
class PaperFaithfulStateActionSpaceBatchReport:
    feature_id: str
    batch_items_covered: list[str]
    feature_064_verified: bool
    paper_state_contract_summary: dict[str, Any]
    waiting_time_summary: dict[str, Any]
    public_queue_vector_summary: dict[str, Any]
    load_history_summary: dict[str, Any]
    forecast_input_summary: dict[str, Any]
    destination_action_space_summary: dict[str, Any]
    legal_mask_summary: dict[str, Any]
    compatibility_summary: dict[str, Any]
    safety_summary: dict[str, Any]
    remaining_blockers: list[str] = field(default_factory=list)
    recommended_next_feature: str = ""
    final_verdict: str = "feature_064_prerequisite_blocked"
    prerequisite_tags_verified: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must equal 065-paper-faithful-state-action-space-batch")
        if self.final_verdict not in ALLOWED_FINAL_VERDICTS:
            raise ValueError("invalid final_verdict")
        if list(self.batch_items_covered) != [
            "Full paper state vector",
            "Private/offloading waiting times",
            "Public queue length vector",
            "W × (N+1) load history matrix",
            "LSTM forecast input based on node active queues",
            "Destination-specific action space",
            "Legal action masking for exact Edge-Agent and Cloud destinations",
        ]:
            raise ValueError("batch_items_covered must preserve the approved batch order")
        _unique_names(self.prerequisite_tags_verified)
        if not REQUIRED_TOP_LEVEL_FIELDS:
            raise ValueError("required fields unavailable")
        _required_keys(self.paper_state_contract_summary, "paper_state_contract_summary", ("paper_state_not_legacy_three_dimensional", "paper_state_version", "legacy_compact_state_present"))
        _required_keys(self.waiting_time_summary, "waiting_time_summary", ("waiting_times_explicit", "waiting_time_source", "waiting_time_exactness"))
        _required_keys(self.public_queue_vector_summary, "public_queue_vector_summary", ("public_queue_vector_not_scalar", "public_queue_vector_length", "public_queue_destination_order"))
        _required_keys(self.load_history_summary, "load_history_summary", ("load_history_shape_valid", "load_history_shape", "load_history_window_w"))
        _required_keys(self.forecast_input_summary, "forecast_input_summary", ("forecast_input_derived_from_active_queue_counts", "forecast_input_shape", "forecast_output_status"))
        _required_keys(self.destination_action_space_summary, "destination_action_space_summary", ("destination_action_space_enabled", "paper_action_count", "action_encoding_version"))
        _required_keys(self.legal_mask_summary, "legal_mask_summary", ("legal_mask_destination_specific", "paper_action_count", "mask_encoding_version"))
        _required_keys(self.compatibility_summary, "compatibility_summary", ("legacy_training_behavior_preserved", "paper_faithful_contract_available", "feature_066_required_to_bind_training", "known_non_migrated_components"))
        _required_keys(self.safety_summary, "safety_summary", ("no_training_rerun", "no_evaluation_campaign_rerun", "no_optimizer_steps", "no_replay_mutation", "no_dependency_drift", "no_prior_feature_artifact_rewrite", "no_paper_reproduction_claim", "no_unsupported_superiority_claim"))
        if not self.paper_state_contract_summary["paper_state_not_legacy_three_dimensional"]:
            raise ValueError("paper state must not be legacy three-dimensional compact state")
        if not self.destination_action_space_summary["destination_action_space_enabled"]:
            raise ValueError("destination-specific action space must be enabled")
        if not self.legal_mask_summary["legal_mask_destination_specific"]:
            raise ValueError("legal mask must be destination-specific")
        if self.final_verdict == "paper_faithful_state_action_space_batch_passed":
            if self.remaining_blockers:
                raise ValueError("passing report cannot include blockers")
            if self.recommended_next_feature != READY_NEXT_FEATURE:
                raise ValueError("passing report must route to Feature 066")
        else:
            if not self.remaining_blockers:
                raise ValueError("blocked report must include blockers")
            if self.recommended_next_feature == READY_NEXT_FEATURE:
                raise ValueError("blocked report must not route to Feature 066")

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        return payload
