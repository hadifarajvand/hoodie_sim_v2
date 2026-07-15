from __future__ import annotations

import pytest

from src.hoodie.experiments.specification import ExperimentSpec, PanelSpec


def test_experiment_spec_serialization_and_validation() -> None:
    spec = ExperimentSpec(
        campaign_id="campaign-1",
        experiment_id="experiment-1",
        policy="HOODIE",
        variant="hoodie_lstm",
        seed=7,
        horizon=10,
        warmup=2,
        topology={"nodes": 4},
        physical={"rate": 1.0},
        workload={"task_count": 3},
        training={"lr": 1e-3},
        evaluation={"metric": "reward"},
    )
    assert "campaign-1" in spec.canonical_json()
    with pytest.raises(ValueError):
        ExperimentSpec(campaign_id="c", experiment_id="e", policy="bad", variant=None, seed=1, horizon=1, warmup=0)
    with pytest.raises(ValueError):
        ExperimentSpec(campaign_id="c", experiment_id="e", policy="HOODIE", variant=None, seed=1, horizon=0, warmup=0)


def test_panel_spec_accepts_required_shape() -> None:
    panel = PanelSpec(panel_id="figure_8a", independent_variable="policy", fixed_parameters={}, policies=("FLC", "RO"), expected_columns=("policy",), output_filenames=("figure_8a.svg",))
    assert panel.panel_id == "figure_8a"
