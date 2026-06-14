from __future__ import annotations

from dataclasses import dataclass
from numbers import Integral, Real
from typing import Iterable

import numpy as np


def _is_integer_like(value: object) -> bool:
    return isinstance(value, Integral) or (isinstance(value, Real) and float(value).is_integer())


def _as_int(value: object, field_name: str) -> int:
    if not _is_integer_like(value):
        raise ValueError(f"{field_name} must be an integer-like value, got {value!r}")
    return int(value)


@dataclass(frozen=True)
class TwoStageAction:
    raw_action_id: int
    source_node_id: int
    first_stage_decision: str
    destination_node_id: int | None
    destination_type: str
    is_valid: bool
    invalid_reason: str | None
    adjacency_allowed: bool | None
    cloud_target: bool
    d_n_1: int
    d_nk_2: dict[int, int]
    paper_destination_nodes: tuple[int, ...]
    paper_d_nk_2: tuple[int, ...]
    dm2_timing: str
    requires_separate_dm2_at_offloading_queue_exit: bool

    @property
    def legacy_target_node_id(self) -> int:
        return self.source_node_id if self.destination_node_id is None else self.destination_node_id


@dataclass(frozen=True)
class TopologyAdapter:
    connection_matrix: np.ndarray
    cloud_node_id: int

    @classmethod
    def from_connection_matrix(cls, connection_matrix: Iterable[Iterable[float]], cloud_node_id: int) -> "TopologyAdapter":
        matrix = np.asarray(connection_matrix)
        if matrix.ndim != 2:
            raise ValueError("connection_matrix must be a 2D matrix")
        edge_node_count = matrix.shape[0]
        if matrix.shape[1] < edge_node_count:
            raise ValueError("connection_matrix must have at least one destination column per edge node")
        if cloud_node_id < edge_node_count:
            raise ValueError("cloud_node_id must be greater than or equal to the edge-node count")
        return cls(connection_matrix=matrix, cloud_node_id=int(cloud_node_id))

    @property
    def number_of_edge_nodes(self) -> int:
        return int(self.connection_matrix.shape[0])

    def horizontal_neighbors(self, source_node_id: int) -> list[int]:
        source = _as_int(source_node_id, "source_node_id")
        if source < 0 or source >= self.number_of_edge_nodes:
            raise ValueError(f"source_node_id must be within [0, {self.number_of_edge_nodes - 1}], got {source}")
        row = self.connection_matrix[source, : self.number_of_edge_nodes]
        return [int(index) for index, value in enumerate(row) if index != source and value != 0]

    def is_horizontal_allowed(self, source_node_id: int, destination_node_id: int) -> bool:
        source = _as_int(source_node_id, "source_node_id")
        destination = _as_int(destination_node_id, "destination_node_id")
        if source < 0 or source >= self.number_of_edge_nodes:
            return False
        if destination < 0 or destination >= self.number_of_edge_nodes:
            return False
        if source == destination:
            return False
        return bool(self.connection_matrix[source, destination] != 0)

    def is_cloud_target(self, destination_node_id: int) -> bool:
        return _as_int(destination_node_id, "destination_node_id") == self.cloud_node_id

    def action_destinations(self, source_node_id: int) -> list[int]:
        return [source_node_id, *self.horizontal_neighbors(source_node_id), self.cloud_node_id]


class TwoStageActionModel:
    def __init__(self, topology: TopologyAdapter) -> None:
        self.topology = topology

    def paper_destination_nodes(self, source_node_id: int) -> tuple[int, ...]:
        source = _as_int(source_node_id, "source_node_id")
        if source < 0 or source >= self.topology.number_of_edge_nodes:
            raise ValueError(f"source_node_id must be within [0, {self.topology.number_of_edge_nodes - 1}], got {source}")
        return tuple([node for node in range(self.topology.number_of_edge_nodes) if node != source] + [self.topology.cloud_node_id])

    def _paper_destination_vector(self, source_node_id: int, destination_node_id: int | None) -> tuple[int, ...]:
        nodes = self.paper_destination_nodes(source_node_id)
        vector = [0] * len(nodes)
        if destination_node_id is None:
            return tuple(vector)
        destination = _as_int(destination_node_id, "destination_node_id")
        if destination not in nodes:
            raise ValueError(
                f"destination_node_id {destination} is not representable in the paper-facing destination vector for source_node_id {source_node_id}"
            )
        vector[nodes.index(destination)] = 1
        return tuple(vector)

    def validate_paper_action_contract(self, action: TwoStageAction) -> None:
        paper_sum = sum(int(value) for value in action.paper_d_nk_2)
        if action.d_n_1 == 1:
            if paper_sum != 0:
                raise ValueError("local/private actions must map to an all-zero paper destination vector")
        elif action.d_n_1 == 0:
            if paper_sum != 1:
                raise ValueError("offload actions must map to exactly one active paper destination")
        else:
            raise ValueError(f"invalid d_n_1 polarity {action.d_n_1!r}")
        if paper_sum > 1:
            raise ValueError("paper destination vector must activate at most one destination")

    def build_action_space(self, source_node_id: int) -> list[TwoStageAction]:
        source = _as_int(source_node_id, "source_node_id")
        if source < 0 or source >= self.topology.number_of_edge_nodes:
            raise ValueError(f"source_node_id must be within [0, {self.topology.number_of_edge_nodes - 1}], got {source}")

        paper_destination_nodes = self.paper_destination_nodes(source)

        actions = [
            TwoStageAction(
                raw_action_id=0,
                source_node_id=source,
                first_stage_decision="local",
                destination_node_id=None,
                destination_type="local",
                is_valid=True,
                invalid_reason=None,
                adjacency_allowed=True,
                cloud_target=False,
                d_n_1=1,
                d_nk_2={},
                paper_destination_nodes=paper_destination_nodes,
                paper_d_nk_2=self._paper_destination_vector(source, None),
                dm2_timing="not_applicable",
                requires_separate_dm2_at_offloading_queue_exit=False,
            )
        ]
        self.validate_paper_action_contract(actions[0])

        for index, destination in enumerate(self.topology.horizontal_neighbors(source), start=1):
            action = TwoStageAction(
                raw_action_id=index,
                source_node_id=source,
                first_stage_decision="offload",
                destination_node_id=destination,
                destination_type="horizontal_edge",
                is_valid=True,
                invalid_reason=None,
                adjacency_allowed=True,
                cloud_target=False,
                d_n_1=0,
                d_nk_2={int(destination): 1},
                paper_destination_nodes=paper_destination_nodes,
                paper_d_nk_2=self._paper_destination_vector(source, destination),
                dm2_timing="collapsed_at_arrival",
                requires_separate_dm2_at_offloading_queue_exit=True,
            )
            self.validate_paper_action_contract(action)
            actions.append(action)

        cloud_action = TwoStageAction(
            raw_action_id=len(actions),
            source_node_id=source,
            first_stage_decision="offload",
            destination_node_id=self.topology.cloud_node_id,
            destination_type="vertical_cloud",
            is_valid=True,
            invalid_reason=None,
            adjacency_allowed=True,
            cloud_target=True,
            d_n_1=0,
            d_nk_2={int(self.topology.cloud_node_id): 1},
            paper_destination_nodes=paper_destination_nodes,
            paper_d_nk_2=self._paper_destination_vector(source, self.topology.cloud_node_id),
            dm2_timing="collapsed_at_arrival",
            requires_separate_dm2_at_offloading_queue_exit=True,
        )
        self.validate_paper_action_contract(cloud_action)
        actions.append(cloud_action)
        return actions

    def action_count(self, source_node_id: int) -> int:
        return len(self.build_action_space(source_node_id))

    def legacy_destinations(self, source_node_id: int) -> np.ndarray:
        return np.asarray(self.topology.action_destinations(source_node_id), dtype=int)

    def decode_raw_action(self, source_node_id: int, raw_action_id: object, strict: bool = False) -> TwoStageAction:
        source = _as_int(source_node_id, "source_node_id")
        if not _is_integer_like(raw_action_id):
            return self._invalid_action(source, raw_action_id, "raw_action_id must be an integer-like value", strict)
        raw_index = int(raw_action_id)
        action_space = self.build_action_space(source)
        if raw_index < 0 or raw_index >= len(action_space):
            return self._invalid_action(
                source,
                raw_index,
                f"raw_action_id {raw_index} is outside the valid action space [0, {len(action_space) - 1}]",
                strict,
            )
        return action_space[raw_index]

    def encode_destination(self, source_node_id: int, destination_node_id: int | None) -> int:
        source = _as_int(source_node_id, "source_node_id")
        if destination_node_id is None:
            return 0
        destination = _as_int(destination_node_id, "destination_node_id")
        action_space = self.build_action_space(source)
        for action in action_space:
            if action.destination_node_id == destination:
                return action.raw_action_id
        raise ValueError(
            f"destination_node_id {destination} is not legal for source_node_id {source}"
        )

    def validate_explicit_choice(
        self,
        source_node_id: int,
        first_stage_decision: str,
        destination_node_id: int | None = None,
        destination_node_ids: list[int] | tuple[int, ...] | None = None,
        strict: bool = False,
    ) -> TwoStageAction:
        source = _as_int(source_node_id, "source_node_id")
        if first_stage_decision == "local":
            if destination_node_id is not None or destination_node_ids:
                return self._invalid_action(
                    source,
                    0,
                    "local actions must not specify a destination",
                    strict,
                )
            return self.build_action_space(source)[0]

        if first_stage_decision != "offload":
            return self._invalid_action(source, 0, f"unknown first_stage_decision {first_stage_decision!r}", strict)

        if destination_node_ids is not None:
            if len(destination_node_ids) != 1:
                return self._invalid_action(
                    source,
                    0,
                    "offload actions must specify exactly one destination",
                    strict,
                )
            destination_node_id = destination_node_ids[0]

        if destination_node_id is None:
            return self._invalid_action(
                source,
                0,
                "offload actions must specify exactly one destination",
                strict,
            )

        destination = _as_int(destination_node_id, "destination_node_id")
        if destination == source:
            return self._invalid_action(source, 0, "self-offload is not allowed", strict)
        if destination == self.topology.cloud_node_id:
            return self.build_action_space(source)[-1]
        if self.topology.is_horizontal_allowed(source, destination):
            action_space = self.build_action_space(source)
            for action in action_space[1:-1]:
                if action.destination_node_id == destination:
                    return action
        return self._invalid_action(
            source,
            0,
            f"destination_node_id {destination} is not a legal neighbor for source_node_id {source}",
            strict,
        )

    def _invalid_action(self, source_node_id: int, raw_action_id: object, reason: str, strict: bool) -> TwoStageAction:
        action = TwoStageAction(
            raw_action_id=int(raw_action_id) if _is_integer_like(raw_action_id) else -1,
            source_node_id=source_node_id,
            first_stage_decision="invalid",
            destination_node_id=None,
            destination_type="invalid",
            is_valid=False,
            invalid_reason=reason,
            adjacency_allowed=False,
            cloud_target=False,
            d_n_1=-1,
            d_nk_2={},
            paper_destination_nodes=self.paper_destination_nodes(source_node_id),
            paper_d_nk_2=tuple(),
            dm2_timing="not_applicable",
            requires_separate_dm2_at_offloading_queue_exit=False,
        )
        if strict:
            raise ValueError(
                f"Invalid two-stage action for source_node_id {source_node_id}: raw_action_id={raw_action_id!r}. {reason}"
            )
        return action
