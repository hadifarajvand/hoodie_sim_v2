from __future__ import annotations

from pathlib import Path


def test_supported_suite_covers_required_subsystems() -> None:
    root = Path(__file__).resolve().parents[1]
    files = {path.name for path in root.rglob('test_*.py')}
    required = {
        'kernel': any('kernel' in name for name in files),
        'learner': any('hoodie_learning_real' in name or 'ddqn' in name or 'lstm_dueling_dqn' in name for name in files),
        'lstm': any('lstm' in name for name in files),
        'checkpoint': any('checkpoint' in name for name in files),
        'reward': any('reward' in name or 'delayed_reward' in name for name in files),
        'distributed': any('distributed' in name for name in files),
        'baselines': any('baseline' in name for name in files),
        'paired_evaluation': any('paired' in name for name in files),
        'campaign': any('campaign' in name for name in files),
        'reproducibility': any('reproducibility' in name for name in files),
    }
    missing = [group for group, present in required.items() if not present]
    assert not missing, f"missing supported subsystems: {missing}"
