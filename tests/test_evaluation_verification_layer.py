from __future__ import annotations

import json
from pathlib import Path

from evaluation.ablation_suite import AblationThrottle, run_ablation_suite
from evaluation.evaluation_pipeline import _build_summary_from_rows, _consistency_report, run_evaluation_pipeline, run_smoke_test
from evaluation.fairness_validator import FairnessValidationFailure, inject_asymmetric_workload_and_validate
from simulation.pipeline import PipelineConfig, run_single_experiment


def _base_config() -> PipelineConfig:
    return PipelineConfig(
        run_id="eval",
        seed=13,
        phase=0,
        num_edge_nodes=1,
        horizon=4,
        task_count=1,
        arrival_probability=1.0,
        smoke_only=True,
    )


def test_smoke_runner_emits_required_outputs(tmp_path: Path) -> None:
    result = run_smoke_test(_base_config(), tmp_path / "smoke")
    assert result["result"]["events"]
    assert (tmp_path / "smoke" / "raw_results.json").exists()
    assert (tmp_path / "smoke" / "summary.json").exists()
    assert (tmp_path / "smoke" / "enriched_summary.json").exists()


def test_fairness_injection_flags_imbalance() -> None:
    base = run_single_experiment(_base_config(), policy="fifo_only")
    rows = [dict(base), dict(base)]
    rows[1]["workload_signature"] = "different-signature"
    report = inject_asymmetric_workload_and_validate(rows, fail_fast=False)
    assert report["passed"] is False
    assert report["report"]["passed"] is False


def test_ablation_throttle_caps_runs(tmp_path: Path) -> None:
    report = run_ablation_suite(_base_config(), tmp_path / "ablation", throttle=AblationThrottle(max_runs_cap=2))
    assert report["ablation_throttled"] is True
    assert report["variant_count"] == 2
    assert len(report["results"]) == 2


def test_consistency_checker_detects_drift() -> None:
    base = run_single_experiment(_base_config(), policy="fifo_only")
    rows = [dict(base)]
    summary_rows = _build_summary_from_rows(rows)
    summary_rows[0]["latency_mean"] = float(summary_rows[0]["latency_mean"]) + 1.0
    report = _consistency_report(rows, summary_rows, {"status": "passed"})
    assert report["passed"] is False
    assert report["metric_drift"]


def test_evaluation_pipeline_produces_reports(tmp_path: Path) -> None:
    base = run_single_experiment(_base_config(), policy="fifo_only")
    experiment_dir = tmp_path / "experiment"
    experiment_dir.mkdir(parents=True, exist_ok=True)
    (experiment_dir / "raw_results.json").write_text(json.dumps([base], indent=2, sort_keys=True))
    (experiment_dir / "summary.json").write_text(json.dumps({"rows": [base], "config_count": 1, "run_count": 1}, indent=2, sort_keys=True))
    report = run_evaluation_pipeline(experiment_dir, experiment_dir / "evaluation")
    assert report["status"] == "passed"
    for name in (
        "raw_results.json",
        "summary.json",
        "enriched_summary.json",
        "fairness_report.json",
        "hypothesis_report.json",
        "ablation_report.json",
        "consistency_report.json",
        "safety_guard_report.json",
    ):
        assert (experiment_dir / "evaluation" / name).exists()
