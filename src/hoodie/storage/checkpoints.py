from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import tempfile
from typing import Any

import torch


GIB = 1024**3
MIB = 1024**2


@dataclass(frozen=True, slots=True)
class CheckpointStoragePolicy:
    """Storage limits applied before every checkpoint write.

    Defaults are deliberately conservative. Production workers may increase the
    per-job budget explicitly, but they may not disable the global free-space
    reserve or the one-latest-replay rule.
    """

    max_checkpoints_per_job: int = 1
    minimum_free_bytes: int = 20 * GIB
    minimum_free_fraction: float = 0.10
    maximum_job_bytes: int = 5 * GIB
    estimated_checkpoint_bytes: int = 2 * GIB
    maximum_replay_snapshots: int = 1

    def __post_init__(self) -> None:
        if self.max_checkpoints_per_job < 1:
            raise ValueError("max_checkpoints_per_job must be at least one")
        if self.maximum_replay_snapshots != 1:
            raise ValueError("exactly one latest replay snapshot is supported")
        if self.minimum_free_bytes < 1 * GIB:
            raise ValueError("minimum_free_bytes may not be below 1 GiB")
        if not 0.0 < self.minimum_free_fraction < 1.0:
            raise ValueError("minimum_free_fraction must be in (0, 1)")
        if self.maximum_job_bytes <= 0:
            raise ValueError("maximum_job_bytes must be positive")
        if self.estimated_checkpoint_bytes <= 0:
            raise ValueError("estimated_checkpoint_bytes must be positive")


def _positive_env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    value = int(raw)
    if value <= 0:
        raise ValueError(f"{name} must be positive")
    return value


def checkpoint_storage_policy() -> CheckpointStoragePolicy:
    return CheckpointStoragePolicy(
        max_checkpoints_per_job=_positive_env_int("HOODIE_MAX_CHECKPOINTS_PER_JOB", 1),
        minimum_free_bytes=_positive_env_int("HOODIE_MIN_FREE_GB", 20) * GIB,
        minimum_free_fraction=float(os.environ.get("HOODIE_MIN_FREE_FRACTION", "0.10")),
        maximum_job_bytes=_positive_env_int("HOODIE_MAX_CHECKPOINT_GB_PER_JOB", 5) * GIB,
        estimated_checkpoint_bytes=_positive_env_int("HOODIE_ESTIMATED_CHECKPOINT_MB", 2048) * MIB,
        maximum_replay_snapshots=1,
    )


def _directory_size(path: Path) -> int:
    if not path.exists():
        return 0
    total = 0
    for candidate in path.rglob("*"):
        if candidate.is_file():
            try:
                total += candidate.stat().st_size
            except FileNotFoundError:
                continue
    return total


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(MIB), b""):
            digest.update(block)
    return digest.hexdigest()


def _atomic_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=path.parent, delete=False
        ) as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
            temporary = Path(handle.name)
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _required_reserve(target: Path, policy: CheckpointStoragePolicy) -> tuple[shutil._ntuple_diskusage, int]:
    usage = shutil.disk_usage(target)
    reserve = max(policy.minimum_free_bytes, int(usage.total * policy.minimum_free_fraction))
    return usage, reserve


def _assert_disk_budget(
    target_dir: Path,
    *,
    budget_root: Path,
    estimated_write_bytes: int,
    replacing_bytes: int,
    policy: CheckpointStoragePolicy,
) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    budget_root.mkdir(parents=True, exist_ok=True)
    usage, required_after_write = _required_reserve(target_dir, policy)
    additional = max(0, estimated_write_bytes - replacing_bytes)
    if usage.free - additional < required_after_write:
        raise OSError(
            "checkpoint disk budget refused write: "
            f"free={usage.free}, estimated_additional={additional}, "
            f"required_reserve={required_after_write}"
        )
    current_job_bytes = _directory_size(budget_root)
    projected_job_bytes = current_job_bytes - replacing_bytes + estimated_write_bytes
    if projected_job_bytes > policy.maximum_job_bytes:
        raise OSError(
            "checkpoint job budget refused write: "
            f"current={current_job_bytes}, projected={projected_job_bytes}, "
            f"maximum={policy.maximum_job_bytes}"
        )


def _atomic_torch_save(
    path: Path,
    payload: object,
    *,
    budget_root: Path,
    policy: CheckpointStoragePolicy,
) -> tuple[int, str]:
    replacing_bytes = path.stat().st_size if path.exists() else 0
    _assert_disk_budget(
        path.parent,
        budget_root=budget_root,
        estimated_write_bytes=policy.estimated_checkpoint_bytes,
        replacing_bytes=replacing_bytes,
        policy=policy,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
        torch.save(payload, temporary)
        size = temporary.stat().st_size
        usage, required_after_write = _required_reserve(path.parent, policy)
        if usage.free < required_after_write:
            raise OSError("checkpoint serialization consumed the configured disk reserve")
        projected = _directory_size(budget_root) - replacing_bytes + size
        if projected > policy.maximum_job_bytes:
            raise OSError(
                "serialized checkpoint exceeds the configured per-job budget: "
                f"projected={projected}, maximum={policy.maximum_job_bytes}"
            )
        loaded = torch.load(temporary, map_location="cpu", weights_only=False)
        if not isinstance(loaded, dict):
            raise ValueError("checkpoint payload must deserialize to a dictionary")
        digest = _sha256_file(temporary)
        with temporary.open("rb") as handle:
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        temporary = None
        return size, digest
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _split_replay_state(policy_state: dict[str, Any]) -> dict[str, Any]:
    replay: dict[str, Any] = {}
    agents = policy_state.get("agents", {})
    if not isinstance(agents, dict):
        return replay
    for agent_id, agent_state in agents.items():
        if not isinstance(agent_state, dict):
            continue
        learner = agent_state.get("learner")
        if not isinstance(learner, dict):
            continue
        if "replay_buffer" in learner:
            replay[str(agent_id)] = learner.pop("replay_buffer")
    return replay


def _make_inference_only(policy_state: dict[str, Any]) -> None:
    agents = policy_state.get("agents", {})
    if not isinstance(agents, dict):
        return
    for agent_state in agents.values():
        if not isinstance(agent_state, dict):
            continue
        learner = agent_state.get("learner")
        if not isinstance(learner, dict):
            continue
        learner.pop("optimizer_state_dict", None)
        learner.pop("target_state_dict", None)
        learner.pop("replay_buffer", None)
        learner.pop("rng_state", None)


def _prune_checkpoint_directories(
    checkpoint_root: Path, current: Path, *, keep: int
) -> list[str]:
    directories = (
        sorted(
            (path for path in checkpoint_root.iterdir() if path.is_dir()),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        if checkpoint_root.exists()
        else []
    )
    retained = {current.resolve()}
    for directory in directories:
        if len(retained) >= keep:
            break
        retained.add(directory.resolve())
    removed: list[str] = []
    for directory in directories:
        if directory.resolve() in retained:
            continue
        shutil.rmtree(directory)
        removed.append(directory.name)
    return removed


def save_bounded_checkpoint(
    *,
    job_dir: Path,
    checkpoint_id: str,
    checkpoint_state: dict[str, Any],
    metadata: dict[str, Any],
    final: bool,
    policy: CheckpointStoragePolicy | None = None,
) -> dict[str, Any]:
    """Persist one atomic model checkpoint and at most one replay snapshot.

    Resumable checkpoints keep optimizer/RNG state and store replay separately in
    ``resume_state/replay_latest.pt``. Final checkpoints are inference-only and
    remove the obsolete replay snapshot only after the final model checkpoint and
    metadata are durably installed.
    """

    storage_policy = policy or checkpoint_storage_policy()
    job_dir = job_dir.resolve()
    checkpoint_root = job_dir / "internal_checkpoints"
    checkpoint_dir = checkpoint_root / checkpoint_id
    checkpoint_path = checkpoint_dir / "checkpoint.pt"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    policy_state = checkpoint_state.get("policy_state")
    if not isinstance(policy_state, dict):
        raise ValueError("checkpoint_state.policy_state must be a dictionary")

    replay_payload = _split_replay_state(policy_state)
    replay_metadata: dict[str, Any] | None = None
    replay_dir = job_dir / "resume_state"
    if final:
        _make_inference_only(policy_state)
        checkpoint_state["resume_capable"] = False
        checkpoint_state.pop("episode_rewards", None)
        checkpoint_state.pop("replay_snapshot", None)
    else:
        checkpoint_state["resume_capable"] = True
        if replay_payload:
            replay_path = replay_dir / "replay_latest.pt"
            replay_size, replay_hash = _atomic_torch_save(
                replay_path,
                {"schema_version": 1, "checkpoint_id": checkpoint_id, "agents": replay_payload},
                budget_root=job_dir,
                policy=storage_policy,
            )
            replay_metadata = {
                "path": str(replay_path.relative_to(job_dir)),
                "sha256": replay_hash,
                "size_bytes": replay_size,
                "checkpoint_id": checkpoint_id,
            }
            _atomic_json(replay_dir / "replay_latest.metadata.json", replay_metadata)
            checkpoint_state["replay_snapshot"] = replay_metadata

    try:
        checkpoint_size, checkpoint_hash = _atomic_torch_save(
            checkpoint_path,
            checkpoint_state,
            budget_root=job_dir,
            policy=storage_policy,
        )
        metadata_payload = {
            **metadata,
            "checkpoint_schema_version": 3,
            "checkpoint_path": str(checkpoint_path.relative_to(job_dir)),
            "checkpoint_sha256": checkpoint_hash,
            "checkpoint_size_bytes": checkpoint_size,
            "resume_capable": not final,
            "replay_snapshot": replay_metadata,
            "storage_policy": asdict(storage_policy),
        }
        _atomic_json(checkpoint_dir / "metadata.json", metadata_payload)
        _atomic_json(
            checkpoint_root / "latest.json",
            {
                "checkpoint_id": checkpoint_id,
                "checkpoint_path": str(checkpoint_path),
                "checkpoint_sha256": checkpoint_hash,
                "resume_capable": not final,
            },
        )
    except Exception:
        if not checkpoint_path.exists():
            shutil.rmtree(checkpoint_dir, ignore_errors=True)
        raise

    removed = _prune_checkpoint_directories(
        checkpoint_root,
        checkpoint_dir,
        keep=storage_policy.max_checkpoints_per_job,
    )
    if final and replay_dir.exists():
        shutil.rmtree(replay_dir)

    retention = {
        "current_checkpoint_id": checkpoint_id,
        "maximum_retained_checkpoints": storage_policy.max_checkpoints_per_job,
        "removed_checkpoint_ids": removed,
        "replay_snapshot_count": 0 if replay_metadata is None else 1,
        "checkpoint_size_bytes": checkpoint_size,
        "job_checkpoint_bytes": _directory_size(job_dir),
        "minimum_free_bytes": storage_policy.minimum_free_bytes,
        "minimum_free_fraction": storage_policy.minimum_free_fraction,
        "maximum_job_bytes": storage_policy.maximum_job_bytes,
    }
    _atomic_json(job_dir / "checkpoint_retention_manifest.json", retention)
    return {
        "checkpoint_id": checkpoint_id,
        "checkpoint_path": checkpoint_path,
        "checkpoint_sha256": checkpoint_hash,
        "checkpoint_size_bytes": checkpoint_size,
        "replay_snapshot": replay_metadata,
        "removed_checkpoint_ids": removed,
    }


def hydrate_replay_snapshot(
    job_dir: Path, checkpoint_state: dict[str, Any]
) -> dict[str, Any]:
    """Restore external replay state into a resumable checkpoint in memory."""

    replay_meta = checkpoint_state.get("replay_snapshot")
    if not isinstance(replay_meta, dict):
        return checkpoint_state
    relative = replay_meta.get("path")
    expected_hash = replay_meta.get("sha256")
    if not isinstance(relative, str) or not relative:
        raise ValueError("replay snapshot metadata is missing its relative path")
    job_dir = job_dir.resolve()
    replay_path = (job_dir / relative).resolve()
    if job_dir not in replay_path.parents:
        raise ValueError("replay snapshot escapes the job directory")
    if not replay_path.exists():
        raise FileNotFoundError(f"missing replay snapshot: {replay_path}")
    actual_hash = _sha256_file(replay_path)
    if expected_hash and actual_hash != expected_hash:
        raise ValueError("replay snapshot hash mismatch")
    payload = torch.load(replay_path, map_location="cpu", weights_only=False)
    agents_replay = payload.get("agents", {}) if isinstance(payload, dict) else {}
    policy_state = checkpoint_state.get("policy_state", {})
    agents = policy_state.get("agents", {}) if isinstance(policy_state, dict) else {}
    for agent_id, replay_state in agents_replay.items():
        agent_state = agents.get(str(agent_id))
        if not isinstance(agent_state, dict):
            raise ValueError(f"replay snapshot references unknown agent {agent_id}")
        learner = agent_state.get("learner")
        if not isinstance(learner, dict):
            raise ValueError(f"agent {agent_id} has no learner state")
        learner["replay_buffer"] = replay_state
    return checkpoint_state
