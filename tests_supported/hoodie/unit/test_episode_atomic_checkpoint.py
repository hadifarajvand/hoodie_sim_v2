from __future__ import annotations

import json
from pathlib import Path

from src.hoodie.experiments import episode_atomic_checkpoint_patch as patch


def _write_progress(
    job_dir: Path, *, current_slot: int, total_slots: int = 110
) -> None:
    job_dir.mkdir(parents=True, exist_ok=True)
    (job_dir / "progress.json").write_text(
        json.dumps(
            {
                "current_episode": 17,
                "current_slot": current_slot,
                "total_slots_per_episode": total_slots,
            }
        )
        + "\n",
        encoding="utf-8",
    )


def test_partial_episode_does_not_serialize_mutated_policy(
    tmp_path: Path, monkeypatch
) -> None:
    job_dir = tmp_path / "job"
    _write_progress(job_dir, current_slot=31)
    delegated = False

    def forbidden_checkpoint(*_args, **_kwargs):
        nonlocal delegated
        delegated = True
        raise AssertionError("partial episode reached checkpoint serializer")

    monkeypatch.setattr(patch, "_ORIGINAL_CHECKPOINT_POLICY", forbidden_checkpoint)

    from src.hoodie.experiments import production_campaign as legacy

    monkeypatch.setattr(legacy, "_load_internal_checkpoint_state", lambda _path: None)
    checkpoint_id = patch.checkpoint_only_at_episode_boundary(job_dir=job_dir)
    assert checkpoint_id == ""
    assert delegated is False
    rollback = json.loads(
        (job_dir / "interruption_rollback.json").read_text(encoding="utf-8")
    )
    assert rollback["status"] == "partial_episode_not_checkpointed"
    assert rollback["rollback_checkpoint_id"] is None


def test_partial_episode_reuses_last_completed_boundary(
    tmp_path: Path, monkeypatch
) -> None:
    job_dir = tmp_path / "job"
    _write_progress(job_dir, current_slot=40)
    monkeypatch.setattr(
        patch,
        "_ORIGINAL_CHECKPOINT_POLICY",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("partial episode was serialized")
        ),
    )

    from src.hoodie.experiments import production_campaign as legacy

    monkeypatch.setattr(
        legacy,
        "_load_internal_checkpoint_state",
        lambda _path: {"checkpoint_id": "safe-boundary"},
    )
    assert (
        patch.checkpoint_only_at_episode_boundary(job_dir=job_dir)
        == "safe-boundary"
    )


def test_episode_boundary_delegates_to_checkpoint_serializer(
    tmp_path: Path, monkeypatch
) -> None:
    job_dir = tmp_path / "job"
    _write_progress(job_dir, current_slot=110)
    observed: list[Path] = []

    def checkpoint(*_args, **kwargs):
        observed.append(Path(kwargs["job_dir"]))
        return "new-boundary"

    monkeypatch.setattr(patch, "_ORIGINAL_CHECKPOINT_POLICY", checkpoint)
    assert (
        patch.checkpoint_only_at_episode_boundary(job_dir=job_dir)
        == "new-boundary"
    )
    assert observed == [job_dir]
    assert not (job_dir / "interruption_rollback.json").exists()
