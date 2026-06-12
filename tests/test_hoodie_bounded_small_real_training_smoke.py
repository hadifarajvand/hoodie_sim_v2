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
        "hoodie_bounded_small_real_training_smoke_manifest.json",
        "hoodie_bounded_small_real_training_smoke_report.json",
        "hoodie_small_real_training_export_manifest.json",
        "main_stdout.txt",
        "main_stderr.txt",
        "main_returncode.txt",
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
        "hoodie_small_real_training_smoke_preflight_report.json",
        "hoodie_small_real_training_export_manifest.json",
        "hoodie_checkpoint_format_report.json",
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
    result = _run(["-c", "import scripts.run_hoodie_bounded_small_real_training_smoke as m; print(m.__name__)"])
    assert result.returncode == 0, result.stderr
    assert "scripts.run_hoodie_bounded_small_real_training_smoke" in result.stdout


def test_missing_allow_flag_exits_non_zero(tmp_path):
    result = _run(["scripts/run_hoodie_bounded_small_real_training_smoke.py", "--output-dir", str(tmp_path / "out")])
    assert result.returncode != 0


def test_output_inside_repo_is_refused_and_creates_no_file(tmp_path):
    repo_output = ROOT / "artifacts/paper-contract-audit/phase6_12/repo_output"
    if repo_output.exists():
        if repo_output.is_dir():
            shutil.rmtree(repo_output)
        else:
            repo_output.unlink()
    result = _run(
        [
            "scripts/run_hoodie_bounded_small_real_training_smoke.py",
            "--output-dir",
            str(repo_output),
            "--allow-bounded-small-real-training-smoke",
            "--allow-main-py-training-execution",
            "--allow-training-checkpoint-export",
        ]
    )
    assert result.returncode != 0
    assert not repo_output.exists()


@pytest.mark.parametrize("flag,value", [("--epochs", "0"), ("--epochs", "2"), ("--episode-time", "0"), ("--episode-time", "4"), ("--expected-agent-count", "0")])
def test_bounds_exits_non_zero(tmp_path, flag, value):
    result = _run(
        [
            "scripts/run_hoodie_bounded_small_real_training_smoke.py",
            "--output-dir",
            str(tmp_path / "out"),
            "--allow-bounded-small-real-training-smoke",
            "--allow-main-py-training-execution",
            "--allow-training-checkpoint-export",
            flag,
            value,
        ]
    )
    assert result.returncode != 0


def test_unsupported_checkpoint_format_exits_non_zero(tmp_path):
    result = _run(
        [
            "scripts/run_hoodie_bounded_small_real_training_smoke.py",
            "--output-dir",
            str(tmp_path / "out"),
            "--allow-bounded-small-real-training-smoke",
            "--allow-main-py-training-execution",
            "--allow-training-checkpoint-export",
            "--checkpoint-format",
            "pytorch_state_dict_payload",
        ]
    )
    assert result.returncode != 0


def test_main_failure_is_reported_structurally(tmp_path, monkeypatch):
    import scripts.run_hoodie_bounded_small_real_training_smoke as smoke
    from subprocess import CompletedProcess

    out = tmp_path / "out"

    def fake_main(*, output_dir, seed, epochs, trace_level, hyperparameters_file, config_file):
        return CompletedProcess(args=["main.py"], returncode=1, stdout="boom", stderr="boom")

    monkeypatch.setattr(smoke, "_run_main_training", fake_main)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "scripts/run_hoodie_bounded_small_real_training_smoke.py",
            "--output-dir",
            str(out),
            "--epochs",
            "1",
            "--episode-time",
            "3",
            "--seed",
            "42",
            "--run-id",
            "phase6_12_bounded_small_real_training_smoke",
            "--allow-bounded-small-real-training-smoke",
            "--allow-main-py-training-execution",
            "--allow-training-checkpoint-export",
        ],
    )
    assert smoke.main() == 1
    report = json.loads((out / "hoodie_bounded_small_real_training_smoke_report.json").read_text())
    assert "main_py_failed" in report["blockers"]


def test_successful_smoke_runs_and_exports_runtime_checkpoints(tmp_path):
    pytest.importorskip("torch")
    import torch
    from decision_makers.agent import Agent
    from training.hoodie_runtime_checkpoint_loader import load_hoodie_checkpoint_with_metadata

    out = tmp_path / "out"
    before = _repo_forbidden_snapshot()
    result = _run(
        [
            "scripts/run_hoodie_bounded_small_real_training_smoke.py",
            "--output-dir",
            str(out),
            "--epochs",
            "1",
            "--episode-time",
            "3",
            "--seed",
            "42",
            "--run-id",
            "phase6_12_bounded_small_real_training_smoke",
            "--allow-bounded-small-real-training-smoke",
            "--allow-main-py-training-execution",
            "--allow-training-checkpoint-export",
        ]
    )
    assert result.returncode == 0, result.stderr

    manifest = json.loads((out / "hoodie_bounded_small_real_training_smoke_manifest.json").read_text())
    report = json.loads((out / "hoodie_bounded_small_real_training_smoke_report.json").read_text())
    export_manifest = json.loads((out / "hoodie_small_real_training_export_manifest.json").read_text())

    assert manifest["bounded_small_real_training_smoke_run"] is True
    assert manifest["main_py_called"] is True
    assert manifest["main_py_training_execution_run"] is True
    assert manifest["training_execution_run"] is True
    assert manifest["simulation_rerun"] is False
    assert manifest["official_training_run"] is False
    assert manifest["full_training_run"] is False
    assert manifest["paper_training_run"] is False
    assert manifest["official_200_episode_validation_run"] is False
    assert manifest["official_claim_allowed"] is False
    assert manifest["checkpoint_export_requested"] is True
    assert manifest["checkpoint_export_performed"] is True
    assert manifest["runtime_loader_verified"] is True
    assert manifest["agent_load_model_verified"] is True
    assert manifest["main_returncode"] == 0
    assert manifest["actual_agent_count"] == 20
    assert manifest["figure10_runner_outputs_present"] is False
    assert export_manifest["blockers"] == []
    assert report["bounded_small_real_training_smoke_run"] is True
    assert report["main_py_called"] is True
    assert report["training_execution_run"] is True
    assert report["official_training_run"] is False
    assert report["full_training_run"] is False
    assert report["paper_training_run"] is False
    assert report["official_200_episode_validation_run"] is False
    assert report["official_claim_allowed"] is False
    assert report["checkpoint_export_performed"] is True
    assert report["runtime_loader_verified"] is True
    assert report["agent_load_model_verified"] is True
    assert report["main_returncode"] == 0
    assert report["figure10_runner_outputs_present"] is False
    assert len(report["generated_checkpoints"]) == 20

    checkpoint_dir = out / "trained_checkpoints"
    assert checkpoint_dir.is_dir()
    for agent_index in range(20):
        checkpoint = checkpoint_dir / f"agent_{agent_index}.pth"
        meta = checkpoint_dir / f"agent_{agent_index}.pth.meta.json"
        assert checkpoint.exists()
        assert meta.exists()
        metadata = json.loads(meta.read_text())
        assert metadata["policy_name"] == "HOODIE"
        assert metadata["small_real_training_smoke_candidate"] is True
        assert metadata["trained_checkpoint"] is True
        assert metadata["trained_checkpoint_scope"] == "small_real_training_smoke_candidate_only"
        assert metadata["paper_training_run"] is False
        assert metadata["full_training_run"] is False
        assert metadata["paper_grade_5000_episode_training_run"] is False
        assert metadata["official_claim_allowed"] is False
        assert metadata["paper_reproduction_claim"] is False
        model, loader_report = load_hoodie_checkpoint_with_metadata(checkpoint)
        assert model is not None
        assert loader_report["runtime_loadable"] is True
        assert loader_report["checkpoint_report"]["format"] == "pytorch_model_file"
        assert loader_report["metadata_report"]["blockers"] == []

    scheduler_file = out / "main_logs" / "scheduler.pth"
    agent = Agent(
        id=0,
        state_dimensions=6,
        lstm_shape=6,
        number_of_actions=3,
        hidden_layers=[8],
        lstm_layers=1,
        lstm_time_step=1,
        dropout_rate=0.0,
        device="cpu",
        epsilon=0.0,
        epsilon_decrement=0.0,
        epsilon_end=0.0,
        gamma=0.99,
        learning_rate=1e-6,
        scheduler_file=str(scheduler_file),
        loss_function=torch.nn.MSELoss,
        optimizer=torch.optim.Adam,
        checkpoint_folder=str(checkpoint_dir / "agent_0.pth"),
        save_model_frequency=10,
        update_weight_percentage=1.0,
        memory_size=10,
        batch_size=2,
        replace_target_iter=5,
    )
    assert isinstance(agent.Q_eval_network, torch.nn.Module)
    assert agent.last_checkpoint_load_report["runtime_loadable"] is True

    assert not (out / "figure10_runner").exists()
    after = _repo_forbidden_snapshot()
    assert before == after

