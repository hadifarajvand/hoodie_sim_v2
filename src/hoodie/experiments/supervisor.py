from __future__ import annotations

import json
import os
import fcntl
from dataclasses import asdict, dataclass
from pathlib import Path
import platform
import time
from typing import Any

from .campaign import campaign_status, resume_production_campaign
from .job_matrix import build_production_job_matrix

@dataclass(slots=True)
class SupervisorState:
    campaign_id: str
    pid: int
    worker_identity: str
    source_commit: str
    started_at: float
    updated_at: float
    last_status: dict[str, Any]
    loops: int = 0
    completed_jobs: int = 0
    failed_jobs: int = 0
    resumed_jobs: int = 0
    quarantined_attempts: int = 0


def _campaign_dir(root: Path, campaign_id: str) -> Path:
    return root / campaign_id


def _supervisor_dir(root: Path, campaign_id: str) -> Path:
    return _campaign_dir(root, campaign_id) / "supervisor"


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _lock_path(supervisor_dir: Path) -> Path:
    return supervisor_dir / "lock"


def _process_exists(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _acquire_lock(supervisor_dir: Path) -> None:
    supervisor_dir.mkdir(parents=True, exist_ok=True)
    lock = _lock_path(supervisor_dir)
    fd = os.open(lock, os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        try:
            payload = json.loads(lock.read_text(encoding="utf-8"))
            pid = int(payload.get("pid", 0))
        except Exception:
            pid = 0
        if _process_exists(pid):
            os.close(fd)
            raise FileExistsError(str(lock)) from exc
        fcntl.flock(fd, fcntl.LOCK_EX)
    os.ftruncate(fd, 0)
    os.write(fd, json.dumps({"pid": os.getpid(), "worker_identity": platform.node(), "started_at": time.time()}, sort_keys=True).encode("utf-8"))
    os.fsync(fd)
    _acquire_lock._fd = fd  # type: ignore[attr-defined]


def _release_lock(supervisor_dir: Path) -> None:
    lock = _lock_path(supervisor_dir)
    fd = getattr(_acquire_lock, "_fd", None)
    if fd is not None:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)
            delattr(_acquire_lock, "_fd")
    if lock.exists():
        lock.unlink()


def supervise_campaign(campaign_id: str, output_dir: Path, *, max_runtime_seconds: float | None = None) -> dict[str, Any]:
    root = output_dir
    supervisor_dir = _supervisor_dir(root, campaign_id)
    start = time.time()
    _acquire_lock(supervisor_dir)
    try:
        rows = build_production_job_matrix(campaign_id)
        state = SupervisorState(
            campaign_id=campaign_id,
            pid=os.getpid(),
            worker_identity=platform.node(),
            source_commit=os.popen("git rev-parse HEAD").read().strip(),
            started_at=start,
            updated_at=start,
            last_status=campaign_status(campaign_id, root),
        )
        _write_json(supervisor_dir / "supervisor_status.json", asdict(state))
        (supervisor_dir / "supervisor.log").write_text("supervisor started\n", encoding="utf-8")
        while True:
            current = campaign_status(campaign_id, root)
            state.last_status = current
            state.updated_at = time.time()
            _write_json(supervisor_dir / "heartbeat.json", {"campaign_id": campaign_id, "pid": os.getpid(), "updated_at": state.updated_at, "status": current})
            _write_json(supervisor_dir / "supervisor_status.json", asdict(state))
            if current.get("completed_jobs") == len(rows) and current.get("failed_jobs") == 0 and current.get("pending_jobs") == 0 and current.get("running_jobs") == 0 and current.get("stale_jobs") == 0 and current.get("corrupt_jobs") == 0 and current.get("blocked_dependency_jobs") == 0:
                _write_json(supervisor_dir / "completion_summary.json", {"campaign_id": campaign_id, "completed_jobs": current.get("completed_jobs", 0), "total_jobs": current.get("total", len(rows)), "finished_at": time.time()})
                return {"campaign_id": campaign_id, "terminal_state": "completed", "status": current, "supervisor_dir": str(supervisor_dir)}
            if max_runtime_seconds is not None and (time.time() - start) >= max_runtime_seconds:
                return {"campaign_id": campaign_id, "terminal_state": "interrupted_resumable", "status": current, "supervisor_dir": str(supervisor_dir)}
            result = resume_production_campaign(campaign_id, root)
            state.loops += 1
            state.resumed_jobs += int(result.get("completed_jobs", 0))
            state.updated_at = time.time()
            _write_json(supervisor_dir / "throughput.json", {"loops": state.loops, "resumed_jobs": state.resumed_jobs, "elapsed_seconds": state.updated_at - start})
            if result.get("completed_jobs", 0) == 0:
                time.sleep(2)
    finally:
        _release_lock(supervisor_dir)
