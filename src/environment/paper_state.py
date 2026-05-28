from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .topology import TopologyGraph

PAPER_STATE_VERSION = "paper_state_v1"
LEGACY_COMPATIBILITY_LABEL = "legacy_compact_state"


@dataclass(slots=True)
class WaitingTimeContract:
    private_waiting_time_slots: int
    offloading_waiting_time_slots: int
    waiting_time_source: str
    waiting_time_exactness: str


@dataclass(slots=True)
class PublicQueueVectorContract:
    public_queue_lengths_by_destination: tuple[int, ...]
    public_queue_vector_length: int
    public_queue_destination_order: tuple[str, ...]
    public_queue_source_scope: str


@dataclass(slots=True)
class PaperLoadHistoryContract:
    window_w: int
    node_count: int
    load_history_matrix: tuple[tuple[int, ...], ...]
    load_history_shape: tuple[int, int]
    load_history_node_order: tuple[str, ...]
    active_queue_counts_by_node: dict[str, int]


@dataclass(slots=True)
class ForecastInputContract:
    forecast_input_matrix: tuple[tuple[int, ...], ...]
    forecast_input_shape: tuple[int, int]
    forecast_input_source: str
    forecast_output_status: str


@dataclass(slots=True)
class PaperStateSnapshot:
    source_agent_id: str
    task_size_mbits: float
    private_waiting_time_slots: int
    offloading_waiting_time_slots: int
    public_queue_lengths_by_destination: tuple[int, ...]
    public_queue_destination_order: tuple[str, ...]
    load_history_matrix: tuple[tuple[int, ...], ...]
    load_history_shape: tuple[int, int]
    load_history_node_order: tuple[str, ...]
    load_history_window_w: int
    forecast_input_matrix: tuple[tuple[int, ...], ...]
    forecast_input_shape: tuple[int, int]
    forecast_input_source: str
    forecast_output_status: str
    active_queue_counts_by_node: dict[str, int]
    legal_destination_ids: tuple[str, ...]
    paper_state_version: str = PAPER_STATE_VERSION
    waiting_time_source: str = "queue_head_age_approximation"
    waiting_time_exactness: str = "approximate"
    public_queue_source_scope: str = "source_visible_public_queues"
    legacy_compact_state: tuple[float, float, float] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_agent_id": self.source_agent_id,
            "task_size_mbits": self.task_size_mbits,
            "private_waiting_time_slots": self.private_waiting_time_slots,
            "offloading_waiting_time_slots": self.offloading_waiting_time_slots,
            "waiting_time_source": self.waiting_time_source,
            "waiting_time_exactness": self.waiting_time_exactness,
            "public_queue_lengths_by_destination": list(self.public_queue_lengths_by_destination),
            "public_queue_vector_length": len(self.public_queue_lengths_by_destination),
            "public_queue_destination_order": list(self.public_queue_destination_order),
            "public_queue_source_scope": self.public_queue_source_scope,
            "load_history_matrix": [list(row) for row in self.load_history_matrix],
            "load_history_shape": list(self.load_history_shape),
            "load_history_node_order": list(self.load_history_node_order),
            "load_history_window_w": self.load_history_window_w,
            "forecast_input_matrix": [list(row) for row in self.forecast_input_matrix],
            "forecast_input_shape": list(self.forecast_input_shape),
            "forecast_input_source": self.forecast_input_source,
            "forecast_output_status": self.forecast_output_status,
            "active_queue_counts_by_node": dict(self.active_queue_counts_by_node),
            "legal_destination_ids": list(self.legal_destination_ids),
            "paper_state_version": self.paper_state_version,
            "legacy_compact_state": list(self.legacy_compact_state) if self.legacy_compact_state is not None else None,
        }


def build_legacy_compact_state(*, slot: int, queue_load: int, history_length: int) -> tuple[float, float, float]:
    return (float(slot), float(queue_load), float(history_length))


def build_waiting_time_contract(*, private_waiting_time_slots: int, offloading_waiting_time_slots: int, source: str, exactness: str = "approximate") -> WaitingTimeContract:
    return WaitingTimeContract(
        private_waiting_time_slots=private_waiting_time_slots,
        offloading_waiting_time_slots=offloading_waiting_time_slots,
        waiting_time_source=source,
        waiting_time_exactness=exactness,
    )


def build_public_queue_vector_contract(*, destination_order: tuple[str, ...], lengths: dict[str, int], source_scope: str = "source_visible_public_queues") -> PublicQueueVectorContract:
    vector = tuple(int(lengths.get(destination, 0)) for destination in destination_order)
    return PublicQueueVectorContract(
        public_queue_lengths_by_destination=vector,
        public_queue_vector_length=len(vector),
        public_queue_destination_order=destination_order,
        public_queue_source_scope=source_scope,
    )


def build_load_history_contract(*, window_w: int, topology: TopologyGraph, active_queue_counts_by_node: dict[str, int]) -> PaperLoadHistoryContract:
    node_order = tuple(list(topology.node_ids) + ["cloud"])
    matrix = tuple(tuple(int(active_queue_counts_by_node.get(node, 0)) for node in node_order) for _ in range(window_w))
    return PaperLoadHistoryContract(
        window_w=window_w,
        node_count=len(node_order),
        load_history_matrix=matrix,
        load_history_shape=(window_w, len(node_order)),
        load_history_node_order=node_order,
        active_queue_counts_by_node=dict(active_queue_counts_by_node),
    )


def build_forecast_input_contract(*, active_queue_counts_by_node: dict[str, int], node_order: tuple[str, ...]) -> ForecastInputContract:
    row = tuple(int(active_queue_counts_by_node.get(node, 0)) for node in node_order)
    matrix = (row,)
    return ForecastInputContract(
        forecast_input_matrix=matrix,
        forecast_input_shape=(1, len(row)),
        forecast_input_source="active_queue_counts_by_node",
        forecast_output_status="contract_only_not_trained",
    )


def build_paper_state_snapshot(
    *,
    source_agent_id: str,
    task_size_mbits: float,
    topology: TopologyGraph,
    public_queue_lengths_by_destination: dict[str, int],
    active_queue_counts_by_node: dict[str, int],
    private_waiting_time_slots: int,
    offloading_waiting_time_slots: int,
    load_history_window_w: int = 10,
    legacy_slot: int = 0,
    queue_load: int = 0,
    history_length: int = 0,
) -> PaperStateSnapshot:
    public_order = tuple(sorted(public_queue_lengths_by_destination))
    legal_destination_ids = tuple(topology.legal_horizontal_destinations(source_agent_id) + ("cloud",))
    load_history_contract = build_load_history_contract(window_w=load_history_window_w, topology=topology, active_queue_counts_by_node=active_queue_counts_by_node)
    forecast = build_forecast_input_contract(active_queue_counts_by_node=active_queue_counts_by_node, node_order=load_history_contract.load_history_node_order)
    return PaperStateSnapshot(
        source_agent_id=source_agent_id,
        task_size_mbits=float(task_size_mbits),
        private_waiting_time_slots=int(private_waiting_time_slots),
        offloading_waiting_time_slots=int(offloading_waiting_time_slots),
        public_queue_lengths_by_destination=tuple(int(public_queue_lengths_by_destination.get(destination, 0)) for destination in public_order),
        public_queue_destination_order=public_order,
        load_history_matrix=load_history_contract.load_history_matrix,
        load_history_shape=load_history_contract.load_history_shape,
        load_history_node_order=load_history_contract.load_history_node_order,
        load_history_window_w=load_history_contract.window_w,
        forecast_input_matrix=forecast.forecast_input_matrix,
        forecast_input_shape=forecast.forecast_input_shape,
        forecast_input_source=forecast.forecast_input_source,
        forecast_output_status=forecast.forecast_output_status,
        active_queue_counts_by_node=dict(active_queue_counts_by_node),
        legal_destination_ids=legal_destination_ids,
        legacy_compact_state=build_legacy_compact_state(slot=legacy_slot, queue_load=queue_load, history_length=history_length),
    )

