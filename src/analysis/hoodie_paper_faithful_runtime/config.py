from __future__ import annotations

from dataclasses import asdict, dataclass, field

ALLOWED_TOPOLOGY_MODES = {
    "complete_edge_graph",
    "paper_topology_adjacency",
    "unknown_from_ocr_requires_pdf_visual_confirmation",
}


@dataclass(slots=True)
class EpisodeConfig:
    episode_id: str = "episode-001"
    num_edge_agents: int = 20
    cloud_node_id: int = 21
    topology_mode: str = "complete_edge_graph"
    adjacency_matrix: list[list[int]] | None = None
    slot_count: int = 110
    action_slot_count: int = 100
    drain_slot_count: int = 10
    slot_duration_sec: float = 0.1
    task_arrival_probability: float = 0.5
    task_size_range_mbits: tuple[float, float] = (2.0, 5.0)
    task_size_values_mbits: tuple[float, ...] = tuple(round(2.0 + i * 0.1, 10) for i in range(31))
    processing_density_gcycles_per_mbit: float = 0.297
    timeout_slots: int = 20
    timeout_sec: float = 2.0
    private_cpu_ghz: float = 5.0
    public_cpu_ghz: float = 5.0
    cloud_cpu_ghz: float = 30.0
    horizontal_rate_mbps: float = 30.0
    vertical_rate_mbps: float = 10.0
    random_seed: int = 7
    paper_faithful_mode: bool = False
    test_mode_reason: str = "runtime_core_test_policy_adapter"
    lookback_window: int = 10
    forecast_mode: str = "gated_no_lstm_trace"

    def __post_init__(self) -> None:
        if self.topology_mode not in ALLOWED_TOPOLOGY_MODES:
            raise ValueError(f"topology_mode must be one of {sorted(ALLOWED_TOPOLOGY_MODES)}")
        if self.adjacency_matrix is None:
            if self.topology_mode == "paper_topology_adjacency":
                raise ValueError("paper_topology_adjacency requires an explicit adjacency_matrix")
            if self.topology_mode == "unknown_from_ocr_requires_pdf_visual_confirmation":
                raise ValueError("unknown_from_ocr_requires_pdf_visual_confirmation cannot be used without a trustworthy adjacency_matrix")
            self.adjacency_matrix = [[0 if i == j else 1 for j in range(self.num_edge_agents)] for i in range(self.num_edge_agents)]
        if len(self.adjacency_matrix) != self.num_edge_agents:
            raise ValueError("adjacency_matrix must match num_edge_agents")
        if self.cloud_node_id != self.num_edge_agents + 1:
            raise ValueError("cloud_node_id must equal num_edge_agents + 1")
        if self.slot_count != self.action_slot_count + self.drain_slot_count:
            raise ValueError("slot_count must equal action_slot_count + drain_slot_count")

    @classmethod
    def default(cls) -> "EpisodeConfig":
        return cls()

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["task_size_values_mbits"] = list(self.task_size_values_mbits)
        payload["task_size_range_mbits"] = list(self.task_size_range_mbits)
        payload["topology_mode_is_explicit"] = True
        return payload
