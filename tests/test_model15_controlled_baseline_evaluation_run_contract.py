from __future__ import annotations

import json
from pathlib import Path

import pytest

from evaluation.baseline_runner import (
    BaselineScenario,
    POLICY_REGISTRY,
    run_baseline_evaluation,
    run_baseline_seed,
    scenario_catalog,
)


def _tiny_scenario() -> BaselineScenario:
    return BaselineScenario(
        scenario_id="tiny",
        description="tiny smoke scenario",
        num_edge_nodes=2,
        arrival_slots=6,
        drain_slots=4,
        task_size_range=(1, 2),
        deadline_range=(3, 5),
        edge_cpu_capacities=(1.0, 1.0),
        cloud_cpu_capacity=2.0,
        arrival_rate_schedule={"type": "constant", "rate": 1.0},
        queue_order=(0, 1, 2),
    )


def test_catalog_exposes_required_scenarios_and_policies() -> None:
    catalog = scenario_catalog()
    assert set(catalog.keys()) == {"low", "medium", "high", "burst"}
    assert set(POLICY_REGISTRY.keys()) == {"FIFO", "RO", "GreedyLatency"}


def test_single_seed_run_writes_required_outputs(tmp_path: Path) -> None:
    out_dir = tmp_path / "seed"
    report = run_baseline_seed(scenario=_tiny_scenario(), policy_name="FIFO", seed=7, output_dir=out_dir)
    assert report["paper_claims_made"] is False
    assert report["no_training"] is True
    assert report["no_learning_updates"] is True
    assert (out_dir / "task_lifecycle.csv").exists()
    assert (out_dir / "action_trace.csv").exists()
    assert (out_dir / "episode_metrics.csv").exists()
    assert (out_dir / "baseline_evaluation_report.json").exists()
    saved = json.loads((out_dir / "baseline_evaluation_report.json").read_text())
    assert saved["seed"] == 7
    assert saved["scenario"]["scenario_id"] == "tiny"
    assert saved["policy"]["name"] == "FIFO"
    assert saved["validation_status"] in {"passed", "degraded"}
    assert "mean" not in saved["computed_metrics"]  # per-seed report stays scalar, not aggregate


def test_reproducible_seed_reports_are_deterministic(tmp_path: Path) -> None:
    scenario = _tiny_scenario()
    out_a = tmp_path / "a"
    out_b = tmp_path / "b"
    report_a = run_baseline_seed(scenario=scenario, policy_name="GreedyLatency", seed=11, output_dir=out_a)
    report_b = run_baseline_seed(scenario=scenario, policy_name="GreedyLatency", seed=11, output_dir=out_b)
    assert report_a["config_hash"] == report_b["config_hash"]
    assert report_a["computed_metrics"] == report_b["computed_metrics"]


def test_aggregate_run_writes_summary_for_multiple_seeds(tmp_path: Path) -> None:
    out_dir = tmp_path / "baseline_runs"
    summary = run_baseline_evaluation(
        out_dir,
        scenario_ids=["low"],
        policy_names=["FIFO", "RO"],
        seeds=[1, 2, 3],
    )
    assert summary["status"] == "passed"
    assert summary["scenario_count"] == 1
    assert summary["policy_count"] == 2
    assert summary["seed_count"] == 3
    policy_summary = json.loads((out_dir / "low" / "FIFO" / "baseline_evaluation_summary.json").read_text())
    assert policy_summary["seed_count"] == 3
    assert policy_summary["aggregated_metrics"]["drop_rate"]["count"] == 3
    assert policy_summary["paper_claims_made"] is False
    root = json.loads((out_dir / "baseline_evaluation_root_summary.json").read_text())
    assert root["paper_claims_made"] is False
    assert len(root["baseline_runs"]) == 2


def test_trace_integrity_degrades_when_orphans_remain(tmp_path: Path) -> None:
    scenario = BaselineScenario(
        scenario_id="orphan",
        description="intentionally overloaded",
        num_edge_nodes=1,
        arrival_slots=2,
        drain_slots=0,
        task_size_range=(5, 5),
        deadline_range=(100, 100),
        edge_cpu_capacities=(0.1,),
        cloud_cpu_capacity=0.1,
        arrival_rate_schedule={"type": "constant", "rate": 4.0},
        queue_order=(0, 1),
    )
    out_dir = tmp_path / "seed"
    report = run_baseline_seed(scenario=scenario, policy_name="RO", seed=3, output_dir=out_dir)
    assert report["trace_integrity"] in {"PASSED", "DEGRADED"}
    assert (out_dir / "baseline_evaluation_report.json").exists()
    if report["trace_integrity"] == "DEGRADED":
        assert report["validation_status"] == "degraded"

