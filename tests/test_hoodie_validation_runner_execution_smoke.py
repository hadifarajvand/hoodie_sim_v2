from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
PYTHON = Path(sys.executable)
os.environ.setdefault("TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD", "1")


def _run(args, cwd=ROOT):
    return subprocess.run([str(PYTHON), *args], cwd=cwd, capture_output=True, text=True, check=False)


def _repo_forbidden_snapshot():
    forbidden_suffixes = {".pth", ".pt", ".pkl", ".pickle"}
    forbidden_names = {
        "paper_state_trace.csv",
        "queue_trace.csv",
        "mleo_candidate_latency_trace.csv",
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
    }
    return {p for p in ROOT.rglob("*") if p.suffix in forbidden_suffixes or p.name in forbidden_names}


def _fake_runner_outputs(output_dir: Path, run_id: str, figure10_data_ready: bool = False, delay_rc: int = 0, drop_rc: int = 0):
    runner_output = output_dir / "figure10_runner"
    runner_output.mkdir(parents=True, exist_ok=True)
    readiness = {"figure10_data_ready": figure10_data_ready, "blocking_reasons": []}
    if figure10_data_ready:
        readiness["blocking_reasons"] = ["unexpected"]
    (runner_output / "figure10_policy_metrics_raw.csv").write_text("x\n1\n")
    (runner_output / "figure10_policy_metrics_summary.json").write_text(json.dumps({"summary": True}, indent=2))
    (runner_output / "figure10_policy_readiness.json").write_text(json.dumps(readiness, indent=2, sort_keys=True))
    (runner_output / "figure10_run_config_snapshot.json").write_text(json.dumps({"snapshot": True}, indent=2))
    (runner_output / "figure10_validation_manifest.json").write_text(json.dumps({"manifest": True}, indent=2))
    for regime, rc in {"delay": delay_rc, "drop_ratio": drop_rc}.items():
        log_dir = runner_output / "runs" / run_id / regime / "HOODIE"
        log_dir.mkdir(parents=True, exist_ok=True)
        (log_dir / "main_returncode.txt").write_text(str(rc))
        (log_dir / "main_stdout.txt").write_text("stdout")
        (log_dir / "main_stderr.txt").write_text("")


def test_script_imports_without_running_execution():
    result = _run(["-c", "import scripts.run_hoodie_validation_runner_execution_smoke as m; print(m.__name__)"])
    assert result.returncode == 0, result.stderr
    assert "scripts.run_hoodie_validation_runner_execution_smoke" in result.stdout


def test_missing_allow_controlled_runner_execution_smoke_exits_non_zero(tmp_path):
    result = _run(
        [
            "scripts/run_hoodie_validation_runner_execution_smoke.py",
            "--output-dir",
            str(tmp_path / "out"),
        ]
    )
    assert result.returncode != 0


def test_output_dir_inside_repo_is_refused_and_creates_no_file_or_directory(tmp_path):
    repo_output = ROOT / "artifacts/paper-contract-audit/phase6_7/repo_output"
    if repo_output.exists():
        if repo_output.is_dir():
            shutil.rmtree(repo_output)
        else:
            repo_output.unlink()
    result = _run(
        [
            "scripts/run_hoodie_validation_runner_execution_smoke.py",
            "--output-dir",
            str(repo_output),
            "--allow-controlled-runner-execution-smoke",
            "--allow-runtime-fixture-checkpoints",
        ]
    )
    assert result.returncode != 0
    assert not repo_output.exists()


def test_episodes_zero_exits_non_zero(tmp_path):
    result = _run(
        [
            "scripts/run_hoodie_validation_runner_execution_smoke.py",
            "--output-dir",
            str(tmp_path / "out"),
            "--allow-controlled-runner-execution-smoke",
            "--allow-runtime-fixture-checkpoints",
            "--episodes",
            "0",
        ]
    )
    assert result.returncode != 0


def test_episodes_three_exits_non_zero(tmp_path):
    result = _run(
        [
            "scripts/run_hoodie_validation_runner_execution_smoke.py",
            "--output-dir",
            str(tmp_path / "out"),
            "--allow-controlled-runner-execution-smoke",
            "--allow-runtime-fixture-checkpoints",
            "--episodes",
            "3",
        ]
    )
    assert result.returncode != 0


def test_missing_runtime_fixture_flag_exits_before_creating_checkpoint_fixture(tmp_path):
    out = tmp_path / "out"
    result = _run(
        [
            "scripts/run_hoodie_validation_runner_execution_smoke.py",
            "--output-dir",
            str(out),
            "--allow-controlled-runner-execution-smoke",
        ]
    )
    assert result.returncode != 0
    assert not (out / "runtime_fixture_checkpoints").exists()


def test_successful_controlled_execution_smoke(tmp_path):
    pytest.importorskip("torch")
    out = tmp_path / "out"
    before = _repo_forbidden_snapshot()
    result = _run(
        [
            "scripts/run_hoodie_validation_runner_execution_smoke.py",
            "--output-dir",
            str(out),
            "--episodes",
            "1",
            "--seed",
            "42",
            "--run-id",
            "phase6_7_runner_execution_smoke",
            "--allow-controlled-runner-execution-smoke",
            "--allow-runtime-fixture-checkpoints",
        ]
    )
    assert result.returncode == 0, result.stderr
    manifest = json.loads((out / "validation_runner_execution_smoke_manifest.json").read_text())
    report = json.loads((out / "validation_runner_execution_smoke_report.json").read_text())
    assert manifest["controlled_runner_execution_smoke_run"] is True
    assert manifest["official_validation_run"] is False
    assert manifest["official_200_episode_validation_run"] is False
    assert manifest["training_run"] is False
    assert manifest["checkpoint_training_run"] is False
    assert manifest["runtime_fixture_checkpoints_created"] is True
    assert manifest["runtime_fixture_checkpoints_trained"] is False
    assert manifest["official_claim_allowed"] is False
    assert manifest["figure10_claim"] is False
    assert manifest["non_official_runner_outputs_created"] is True
    assert manifest["official_figure10_outputs_created"] is False
    assert report["controlled_validation_runner_execution_smoke_run"] is True
    assert report["official_validation_run"] is False
    assert report["official_200_episode_validation_run"] is False
    assert report["training_run"] is False
    assert report["checkpoint_training_run"] is False
    assert report["runtime_fixture_checkpoints_created"] is True
    assert report["runtime_fixture_checkpoints_trained"] is False
    assert report["official_claim_allowed"] is False
    assert report["figure10_claim"] is False
    assert report["validation_episode_count"] == 1
    assert report["figure10_data_ready"] is False
    assert report["main_py_subprocesses_seen"] is True
    assert report["main_py_all_returncodes_zero"] is True
    assert (out / "runtime_fixture_checkpoints").is_dir()
    fixture_files = sorted((out / "runtime_fixture_checkpoints").glob("agent_*.pth"))
    assert len(fixture_files) == 20
    assert (out / "figure10_runner" / "figure10_policy_metrics_raw.csv").exists()
    assert (out / "figure10_runner" / "figure10_policy_metrics_summary.json").exists()
    assert (out / "figure10_runner" / "figure10_policy_readiness.json").exists()
    assert (out / "figure10_runner" / "figure10_run_config_snapshot.json").exists()
    assert (out / "figure10_runner" / "figure10_validation_manifest.json").exists()
    for regime in ("delay", "drop_ratio"):
        assert (out / "figure10_runner" / "runs" / "phase6_7_runner_execution_smoke" / regime / "HOODIE" / "main_returncode.txt").exists()
    after = _repo_forbidden_snapshot()
    assert before == after


def test_fixture_checkpoints_are_runtime_loadable(tmp_path):
    pytest.importorskip("torch")
    out = tmp_path / "out"
    result = _run(
        [
            "scripts/run_hoodie_validation_runner_execution_smoke.py",
            "--output-dir",
            str(out),
            "--episodes",
            "1",
            "--seed",
            "42",
            "--allow-controlled-runner-execution-smoke",
            "--allow-runtime-fixture-checkpoints",
        ]
    )
    assert result.returncode == 0, result.stderr
    from training.hoodie_checkpoint_interop import inspect_runtime_torch_checkpoint

    checkpoint = out / "runtime_fixture_checkpoints" / "agent_0.pth"
    inspection = inspect_runtime_torch_checkpoint(checkpoint)
    assert inspection["loadable"] is True
    metadata = json.loads((out / "runtime_fixture_checkpoints" / "agent_0.pth.meta.json").read_text())
    assert metadata["runtime_fixture_checkpoint"] is True
    assert metadata["trained_checkpoint"] is False


def test_runner_failure_is_reported_structurally(tmp_path, monkeypatch):
    pytest.importorskip("torch")
    import scripts.run_hoodie_validation_runner_execution_smoke as smoke
    from subprocess import CompletedProcess

    out = tmp_path / "out"

    def fake_runner(*, output_dir, checkpoint_dir, episodes, seed, run_id, hyperparameters_file):
        _fake_runner_outputs(output_dir, run_id, figure10_data_ready=False, delay_rc=1, drop_rc=1)
        return CompletedProcess(args=["figure10_validation.py"], returncode=1, stdout="boom", stderr="boom")

    monkeypatch.setattr(smoke, "_run_figure10_runner", fake_runner)
    result = smoke.run_smoke(
        argparse.Namespace(
            output_dir=str(out),
            allow_controlled_runner_execution_smoke=True,
            episodes=1,
            seed=42,
            run_id="phase6_7_runner_execution_smoke",
            allow_runtime_fixture_checkpoints=True,
            policies="HOODIE",
        )
    )
    report = json.loads((out / "validation_runner_execution_smoke_report.json").read_text())
    assert "figure10_runner_execution_failed" in report["blockers"]
    assert report["official_claim_allowed"] is False
    assert result["report"]["official_claim_allowed"] is False


def test_unexpected_official_readiness_true_adds_blocker(tmp_path, monkeypatch):
    pytest.importorskip("torch")
    import scripts.run_hoodie_validation_runner_execution_smoke as smoke
    from subprocess import CompletedProcess

    out = tmp_path / "out"

    def fake_runner(*, output_dir, checkpoint_dir, episodes, seed, run_id, hyperparameters_file):
        _fake_runner_outputs(output_dir, run_id, figure10_data_ready=True, delay_rc=0, drop_rc=0)
        return CompletedProcess(args=["figure10_validation.py"], returncode=0, stdout="ok", stderr="")

    monkeypatch.setattr(smoke, "_run_figure10_runner", fake_runner)
    result = smoke.run_smoke(
        argparse.Namespace(
            output_dir=str(out),
            allow_controlled_runner_execution_smoke=True,
            episodes=1,
            seed=42,
            run_id="phase6_7_runner_execution_smoke",
            allow_runtime_fixture_checkpoints=True,
            policies="HOODIE",
        )
    )
    report = json.loads((out / "validation_runner_execution_smoke_report.json").read_text())
    assert "unexpected_official_readiness_true_in_smoke" in report["blockers"]
    assert result["manifest"]["blockers"]
