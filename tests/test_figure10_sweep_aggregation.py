import json
import tempfile
from pathlib import Path
import shutil
import os
import stat
import pytest
from scripts.aggregate_figure10_sweep_results import aggregate

BASE_POLICIES = ["RO","FLC","VO","HO","BCO","MLEO"]


def make_synthetic_sweep(root: Path, value: str):
    d = root / value
    d.mkdir(parents=True, exist_ok=True)
    # create per-regime summary structure
    summary = {}
    for regime in ["delay","drop_ratio"]:
        summary[regime] = {}
        for pol in BASE_POLICIES:
            summary[regime][pol] = {
                'episodes_requested': 10,
                'episodes_completed': 10,
                'mean_average_computation_delay': 1.0 if regime=='delay' else None,
                'std_average_computation_delay': 0.1,
                'mean_drop_ratio': 0.2 if regime=='drop_ratio' else None,
                'std_drop_ratio': 0.02,
                'total_tasks': 12,
                'completed_tasks': 12,
                'dropped_tasks': 0,
                'pending_tasks': 0,
            }
    (d / 'figure10_policy_metrics_summary.json').write_text(json.dumps(summary))
    readiness = {
        'baseline_validation_ready': False,
        'figure10_data_ready': False,
        'active_policy_set': BASE_POLICIES,
        'missing_policies': [],
        'validation_episode_count': 10
    }
    (d / 'figure10_policy_readiness.json').write_text(json.dumps(readiness))


def test_aggregator_creates_outputs(tmp_path):
    inp = tmp_path / 'sweep'
    make_synthetic_sweep(inp, '0.1')
    make_synthetic_sweep(inp, '0.2')
    out = tmp_path / 'out'
    res = aggregate(inp, out, 'task_arrival_probability', 'smoke-test', strict=False)
    # files exist
    assert Path(res['csv']).exists()
    assert Path(res['json']).exists()
    assert Path(res['metadata']).exists()
    for p in res['plots']:
        assert Path(p).exists()
    # metadata checks
    meta = json.loads(Path(res['metadata']).read_text())
    assert meta['plot_scope'] == 'smoke_sweep_baseline_only'
    assert meta['figure_claim'] == 'not_full_official_figure10'
    assert meta['simulation_rerun'] is False
    assert meta['paper_performance_claims_made'] is False
    assert 'HOODIE' not in meta['policies_plotted']


def test_strict_fails_on_missing_value(tmp_path):
    inp = tmp_path / 'sweep'
    # only create 0.1
    make_synthetic_sweep(inp, '0.1')
    out = tmp_path / 'out'
    with pytest.raises(SystemExit):
        aggregate(inp, out, 'task_arrival_probability', 'smoke-test', strict=True)


def test_script_does_not_import_simulation_entrypoints():
    # ensure the aggregator module does not import main or run_figure10_validation
    import importlib
    mod = importlib.import_module('scripts.aggregate_figure10_sweep_results')
    src = Path(mod.__file__).read_text()
    assert 'run_figure10_validation' not in src
    assert 'main.py' not in src
