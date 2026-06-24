"""Paper-faithful environment builder.

Constructs HoodieGymEnvironment with paper Table 4 parameters exactly.
"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from src.environment.compute_config import ComputeConfig
from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.link_rate_config import LinkRateConfig
from src.environment.runtime_model import SharedRuntimeParameters
from src.environment.topology import TopologyGraph
from src.environment.trace_source import TraceSource
from src.environment.traffic_config import TrafficConfig
from src.environment.traffic_generator import TrafficGenerator

from src.analysis.full_training_reproduction_campaign import trainer as campaign_trainer

from .config import PaperFaithfulConfig, build_paper_faithful_profile


def build_paper_faithful_traffic_config(cfg: PaperFaithfulConfig) -> TrafficConfig:
    """Create TrafficConfig from paper-faithful profile."""
    return TrafficConfig(
        scenario_name="paper_default",
        number_of_agents=cfg.num_agents,
        episode_length=cfg.episode_length,
        arrival_probability=cfg.arrival_probability,
        slot_duration_seconds=cfg.slot_duration_seconds,
        timeout_slots=cfg.timeout_slots,
        task_size_mbits_min=cfg.task_size_mbits_min,
        task_size_mbits_max=cfg.task_size_mbits_max,
        task_size_mbits_step=cfg.task_size_mbits_step,
        processing_density_gcycles_per_mbit=cfg.processing_density_gcycles_per_mbit,
    )


def ensure_paper_faithful_trace_bank(cfg: PaperFaithfulConfig, trace_root: Path, seed: int) -> Path:
    """Generate and cache paper-faithful traces."""
    trace_root.mkdir(parents=True, exist_ok=True)
    traffic_config = build_paper_faithful_traffic_config(cfg)
    trace = TrafficGenerator.generate(traffic_config, seed)
    trace_path = trace_root / f"paper_faithful-{seed}.json"
    if not trace_path.exists():
        trace.write_json(trace_path)
    return trace_path


def build_paper_faithful_environment(cfg: PaperFaithfulConfig, *, episode_length: int, seed: int, trace_root: Path) -> HoodieGymEnvironment:
    """Construct a paper-faithful HoodieGymEnvironment using traces from paper-faithful trace bank.

    Uses paper-faithful traffic parameters to generate and load traces.
    This ensures task sizes, densities, and all traffic parameters match the paper exactly.
    """
    # Generate and cache trace for reproducibility
    ensure_paper_faithful_trace_bank(cfg, trace_root, seed)

    # Use HoodieGymEnvironment with paper-faithful compute, link rate, and trace configs.
    return HoodieGymEnvironment(
        episode_length=episode_length,
        topology=TopologyGraph.from_approved_assumption_registry(),
        runtime_parameters=SharedRuntimeParameters(),
        compute_config=ComputeConfig(
            cpu_capacity_per_slot_agent=cfg.cpu_private_gcycles_per_slot,
            cpu_capacity_per_slot_edge=cfg.cpu_public_gcycles_per_slot,
            cpu_capacity_per_slot_cloud=cfg.cpu_cloud_gcycles_per_slot,
        ),
        trace_source=TraceSource.from_trace_bank(f"paper_faithful-{seed}", root_path=trace_root),
        link_rate_config=LinkRateConfig(
            horizontal_data_rate_mbps=cfg.horizontal_link_rate_mbps,
            vertical_data_rate_mbps=cfg.vertical_link_rate_mbps,
            slot_duration_seconds=cfg.slot_duration_seconds,
        ),
        policy_name="HOODIE",
    )


@contextmanager
def patched_paper_faithful_environment(cfg: PaperFaithfulConfig, trace_root: Path) -> Iterator[None]:
    """Context manager that patches trainer to use paper-faithful environment.

    This patches campaign_trainer._build_environment so that DDQNTrainer._episode_rollout()
    and DDQNTrainer.evaluate() both use the paper-faithful environment instead of the default.
    """
    original_trainer_builder = campaign_trainer._build_environment

    def _build_environment(config, *, episode_length: int, seed: int):
        return build_paper_faithful_environment(cfg, episode_length=episode_length, seed=seed, trace_root=trace_root)

    campaign_trainer._build_environment = _build_environment
    try:
        yield
    finally:
        campaign_trainer._build_environment = original_trainer_builder
