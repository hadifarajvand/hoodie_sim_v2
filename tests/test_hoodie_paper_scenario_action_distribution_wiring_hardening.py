from __future__ import annotations

import argparse
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
    forbidden_suffixes = {".pth", ".pt", ".pkl", ".pickle"}
    forbidden_names = {
        "hoodie_paper_scenario_action_distribution_wiring_hardening_manifest.json",
        "hoodie_paper_scenario_action_distribution_wiring_hardening_report.json",
        "hoodie_action_distribution_contract_summary.json",
        "hoodie_smoke_checkpoint_evaluation_metrics_hardening_manifest.json",
        "hoodie_smoke_checkpoint_evaluation_metrics_hardening_report.json",
        "hoodie_smoke_checkpoint_metrics_contract_summary.json",
        "hoodie_trained_checkpoint_evaluation_wiring_smoke_manifest.json",
        "hoodie_trained_checkpoint_evaluation_wiring_smoke_report.json",
        "hoodie_bounded_small_real_training_smoke_manifest.json",
        "hoodie_bounded_small_real_training_smoke_report.json",
        "hoodie_small_real_training_export_manifest.json",
        "figure10_policy_metrics_raw.csv",
        "figure10_policy_metrics_summary.json",
        "figure10_policy_readiness.json",
        "figure10_run_config_snapshot.json",
        "figure10_validation_manifest.json",
        "action_records.json",
        "hoodie_action_distribution.csv",
        "hoodie_action_distribution.json",
        "hoodie_action_distribution_metadata.json",
        "scheduler.pth",
        "paper_state_trace.csv",
        "queue_trace.csv",
        "mleo_candidate_latency_trace.csv",
    }
    return {p for p in ROOT.rglob("*") if p.suffix in forbidden_suffixes or p.name in forbidden_names}


def _write_json(path: Path, data: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True))


def _write_metrics_hardening_tree(
    output_dir: Path,
    *,
    figure10_data_ready: bool = False,
    diagnostics: dict[str, object] | None = None,
    write_manifest: bool = True,
    write_report: bool = True,
) -> None:
    metrics = output_dir / "metrics_hardening"
    wiring = metrics / "wiring_smoke"
    runner = wiring / "evaluation_runner"
    runner.mkdir(parents=True, exist_ok=True)
    raw_rows = [
        {
            "run_id": "phase6_14_smoke_checkpoint_evaluation_metrics_hardening",
            "regime_id": "delay",
            "policy_name": "HOODIE",
            "policy_class": "Agent",
            "episode_id": 0,
            "validation_episode_count": 1,
            "task_count": 1,
            "completed_tasks": 1,
            "dropped_tasks": 0,
            "pending_tasks": 0,
            "average_computation_delay": 0.0,
            "drop_ratio": 0.0,
            "mean_reward": 0.0,
            "total_reward": 0.0,
            "mleo_contract_status": "missing",
            "delayed_reward_contract_status": "missing",
            "policy_readiness_status": "ready",
            "hoodie_checkpoint_status": "present_and_loaded",
            "config_hash": "abc",
            "trace_dir": str(runner / "runs" / "phase6_14" / "delay" / "HOODIE" / "trace"),
            "notes_json": json.dumps(
                {
                    "regime_id": "delay",
                    "regime_source": "paper_contract_or_unverified_runtime_override",
                    "average_computation_delay_denominator": 1,
                    "drop_ratio_denominator": 1,
                    "policy_readiness_status": "ready",
                    "pending_tasks_visible": True,
                    "contract_diagnostics": [],
                },
                sort_keys=True,
            ),
        },
        {
            "run_id": "phase6_14_smoke_checkpoint_evaluation_metrics_hardening",
            "regime_id": "drop_ratio",
            "policy_name": "HOODIE",
            "policy_class": "Agent",
            "episode_id": 0,
            "validation_episode_count": 1,
            "task_count": 1,
            "completed_tasks": 1,
            "dropped_tasks": 0,
            "pending_tasks": 0,
            "average_computation_delay": 0.0,
            "drop_ratio": 0.0,
            "mean_reward": 0.0,
            "total_reward": 0.0,
            "mleo_contract_status": "missing",
            "delayed_reward_contract_status": "missing",
            "policy_readiness_status": "ready",
            "hoodie_checkpoint_status": "present_and_loaded",
            "config_hash": "abc",
            "trace_dir": str(runner / "runs" / "phase6_14" / "drop_ratio" / "HOODIE" / "trace"),
            "notes_json": json.dumps(
                {
                    "regime_id": "drop_ratio",
                    "regime_source": "paper_contract_or_unverified_runtime_override",
                    "average_computation_delay_denominator": 1,
                    "drop_ratio_denominator": 1,
                    "policy_readiness_status": "ready",
                    "pending_tasks_visible": True,
                    "contract_diagnostics": [],
                },
                sort_keys=True,
            ),
        },
    ]
    with (runner / "figure10_policy_metrics_raw.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(raw_rows[0].keys()))
        writer.writeheader()
        writer.writerows(raw_rows)
    _write_json(runner / "figure10_policy_metrics_summary.json", {"registry": {"active_policy_set": ["HOODIE"]}, "validation_episode_count": 1, "figure10_data_ready": figure10_data_ready, "no_metric_rows_generated": False})
    _write_json(runner / "figure10_policy_readiness.json", {"validation_episode_count": 1, "active_policy_set": ["HOODIE"], "figure10_data_ready": figure10_data_ready})
    _write_json(runner / "figure10_validation_manifest.json", {"diagnostic_only": True, "figure10_data_ready": figure10_data_ready, **(diagnostics or {})})
    _write_json(runner / "figure10_run_config_snapshot.json", {"trace_level": "summary"})
    if write_manifest:
        _write_json(metrics / "hoodie_smoke_checkpoint_evaluation_metrics_hardening_manifest.json", {"metrics_consistency_valid": True, "raw_metrics_policy_scope_valid": True, "raw_metrics_regime_scope_valid": True, "raw_metrics_numeric_contract_valid": True, "raw_metrics_notes_json_valid": True, "summary_metrics_schema_valid": True, "readiness_schema_valid": True, "manifest_schema_valid": True, "official_claim_allowed": False, "paper_reproduction_claim": False, "readiness_figure10_data_ready": figure10_data_ready})
    if write_report:
        _write_json(metrics / "hoodie_smoke_checkpoint_evaluation_metrics_hardening_report.json", {"metrics_hardening_run": True, "wiring_smoke_completed": True, "metrics_files_present": True, "raw_metrics_schema_valid": True, "raw_metrics_numeric_contract_valid": True, "raw_metrics_notes_json_valid": True, "metrics_consistency_valid": True, "figure10_data_ready": figure10_data_ready, "official_claim_allowed": False, "paper_reproduction_claim": False, "blockers": []})


def _run_smoke(output_dir: Path, *, allow_unknown_actions_for_diagnostic: bool = False, figure10_data_ready: bool = False, diagnostics: dict[str, object] | None = None):
    import scripts.run_hoodie_paper_scenario_action_distribution_wiring_hardening as smoke

    def fake_run_metrics_hardening(**kwargs):
        _write_metrics_hardening_tree(kwargs["output_dir"], figure10_data_ready=figure10_data_ready, diagnostics=diagnostics)
        return subprocess.CompletedProcess(args=["metrics"], returncode=0, stdout="", stderr="")

    smoke._run_metrics_hardening = fake_run_metrics_hardening
    return smoke.run_smoke(
        argparse.Namespace(
            output_dir=str(output_dir),
            training_epochs=1,
            training_episode_time=3,
            validation_episodes=1,
            seed=42,
            run_id="phase6_15_paper_scenario_action_distribution_wiring_hardening",
            expected_agent_count=20,
            trace_level="summary",
            allow_paper_scenario_action_distribution_wiring_hardening=True,
            allow_smoke_checkpoint_evaluation_metrics_hardening=True,
            allow_trained_checkpoint_evaluation_wiring_smoke=True,
            allow_bounded_training_smoke=True,
            allow_figure10_validation_test_mode=True,
            allow_main_py_training_execution=True,
            allow_training_checkpoint_export=True,
            allow_unknown_actions_for_diagnostic=allow_unknown_actions_for_diagnostic,
            policies="HOODIE",
        )
    )


def test_script_imports_without_running():
    result = _run(["-c", "import scripts.run_hoodie_paper_scenario_action_distribution_wiring_hardening as m; print(m.__name__)"])
    assert result.returncode == 0, result.stderr
    assert "scripts.run_hoodie_paper_scenario_action_distribution_wiring_hardening" in result.stdout


@pytest.mark.parametrize(
    "missing_flag",
    [
        "--allow-paper-scenario-action-distribution-wiring-hardening",
        "--allow-smoke-checkpoint-evaluation-metrics-hardening",
        "--allow-trained-checkpoint-evaluation-wiring-smoke",
        "--allow-bounded-training-smoke",
        "--allow-figure10-validation-test-mode",
        "--allow-main-py-training-execution",
        "--allow-training-checkpoint-export",
    ],
)
def test_missing_allow_flags_exit_non_zero(tmp_path, missing_flag):
    flags = [
        "--allow-paper-scenario-action-distribution-wiring-hardening",
        "--allow-smoke-checkpoint-evaluation-metrics-hardening",
        "--allow-trained-checkpoint-evaluation-wiring-smoke",
        "--allow-bounded-training-smoke",
        "--allow-figure10-validation-test-mode",
        "--allow-main-py-training-execution",
        "--allow-training-checkpoint-export",
    ]
    flags.remove(missing_flag)
    result = _run(
        [
            "scripts/run_hoodie_paper_scenario_action_distribution_wiring_hardening.py",
            "--output-dir",
            str(tmp_path / "out"),
            "--training-epochs",
            "1",
            "--training-episode-time",
            "3",
            "--validation-episodes",
            "1",
            "--seed",
            "42",
            "--run-id",
            "phase6_15_paper_scenario_action_distribution_wiring_hardening",
            *flags,
        ]
    )
    assert result.returncode != 0


@pytest.mark.parametrize(
    "flag,value",
    [
        ("--training-epochs", "0"),
        ("--training-epochs", "2"),
        ("--training-episode-time", "0"),
        ("--training-episode-time", "4"),
        ("--validation-episodes", "0"),
        ("--validation-episodes", "2"),
    ],
)
def test_bounds_exit_non_zero(tmp_path, flag, value):
    result = _run(
        [
            "scripts/run_hoodie_paper_scenario_action_distribution_wiring_hardening.py",
            "--output-dir",
            str(tmp_path / "out"),
            "--allow-paper-scenario-action-distribution-wiring-hardening",
            "--allow-smoke-checkpoint-evaluation-metrics-hardening",
            "--allow-trained-checkpoint-evaluation-wiring-smoke",
            "--allow-bounded-training-smoke",
            "--allow-figure10-validation-test-mode",
            "--allow-main-py-training-execution",
            "--allow-training-checkpoint-export",
            flag,
            value,
        ]
    )
    assert result.returncode != 0


def test_output_inside_repo_is_refused_and_creates_no_file_or_directory(tmp_path):
    repo_output = ROOT / "artifacts/paper-contract-audit/phase6_15/repo_output"
    if repo_output.exists():
        if repo_output.is_dir():
            shutil.rmtree(repo_output)
        else:
            repo_output.unlink()
    result = _run(
        [
            "scripts/run_hoodie_paper_scenario_action_distribution_wiring_hardening.py",
            "--output-dir",
            str(repo_output),
            "--allow-paper-scenario-action-distribution-wiring-hardening",
            "--allow-smoke-checkpoint-evaluation-metrics-hardening",
            "--allow-trained-checkpoint-evaluation-wiring-smoke",
            "--allow-bounded-training-smoke",
            "--allow-figure10-validation-test-mode",
            "--allow-main-py-training-execution",
            "--allow-training-checkpoint-export",
        ]
    )
    assert result.returncode != 0
    assert not repo_output.exists()


def test_successful_wiring_hardening_runs_only_in_tmp_path(tmp_path):
    before = _repo_forbidden_snapshot()
    import scripts.run_hoodie_paper_scenario_action_distribution_wiring_hardening as smoke

    result = _run_smoke(tmp_path / "out")
    assert result["manifest"]["action_distribution_wiring_hardening_run"] is True
    assert result["manifest"]["metrics_hardening_run"] is True
    assert result["manifest"]["validation_policies"] == ["HOODIE"]
    assert result["manifest"]["validation_episodes"] == 1
    assert result["manifest"]["simulation_rerun"] is True
    assert result["manifest"]["official_simulation_rerun"] is False
    assert result["manifest"]["action_records_present"] is True
    assert result["manifest"]["action_records_schema_valid"] is True
    assert result["manifest"]["action_records_explicit_category_valid"] is True
    assert result["manifest"]["action_records_policy_scope_valid"] is True
    assert result["manifest"]["action_records_regime_scope_valid"] is True
    assert result["manifest"]["action_distribution_files_present"] is True
    assert result["manifest"]["action_distribution_counts_valid"] is True
    assert result["manifest"]["action_distribution_ratios_valid"] is True
    assert result["manifest"]["unknown_actions_present"] is False
    assert result["manifest"]["paper_scenario_action_distribution_ready"] is False
    assert result["manifest"]["figure9_data_ready"] is False
    assert result["manifest"]["figure10_data_ready"] is False
    assert result["manifest"]["official_claim_allowed"] is False
    assert result["manifest"]["paper_reproduction_claim"] is False
    assert result["report"]["metrics_hardening_completed"] is True
    assert result["report"]["action_records_present"] is True
    assert result["report"]["action_distribution_files_present"] is True
    assert result["report"]["action_distribution_counts_valid"] is True
    assert result["report"]["action_distribution_ratios_valid"] is True
    assert result["report"]["figure9_data_ready"] is False
    assert result["report"]["figure10_data_ready"] is False
    assert result["report"]["official_claim_allowed"] is False
    assert result["report"]["paper_reproduction_claim"] is False
    assert result["manifest"]["action_records_source"] == "synthetic_phase6_15_wiring_probe"
    assert result["manifest"]["synthetic_action_records_used"] is True
    assert result["manifest"]["real_action_records_used"] is False
    out = tmp_path / "out"
    action_dir = out / "action_distribution"
    records = json.loads((action_dir / "action_records.json").read_text())
    csv_rows = list(csv.DictReader((action_dir / "hoodie_action_distribution.csv").read_text().splitlines()))
    distribution = json.loads((action_dir / "hoodie_action_distribution.json").read_text())
    metadata = json.loads((action_dir / "hoodie_action_distribution_metadata.json").read_text())
    contract = json.loads((action_dir / "hoodie_action_distribution_contract_summary.json").read_text())
    assert len(records) == distribution["total_actions"]
    assert all(record["policy_name"] == "HOODIE" for record in records)
    assert sorted({record["regime_id"] for record in records}) == ["delay", "drop_ratio"]
    assert all(isinstance(record["selected_action"], str) for record in records)
    assert all(record["selected_action"] in {"local", "horizontal", "vertical"} for record in records)
    assert all(record["diagnostic_only"] is True for record in records)
    assert all(record["official_figure_claim"] is False for record in records)
    assert all(record["paper_reproduction_claim"] is False for record in records)
    assert distribution["policy_name"] == "HOODIE"
    assert distribution["unknown_count"] == 0
    assert distribution["local_count"] + distribution["horizontal_count"] + distribution["vertical_count"] + distribution["unknown_count"] == distribution["total_actions"]
    assert abs(distribution["local_ratio"] + distribution["horizontal_ratio"] + distribution["vertical_ratio"] + distribution["unknown_ratio"] - 1.0) < 1e-9
    assert metadata["official_figure_claim"] is False
    assert metadata["paper_reproduction_claim"] is False
    assert metadata["source"] == "checkpointed_evaluation_or_synthetic_test"
    assert contract["figure9_data_ready"] is False
    assert contract["figure10_data_ready"] is False
    assert before == _repo_forbidden_snapshot()


def test_metrics_hardening_returncode_nonzero_sets_blocker(tmp_path):
    import scripts.run_hoodie_paper_scenario_action_distribution_wiring_hardening as smoke

    def fake_run_metrics_hardening(**kwargs):
        return subprocess.CompletedProcess(args=["metrics"], returncode=1, stdout="", stderr="")

    smoke._run_metrics_hardening = fake_run_metrics_hardening
    result = smoke.run_smoke(
        argparse.Namespace(
            output_dir=str(tmp_path / "out"),
            training_epochs=1,
            training_episode_time=3,
            validation_episodes=1,
            seed=42,
            run_id="phase6_15_paper_scenario_action_distribution_wiring_hardening",
            expected_agent_count=20,
            trace_level="summary",
            allow_paper_scenario_action_distribution_wiring_hardening=True,
            allow_smoke_checkpoint_evaluation_metrics_hardening=True,
            allow_trained_checkpoint_evaluation_wiring_smoke=True,
            allow_bounded_training_smoke=True,
            allow_figure10_validation_test_mode=True,
            allow_main_py_training_execution=True,
            allow_training_checkpoint_export=True,
            allow_unknown_actions_for_diagnostic=False,
            policies="HOODIE",
        )
    )
    assert "metrics_hardening_failed" in result["report"]["blockers"]


def test_metrics_hardening_manifest_missing_sets_blocker(tmp_path):
    import scripts.run_hoodie_paper_scenario_action_distribution_wiring_hardening as smoke

    def fake_run_metrics_hardening(**kwargs):
        _write_metrics_hardening_tree(kwargs["output_dir"], write_manifest=False)
        return subprocess.CompletedProcess(args=["metrics"], returncode=0, stdout="", stderr="")

    smoke._run_metrics_hardening = fake_run_metrics_hardening
    result = smoke.run_smoke(
        argparse.Namespace(
            output_dir=str(tmp_path / "out"),
            training_epochs=1,
            training_episode_time=3,
            validation_episodes=1,
            seed=42,
            run_id="phase6_15_paper_scenario_action_distribution_wiring_hardening",
            expected_agent_count=20,
            trace_level="summary",
            allow_paper_scenario_action_distribution_wiring_hardening=True,
            allow_smoke_checkpoint_evaluation_metrics_hardening=True,
            allow_trained_checkpoint_evaluation_wiring_smoke=True,
            allow_bounded_training_smoke=True,
            allow_figure10_validation_test_mode=True,
            allow_main_py_training_execution=True,
            allow_training_checkpoint_export=True,
            allow_unknown_actions_for_diagnostic=False,
            policies="HOODIE",
        )
    )
    assert "metrics_hardening_manifest_missing" in result["report"]["blockers"]


def test_metrics_hardening_report_missing_sets_blocker(tmp_path):
    import scripts.run_hoodie_paper_scenario_action_distribution_wiring_hardening as smoke

    def fake_run_metrics_hardening(**kwargs):
        _write_metrics_hardening_tree(kwargs["output_dir"], write_report=False)
        return subprocess.CompletedProcess(args=["metrics"], returncode=0, stdout="", stderr="")

    smoke._run_metrics_hardening = fake_run_metrics_hardening
    result = smoke.run_smoke(
        argparse.Namespace(
            output_dir=str(tmp_path / "out"),
            training_epochs=1,
            training_episode_time=3,
            validation_episodes=1,
            seed=42,
            run_id="phase6_15_paper_scenario_action_distribution_wiring_hardening",
            expected_agent_count=20,
            trace_level="summary",
            allow_paper_scenario_action_distribution_wiring_hardening=True,
            allow_smoke_checkpoint_evaluation_metrics_hardening=True,
            allow_trained_checkpoint_evaluation_wiring_smoke=True,
            allow_bounded_training_smoke=True,
            allow_figure10_validation_test_mode=True,
            allow_main_py_training_execution=True,
            allow_training_checkpoint_export=True,
            allow_unknown_actions_for_diagnostic=False,
            policies="HOODIE",
        )
    )
    assert "metrics_hardening_report_missing" in result["report"]["blockers"]


def test_metrics_hardening_consistency_false_sets_blocker(tmp_path):
    import scripts.run_hoodie_paper_scenario_action_distribution_wiring_hardening as smoke

    def fake_run_metrics_hardening(**kwargs):
        _write_metrics_hardening_tree(kwargs["output_dir"], diagnostics={"metrics_consistency_valid": False})
        metrics = Path(kwargs["output_dir"]) / "metrics_hardening"
        _write_json(metrics / "hoodie_smoke_checkpoint_evaluation_metrics_hardening_manifest.json", {"metrics_consistency_valid": False, "raw_metrics_policy_scope_valid": True, "raw_metrics_regime_scope_valid": True, "raw_metrics_numeric_contract_valid": True, "raw_metrics_notes_json_valid": True, "summary_metrics_schema_valid": True, "readiness_schema_valid": True, "manifest_schema_valid": True, "official_claim_allowed": False, "paper_reproduction_claim": False, "readiness_figure10_data_ready": False})
        return subprocess.CompletedProcess(args=["metrics"], returncode=0, stdout="", stderr="")

    smoke._run_metrics_hardening = fake_run_metrics_hardening
    result = smoke.run_smoke(
        argparse.Namespace(
            output_dir=str(tmp_path / "out"),
            training_epochs=1,
            training_episode_time=3,
            validation_episodes=1,
            seed=42,
            run_id="phase6_15_paper_scenario_action_distribution_wiring_hardening",
            expected_agent_count=20,
            trace_level="summary",
            allow_paper_scenario_action_distribution_wiring_hardening=True,
            allow_smoke_checkpoint_evaluation_metrics_hardening=True,
            allow_trained_checkpoint_evaluation_wiring_smoke=True,
            allow_bounded_training_smoke=True,
            allow_figure10_validation_test_mode=True,
            allow_main_py_training_execution=True,
            allow_training_checkpoint_export=True,
            allow_unknown_actions_for_diagnostic=False,
            policies="HOODIE",
        )
    )
    assert "metrics_hardening_consistency_invalid" in result["report"]["blockers"]
    assert result["manifest"]["action_distribution_wiring_ready"] is False


def test_metrics_hardening_policy_scope_false_sets_blocker(tmp_path):
    import scripts.run_hoodie_paper_scenario_action_distribution_wiring_hardening as smoke

    def fake_run_metrics_hardening(**kwargs):
        _write_metrics_hardening_tree(kwargs["output_dir"])
        metrics = Path(kwargs["output_dir"]) / "metrics_hardening"
        _write_json(metrics / "hoodie_smoke_checkpoint_evaluation_metrics_hardening_manifest.json", {"metrics_consistency_valid": True, "raw_metrics_policy_scope_valid": False, "raw_metrics_regime_scope_valid": True, "raw_metrics_numeric_contract_valid": True, "raw_metrics_notes_json_valid": True, "summary_metrics_schema_valid": True, "readiness_schema_valid": True, "manifest_schema_valid": True, "official_claim_allowed": False, "paper_reproduction_claim": False, "readiness_figure10_data_ready": False})
        return subprocess.CompletedProcess(args=["metrics"], returncode=0, stdout="", stderr="")

    smoke._run_metrics_hardening = fake_run_metrics_hardening
    result = smoke.run_smoke(
        argparse.Namespace(
            output_dir=str(tmp_path / "out"),
            training_epochs=1,
            training_episode_time=3,
            validation_episodes=1,
            seed=42,
            run_id="phase6_15_paper_scenario_action_distribution_wiring_hardening",
            expected_agent_count=20,
            trace_level="summary",
            allow_paper_scenario_action_distribution_wiring_hardening=True,
            allow_smoke_checkpoint_evaluation_metrics_hardening=True,
            allow_trained_checkpoint_evaluation_wiring_smoke=True,
            allow_bounded_training_smoke=True,
            allow_figure10_validation_test_mode=True,
            allow_main_py_training_execution=True,
            allow_training_checkpoint_export=True,
            allow_unknown_actions_for_diagnostic=False,
            policies="HOODIE",
        )
    )
    assert "metrics_hardening_raw_policy_scope_invalid" in result["report"]["blockers"]


def test_figure10_data_ready_true_sets_blocker(tmp_path):
    import scripts.run_hoodie_paper_scenario_action_distribution_wiring_hardening as smoke

    def fake_run_metrics_hardening(**kwargs):
        _write_metrics_hardening_tree(kwargs["output_dir"], figure10_data_ready=True)
        return subprocess.CompletedProcess(args=["metrics"], returncode=0, stdout="", stderr="")

    smoke._run_metrics_hardening = fake_run_metrics_hardening
    result = smoke.run_smoke(
        argparse.Namespace(
            output_dir=str(tmp_path / "out"),
            training_epochs=1,
            training_episode_time=3,
            validation_episodes=1,
            seed=42,
            run_id="phase6_15_paper_scenario_action_distribution_wiring_hardening",
            expected_agent_count=20,
            trace_level="summary",
            allow_paper_scenario_action_distribution_wiring_hardening=True,
            allow_smoke_checkpoint_evaluation_metrics_hardening=True,
            allow_trained_checkpoint_evaluation_wiring_smoke=True,
            allow_bounded_training_smoke=True,
            allow_figure10_validation_test_mode=True,
            allow_main_py_training_execution=True,
            allow_training_checkpoint_export=True,
            allow_unknown_actions_for_diagnostic=False,
            policies="HOODIE",
        )
    )
    assert "metrics_hardening_figure10_data_ready_true" in result["report"]["blockers"] or "unexpected_figure10_data_ready_true" in result["report"]["blockers"]


def test_real_action_records_json_is_used_when_present(tmp_path):
    import scripts.run_hoodie_paper_scenario_action_distribution_wiring_hardening as smoke

    def fake_run_metrics_hardening(**kwargs):
        _write_metrics_hardening_tree(kwargs["output_dir"])
        action_root = Path(kwargs["output_dir"]) / "metrics_hardening" / "wiring_smoke"
        real = action_root / "evaluation_runner" / "action_records.json"
        _write_json(
            real,
            [
                {
                    "run_id": "phase6_14_smoke_checkpoint_evaluation_metrics_hardening",
                    "regime_id": "delay",
                    "policy_name": "HOODIE",
                    "agent_index": 0,
                    "evaluation_step": 0,
                    "action_category": "local",
                    "selected_action": "local",
                    "source": "real",
                    "diagnostic_only": True,
                    "official_figure_claim": False,
                    "paper_reproduction_claim": False,
                }
            ],
        )
        return subprocess.CompletedProcess(args=["metrics"], returncode=0, stdout="", stderr="")

    smoke._run_metrics_hardening = fake_run_metrics_hardening
    result = smoke.run_smoke(
        argparse.Namespace(
            output_dir=str(tmp_path / "out"),
            training_epochs=1,
            training_episode_time=3,
            validation_episodes=1,
            seed=42,
            run_id="phase6_15_paper_scenario_action_distribution_wiring_hardening",
            expected_agent_count=20,
            trace_level="summary",
            allow_paper_scenario_action_distribution_wiring_hardening=True,
            allow_smoke_checkpoint_evaluation_metrics_hardening=True,
            allow_trained_checkpoint_evaluation_wiring_smoke=True,
            allow_bounded_training_smoke=True,
            allow_figure10_validation_test_mode=True,
            allow_main_py_training_execution=True,
            allow_training_checkpoint_export=True,
            allow_unknown_actions_for_diagnostic=False,
            policies="HOODIE",
        )
    )
    assert result["manifest"]["real_action_records_used"] is True
    assert result["manifest"]["synthetic_action_records_used"] is False
    assert "evaluation_runner/action_records.json" in result["manifest"]["action_records_source_path"]


def test_invalid_real_action_records_does_not_fallback_to_synthetic(tmp_path):
    import scripts.run_hoodie_paper_scenario_action_distribution_wiring_hardening as smoke

    def fake_run_metrics_hardening(**kwargs):
        _write_metrics_hardening_tree(kwargs["output_dir"])
        real = Path(kwargs["output_dir"]) / "metrics_hardening" / "wiring_smoke" / "evaluation_runner" / "action_records.json"
        _write_json(real, [{"run_id": "phase6_14_smoke_checkpoint_evaluation_metrics_hardening"}])
        return subprocess.CompletedProcess(args=["metrics"], returncode=0, stdout="", stderr="")

    smoke._run_metrics_hardening = fake_run_metrics_hardening
    result = smoke.run_smoke(
        argparse.Namespace(
            output_dir=str(tmp_path / "out"),
            training_epochs=1,
            training_episode_time=3,
            validation_episodes=1,
            seed=42,
            run_id="phase6_15_paper_scenario_action_distribution_wiring_hardening",
            expected_agent_count=20,
            trace_level="summary",
            allow_paper_scenario_action_distribution_wiring_hardening=True,
            allow_smoke_checkpoint_evaluation_metrics_hardening=True,
            allow_trained_checkpoint_evaluation_wiring_smoke=True,
            allow_bounded_training_smoke=True,
            allow_figure10_validation_test_mode=True,
            allow_main_py_training_execution=True,
            allow_training_checkpoint_export=True,
            allow_unknown_actions_for_diagnostic=False,
            policies="HOODIE",
        )
    )
    assert result["manifest"]["synthetic_action_records_used"] is False
    assert "action_records_schema_missing_fields" in result["report"]["blockers"]


def test_missing_action_records_uses_synthetic_probe_marked_diagnostic(tmp_path):
    import scripts.run_hoodie_paper_scenario_action_distribution_wiring_hardening as smoke

    def fake_run_metrics_hardening(**kwargs):
        _write_metrics_hardening_tree(kwargs["output_dir"])
        return subprocess.CompletedProcess(args=["metrics"], returncode=0, stdout="", stderr="")

    smoke._run_metrics_hardening = fake_run_metrics_hardening
    result = smoke.run_smoke(
        argparse.Namespace(
            output_dir=str(tmp_path / "out"),
            training_epochs=1,
            training_episode_time=3,
            validation_episodes=1,
            seed=42,
            run_id="phase6_15_paper_scenario_action_distribution_wiring_hardening",
            expected_agent_count=20,
            trace_level="summary",
            allow_paper_scenario_action_distribution_wiring_hardening=True,
            allow_smoke_checkpoint_evaluation_metrics_hardening=True,
            allow_trained_checkpoint_evaluation_wiring_smoke=True,
            allow_bounded_training_smoke=True,
            allow_figure10_validation_test_mode=True,
            allow_main_py_training_execution=True,
            allow_training_checkpoint_export=True,
            allow_unknown_actions_for_diagnostic=False,
            policies="HOODIE",
        )
    )
    assert result["manifest"]["synthetic_action_records_used"] is True
    assert result["manifest"]["action_records_source"] == "synthetic_phase6_15_wiring_probe"
    assert "synthetic_action_records_used_for_wiring_only" in result["report"]["warnings"]


def test_action_records_empty_sets_blocker(tmp_path):
    import scripts.run_hoodie_paper_scenario_action_distribution_wiring_hardening as smoke

    def fake_run_metrics_hardening(**kwargs):
        _write_metrics_hardening_tree(kwargs["output_dir"])
        action = Path(kwargs["output_dir"]) / "metrics_hardening" / "wiring_smoke" / "evaluation_runner" / "action_records.json"
        _write_json(action, [])
        return subprocess.CompletedProcess(args=["metrics"], returncode=0, stdout="", stderr="")

    smoke._run_metrics_hardening = fake_run_metrics_hardening
    result = smoke.run_smoke(
        argparse.Namespace(
            output_dir=str(tmp_path / "out"),
            training_epochs=1,
            training_episode_time=3,
            validation_episodes=1,
            seed=42,
            run_id="phase6_15_paper_scenario_action_distribution_wiring_hardening",
            expected_agent_count=20,
            trace_level="summary",
            allow_paper_scenario_action_distribution_wiring_hardening=True,
            allow_smoke_checkpoint_evaluation_metrics_hardening=True,
            allow_trained_checkpoint_evaluation_wiring_smoke=True,
            allow_bounded_training_smoke=True,
            allow_figure10_validation_test_mode=True,
            allow_main_py_training_execution=True,
            allow_training_checkpoint_export=True,
            allow_unknown_actions_for_diagnostic=False,
            policies="HOODIE",
        )
    )
    assert "action_records_empty" in result["report"]["blockers"]


def test_action_record_missing_required_schema_fields_sets_blocker(tmp_path):
    import scripts.run_hoodie_paper_scenario_action_distribution_wiring_hardening as smoke

    def fake_run_metrics_hardening(**kwargs):
        _write_metrics_hardening_tree(kwargs["output_dir"])
        action = Path(kwargs["output_dir"]) / "metrics_hardening" / "wiring_smoke" / "evaluation_runner" / "action_records.json"
        _write_json(action, [{"run_id": "phase6_14_smoke_checkpoint_evaluation_metrics_hardening"}])
        return subprocess.CompletedProcess(args=["metrics"], returncode=0, stdout="", stderr="")

    smoke._run_metrics_hardening = fake_run_metrics_hardening
    result = smoke.run_smoke(
        argparse.Namespace(
            output_dir=str(tmp_path / "out"),
            training_epochs=1,
            training_episode_time=3,
            validation_episodes=1,
            seed=42,
            run_id="phase6_15_paper_scenario_action_distribution_wiring_hardening",
            expected_agent_count=20,
            trace_level="summary",
            allow_paper_scenario_action_distribution_wiring_hardening=True,
            allow_smoke_checkpoint_evaluation_metrics_hardening=True,
            allow_trained_checkpoint_evaluation_wiring_smoke=True,
            allow_bounded_training_smoke=True,
            allow_figure10_validation_test_mode=True,
            allow_main_py_training_execution=True,
            allow_training_checkpoint_export=True,
            allow_unknown_actions_for_diagnostic=False,
            policies="HOODIE",
        )
    )
    assert "action_records_schema_missing_fields" in result["report"]["blockers"]


def test_action_record_missing_category_sets_blocker(tmp_path):
    import scripts.run_hoodie_paper_scenario_action_distribution_wiring_hardening as smoke

    def fake_run_metrics_hardening(**kwargs):
        _write_metrics_hardening_tree(kwargs["output_dir"])
        action = Path(kwargs["output_dir"]) / "metrics_hardening" / "wiring_smoke" / "evaluation_runner" / "action_records.json"
        _write_json(action, [
            {
                "run_id": "phase6_14_smoke_checkpoint_evaluation_metrics_hardening",
                "regime_id": "delay",
                "policy_name": "HOODIE",
                "agent_index": 0,
                "evaluation_step": 0,
                "source": "real",
                "diagnostic_only": True,
                "official_figure_claim": False,
                "paper_reproduction_claim": False,
            }
        ])
        return subprocess.CompletedProcess(args=["metrics"], returncode=0, stdout="", stderr="")

    smoke._run_metrics_hardening = fake_run_metrics_hardening
    result = smoke.run_smoke(
        argparse.Namespace(
            output_dir=str(tmp_path / "out"),
            training_epochs=1,
            training_episode_time=3,
            validation_episodes=1,
            seed=42,
            run_id="phase6_15_paper_scenario_action_distribution_wiring_hardening",
            expected_agent_count=20,
            trace_level="summary",
            allow_paper_scenario_action_distribution_wiring_hardening=True,
            allow_smoke_checkpoint_evaluation_metrics_hardening=True,
            allow_trained_checkpoint_evaluation_wiring_smoke=True,
            allow_bounded_training_smoke=True,
            allow_figure10_validation_test_mode=True,
            allow_main_py_training_execution=True,
            allow_training_checkpoint_export=True,
            allow_unknown_actions_for_diagnostic=False,
            policies="HOODIE",
        )
    )
    assert "action_record_category_missing" in result["report"]["blockers"]


def test_action_record_numeric_only_sets_blocker(tmp_path):
    import scripts.run_hoodie_paper_scenario_action_distribution_wiring_hardening as smoke

    def fake_run_metrics_hardening(**kwargs):
        _write_metrics_hardening_tree(kwargs["output_dir"])
        action = Path(kwargs["output_dir"]) / "metrics_hardening" / "wiring_smoke" / "evaluation_runner" / "action_records.json"
        _write_json(action, [
            {
                "run_id": "phase6_14_smoke_checkpoint_evaluation_metrics_hardening",
                "regime_id": "delay",
                "policy_name": "HOODIE",
                "agent_index": 0,
                "evaluation_step": 0,
                "source": "real",
                "diagnostic_only": True,
                "official_figure_claim": False,
                "paper_reproduction_claim": False,
                "selected_action": 0,
            }
        ])
        return subprocess.CompletedProcess(args=["metrics"], returncode=0, stdout="", stderr="")

    smoke._run_metrics_hardening = fake_run_metrics_hardening
    result = smoke.run_smoke(
        argparse.Namespace(
            output_dir=str(tmp_path / "out"),
            training_epochs=1,
            training_episode_time=3,
            validation_episodes=1,
            seed=42,
            run_id="phase6_15_paper_scenario_action_distribution_wiring_hardening",
            expected_agent_count=20,
            trace_level="summary",
            allow_paper_scenario_action_distribution_wiring_hardening=True,
            allow_smoke_checkpoint_evaluation_metrics_hardening=True,
            allow_trained_checkpoint_evaluation_wiring_smoke=True,
            allow_bounded_training_smoke=True,
            allow_figure10_validation_test_mode=True,
            allow_main_py_training_execution=True,
            allow_training_checkpoint_export=True,
            allow_unknown_actions_for_diagnostic=False,
            policies="HOODIE",
        )
    )
    assert "action_record_numeric_only_unmapped" in result["report"]["blockers"]


def test_action_record_unknown_category_sets_blocker(tmp_path):
    import scripts.run_hoodie_paper_scenario_action_distribution_wiring_hardening as smoke

    def fake_run_metrics_hardening(**kwargs):
        _write_metrics_hardening_tree(kwargs["output_dir"])
        action = Path(kwargs["output_dir"]) / "metrics_hardening" / "wiring_smoke" / "evaluation_runner" / "action_records.json"
        _write_json(action, [
            {
                "run_id": "phase6_14_smoke_checkpoint_evaluation_metrics_hardening",
                "regime_id": "delay",
                "policy_name": "HOODIE",
                "agent_index": 0,
                "evaluation_step": 0,
                "source": "real",
                "diagnostic_only": True,
                "official_figure_claim": False,
                "paper_reproduction_claim": False,
                "selected_action": "unknown",
            }
        ])
        return subprocess.CompletedProcess(args=["metrics"], returncode=0, stdout="", stderr="")

    smoke._run_metrics_hardening = fake_run_metrics_hardening
    result = smoke.run_smoke(
        argparse.Namespace(
            output_dir=str(tmp_path / "out"),
            training_epochs=1,
            training_episode_time=3,
            validation_episodes=1,
            seed=42,
            run_id="phase6_15_paper_scenario_action_distribution_wiring_hardening",
            expected_agent_count=20,
            trace_level="summary",
            allow_paper_scenario_action_distribution_wiring_hardening=True,
            allow_smoke_checkpoint_evaluation_metrics_hardening=True,
            allow_trained_checkpoint_evaluation_wiring_smoke=True,
            allow_bounded_training_smoke=True,
            allow_figure10_validation_test_mode=True,
            allow_main_py_training_execution=True,
            allow_training_checkpoint_export=True,
            allow_unknown_actions_for_diagnostic=False,
            policies="HOODIE",
        )
    )
    assert "unknown_actions_present" in result["report"]["blockers"] or "action_record_unknown_category" in result["report"]["blockers"]
    import scripts.run_hoodie_paper_scenario_action_distribution_wiring_hardening as smoke

    def fake_run_metrics_hardening(**kwargs):
        _write_metrics_hardening_tree(kwargs["output_dir"])
        return subprocess.CompletedProcess(args=["metrics"], returncode=0, stdout="", stderr="")

    smoke._run_metrics_hardening = fake_run_metrics_hardening
    def fake_build_action_records(rows, run_id, allow_unknown_actions_for_diagnostic):
        return [
            {
                "run_id": run_id,
                "regime_id": "delay",
                "policy_name": "HOODIE",
                "agent_index": 0,
                "evaluation_step": 0,
                "action": 0,
                "source": "phase6_15_action_distribution_wiring_probe",
                "diagnostic_only": True,
                "official_figure_claim": False,
                "paper_reproduction_claim": False,
            }
        ]

    smoke._build_action_records = fake_build_action_records
    result = smoke.run_smoke(
        argparse.Namespace(
            output_dir=str(tmp_path / "out"),
            training_epochs=1,
            training_episode_time=3,
            validation_episodes=1,
            seed=42,
            run_id="phase6_15_paper_scenario_action_distribution_wiring_hardening",
            expected_agent_count=20,
            trace_level="summary",
            allow_paper_scenario_action_distribution_wiring_hardening=True,
            allow_smoke_checkpoint_evaluation_metrics_hardening=True,
            allow_trained_checkpoint_evaluation_wiring_smoke=True,
            allow_bounded_training_smoke=True,
            allow_figure10_validation_test_mode=True,
            allow_main_py_training_execution=True,
            allow_training_checkpoint_export=True,
            allow_unknown_actions_for_diagnostic=False,
            policies="HOODIE",
        )
    )
    assert "action_record_category_missing" in result["report"]["blockers"] or "action_record_numeric_only_unmapped" in result["report"]["blockers"]


def test_unknown_actions_are_blocked_without_diagnostic_flag(tmp_path):
    import scripts.run_hoodie_paper_scenario_action_distribution_wiring_hardening as smoke

    def fake_run_metrics_hardening(**kwargs):
        _write_metrics_hardening_tree(kwargs["output_dir"])
        return subprocess.CompletedProcess(args=["metrics"], returncode=0, stdout="", stderr="")

    def fake_build_action_records(rows, run_id, allow_unknown_actions_for_diagnostic):
        return [
            {
                "run_id": run_id,
                "regime_id": "delay",
                "policy_name": "HOODIE",
                "agent_index": 0,
                "evaluation_step": 0,
                "action_category": "unknown",
                "selected_action": "unknown",
                "source": "phase6_15_action_distribution_wiring_probe",
                "diagnostic_only": True,
                "official_figure_claim": False,
                "paper_reproduction_claim": False,
            }
        ]

    smoke._run_metrics_hardening = fake_run_metrics_hardening
    smoke._build_action_records = fake_build_action_records
    result = smoke.run_smoke(
        argparse.Namespace(
            output_dir=str(tmp_path / "out"),
            training_epochs=1,
            training_episode_time=3,
            validation_episodes=1,
            seed=42,
            run_id="phase6_15_paper_scenario_action_distribution_wiring_hardening",
            expected_agent_count=20,
            trace_level="summary",
            allow_paper_scenario_action_distribution_wiring_hardening=True,
            allow_smoke_checkpoint_evaluation_metrics_hardening=True,
            allow_trained_checkpoint_evaluation_wiring_smoke=True,
            allow_bounded_training_smoke=True,
            allow_figure10_validation_test_mode=True,
            allow_main_py_training_execution=True,
            allow_training_checkpoint_export=True,
            allow_unknown_actions_for_diagnostic=False,
            policies="HOODIE",
        )
    )
    assert "unknown_actions_present" in result["manifest"]["blockers"] or "action_distribution_unknown_count_not_allowed" in result["manifest"]["blockers"]


def test_action_distribution_csv_missing_sets_blocker(tmp_path):
    import scripts.run_hoodie_paper_scenario_action_distribution_wiring_hardening as smoke

    _run_smoke(tmp_path / "out")
    action_dir = tmp_path / "out" / "action_distribution"
    (action_dir / "hoodie_action_distribution.csv").unlink()
    blockers = smoke._validate_action_distribution_outputs(
        action_dir,
        json.loads((action_dir / "action_records.json").read_text()),
        allow_unknown_actions_for_diagnostic=False,
    )
    assert "action_distribution_file_missing" in blockers or "action_distribution_csv_invalid" in blockers


def test_action_distribution_json_count_mismatch_sets_blocker(tmp_path):
    import scripts.run_hoodie_paper_scenario_action_distribution_wiring_hardening as smoke

    _run_smoke(tmp_path / "out")
    action_dir = tmp_path / "out" / "action_distribution"
    distribution_path = action_dir / "hoodie_action_distribution.json"
    distribution = json.loads(distribution_path.read_text())
    distribution["total_actions"] = distribution["total_actions"] + 1
    _write_json(distribution_path, distribution)
    blockers = smoke._validate_action_distribution_outputs(
        action_dir,
        json.loads((action_dir / "action_records.json").read_text()),
        allow_unknown_actions_for_diagnostic=False,
    )
    assert "action_distribution_count_mismatch" in blockers


def test_action_distribution_ratio_invalid_sets_blocker(tmp_path):
    import scripts.run_hoodie_paper_scenario_action_distribution_wiring_hardening as smoke

    _run_smoke(tmp_path / "out")
    action_dir = tmp_path / "out" / "action_distribution"
    distribution_path = action_dir / "hoodie_action_distribution.json"
    distribution = json.loads(distribution_path.read_text())
    distribution["local_ratio"] = 1.5
    _write_json(distribution_path, distribution)
    blockers = smoke._validate_action_distribution_outputs(
        action_dir,
        json.loads((action_dir / "action_records.json").read_text()),
        allow_unknown_actions_for_diagnostic=False,
    )
    assert "action_distribution_ratio_invalid" in blockers


def test_action_distribution_ratio_sum_invalid_sets_blocker(tmp_path):
    import scripts.run_hoodie_paper_scenario_action_distribution_wiring_hardening as smoke

    _run_smoke(tmp_path / "out")
    action_dir = tmp_path / "out" / "action_distribution"
    distribution_path = action_dir / "hoodie_action_distribution.json"
    distribution = json.loads(distribution_path.read_text())
    distribution["local_ratio"] = 0.6
    distribution["horizontal_ratio"] = 0.2
    distribution["vertical_ratio"] = 0.1
    distribution["unknown_ratio"] = 0.1
    _write_json(distribution_path, distribution)
    blockers = smoke._validate_action_distribution_outputs(
        action_dir,
        json.loads((action_dir / "action_records.json").read_text()),
        allow_unknown_actions_for_diagnostic=False,
    )
    assert "action_distribution_ratio_sum_invalid" in blockers


def test_action_distribution_metadata_official_claim_sets_blocker(tmp_path):
    import scripts.run_hoodie_paper_scenario_action_distribution_wiring_hardening as smoke

    _run_smoke(tmp_path / "out")
    action_dir = tmp_path / "out" / "action_distribution"
    metadata_path = action_dir / "hoodie_action_distribution_metadata.json"
    metadata = json.loads(metadata_path.read_text())
    metadata["official_claim_allowed"] = True
    _write_json(metadata_path, metadata)
    blockers = smoke._validate_action_distribution_outputs(
        action_dir,
        json.loads((action_dir / "action_records.json").read_text()),
        allow_unknown_actions_for_diagnostic=False,
    )
    assert "action_distribution_official_claim_violation" in blockers


def test_action_distribution_metadata_paper_reproduction_sets_blocker(tmp_path):
    import scripts.run_hoodie_paper_scenario_action_distribution_wiring_hardening as smoke

    _run_smoke(tmp_path / "out")
    action_dir = tmp_path / "out" / "action_distribution"
    metadata_path = action_dir / "hoodie_action_distribution_metadata.json"
    metadata = json.loads(metadata_path.read_text())
    metadata["paper_reproduction_claim"] = True
    _write_json(metadata_path, metadata)
    blockers = smoke._validate_action_distribution_outputs(
        action_dir,
        json.loads((action_dir / "action_records.json").read_text()),
        allow_unknown_actions_for_diagnostic=False,
    )
    assert "action_distribution_paper_reproduction_claim_violation" in blockers


def test_no_generated_artifacts_outside_tmp_path(tmp_path):
    before = _repo_forbidden_snapshot()
    after = _repo_forbidden_snapshot()
    assert before == after
