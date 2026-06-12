from __future__ import annotations

import json
import os
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
        "hoodie_small_real_training_smoke_preflight_report.json",
        "hoodie_small_real_training_export_manifest.json",
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
    }
    return {p for p in ROOT.rglob("*") if p.suffix in forbidden_suffixes or p.name in forbidden_names}


def _make_dummy_agent(tmp_path):
    pytest.importorskip("torch")
    import torch
    from decision_makers.agent import DeepQNetwork

    class DummyAgent:
        pass

    agent = DummyAgent()
    agent.state_dimensions = 6
    agent.number_of_actions = 3
    agent.Q_eval_network = DeepQNetwork(
        state_dimensions=6,
        lstm_input_shape=6,
        lstm_output_shape=6,
        number_of_actions=3,
        hidden_layers=[8],
        lstm_layers=1,
        dueling=True,
        dropout_rate=0.0,
    )
    return agent


def test_module_imports_without_side_effects():
    result = _run(["-c", "import training.hoodie_training_checkpoint_export as m; print(m.__name__)"])
    assert result.returncode == 0, result.stderr
    assert "training.hoodie_training_checkpoint_export" in result.stdout


def test_build_training_checkpoint_metadata(tmp_path):
    from training.hoodie_training_checkpoint_export import build_training_checkpoint_metadata

    metadata = build_training_checkpoint_metadata(
        agent_index=0,
        agent_count=20,
        checkpoint_format="pytorch_model_file",
        seed=42,
        state_dim=6,
        action_count=3,
        episode_count=1,
        training_step_count=2,
        run_id="phase6_11",
        phase="6.11",
        created_by="test",
    )
    assert metadata["policy_name"] == "HOODIE"
    assert metadata["trained_checkpoint"] is True
    assert metadata["trained_checkpoint_scope"] == "small_real_training_smoke_candidate_only"
    assert metadata["paper_training_run"] is False
    assert metadata["full_training_run"] is False
    assert metadata["paper_grade_5000_episode_training_run"] is False
    assert metadata["official_claim_allowed"] is False
    assert metadata["paper_reproduction_claim"] is False


def test_export_agent_runtime_checkpoint_writes_model_and_sidecar(tmp_path):
    pytest.importorskip("torch")
    from training.hoodie_training_checkpoint_export import build_training_checkpoint_metadata, export_agent_runtime_checkpoint
    from training.hoodie_runtime_checkpoint_loader import load_hoodie_checkpoint_with_metadata

    agent = _make_dummy_agent(tmp_path)
    checkpoint_path = tmp_path / "agent_0.pth"
    metadata = build_training_checkpoint_metadata(
        agent_index=0,
        agent_count=1,
        checkpoint_format="pytorch_model_file",
        seed=42,
        state_dim=6,
        action_count=3,
        episode_count=1,
        training_step_count=2,
        run_id="phase6_11",
        phase="6.11",
        created_by="test",
    )
    report = export_agent_runtime_checkpoint(agent, checkpoint_path, metadata, checkpoint_format="pytorch_model_file")
    assert report["checkpoint_written"] is True
    assert report["metadata_written"] is True
    assert checkpoint_path.exists()
    assert checkpoint_path.with_name(checkpoint_path.name + ".meta.json").exists()
    model, load_report = load_hoodie_checkpoint_with_metadata(checkpoint_path)
    assert model is not None
    assert load_report["runtime_loadable"] is True


def test_export_refuses_repo_relative_output_path(tmp_path):
    from training.hoodie_training_checkpoint_export import export_training_checkpoints

    agent = _make_dummy_agent(tmp_path)
    report = export_training_checkpoints([agent], ROOT / "artifacts/paper-contract-audit/phase6_11/repo_output", run_id="x", seed=1, episode_count=1, training_step_count=1)
    assert "repo_output_refused" in report["blockers"]


def test_export_rejects_unsupported_format(tmp_path):
    from training.hoodie_training_checkpoint_export import build_training_checkpoint_metadata, export_agent_runtime_checkpoint

    agent = _make_dummy_agent(tmp_path)
    metadata = build_training_checkpoint_metadata(
        agent_index=0,
        agent_count=1,
        checkpoint_format="trainer_json_checkpoint",
        seed=42,
        state_dim=6,
        action_count=3,
        episode_count=1,
        training_step_count=2,
        run_id="phase6_11",
        phase="6.11",
        created_by="test",
    )
    report = export_agent_runtime_checkpoint(agent, tmp_path / "bad.pth", metadata, checkpoint_format="trainer_json_checkpoint")
    assert "unsupported_checkpoint_format" in report["blockers"]


def test_export_rejects_official_claim_true(tmp_path):
    from training.hoodie_training_checkpoint_export import build_training_checkpoint_metadata, export_agent_runtime_checkpoint

    agent = _make_dummy_agent(tmp_path)
    metadata = build_training_checkpoint_metadata(
        agent_index=0,
        agent_count=1,
        checkpoint_format="pytorch_model_file",
        seed=42,
        state_dim=6,
        action_count=3,
        episode_count=1,
        training_step_count=2,
        run_id="phase6_11",
        phase="6.11",
        created_by="test",
    )
    metadata["official_claim_allowed"] = True
    report = export_agent_runtime_checkpoint(agent, tmp_path / "bad.pth", metadata, checkpoint_format="pytorch_model_file")
    assert "official_claim_violation" in report["blockers"]


def test_export_training_checkpoints_multiple_agents(tmp_path):
    pytest.importorskip("torch")
    from training.hoodie_training_checkpoint_export import export_training_checkpoints

    agents = [_make_dummy_agent(tmp_path), _make_dummy_agent(tmp_path)]
    out = tmp_path / "export"
    report = export_training_checkpoints(agents, out, run_id="phase6_11", seed=42, episode_count=1, training_step_count=2)
    assert report["all_checkpoints_written"] is True
    assert report["all_metadata_written"] is True
    assert (out / "agent_0.pth").exists()
    assert (out / "agent_0.pth.meta.json").exists()
    assert (out / "agent_1.pth").exists()
    assert (out / "agent_1.pth.meta.json").exists()


def test_no_generated_artifacts_outside_tmp_path(tmp_path):
    before = _repo_forbidden_snapshot()
    from training.hoodie_training_checkpoint_export import export_training_checkpoints

    agents = [_make_dummy_agent(tmp_path)]
    report = export_training_checkpoints(agents, tmp_path / "export", run_id="phase6_11", seed=42, episode_count=1, training_step_count=1)
    assert report["all_checkpoints_written"] is True
    after = _repo_forbidden_snapshot()
    assert before == after
