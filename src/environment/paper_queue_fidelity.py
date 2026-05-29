from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class PaperQueueFidelitySnapshot:
    private_queue_length: int
    offloading_queue_length: int
    public_queue_lengths_by_destination: dict[str, int]
    cloud_public_queue_lengths: dict[str, int]
    active_queue_counts_by_node: dict[str, int]
    queue_ordering_policy: str = "FIFO"
    queue_fidelity_version: str = "paper_queue_fidelity_v1"

    def to_dict(self) -> dict[str, Any]:
        return {
            "private_queue_length": self.private_queue_length,
            "offloading_queue_length": self.offloading_queue_length,
            "public_queue_lengths_by_destination": dict(self.public_queue_lengths_by_destination),
            "cloud_public_queue_lengths": dict(self.cloud_public_queue_lengths),
            "active_queue_counts_by_node": dict(self.active_queue_counts_by_node),
            "queue_ordering_policy": self.queue_ordering_policy,
            "queue_fidelity_version": self.queue_fidelity_version,
        }

