from __future__ import annotations

from pathlib import Path
import tempfile
from typing import Any

from src.analysis.deadline_timeout_feasible_workload_calibration.calibration import build_calibration_profile, patched_calibrated_environment
from src.analysis.full_training_reproduction_campaign.replay import build_state_vector, state_dimension_for_profile
from src.analysis.full_training_reproduction_campaign.trainer import _build_environment

from .config import (
    CALIBRATION_PROFILE_NAME,
    EVALUATION_EPISODE_COUNT,
    EPISODE_LENGTH,
    NEW_STATE_REPRESENTATION_PROFILE,
    STATE_REPRESENTATION_PROFILE_LEGACY_MINIMAL,
)
from .state_features import LEGACY_STATE_FEATURE_NAMES, NEW_STATE_FEATURE_NAMES, state_feature_group_coverage
from .state_profile_adapter import build_profiled_campaign_config


def _choose_first_legal_action(legal_action_mask: dict[str, bool]) -> str | None:
    for action in ("local", "horizontal", "vertical"):
        if legal_action_mask.get(action, False):
            return action
    return None


def _sample_state_records(
    *,
    state_representation_profile: str,
    episode_count: int,
    episode_length: int,
    sample_limit: int,
) -> list[dict[str, Any]]:
    calibration_root = Path(tempfile.gettempdir()) / "calibrated-traces"
    calibration_profile = build_calibration_profile(calibration_root)
    records: list[dict[str, Any]] = []
    with patched_calibrated_environment(calibration_profile):
        for episode_index in range(episode_count):
            env = _build_environment(
                build_profiled_campaign_config(state_representation_profile=state_representation_profile),
                episode_length=episode_length,
                seed=episode_index,
            )
            env.reset(seed=episode_index)
            while len(records) < sample_limit:
                current_task = env.current_task
                observation = env.observe_flat(current_task) if current_task is not None else env.observe_flat()
                state_vector = build_state_vector(
                    observation=observation,
                    current_task=current_task,
                    episode_length=episode_length,
                    state_representation_profile=state_representation_profile,
                )
                legal_action_mask = dict(observation.get("legal_action_mask", {}))
                records.append(
                    {
                        "episode_id": episode_index,
                        "slot": int(env.current_slot),
                        "state_dim": len(state_vector),
                        "state_representation_profile": state_representation_profile,
                        "state_vector": list(state_vector),
                        "task_id": int(getattr(current_task, "task_id", 0) if current_task is not None else 0),
                        "source_agent_id": int(getattr(current_task, "source_agent_id", 0) if current_task is not None else 0),
                        "queue_load": int(observation.get("queue_load", 0) or 0),
                        "legal_action_mask": dict(legal_action_mask),
                        "selected_action": _choose_first_legal_action(legal_action_mask),
                    }
                )
                if len(records) >= sample_limit:
                    break
                action = _choose_first_legal_action(legal_action_mask)
                next_observation, reward, terminated, truncated, info = env.step(action)
                if terminated or truncated:
                    break
    return records


def build_state_feature_coverage_audit(*, sample_limit: int = 25) -> dict[str, Any]:
    legacy_state_dim = state_dimension_for_profile(STATE_REPRESENTATION_PROFILE_LEGACY_MINIMAL)
    new_state_dim = state_dimension_for_profile(NEW_STATE_REPRESENTATION_PROFILE)
    state_sample_records = _sample_state_records(
        state_representation_profile=NEW_STATE_REPRESENTATION_PROFILE,
        episode_count=EVALUATION_EPISODE_COUNT,
        episode_length=EPISODE_LENGTH,
        sample_limit=sample_limit,
    )
    flattened_values = [float(value) for record in state_sample_records for value in record.get("state_vector", [])]
    state_vector_min = min(flattened_values) if flattened_values else 0.0
    state_vector_max = max(flattened_values) if flattened_values else 0.0
    state_normalization_summary = {
        "no_nan_in_state_vector": all(value == value for value in flattened_values),
        "no_inf_in_state_vector": all(value not in {float("inf"), float("-inf")} for value in flattened_values),
        "state_vector_min": state_vector_min,
        "state_vector_max": state_vector_max,
        "state_dim_consistent_across_train_eval": all(record.get("state_dim") == new_state_dim for record in state_sample_records),
    }
    return {
        "legacy_state_dim": legacy_state_dim,
        "new_state_dim": new_state_dim,
        "added_feature_count": new_state_dim - legacy_state_dim,
        "added_feature_names": list(NEW_STATE_FEATURE_NAMES[legacy_state_dim:]),
        "missing_or_approximated_state_features": [
            "previous_action",
            "previous_reward",
            "previous_terminal_outcome_hint",
            "path-specific queue pressure is approximated from global queue/load and available path hints",
        ],
        "state_feature_group_coverage": state_feature_group_coverage(),
        "state_normalization_summary": state_normalization_summary,
        "state_sample_records": state_sample_records,
        "train_eval_state_dim_match": state_normalization_summary["state_dim_consistent_across_train_eval"],
        "calibration_profile_name": CALIBRATION_PROFILE_NAME,
    }


def build_state_normalization_audit(state_feature_coverage_audit: dict[str, Any]) -> dict[str, Any]:
    summary = dict(state_feature_coverage_audit.get("state_normalization_summary", {}))
    return {
        "no_nan_in_state_vector": bool(summary.get("no_nan_in_state_vector", False)),
        "no_inf_in_state_vector": bool(summary.get("no_inf_in_state_vector", False)),
        "state_vector_min": float(summary.get("state_vector_min", 0.0)),
        "state_vector_max": float(summary.get("state_vector_max", 0.0)),
        "state_dim_consistent_across_train_eval": bool(summary.get("state_dim_consistent_across_train_eval", False)),
        "state_samples": list(state_feature_coverage_audit.get("state_sample_records", [])),
    }
