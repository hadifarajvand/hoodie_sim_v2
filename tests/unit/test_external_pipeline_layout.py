from hashlib import sha256
import json
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


def test_bundle_seal_keeps_json_and_shell_inventories_consistent(
    tmp_path: Path, monkeypatch
) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    payload = bundle / "payload.txt"
    payload.write_text("payload\n", encoding="utf-8")
    payload_hash = sha256(payload.read_bytes()).hexdigest()
    (bundle / "checksums.json").write_text(
        json.dumps({"payload.txt": payload_hash}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    def verify_inventory(root: Path):
        expected = json.loads((root / "checksums.json").read_text(encoding="utf-8"))
        actual = {
            str(path.relative_to(root)): sha256(path.read_bytes()).hexdigest()
            for path in root.rglob("*")
            if path.is_file() and path.name != "checksums.json"
        }
        assert actual == expected
        return {"verified": True}

    monkeypatch.setattr(
        external_pipeline.scientific_pipeline,
        "verify_bundle",
        verify_inventory,
    )
    checksum_path = external_pipeline._seal_bundle(bundle)
    assert checksum_path == bundle / "SHA256SUMS"
    assert "checksums.json" not in checksum_path.read_text(encoding="utf-8")
    assert "payload.txt" in checksum_path.read_text(encoding="utf-8")
