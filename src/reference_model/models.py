"""Immutable data models for the reference lifecycle kernel."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ActionType(str, Enum):
    LOCAL_COMPUTE = "local_compute"
    HORIZONTAL_OFFLOAD = "horizontal_offload"
    VERTICAL_OFFLOAD = "vertical_offload"


class TerminalStatus(str, Enum):
    COMPLETED = "completed"
    DROPPED_TIMEOUT = "dropped_timeout"


@dataclass(frozen=True, slots=True)
class TaskIdentity:
    task_id: str
    origin_edge_agent: str
    destination_target: str


@dataclass(frozen=True, slots=True)
class TaskWorkload:
    task_size: int
    timeout_slot: int
    current_slot: int


@dataclass(frozen=True, slots=True)
class ActionInput:
    action_type: ActionType
    destination_target: str | None = None

