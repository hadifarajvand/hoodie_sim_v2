from __future__ import annotations

from pathlib import Path
from typing import Any

from .production_campaign import _run_evaluation_job, _run_training_job, ProductionJobRow


def execute_job(row: ProductionJobRow, job_dir: Path, *, source_commit: str, checkpoint_state: dict[str, Any] | None = None):
    return _run_training_job(row, job_dir, source_commit=source_commit) if row.job_type == "training" else _run_evaluation_job(row, job_dir, source_commit=source_commit, checkpoint_state=checkpoint_state)
