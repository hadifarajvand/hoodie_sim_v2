from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Topology:
    mode: str
    adjacency_matrix: list[list[int]]

    @classmethod
    def complete_edge_graph(cls, num_edge_agents: int) -> "Topology":
        matrix = [[0 if i == j else 1 for j in range(num_edge_agents)] for i in range(num_edge_agents)]
        return cls(mode="complete_edge_graph", adjacency_matrix=matrix)

    def legal_horizontal_destinations(self, source_ea_id: int) -> list[int]:
        row = self.adjacency_matrix[source_ea_id - 1]
        return [index + 1 for index, value in enumerate(row) if value and (index + 1) != source_ea_id]

