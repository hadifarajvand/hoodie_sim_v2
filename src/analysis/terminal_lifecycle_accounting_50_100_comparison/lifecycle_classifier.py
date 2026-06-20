from __future__ import annotations

from collections import Counter
from typing import Any

from src.analysis.evaluation_instrumentation_reward_state_diagnostic.instrumented_evaluator import action_order, normalize_action_name
from src.environment.reward_timing import phi_private

TERMINAL_OUTCOME_EVENT_TYPES = {"task_completed", "task_dropped"}
LIFECYCLE_ONLY_EVENT_TYPES = {
    "deadline_reached",
    "deadline_expired",
    "reward_emitted",
    "execution_started",
    "transmission_started",
    "transmission_completed",
    "execution_completed",
}
PENDING_EVENT_TYPES = {"pending_at_horizon"}


def canonical_task_key(trace_id: str, episode_id: int, task_id: int | str) -> str:
    return f"{trace_id}:{episode_id}:{int(task_id)}"


def classify_event_type(event_type: str) -> str:
    if event_type in TERMINAL_OUTCOME_EVENT_TYPES:
        return "terminal_outcome_event"
    if event_type == "reward_emitted":
        return "reward_event"
    if event_type in LIFECYCLE_ONLY_EVENT_TYPES:
        return "lifecycle_event_only"
    if event_type in PENDING_EVENT_TYPES:
        return "pending_event"
    return "other"


def terminal_outcome_from_event_types(event_types: set[str], *, pending_evidence: bool) -> str:
    if "task_completed" in event_types:
        return "completed"
    if "task_dropped" in event_types:
        return "dropped"
    if pending_evidence:
        return "pending_at_horizon"
    return "unknown"


def terminal_reward_for_outcome(outcome: str, *, arrival_slot: int | None, completion_or_drop_slot: int | None, drop_penalty: float = 40.0) -> float:
    if outcome == "completed" and arrival_slot is not None and completion_or_drop_slot is not None:
        return -float(phi_private(int(completion_or_drop_slot), int(arrival_slot)))
    if outcome == "dropped":
        return -float(drop_penalty)
    return 0.0


def empty_event_classification() -> dict[str, Any]:
    return {
        "terminal_outcome_event_count": 0,
        "lifecycle_only_event_count": 0,
        "reward_event_count": 0,
        "pending_event_count": 0,
        "event_type_counts": {event_type: 0 for event_type in sorted(TERMINAL_OUTCOME_EVENT_TYPES | LIFECYCLE_ONLY_EVENT_TYPES | PENDING_EVENT_TYPES)},
        "sample_events": [],
    }


def empty_completion_path_audit() -> dict[str, Any]:
    return {
        "execution_completed_event_count": 0,
        "task_completed_event_count": 0,
        "completed_canonical_task_count": 0,
        "deadline_reached_event_count": 0,
        "deadline_expired_event_count": 0,
        "task_dropped_event_count": 0,
        "reward_emitted_event_count": 0,
        "pending_at_horizon_count": 0,
        "execution_completed_but_no_task_completed_detected": False,
        "task_completed_but_no_reward_detected": False,
        "deadline_reached_then_task_dropped_duplicate_detected": False,
        "reward_emitted_without_terminal_outcome_detected": False,
        "terminal_outcome_without_reward_detected": False,
    }


def legal_action_mask_signature(mask: dict[str, bool]) -> str:
    return "|".join(f"{action}={int(bool(mask.get(action, False)))}" for action in action_order())


def normalize_selected_action(action: str | None) -> str | None:
    return normalize_action_name(action)
