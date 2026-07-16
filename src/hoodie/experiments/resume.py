from __future__ import annotations

from dataclasses import dataclass
import json
import csv
from pathlib import Path

@dataclass(frozen=True, slots=True)
class JobState:
    value: str


def classify_job_state(job_dir: Path) -> JobState:
    status_path = job_dir / "status.json"
    if status_path.exists():
        try:
            payload = json.loads(status_path.read_text(encoding="utf-8"))
            status = str(payload.get("status", "")).strip().lower()
            if status in {"pending", "running", "completed", "failed", "stale", "corrupt", "quarantined", "blocked_dependency", "interrupted_resumable", "stalled_restart_required", "scientifically_incomplete"}:
                if status == "completed" and not _completed_job_scientifically_complete(job_dir, payload):
                    return JobState("scientifically_incomplete")
                return JobState("pending" if status in {"interrupted_resumable", "stalled_restart_required"} else status)
        except Exception:
            return JobState("corrupt")
    if (job_dir / "completion.marker").exists():
        return JobState("completed")
    if any(child.suffix == ".tmp" for child in job_dir.iterdir() if child.exists()):
        return JobState("corrupt")
    if any(job_dir.iterdir()):
        return JobState("failed")
    return JobState("pending")


def _completed_job_scientifically_complete(job_dir: Path, status_payload: dict[str, object]) -> bool:
    job_type = str(status_payload.get("job_type", "")).strip().lower()
    if job_type != "training":
        return True
    history_path = job_dir / "training_history.csv"
    if not history_path.exists() or not (job_dir / "completion.marker").exists():
        return False
    with history_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return bool(rows)
