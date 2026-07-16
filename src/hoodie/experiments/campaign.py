from __future__ import annotations

from pathlib import Path
from typing import Any

from .production_campaign import campaign_status as _campaign_status
from .production_campaign import resume_production_campaign as _resume_production_campaign
from .production_campaign import run_production_campaign as _run_production_campaign


def run_smoke_campaign(*, campaign_id: str, output_dir: Path, smoke: bool = True) -> dict[str, Any]:
    del smoke
    return {"campaign_id": campaign_id, "output_dir": str(output_dir), "status": "smoke-runner-retained"}


def run_production_campaign(*, campaign_id: str, output_dir: Path, max_jobs: int | None = None, max_runtime_seconds: float | None = None, job_id: str | None = None, allow_paused_recovery: bool = False) -> dict[str, Any]:
    return _run_production_campaign(campaign_id=campaign_id, output_dir=output_dir, max_jobs=max_jobs, max_runtime_seconds=max_runtime_seconds, job_id=job_id, allow_paused_recovery=allow_paused_recovery)


def campaign_status(campaign_id: str, output_dir: Path | None = None) -> dict[str, Any]:
    return _campaign_status(campaign_id, output_dir)


def resume_production_campaign(campaign_id: str, output_dir: Path | None = None, *, max_jobs: int | None = None, max_runtime_seconds: float | None = None, job_id: str | None = None, allow_paused_recovery: bool = False) -> dict[str, Any]:
    return _resume_production_campaign(campaign_id, output_dir, max_jobs=max_jobs, max_runtime_seconds=max_runtime_seconds, job_id=job_id, allow_paused_recovery=allow_paused_recovery)
