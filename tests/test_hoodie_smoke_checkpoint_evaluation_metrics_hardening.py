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
    forbidden_suffixes = {".pth", ".pt", ".pkl", ".pickle"}
    forbidden_names = {
        "hoodie_smoke_checkpoint_evaluation_metrics_hardening_manifest.json",
        "hoodie_smoke_checkpoint_evaluation_metrics_hardening_report.json",
        "hoodie_smoke_checkpoint_metrics_contract_summary.json",
        "hoodie_trained_checkpoint_evaluation_wiring_smoke_manifest.json",
        "hoodie_trained_checkpoint_evaluation_wiring_smoke_report.json",
        "hoodie_bounded_small_real_training_smoke_manifest.json",
        "hoodie_bounded_small_real_training_smoke_report.json",
        "hoodie_small_real_training_export_manifest.json",
        "hoodie_small_real_training_smoke_preflight_report.json",
        "controlled_trained_checkpoint_loading_smoke_manifest.json",
        "controlled_trained_checkpoint_loading_smoke_report.json",
        "hoodie_checkpoint_format_report.json",
        "validation_runner_execution_smoke_manifest.json",
        "validation_runner_execution_smoke_report.json",
        "validation_runner_checkpoint_smoke_manifest.json",
        "validation_runner_checkpoint_smoke_report.json",
        "validation_runner_checkpoint_preflight_report.json",
        "figure10_policy_metrics_raw.csv",
        "figure10_policy_metrics_summary.json",
        "figure10_policy_readiness.json",
        "figure10_run_config_snapshot.json",
        "figure10_validation_manifest.json",
        "checkpointed_evaluation_manifest.json",
        "checkpointed_evaluation_report.json",
        "action_records.json",
        "hoodie_action_distribution.csv",
        "hoodie_action_distribution.json",
        "hoodie_action_distribution_metadata.json",
        "smoke_report.json",
        "manifest.json",
        "preflight_report.json",
        "main_stdout.txt",
        "main_stderr.txt",
        "main_returncode.txt",
        "scheduler.pth",
        "paper_state_trace.csv",
        "queue_trace.csv",
        "mleo_candidate_latency_trace.csv",
    }
    return {p for p in ROOT.rglob("*") if p.suffix in forbidden_suffixes or p.name in forbidden_names}


def _load_json(path: Path):
    return json.loads(path.read_text())


def _training_smoke_result(output_dir: Path, *, include_export_manifest: bool = True):
    training_dir = output_dir / "wiring_smoke"
    checkpoint_dir = training_dir / "trained_checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    (checkpoint_dir / "agent_0.pth").write_text("checkpoint")
    (checkpoint_dir / "agent_0.pth.meta.json").write_text(
        json.dumps({"policy_name": "HOODIE", "checkpoint_format": "pytorch_model_file", "official_claim_allowed": False}, indent=2, sort_keys=True)
    )
    if include_export_manifest:
        (training_dir / "hoodie_small_real_training_export_manifest.json").write_text(json.dumps({"blockers": []}, indent=2, sort_keys=True))
    manifest = {
        "blockers": [],
        "official_claim_allowed": False,
    }
    report = {
        "main_returncode": 0,
        "runtime_loader_verified": True,
        "agent_load_model_verified": True,
        "official_claim_allowed": False,
        "blockers": [],
        "actual_agent_count": 1,
    }
    (training_dir / "hoodie_bounded_small_real_training_smoke_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True))
    (training_dir / "hoodie_bounded_small_real_training_smoke_report.json").write_text(json.dumps(report, indent=2, sort_keys=True))
    return {
        "manifest": manifest,
        "report": report,
        "manifest_path": training_dir / "hoodie_bounded_small_real_training_smoke_manifest.json",
        "report_path": training_dir / "hoodie_bounded_small_real_training_smoke_report.json",
        "checkpoint_dir": checkpoint_dir,
    }


def _write_metrics_file(output_dir: Path, *, raw_rows: list[dict[str, object]], summary: dict[str, object] | None = None, readiness: dict[str, object] | None = None, manifest: dict[str, object] | None = None):
    runner = output_dir / "wiring_smoke" / "evaluation_runner"
    runner.mkdir(parents=True, exist_ok=True)
    raw_path = runner / "figure10_policy_metrics_raw.csv"
    if raw_rows:
        with raw_path.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(raw_rows[0].keys()))
            writer.writeheader()
            writer.writerows(raw_rows)
    else:
        raw_path.write_text("")
    if summary is not None:
        (runner / "figure10_policy_metrics_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True))
    if readiness is not None:
        (runner / "figure10_policy_readiness.json").write_text(json.dumps(readiness, indent=2, sort_keys=True))
    if manifest is not None:
        (runner / "figure10_validation_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True))
    (runner / "figure10_run_config_snapshot.json").write_text(json.dumps({"trace_level": "summary"}, indent=2, sort_keys=True))


def _valid_raw_rows(output_dir: Path):
    trace_dir = output_dir / "wiring_smoke" / "evaluation_runner" / "runs" / "phase6_14_smoke_checkpoint_evaluation_metrics_hardening_evaluation" / "delay" / "HOODIE" / "trace"
    trace_dir.mkdir(parents=True, exist_ok=True)
    notes = {
        "regime_id": "delay",
        "regime_source": "paper_contract_or_unverified_runtime_override",
        "average_computation_delay_denominator": 1,
        "drop_ratio_denominator": 1,
        "policy_readiness_status": "ready",
        "pending_tasks_visible": True,
        "timeout_slots": 1,
        "contract_diagnostics": [],
    }
    base = {
        "run_id": "phase6_14_smoke_checkpoint_evaluation_metrics_hardening",
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
        "trace_dir": str(trace_dir),
        "notes_json": json.dumps(notes, sort_keys=True),
    }
    delay = dict(base, regime_id="delay")
    drop = dict(base, regime_id="drop_ratio")
    return [delay, drop]


def test_script_imports_without_running():
    result = _run(["-c", "import scripts.run_hoodie_smoke_checkpoint_evaluation_metrics_hardening as m; print(m.__name__)"])
    assert result.returncode == 0, result.stderr
    assert "scripts.run_hoodie_smoke_checkpoint_evaluation_metrics_hardening" in result.stdout


@pytest.mark.parametrize(
    "missing_flag, extra_args",
    [
        ("--allow-smoke-checkpoint-evaluation-metrics-hardening", ["--allow-trained-checkpoint-evaluation-wiring-smoke", "--allow-bounded-training-smoke", "--allow-figure10-validation-test-mode", "--allow-main-py-training-execution", "--allow-training-checkpoint-export"]),
        ("--allow-trained-checkpoint-evaluation-wiring-smoke", ["--allow-smoke-checkpoint-evaluation-metrics-hardening", "--allow-bounded-training-smoke", "--allow-figure10-validation-test-mode", "--allow-main-py-training-execution", "--allow-training-checkpoint-export"]),
        ("--allow-bounded-training-smoke", ["--allow-smoke-checkpoint-evaluation-metrics-hardening", "--allow-trained-checkpoint-evaluation-wiring-smoke", "--allow-figure10-validation-test-mode", "--allow-main-py-training-execution", "--allow-training-checkpoint-export"]),
        ("--allow-figure10-validation-test-mode", ["--allow-smoke-checkpoint-evaluation-metrics-hardening", "--allow-trained-checkpoint-evaluation-wiring-smoke", "--allow-bounded-training-smoke", "--allow-main-py-training-execution", "--allow-training-checkpoint-export"]),
        ("--allow-main-py-training-execution", ["--allow-smoke-checkpoint-evaluation-metrics-hardening", "--allow-trained-checkpoint-evaluation-wiring-smoke", "--allow-bounded-training-smoke", "--allow-figure10-validation-test-mode", "--allow-training-checkpoint-export"]),
        ("--allow-training-checkpoint-export", ["--allow-smoke-checkpoint-evaluation-metrics-hardening", "--allow-trained-checkpoint-evaluation-wiring-smoke", "--allow-bounded-training-smoke", "--allow-figure10-validation-test-mode", "--allow-main-py-training-execution"]),
    ],
)
def test_missing_flags_exit_non_zero(tmp_path, missing_flag, extra_args):
    result = _run(
        [
            "scripts/run_hoodie_smoke_checkpoint_evaluation_metrics_hardening.py",
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
            "phase6_14_smoke_checkpoint_evaluation_metrics_hardening",
            *extra_args,
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
            "scripts/run_hoodie_smoke_checkpoint_evaluation_metrics_hardening.py",
            "--output-dir",
            str(tmp_path / "out"),
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
    repo_output = ROOT / "artifacts/paper-contract-audit/phase6_14/repo_output"
    if repo_output.exists():
        if repo_output.is_dir():
            shutil.rmtree(repo_output)
        else:
            repo_output.unlink()
    result = _run(
        [
            "scripts/run_hoodie_smoke_checkpoint_evaluation_metrics_hardening.py",
            "--output-dir",
            str(repo_output),
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


def test_successful_metrics_hardening_smoke_runs_only_in_tmp_path(tmp_path):
    out = tmp_path / "out"
    before = _repo_forbidden_snapshot()
    result = _run(
        [
            "scripts/run_hoodie_smoke_checkpoint_evaluation_metrics_hardening.py",
            "--output-dir",
            str(out),
            "--training-epochs",
            "1",
            "--training-episode-time",
            "3",
            "--validation-episodes",
            "1",
            "--seed",
            "42",
            "--run-id",
            "phase6_14_smoke_checkpoint_evaluation_metrics_hardening",
            "--allow-smoke-checkpoint-evaluation-metrics-hardening",
            "--allow-trained-checkpoint-evaluation-wiring-smoke",
            "--allow-bounded-training-smoke",
            "--allow-figure10-validation-test-mode",
            "--allow-main-py-training-execution",
            "--allow-training-checkpoint-export",
        ]
    )
    assert result.returncode == 0, result.stderr
    manifest = _load_json(out / "hoodie_smoke_checkpoint_evaluation_metrics_hardening_manifest.json")
    report = _load_json(out / "hoodie_smoke_checkpoint_evaluation_metrics_hardening_report.json")
    wiring_manifest = _load_json(out / "wiring_smoke" / "hoodie_trained_checkpoint_evaluation_wiring_smoke_manifest.json")
    wiring_report = _load_json(out / "wiring_smoke" / "hoodie_trained_checkpoint_evaluation_wiring_smoke_report.json")
    raw_path = out / "wiring_smoke" / "evaluation_runner" / "figure10_policy_metrics_raw.csv"
    summary_path = out / "wiring_smoke" / "evaluation_runner" / "figure10_policy_metrics_summary.json"
    readiness_path = out / "wiring_smoke" / "evaluation_runner" / "figure10_policy_readiness.json"
    validation_manifest_path = out / "wiring_smoke" / "evaluation_runner" / "figure10_validation_manifest.json"

    assert manifest["metrics_hardening_run"] is True
    assert manifest["wiring_smoke_run"] is True
    assert manifest["validation_policies"] == ["HOODIE"]
    assert manifest["validation_episodes"] == 1
    assert manifest["strict_readiness_used"] is False
    assert manifest["raw_metrics_schema_valid"] is True
    assert manifest["raw_metrics_rows_present"] is True
    assert manifest["raw_metrics_policy_scope_valid"] is True
    assert manifest["raw_metrics_regime_scope_valid"] is True
    assert manifest["raw_metrics_numeric_contract_valid"] is True
    assert manifest["raw_metrics_notes_json_valid"] is True
    assert manifest["summary_metrics_schema_valid"] is True
    assert manifest["readiness_schema_valid"] is True
    assert manifest["manifest_schema_valid"] is True
    assert manifest["metrics_consistency_valid"] is True
    assert manifest["non_official_guard_valid"] is True
    assert manifest["raw_row_count"] == 2
    assert manifest["raw_policy_set"] == ["HOODIE"]
    assert manifest["raw_regime_set"] == ["delay", "drop_ratio"]
    assert manifest["readiness_figure10_data_ready"] is False
    assert manifest["official_claim_allowed"] is False
    assert manifest["paper_reproduction_claim"] is False
    assert report["metrics_hardening_run"] is True
    assert report["wiring_smoke_completed"] is True
    assert report["metrics_files_present"] is True
    assert report["raw_metrics_schema_valid"] is True
    assert report["raw_metrics_numeric_contract_valid"] is True
    assert report["raw_metrics_notes_json_valid"] is True
    assert report["metrics_consistency_valid"] is True
    assert report["figure10_data_ready"] is False
    assert report["official_claim_allowed"] is False
    assert report["paper_reproduction_claim"] is False
    assert report["blockers"] == []
    assert wiring_manifest["trained_checkpoint_evaluation_wiring_smoke_run"] is True
    assert wiring_manifest["evaluation_checkpoints_runtime_loadable"] is True
    assert wiring_manifest["figure10_data_ready"] is False
    assert wiring_report["trained_checkpoint_evaluation_wiring_smoke_run"] is True
    assert wiring_report["evaluation_checkpoints_runtime_loadable"] is True
    assert wiring_report["figure10_data_ready"] is False

    rows = list(csv.DictReader(raw_path.read_text().splitlines()))
    assert len(rows) == 2
    assert sorted({row["policy_name"] for row in rows}) == ["HOODIE"]
    assert sorted({row["regime_id"] for row in rows}) == ["delay", "drop_ratio"]
    assert all(int(row["validation_episode_count"]) == 1 for row in rows)
    assert all(float(row["drop_ratio"]) >= 0.0 and float(row["drop_ratio"]) <= 1.0 for row in rows)
    for row in rows:
        assert row["notes_json"]
        notes = json.loads(row["notes_json"])
        assert notes["regime_id"] == row["regime_id"]
        assert "average_computation_delay_denominator" in notes
        assert "drop_ratio_denominator" in notes
        assert "policy_readiness_status" in notes
        assert "pending_tasks_visible" in notes
    assert summary_path.exists()
    assert readiness_path.exists()
    assert validation_manifest_path.exists()
    assert before == _repo_forbidden_snapshot()


def test_missing_raw_csv_sets_blocker(tmp_path, monkeypatch):
    import scripts.run_hoodie_smoke_checkpoint_evaluation_metrics_hardening as smoke

    def fake_run_wiring_smoke(**kwargs):
        return subprocess.CompletedProcess(args=["wiring"], returncode=0, stdout="", stderr="")

    monkeypatch.setattr(smoke, "_run_wiring_smoke", fake_run_wiring_smoke)
    monkeypatch.setattr(smoke, "_validate_raw_metrics", lambda *args, **kwargs: (False, {}, ["raw_metrics_missing"]))
    monkeypatch.setattr(smoke, "_validate_summary", lambda *args, **kwargs: (True, {}, []))
    monkeypatch.setattr(smoke, "_validate_readiness", lambda *args, **kwargs: (True, {"figure10_data_ready": False}, []))
    monkeypatch.setattr(smoke, "_validate_manifest", lambda *args, **kwargs: (True, {"diagnostic_only": True, "figure10_data_ready": False}, []))
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "scripts/run_hoodie_smoke_checkpoint_evaluation_metrics_hardening.py",
            "--output-dir",
            str(tmp_path / "out"),
            "--allow-smoke-checkpoint-evaluation-metrics-hardening",
            "--allow-trained-checkpoint-evaluation-wiring-smoke",
            "--allow-bounded-training-smoke",
            "--allow-figure10-validation-test-mode",
            "--allow-main-py-training-execution",
            "--allow-training-checkpoint-export",
        ],
    )
    assert smoke.main() == 1
    report = _load_json(tmp_path / "out" / "hoodie_smoke_checkpoint_evaluation_metrics_hardening_report.json")
    assert "raw_metrics_missing" in report["blockers"]


def test_raw_metrics_empty_sets_blocker(tmp_path, monkeypatch):
    import scripts.run_hoodie_smoke_checkpoint_evaluation_metrics_hardening as smoke

    def fake_run_wiring_smoke(**kwargs):
        return subprocess.CompletedProcess(args=["wiring"], returncode=0, stdout="", stderr="")

    monkeypatch.setattr(smoke, "_run_wiring_smoke", fake_run_wiring_smoke)
    monkeypatch.setattr(smoke, "_validate_raw_metrics", lambda *args, **kwargs: (False, {}, ["raw_metrics_empty"]))
    monkeypatch.setattr(smoke, "_validate_summary", lambda *args, **kwargs: (True, {}, []))
    monkeypatch.setattr(smoke, "_validate_readiness", lambda *args, **kwargs: (True, {"figure10_data_ready": False}, []))
    monkeypatch.setattr(smoke, "_validate_manifest", lambda *args, **kwargs: (True, {"diagnostic_only": True, "figure10_data_ready": False}, []))
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "scripts/run_hoodie_smoke_checkpoint_evaluation_metrics_hardening.py",
            "--output-dir",
            str(tmp_path / "out"),
            "--allow-smoke-checkpoint-evaluation-metrics-hardening",
            "--allow-trained-checkpoint-evaluation-wiring-smoke",
            "--allow-bounded-training-smoke",
            "--allow-figure10-validation-test-mode",
            "--allow-main-py-training-execution",
            "--allow-training-checkpoint-export",
        ],
    )
    assert smoke.main() == 1
    report = _load_json(tmp_path / "out" / "hoodie_smoke_checkpoint_evaluation_metrics_hardening_report.json")
    assert "raw_metrics_empty" in report["blockers"]


def test_unexpected_policy_set_sets_blocker(tmp_path, monkeypatch):
    import scripts.run_hoodie_smoke_checkpoint_evaluation_metrics_hardening as smoke

    def fake_run_wiring_smoke(**kwargs):
        return subprocess.CompletedProcess(args=["wiring"], returncode=0, stdout="", stderr="")

    monkeypatch.setattr(smoke, "_run_wiring_smoke", fake_run_wiring_smoke)
    monkeypatch.setattr(smoke, "_validate_raw_metrics", lambda *args, **kwargs: (False, {"policy_set": ["RO"]}, ["raw_metrics_unexpected_policy_set"]))
    monkeypatch.setattr(smoke, "_validate_summary", lambda *args, **kwargs: (True, {}, []))
    monkeypatch.setattr(smoke, "_validate_readiness", lambda *args, **kwargs: (True, {"figure10_data_ready": False}, []))
    monkeypatch.setattr(smoke, "_validate_manifest", lambda *args, **kwargs: (True, {"diagnostic_only": True, "figure10_data_ready": False}, []))
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "scripts/run_hoodie_smoke_checkpoint_evaluation_metrics_hardening.py",
            "--output-dir",
            str(tmp_path / "out"),
            "--allow-smoke-checkpoint-evaluation-metrics-hardening",
            "--allow-trained-checkpoint-evaluation-wiring-smoke",
            "--allow-bounded-training-smoke",
            "--allow-figure10-validation-test-mode",
            "--allow-main-py-training-execution",
            "--allow-training-checkpoint-export",
        ],
    )
    assert smoke.main() == 1
    report = _load_json(tmp_path / "out" / "hoodie_smoke_checkpoint_evaluation_metrics_hardening_report.json")
    assert "raw_metrics_unexpected_policy_set" in report["blockers"]


def test_unexpected_regime_set_sets_blocker(tmp_path, monkeypatch):
    import scripts.run_hoodie_smoke_checkpoint_evaluation_metrics_hardening as smoke

    def fake_run_wiring_smoke(**kwargs):
        return subprocess.CompletedProcess(args=["wiring"], returncode=0, stdout="", stderr="")

    monkeypatch.setattr(smoke, "_run_wiring_smoke", fake_run_wiring_smoke)
    monkeypatch.setattr(smoke, "_validate_raw_metrics", lambda *args, **kwargs: (False, {"regime_set": ["delay"]}, ["raw_metrics_unexpected_regime_set"]))
    monkeypatch.setattr(smoke, "_validate_summary", lambda *args, **kwargs: (True, {}, []))
    monkeypatch.setattr(smoke, "_validate_readiness", lambda *args, **kwargs: (True, {"figure10_data_ready": False}, []))
    monkeypatch.setattr(smoke, "_validate_manifest", lambda *args, **kwargs: (True, {"diagnostic_only": True, "figure10_data_ready": False}, []))
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "scripts/run_hoodie_smoke_checkpoint_evaluation_metrics_hardening.py",
            "--output-dir",
            str(tmp_path / "out"),
            "--allow-smoke-checkpoint-evaluation-metrics-hardening",
            "--allow-trained-checkpoint-evaluation-wiring-smoke",
            "--allow-bounded-training-smoke",
            "--allow-figure10-validation-test-mode",
            "--allow-main-py-training-execution",
            "--allow-training-checkpoint-export",
        ],
    )
    assert smoke.main() == 1
    report = _load_json(tmp_path / "out" / "hoodie_smoke_checkpoint_evaluation_metrics_hardening_report.json")
    assert "raw_metrics_unexpected_regime_set" in report["blockers"]


def test_invalid_drop_ratio_sets_blocker(tmp_path, monkeypatch):
    import scripts.run_hoodie_smoke_checkpoint_evaluation_metrics_hardening as smoke

    def fake_run_wiring_smoke(**kwargs):
        return subprocess.CompletedProcess(args=["wiring"], returncode=0, stdout="", stderr="")

    monkeypatch.setattr(smoke, "_run_wiring_smoke", fake_run_wiring_smoke)
    monkeypatch.setattr(smoke, "_validate_raw_metrics", lambda *args, **kwargs: (False, {}, ["raw_metrics_invalid_drop_ratio"]))
    monkeypatch.setattr(smoke, "_validate_summary", lambda *args, **kwargs: (True, {}, []))
    monkeypatch.setattr(smoke, "_validate_readiness", lambda *args, **kwargs: (True, {"figure10_data_ready": False}, []))
    monkeypatch.setattr(smoke, "_validate_manifest", lambda *args, **kwargs: (True, {"diagnostic_only": True, "figure10_data_ready": False}, []))
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "scripts/run_hoodie_smoke_checkpoint_evaluation_metrics_hardening.py",
            "--output-dir",
            str(tmp_path / "out"),
            "--allow-smoke-checkpoint-evaluation-metrics-hardening",
            "--allow-trained-checkpoint-evaluation-wiring-smoke",
            "--allow-bounded-training-smoke",
            "--allow-figure10-validation-test-mode",
            "--allow-main-py-training-execution",
            "--allow-training-checkpoint-export",
        ],
    )
    assert smoke.main() == 1
    report = _load_json(tmp_path / "out" / "hoodie_smoke_checkpoint_evaluation_metrics_hardening_report.json")
    assert "raw_metrics_invalid_drop_ratio" in report["blockers"]


def test_inconsistent_task_counts_sets_blocker(tmp_path, monkeypatch):
    import scripts.run_hoodie_smoke_checkpoint_evaluation_metrics_hardening as smoke

    def fake_run_wiring_smoke(**kwargs):
        return subprocess.CompletedProcess(args=["wiring"], returncode=0, stdout="", stderr="")

    monkeypatch.setattr(smoke, "_run_wiring_smoke", fake_run_wiring_smoke)
    monkeypatch.setattr(smoke, "_validate_raw_metrics", lambda *args, **kwargs: (False, {}, ["raw_metrics_task_count_inconsistent"]))
    monkeypatch.setattr(smoke, "_validate_summary", lambda *args, **kwargs: (True, {}, []))
    monkeypatch.setattr(smoke, "_validate_readiness", lambda *args, **kwargs: (True, {"figure10_data_ready": False}, []))
    monkeypatch.setattr(smoke, "_validate_manifest", lambda *args, **kwargs: (True, {"diagnostic_only": True, "figure10_data_ready": False}, []))
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "scripts/run_hoodie_smoke_checkpoint_evaluation_metrics_hardening.py",
            "--output-dir",
            str(tmp_path / "out"),
            "--allow-smoke-checkpoint-evaluation-metrics-hardening",
            "--allow-trained-checkpoint-evaluation-wiring-smoke",
            "--allow-bounded-training-smoke",
            "--allow-figure10-validation-test-mode",
            "--allow-main-py-training-execution",
            "--allow-training-checkpoint-export",
        ],
    )
    assert smoke.main() == 1
    report = _load_json(tmp_path / "out" / "hoodie_smoke_checkpoint_evaluation_metrics_hardening_report.json")
    assert "raw_metrics_task_count_inconsistent" in report["blockers"]


def test_invalid_notes_json_sets_blocker(tmp_path, monkeypatch):
    import scripts.run_hoodie_smoke_checkpoint_evaluation_metrics_hardening as smoke

    def fake_run_wiring_smoke(**kwargs):
        return subprocess.CompletedProcess(args=["wiring"], returncode=0, stdout="", stderr="")

    monkeypatch.setattr(smoke, "_run_wiring_smoke", fake_run_wiring_smoke)
    monkeypatch.setattr(smoke, "_validate_raw_metrics", lambda *args, **kwargs: (False, {}, ["raw_metrics_notes_json_invalid"]))
    monkeypatch.setattr(smoke, "_validate_summary", lambda *args, **kwargs: (True, {}, []))
    monkeypatch.setattr(smoke, "_validate_readiness", lambda *args, **kwargs: (True, {"figure10_data_ready": False}, []))
    monkeypatch.setattr(smoke, "_validate_manifest", lambda *args, **kwargs: (True, {"diagnostic_only": True, "figure10_data_ready": False}, []))
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "scripts/run_hoodie_smoke_checkpoint_evaluation_metrics_hardening.py",
            "--output-dir",
            str(tmp_path / "out"),
            "--allow-smoke-checkpoint-evaluation-metrics-hardening",
            "--allow-trained-checkpoint-evaluation-wiring-smoke",
            "--allow-bounded-training-smoke",
            "--allow-figure10-validation-test-mode",
            "--allow-main-py-training-execution",
            "--allow-training-checkpoint-export",
        ],
    )
    assert smoke.main() == 1
    report = _load_json(tmp_path / "out" / "hoodie_smoke_checkpoint_evaluation_metrics_hardening_report.json")
    assert "raw_metrics_notes_json_invalid" in report["blockers"]


def test_trace_dir_outside_output_dir_sets_blocker(tmp_path, monkeypatch):
    import scripts.run_hoodie_smoke_checkpoint_evaluation_metrics_hardening as smoke

    def fake_run_wiring_smoke(**kwargs):
        return subprocess.CompletedProcess(args=["wiring"], returncode=0, stdout="", stderr="")

    monkeypatch.setattr(smoke, "_run_wiring_smoke", fake_run_wiring_smoke)
    monkeypatch.setattr(smoke, "_validate_raw_metrics", lambda *args, **kwargs: (False, {}, ["raw_metrics_trace_dir_outside_output_dir"]))
    monkeypatch.setattr(smoke, "_validate_summary", lambda *args, **kwargs: (True, {}, []))
    monkeypatch.setattr(smoke, "_validate_readiness", lambda *args, **kwargs: (True, {"figure10_data_ready": False}, []))
    monkeypatch.setattr(smoke, "_validate_manifest", lambda *args, **kwargs: (True, {"diagnostic_only": True, "figure10_data_ready": False}, []))
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "scripts/run_hoodie_smoke_checkpoint_evaluation_metrics_hardening.py",
            "--output-dir",
            str(tmp_path / "out"),
            "--allow-smoke-checkpoint-evaluation-metrics-hardening",
            "--allow-trained-checkpoint-evaluation-wiring-smoke",
            "--allow-bounded-training-smoke",
            "--allow-figure10-validation-test-mode",
            "--allow-main-py-training-execution",
            "--allow-training-checkpoint-export",
        ],
    )
    assert smoke.main() == 1
    report = _load_json(tmp_path / "out" / "hoodie_smoke_checkpoint_evaluation_metrics_hardening_report.json")
    assert "raw_metrics_trace_dir_outside_output_dir" in report["blockers"]


def test_readiness_true_sets_blocker(tmp_path, monkeypatch):
    import scripts.run_hoodie_smoke_checkpoint_evaluation_metrics_hardening as smoke

    def fake_run_wiring_smoke(**kwargs):
        return subprocess.CompletedProcess(args=["wiring"], returncode=0, stdout="", stderr="")

    monkeypatch.setattr(smoke, "_run_wiring_smoke", fake_run_wiring_smoke)
    monkeypatch.setattr(smoke, "_validate_raw_metrics", lambda *args, **kwargs: (True, {"policy_set": ["HOODIE"], "regime_set": ["delay", "drop_ratio"], "row_count": 2}, []))
    monkeypatch.setattr(smoke, "_validate_summary", lambda *args, **kwargs: (True, {"registry": {"active_policy_set": ["HOODIE"]}, "validation_episode_count": 1, "figure10_data_ready": False, "no_metric_rows_generated": False}, []))
    monkeypatch.setattr(smoke, "_validate_readiness", lambda *args, **kwargs: (False, {"figure10_data_ready": True}, ["unexpected_figure10_data_ready_true"]))
    monkeypatch.setattr(smoke, "_validate_manifest", lambda *args, **kwargs: (True, {"diagnostic_only": True, "figure10_data_ready": False}, []))
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "scripts/run_hoodie_smoke_checkpoint_evaluation_metrics_hardening.py",
            "--output-dir",
            str(tmp_path / "out"),
            "--allow-smoke-checkpoint-evaluation-metrics-hardening",
            "--allow-trained-checkpoint-evaluation-wiring-smoke",
            "--allow-bounded-training-smoke",
            "--allow-figure10-validation-test-mode",
            "--allow-main-py-training-execution",
            "--allow-training-checkpoint-export",
        ],
    )
    assert smoke.main() == 1
    report = _load_json(tmp_path / "out" / "hoodie_smoke_checkpoint_evaluation_metrics_hardening_report.json")
    assert "unexpected_figure10_data_ready_true" in report["blockers"]


def test_official_claim_true_sets_blocker(tmp_path, monkeypatch):
    import scripts.run_hoodie_smoke_checkpoint_evaluation_metrics_hardening as smoke

    def fake_run_wiring_smoke(**kwargs):
        return subprocess.CompletedProcess(args=["wiring"], returncode=0, stdout="", stderr="")

    monkeypatch.setattr(smoke, "_run_wiring_smoke", fake_run_wiring_smoke)
    monkeypatch.setattr(smoke, "_validate_raw_metrics", lambda *args, **kwargs: (True, {"policy_set": ["HOODIE"], "regime_set": ["delay", "drop_ratio"], "row_count": 2}, []))
    monkeypatch.setattr(smoke, "_validate_summary", lambda *args, **kwargs: (True, {"registry": {"active_policy_set": ["HOODIE"]}, "validation_episode_count": 1, "figure10_data_ready": False, "no_metric_rows_generated": False}, []))
    monkeypatch.setattr(smoke, "_validate_readiness", lambda *args, **kwargs: (True, {"figure10_data_ready": False}, []))
    monkeypatch.setattr(smoke, "_validate_manifest", lambda *args, **kwargs: (False, {"diagnostic_only": True, "figure10_data_ready": False, "paper_performance_claims_made": True}, ["official_claim_violation"]))
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "scripts/run_hoodie_smoke_checkpoint_evaluation_metrics_hardening.py",
            "--output-dir",
            str(tmp_path / "out"),
            "--allow-smoke-checkpoint-evaluation-metrics-hardening",
            "--allow-trained-checkpoint-evaluation-wiring-smoke",
            "--allow-bounded-training-smoke",
            "--allow-figure10-validation-test-mode",
            "--allow-main-py-training-execution",
            "--allow-training-checkpoint-export",
        ],
    )
    assert smoke.main() == 1
    report = _load_json(tmp_path / "out" / "hoodie_smoke_checkpoint_evaluation_metrics_hardening_report.json")
    assert "official_claim_violation" in report["blockers"]


def test_paper_reproduction_true_sets_blocker(tmp_path, monkeypatch):
    import scripts.run_hoodie_smoke_checkpoint_evaluation_metrics_hardening as smoke

    def fake_run_wiring_smoke(**kwargs):
        return subprocess.CompletedProcess(args=["wiring"], returncode=0, stdout="", stderr="")

    monkeypatch.setattr(smoke, "_run_wiring_smoke", fake_run_wiring_smoke)
    monkeypatch.setattr(smoke, "_validate_raw_metrics", lambda *args, **kwargs: (True, {"policy_set": ["HOODIE"], "regime_set": ["delay", "drop_ratio"], "row_count": 2}, []))
    monkeypatch.setattr(smoke, "_validate_summary", lambda *args, **kwargs: (True, {"registry": {"active_policy_set": ["HOODIE"]}, "validation_episode_count": 1, "figure10_data_ready": False, "no_metric_rows_generated": False}, []))
    monkeypatch.setattr(smoke, "_validate_readiness", lambda *args, **kwargs: (True, {"figure10_data_ready": False}, []))
    monkeypatch.setattr(smoke, "_validate_manifest", lambda *args, **kwargs: (False, {"diagnostic_only": True, "figure10_data_ready": False, "paper_performance_claims_made": True}, ["paper_reproduction_claim_violation"]))
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "scripts/run_hoodie_smoke_checkpoint_evaluation_metrics_hardening.py",
            "--output-dir",
            str(tmp_path / "out"),
            "--allow-smoke-checkpoint-evaluation-metrics-hardening",
            "--allow-trained-checkpoint-evaluation-wiring-smoke",
            "--allow-bounded-training-smoke",
            "--allow-figure10-validation-test-mode",
            "--allow-main-py-training-execution",
            "--allow-training-checkpoint-export",
        ],
    )
    assert smoke.main() == 1
    report = _load_json(tmp_path / "out" / "hoodie_smoke_checkpoint_evaluation_metrics_hardening_report.json")
    assert "paper_reproduction_claim_violation" in report["blockers"]


def test_no_generated_artifacts_outside_tmp_path(tmp_path):
    before = _repo_forbidden_snapshot()
    after = _repo_forbidden_snapshot()
    assert before == after
