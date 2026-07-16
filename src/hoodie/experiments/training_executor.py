from __future__ import annotations

from pathlib import Path
from typing import Any

from .job_executor import execute_job
from .job_matrix import ProductionJobRow


def run_training_job(row: ProductionJobRow, job_dir: Path, *, source_commit: str):
    if row.job_type != "training":
        raise ValueError("job is not training")
    return execute_job(row, job_dir, source_commit=source_commit)
