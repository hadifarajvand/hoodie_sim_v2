from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.hoodie.experiments import distributed_import_patch as patch
from src.hoodie.experiments import distributed_v2


def _write_bundle(
    root: Path,
    *,
    campaign_id: str = "campaign-a",
    shard_id: str = "training-001",
    job_id: str = "job-1",
    status: str = "completed",
    job_status: str = "completed",
) -> Path:
    job_dir = root / "job_outputs" / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    (job_dir / "status.json").write_text(
        json.dumps(
            {
                "campaign_id": campaign_id,
                "job_id": job_id,
                "status": job_status,
                "completion_marker": job_status == "completed",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    if job_status == "completed":
        (job_dir / "completion.marker").write_text("completed\n", encoding="utf-8")
    (job_dir / "scientific.csv").write_text("episode,value\n0,1\n", encoding="utf-8")

    payload: dict[str, object] = {
        "schema_version": 2,
        "campaign_id": campaign_id,
        "shard_id": shard_id,
        "phase": "training",
        "plan_hash": "plan",
        "source_commit": "commit",
        "source_contract_hash": "contract",
        "matrix_hash": "matrix",
        "job_ids": [job_id],
        "job_results": [{"job_id": job_id, "status": job_status}],
        "status": status,
    }
    payload["result_hash"] = distributed_v2._hash(payload)
    (root / "result_bundle.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (root / "checksums.json").write_text(
        json.dumps(
            distributed_v2._checksums(root, exclude=("checksums.json",)),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return root


def _campaign_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "campaigns"
    monkeypatch.setattr(distributed_v2, "CAMPAIGN_ROOT", root)
    return root


def test_incomplete_single_shard_is_rejected_before_campaign_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    campaign_root = _campaign_root(tmp_path, monkeypatch)
    result_root = _write_bundle(
        tmp_path / "partial", status="interrupted_resumable", job_status="interrupted_resumable"
    )
    with pytest.raises(
        RuntimeError, match="refusing to import a non-completed shard"
    ):
        distributed_v2.import_shard_results("campaign-a", result_root)
    assert not (campaign_root / "campaign-a").exists()


def test_completed_bundle_with_incomplete_job_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    campaign_root = _campaign_root(tmp_path, monkeypatch)
    result_root = _write_bundle(
        tmp_path / "false-complete",
        status="completed",
        job_status="interrupted_resumable",
    )
    with pytest.raises(RuntimeError, match="non-completed job"):
        distributed_v2.import_shard_results("campaign-a", result_root)
    assert not (campaign_root / "campaign-a").exists()


def test_completed_shard_promotes_real_files_and_is_idempotent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    campaign_root = _campaign_root(tmp_path, monkeypatch)
    result_root = _write_bundle(tmp_path / "complete")

    result = distributed_v2.import_shard_results("campaign-a", result_root)
    imported = campaign_root / "campaign-a" / "jobs" / "job-1"
    assert result["imported_jobs"] == 1
    assert result["idempotent"] is False
    assert (imported / "scientific.csv").read_text(encoding="utf-8") == "episode,value\n0,1\n"
    assert (imported / "completion.marker").is_file()
    assert (campaign_root / "campaign-a" / "shard_imports" / "training-001.json").is_file()

    second = distributed_v2.import_shard_results("campaign-a", result_root)
    assert second["idempotent"] is True
    assert second["imported_jobs"] == 0


def test_conflicting_existing_job_is_rejected_without_overwrite(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    campaign_root = _campaign_root(tmp_path, monkeypatch)
    result_root = _write_bundle(tmp_path / "complete")
    destination = campaign_root / "campaign-a" / "jobs" / "job-1"
    destination.mkdir(parents=True)
    (destination / "sentinel.txt").write_text("preserve", encoding="utf-8")

    with pytest.raises(ValueError, match="conflicting imported job output"):
        distributed_v2.import_shard_results("campaign-a", result_root)
    assert (destination / "sentinel.txt").read_text(encoding="utf-8") == "preserve"
    assert not (campaign_root / "campaign-a" / "shard_imports" / "training-001.json").exists()


def test_bulk_import_preflights_all_bundles_before_campaign_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    campaign_root = _campaign_root(tmp_path, monkeypatch)
    results_dir = tmp_path / "results"
    _write_bundle(results_dir / "training-001")
    _write_bundle(
        results_dir / "training-002",
        shard_id="training-002",
        job_id="job-2",
        status="interrupted_resumable",
        job_status="interrupted_resumable",
    )
    with pytest.raises(RuntimeError, match="non-completed shard"):
        distributed_v2.import_results_directory("campaign-a", results_dir)
    assert not (campaign_root / "campaign-a").exists()


def test_empty_bulk_import_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _campaign_root(tmp_path, monkeypatch)
    results_dir = tmp_path / "empty"
    results_dir.mkdir()
    with pytest.raises(FileNotFoundError, match="no result_bundle"):
        distributed_v2.import_results_directory("campaign-a", results_dir)


def test_duplicate_shard_bundles_are_rejected_before_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    campaign_root = _campaign_root(tmp_path, monkeypatch)
    results_dir = tmp_path / "duplicates"
    _write_bundle(results_dir / "copy-a", shard_id="training-001", job_id="job-1")
    _write_bundle(results_dir / "copy-b", shard_id="training-001", job_id="job-2")
    with pytest.raises(ValueError, match="duplicate result bundles"):
        distributed_v2.import_results_directory("campaign-a", results_dir)
    assert not (campaign_root / "campaign-a").exists()


def test_bulk_failure_rolls_back_jobs_receipts_and_registry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    campaign_root = _campaign_root(tmp_path, monkeypatch)
    results_dir = tmp_path / "results"
    _write_bundle(results_dir / "training-001", shard_id="training-001", job_id="job-1")
    _write_bundle(results_dir / "training-002", shard_id="training-002", job_id="job-2")

    original = patch._import_one_locked
    calls = 0

    def fail_second(campaign_id: str, root: Path, payload: dict[str, object]):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise RuntimeError("synthetic second import failure")
        return original(campaign_id, root, payload)

    monkeypatch.setattr(patch, "_import_one_locked", fail_second)
    with pytest.raises(RuntimeError, match="synthetic second import failure"):
        distributed_v2.import_results_directory("campaign-a", results_dir)

    campaign = campaign_root / "campaign-a"
    assert not list((campaign / "jobs").glob("*")) if (campaign / "jobs").exists() else True
    assert not list((campaign / "shard_imports").glob("*.json")) if (campaign / "shard_imports").exists() else True
    assert not (campaign / "checkpoint_registry.json").exists()
