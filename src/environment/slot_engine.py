from __future__ import annotations

from dataclasses import dataclass, field

from .offloading_queue import OffloadingQueue
from .public_queue import PublicQueue
from .runtime_model import SharedRuntimeParameters
from .task import Task


@dataclass(slots=True)
class SlotEngine:
    """SlotEngine is helper-only. HoodieGymEnvironment owns episode and slot lifecycle orchestration."""

    current_slot: int = 0
    trace_metadata: dict[str, str] | None = None
    runtime_parameters: SharedRuntimeParameters = field(default_factory=SharedRuntimeParameters)

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
