from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

_INSTALLED = False
_ORIGINAL_CHECKPOINT_POLICY: Callable[..., str] | None = None


def _partial_episode_progress(job_dir: Path) -> dict[str, Any] | None:
    progress_path = job_dir / "progress.json"
    if not progress_path.exists():
        return None
    payload = json.loads(progress_path.read_text(encoding="utf-8"))
    current_slot = payload.get("current_slot")
    total_slots = payload.get("total_slots_per_episode")
    if current_slot is None or total_slots is None:
        return None
    if int(current_slot) >= int(total_slots):
        return None
    return payload


def checkpoint_only_at_episode_boundary(*args: Any, **kwargs: Any) -> str:
    """Never serialize a learner after only a prefix of an episode.

    Training rewards are delayed until task resolution. Replaying a partial episode from
    its beginning after serializing the mutated learner would duplicate replay transitions
    and optimizer updates. When interruption is observed before the terminal slot, this
    guard keeps the previous episode-boundary checkpoint (or no checkpoint for episode
    zero). The next invocation safely replays from that boundary.
    """

    if _ORIGINAL_CHECKPOINT_POLICY is None:  # pragma: no cover
        raise RuntimeError("episode-atomic checkpoint patch is not installed")
    job_dir_value = kwargs.get("job_dir")
    if job_dir_value is None:
        raise TypeError("job_dir is required")
    job_dir = Path(job_dir_value)
    partial = _partial_episode_progress(job_dir)
    if partial is None:
        return _ORIGINAL_CHECKPOINT_POLICY(*args, **kwargs)

    from . import production_campaign as legacy

    previous = legacy._load_internal_checkpoint_state(job_dir)
    previous_id = "" if previous is None else str(previous.get("checkpoint_id", ""))
    legacy._write_json(
        job_dir / "interruption_rollback.json",
        {
            "status": "partial_episode_not_checkpointed",
            "current_episode": partial.get("current_episode"),
            "current_slot": partial.get("current_slot"),
            "total_slots_per_episode": partial.get("total_slots_per_episode"),
            "rollback_checkpoint_id": previous_id or None,
            "resume_semantics": "restart_from_last_completed_episode_boundary",
        },
    )
    return previous_id


def install_episode_atomic_checkpoint_patch() -> None:
    global _INSTALLED
    global _ORIGINAL_CHECKPOINT_POLICY
    if _INSTALLED:
        return

    from . import production_patch

    _ORIGINAL_CHECKPOINT_POLICY = production_patch._checkpoint_policy
    production_patch._checkpoint_policy = checkpoint_only_at_episode_boundary
    _INSTALLED = True
