from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class TopologyGraph:
    node_ids: tuple[str, ...]
    legal_adjacency: dict[str, tuple[str, ...]] = field(default_factory=dict)

    def is_legal_destination(self, source_node_id: str, destination_node_id: str) -> bool:
        allowed = self.legal_adjacency.get(source_node_id, ())
        return destination_node_id in allowed
