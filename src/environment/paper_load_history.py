from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .topology import TopologyGraph


@dataclass(slots=True)
class PaperLoadHistory:
    window_w: int
    node_order: tuple[str, ...]
    load_history_matrix: tuple[tuple[int, ...], ...]
    load_history_shape: tuple[int, int]
    active_queue_counts_by_node: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return {
            "window_w": self.window_w,
            "node_order": list(self.node_order),
            "load_history_matrix": [list(row) for row in self.load_history_matrix],
            "load_history_shape": list(self.load_history_shape),
            "active_queue_counts_by_node": dict(self.active_queue_counts_by_node),
        }


def build_paper_load_history(topology: TopologyGraph, active_queue_counts_by_node: dict[str, int], *, window_w: int = 10) -> PaperLoadHistory:
    node_order = tuple(list(topology.node_ids) + ["cloud"])
    row = tuple(int(active_queue_counts_by_node.get(node, 0)) for node in node_order)
    matrix = tuple(tuple(row) for _ in range(window_w))
    return PaperLoadHistory(
        window_w=window_w,
        node_order=node_order,
        load_history_matrix=matrix,
        load_history_shape=(window_w, len(node_order)),
        active_queue_counts_by_node=dict(active_queue_counts_by_node),
    )

