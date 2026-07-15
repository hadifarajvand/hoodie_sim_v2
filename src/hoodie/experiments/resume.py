from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True, slots=True)
class JobState:
    value: str


def classify_job_state(job_dir: Path) -> JobState:
    if (job_dir / "completion.marker").exists():
        return JobState("completed")
    if any(child.suffix == ".tmp" for child in job_dir.iterdir() if child.exists()):
        return JobState("corrupt")
    if any(job_dir.iterdir()):
        return JobState("failed")
    return JobState("pending")
