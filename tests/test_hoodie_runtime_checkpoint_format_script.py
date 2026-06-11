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
    import torch

    scheduler = tmp_path / "scheduler.pth"
    _make_scheduler(scheduler)
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


def _full_model_ckpt(path: Path):
    pytest.importorskip("torch")
    from decision_makers.agent import DeepQNetwork
    import torch

    torch.save(DeepQNetwork(6, 6, 6, 3, [8], 1, True, 0.0), path)


def _state_dict_ckpt(path: Path):
    pytest.importorskip("torch")
    from decision_makers.agent import DeepQNetwork
    import torch

    payload = {
        "state_dict": DeepQNetwork(6, 6, 6, 3, [8], 1, True, 0.0).state_dict(),
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


def _meta(path: Path, checkpoint_format: str = "pytorch_model_file", official: bool = False):
    path.write_text(
        json.dumps(
            {
                "policy_name": "HOODIE",
                "checkpoint_format": checkpoint_format,
                "official_claim_allowed": official,
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


def test_imports_without_running():
    result = _run(["-c", "import scripts.check_hoodie_runtime_checkpoint_format as m; print(m.__name__)"])
    assert result.returncode == 0, result.stderr


def test_missing_allow_flag_exits_non_zero(tmp_path):
    result = _run(
        [
            "scripts/check_hoodie_runtime_checkpoint_format.py",
            "--checkpoint-dir",
            str(tmp_path / "ckpt"),
            "--agent-count",
            "1",
        ]
    )
    assert result.returncode != 0


def test_agent_count_zero_exits_non_zero(tmp_path):
    result = _run(
        [
            "scripts/check_hoodie_runtime_checkpoint_format.py",
            "--checkpoint-dir",
            str(tmp_path / "ckpt"),
            "--agent-count",
            "0",
            "--allow-format-check",
        ]
    )
    assert result.returncode != 0


def test_output_inside_repo_refused(tmp_path):
    repo_output = ROOT / "artifacts/paper-contract-audit/phase6_8/hoodie_checkpoint_format_report.json"
    if repo_output.exists():
        repo_output.unlink()
    result = _run(
        [
            "scripts/check_hoodie_runtime_checkpoint_format.py",
            "--checkpoint-dir",
            str(tmp_path / "ckpt"),
            "--agent-count",
            "1",
            "--allow-format-check",
            "--output",
            str(repo_output),
        ]
    )
    assert result.returncode != 0
    assert not repo_output.exists()


def test_full_model_checkpoint_passes(tmp_path):
    pytest.importorskip("torch")
    ckpt = tmp_path / "ckpt"
    ckpt.mkdir()
    p = ckpt / "agent_0.pth"
    _full_model_ckpt(p)
    _meta(p.with_name("agent_0.pth.meta.json"), "pytorch_model_file")
    result = _run(
        [
            "scripts/check_hoodie_runtime_checkpoint_format.py",
            "--checkpoint-dir",
            str(ckpt),
            "--agent-count",
            "1",
            "--allow-format-check",
        ]
    )
    assert result.returncode == 0, result.stderr


def test_state_dict_payload_passes(tmp_path):
    pytest.importorskip("torch")
    ckpt = tmp_path / "ckpt"
    ckpt.mkdir()
    p = ckpt / "agent_0.pth"
    _state_dict_ckpt(p)
    _meta(p.with_name("agent_0.pth.meta.json"), "pytorch_state_dict_payload")
    result = _run(
        [
            "scripts/check_hoodie_runtime_checkpoint_format.py",
            "--checkpoint-dir",
            str(ckpt),
            "--agent-count",
            "1",
            "--allow-format-check",
        ]
    )
    assert result.returncode == 0, result.stderr


def test_trainer_json_checkpoint_rejected(tmp_path):
    ckpt = tmp_path / "ckpt"
    ckpt.mkdir()
    p = ckpt / "agent_0.pth"
    p.write_text(json.dumps({"algorithm": "dqn", "policy_weights": []}))
    _meta(p.with_name("agent_0.pth.meta.json"), "trainer_json_checkpoint")
    out = tmp_path / "report.json"
    result = _run(
        [
            "scripts/check_hoodie_runtime_checkpoint_format.py",
            "--checkpoint-dir",
            str(ckpt),
            "--agent-count",
            "1",
            "--allow-format-check",
            "--output",
            str(out),
        ]
    )
    assert result.returncode != 0
    report = json.loads(out.read_text())
    assert "trainer_json_checkpoint_not_runtime_loadable" in report["blockers"]


def test_corrupt_checkpoint_rejected_and_reported(tmp_path):
    ckpt = tmp_path / "ckpt"
    ckpt.mkdir()
    p = ckpt / "agent_0.pth"
    p.write_text("bad")
    _meta(p.with_name("agent_0.pth.meta.json"), "pytorch_model_file")
    out = tmp_path / "report.json"
    result = _run(
        [
            "scripts/check_hoodie_runtime_checkpoint_format.py",
            "--checkpoint-dir",
            str(ckpt),
            "--agent-count",
            "1",
            "--allow-format-check",
            "--output",
            str(out),
        ]
    )
    assert result.returncode != 0
    report = json.loads(out.read_text())
    assert report["all_agents_runtime_loadable"] is False
    assert report["agent_reports"][0]["runtime_loadable"] is False


def test_all_agents_runtime_loadable_true_only_when_all_valid(tmp_path):
    pytest.importorskip("torch")
    ckpt = tmp_path / "ckpt"
    ckpt.mkdir()
    for idx in range(2):
        p = ckpt / f"agent_{idx}.pth"
        _full_model_ckpt(p)
        _meta(p.with_name(f"agent_{idx}.pth.meta.json"), "pytorch_model_file")
    out = tmp_path / "report.json"
    result = _run(
        [
            "scripts/check_hoodie_runtime_checkpoint_format.py",
            "--checkpoint-dir",
            str(ckpt),
            "--agent-count",
            "2",
            "--allow-format-check",
            "--output",
            str(out),
        ]
    )
    assert result.returncode == 0, result.stderr
    report = json.loads(out.read_text())
    assert report["all_agents_runtime_loadable"] is True


def test_no_generated_artifacts_outside_tmp_path(tmp_path):
    before = {p for p in ROOT.rglob("*") if p.name == "hoodie_checkpoint_format_report.json"}
    assert before == {p for p in before if "artifacts" in str(p)}
