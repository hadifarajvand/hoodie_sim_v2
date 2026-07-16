from __future__ import annotations

from dataclasses import dataclass
import json
import csv
from pathlib import Path

from .source_contracts import SOURCE_CONTRACT_PATH

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
    if str(status_payload.get("job_type", "")).strip().lower() != "training":
        return True
    panel_id = str(status_payload.get("panel_id", "")).strip()
    if not panel_id:
        return False
    try:
        payload = json.loads(SOURCE_CONTRACT_PATH.read_text(encoding="utf-8"))
    except Exception:
        return False
    panel = next((item for item in payload.get("panels", []) if item.get("panel_id") == panel_id), None)
    if panel is None:
        return False
    required_training_episodes = int(panel.get("training_episodes", 0) or 0)
    history_path = job_dir / "training_history.csv"
    if not history_path.exists():
        return False
    with history_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        return False
    episodes = sorted({int(row.get("episode_or_step", -1)) for row in rows})
    if len(episodes) != required_training_episodes:
        return False
    return episodes[0] == 0 and episodes[-1] == required_training_episodes - 1
