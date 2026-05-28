from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .topology import TopologyGraph

ACTION_ENCODING_VERSION = "paper_destination_action_space_v1"


@dataclass(slots=True)
class PaperActionSpace:
    paper_action_count: int
    action_index_to_destination: tuple[str, ...]
    destination_to_action_index: dict[str, int]
    local_action_index: int
    cloud_action_index: int
    horizontal_action_indices: tuple[int, ...]
    invalid_action_indices: tuple[int, ...]
    action_encoding_version: str = ACTION_ENCODING_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "paper_action_count": self.paper_action_count,
            "action_index_to_destination": list(self.action_index_to_destination),
            "destination_to_action_index": dict(self.destination_to_action_index),
            "local_action_index": self.local_action_index,
            "cloud_action_index": self.cloud_action_index,
            "horizontal_action_indices": list(self.horizontal_action_indices),
            "invalid_action_indices": list(self.invalid_action_indices),
            "action_encoding_version": self.action_encoding_version,
        }


def build_paper_action_space(topology: TopologyGraph, *, source_agent_id: str, include_reserved_invalid: bool = True) -> PaperActionSpace:
    edge_nodes = list(topology.node_ids)
    destinations = ["local", *edge_nodes, "cloud"]
    destination_to_action_index = {destination: index for index, destination in enumerate(destinations)}
    horizontal_indices = tuple(destination_to_action_index[node] for node in topology.legal_horizontal_destinations(source_agent_id))
    return PaperActionSpace(
        paper_action_count=len(destinations),
        action_index_to_destination=tuple(destinations),
        destination_to_action_index=destination_to_action_index,
        local_action_index=destination_to_action_index["local"],
        cloud_action_index=destination_to_action_index["cloud"],
        horizontal_action_indices=horizontal_indices,
        invalid_action_indices=(),
    )


def build_legal_action_mask(topology: TopologyGraph, *, source_agent_id: str, include_reserved_invalid: bool = True, cloud_disabled: bool = False) -> dict[str, Any]:
    action_space = build_paper_action_space(topology, source_agent_id=source_agent_id, include_reserved_invalid=include_reserved_invalid)
    legal_action_mask = [False] * action_space.paper_action_count
    legal_action_reasons: dict[str, str] = {}
    illegal_action_reasons: dict[str, str] = {}

    legal_action_mask[action_space.local_action_index] = True
    legal_action_reasons["local"] = "local/self compute is always legal for pending tasks"
    for destination in topology.node_ids:
        index = action_space.destination_to_action_index[destination]
        if destination == source_agent_id:
            illegal_action_reasons[destination] = "self horizontal destination is illegal"
            continue
        if topology.is_legal_destination(source_agent_id, destination):
            legal_action_mask[index] = True
            legal_action_reasons[destination] = "exact topology neighbor is legal for horizontal offloading"
        else:
            illegal_action_reasons[destination] = "non-neighbor edge destination is illegal"

    cloud_index = action_space.cloud_action_index
    if cloud_disabled:
        illegal_action_reasons["cloud"] = "cloud destination disabled by config"
    else:
        legal_action_mask[cloud_index] = True
        legal_action_reasons["cloud"] = "cloud destination is legal for vertical offloading"

    return {
        "source_agent_id": source_agent_id,
        "topology_source": "recovered_user_approved_assumption_registry:Figure_7_adjacency",
        "mask_encoding_version": "paper_destination_mask_v1",
        "legal_action_mask": legal_action_mask,
        "legal_action_reasons": legal_action_reasons,
        "illegal_action_reasons": illegal_action_reasons,
        "paper_action_count": action_space.paper_action_count,
    }
