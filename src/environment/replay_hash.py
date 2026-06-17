from __future__ import annotations

from dataclasses import asdict, is_dataclass
import json
from hashlib import sha256
from pathlib import Path
from typing import Any


_VOLATILE_KEYS = {
    "absolute_path",
    "created_at",
    "cwd",
    "datetime",
    "memory_address",
    "object_address",
    "path",
    "pid",
    "timestamp",
    "tmp_path",
    "wall_clock",
    "workdir",
}


def canonicalize_for_replay(value: Any) -> Any:
    if is_dataclass(value):
        return canonicalize_for_replay(asdict(value))
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        canonical: dict[str, Any] = {}
        for key in sorted(value):
            if key in _VOLATILE_KEYS:
                continue
            canonical[str(key)] = canonicalize_for_replay(value[key])
        return canonical
    if isinstance(value, (list, tuple)):
        return [canonicalize_for_replay(item) for item in value]
    if isinstance(value, set):
        return [canonicalize_for_replay(item) for item in sorted(value, key=repr)]
    return value


def stable_replay_hash(payload: dict[str, Any]) -> str:
    canonical_payload = canonicalize_for_replay(payload)
    serialized = json.dumps(canonical_payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256(serialized.encode("utf-8")).hexdigest()


def _task_snapshot(task: Any) -> dict[str, Any]:
    return canonicalize_for_replay(
        {
            "task_id": task.task_id,
            "source_agent_id": task.source_agent_id,
            "arrival_slot": task.arrival_slot,
            "size": task.size,
            "processing_density": task.processing_density,
            "timeout_length": task.timeout_length,
            "absolute_deadline_slot": task.absolute_deadline_slot,
            "cycles_required": task.cycles_required,
            "cycles_remaining": task.cycles_remaining,
            "selected_action": task.selected_action,
            "resolved_destination": task.resolved_destination,
            "queue_state": task.queue_state,
            "start_slot": task.start_slot,
            "completion_slot": task.completion_slot,
            "terminal_outcome": task.terminal_outcome,
            "reward_emitted": task.reward_emitted,
            "drop_flag": task.drop_flag,
            "metadata": task.metadata,
        }
    )


def _queue_snapshot(queue: Any) -> dict[str, Any]:
    return canonicalize_for_replay(
        {
            "kind": queue.__class__.__name__,
            "host_node_id": getattr(queue, "host_node_id", None),
            "source_agent_id": getattr(queue, "source_agent_id", None),
            "owner_node_id": getattr(queue, "owner_node_id", None),
            "resolved_destination": getattr(queue, "resolved_destination", None),
            "current_head_entered_at": getattr(queue, "current_head_entered_at", None),
            "tasks": [_task_snapshot(task) for task in getattr(queue, "tasks", ())],
        }
    )


def build_euls_replay_payload(environment: Any) -> dict[str, Any]:
    trace = getattr(environment, "trace", None)
    trace_payload = {
        "trace_id": getattr(trace, "trace_id", ""),
        "seed": getattr(trace, "seed", None),
        "metadata": getattr(trace, "metadata", {}),
        "tasks": [
            canonicalize_for_replay(
                {
                    "task_id": task.task_id,
                    "source_agent_id": task.source_agent_id,
                    "arrival_slot": task.arrival_slot,
                    "size": task.size,
                    "processing_density": task.processing_density,
                    "timeout_length": task.timeout_length,
                    "absolute_deadline_slot": task.absolute_deadline_slot,
                    "cycles_required": task.cycles_required,
                    "cycles_remaining": task.cycles_remaining,
                }
            )
            for task in getattr(trace, "tasks", ())
        ],
    }
    queues_payload = {
        "private": {
            key: _queue_snapshot(queue)
            for key, queue in sorted(getattr(environment, "_private_queues", {}).items())
        },
        "offloading": {
            f"{source}->{destination}": _queue_snapshot(queue)
            for (source, destination), queue in sorted(getattr(environment, "_offloading_queues", {}).items())
        },
        "public": {
            f"{host}:{source}": _queue_snapshot(queue)
            for (host, source), queue in sorted(getattr(environment, "_public_queues", {}).items())
        },
    }
    history = [
        canonicalize_for_replay(
            {
                "task_id": record.task_id,
                "arrival_slot": record.arrival_slot,
                "selected_action": record.selected_action,
                "resolved_destination": record.resolved_destination,
                "terminal_outcome": record.terminal_outcome,
                "completion_slot": record.completion_slot,
                "reward": record.reward,
            }
        )
        for record in getattr(environment, "_history", ())
    ]
    payload = {
        "trace": trace_payload,
        "seed": getattr(environment, "seed", None),
        "episode_length": getattr(environment, "episode_length", None),
        "policy_name": getattr(environment, "policy_name", None),
        "current_slot": getattr(environment, "current_slot", None),
        "runtime_parameters": canonicalize_for_replay(getattr(environment, "runtime_parameters", {})),
        "compute_config": canonicalize_for_replay(getattr(environment, "compute_config", {})),
        "link_rate_config": canonicalize_for_replay(getattr(environment, "link_rate_config", {})),
        "metrics": canonicalize_for_replay(getattr(environment, "_metrics", {})),
        "history": history,
        "queue_state_snapshot": queues_payload,
        "pending_terminal_task_ids": [task.task_id for task in getattr(environment, "_pending_terminal_tasks", ())],
        "lifecycle_trace_events": canonicalize_for_replay(
            getattr(getattr(environment, "trace_recorder", None), "snapshot", lambda: [])()
        ),
        "finalized_task_count": len(history),
    }
    return canonicalize_for_replay(payload)
