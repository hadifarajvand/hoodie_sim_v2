from __future__ import annotations

from pathlib import Path

import pytest
import torch
from torch import nn

from src.hoodie.experiments.production_campaign import _probe_policy_q_value
from src.hoodie.experiments.supervisor import supervise_campaign


class _CheckingNetwork(nn.Module):
    def __init__(self, device: torch.device) -> None:
        super().__init__()
        self.device = device

    def forward(self, state: torch.Tensor) -> torch.Tensor:  # type: ignore[override]
        assert state.device.type == self.device.type
        return torch.ones(3, device=self.device)


class _FakeLearner:
    def __init__(self, device: torch.device) -> None:
        self.device = device
        self.input_dim = 4
        self.online_network = _CheckingNetwork(device)


class _FakePolicy:
    def __init__(self, device: torch.device) -> None:
        self.learner = type('Wrapped', (), {'learner': _FakeLearner(device)})()


@pytest.mark.parametrize(
    'device_name',
    [
        'cpu',
        pytest.param('mps', marks=pytest.mark.skipif(not (getattr(torch.backends, 'mps', None) is not None and torch.backends.mps.is_available()), reason='mps unavailable')),
        pytest.param('cuda', marks=pytest.mark.skipif(not torch.cuda.is_available(), reason='cuda unavailable')),
    ],
)
def test_q_value_probe_uses_learner_device(device_name: str) -> None:
    device = torch.device(device_name)
    assert _probe_policy_q_value(_FakePolicy(device)) == pytest.approx(1.0)


def test_supervisor_rejects_duplicate_lock(tmp_path: Path) -> None:
    campaign_id = 'figures-8-11-7587c7c6382c'
    campaign_root = tmp_path / 'artifacts' / 'hoodie' / 'campaigns'
    supervisor_dir = campaign_root / campaign_id / 'supervisor'
    supervisor_dir.mkdir(parents=True, exist_ok=True)
    proc = subprocess.Popen([sys.executable, '-c', _lock_script(str(supervisor_dir))], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert proc.stdout is not None
    assert proc.stdout.readline().strip() == 'acquired'
    with pytest.raises(FileExistsError):
        supervise_campaign(campaign_id, campaign_root, max_runtime_seconds=0.0)
    proc.wait(timeout=10)
    assert proc.stdout.readline().strip() == 'released'


def test_supervisor_reclaims_stale_lock(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    campaign_id = 'figures-8-11-7587c7c6382c'
    campaign_root = tmp_path / 'artifacts' / 'hoodie' / 'campaigns'
    supervisor_dir = campaign_root / campaign_id / 'supervisor'
    supervisor_dir.mkdir(parents=True, exist_ok=True)
    (supervisor_dir / 'lock').write_text('{"pid": 999999, "worker_identity": "ghost", "started_at": 0}', encoding='utf-8')
    monkeypatch.setattr('src.hoodie.experiments.supervisor.campaign_status', lambda *args, **kwargs: {'completed_jobs': 0, 'failed_jobs': 0, 'pending_jobs': 0, 'blocked_dependency_jobs': 0, 'running_jobs': 0, 'stale_jobs': 0, 'corrupt_jobs': 0, 'quarantined_jobs': 0, 'total': 284})
    monkeypatch.setattr('src.hoodie.experiments.supervisor.resume_production_campaign', lambda *args, **kwargs: {'completed_jobs': 0})
    result = supervise_campaign(campaign_id, campaign_root, max_runtime_seconds=0.0)
    assert result['terminal_state'] == 'interrupted_resumable'


import json
import subprocess
import sys
import time
from dataclasses import asdict

from src.hoodie.experiments import production_campaign as pc
from src.hoodie.experiments.job_matrix import build_production_job_matrix
from src.hoodie.experiments.supervisor import _acquire_lock, _release_lock


class _TinyTask:
    def __init__(self, task_id: int) -> None:
        self.task_id = task_id
        self.source_agent_id = f'a{task_id}'
        self.size = 1.0
        self.processing_density = 1.0
        self.timeout_length = 1
        self.absolute_deadline_slot = 1


class _TinyTrace:
    def __init__(self) -> None:
        self.trace_id = 'tiny-trace'
        self.seed = 7
        self.tasks = [_TinyTask(1)]


class _TinyRegistry:
    def hash(self) -> str:
        return 'trace-hash'


def _lock_script(path: str) -> str:
    return (
        "from pathlib import Path; import time; "
        "from src.hoodie.experiments.supervisor import _acquire_lock, _release_lock; "
        f"root = Path({path!r}); _acquire_lock(root); print('acquired', flush=True); "
        "time.sleep(2); _release_lock(root); print('released', flush=True)"
    )


class _TinyEnv:
    def __init__(self, *args, **kwargs) -> None:
        self.current_slot = 0
        self._steps = 0
        self.supplied_trace = kwargs.get('supplied_trace')

    def reset(self, seed: int) -> None:
        self.current_slot = 0
        self._steps = 0

    def step_slot(self, policy):
        self._steps += 1
        self.current_slot = self._steps
        done = self._steps >= 2
        info = {
            'decision_events': [{'task_id': 1, 'action': 'local', 'legal_action_mask': {'local': True, 'horizontal': False, 'vertical': False}}],
            'finalized_tasks': [{'task_id': 1, 'source_agent_id': 'a1', 'arrival_slot': 0, 'decision_slot': 0, 'selected_action': 'local', 'resolved_destination': 'local', 'completion_slot': self._steps, 'terminal_outcome': 'completed', 'queue_delay_slots': 0, 'transmission_delay_slots': 0, 'service_delay_slots': 0, 'delay': 0.0, 'reward': 1.0}],
            'reward_delivery_events': [{'task_id': 1, 'reward': 1.0, 'selected_action': 'local', 'resolution_slot': self._steps}],
        }
        return {'slot': self._steps}, 1.0, done, False, info


def _lock_worker(path: str, queue) -> None:
    root = Path(path)
    _acquire_lock(root)
    queue.put('acquired')
    time.sleep(2)
    _release_lock(root)
    queue.put('released')


def test_training_writes_progress_and_checkpoint(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    campaign_root = tmp_path / 'artifacts' / 'hoodie' / 'campaigns'
    job_dir = campaign_root / 'figures-8-11-test' / 'jobs' / 'figure_8a-1-HOODIE-None'
    job_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(pc, '_build_trace', lambda row: (_TinyRegistry(), {'trace': _TinyTrace(), 'trace_hash': 'trace-hash'}))
    monkeypatch.setattr(pc, '_training_config', lambda row, trace_hash, output_dir: type('Cfg', (), {'episode_count': 2, 'episode_length': 2, 'drain_slots': 0, 'learning_rate': 1e-3})())
    monkeypatch.setattr(pc, 'EvaluationHoodieGymEnvironment', _TinyEnv)
    base_row = build_production_job_matrix('figures-8-11-test')[0]
    row = pc.ProductionJobRow(**{**asdict(base_row), 'campaign_id': 'figures-8-11-test', 'job_id': 'figure_8a-1-HOODIE-None'})
    result = pc._run_training_job(row, job_dir, source_commit='deadbeef')
    assert result.status == 'scientifically_incomplete'
    assert (job_dir / 'progress.json').exists()
    progress = json.loads((job_dir / 'progress.json').read_text(encoding='utf-8'))
    assert progress['current_episode'] >= 0
    assert (job_dir / 'internal_checkpoints' / 'latest.json').exists()
    assert (job_dir / 'training_history.csv').exists()


def test_supervisor_lock_rejects_second_process(tmp_path: Path) -> None:
    supervisor_dir = tmp_path / 'supervisor'
    proc = subprocess.Popen([sys.executable, '-c', _lock_script(str(supervisor_dir))], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert proc.stdout is not None
    assert proc.stdout.readline().strip() == 'acquired'
    with pytest.raises(FileExistsError):
        _acquire_lock(supervisor_dir)
    proc.wait(timeout=10)
    assert proc.stdout.readline().strip() == 'released'
    assert proc.returncode == 0


def test_training_config_uses_source_contracted_episode_count() -> None:
    base_row = build_production_job_matrix('figures-8-11-test')[0]
    config = pc._training_config(pc.ProductionJobRow(**asdict(base_row)), trace_hash='trace-hash', output_dir=Path('/tmp'))
    assert config.episode_count == 5000


def test_scientific_completion_rejects_underfilled_history(tmp_path: Path) -> None:
    campaign_root = tmp_path / 'artifacts' / 'hoodie' / 'campaigns'
    job_dir = campaign_root / 'figures-8-11-test' / 'jobs' / 'figure_8a-1-HOODIE-None'
    job_dir.mkdir(parents=True, exist_ok=True)
    (job_dir / 'training_history.csv').write_text('episode_or_step,loss,epsilon,replay_size,target_update_count,checkpoint_id\n0,1.0,0.1,1,1,abc\n1,1.0,0.1,1,1,abc\n', encoding='utf-8')
    (job_dir / 'internal_checkpoints').mkdir(parents=True, exist_ok=True)
    (job_dir / 'internal_checkpoints' / 'latest.json').write_text(json.dumps({'checkpoint_id': 'abc', 'checkpoint_path': str(job_dir / 'internal_checkpoints' / 'abc' / 'checkpoint.pt')}), encoding='utf-8')
    (job_dir / 'checkpoint_selection.json').write_text(json.dumps({'checkpoint_id': 'abc'}), encoding='utf-8')
    (job_dir / 'completion.marker').write_text('complete\n', encoding='utf-8')
    base_row = build_production_job_matrix('figures-8-11-test')[0]
    row = pc.ProductionJobRow(**asdict(base_row))
    assert pc._job_scientifically_complete(job_dir, row) is False


def test_figure_8a_episode_count_comes_from_source_contract_not_x_value() -> None:
    row = next(row for row in build_production_job_matrix('figures-8-11-test') if row.job_id == 'figure_8a-1-HOODIE-None')
    config = pc._training_config(pc.ProductionJobRow(**asdict(row)), trace_hash='trace-hash', output_dir=Path('/tmp'))
    assert config.episode_count == 5000
    assert config.episode_count != 500


def test_figure_11_episode_count_locked_by_source_contract() -> None:
    row = next(row for row in build_production_job_matrix('figures-8-11-test') if row.panel_id == 'figure_11')
    config = pc._training_config(pc.ProductionJobRow(**asdict(row)), trace_hash='trace-hash', output_dir=Path('/tmp'))
    assert config.episode_count == 3000


def test_underfilled_history_cannot_complete_5000_episode_job(tmp_path: Path) -> None:
    campaign_root = tmp_path / 'artifacts' / 'hoodie' / 'campaigns'
    job_dir = campaign_root / 'figures-8-11-test' / 'jobs' / 'figure_8a-1-HOODIE-None'
    job_dir.mkdir(parents=True, exist_ok=True)
    (job_dir / 'training_history.csv').write_text('episode_or_step,loss,epsilon,replay_size,target_update_count,checkpoint_id\n0,1.0,0.1,1,1,abc\n1,1.0,0.1,1,1,abc\n', encoding='utf-8')
    (job_dir / 'internal_checkpoints').mkdir(parents=True, exist_ok=True)
    (job_dir / 'internal_checkpoints' / 'latest.json').write_text(json.dumps({'checkpoint_id': 'abc', 'checkpoint_path': str(job_dir / 'internal_checkpoints' / 'abc' / 'checkpoint.pt')}), encoding='utf-8')
    (job_dir / 'checkpoint_selection.json').write_text(json.dumps({'checkpoint_id': 'abc'}), encoding='utf-8')
    (job_dir / 'completion.marker.invalid').write_text('invalid\n', encoding='utf-8')
    row = pc.ProductionJobRow(**asdict(next(row for row in build_production_job_matrix('figures-8-11-test') if row.job_id == 'figure_8a-1-HOODIE-None')))
    assert pc._job_scientifically_complete(job_dir, row) is False


def test_training_resume_preserves_episodes_zero_through_120(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    campaign_root = tmp_path / 'artifacts' / 'hoodie' / 'campaigns'
    job_dir = campaign_root / 'figures-8-11-test' / 'jobs' / 'figure_8a-1-HOODIE-None'
    job_dir.mkdir(parents=True, exist_ok=True)
    (job_dir / 'training_history.csv').write_text('episode_or_step,loss,epsilon,replay_size,target_update_count,checkpoint_id\n' + '\n'.join(f'{episode},1.0,0.1,1,1,abc' for episode in range(121)) + '\n', encoding='utf-8')
    (job_dir / 'status.json').write_text(json.dumps({'attempt': 2}), encoding='utf-8')
    (job_dir / 'internal_checkpoints').mkdir(parents=True, exist_ok=True)
    checkpoint = job_dir / 'internal_checkpoints' / 'abc' / 'checkpoint.pt'
    checkpoint.parent.mkdir(parents=True, exist_ok=True)
    torch.save({'policy_state': {}, 'next_episode': 121, 'episode_rewards': [], 'transition_rows': [], 'decision_rows': [], 'task_rows': []}, checkpoint)
    (job_dir / 'internal_checkpoints' / 'latest.json').write_text(json.dumps({'checkpoint_id': 'abc', 'checkpoint_path': str(checkpoint)}), encoding='utf-8')
    row = pc.ProductionJobRow(**asdict(next(row for row in build_production_job_matrix('figures-8-11-test') if row.job_id == 'figure_8a-1-HOODIE-None')))
    monkeypatch.setattr(pc, '_build_trace', lambda row: (_TinyRegistry(), {'trace': _TinyTrace(), 'trace_hash': 'trace-hash'}))
    monkeypatch.setattr(pc, 'EvaluationHoodieGymEnvironment', _TinyEnv)
    monkeypatch.setattr(pc, 'build_deterministic_trace', lambda **kwargs: _TinyTrace())
    monkeypatch.setattr(pc, '_training_config', lambda row, trace_hash, output_dir: type('Cfg', (), {'episode_count': 5000, 'episode_length': 2, 'drain_slots': 0, 'learning_rate': 1e-3})())
    result = pc._run_training_job(row, job_dir, source_commit='deadbeef', max_runtime_seconds=0.0)
    assert result.status == 'interrupted_resumable'
    history = [line for line in (job_dir / 'training_history.csv').read_text().splitlines() if line and not line.startswith('episode_or_step')]
    assert len(history) >= 121
    assert history[0].startswith('0,')
    assert history[-1].split(',')[0] == '120'
