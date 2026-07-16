from __future__ import annotations

from pathlib import Path

from .resume import classify_job_state


def recover_job(job_dir: Path) -> str:
    return classify_job_state(job_dir).value
