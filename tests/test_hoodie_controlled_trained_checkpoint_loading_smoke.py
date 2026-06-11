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
        "controlled_trained_checkpoint_loading_smoke_manifest.json",
        "controlled_trained_checkpoint_loading_smoke_report.json",
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


def test_script_imports_without_running():
    result = _run(["-c", "import scripts.run_hoodie_controlled_trained_checkpoint_loading_smoke as m; print(m.__name__)"])
    assert result.returncode == 0, result.stderr
    assert "scripts.run_hoodie_controlled_trained_checkpoint_loading_smoke" in result.stdout


def test_missing_allow_controlled_trained_checkpoint_smoke_exits_non_zero(tmp_path):
    result = _run(
        [
            "scripts/run_hoodie_controlled_trained_checkpoint_loading_smoke.py",
            "--output-dir",
            str(tmp_path / "out"),
            "--allow-synthetic-training-step",
        ]
    )
    assert result.returncode != 0


def test_missing_allow_synthetic_training_step_exits_non_zero(tmp_path):
    result = _run(
        [
            "scripts/run_hoodie_controlled_trained_checkpoint_loading_smoke.py",
            "--output-dir",
            str(tmp_path / "out"),
            "--allow-controlled-trained-checkpoint-smoke",
        ]
    )
    assert result.returncode != 0


def test_output_inside_repo_is_refused_and_creates_no_file_or_directory(tmp_path):
    repo_output = ROOT / "artifacts/paper-contract-audit/phase6_9/repo_output"
    if repo_output.exists():
        if repo_output.is_dir():
            shutil.rmtree(repo_output)
        else:
            repo_output.unlink()
    result = _run(
        [
            "scripts/run_hoodie_controlled_trained_checkpoint_loading_smoke.py",
            "--output-dir",
            str(repo_output),
            "--allow-controlled-trained-checkpoint-smoke",
            "--allow-synthetic-training-step",
        ]
    )
    assert result.returncode != 0
    assert not repo_output.exists()


def test_episodes_zero_exits_non_zero(tmp_path):
    result = _run(
        [
            "scripts/run_hoodie_controlled_trained_checkpoint_loading_smoke.py",
            "--output-dir",
            str(tmp_path / "out"),
            "--allow-controlled-trained-checkpoint-smoke",
            "--allow-synthetic-training-step",
            "--episodes",
            "0",
        ]
    )
    assert result.returncode != 0


def test_episodes_three_exits_non_zero(tmp_path):
    result = _run(
        [
            "scripts/run_hoodie_controlled_trained_checkpoint_loading_smoke.py",
            "--output-dir",
            str(tmp_path / "out"),
            "--allow-controlled-trained-checkpoint-smoke",
            "--allow-synthetic-training-step",
            "--episodes",
            "3",
        ]
    )
    assert result.returncode != 0


def test_synthetic_steps_zero_exits_non_zero(tmp_path):
    result = _run(
        [
            "scripts/run_hoodie_controlled_trained_checkpoint_loading_smoke.py",
            "--output-dir",
            str(tmp_path / "out"),
            "--allow-controlled-trained-checkpoint-smoke",
            "--allow-synthetic-training-step",
            "--synthetic-steps",
            "0",
        ]
    )
    assert result.returncode != 0


def test_synthetic_steps_three_exits_non_zero(tmp_path):
    result = _run(
        [
            "scripts/run_hoodie_controlled_trained_checkpoint_loading_smoke.py",
            "--output-dir",
            str(tmp_path / "out"),
            "--allow-controlled-trained-checkpoint-smoke",
            "--allow-synthetic-training-step",
            "--synthetic-steps",
            "3",
        ]
    )
    assert result.returncode != 0


def test_unsupported_checkpoint_format_exits_non_zero(tmp_path):
    result = _run(
        [
            "scripts/run_hoodie_controlled_trained_checkpoint_loading_smoke.py",
            "--output-dir",
            str(tmp_path / "out"),
            "--allow-controlled-trained-checkpoint-smoke",
            "--allow-synthetic-training-step",
            "--checkpoint-format",
            "trainer_json_checkpoint",
        ]
    )
    assert result.returncode != 0


def test_successful_smoke_state_dict_payload(tmp_path):
    pytest.importorskip("torch")
    out = tmp_path / "out"
    before = _repo_forbidden_snapshot()
    result = _run(
        [
            "scripts/run_hoodie_controlled_trained_checkpoint_loading_smoke.py",
            "--output-dir",
            str(out),
            "--episodes",
            "1",
            "--synthetic-steps",
            "1",
            "--seed",
            "42",
            "--run-id",
            "phase6_9_controlled_trained_checkpoint_smoke",
            "--allow-controlled-trained-checkpoint-smoke",
            "--allow-synthetic-training-step",
            "--checkpoint-format",
            "pytorch_state_dict_payload",
        ]
    )
    assert result.returncode == 0, result.stderr
    manifest = json.loads((out / "controlled_trained_checkpoint_loading_smoke_manifest.json").read_text())
    report = json.loads((out / "controlled_trained_checkpoint_loading_smoke_report.json").read_text())
    assert manifest["controlled_synthetic_training_smoke_run"] is True
    assert manifest["trained_checkpoint_created"] is True
    assert manifest["trained_checkpoint_scope"] == "synthetic_controlled_smoke_only"
    assert manifest["official_claim_allowed"] is False
    assert manifest["paper_training_run"] is False
    assert manifest["full_training_run"] is False
    assert report["controlled_trained_checkpoint_loading_smoke_run"] is True
    assert report["controlled_synthetic_training_smoke_run"] is True
    assert report["paper_training_run"] is False
    assert report["full_training_run"] is False
    assert report["official_validation_run"] is False
    assert report["official_200_episode_validation_run"] is False
    assert report["official_claim_allowed"] is False
    assert report["paper_reproduction_claim"] is False
    assert report["figure10_claim"] is False
    assert report["figure10_data_ready"] is False
    assert report["trained_checkpoint_scope"] == "synthetic_controlled_smoke_only"
    assert report["validation_episode_count"] == 1
    assert report["runtime_loader_accepted_checkpoint"] is True
    assert report["agent_load_model_verified"] is True
    assert report["runner_completed"] is True
    assert report["main_py_subprocesses_seen"] is True
    assert report["main_py_all_returncodes_zero"] is True
    assert report["runner_loaded_checkpoint_from_stdout"] is True
    assert report["runner_sidecars_present"] is True
    assert (out / "controlled_trained_checkpoints").is_dir()
    fixture_files = sorted((out / "controlled_trained_checkpoints").glob("agent_*.pth"))
    assert len(fixture_files) == 20
    for agent_index in range(20):
        checkpoint = out / "controlled_trained_checkpoints" / f"agent_{agent_index}.pth"
        meta = out / "controlled_trained_checkpoints" / f"agent_{agent_index}.pth.meta.json"
        assert checkpoint.exists()
        assert meta.exists()
        metadata = json.loads(meta.read_text())
        assert metadata["controlled_training_smoke"] is True
        assert metadata["trained_checkpoint"] is True
        assert metadata["paper_training_run"] is False
        assert metadata["official_claim_allowed"] is False
    for regime in ("delay", "drop_ratio"):
        regime_dir = out / "figure10_runner" / "runs" / "phase6_9_controlled_trained_checkpoint_smoke" / regime / "HOODIE"
        assert (regime_dir / "main_returncode.txt").exists()
        assert (regime_dir / "main_stdout.txt").exists()
        assert "model weights loaded" in (regime_dir / "main_stdout.txt").read_text()
        log_dir = regime_dir / "logs"
        assert (log_dir / "agent_0.pth").exists()
        assert (log_dir / "agent_0.pth.meta.json").exists()
    after = _repo_forbidden_snapshot()
    assert before == after


def test_successful_smoke_model_file_format_helper(tmp_path):
    pytest.importorskip("torch")
    import scripts.run_hoodie_controlled_trained_checkpoint_loading_smoke as smoke
    from training.hoodie_runtime_checkpoint_loader import load_hoodie_checkpoint_with_metadata

    out = tmp_path / "helper"
    checkpoint_dir, summaries, losses, warnings = smoke._build_controlled_trained_checkpoints(
        output_dir=out,
        seed=42,
        checkpoint_format="pytorch_model_file",
        agent_count=20,
        synthetic_steps=1,
        episodes=1,
    )
    assert len(summaries) == 20
    assert len(losses) == 20
    assert warnings == []
    model, report = load_hoodie_checkpoint_with_metadata(checkpoint_dir / "agent_0.pth")
    assert model is not None
    assert report["runtime_loadable"] is True
    verified, load_report = smoke._verify_agent_load_model(checkpoint_dir / "agent_0.pth", out)
    assert verified is True
    assert "runtime_loadable" in load_report


def test_runner_failure_is_reported_structurally(tmp_path, monkeypatch):
    pytest.importorskip("torch")
    import scripts.run_hoodie_controlled_trained_checkpoint_loading_smoke as smoke
    from subprocess import CompletedProcess

    out = tmp_path / "out"

    def fake_runner(*, output_dir, checkpoint_dir, episodes, seed, run_id, hyperparameters_file):
        runner_output = output_dir / "figure10_runner"
        runner_output.mkdir(parents=True, exist_ok=True)
        (runner_output / "figure10_policy_metrics_raw.csv").write_text("x\n1\n")
        (runner_output / "figure10_policy_metrics_summary.json").write_text("{}")
        (runner_output / "figure10_policy_readiness.json").write_text(json.dumps({"figure10_data_ready": False}))
        (runner_output / "figure10_run_config_snapshot.json").write_text("{}")
        (runner_output / "figure10_validation_manifest.json").write_text("{}")
        for regime in ("delay", "drop_ratio"):
            regime_dir = runner_output / "runs" / run_id / regime / "HOODIE"
            regime_dir.mkdir(parents=True, exist_ok=True)
            (regime_dir / "main_returncode.txt").write_text("1")
            (regime_dir / "main_stdout.txt").write_text("model weights loaded")
            (regime_dir / "main_stderr.txt").write_text("boom")
            log_dir = regime_dir / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            (log_dir / "agent_0.pth").write_text("checkpoint")
            (log_dir / "agent_0.pth.meta.json").write_text("{}")
        return CompletedProcess(args=["figure10_validation.py"], returncode=1, stdout="boom", stderr="boom")

    monkeypatch.setattr(smoke, "_run_figure10_runner", fake_runner)
    result = smoke.run_smoke(
        argparse.Namespace(
            output_dir=str(out),
            allow_controlled_trained_checkpoint_smoke=True,
            allow_synthetic_training_step=True,
            episodes=1,
            synthetic_steps=1,
            seed=42,
            run_id="phase6_9_controlled_trained_checkpoint_smoke",
            checkpoint_format="pytorch_state_dict_payload",
        )
    )
    report = json.loads((out / "controlled_trained_checkpoint_loading_smoke_report.json").read_text())
    assert "figure10_runner_execution_failed" in report["blockers"]
    assert report["official_claim_allowed"] is False
    assert result["report"]["official_claim_allowed"] is False


def test_unexpected_official_readiness_true_adds_blocker(tmp_path, monkeypatch):
    pytest.importorskip("torch")
    import scripts.run_hoodie_controlled_trained_checkpoint_loading_smoke as smoke
    from subprocess import CompletedProcess

    out = tmp_path / "out"

    def fake_runner(*, output_dir, checkpoint_dir, episodes, seed, run_id, hyperparameters_file):
        runner_output = output_dir / "figure10_runner"
        runner_output.mkdir(parents=True, exist_ok=True)
        (runner_output / "figure10_policy_metrics_raw.csv").write_text("x\n1\n")
        (runner_output / "figure10_policy_metrics_summary.json").write_text("{}")
        (runner_output / "figure10_policy_readiness.json").write_text(json.dumps({"figure10_data_ready": True}))
        (runner_output / "figure10_run_config_snapshot.json").write_text("{}")
        (runner_output / "figure10_validation_manifest.json").write_text("{}")
        for regime in ("delay", "drop_ratio"):
            regime_dir = runner_output / "runs" / run_id / regime / "HOODIE"
            regime_dir.mkdir(parents=True, exist_ok=True)
            (regime_dir / "main_returncode.txt").write_text("0")
            (regime_dir / "main_stdout.txt").write_text("model weights loaded")
            (regime_dir / "main_stderr.txt").write_text("")
            log_dir = regime_dir / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            (log_dir / "agent_0.pth").write_text("checkpoint")
            (log_dir / "agent_0.pth.meta.json").write_text("{}")
        return CompletedProcess(args=["figure10_validation.py"], returncode=0, stdout="ok", stderr="")

    monkeypatch.setattr(smoke, "_run_figure10_runner", fake_runner)
    result = smoke.run_smoke(
        argparse.Namespace(
            output_dir=str(out),
            allow_controlled_trained_checkpoint_smoke=True,
            allow_synthetic_training_step=True,
            episodes=1,
            synthetic_steps=1,
            seed=42,
            run_id="phase6_9_controlled_trained_checkpoint_smoke",
            checkpoint_format="pytorch_state_dict_payload",
        )
    )
    report = json.loads((out / "controlled_trained_checkpoint_loading_smoke_report.json").read_text())
    assert "unexpected_official_readiness_true_in_smoke" in report["blockers"]
    assert result["manifest"]["figure10_data_ready"] is False


def test_runner_stdout_without_load_message_is_reported(tmp_path, monkeypatch):
    pytest.importorskip("torch")
    import scripts.run_hoodie_controlled_trained_checkpoint_loading_smoke as smoke
    from subprocess import CompletedProcess

    out = tmp_path / "out"

    def fake_runner(*, output_dir, checkpoint_dir, episodes, seed, run_id, hyperparameters_file):
        runner_output = output_dir / "figure10_runner"
        runner_output.mkdir(parents=True, exist_ok=True)
        (runner_output / "figure10_policy_metrics_raw.csv").write_text("x\n1\n")
        (runner_output / "figure10_policy_metrics_summary.json").write_text("{}")
        (runner_output / "figure10_policy_readiness.json").write_text(json.dumps({"figure10_data_ready": False}))
        (runner_output / "figure10_run_config_snapshot.json").write_text("{}")
        (runner_output / "figure10_validation_manifest.json").write_text("{}")
        for regime in ("delay", "drop_ratio"):
            regime_dir = runner_output / "runs" / run_id / regime / "HOODIE"
            regime_dir.mkdir(parents=True, exist_ok=True)
            (regime_dir / "main_returncode.txt").write_text("0")
            (regime_dir / "main_stdout.txt").write_text("no load message")
            (regime_dir / "main_stderr.txt").write_text("")
            log_dir = regime_dir / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            (log_dir / "agent_0.pth").write_text("checkpoint")
            (log_dir / "agent_0.pth.meta.json").write_text("{}")
        return CompletedProcess(args=["figure10_validation.py"], returncode=0, stdout="ok", stderr="")

    monkeypatch.setattr(smoke, "_run_figure10_runner", fake_runner)
    result = smoke.run_smoke(
        argparse.Namespace(
            output_dir=str(out),
            allow_controlled_trained_checkpoint_smoke=True,
            allow_synthetic_training_step=True,
            episodes=1,
            synthetic_steps=1,
            seed=42,
            run_id="phase6_9_controlled_trained_checkpoint_smoke",
            checkpoint_format="pytorch_state_dict_payload",
        )
    )
    report = json.loads((out / "controlled_trained_checkpoint_loading_smoke_report.json").read_text())
    assert "runner_checkpoint_load_not_observed" in report["blockers"]
    assert result["report"]["official_claim_allowed"] is False


def test_no_generated_artifacts_outside_tmp_path(tmp_path):
    before = _repo_forbidden_snapshot()
    out = tmp_path / "out"
    result = _run(
        [
            "scripts/run_hoodie_controlled_trained_checkpoint_loading_smoke.py",
            "--output-dir",
            str(out),
            "--episodes",
            "1",
            "--synthetic-steps",
            "1",
            "--seed",
            "42",
            "--allow-controlled-trained-checkpoint-smoke",
            "--allow-synthetic-training-step",
        ]
    )
    assert result.returncode == 0, result.stderr
    after = _repo_forbidden_snapshot()
    assert before == after
