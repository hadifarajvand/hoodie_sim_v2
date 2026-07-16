from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import torch

from src.hoodie.experiments import checkpoint_storage_patch
from src.hoodie.storage import checkpoints
from src.hoodie.storage.checkpoints import (
    CheckpointStoragePolicy,
    hydrate_replay_snapshot,
    save_bounded_checkpoint,
)


GIB = 1024**3
MIB = 1024**2


def _policy() -> CheckpointStoragePolicy:
    return CheckpointStoragePolicy(
        max_checkpoints_per_job=1,
        minimum_free_bytes=GIB,
        minimum_free_fraction=0.01,
        maximum_job_bytes=128 * MIB,
        estimated_checkpoint_bytes=MIB,
    )


def _checkpoint_state(*, episode: int = 1) -> dict[str, object]:
    return {
        "schema_version": 3,
        "checkpoint_id": f"checkpoint-{episode}",
        "next_episode": episode,
        "episode_rewards": [float(index) for index in range(episode)],
        "policy_state": {
            "policy_name": "HOODIE",
            "policy_kind": "distributed_hoodie",
            "backend_type": "cpu",
            "device_string": "cpu",
            "agents": {
                "1": {
                    "use_lstm": True,
                    "learner": {
                        "learner_kind": "destination_recurrent_ddqn",
                        "action_order": ["local", "cloud"],
                        "online_state_dict": {"weight": torch.ones(2, 2)},
                        "target_state_dict": {"weight": torch.zeros(2, 2)},
                        "optimizer_state_dict": {"state": {}, "param_groups": []},
                        "replay_buffer": {
                            "capacity": 4,
                            "warmup_size": 1,
                            "batch_size": 1,
                            "seed": 7,
                            "rng_state": None,
                            "items": ["transition"],
                        },
                        "rng_state": (3, (1, 2, 3), None),
                        "training_steps": episode,
                        "target_update_steps": 0,
                    },
                }
            },
        },
        "backend_type": "cpu",
        "device_string": "cpu",
    }


def _save(job_dir: Path, checkpoint_id: str, *, final: bool = False):
    return save_bounded_checkpoint(
        job_dir=job_dir,
        checkpoint_id=checkpoint_id,
        checkpoint_state=_checkpoint_state(episode=int(checkpoint_id.rsplit("-", 1)[-1])),
        metadata={"checkpoint_id": checkpoint_id, "training_job_id": "train"},
        final=final,
        policy=_policy(),
    )


def test_replay_is_external_and_hydrates_for_resume(tmp_path: Path) -> None:
    job_dir = tmp_path / "job"
    result = _save(job_dir, "checkpoint-1")

    stored = torch.load(result["checkpoint_path"], map_location="cpu", weights_only=False)
    learner = stored["policy_state"]["agents"]["1"]["learner"]
    assert "replay_buffer" not in learner
    assert "optimizer_state_dict" in learner
    assert stored["resume_capable"] is True
    assert (job_dir / "resume_state" / "replay_latest.pt").is_file()

    hydrated = hydrate_replay_snapshot(job_dir, stored)
    assert hydrated["policy_state"]["agents"]["1"]["learner"]["replay_buffer"]["items"] == ["transition"]


def test_only_latest_checkpoint_and_replay_snapshot_are_retained(tmp_path: Path) -> None:
    job_dir = tmp_path / "job"
    _save(job_dir, "checkpoint-1")
    _save(job_dir, "checkpoint-2")

    directories = [path.name for path in (job_dir / "internal_checkpoints").iterdir() if path.is_dir()]
    assert directories == ["checkpoint-2"]
    replay_metadata = json.loads(
        (job_dir / "resume_state" / "replay_latest.metadata.json").read_text(encoding="utf-8")
    )
    assert replay_metadata["checkpoint_id"] == "checkpoint-2"
    retention = json.loads(
        (job_dir / "checkpoint_retention_manifest.json").read_text(encoding="utf-8")
    )
    assert retention["maximum_retained_checkpoints"] == 1
    assert retention["replay_snapshot_count"] == 1


def test_final_checkpoint_is_inference_only_and_removes_replay(tmp_path: Path) -> None:
    job_dir = tmp_path / "job"
    _save(job_dir, "checkpoint-1")
    result = _save(job_dir, "checkpoint-2", final=True)

    stored = torch.load(result["checkpoint_path"], map_location="cpu", weights_only=False)
    learner = stored["policy_state"]["agents"]["1"]["learner"]
    assert stored["resume_capable"] is False
    assert "episode_rewards" not in stored
    assert "replay_buffer" not in learner
    assert "optimizer_state_dict" not in learner
    assert "target_state_dict" not in learner
    assert "rng_state" not in learner
    assert not (job_dir / "resume_state").exists()
    assert [path.name for path in (job_dir / "internal_checkpoints").iterdir() if path.is_dir()] == ["checkpoint-2"]


def test_scientific_datasets_are_rejected_before_serialization(tmp_path: Path) -> None:
    state = _checkpoint_state()
    state["task_rows"] = [{"task_id": 1}]
    with pytest.raises(ValueError, match="must not be embedded"):
        save_bounded_checkpoint(
            job_dir=tmp_path / "job",
            checkpoint_id="checkpoint-1",
            checkpoint_state=state,
            metadata={},
            final=False,
            policy=_policy(),
        )
    assert not list(tmp_path.rglob("checkpoint.pt"))


def test_low_disk_guard_refuses_before_torch_save(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        checkpoints.shutil,
        "disk_usage",
        lambda _path: SimpleNamespace(total=10 * GIB, used=9 * GIB, free=512 * MIB),
    )
    called = False

    def forbidden_save(*_args, **_kwargs):
        nonlocal called
        called = True
        raise AssertionError("torch.save must not run after a failed budget check")

    monkeypatch.setattr(checkpoints.torch, "save", forbidden_save)
    with pytest.raises(OSError, match="disk budget refused write"):
        _save(tmp_path / "job", "checkpoint-1")
    assert called is False


def test_failed_replacement_preserves_previous_checkpoint(tmp_path: Path, monkeypatch) -> None:
    job_dir = tmp_path / "job"
    first = _save(job_dir, "checkpoint-1", final=True)
    prior_bytes = Path(first["checkpoint_path"]).read_bytes()
    prior_latest = (job_dir / "internal_checkpoints" / "latest.json").read_text(encoding="utf-8")

    monkeypatch.setattr(
        checkpoints.torch,
        "save",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("synthetic write failure")),
    )
    with pytest.raises(RuntimeError, match="synthetic write failure"):
        _save(job_dir, "checkpoint-2", final=True)

    assert Path(first["checkpoint_path"]).read_bytes() == prior_bytes
    assert (job_dir / "internal_checkpoints" / "latest.json").read_text(encoding="utf-8") == prior_latest


def test_training_loader_hydrates_external_replay(tmp_path: Path, monkeypatch) -> None:
    job_dir = tmp_path / "job"
    result = _save(job_dir, "checkpoint-1")

    monkeypatch.setattr(
        checkpoint_storage_patch,
        "_ORIGINAL_LOAD_INTERNAL_CHECKPOINT_STATE",
        lambda _job_dir: torch.load(result["checkpoint_path"], map_location="cpu", weights_only=False),
    )
    loaded = checkpoint_storage_patch.load_internal_checkpoint_state(job_dir)
    assert loaded is not None
    assert loaded["policy_state"]["agents"]["1"]["learner"]["replay_buffer"]["items"] == ["transition"]
