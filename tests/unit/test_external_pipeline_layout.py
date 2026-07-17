from hashlib import sha256
import json
from pathlib import Path

import pytest

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
    inventory_path = bundle / "bundle_checksums.json"
    inventory_path.write_text(
        json.dumps({"payload.txt": payload_hash}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    def verify_inventory(root: Path):
        expected = json.loads(
            (root / "bundle_checksums.json").read_text(encoding="utf-8")
        )
        actual = {
            str(path.relative_to(root)): sha256(path.read_bytes()).hexdigest()
            for path in root.rglob("*")
            if path.is_file() and path.name != "bundle_checksums.json"
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
    checksum_text = checksum_path.read_text(encoding="utf-8")
    assert "bundle_checksums.json" not in checksum_text
    assert "payload.txt" in checksum_text


def test_seal_result_requires_canonical_external_release_path(
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
    wrong = tmp_path / "external" / "campaigns" / "releases" / "demo-bundle"
    wrong.mkdir(parents=True)

    with pytest.raises(RuntimeError, match="outside the resolved release"):
        external_pipeline._seal_result(
            layout,
            {"bundle_dir": str(wrong), "bundle_hash": "before"},
        )


def test_seal_result_returns_final_inventory_hash(
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
    bundle = layout.bundles_dir / "demo-bundle"
    bundle.mkdir(parents=True)
    payload = bundle / "payload.txt"
    payload.write_text("payload\n", encoding="utf-8")
    (bundle / "bundle_checksums.json").write_text(
        json.dumps(
            {"payload.txt": sha256(payload.read_bytes()).hexdigest()},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        external_pipeline.scientific_pipeline,
        "verify_bundle",
        lambda root: {"bundle": str(root), "verified": True},
    )
    result = external_pipeline._seal_result(
        layout,
        {"bundle_dir": str(bundle), "bundle_hash": "before"},
    )
    inventory = bundle / "bundle_checksums.json"
    assert result["preseal_bundle_hash"] == "before"
    assert result["bundle_hash"] == sha256(inventory.read_bytes()).hexdigest()
    assert result["sha256sums"] == str(bundle / "SHA256SUMS")


def test_verify_run_requires_a_sealed_bundle(tmp_path: Path, monkeypatch) -> None:
    repository = tmp_path / "repo"
    repository.mkdir()
    campaign = tmp_path / "external" / "campaigns" / "demo"
    campaign.mkdir(parents=True)
    layout = resolve_campaign_layout(
        campaign_dir=campaign,
        repository=repository,
    )

    monkeypatch.setattr(
        external_pipeline,
        "_complete_status",
        lambda current: {"total": 1, "completed_jobs": 1},
    )
    monkeypatch.setattr(
        external_pipeline.scientific_pipeline,
        "verify_campaign",
        lambda campaign_id: {"verified": True, "campaign_id": campaign_id},
    )

    with pytest.raises(FileNotFoundError, match="finalized bundle is missing"):
        external_pipeline.verify_run(layout)
