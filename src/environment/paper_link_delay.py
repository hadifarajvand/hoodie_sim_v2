from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class PaperLinkDelayContract:
    source_node_id: str
    destination_node_id: str
    link_type: str
    task_size_mbits: float
    data_rate_mbps: float
    transmission_delay_seconds: float
    transmission_delay_slots: int
    link_delay_source: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_node_id": self.source_node_id,
            "destination_node_id": self.destination_node_id,
            "link_type": self.link_type,
            "task_size_mbits": self.task_size_mbits,
            "data_rate_mbps": self.data_rate_mbps,
            "transmission_delay_seconds": self.transmission_delay_seconds,
            "transmission_delay_slots": self.transmission_delay_slots,
            "link_delay_source": self.link_delay_source,
        }


def build_link_delay_contract(
    *,
    source_node_id: str,
    destination_node_id: str,
    link_type: str,
    task_size_mbits: float,
    data_rate_mbps: float,
    link_delay_source: str,
    slot_seconds: float = 1.0,
) -> PaperLinkDelayContract:
    transmission_delay_seconds = task_size_mbits / data_rate_mbps
    transmission_delay_slots = max(1, math.ceil(transmission_delay_seconds / slot_seconds))
    return PaperLinkDelayContract(
        source_node_id=source_node_id,
        destination_node_id=destination_node_id,
        link_type=link_type,
        task_size_mbits=task_size_mbits,
        data_rate_mbps=data_rate_mbps,
        transmission_delay_seconds=transmission_delay_seconds,
        transmission_delay_slots=transmission_delay_slots,
        link_delay_source=link_delay_source,
    )
