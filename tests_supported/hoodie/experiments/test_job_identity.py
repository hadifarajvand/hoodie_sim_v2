from __future__ import annotations

from src.hoodie.experiments.job_identity import compute_experiment_id, compute_job_id
from src.hoodie.experiments.panel_registry import PANEL_REGISTRY
from src.hoodie.experiments.specification import ExperimentSpec


def _spec(seed: int = 7) -> ExperimentSpec:
    return ExperimentSpec(campaign_id="campaign-1", experiment_id="experiment-1", policy="HOODIE", variant="hoodie_lstm", seed=seed, horizon=10, warmup=2, workload={"task_count": 3})


def test_experiment_id_is_deterministic_and_sensitive() -> None:
    a = compute_experiment_id(_spec(), source_commit="abc").value
    b = compute_experiment_id(_spec(), source_commit="abc").value
    c = compute_experiment_id(_spec(seed=8), source_commit="abc").value
    assert a == b
    assert a != c


def test_job_id_depends_on_panel_and_trace() -> None:
    spec = _spec()
    panel = PANEL_REGISTRY["figure_8a"].spec
    first = compute_job_id(spec, panel, source_commit="abc", trace_hash="trace-1").value
    second = compute_job_id(spec, panel, source_commit="abc", trace_hash="trace-1").value
    third = compute_job_id(spec, panel, source_commit="abc", trace_hash="trace-2").value
    assert first == second
    assert first != third
