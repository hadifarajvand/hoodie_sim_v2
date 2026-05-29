from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .topology import TopologyGraph


@dataclass(slots=True)
class HoodieNeighborGraph:
    topology: TopologyGraph
    neighbor_reachability: dict[str, tuple[str, ...]] = field(default_factory=dict)

    @classmethod
    def build(cls, topology: TopologyGraph) -> "HoodieNeighborGraph":
        reachability = {node: topology.legal_horizontal_destinations(node) for node in topology.node_ids}
        return cls(topology=topology, neighbor_reachability=reachability)

    def get_neighbors(self, node_id: str) -> tuple[str, ...]:
        return self.neighbor_reachability.get(node_id, ())

    def is_reachable(self, src: str, dst: str) -> bool:
        if dst == "cloud":
            return True
        return self.topology.is_legal_destination(src, dst)

    def get_available_destinations(self, src: str, congestion_state: dict[str, bool]) -> tuple[str, ...]:
        neighbors = tuple(dst for dst in self.get_neighbors(src) if not congestion_state.get(dst, False))
        if not neighbors:
            return ("cloud",)
        return ("local",) + neighbors + ("cloud",)

    def to_dict(self) -> dict[str, Any]:
        return {
            "neighbor_reachability": {node: list(neighbors) for node, neighbors in self.neighbor_reachability.items()},
            "node_count": len(self.neighbor_reachability),
            "deterministic_topology_behavior": True,
        }
