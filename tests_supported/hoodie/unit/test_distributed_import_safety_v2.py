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
    status: str = "completed",
    job_status: str | None = None,
) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    payload: dict[str, object] = {
        "campaign_id": campaign_id,
        "shard_id": shard_id,
        "status": status,
    }
    if job_status is not None:
        payload["job_ids"] = ["job-1"]
        payload["job_results"] = [
            {"job_id": "job-1", "status": job_status}
        ]
    (root / "result_bundle.json").write_text(
        json.dumps(payload) + "\n", encoding="utf-8"
    )
    return root


def test_incomplete_single_shard_is_rejected_before_delegate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    result_root = _write_bundle(
        tmp_path / "partial", status="interrupted_resumable"
    )
    delegated = False

    def forbidden_delegate(_campaign_id: str, _result_root: Path):
        nonlocal delegated
        delegated = True
        raise AssertionError("partial result reached canonical importer")

    monkeypatch.setattr(
        patch, "_ORIGINAL_IMPORT_SHARD_RESULTS", forbidden_delegate
    )
    with pytest.raises(
        RuntimeError, match="refusing to import a non-completed shard"
    ):
        distributed_v2.import_shard_results("campaign-a", result_root)
    assert delegated is False


def test_completed_bundle_with_incomplete_job_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    result_root = _write_bundle(
        tmp_path / "false-complete",
        status="completed",
        job_status="interrupted_resumable",
    )
    delegated = False

    def forbidden_delegate(_campaign_id: str, _result_root: Path):
        nonlocal delegated
        delegated = True
        raise AssertionError("inconsistent result reached canonical importer")

    monkeypatch.setattr(
        patch, "_ORIGINAL_IMPORT_SHARD_RESULTS", forbidden_delegate
    )
    with pytest.raises(RuntimeError, match="claims completion"):
        distributed_v2.import_shard_results("campaign-a", result_root)
    assert delegated is False


def test_completed_single_shard_delegates_to_canonical_importer(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    result_root = _write_bundle(tmp_path / "complete")
    observed: list[tuple[str, Path]] = []

    def delegate(campaign_id: str, root: Path):
        observed.append((campaign_id, root))
        return {"campaign_id": campaign_id, "imported": True}

    monkeypatch.setattr(patch, "_ORIGINAL_IMPORT_SHARD_RESULTS", delegate)
    result = distributed_v2.import_shard_results("campaign-a", result_root)
    assert result["imported"] is True
    assert observed == [("campaign-a", result_root)]


def test_bulk_import_preflights_all_bundles_before_delegate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    results_dir = tmp_path / "results"
    _write_bundle(results_dir / "training-001", status="completed")
    _write_bundle(
        results_dir / "training-002",
        shard_id="training-002",
        status="interrupted_resumable",
    )
    delegated = False

    def forbidden_delegate(_campaign_id: str, _results_dir: Path):
        nonlocal delegated
        delegated = True
        raise AssertionError(
            "bulk import started before completion preflight finished"
        )

    monkeypatch.setattr(
        patch, "_ORIGINAL_IMPORT_RESULTS_DIRECTORY", forbidden_delegate
    )
    with pytest.raises(RuntimeError, match="refusing bulk import"):
        distributed_v2.import_results_directory("campaign-a", results_dir)
    assert delegated is False


def test_empty_bulk_import_is_rejected_before_delegate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    results_dir = tmp_path / "empty"
    results_dir.mkdir()
    delegated = False

    def forbidden_delegate(_campaign_id: str, _results_dir: Path):
        nonlocal delegated
        delegated = True
        raise AssertionError("empty import reached canonical importer")

    monkeypatch.setattr(
        patch, "_ORIGINAL_IMPORT_RESULTS_DIRECTORY", forbidden_delegate
    )
    with pytest.raises(FileNotFoundError, match="no result_bundle"):
        distributed_v2.import_results_directory("campaign-a", results_dir)
    assert delegated is False


def test_duplicate_shard_bundles_are_rejected_before_delegate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    results_dir = tmp_path / "duplicates"
    _write_bundle(results_dir / "copy-a", shard_id="training-001")
    _write_bundle(results_dir / "copy-b", shard_id="training-001")
    delegated = False

    def forbidden_delegate(_campaign_id: str, _results_dir: Path):
        nonlocal delegated
        delegated = True
        raise AssertionError("duplicate import reached canonical importer")

    monkeypatch.setattr(
        patch, "_ORIGINAL_IMPORT_RESULTS_DIRECTORY", forbidden_delegate
    )
    with pytest.raises(ValueError, match="duplicate result bundles"):
        distributed_v2.import_results_directory("campaign-a", results_dir)
    assert delegated is False
