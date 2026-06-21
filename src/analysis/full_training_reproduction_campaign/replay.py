from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Any, Iterable

import torch

ACTION_INDEX_TO_SEMANTICS: dict[int, str] = {
    0: "local",
    1: "horizontal",
    2: "vertical",
}

SEMANTICS_TO_ACTION_INDEX: dict[str, int] = {value: key for key, value in ACTION_INDEX_TO_SEMANTICS.items()}

STATE_REPRESENTATION_PROFILE_LEGACY_MINIMAL = "legacy_minimal"
STATE_REPRESENTATION_PROFILE_DEADLINE_QUEUE_FEASIBILITY_V1 = "deadline_queue_feasibility_v1"
STATE_REPRESENTATION_PROFILES: tuple[str, ...] = (
    STATE_REPRESENTATION_PROFILE_LEGACY_MINIMAL,
    STATE_REPRESENTATION_PROFILE_DEADLINE_QUEUE_FEASIBILITY_V1,
)

STATE_DIM = 3
STATE_DIM_LEGACY_MINIMAL = 3
STATE_DIM_DEADLINE_QUEUE_FEASIBILITY_V1 = 30
LOOKBACK_W = 10
DATA_SOURCE = "environment_rollout"


def zero_state_row() -> tuple[float, float, float]:
    return (0.0, 0.0, 0.0)


def zero_state_row_for_profile(*, state_representation_profile: str = STATE_REPRESENTATION_PROFILE_LEGACY_MINIMAL) -> tuple[float, ...]:
    if state_representation_profile == STATE_REPRESENTATION_PROFILE_LEGACY_MINIMAL:
        return (0.0, 0.0, 0.0)
    if state_representation_profile == STATE_REPRESENTATION_PROFILE_DEADLINE_QUEUE_FEASIBILITY_V1:
        return tuple(0.0 for _ in range(STATE_DIM_DEADLINE_QUEUE_FEASIBILITY_V1))
    raise ValueError(f"Unsupported state representation profile: {state_representation_profile}")


def state_dimension_for_profile(state_representation_profile: str) -> int:
    if state_representation_profile == STATE_REPRESENTATION_PROFILE_LEGACY_MINIMAL:
        return STATE_DIM_LEGACY_MINIMAL
    if state_representation_profile == STATE_REPRESENTATION_PROFILE_DEADLINE_QUEUE_FEASIBILITY_V1:
        return STATE_DIM_DEADLINE_QUEUE_FEASIBILITY_V1
    raise ValueError(f"Unsupported state representation profile: {state_representation_profile}")


def _clip_unit(value: float) -> float:
    if value != value or value in {float("inf"), float("-inf")}:
        return 0.0
    return max(0.0, min(float(value), 1.0))


def _clip_signed_unit(value: float) -> float:
    if value != value or value in {float("inf"), float("-inf")}:
        return 0.0
    return max(-1.0, min(float(value), 1.0))


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        result = float(value)
    except Exception:
        return float(default)
    if result != result or result in {float("inf"), float("-inf")}:
        return float(default)
    return result


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return int(default)


def _observation_value(observation: dict[str, Any], key: str, default: Any = None) -> Any:
    if key in observation:
        return observation.get(key, default)
    return observation.get(key.replace("_norm", ""), default)


def _path_total_slots_features(
    *,
    observation: dict[str, Any],
    current_task: Any | None,
    episode_length: int,
) -> tuple[float, float, float, float, float, float, bool, bool, bool, float, float, float, float, float]:
    task_size = _safe_float(_observation_value(observation, "task_size", getattr(current_task, "size", 0.0) if current_task is not None else 0.0))
    processing_density = _safe_float(
        _observation_value(observation, "processing_density", getattr(current_task, "processing_density", 0.0) if current_task is not None else 0.0)
    )
    timeout_length = max(_safe_int(_observation_value(observation, "timeout_length", getattr(current_task, "timeout_length", 0) if current_task is not None else 0)), 0)
    absolute_deadline_slot = _safe_int(
        _observation_value(
            observation,
            "absolute_deadline_slot",
            getattr(current_task, "absolute_deadline_slot", None) if current_task is not None else None,
        ),
        default=-1,
    )
    current_slot = _safe_int(_observation_value(observation, "slot", getattr(current_task, "slot", 0) if current_task is not None else 0))
    queue_load = max(_safe_float(_observation_value(observation, "queue_load", 0.0)), 0.0)
    legal_action_mask = dict(_observation_value(observation, "legal_action_mask", {}) or {})
    fallback_hints = dict(_observation_value(observation, "fallback_hints", {}) or {})
    latency_estimates = dict(_observation_value(observation, "latency_estimates", {}) or {})
    balance_hint = dict(_observation_value(observation, "balance_hint", {}) or {})

    # Use the same feasibility conventions as the calibrated diagnostic layers.
    from src.analysis.completion_path_deadline_feasibility_repair.feasibility import estimate_task_action_feasibility

    task_payload = {
        "task_id": _safe_int(_observation_value(observation, "task_id", getattr(current_task, "task_id", 0) if current_task is not None else 0)),
        "trace_id": _observation_value(observation, "trace_id", None),
        "episode_id": _observation_value(observation, "episode_id", None),
        "slot": current_slot,
        "arrival_slot": _safe_int(_observation_value(observation, "arrival_slot", getattr(current_task, "arrival_slot", current_slot) if current_task is not None else current_slot)),
        "absolute_deadline_slot": absolute_deadline_slot if absolute_deadline_slot >= 0 else current_slot + timeout_length,
        "timeout_length": timeout_length,
        "task_size": task_size,
        "size": task_size,
        "processing_density": processing_density,
        "queue_load": queue_load,
        "legal_action_mask": legal_action_mask,
        "source_agent_id": _safe_int(_observation_value(observation, "source_agent_id", getattr(current_task, "source_agent_id", 0) if current_task is not None else 0)),
    }
    estimate = estimate_task_action_feasibility(task_payload)
    local_total_slots = float(estimate["local_estimated_execution_slots"])
    horizontal_total_slots = float(estimate["horizontal_estimated_total_slots"])
    vertical_total_slots = float(estimate["vertical_estimated_total_slots"])
    local_slack = float(estimate["deadline_slack_for_local"])
    horizontal_slack = float(estimate["deadline_slack_for_horizontal"])
    vertical_slack = float(estimate["deadline_slack_for_vertical"])
    remaining_time = max(float(task_payload["absolute_deadline_slot"] - current_slot), 0.0)
    best_legal_total = min(
        [
            total
            for total, legal in (
                (local_total_slots, bool(legal_action_mask.get("local", False))),
                (horizontal_total_slots, bool(legal_action_mask.get("horizontal", False))),
                (vertical_total_slots, bool(legal_action_mask.get("vertical", False))),
            )
            if legal
        ],
        default=min(local_total_slots, horizontal_total_slots, vertical_total_slots),
    )
    deadline_slack = remaining_time - best_legal_total
    deadline_urgency_ratio = remaining_time / max(float(timeout_length), 1.0)
    is_deadline_immediate = 1.0 if remaining_time <= 2.0 else 0.0
    local_private_queue_load_norm = _clip_unit((queue_load + _safe_float(balance_hint.get("local", queue_load))) / max(float(episode_length), 1.0))
    public_offloading_queue_load_norm = _clip_unit((queue_load + _safe_float(fallback_hints.get("horizontal", queue_load))) / max(float(episode_length), 1.0))
    horizontal_path_queue_load_norm = _clip_unit(_safe_float(balance_hint.get("horizontal", queue_load)) / max(float(episode_length), 1.0))
    vertical_cloud_path_queue_load_norm = _clip_unit(_safe_float(balance_hint.get("vertical", queue_load)) / max(float(episode_length), 1.0))
    pending_task_pressure_norm = _clip_unit(queue_load / max(float(episode_length), 1.0))

    source_agent_id_norm = _clip_unit(_safe_float(task_payload["source_agent_id"]) / 10.0)

    return (
        _clip_unit(float(task_payload["slot"]) / max(float(episode_length - 1), 1.0)),
        _clip_unit(task_size / 60.0),
        _clip_unit(processing_density / 5.0),
        _clip_unit(queue_load / max(float(episode_length), 1.0)),
        _clip_unit(_safe_float(_observation_value(observation, "history_length", 0.0)) / max(float(episode_length), 1.0)),
        _clip_unit(timeout_length / max(float(episode_length), 1.0)),
        _clip_unit(float(task_payload["absolute_deadline_slot"]) / max(float(episode_length), 1.0)),
        _clip_unit(remaining_time / max(float(episode_length), 1.0)),
        _clip_signed_unit(deadline_slack / max(float(episode_length), 1.0)),
        _clip_unit(deadline_urgency_ratio),
        is_deadline_immediate,
        _clip_unit(local_total_slots / max(float(episode_length), 1.0)),
        _clip_unit(horizontal_total_slots / max(float(episode_length), 1.0)),
        _clip_unit(vertical_total_slots / max(float(episode_length), 1.0)),
        _clip_signed_unit(local_slack / max(float(episode_length), 1.0)),
        _clip_signed_unit(horizontal_slack / max(float(episode_length), 1.0)),
        _clip_signed_unit(vertical_slack / max(float(episode_length), 1.0)),
        1.0 if bool(estimate["local_feasible_before_deadline"]) else 0.0,
        1.0 if bool(estimate["horizontal_feasible_before_deadline"]) else 0.0,
        1.0 if bool(estimate["vertical_feasible_before_deadline"]) else 0.0,
        local_private_queue_load_norm,
        public_offloading_queue_load_norm,
        horizontal_path_queue_load_norm,
        vertical_cloud_path_queue_load_norm,
        pending_task_pressure_norm,
        1.0 if bool(legal_action_mask.get("local", False)) else 0.0,
        1.0 if bool(legal_action_mask.get("horizontal", False)) else 0.0,
        1.0 if bool(legal_action_mask.get("vertical", False)) else 0.0,
        _clip_unit(sum(1 for value in legal_action_mask.values() if bool(value)) / 3.0),
        source_agent_id_norm,
    )


def build_state_window(
    history: Iterable[tuple[float, ...]],
    *,
    state_representation_profile: str = STATE_REPRESENTATION_PROFILE_LEGACY_MINIMAL,
) -> tuple[tuple[float, ...], ...]:
    rows = list(history)[-LOOKBACK_W:]
    if len(rows) < LOOKBACK_W:
        zero_row = rows[0] if rows else zero_state_row_for_profile(state_representation_profile=state_representation_profile)
        padding = [tuple(0.0 for _ in zero_row) for _ in range(LOOKBACK_W - len(rows))]
        rows = padding + rows
    return tuple(rows)


def build_state_window_tensor(window: tuple[tuple[float, ...], ...], *, device: torch.device | None = None) -> torch.Tensor:
    return torch.tensor(window, dtype=torch.float32, device=device)


def build_state_vector(
    *,
    observation: dict[str, Any],
    current_task: Any | None,
    episode_length: int,
    state_representation_profile: str = STATE_REPRESENTATION_PROFILE_LEGACY_MINIMAL,
) -> tuple[float, ...]:
    slot = float(observation.get("slot", 0.0))
    queue_load = float(observation.get("queue_load", 0.0))
    history_length = float(observation.get("history_length", 0.0))
    slot_norm = slot / max(float(episode_length - 1), 1.0)
    queue_norm = min(queue_load / max(float(episode_length), 1.0), 1.0)
    history_norm = min(history_length / max(float(episode_length), 1.0), 1.0)
    if state_representation_profile == STATE_REPRESENTATION_PROFILE_LEGACY_MINIMAL:
        if current_task is None:
            return (slot_norm, queue_norm, history_norm)
        size_norm = min(float(getattr(current_task, "size", 0.0)) / 100.0, 1.0)
        density_norm = min(float(getattr(current_task, "processing_density", 0.0)) / 5.0, 1.0)
        return (slot_norm, size_norm, density_norm)
    if state_representation_profile == STATE_REPRESENTATION_PROFILE_DEADLINE_QUEUE_FEASIBILITY_V1:
        if current_task is None and not observation:
            return zero_state_row_for_profile(state_representation_profile=state_representation_profile)
        return _path_total_slots_features(observation=observation, current_task=current_task, episode_length=episode_length)
    raise ValueError(f"Unsupported state representation profile: {state_representation_profile}")


def legal_action_mask_to_tuple(mask: dict[str, bool]) -> tuple[bool, bool, bool]:
    return (bool(mask.get("local", False)), bool(mask.get("horizontal", False)), bool(mask.get("vertical", False)))


def action_index_to_semantics(action_index: int) -> str:
    try:
        return ACTION_INDEX_TO_SEMANTICS[action_index]
    except KeyError as exc:  # pragma: no cover - defensive
        raise ValueError(f"Unsupported action index: {action_index}") from exc


def semantics_to_action_index(semantics: str) -> int:
    try:
        return SEMANTICS_TO_ACTION_INDEX[semantics]
    except KeyError as exc:  # pragma: no cover - defensive
        raise ValueError(f"Unsupported action semantics: {semantics}") from exc


@dataclass(slots=True, frozen=True)
class ReplayTransition:
    state: tuple[tuple[float, ...], ...]
    action: int
    legal_action_mask: tuple[bool, bool, bool]
    next_state: tuple[tuple[float, ...], ...]
    reward: float
    reward_available: bool
    terminal: bool
    terminal_reason: str | None
    pending_at_horizon: bool
    arrival_slot: int
    completion_or_drop_slot: int | None
    agent_id: int
    episode_id: int
    step_id: int
    source_type: str = DATA_SOURCE

    def __post_init__(self) -> None:
        if len(self.state) != LOOKBACK_W:
            raise ValueError("ReplayTransition.state must contain ten history rows.")
        if len(self.next_state) != LOOKBACK_W:
            raise ValueError("ReplayTransition.next_state must contain ten history rows.")
        if self.action not in ACTION_INDEX_TO_SEMANTICS:
            raise ValueError("ReplayTransition.action must be one of the stable action indices 0, 1, or 2.")
        if len(self.legal_action_mask) != 3:
            raise ValueError("ReplayTransition.legal_action_mask must contain three entries.")
        if self.source_type != DATA_SOURCE:
            raise ValueError("ReplayTransition.source_type must equal environment_rollout.")
        if self.pending_at_horizon and self.terminal:
            raise ValueError("Pending-at-horizon transitions must remain non-terminal.")
        if self.reward_available:
            if not self.terminal:
                raise ValueError("Only terminal completion/drop transitions may mark reward_available=true.")
            if self.terminal_reason not in {"completed", "dropped"}:
                raise ValueError("Terminal reward-bearing transitions must end in completion or drop.")
        if self.terminal and self.terminal_reason not in {"completed", "dropped", "pending_at_horizon"}:
            raise ValueError("Terminal transitions must have a recognized terminal_reason.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "state": [list(row) for row in self.state],
            "action": self.action,
            "legal_action_mask": list(self.legal_action_mask),
            "next_state": [list(row) for row in self.next_state],
            "reward": self.reward,
            "reward_available": self.reward_available,
            "terminal": self.terminal,
            "terminal_reason": self.terminal_reason,
            "pending_at_horizon": self.pending_at_horizon,
            "arrival_slot": self.arrival_slot,
            "completion_or_drop_slot": self.completion_or_drop_slot,
            "agent_id": self.agent_id,
            "episode_id": self.episode_id,
            "step_id": self.step_id,
            "source_type": self.source_type,
        }


@dataclass(slots=True)
class ReplayBatch:
    transitions: tuple[ReplayTransition, ...]
    state_tensor: torch.Tensor
    next_state_tensor: torch.Tensor
    action_tensor: torch.Tensor
    legal_action_mask_tensor: torch.Tensor
    reward_tensor: torch.Tensor
    reward_available_tensor: torch.Tensor
    terminal_tensor: torch.Tensor
    pending_at_horizon_tensor: torch.Tensor

    def to_dict(self) -> dict[str, Any]:
        return {
            "transitions": [transition.to_dict() for transition in self.transitions],
            "batch_size": len(self.transitions),
        }


class ReplayBuffer:
    def __init__(self, capacity: int, *, seed: int) -> None:
        if capacity <= 0:
            raise ValueError("ReplayBuffer.capacity must be positive.")
        self.capacity = capacity
        self._transitions: deque[ReplayTransition] = deque(maxlen=capacity)
        self._seed = seed

    def __len__(self) -> int:
        return len(self._transitions)

    def add(self, transition: ReplayTransition) -> None:
        self._transitions.append(transition)

    def as_list(self) -> list[ReplayTransition]:
        return list(self._transitions)

    def sample(self, batch_size: int, *, rng) -> ReplayBatch:
        if len(self._transitions) < batch_size:
            raise ValueError("ReplayBuffer does not contain enough transitions for the requested batch size.")
        indices = sorted(rng.sample(range(len(self._transitions)), batch_size))
        transitions = tuple(self._transitions[index] for index in indices)
        return self._to_batch(transitions)

    def _to_batch(self, transitions: tuple[ReplayTransition, ...]) -> ReplayBatch:
        state_tensor = torch.tensor([transition.state for transition in transitions], dtype=torch.float32)
        next_state_tensor = torch.tensor([transition.next_state for transition in transitions], dtype=torch.float32)
        action_tensor = torch.tensor([transition.action for transition in transitions], dtype=torch.long)
        legal_action_mask_tensor = torch.tensor([transition.legal_action_mask for transition in transitions], dtype=torch.bool)
        reward_tensor = torch.tensor([transition.reward for transition in transitions], dtype=torch.float32)
        reward_available_tensor = torch.tensor([transition.reward_available for transition in transitions], dtype=torch.bool)
        terminal_tensor = torch.tensor([transition.terminal for transition in transitions], dtype=torch.bool)
        pending_at_horizon_tensor = torch.tensor([transition.pending_at_horizon for transition in transitions], dtype=torch.bool)
        return ReplayBatch(
            transitions=transitions,
            state_tensor=state_tensor,
            next_state_tensor=next_state_tensor,
            action_tensor=action_tensor,
            legal_action_mask_tensor=legal_action_mask_tensor,
            reward_tensor=reward_tensor,
            reward_available_tensor=reward_available_tensor,
            terminal_tensor=terminal_tensor,
            pending_at_horizon_tensor=pending_at_horizon_tensor,
        )
