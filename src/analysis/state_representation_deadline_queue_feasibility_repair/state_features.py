from __future__ import annotations

from typing import Any

from src.analysis.full_training_reproduction_campaign.replay import build_state_vector

from .config import LEGACY_STATE_REPRESENTATION_PROFILE, NEW_STATE_REPRESENTATION_PROFILE

LEGACY_STATE_FEATURE_NAMES = ["slot_norm", "task_size_norm", "processing_density_norm"]

NEW_STATE_FEATURE_NAMES = [
    "slot_norm",
    "task_size_norm",
    "processing_density_norm",
    "basic_queue_load_norm",
    "history_length_norm",
    "timeout_length_norm",
    "absolute_deadline_slot_norm",
    "remaining_time_to_deadline_norm",
    "deadline_slack_norm",
    "deadline_urgency_ratio",
    "is_deadline_immediate",
    "local_estimated_total_slots_norm",
    "horizontal_estimated_total_slots_norm",
    "vertical_estimated_total_slots_norm",
    "local_deadline_slack_norm",
    "horizontal_deadline_slack_norm",
    "vertical_deadline_slack_norm",
    "local_feasible_before_deadline",
    "horizontal_feasible_before_deadline",
    "vertical_feasible_before_deadline",
    "local_private_queue_load_norm",
    "public_offloading_queue_load_norm",
    "horizontal_path_queue_load_norm",
    "vertical_cloud_path_queue_load_norm",
    "pending_task_pressure_norm",
    "legal_local",
    "legal_horizontal",
    "legal_vertical",
    "legal_action_count_norm",
    "source_agent_id_norm",
]

STATE_FEATURE_GROUPS: dict[str, list[str]] = {
    "minimal": list(LEGACY_STATE_FEATURE_NAMES),
    "deadline_timeout": [
        "timeout_length_norm",
        "absolute_deadline_slot_norm",
        "remaining_time_to_deadline_norm",
        "deadline_slack_norm",
        "deadline_urgency_ratio",
        "is_deadline_immediate",
    ],
    "action_path_feasibility": [
        "local_estimated_total_slots_norm",
        "horizontal_estimated_total_slots_norm",
        "vertical_estimated_total_slots_norm",
        "local_deadline_slack_norm",
        "horizontal_deadline_slack_norm",
        "vertical_deadline_slack_norm",
        "local_feasible_before_deadline",
        "horizontal_feasible_before_deadline",
        "vertical_feasible_before_deadline",
    ],
    "queue_pressure": [
        "local_private_queue_load_norm",
        "public_offloading_queue_load_norm",
        "horizontal_path_queue_load_norm",
        "vertical_cloud_path_queue_load_norm",
        "pending_task_pressure_norm",
    ],
    "legal_availability": [
        "legal_local",
        "legal_horizontal",
        "legal_vertical",
        "legal_action_count_norm",
    ],
    "source_context": ["source_agent_id_norm"],
}

OPTIONAL_OR_APPROXIMATED_FEATURES = [
    "local_private_queue_load_norm",
    "public_offloading_queue_load_norm",
    "horizontal_path_queue_load_norm",
    "vertical_cloud_path_queue_load_norm",
    "pending_task_pressure_norm",
]

MISSING_OR_APPROXIMATED_STATE_FEATURES = [
    "previous_action",
    "previous_reward",
    "previous_terminal_outcome_hint",
    "queue_load per path is approximated from available global queue/load and path hints",
]


def state_feature_names(state_representation_profile: str) -> list[str]:
    if state_representation_profile == LEGACY_STATE_REPRESENTATION_PROFILE:
        return list(LEGACY_STATE_FEATURE_NAMES)
    if state_representation_profile == NEW_STATE_REPRESENTATION_PROFILE:
        return list(NEW_STATE_FEATURE_NAMES)
    raise ValueError(f"Unsupported state representation profile: {state_representation_profile}")


def build_profiled_state_vector(
    *,
    observation: dict[str, Any],
    current_task: Any | None,
    episode_length: int,
    state_representation_profile: str,
) -> tuple[float, ...]:
    return build_state_vector(
        observation=observation,
        current_task=current_task,
        episode_length=episode_length,
        state_representation_profile=state_representation_profile,
    )


def state_feature_group_coverage() -> dict[str, Any]:
    return {
        "minimal": {"covered": True, "feature_names": list(LEGACY_STATE_FEATURE_NAMES)},
        "deadline_timeout": {"covered": True, "feature_names": list(STATE_FEATURE_GROUPS["deadline_timeout"])},
        "action_path_feasibility": {"covered": True, "feature_names": list(STATE_FEATURE_GROUPS["action_path_feasibility"])},
        "queue_pressure": {"covered": True, "feature_names": list(STATE_FEATURE_GROUPS["queue_pressure"])},
        "legal_availability": {"covered": True, "feature_names": list(STATE_FEATURE_GROUPS["legal_availability"])},
        "source_context": {"covered": True, "feature_names": list(STATE_FEATURE_GROUPS["source_context"])},
        "optional_history": {
            "covered": False,
            "feature_names": ["previous_action", "previous_reward", "previous_terminal_outcome_hint"],
        },
    }
