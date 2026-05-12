from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


DEFAULT_APPROVED_REGISTRY_PATH = Path("resources/papers/hoodie/recovered/user-approved-assumption-registry.json")
APPROVED_FIGURE_7_ITEM_ID = "Figure_7_adjacency"


@dataclass(slots=True)
class TopologyGraph:
    node_ids: tuple[str, ...]
    legal_adjacency: dict[str, tuple[str, ...]] = field(default_factory=dict)

    def is_legal_destination(self, source_node_id: str, destination_node_id: str) -> bool:
        allowed = self.legal_adjacency.get(source_node_id, ())
        return destination_node_id in allowed

    def legal_horizontal_destinations(self, source_node_id: str) -> tuple[str, ...]:
        allowed = tuple(destination for destination in self.legal_adjacency.get(source_node_id, ()) if destination != "cloud" and destination != source_node_id)
        return allowed

    @classmethod
    def from_approved_assumption_registry(cls, registry_path: str | Path = DEFAULT_APPROVED_REGISTRY_PATH) -> "TopologyGraph":
        path = Path(registry_path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        entries = payload.get("entries", [])
        figure = next((entry for entry in entries if entry.get("item_id") == APPROVED_FIGURE_7_ITEM_ID), None)
        if figure is None:
            raise ValueError("Approved Figure_7_adjacency assumption is missing from the registry snapshot")
        proposed_value = figure.get("proposed_value") or {}
        matrix = proposed_value.get("adjacency_matrix")
        if not isinstance(matrix, list) or len(matrix) != 20 or any(not isinstance(row, list) or len(row) != 20 for row in matrix):
            raise ValueError("Approved Figure_7_adjacency adjacency matrix must be 20x20")
        node_ids = tuple(str(index) for index in range(1, 21))
        if any(matrix[index][index] != 0 for index in range(20)):
            raise ValueError("Approved Figure_7_adjacency adjacency matrix must have a zero diagonal")
        if any(matrix[row][col] != matrix[col][row] for row in range(20) for col in range(20)):
            raise ValueError("Approved Figure_7_adjacency adjacency matrix must be symmetric")
        if any(sum(int(value) for value in row) != 3 for row in matrix):
            raise ValueError("Approved Figure_7_adjacency must have degree 3 for every node")
        if sum(sum(int(value) for value in row) for row in matrix) // 2 != 30:
            raise ValueError("Approved Figure_7_adjacency must contain 30 undirected edges")
        legal_adjacency: dict[str, tuple[str, ...]] = {}
        for index, row in enumerate(matrix, start=1):
            destinations = tuple(str(destination_index) for destination_index, value in enumerate(row, start=1) if value)
            legal_adjacency[str(index)] = destinations
        return cls(node_ids=node_ids, legal_adjacency=legal_adjacency)
