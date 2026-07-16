from __future__ import annotations

from pathlib import Path
from typing import Any

from .job_executor import execute_job
from .job_matrix import ProductionJobRow


def run_evaluation_job(row: ProductionJobRow, job_dir: Path, *, source_commit: str, checkpoint_state: dict[str, Any] | None = None):
    if row.job_type != "evaluation":
        raise ValueError("job is not evaluation")
    return execute_job(row, job_dir, source_commit=source_commit, checkpoint_state=checkpoint_state)
