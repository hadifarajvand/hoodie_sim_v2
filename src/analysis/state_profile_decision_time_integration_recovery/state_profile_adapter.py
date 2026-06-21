from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from src.analysis.full_training_reproduction_campaign.config import CampaignConfig
from src.analysis.full_training_reproduction_campaign.replay import (
    STATE_REPRESENTATION_PROFILE_LEGACY_MINIMAL,
    state_dimension_for_profile,
)
from src.analysis.terminal_lifecycle_accounting_50_100_comparison import repaired_terminal_evaluator as terminal_evaluator

from .config import EPISODE_LENGTH, NEW_STATE_REPRESENTATION_PROFILE


def build_profiled_campaign_config(*, state_representation_profile: str = NEW_STATE_REPRESENTATION_PROFILE) -> CampaignConfig:
    return CampaignConfig(
        state_representation_profile=state_representation_profile,
        state_dim=state_dimension_for_profile(state_representation_profile),
        evaluation_trace_bank_id="state-repair-eval-bank",
        training_trace_bank_id="state-repair-train-bank",
        evaluation_episode_length=EPISODE_LENGTH,
        full_campaign_episode_length=EPISODE_LENGTH,
    )


def build_legacy_campaign_config() -> CampaignConfig:
    return CampaignConfig(
        state_representation_profile=STATE_REPRESENTATION_PROFILE_LEGACY_MINIMAL,
        state_dim=state_dimension_for_profile(STATE_REPRESENTATION_PROFILE_LEGACY_MINIMAL),
        evaluation_trace_bank_id="state-repair-legacy-eval-bank",
        training_trace_bank_id="state-repair-legacy-train-bank",
        evaluation_episode_length=EPISODE_LENGTH,
        full_campaign_episode_length=EPISODE_LENGTH,
    )


@contextmanager
def patched_terminal_evaluator_state_profile(state_representation_profile: str) -> Iterator[None]:
    original_build_state_vector = terminal_evaluator.build_state_vector

    def build_state_vector_profiled(*, observation, current_task, episode_length):
        from src.analysis.full_training_reproduction_campaign.replay import build_state_vector

        return build_state_vector(
            observation=observation,
            current_task=current_task,
            episode_length=episode_length,
            state_representation_profile=state_representation_profile,
        )

    terminal_evaluator.build_state_vector = build_state_vector_profiled
    try:
        yield
    finally:
        terminal_evaluator.build_state_vector = original_build_state_vector


def state_representation_profile_metadata(state_representation_profile: str) -> dict[str, object]:
    return {
        "state_representation_profile": state_representation_profile,
        "state_dim": state_dimension_for_profile(state_representation_profile),
        "legacy_profile_preserved": state_representation_profile != STATE_REPRESENTATION_PROFILE_LEGACY_MINIMAL,
    }
