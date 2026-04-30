from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Sequence

from .offloading_queue import OffloadingQueue
from .public_queue import PublicQueue
from .runtime_model import (
    SharedRuntimeParameters,
    advance_shared_runtime,
    resolve_runtime_terminal_state,
)
from .slot_boundaries import emit_reward_if_terminal
from .task import Task


@dataclass(slots=True)
class SlotEngine:
    """Provides helper methods for slot-phase progression; episode ownership remains external."""

    current_slot: int = 0
    trace_metadata: dict[str, str] | None = None
    runtime_parameters: SharedRuntimeParameters = field(default_factory=SharedRuntimeParameters)
    slot_flow: tuple[str, ...] = (
        "arrival_loading_or_generation",
        "task_creation",
        "observation_construction",
        "legal_action_masking",
        "policy_action_selection",
        "queue_admission",
        "offloading_progression",
        "public_queue_admission_after_offload",
        "execution_progression",
        "completion_drop_handling",
        "delayed_reward_emission",
        "metric_updates",
    )

    def run_slot(self, tasks: Iterable[Task]) -> list[Task]:
        slot_tasks = list(tasks)
        resolved: list[Task] = []

        self.arrival_loading_or_generation(slot_tasks)
        self.task_creation(slot_tasks)
        self.observation_construction(slot_tasks)
        self.legal_action_masking(slot_tasks)
        self.policy_action_selection(slot_tasks)
        self.queue_admission(slot_tasks)
        self.offloading_progression(slot_tasks)
        self.public_queue_admission_after_offload(slot_tasks)
        self.execution_progression(slot_tasks)
        self.completion_drop_handling(slot_tasks)
        self.delayed_reward_emission(slot_tasks)
        self.metric_updates(slot_tasks)

        resolved.extend(slot_tasks)
        self.current_slot += 1
        return resolved

    def slot_flow_names(self) -> tuple[str, ...]:
        return self.slot_flow

    def arrival_loading_or_generation(self, tasks: Sequence[Task]) -> None:
        return None

    def task_creation(self, tasks: Sequence[Task]) -> None:
        return None

    def observation_construction(self, tasks: Sequence[Task]) -> None:
        return None

    def legal_action_masking(self, tasks: Sequence[Task]) -> None:
        return None

    def policy_action_selection(self, tasks: Sequence[Task]) -> None:
        return None

    def queue_admission(self, tasks: Sequence[Task]) -> None:
        return None

    def offloading_progression(self, tasks: Sequence[Task]) -> None:
        return None

    def public_queue_admission_after_offload(self, tasks: Sequence[Task]) -> None:
        return None

    def execution_progression(self, tasks: Sequence[Task]) -> None:
        return None

    def completion_drop_handling(self, tasks: Sequence[Task]) -> None:
        for task in tasks:
            if task.completion_slot is None:
                destination_kind = self._destination_kind(task)
                progress = advance_shared_runtime(task, destination_kind, self.current_slot, self.runtime_parameters)
                resolve_runtime_terminal_state(
                    task,
                    progress.terminal_slot or task.arrival_slot,
                    self.current_slot,
                    self.runtime_parameters,
                )
            elif task.terminal_outcome is None:
                resolve_runtime_terminal_state(
                    task,
                    task.completion_slot,
                    self.current_slot,
                    self.runtime_parameters,
                )

    def delayed_reward_emission(self, tasks: Sequence[Task]) -> None:
        for task in tasks:
            emit_reward_if_terminal(task)

    def metric_updates(self, tasks: Sequence[Task]) -> None:
        return None

    def admit_offload_completion(
        self,
        offloading_queue: OffloadingQueue,
        public_queue: PublicQueue,
        completion_slot: int,
    ) -> bool:
        if offloading_queue.current_head_entered_at is None:
            return False
        if completion_slot <= offloading_queue.current_head_entered_at:
            return False

        task = offloading_queue.dequeue()
        public_queue.enqueue(task, slot=completion_slot)
        return True

    def _destination_kind(self, task: Task) -> str:
        if task.resolved_destination in {"self", None}:
            return "local"
        if task.resolved_destination == "cloud":
            return "cloud"
        return "public"
