from pathlib import Path

from src.hoodie.experiments import external_pipeline
from src.hoodie.experiments.campaign_layout import resolve_campaign_layout


def test_aggregate_uses_the_resolved_external_root(
    tmp_path: Path, monkeypatch
) -> None:
    repository = tmp_path / "repo"
    repository.mkdir()
    campaign = tmp_path / "external" / "campaigns" / "demo"
    campaign.mkdir(parents=True)
    layout = resolve_campaign_layout(
        campaign_dir=campaign,
        repository=repository,
    )

    def fake_aggregate(campaign_id: str):
        return {
            "campaign_id": campaign_id,
            "bound_root": str(external_pipeline.scientific_pipeline.CAMPAIGN_ROOT),
        }

    monkeypatch.setattr(
        external_pipeline.scientific_pipeline,
        "aggregate_campaign",
        fake_aggregate,
    )
    result = external_pipeline.aggregate_campaign(layout)
    assert result["campaign_root"] == str(campaign.resolve())
    assert result["bound_root"] == str(campaign.resolve().parent)
    assert layout.manifest_path.exists()
