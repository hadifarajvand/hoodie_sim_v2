from __future__ import annotations

from dataclasses import dataclass, field

from .offloading_queue import OffloadingQueue
from .public_queue import PublicQueue
from .runtime_model import SharedRuntimeParameters
from .task import Task


@dataclass(slots=True)
class SlotEngine:
    """Helper for deterministic slot-boundary transmission completion."""

    current_slot: int = 0
    trace_metadata: dict[str, str] | None = None
    runtime_parameters: SharedRuntimeParameters = field(default_factory=SharedRuntimeParameters)

    def admit_offload_completion(
        self,
        offloading_queue: OffloadingQueue,
        public_queue: PublicQueue,
        completion_slot: int,
    ) -> Task | None:
        if not offloading_queue.tasks:
            return None

        task = offloading_queue.tasks[0]
        transmission_delay_slots = task.metadata.get("transmission_delay_slots")
        if transmission_delay_slots is None:
            return None

        transmission_started_at = task.metadata.get("transmission_started_at")
        if transmission_started_at is None:
            transmission_started_at = int(completion_slot)
            task.transmission_start_slot = int(completion_slot)
            task.metadata["transmission_start_slot"] = int(completion_slot)
            task.metadata["transmission_started_at"] = int(completion_slot)

        finishing_slot = int(transmission_started_at) + int(transmission_delay_slots) - 1
        if completion_slot < finishing_slot:
            return None

        task.transmission_completion_slot = int(completion_slot)
        task.metadata["transmission_completion_slot"] = int(completion_slot)
        task = offloading_queue.dequeue()

        # Enqueue with the current physical slot so the shared-queue kernel's
        # "entered this slot" guard prevents same-slot execution.  Externally,
        # the destination-admission event is the opening of slot t+1.
        public_queue.enqueue(task, slot=completion_slot)
        task.destination_admission_slot = int(completion_slot) + 1
        task.metadata["destination_admission_slot"] = int(completion_slot) + 1
        return task
