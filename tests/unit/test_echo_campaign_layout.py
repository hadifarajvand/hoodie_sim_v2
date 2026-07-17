from __future__ import annotations

from pathlib import Path

import pytest

from src.hoodie.experiments.campaign_layout import (
    CampaignLocationError,
    CampaignNotFoundError,
    atomic_write_json,
    resolve_campaign_layout,
)


def test_external_campaign_layout_round_trip(tmp_path: Path) -> None:
    repository = tmp_path / "repo"
    repository.mkdir()
    external = tmp_path / "external"
    campaign = external / "campaigns" / "demo"
    campaign.mkdir(parents=True)

    layout = resolve_campaign_layout(
        campaign_dir=campaign,
        repository=repository,
    )
    assert layout.campaign_root == campaign.resolve()
    assert layout.aggregate_dir == campaign.resolve() / "aggregates"
    assert layout.bundles_dir == campaign.resolve().parent / "releases"

    atomic_write_json(
        layout.manifest_path,
        {
            "campaign_id": "demo",
            "campaign_root": str(campaign.resolve()),
        },
    )
    restored = resolve_campaign_layout(
        manifest_path=layout.manifest_path,
        repository=repository,
    )
    assert restored.campaign_root == layout.campaign_root
    assert restored.manifest_path == layout.manifest_path


def test_repository_local_campaign_is_rejected(tmp_path: Path) -> None:
    repository = tmp_path / "repo"
    campaign = repository / "artifacts" / "hoodie" / "campaigns" / "demo"
    campaign.mkdir(parents=True)

    with pytest.raises(CampaignLocationError, match="outside the repository"):
        resolve_campaign_layout(
            campaign_dir=campaign,
            repository=repository,
        )


def test_missing_explicit_campaign_is_not_storage_blocker(tmp_path: Path) -> None:
    repository = tmp_path / "repo"
    repository.mkdir()
    missing = tmp_path / "external" / "campaigns" / "missing"

    with pytest.raises(CampaignNotFoundError) as captured:
        resolve_campaign_layout(
            campaign_dir=missing,
            repository=repository,
        )
    assert captured.value.error_type == "campaign_not_found"


def test_protected_legacy_campaign_is_rejected(tmp_path: Path) -> None:
    repository = tmp_path / "repo"
    repository.mkdir()
    protected = tmp_path / "external" / "campaigns" / "figures-8-11-7587c7c6382c"
    protected.mkdir(parents=True)

    with pytest.raises(CampaignLocationError, match="protected legacy"):
        resolve_campaign_layout(
            campaign_dir=protected,
            repository=repository,
        )


def test_location_arguments_must_be_absolute(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    with pytest.raises(CampaignLocationError, match="absolute"):
        resolve_campaign_layout(
            campaign_dir=Path("relative-campaign"),
            repository=tmp_path / "repo",
            require_existing=False,
        )
