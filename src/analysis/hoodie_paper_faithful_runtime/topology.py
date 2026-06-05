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

    @classmethod
    def from_adjacency_matrix(cls, adjacency_matrix: list[list[int]]) -> "Topology":
        return cls(mode="paper_topology_adjacency", adjacency_matrix=adjacency_matrix)

    def legal_horizontal_destinations(self, source_ea_id: int) -> list[int]:
        row = self.adjacency_matrix[source_ea_id - 1]
        return [index + 1 for index, value in enumerate(row) if value and (index + 1) != source_ea_id]

    def is_legal_destination(self, source_ea_id: int, destination_ea_id: int) -> bool:
        return destination_ea_id in self.legal_horizontal_destinations(source_ea_id)

    def to_dict(self) -> dict[str, object]:
        return {
            "topology_mode": self.mode,
            "adjacency_matrix": self.adjacency_matrix,
            "temporary_complete_edge_graph": self.mode == "complete_edge_graph",
            "topology_mode_warning": (
                "complete_edge_graph used as explicit temporary mode"
                if self.mode == "complete_edge_graph"
                else "paper topology adjacency used"
            ),
        }
