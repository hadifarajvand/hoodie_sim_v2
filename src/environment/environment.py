from __future__ import annotations

from dataclasses import dataclass, field

from .deadline_rules import has_expired
from .runtime_model import SharedRuntimeParameters, resolve_runtime_terminal_state
from .topology import TopologyGraph
from .task import Task
from src.policies.action_masking import select_legal_action
from src.policies.policy_interface import PolicyContext


@dataclass(slots=True)
class TaskStateSnapshot:
    active_task_ids: tuple[int, ...] = ()
    terminal_outcomes_by_task_id: dict[int, str] = field(default_factory=dict)


@dataclass(slots=True)
class QueueStateSnapshot:
    private_queue_heads: dict[str, int | None] = field(default_factory=dict)
    offloading_queue_heads: dict[str, int | None] = field(default_factory=dict)
    public_queue_heads: dict[tuple[str, str], int | None] = field(default_factory=dict)


@dataclass(slots=True)
class MetricStateSnapshot:
    aggregate_metrics: dict[str, float] = field(default_factory=dict)


@dataclass(slots=True)
class EnvironmentState:
    current_slot: int
    task_state: TaskStateSnapshot = field(default_factory=TaskStateSnapshot)
    queue_state: QueueStateSnapshot = field(default_factory=QueueStateSnapshot)
    topology_state: TopologyGraph | None = None
    metric_state: MetricStateSnapshot = field(default_factory=MetricStateSnapshot)


def apply_policy_action(
    task: Task,
    context: PolicyContext,
    action: str,
    resolved_destination: str | None = None,
) -> str:
    selected_action = select_legal_action(context, action)
    task.selected_action = selected_action
    task.resolved_destination = resolved_destination
    return selected_action


def finalize_task_runtime_state(task: Task, current_slot: int) -> None:
    finalize_task_runtime_state_with_parameters(task, current_slot, None)


def finalize_task_runtime_state_with_parameters(
    task: Task,
    current_slot: int,
    parameters: SharedRuntimeParameters | None,
) -> None:
    if task.terminal_outcome is not None:
        task.drop_flag = task.terminal_outcome == "dropped"
        task.reward_emitted = task.terminal_outcome in {"completed", "dropped"}
        return
    if task.completion_slot is not None:
        resolve_runtime_terminal_state(task, task.completion_slot, current_slot, parameters)
    elif has_expired(task, current_slot):
        task.terminal_outcome = "dropped"
        task.drop_flag = True
    if task.terminal_outcome in {"completed", "dropped"}:
        task.reward_emitted = True
