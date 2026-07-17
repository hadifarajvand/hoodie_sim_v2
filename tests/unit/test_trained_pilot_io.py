from __future__ import annotations

from pathlib import Path

import pytest

from src.hoodie.experiments.trained_pilot import PilotConfig
from src.hoodie.experiments.trained_pilot_io import (
    PROTECTED_CAMPAIGN_ID,
    repository_root,
    resolve_campaign_root,
)


def test_trained_pilot_defaults_are_bounded_but_physical_scale() -> None:
    config = PilotConfig()
    assert config.agent_count == 20
    assert config.training_episodes == 12
    assert config.evaluation_episodes == 20
    assert config.episode_slots == 110
    assert config.drain_slots == 10


def test_campaign_root_must_be_absolute_and_external(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="absolute"):
        resolve_campaign_root("relative-output", "pilot")
    with pytest.raises(ValueError, match="outside"):
        resolve_campaign_root(repository_root() / "generated", "pilot")
    assert resolve_campaign_root(tmp_path.resolve(), "pilot") == (
        tmp_path.resolve() / "campaigns" / "pilot"
    )


def test_protected_legacy_campaign_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="protected"):
        resolve_campaign_root(tmp_path.resolve(), PROTECTED_CAMPAIGN_ID)
