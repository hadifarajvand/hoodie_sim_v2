from __future__ import annotations

import csv
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from statistics import mean
from typing import Any, Iterable

import numpy as np

from .replay_buffer import Transition


REQUIRED_FIELDS = {"state", "action", "reward", "next_state", "done"}


@dataclass(frozen=True)
class TraceDatasetSummary:
    source_trace_dir: str
    episodes: int
    transitions: int
    state_dim: int | None
    action_count: int | None
    reward_mean: float | None
    reward_min: float | None
    reward_max: float | None
    required_files_present: dict[str, bool]
    missing_optional_fields: dict[str, int]
    unavailable_fields: list[str]
    approximation_warnings: list[str]
    reconstructed: bool
    notes: list[str]


@dataclass
class TraceDataset:
    transitions: list[Transition]
    summary: TraceDatasetSummary


def _iter_files(trace_dir: Path) -> list[Path]:
    files: list[Path] = []
    for pattern in ("*.json", "*.jsonl", "*.csv"):
        files.extend(trace_dir.rglob(pattern))
    return sorted({path for path in files if path.is_file()})


REQUIRED_TRACE_FILES = (
    "task_lifecycle.csv",
    "queue_trace.csv",
    "action_trace.csv",
    "episode_metrics.csv",
)


def _load_json_file(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text())
    if isinstance(data, list):
        return [row for row in data if isinstance(row, dict)]
    if isinstance(data, dict):
        return [data]
    return []


def _load_jsonl_file(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        rows.append(json.loads(line))
    return [row for row in rows if isinstance(row, dict)]


def _load_csv_file(path: Path) -> list[dict[str, Any]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def _load_any(path: Path) -> list[dict[str, Any]]:
    if path.suffix == ".json":
        return _load_json_file(path)
    if path.suffix == ".jsonl":
        return _load_jsonl_file(path)
    if path.suffix == ".csv":
        return _load_csv_file(path)
    return []


def _as_array(value: Any) -> np.ndarray:
    if isinstance(value, np.ndarray):
        return value.astype(np.float32)
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return np.asarray(parsed, dtype=np.float32)
        except Exception:
            raise ValueError(f"cannot parse state value: {value!r}")
    if isinstance(value, (list, tuple)):
        return np.asarray(value, dtype=np.float32)
    raise ValueError(f"unsupported array-like value: {type(value)!r}")


def _extract_transition(row: dict[str, Any]) -> Transition:
    missing = [field for field in REQUIRED_FIELDS if field not in row]
    if missing:
        raise ValueError(f"missing required training fields: {missing}")
    state = _as_array(row["state"])
    next_state = _as_array(row["next_state"])
    action = int(row["action"])
    reward = float(row["reward"])
    done = bool(row["done"])
    episode_id = int(row["episode_id"]) if row.get("episode_id") not in (None, "", "None") else None
    task_id = int(row["task_id"]) if row.get("task_id") not in (None, "", "None") else None
    step_index = int(row["step_index"]) if row.get("step_index") not in (None, "", "None") else None
    policy_name = row.get("policy_name") or row.get("baseline_name")
    return Transition(
        state=state,
        action=action,
        reward=reward,
        next_state=next_state,
        done=done,
        episode_id=episode_id,
        task_id=task_id,
        step_index=step_index,
        policy_name=policy_name,
    )


def _reconstruct_from_task_traces(rows: list[dict[str, Any]]) -> list[Transition]:
    transitions: list[Transition] = []
    per_episode: dict[Any, list[dict[str, Any]]] = {}
    for row in rows:
        episode_id = row.get("episode_id")
        per_episode.setdefault(episode_id, []).append(row)

    for episode_rows in per_episode.values():
        ordered = sorted(
            episode_rows,
            key=lambda row: (
                int(float(row.get("time") or row.get("step_index") or 0)),
                int(float(row.get("task_id") or 0)),
            ),
        )
        for idx, row in enumerate(ordered):
            if row.get("selected_action") in (None, "", "None"):
                continue
            action = int(float(row["selected_action"]))
            reward_value = row.get("reward_received")
            if reward_value in (None, "", "None"):
                reward_value = row.get("reward")
            if reward_value in (None, "", "None"):
                reward = 0.0
            else:
                reward = float(reward_value)
            state = np.asarray(
                [
                    float(row.get("arrival_time") or row.get("time") or idx),
                    float(row.get("queue_enter_time") or 0),
                ],
                dtype=np.float32,
            )
            next_state = state.copy()
            task_id = int(float(row["task_id"])) if row.get("task_id") not in (None, "", "None") else None
            transitions.append(
                Transition(
                    state=state,
                    action=action,
                    reward=reward,
                    next_state=next_state,
                    done=row.get("final_status") in {"completed", "dropped"},
                    episode_id=int(float(row["episode_id"])) if row.get("episode_id") not in (None, "", "None") else None,
                    task_id=task_id,
                    step_index=int(float(row.get("time") or row.get("step_index") or idx)),
                    policy_name=row.get("policy_name") or row.get("baseline_name"),
                )
            )
    return transitions


def load_trace_dataset(trace_dir: str | Path) -> tuple[list[Transition], TraceDatasetSummary]:
    trace_dir = Path(trace_dir)
    required_files_present = {name: (trace_dir / name).exists() for name in REQUIRED_TRACE_FILES}
    missing_required_files = [name for name, present in required_files_present.items() if not present]
    rows: list[dict[str, Any]] = []
    notes: list[str] = []
    unavailable_fields: list[str] = []
    approximation_warnings: list[str] = []
    missing_optional_fields = {
        "task_id": 0,
        "step_index": 0,
        "policy_name": 0,
        "baseline_name": 0,
    }
    if missing_required_files:
        raise ValueError(f"missing required trace files: {missing_required_files}")
    for path in _iter_files(trace_dir):
        loaded = _load_any(path)
        rows.extend(loaded)
        if path.suffix in {".json", ".jsonl"}:
            for row in loaded:
                for key in missing_optional_fields:
                    if row.get(key) in (None, "", "None"):
                        missing_optional_fields[key] += 1

    transitions: list[Transition] = []
    reconstructed = False
    if rows and REQUIRED_FIELDS.issubset(rows[0].keys()):
        for row in rows:
            transitions.append(_extract_transition(row))
    else:
        task_rows = [row for row in rows if "final_status" in row or "selected_action" in row]
        if task_rows:
            transitions = _reconstruct_from_task_traces(task_rows)
            reconstructed = True
            notes.append("reconstructed transitions from task lifecycle traces")
            unavailable_fields.extend(["state", "next_state"])
            approximation_warnings.append("state and next_state were reconstructed from task lifecycle fields")
        else:
            raise ValueError("trace directory does not contain direct RL transitions or task traces")

    if not transitions:
        raise ValueError("trace directory did not produce any training transitions")

    rewards = [transition.reward for transition in transitions]
    state_dim = len(transitions[0].state) if transitions else None
    action_count = (max(transition.action for transition in transitions) + 1) if transitions else None
    summary = TraceDatasetSummary(
        source_trace_dir=str(trace_dir),
        episodes=len({transition.episode_id for transition in transitions if transition.episode_id is not None}),
        transitions=len(transitions),
        state_dim=state_dim,
        action_count=action_count,
        reward_mean=mean(rewards) if rewards else None,
        reward_min=min(rewards) if rewards else None,
        reward_max=max(rewards) if rewards else None,
        required_files_present=required_files_present,
        missing_optional_fields=missing_optional_fields,
        unavailable_fields=unavailable_fields,
        approximation_warnings=approximation_warnings,
        reconstructed=reconstructed,
        notes=notes,
    )
    return transitions, summary


def summary_to_dict(summary: TraceDatasetSummary) -> dict[str, Any]:
    return asdict(summary)
