import json
from pathlib import Path
import tempfile
import pytest

from training.hoodie_checkpoint_interop import (
    detect_checkpoint_format,
    inspect_trainer_json_checkpoint,
    inspect_runtime_torch_checkpoint,
    assess_hoodie_checkpoint_dir,
    write_checkpoint_metadata_sidecar,
)


def test_missing_checkpoint(tmp_path):
    p = tmp_path / "nope"
    res = detect_checkpoint_format(p)
    assert res["format"] == "missing"


def test_trainer_json_detection_and_inspect(tmp_path):
    payload = {
        "algorithm": "dqn",
        "seed": 42,
        "state_dim": 10,
        "action_count": 3,
        "policy_weights": [[0.1] * 3] * 10,
    }
    p = tmp_path / "model.chkpt"
    p.write_text(json.dumps(payload))
    fmt = detect_checkpoint_format(p)
    assert fmt["format"] == "trainer_json_checkpoint"
    info = inspect_trainer_json_checkpoint(p)
    assert info["algorithm"] == "dqn"
    assert info["state_dim"] == 10


def test_inspect_runtime_torch_checkpoint_safe(tmp_path):
    # create a small dict and save via json to simulate non-torch file
    p = tmp_path / "fake.pth"
    p.write_text(json.dumps({"not": "torch"}))
    # inspect should not raise; may report error when torch.load fails
    info = inspect_runtime_torch_checkpoint(p)
    assert "error" in info or isinstance(info.get("loadable"), bool)


def test_assess_checkpoint_dir_and_sidecar(tmp_path):
    d = tmp_path / "ckptdir"
    d.mkdir()
    # create trainer chkpt only
    (d / "phase3_model.chkpt").write_text(json.dumps({"policy_weights": []}))
    res = assess_hoodie_checkpoint_dir(d, expected_agent_count=1)
    assert "trainer_json_checkpoint_not_runtime_loadable" in res.get("issues", [])
    # sidecar writer
    fake_model = d / "agent_0.pth"
    fake_model.write_text("x")

    # missing sidecar should be reported
    res2 = assess_hoodie_checkpoint_dir(d, expected_agent_count=1)
    assert "missing_metadata_sidecar" in res2.get("issues", [])

    # write a valid metadata sidecar
    meta = {
        "policy_name": "HOODIE",
        "checkpoint_format": "pytorch_model_file",
        "created_by": "unit-test",
        "seed": 42,
        "state_dim": 5,
        "action_count": 3,
        "paper_contract_ref": "paper_table4_contract.json",
        "episode_count": 0,
    }
    meta_path = write_checkpoint_metadata_sidecar(fake_model, meta)
    assert meta_path.exists()


def test_write_metadata_sidecar_validates_required_fields(tmp_path):
    f = tmp_path / "agent_0.pth"
    f.write_text("x")
    bad_meta = {
        "policy_name": "HOODIE",
        "checkpoint_format": "pytorch_model_file",
        "created_by": "unit-test",
        # missing seed/state_dim/action_count and paper_contract_ref/episode_count
    }
    import pytest

    with pytest.raises(ValueError):
        write_checkpoint_metadata_sidecar(f, bad_meta)
