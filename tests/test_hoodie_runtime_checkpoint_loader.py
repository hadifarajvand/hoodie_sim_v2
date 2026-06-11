from __future__ import annotations

import json
import pickle
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
PYTHON = Path(sys.executable)


def _run(args, cwd=ROOT):
    return subprocess.run([str(PYTHON), *args], cwd=cwd, capture_output=True, text=True, check=False)


def _make_scheduler(path: Path):
    from lr_schedulers import constant

    with path.open("wb") as f:
        pickle.dump(constant, f)


def _make_agent(tmp_path: Path, checkpoint_folder: Path):
    pytest.importorskip("torch")
    from decision_makers.agent import Agent

    scheduler = tmp_path / "scheduler.pth"
    _make_scheduler(scheduler)
    import torch

    return Agent(
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
        scheduler_file=str(scheduler),
        loss_function=torch.nn.MSELoss,
        optimizer=torch.optim.Adam,
        checkpoint_folder=str(checkpoint_folder),
        save_model_frequency=10,
        update_weight_percentage=1.0,
        memory_size=10,
        batch_size=2,
        replace_target_iter=5,
    )


def _make_full_model_checkpoint(path: Path):
    pytest.importorskip("torch")
    from decision_makers.agent import DeepQNetwork
    import torch

    model = DeepQNetwork(6, 6, 6, 3, [8], 1, True, 0.0)
    torch.save(model, path)


def _make_state_dict_checkpoint(path: Path):
    pytest.importorskip("torch")
    from decision_makers.agent import DeepQNetwork
    import torch

    model = DeepQNetwork(6, 6, 6, 3, [8], 1, True, 0.0)
    payload = {
        "state_dict": model.state_dict(),
        "model_class": "DeepQNetwork",
        "state_dim": 6,
        "lstm_input_shape": 6,
        "lstm_output_shape": 6,
        "number_of_actions": 3,
        "hidden_layers": [8],
        "lstm_layers": 1,
        "dueling": True,
        "dropout_rate": 0.0,
    }
    torch.save(payload, path)


def _write_metadata(path: Path, checkpoint_format: str = "pytorch_model_file", official_claim_allowed: bool = False):
    path.write_text(
        json.dumps(
            {
                "policy_name": "HOODIE",
                "checkpoint_format": checkpoint_format,
                "official_claim_allowed": official_claim_allowed,
                "runtime_fixture_checkpoint": False,
                "trained_checkpoint": True,
                "created_by": "tests",
                "seed": 42,
                "state_dim": 6,
                "action_count": 3,
                "agent_index": 0,
                "agent_count": 1,
                "paper_contract_ref": "config/paper_table4_contract.json",
                "episode_count": 1,
            },
            indent=2,
            sort_keys=True,
        )
    )


def test_import_loader_without_side_effects():
    result = _run(["-c", "import training.hoodie_runtime_checkpoint_loader as m; print(m.__name__)"])
    assert result.returncode == 0, result.stderr


def test_missing_checkpoint_rejected(tmp_path):
    from training.hoodie_runtime_checkpoint_loader import load_deepqnetwork_checkpoint

    model, report = load_deepqnetwork_checkpoint(tmp_path / "missing.pth")
    assert model is None
    assert report["loadable"] is False
    assert "checkpoint_missing" in report["blockers"]


def test_corrupt_checkpoint_rejected(tmp_path):
    from training.hoodie_runtime_checkpoint_loader import load_deepqnetwork_checkpoint

    p = tmp_path / "bad.pth"
    p.write_text("not torch")
    model, report = load_deepqnetwork_checkpoint(p)
    assert model is None
    assert report["loadable"] is False
    assert "checkpoint_load_failed" in report["blockers"]
    assert "checkpoint_not_loadable" in report["blockers"]


def test_trainer_json_checkpoint_rejected(tmp_path):
    from training.hoodie_runtime_checkpoint_loader import load_deepqnetwork_checkpoint

    p = tmp_path / "agent_0.pth"
    p.write_text(json.dumps({"algorithm": "dqn", "policy_weights": [], "seed": 1}))
    model, report = load_deepqnetwork_checkpoint(p)
    assert model is None
    assert "trainer_json_checkpoint_not_runtime_loadable" in report["blockers"]


def test_full_model_checkpoint_loads(tmp_path):
    pytest.importorskip("torch")
    from training.hoodie_runtime_checkpoint_loader import load_deepqnetwork_checkpoint

    p = tmp_path / "agent_0.pth"
    _make_full_model_checkpoint(p)
    model, report = load_deepqnetwork_checkpoint(p)
    assert model is not None
    assert report["loadable"] is True
    assert report["format"] == "pytorch_model_file"


def test_state_dict_payload_loads(tmp_path):
    pytest.importorskip("torch")
    from training.hoodie_runtime_checkpoint_loader import load_deepqnetwork_checkpoint

    p = tmp_path / "agent_0.pth"
    _make_state_dict_checkpoint(p)
    model, report = load_deepqnetwork_checkpoint(p)
    assert model is not None
    assert report["loadable"] is True
    assert report["format"] == "pytorch_state_dict_payload"


def test_state_dict_payload_missing_state_dict_rejected(tmp_path):
    pytest.importorskip("torch")
    from training.hoodie_runtime_checkpoint_loader import load_deepqnetwork_checkpoint
    import torch

    p = tmp_path / "agent_0.pth"
    torch.save({"model_class": "DeepQNetwork"}, p)
    model, report = load_deepqnetwork_checkpoint(p)
    assert model is None
    assert "missing_state_dict" in report["blockers"]


def test_state_dict_payload_unsupported_model_class_rejected(tmp_path):
    pytest.importorskip("torch")
    from training.hoodie_runtime_checkpoint_loader import load_deepqnetwork_checkpoint
    import torch

    p = tmp_path / "agent_0.pth"
    torch.save(
        {
            "state_dict": {},
            "model_class": "OtherModel",
            "state_dim": 6,
            "lstm_input_shape": 6,
            "lstm_output_shape": 6,
            "number_of_actions": 3,
            "hidden_layers": [8],
            "lstm_layers": 1,
            "dueling": True,
            "dropout_rate": 0.0,
        },
        p,
    )
    model, report = load_deepqnetwork_checkpoint(p)
    assert model is None
    assert "unsupported_model_class" in report["blockers"]


def test_metadata_missing_and_official_claim_true_blockers(tmp_path):
    from training.hoodie_runtime_checkpoint_loader import validate_hoodie_checkpoint_metadata

    missing = validate_hoodie_checkpoint_metadata(tmp_path / "agent_0.pth.meta.json")
    assert "metadata_missing" in missing["blockers"]
    meta = tmp_path / "agent_0.pth.meta.json"
    _write_metadata(meta, official_claim_allowed=True)
    report = validate_hoodie_checkpoint_metadata(meta)
    assert "metadata_official_claim_allowed_true" in report["blockers"]


def test_load_hoodie_checkpoint_with_metadata(tmp_path):
    pytest.importorskip("torch")
    from training.hoodie_runtime_checkpoint_loader import load_hoodie_checkpoint_with_metadata

    p = tmp_path / "agent_0.pth"
    _make_full_model_checkpoint(p)
    _write_metadata(p.with_name("agent_0.pth.meta.json"), checkpoint_format="pytorch_model_file")
    _, report = load_hoodie_checkpoint_with_metadata(p)
    assert report["runtime_loadable"] is True

    p2 = tmp_path / "agent_1.pth"
    _make_state_dict_checkpoint(p2)
    _write_metadata(p2.with_name("agent_1.pth.meta.json"), checkpoint_format="pytorch_state_dict_payload")
    _, report2 = load_hoodie_checkpoint_with_metadata(p2)
    assert report2["runtime_loadable"] is True

    p3 = tmp_path / "agent_2.pth"
    p3.write_text(json.dumps({"algorithm": "dqn", "policy_weights": []}))
    _write_metadata(p3.with_name("agent_2.pth.meta.json"), checkpoint_format="trainer_json_checkpoint")
    _, report3 = load_hoodie_checkpoint_with_metadata(p3)
    assert report3["runtime_loadable"] is False


def test_agent_load_model_supports_both_formats(tmp_path):
    pytest.importorskip("torch")
    full_ckpt = tmp_path / "full.pth"
    state_ckpt = tmp_path / "state.pth"
    _make_full_model_checkpoint(full_ckpt)
    _make_state_dict_checkpoint(state_ckpt)
    _write_metadata(full_ckpt.with_name("full.pth.meta.json"), checkpoint_format="pytorch_model_file")
    _write_metadata(state_ckpt.with_name("state.pth.meta.json"), checkpoint_format="pytorch_state_dict_payload")
    agent = _make_agent(tmp_path, full_ckpt)
    import torch

    assert isinstance(agent.Q_eval_network, torch.nn.Module)
    assert agent.last_checkpoint_load_report["loadable"] is True
    agent.checkpoint_folder = str(state_ckpt)
    agent.load_model()
    assert isinstance(agent.Q_eval_network, torch.nn.Module)
    assert agent.last_checkpoint_load_report["loadable"] is True


def test_agent_load_model_keeps_module_and_reports_missing_sidecar(tmp_path):
    pytest.importorskip("torch")
    full_ckpt = tmp_path / "full_missing_meta.pth"
    _make_full_model_checkpoint(full_ckpt)
    agent = _make_agent(tmp_path, full_ckpt)
    import torch

    assert isinstance(agent.Q_eval_network, torch.nn.Module)
    assert agent.last_checkpoint_load_report["runtime_loadable"] is False
    assert "metadata_missing" in agent.last_checkpoint_load_report["blockers"]


def test_agent_load_model_keeps_initial_network_on_corrupt_checkpoint(tmp_path):
    pytest.importorskip("torch")
    ckpt = tmp_path / "bad.pth"
    ckpt.write_text("bad")
    _write_metadata(ckpt.with_name("bad.pth.meta.json"), checkpoint_format="pytorch_model_file")
    agent = _make_agent(tmp_path, ckpt)
    import torch

    assert isinstance(agent.Q_eval_network, torch.nn.Module)
    assert agent.last_checkpoint_load_report["loadable"] is False
    assert agent.last_checkpoint_load_report["blockers"]


def test_no_generated_artifacts_outside_tmp_path(tmp_path):
    forbidden_names = {
        "hoodie_checkpoint_format_report.json",
    }
    before = {p for p in ROOT.rglob("*") if p.name in forbidden_names or p.suffix in {".pth", ".pt", ".pkl", ".pickle"}}
    assert before == {p for p in before if "artifacts" in str(p) or "outputs" in str(p)}
