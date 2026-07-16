from __future__ import annotations

import json
from pathlib import Path

from src.hoodie.experiments.production_campaign import campaign_status, resume_production_campaign


def _write_job(job_root: Path, job_id: str, *, status: str) -> None:
    job_dir = job_root / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    (job_dir / 'status.json').write_text(json.dumps({'status': status}), encoding='utf-8')
    if status == 'completed':
        (job_dir / 'completion.marker').write_text('complete\n', encoding='utf-8')


def test_campaign_status_accounts_for_full_matrix(tmp_path: Path) -> None:
    campaign_id = 'figures-8-11-test'
    job_root = tmp_path / 'artifacts' / 'hoodie' / 'campaigns' / campaign_id / 'jobs'
    _write_job(job_root, 'figure_8a-0-HOODIE-None', status='completed')
    _write_job(job_root, 'figure_8a-1-HOODIE-None', status='failed')
    status = campaign_status(campaign_id, tmp_path / 'artifacts' / 'hoodie' / 'campaigns')
    assert status['total'] == 284
    assert status['completed_jobs'] == 1
    assert status['failed_jobs'] == 1
    assert status['pending_jobs'] + status['blocked_dependency_jobs'] == 282
    assert sum(status[key] for key in ('pending_jobs', 'running_jobs', 'completed_jobs', 'failed_jobs', 'stale_jobs', 'corrupt_jobs', 'quarantined_jobs', 'blocked_dependency_jobs')) == 284


def test_resume_uses_frozen_matrix_not_existing_dirs(monkeypatch: object, tmp_path: Path) -> None:
    seen: list[str] = []

    def fake_run(*, campaign_id: str, output_dir: Path | None = None, max_jobs: int | None = None, max_runtime_seconds: float | None = None, job_id: str | None = None, allow_paused_recovery: bool = False):
        seen.append(campaign_id)
        return {'campaign_id': campaign_id, 'total_jobs': 284, 'completed_jobs': 0}

    monkeypatch.setattr('src.hoodie.experiments.production_campaign.run_production_campaign', fake_run)
    result = resume_production_campaign('figures-8-11-test', tmp_path / 'artifacts' / 'hoodie' / 'campaigns')
    assert result['campaign_id'] == 'figures-8-11-test'
    assert seen == ['figures-8-11-test']
