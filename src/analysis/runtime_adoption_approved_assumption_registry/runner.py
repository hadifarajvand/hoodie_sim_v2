from __future__ import annotations

from dataclasses import dataclass

from src.analysis.user_approved_assumption_patch_registry.registry import build_user_approved_assumption_registry
from src.environment.compute_config import ComputeConfig
from src.environment.link_rate_config import LinkRateConfig
from src.environment.topology import TopologyGraph
from src.environment.traffic_config import TrafficScenarioPreset, TrafficConfig
from src.evaluation.aggregate_metrics import aggregate_terminal_rewards


@dataclass(frozen=True, slots=True)
class RuntimeAdoptionContracts:
    registry_path: str
    compute_config: ComputeConfig
    topology: TopologyGraph
    link_rate_config: LinkRateConfig
    traffic_config: TrafficConfig


def load_runtime_adoption_contracts() -> RuntimeAdoptionContracts:
    registry = build_user_approved_assumption_registry()
    if registry.get("item_count") != 8:
        raise ValueError("Approved assumption registry must contain exactly 8 items")
    topology = TopologyGraph.from_approved_assumption_registry()
    traffic_config = TrafficScenarioPreset.paper_default()
    return RuntimeAdoptionContracts(
        registry_path="resources/papers/hoodie/recovered/user-approved-assumption-registry.json",
        compute_config=ComputeConfig(),
        topology=topology,
        link_rate_config=LinkRateConfig(),
        traffic_config=traffic_config,
    )


def preview_runtime_adoption_aggregation(per_agent_episode_rewards: list[list[float | int | None]]) -> float:
    return aggregate_terminal_rewards(per_agent_episode_rewards)
