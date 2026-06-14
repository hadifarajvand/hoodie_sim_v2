from __future__ import annotations

import csv
import json
import ast
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import mean
from typing import Any

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
    paper_state_trace_present: bool
    state_source: str | None
    next_state_source: str | None
    waiting_time_source: str | None
    load_history_source: str | None
    predicted_next_load_method: str | None
    paper_lstm_forecast: bool | None
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


@dataclass(frozen=True)
class PaperStateRecord:
    task_id: int
    episode_id: int | None
    time: int | None
    eta_n: float | None
    w_priv_n: float | None
    w_off_n: float | None
    l_pub_n_prev: np.ndarray
    active_load_vector: np.ndarray
    load_history: np.ndarray
    predicted_next_load: np.ndarray | None
    unavailable_fields: list[str]


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


def _load_json_array(value: Any) -> Any:
    if value in (None, "", "None"):
        return None
    if isinstance(value, (list, dict)):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            try:
                return ast.literal_eval(value)
            except Exception:
                return None
    return value


def _as_array(value: Any) -> np.ndarray:
    if isinstance(value, np.ndarray):
        return value.astype(np.float32)
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return np.asarray(parsed, dtype=np.float32)
        except Exception as exc:  # pragma: no cover - defensive
            raise ValueError(f"cannot parse state value: {value!r}") from exc
    if isinstance(value, (list, tuple)):
        return np.asarray(value, dtype=np.float32)
    raise ValueError(f"unsupported array-like value: {type(value)!r}")


def _safe_float(value: Any) -> float | None:
    if value in (None, "", "None"):
        return None
    try:
        return float(value)
    except Exception:
        return None


def _safe_int(value: Any) -> int | None:
    if value in (None, "", "None"):
        return None
    try:
        return int(float(value))
    except Exception:
        return None


def _time_key(episode_id: Any, time_value: Any) -> tuple[Any, Any]:
    return _safe_int(episode_id), _safe_int(time_value)


def _group_queue_rows(rows: list[dict[str, Any]]) -> dict[tuple[Any, Any], list[dict[str, Any]]]:
    grouped: dict[tuple[Any, Any], list[dict[str, Any]]] = {}
    for row in rows:
        if "queue_type" not in row:
            continue
        grouped.setdefault(_time_key(row.get("episode_id"), row.get("time")), []).append(row)
    return grouped


def _group_action_rows(rows: list[dict[str, Any]]) -> dict[tuple[Any, Any, Any], list[dict[str, Any]]]:
    grouped: dict[tuple[Any, Any, Any], list[dict[str, Any]]] = {}
    for row in rows:
        if "selected_action" not in row and "raw_action_id" not in row:
            continue
        key = (_safe_int(row.get("episode_id")), _safe_int(row.get("time")), _safe_int(row.get("agent_id")))
        grouped.setdefault(key, []).append(row)
    return grouped


def _infer_reward(task_row: dict[str, Any]) -> float:
    status = str(task_row.get("final_status") or "pending")
    arrival_time = _safe_int(task_row.get("arrival_time"))
    completion_time = _safe_int(task_row.get("completion_time"))
    if status == "completed" and arrival_time is not None and completion_time is not None:
        delay = max(0, completion_time - arrival_time + 1)
        return float(-delay)
    if status == "dropped":
        return -40.0
    return 0.0


def _extract_node_count(queue_rows: list[dict[str, Any]]) -> int | None:
    node_ids = sorted(
        {
            _safe_int(row.get("node_id"))
            for row in queue_rows
            if _safe_int(row.get("node_id")) is not None and str(row.get("queue_type")) != "cloud"
        }
    )
    if not node_ids:
        return None
    return max(node_ids) + 1


def _build_public_vector(
    episode_id: Any,
    time_value: Any,
    queue_rows_by_episode_time: dict[tuple[Any, Any], list[dict[str, Any]]],
    node_count: int | None,
) -> np.ndarray:
    if node_count is None:
        return np.asarray([], dtype=np.float32)
    vector = np.full(node_count + 1, np.nan, dtype=np.float32)
    rows = queue_rows_by_episode_time.get(_time_key(episode_id, time_value), [])
    for row in rows:
        node_id = _safe_int(row.get("node_id"))
        if node_id is None or node_id > node_count:
            continue
        queue_type = str(row.get("queue_type") or "")
        if queue_type in {"private", "offloading"}:
            continue
        if queue_type.startswith("public:") or queue_type == "cloud":
            queue_length = _safe_float(row.get("queue_length"))
            if queue_length is not None:
                vector[node_id] = np.nansum([vector[node_id], queue_length]) if not np.isnan(vector[node_id]) else queue_length
    return vector


def _build_load_history(
    episode_id: Any,
    time_value: Any,
    queue_rows_by_episode_time: dict[tuple[Any, Any], list[dict[str, Any]]],
    node_count: int | None,
    load_window: int = 4,
) -> np.ndarray:
    if node_count is None:
        return np.asarray([], dtype=np.float32)
    history: list[np.ndarray] = []
    current_time = _safe_int(time_value)
    episode_times = sorted({t for ep, t in queue_rows_by_episode_time if ep == _safe_int(episode_id) and t is not None and (current_time is None or t <= current_time)})
    for t in episode_times[-load_window:]:
        row_vector = np.full(node_count + 1, np.nan, dtype=np.float32)
        rows = queue_rows_by_episode_time.get(_time_key(episode_id, t), [])
        for row in rows:
            node_id = _safe_int(row.get("node_id"))
            if node_id is None or node_id > node_count:
                continue
            queue_length = _safe_float(row.get("queue_length"))
            if queue_length is None:
                continue
            row_vector[node_id] = np.nansum([row_vector[node_id], queue_length]) if not np.isnan(row_vector[node_id]) else queue_length
        history.append(row_vector)
    while len(history) < load_window:
        history.insert(0, np.full(node_count + 1, np.nan, dtype=np.float32))
    return np.asarray(history, dtype=np.float32)


def _build_paper_state(
    task_row: dict[str, Any],
    queue_rows_by_episode_time: dict[tuple[Any, Any], list[dict[str, Any]]],
    node_count: int | None,
    load_window: int = 4,
) -> PaperStateRecord:
    episode_id = task_row.get("episode_id")
    time_value = task_row.get("queue_enter_time") or task_row.get("arrival_time") or task_row.get("time")
    rows = queue_rows_by_episode_time.get(_time_key(episode_id, time_value), [])
    source_node = _safe_int(task_row.get("source_node"))
    eta_n = _safe_float(task_row.get("input_data_size"))
    if eta_n is None:
        eta_n = _safe_float(task_row.get("task_size"))
    private_row = next((row for row in rows if _safe_int(row.get("node_id")) == source_node and row.get("queue_type") == "private"), None)
    offloading_row = next((row for row in rows if _safe_int(row.get("node_id")) == source_node and row.get("queue_type") == "offloading"), None)
    w_priv_n = _safe_float(private_row.get("queue_length")) if private_row is not None else None
    w_off_n = _safe_float(offloading_row.get("queue_length")) if offloading_row is not None else None

    current_time = _safe_int(time_value)
    l_pub_n_prev = _build_public_vector(episode_id, current_time - 1 if current_time is not None else time_value, queue_rows_by_episode_time, node_count)
    active_load_vector = _build_public_vector(episode_id, time_value, queue_rows_by_episode_time, node_count)
    load_history = _build_load_history(episode_id, time_value, queue_rows_by_episode_time, node_count, load_window=load_window)

    unavailable_fields = []
    if eta_n is None:
        unavailable_fields.append("eta_n")
    if w_priv_n is None:
        unavailable_fields.append("w_priv_n")
    if w_off_n is None:
        unavailable_fields.append("w_off_n")
    if l_pub_n_prev.size == 0:
        unavailable_fields.append("l_pub_n_prev")
    if load_history.size == 0:
        unavailable_fields.append("L(t)")

    return PaperStateRecord(
        task_id=_safe_int(task_row.get("task_id")) or 0,
        episode_id=_safe_int(episode_id),
        time=_safe_int(time_value),
        eta_n=eta_n,
        w_priv_n=w_priv_n,
        w_off_n=w_off_n,
        l_pub_n_prev=l_pub_n_prev,
        active_load_vector=active_load_vector,
        load_history=load_history,
        predicted_next_load=None,
        unavailable_fields=unavailable_fields,
    )


def _action_trace_to_dict(action_row: dict[str, Any] | None) -> dict[str, Any] | None:
    if action_row is None:
        return None
    result = dict(action_row)
    if "d_nk_2" in result and isinstance(result["d_nk_2"], str) and result["d_nk_2"] not in (None, "", "None"):
        try:
            result["d_nk_2"] = json.loads(result["d_nk_2"])
        except Exception:
            result["d_nk_2"] = None
    return result


def _extract_transition(row: dict[str, Any]) -> Transition:
    missing = [field for field in REQUIRED_FIELDS if field not in row]
    if missing:
        raise ValueError(f"missing required training fields: {missing}")
    state = _as_array(row["state"])
    next_state = _as_array(row["next_state"])
    action = int(row["action"])
    reward = float(row["reward"])
    done = bool(row["done"])
    episode_id = _safe_int(row.get("episode_id"))
    task_id = _safe_int(row.get("task_id"))
    step_index = _safe_int(row.get("step_index"))
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


def _parse_paper_state_row(row: dict[str, Any]) -> dict[str, Any]:
    state_vector = np.asarray(_load_json_array(row.get("state_vector_json")) or [], dtype=np.float32)
    l_pub_n_prev = np.asarray(_load_json_array(row.get("l_pub_n_prev_json")) or [], dtype=np.float32)
    active_load_vector = np.asarray(_load_json_array(row.get("active_load_vector_json")) or [], dtype=np.float32)
    load_history = np.asarray(_load_json_array(row.get("L_t_json")) or [], dtype=np.float32)
    predicted_next_load = _load_json_array(row.get("predicted_next_load_json"))
    predicted_next_load_array = None if predicted_next_load is None else np.asarray(predicted_next_load, dtype=np.float32)
    return {
        "episode_id": _safe_int(row.get("episode_id")),
        "time": _safe_int(row.get("time")),
        "agent_id": _safe_int(row.get("agent_id")),
        "task_id": _safe_int(row.get("task_id")),
        "eta_n": _safe_float(row.get("eta_n")),
        "w_priv_n": _safe_float(row.get("w_priv_n")),
        "w_off_n": _safe_float(row.get("w_off_n")),
        "l_pub_n_prev": l_pub_n_prev,
        "active_load_vector": active_load_vector,
        "load_history": load_history,
        "predicted_next_load": predicted_next_load_array,
        "predicted_next_load_method": row.get("predicted_next_load_method"),
        "paper_lstm_forecast": str(row.get("paper_lstm_forecast")).lower() == "true",
        "unavailable_fields": _load_json_array(row.get("unavailable_fields_json")) or [],
        "approximation_warnings": _load_json_array(row.get("approximation_warnings_json")) or [],
        "state": state_vector,
    }


def _build_transition_from_paper_state_rows(
    paper_rows: list[dict[str, Any]],
    action_rows: list[dict[str, Any]],
) -> tuple[list[Transition], dict[str, Any]]:
    parsed = [_parse_paper_state_row(row) for row in paper_rows]
    parsed.sort(key=lambda row: (row["episode_id"] if row["episode_id"] is not None else -1, row["agent_id"] if row["agent_id"] is not None else -1, row["time"] if row["time"] is not None else -1))
    action_rows_by_key: dict[tuple[Any, Any, Any], dict[str, Any]] = {}
    for row in action_rows:
        key = (_safe_int(row.get("episode_id")), _safe_int(row.get("time")), _safe_int(row.get("agent_id")))
        action_rows_by_key[key] = row

    transitions: list[Transition] = []
    approximation_warnings: list[str] = []
    for idx, row in enumerate(parsed):
        next_row = next(
            (
                candidate
                for candidate in parsed[idx + 1 :]
                if candidate["episode_id"] == row["episode_id"] and candidate["agent_id"] == row["agent_id"] and candidate["time"] is not None and row["time"] is not None and candidate["time"] == row["time"] + 1
            ),
            None,
        )
        action_row = action_rows_by_key.get((row["episode_id"], row["time"], row["agent_id"]))
        state = row["state"].astype(np.float32)
        if next_row is not None:
            next_state = next_row["state"].astype(np.float32)
            done = False
            next_state_source = "runtime_paper_state_trace"
        else:
            next_state = state.copy()
            done = True
            next_state_source = "terminal_copy"
        reward = 0.0
        selected_action = 0
        if action_row is not None:
            if action_row.get("reward_received") not in (None, "", "None"):
                reward = float(action_row["reward_received"])
            if action_row.get("selected_action") not in (None, "", "None"):
                selected_action = int(float(action_row["selected_action"]))
        transition = Transition(
            state=state,
            action=selected_action,
            reward=reward,
            next_state=next_state,
            done=done,
            episode_id=row["episode_id"],
            task_id=row["task_id"],
            step_index=row["time"],
            policy_name=action_row.get("policy_name") if action_row else None,
            raw_action_id=_safe_int(action_row.get("raw_action_id")) if action_row else None,
            first_stage_decision=action_row.get("first_stage_decision") if action_row else None,
            destination_node_id=_safe_int(action_row.get("destination_node_id")) if action_row and action_row.get("destination_node_id") not in (None, "", "None") else None,
            destination_type=action_row.get("destination_type") if action_row else None,
            is_valid=str(action_row.get("is_valid")).lower() == "true" if action_row and action_row.get("is_valid") not in (None, "", "None") else None,
            invalid_reason=action_row.get("invalid_reason") if action_row else None,
            adjacency_allowed=str(action_row.get("adjacency_allowed")).lower() == "true" if action_row and action_row.get("adjacency_allowed") not in (None, "", "None") else None,
            cloud_target=str(action_row.get("cloud_target")).lower() == "true" if action_row and action_row.get("cloud_target") not in (None, "", "None") else None,
            d_n_1=_safe_int(action_row.get("d_n_1")) if action_row else None,
            d_nk_2=_load_json_array(action_row.get("d_nk_2")) if action_row and action_row.get("d_nk_2") not in (None, "", "None") else None,
            eta_n=row["eta_n"],
            w_priv_n=row["w_priv_n"],
            w_off_n=row["w_off_n"],
            l_pub_n_prev=row["l_pub_n_prev"],
            active_load_vector=row["active_load_vector"],
            load_history=row["load_history"],
            predicted_next_load=row["predicted_next_load"],
        )
        transitions.append(transition)
        if next_row is None:
            approximation_warnings.append(f"next_state copied for terminal row episode={row['episode_id']} agent={row['agent_id']} time={row['time']}")

    summary = {
        "paper_state_trace_present": True,
        "state_source": "runtime_paper_state_trace",
        "next_state_source": "runtime_paper_state_trace",
        "waiting_time_source": "runtime_queue_waiting_time",
        "load_history_source": "runtime_active_load_matrix",
        "predicted_next_load_method": parsed[0]["predicted_next_load_method"] if parsed else None,
        "paper_lstm_forecast": parsed[0]["paper_lstm_forecast"] if parsed else None,
        "approximation_warnings": approximation_warnings,
        "state_dim": len(transitions[0].state) if transitions else None,
        "action_count": max(t.action for t in transitions) + 1 if transitions else None,
        "episodes": len({t.episode_id for t in transitions if t.episode_id is not None}),
        "transitions": len(transitions),
    }
    return transitions, summary


def _build_transition_from_task_row(
    row: dict[str, Any],
    action_row: dict[str, Any] | None,
    queue_rows_by_episode_time: dict[tuple[Any, Any], list[dict[str, Any]]],
    node_count: int | None,
    load_window: int = 4,
) -> Transition:
    state_rec = _build_paper_state(row, queue_rows_by_episode_time, node_count=node_count, load_window=load_window)
    eta = np.nan if state_rec.eta_n is None else state_rec.eta_n
    w_priv = np.nan if state_rec.w_priv_n is None else state_rec.w_priv_n
    w_off = np.nan if state_rec.w_off_n is None else state_rec.w_off_n
    state_parts = [np.asarray([eta, w_priv, w_off], dtype=np.float32)]
    if state_rec.l_pub_n_prev.size:
        state_parts.append(state_rec.l_pub_n_prev.astype(np.float32).reshape(-1))
    if state_rec.load_history.size:
        state_parts.append(state_rec.load_history.astype(np.float32).reshape(-1))
    if state_rec.predicted_next_load is not None:
        state_parts.append(state_rec.predicted_next_load.astype(np.float32).reshape(-1))
    elif node_count is not None:
        state_parts.append(np.full(node_count + 1, np.nan, dtype=np.float32))
    state = np.concatenate(state_parts).astype(np.float32)
    next_state = state.copy()

    reward = _infer_reward(row)
    if action_row is not None and action_row.get("reward_received") not in (None, "", "None"):
        # Keep delayed lifecycle reward as primary source, but surface the runtime
        # reward row when it matches the lifecycle value. This is a traceability aid,
        # not a replacement for delayed reward reconstruction.
        try:
            runtime_reward = float(action_row["reward_received"])
            if abs(runtime_reward - reward) <= 1e-6:
                reward = runtime_reward
        except Exception:
            pass

    selected_action = action_row.get("selected_action") if action_row is not None else row.get("selected_action")
    if selected_action in (None, "", "None"):
        raise ValueError("task trace row is missing selected_action coverage")

    first_stage_decision = None
    destination_node_id = None
    destination_type = None
    is_valid = None
    invalid_reason = None
    adjacency_allowed = None
    cloud_target = None
    d_n_1 = None
    d_nk_2 = None
    raw_action_id = int(float(selected_action))
    if action_row is not None:
        action_data = _action_trace_to_dict(action_row)
        first_stage_decision = action_data.get("first_stage_decision")
        destination_node_id = _safe_int(action_data.get("destination_node_id"))
        destination_type = action_data.get("destination_type")
        if action_data.get("is_valid") not in (None, "", "None"):
            is_valid = str(action_data.get("is_valid")).lower() == "true"
        invalid_reason = action_data.get("invalid_reason")
        if action_data.get("adjacency_allowed") not in (None, "", "None"):
            adjacency_allowed = str(action_data.get("adjacency_allowed")).lower() == "true"
        if action_data.get("cloud_target") not in (None, "", "None"):
            cloud_target = str(action_data.get("cloud_target")).lower() == "true"
        d_n_1 = _safe_int(action_data.get("d_n_1"))
        d_nk_2 = action_data.get("d_nk_2")

    if first_stage_decision is None:
        first_stage_decision = "local" if destination_node_id in (None, _safe_int(row.get("source_node"))) else "offload"
    if destination_type is None:
        if first_stage_decision == "local":
            destination_type = "local"
        elif destination_node_id == node_count:
            destination_type = "vertical_cloud"
        elif destination_node_id is None:
            destination_type = "invalid"
        else:
            destination_type = "horizontal_edge"
    if is_valid is None:
        is_valid = destination_type != "invalid"
    if adjacency_allowed is None:
        adjacency_allowed = destination_type in {"local", "horizontal_edge", "vertical_cloud"}
    if cloud_target is None:
        cloud_target = destination_type == "vertical_cloud"
    if d_n_1 is None:
        d_n_1 = 1 if first_stage_decision == "local" else 0
    if d_nk_2 is None:
        d_nk_2 = {} if first_stage_decision == "local" else {int(destination_node_id): 1} if destination_node_id is not None else {}

    return Transition(
        state=state,
        action=raw_action_id,
        reward=reward,
        next_state=next_state,
        done=str(row.get("final_status") or "") in {"completed", "dropped"},
        episode_id=_safe_int(row.get("episode_id")),
        task_id=_safe_int(row.get("task_id")),
        step_index=_safe_int(row.get("time") or row.get("step_index") or row.get("queue_enter_time")),
        policy_name=row.get("policy_name") or row.get("baseline_name"),
        raw_action_id=raw_action_id,
        first_stage_decision=first_stage_decision,
        destination_node_id=destination_node_id,
        destination_type=destination_type,
        is_valid=is_valid,
        invalid_reason=invalid_reason,
        adjacency_allowed=adjacency_allowed,
        cloud_target=cloud_target,
        d_n_1=d_n_1,
        d_nk_2=d_nk_2 if isinstance(d_nk_2, dict) else None,
        eta_n=state_rec.eta_n,
        w_priv_n=state_rec.w_priv_n,
        w_off_n=state_rec.w_off_n,
        l_pub_n_prev=state_rec.l_pub_n_prev,
        active_load_vector=state_rec.active_load_vector,
        load_history=state_rec.load_history,
        predicted_next_load=state_rec.predicted_next_load,
    )


def _reconstruct_from_task_traces(rows: list[dict[str, Any]]) -> tuple[list[Transition], list[str], list[str], dict[str, int]]:
    transitions: list[Transition] = []
    notes: list[str] = ["reconstructed transitions from task lifecycle traces"]
    approximation_warnings: list[str] = []
    missing_optional_fields = {
        "task_id": 0,
        "step_index": 0,
        "policy_name": 0,
        "baseline_name": 0,
    }

    queue_rows = [row for row in rows if "queue_type" in row]
    node_count = _extract_node_count(queue_rows)
    queue_rows_by_episode_time = _group_queue_rows(rows)
    action_rows_by_key = _group_action_rows(rows)

    task_rows = [row for row in rows if "final_status" in row]
    if not task_rows:
        raise ValueError("trace directory does not contain task traces")

    for row in task_rows:
        if row.get("selected_action") in (None, "", "None"):
            continue
        episode_id = row.get("episode_id")
        source_node = row.get("source_node")
        time_key_candidates = [
            row.get("queue_enter_time"),
            row.get("arrival_time"),
            row.get("time"),
        ]
        action_row = None
        for time_value in time_key_candidates:
            key = (_safe_int(episode_id), _safe_int(time_value), _safe_int(source_node))
            candidates = action_rows_by_key.get(key, [])
            if candidates:
                action_row = candidates[0]
                break
        if action_row is None:
            approximation_warnings.append(
                f"no action_trace row matched task_id={row.get('task_id')} episode_id={episode_id} source_node={source_node}"
            )
        transition = _build_transition_from_task_row(
            row,
            action_row,
            queue_rows_by_episode_time,
            node_count=node_count,
        )
        transitions.append(transition)
        for key in missing_optional_fields:
            if row.get(key) in (None, "", "None"):
                missing_optional_fields[key] += 1

    return transitions, notes, approximation_warnings, missing_optional_fields


def load_trace_dataset(trace_dir: str | Path) -> tuple[list[Transition], TraceDatasetSummary]:
    trace_dir = Path(trace_dir)
    required_files_present = {name: (trace_dir / name).exists() for name in REQUIRED_TRACE_FILES}
    missing_required_files = [name for name, present in required_files_present.items() if not present]
    if missing_required_files:
        raise ValueError(f"missing required trace files: {missing_required_files}")

    rows: list[dict[str, Any]] = []
    for path in _iter_files(trace_dir):
        rows.extend(_load_any(path))

    notes: list[str] = []
    unavailable_fields: list[str] = []
    approximation_warnings: list[str] = []
    missing_optional_fields = {
        "task_id": 0,
        "step_index": 0,
        "policy_name": 0,
        "baseline_name": 0,
        "paper_state_eta_n": 0,
        "paper_state_w_priv_n": 0,
        "paper_state_w_off_n": 0,
        "paper_state_l_pub_n_prev": 0,
        "paper_state_L_t": 0,
        "paper_state_predicted_next_load": 0,
        "reward_delayed_task_id": 0,
    }

    transitions: list[Transition] = []
    reconstructed = False
    paper_state_rows = [row for row in rows if "state_vector_json" in row and "active_load_vector_json" in row]
    state_source = None
    next_state_source = None
    waiting_time_source = None
    load_history_source = None
    predicted_next_load_method = None
    paper_lstm_forecast = None

    if paper_state_rows:
        action_rows = [row for row in rows if "selected_action" in row and "reward_received" in row]
        transitions, paper_summary = _build_transition_from_paper_state_rows(paper_state_rows, action_rows)
        reconstructed = True
        notes.append("reconstructed transitions from runtime paper_state_trace")
        approximation_warnings.extend(paper_summary["approximation_warnings"])
        state_source = paper_summary["state_source"]
        next_state_source = paper_summary["next_state_source"]
        waiting_time_source = paper_summary["waiting_time_source"]
        load_history_source = paper_summary["load_history_source"]
        predicted_next_load_method = paper_summary["predicted_next_load_method"]
        paper_lstm_forecast = paper_summary["paper_lstm_forecast"]
    else:
        task_rows = [row for row in rows if "final_status" in row]
        if task_rows:
            reconstructed = True
            transitions, notes, approximation_warnings, task_missing = _reconstruct_from_task_traces(rows)
            missing_optional_fields.update(task_missing)
            if not transitions:
                raise ValueError("trace directory does not contain task traces with selected_action coverage")
            state_source = "legacy_lifecycle_reconstruction"
            next_state_source = "legacy_state_copy"
            waiting_time_source = "legacy_queue_length_proxy"
            load_history_source = "legacy_queue_length_history"
            predicted_next_load_method = "unavailable"
            paper_lstm_forecast = False
        elif rows and REQUIRED_FIELDS.issubset(rows[0].keys()):
            for row in rows:
                transitions.append(_extract_transition(row))
            state_source = "direct_replay_buffer"
            next_state_source = "direct_replay_buffer"
            waiting_time_source = "direct_replay_buffer"
            load_history_source = "direct_replay_buffer"
            predicted_next_load_method = "unavailable"
            paper_lstm_forecast = False
        else:
            raise ValueError("trace directory does not contain direct RL transitions or task traces")

    if not transitions:
        raise ValueError("trace directory did not produce any training transitions")

    for transition in transitions:
        if transition.eta_n is None:
            missing_optional_fields["paper_state_eta_n"] += 1
            unavailable_fields.append("eta_n")
        if transition.w_priv_n is None:
            missing_optional_fields["paper_state_w_priv_n"] += 1
            unavailable_fields.append("w_priv_n")
        if transition.w_off_n is None:
            missing_optional_fields["paper_state_w_off_n"] += 1
            unavailable_fields.append("w_off_n")
        if transition.l_pub_n_prev is None or transition.l_pub_n_prev.size == 0:
            missing_optional_fields["paper_state_l_pub_n_prev"] += 1
            unavailable_fields.append("l_pub_n_prev")
        if transition.load_history is None or transition.load_history.size == 0:
            missing_optional_fields["paper_state_L_t"] += 1
            unavailable_fields.append("L(t)")
        if transition.predicted_next_load is None:
            missing_optional_fields["paper_state_predicted_next_load"] += 1
            unavailable_fields.append("predicted_next_load")
        if transition.task_id is None:
            missing_optional_fields["reward_delayed_task_id"] += 1

    rewards = [transition.reward for transition in transitions]
    state_dim = len(transitions[0].state) if transitions else None
    action_count = (max(transition.action for transition in transitions) + 1) if transitions else None
    summary = TraceDatasetSummary(
        source_trace_dir=str(trace_dir),
        episodes=len({transition.episode_id for transition in transitions if transition.episode_id is not None}),
        transitions=len(transitions),
        state_dim=state_dim,
        action_count=action_count,
        paper_state_trace_present=bool(paper_state_rows),
        state_source=state_source,
        next_state_source=next_state_source,
        waiting_time_source=waiting_time_source,
        load_history_source=load_history_source,
        predicted_next_load_method=predicted_next_load_method,
        paper_lstm_forecast=paper_lstm_forecast,
        reward_mean=mean(rewards) if rewards else None,
        reward_min=min(rewards) if rewards else None,
        reward_max=max(rewards) if rewards else None,
        required_files_present=required_files_present,
        missing_optional_fields=missing_optional_fields,
        unavailable_fields=sorted(set(unavailable_fields)),
        approximation_warnings=sorted(set(approximation_warnings)),
        reconstructed=reconstructed,
        notes=notes,
    )
    return transitions, summary


def summary_to_dict(summary: TraceDatasetSummary) -> dict[str, Any]:
    return asdict(summary)
