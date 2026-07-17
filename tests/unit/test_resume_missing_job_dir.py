from pathlib import Path

from src.hoodie.experiments.resume import classify_job_state


def test_missing_job_directory_is_pending(tmp_path: Path) -> None:
    assert classify_job_state(tmp_path / "not-created").value == "pending"
