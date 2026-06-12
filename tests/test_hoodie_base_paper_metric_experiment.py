from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
PYTHON = Path(sys.executable)


def _run(args, cwd=ROOT):
    return subprocess.run([str(PYTHON), *args], cwd=cwd, capture_output=True, text=True, check=False)


def _repo_forbidden_snapshot():
    forbidden_suffixes = {".png", ".csv", ".json", ".md"}
    forbidden_names = {
        "base_paper_metrics_raw.csv",
        "base_paper_metrics_summary.csv",
        "base_paper_metrics_summary.json",
        "base_paper_metric_experiment_report.md",
        "base_paper_metric_experiment_manifest.json",
    }
    return {p for p in ROOT.rglob("*") if p.suffix in forbidden_suffixes or p.name in forbidden_names}


def _read_json(path: Path):
    return json.loads(path.read_text())


def test_script_imports_without_running():
    result = _run(["-c", "import scripts.run_hoodie_base_paper_metric_experiment as m; print(m.__name__)"])
    assert result.returncode == 0, result.stderr
    assert "scripts.run_hoodie_base_paper_metric_experiment" in result.stdout


def test_missing_allow_flag_exits_non_zero(tmp_path):
    result = _run(
        [
            "scripts/run_hoodie_base_paper_metric_experiment.py",
            "--output-dir",
            str(tmp_path / "out"),
            "--episodes",
            "3",
            "--episode-time",
            "2",
            "--seed",
            "42",
            "--run-id",
            "phase7_base_paper_metric_experiment_quick",
            "--mode",
            "quick",
            "--policies",
            "HOODIE,RO,FLC",
            "--allow-nonofficial-paper-metric-output",
        ]
    )
    assert result.returncode != 0


def test_output_dir_inside_repo_is_refused(tmp_path):
    repo_output = ROOT / "artifacts" / "paper-contract-audit" / "phase7_0" / "repo_output"
    if repo_output.exists():
        if repo_output.is_dir():
            shutil.rmtree(repo_output)
        else:
            repo_output.unlink()
    result = _run(
        [
            "scripts/run_hoodie_base_paper_metric_experiment.py",
            "--output-dir",
            str(repo_output),
            "--episodes",
            "3",
            "--episode-time",
            "2",
            "--seed",
            "42",
            "--run-id",
            "phase7_base_paper_metric_experiment_quick",
            "--mode",
            "quick",
            "--policies",
            "HOODIE,RO,FLC",
            "--allow-base-paper-metric-experiment",
            "--allow-nonofficial-paper-metric-output",
        ]
    )
    assert result.returncode != 0
    assert not repo_output.exists()


def test_quick_mode_generates_outputs(tmp_path):
    before = _repo_forbidden_snapshot()
    result = _run(
        [
            "scripts/run_hoodie_base_paper_metric_experiment.py",
            "--output-dir",
            str(tmp_path / "out"),
            "--episodes",
            "3",
            "--episode-time",
            "2",
            "--seed",
            "42",
            "--run-id",
            "phase7_base_paper_metric_experiment_quick",
            "--mode",
            "quick",
            "--policies",
            "HOODIE,RO,FLC",
            "--allow-base-paper-metric-experiment",
            "--allow-nonofficial-paper-metric-output",
        ]
    )
    assert result.returncode == 0, result.stderr
    output = tmp_path / "out" / "paper_metric_outputs"
    raw = output / "base_paper_metrics_raw.csv"
    summary_csv = output / "base_paper_metrics_summary.csv"
    summary_json = output / "base_paper_metrics_summary.json"
    manifest = output / "base_paper_metric_experiment_manifest.json"
    report = output / "base_paper_metric_experiment_report.md"
    plots = output / "plots"
    assert raw.exists()
    assert summary_csv.exists()
    assert summary_json.exists()
    assert manifest.exists()
    assert report.exists()
    assert plots.exists()
    assert any(p.name == "delay_vs_task_arrival_probability.png" for p in plots.iterdir())
    assert any(p.name == "drop_ratio_vs_task_arrival_probability.png" for p in plots.iterdir())
    assert before == _repo_forbidden_snapshot()


def test_quick_mode_generates_required_manifest_fields(tmp_path):
    _run(
        [
            "scripts/run_hoodie_base_paper_metric_experiment.py",
            "--output-dir",
            str(tmp_path / "out"),
            "--episodes",
            "3",
            "--episode-time",
            "2",
            "--seed",
            "42",
            "--run-id",
            "phase7_base_paper_metric_experiment_quick",
            "--mode",
            "quick",
            "--policies",
            "HOODIE,RO,FLC",
            "--allow-base-paper-metric-experiment",
            "--allow-nonofficial-paper-metric-output",
        ]
    )
    manifest = _read_json(tmp_path / "out" / "paper_metric_outputs" / "base_paper_metric_experiment_manifest.json")
    assert manifest["official_paper_reproduction"] is False
    assert manifest["exact_figure_reproduction_claim"] is False
    assert manifest["contribution_enabled"] is False
    assert manifest["deadline_aware_extension"] is False
    assert manifest["qos_extension"] is False
    assert manifest["queueing_extension"] is False


def test_raw_and_summary_columns_present(tmp_path):
    _run(
        [
            "scripts/run_hoodie_base_paper_metric_experiment.py",
            "--output-dir",
            str(tmp_path / "out"),
            "--episodes",
            "3",
            "--episode-time",
            "2",
            "--seed",
            "42",
            "--run-id",
            "phase7_base_paper_metric_experiment_quick",
            "--mode",
            "quick",
            "--policies",
            "HOODIE,RO,FLC",
            "--allow-base-paper-metric-experiment",
            "--allow-nonofficial-paper-metric-output",
        ]
    )
    output = tmp_path / "out" / "paper_metric_outputs"
    raw_rows = list(csv.DictReader((output / "base_paper_metrics_raw.csv").read_text().splitlines()))
    summary_rows = list(csv.DictReader((output / "base_paper_metrics_summary.csv").read_text().splitlines()))
    raw_required = {
        "run_id",
        "mode",
        "sweep_name",
        "sweep_parameter",
        "sweep_value",
        "policy_name",
        "episode_id",
        "seed",
        "total_tasks",
        "completed_tasks",
        "dropped_tasks",
        "pending_tasks",
        "average_delay",
        "drop_ratio",
        "mean_reward",
        "total_reward",
        "local_action_count",
        "horizontal_action_count",
        "vertical_action_count",
        "unknown_action_count",
        "local_action_ratio",
        "horizontal_action_ratio",
        "vertical_action_ratio",
        "unknown_action_ratio",
        "source_trace_dir",
        "policy_status",
        "notes_json",
    }
    summary_required = {
        "sweep_name",
        "sweep_value",
        "policy_name",
        "episodes_completed",
        "mean_average_delay",
        "std_average_delay",
        "mean_drop_ratio",
        "std_drop_ratio",
        "total_tasks",
        "completed_tasks",
        "dropped_tasks",
        "pending_tasks",
        "mean_local_action_ratio",
        "mean_horizontal_action_ratio",
        "mean_vertical_action_ratio",
        "mean_unknown_action_ratio",
        "policy_status",
        "warnings",
    }
    assert raw_rows and raw_required.issubset(raw_rows[0].keys())
    assert summary_rows and summary_required.issubset(summary_rows[0].keys())


def test_unavailable_baseline_is_recorded_but_not_fatal(tmp_path, monkeypatch):
    import scripts.run_hoodie_base_paper_metric_experiment as experiment

    real_profile = experiment._policy_profile

    def fake_profile(policy_name):
        if policy_name == "RO":
            raise RuntimeError("baseline not available in this test")
        return real_profile(policy_name)

    monkeypatch.setattr(experiment, "_policy_profile", fake_profile)
    result = experiment.main(
        [
            "--output-dir",
            str(tmp_path / "out"),
            "--episodes",
            "3",
            "--episode-time",
            "2",
            "--seed",
            "42",
            "--run-id",
            "phase7_base_paper_metric_experiment_quick",
            "--mode",
            "quick",
            "--policies",
            "HOODIE,RO,FLC",
            "--allow-base-paper-metric-experiment",
            "--allow-nonofficial-paper-metric-output",
        ]
    )
    assert result == 0
    manifest = _read_json(tmp_path / "out" / "paper_metric_outputs" / "base_paper_metric_experiment_manifest.json")
    assert "RO" in manifest["failed_or_unavailable_policies"]


def test_no_generated_artifacts_inside_repo_tree(tmp_path):
    before = _repo_forbidden_snapshot()
    _run(
        [
            "scripts/run_hoodie_base_paper_metric_experiment.py",
            "--output-dir",
            str(tmp_path / "out"),
            "--episodes",
            "3",
            "--episode-time",
            "2",
            "--seed",
            "42",
            "--run-id",
            "phase7_base_paper_metric_experiment_quick",
            "--mode",
            "quick",
            "--policies",
            "HOODIE,RO,FLC",
            "--allow-base-paper-metric-experiment",
            "--allow-nonofficial-paper-metric-output",
        ]
    )
    assert before == _repo_forbidden_snapshot()
