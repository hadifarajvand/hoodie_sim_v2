from __future__ import annotations

import numpy as np

from .action_model import TopologyAdapter, TwoStageAction, TwoStageActionModel


class Matchmaker():
    def __init__(
        self,
        id,
        offloading_servers,
        cloud_id: int | None = None,
        topology: TopologyAdapter | None = None,
    ):
        self.id = id
        if topology is None:
            neighbors = np.asarray(offloading_servers, dtype=int)
            edge_node_count = int(max([id, *neighbors.tolist()], default=id) + 1)
            inferred_cloud_id = int(cloud_id if cloud_id is not None else edge_node_count)
            adjacency = np.zeros((edge_node_count, edge_node_count), dtype=int)
            adjacency[id, neighbors] = 1
            topology = TopologyAdapter.from_connection_matrix(adjacency, cloud_node_id=inferred_cloud_id)
        self.topology = topology
        self.action_model = TwoStageActionModel(self.topology)
        self.possible_actions = self.action_model.legacy_destinations(self.id)

    def match_action(self, server_id, action):
        assert server_id == self.id
        decoded = self.action_model.decode_raw_action(server_id, action, strict=True)
        return decoded.legacy_target_node_id

    def decode_action(self, server_id, action, strict: bool = True) -> TwoStageAction:
        assert server_id == self.id
        return self.action_model.decode_raw_action(server_id, action, strict=strict)

    def get_action_space(self):
        return self.action_model.build_action_space(self.id)

    def get_number_of_actions(self):
        return self.action_model.action_count(self.id)

    def get_rows(self):
        return self.possible_actions
