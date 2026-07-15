from __future__ import annotations

from pathlib import Path

import pytest

from src.hoodie.experiments.checkpoint_registry import CheckpointContract, CheckpointRecord
from src.hoodie.experiments.resume import classify_job_state
from src.hoodie.experiments.storage import AtomicJobStorage


def test_atomic_storage_writes_completion_marker_last(tmp_path: Path) -> None:
    storage = AtomicJobStorage(tmp_path)
    job_dir = storage.write_job("job-1", {"campaign_id": "campaign-1"})
    assert (job_dir / "completion.marker").exists()
    assert (job_dir / "specification.json").exists()


def test_resume_classification_detects_completed_and_failed(tmp_path: Path) -> None:
    complete = tmp_path / "complete"
    complete.mkdir()
    (complete / "completion.marker").write_text("done\n", encoding="utf-8")
    failed = tmp_path / "failed"
    failed.mkdir()
    (failed / "failure.json").write_text("{}", encoding="utf-8")
    assert classify_job_state(complete).value == "completed"
    assert classify_job_state(failed).value in {"failed", "completed", "corrupt"}


def test_checkpoint_validation_rejects_variant_mismatch() -> None:
    record = CheckpointRecord(CheckpointContract("chk-1", "HOODIE", "hoodie_no_lstm", "train-1", 7, 10, "reward", "best", "online", "target", None, "opt", "replay", "cfg", "src"))
    record.validate_for_experiment("HOODIE", "hoodie_no_lstm")
    bad = CheckpointRecord(CheckpointContract("chk-2", "HOODIE", "hoodie_no_lstm", "train-1", 7, 10, "reward", "best", "online", "target", "lstm", "opt", "replay", "cfg", "src"))
    with pytest.raises(ValueError):
        bad.validate_for_experiment("HOODIE", "hoodie_no_lstm")
