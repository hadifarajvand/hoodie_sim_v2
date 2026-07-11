"""Configuration template generators for parameter sweep experiments.

Each function returns a CampaignConfig with one parameter varied
while keeping paper defaults for everything else.

Some parameters (arrival probability, CPU capacity, agent count,
task timeout) live in the environment layer (TrafficConfig, ComputeConfig)
and are not yet wired through CampaignConfig. Those functions return
paper_default as a placeholder -- update the implementations once
CampaignConfig exposes those knobs.
"""

from __future__ import annotations

from dataclasses import replace

from src.analysis.full_training_reproduction_campaign.config import CampaignConfig


def _with_sweep_metadata(base: CampaignConfig, **metadata: object) -> CampaignConfig:
    merged = dict(base.sweep_metadata)
    merged.update(metadata)
    return replace(base, sweep_metadata=merged)


def paper_default() -> CampaignConfig:
    """Return the default paper configuration."""
    return _with_sweep_metadata(CampaignConfig.paper_default(), sweep_type="paper_default")


def vary_arrival_probability(rate: float) -> CampaignConfig:
    """Return config with varied task arrival probability.

    NOTE: arrival_probability lives in TrafficConfig (environment layer),
    not in CampaignConfig.  Returns paper_default placeholder.

    Valid rates: 0.2, 0.4, 0.6, 0.8, 1.0
    """
    if not 0.0 < rate <= 1.0:
        raise ValueError(f"arrival_probability must be in (0, 1], got {rate}")
    return _with_sweep_metadata(
        CampaignConfig.paper_default(),
        sweep_type="arrival_probability",
        arrival_probability=float(rate),
    )


def vary_cpu_capacity(mips: float) -> CampaignConfig:
    """Return config with varied CPU computation capacity (MIPS-equivalent).

    NOTE: CPU capacity lives in ComputeConfig (environment layer),
    not in CampaignConfig.  Returns paper_default placeholder.
    """
    if mips <= 0:
        raise ValueError(f"cpu_capacity must be positive, got {mips}")
    return _with_sweep_metadata(
        CampaignConfig.paper_default(),
        sweep_type="cpu_capacity",
        cpu_capacity=float(mips),
    )


def vary_num_drl_agents(count: int) -> CampaignConfig:
    """Return config with varied number of DRL agents (edge agents).

    NOTE: agent count lives in TrafficConfig / topology (environment layer),
    not in CampaignConfig.  Returns paper_default placeholder.
    """
    if count <= 0:
        raise ValueError(f"num_drl_agents must be positive, got {count}")
    return _with_sweep_metadata(
        CampaignConfig.paper_default(),
        sweep_type="num_drl_agents",
        num_drl_agents=int(count),
    )


def vary_offload_data_rate(horizontal_mbps: float, vertical_mbps: float) -> CampaignConfig:
    """Return config with varied horizontal / vertical offload data rates.

    Maps directly to CampaignConfig fields horizontal_data_rate_mbps
    and vertical_data_rate_mbps.
    """
    if horizontal_mbps <= 0:
        raise ValueError(f"horizontal_data_rate must be positive, got {horizontal_mbps}")
    if vertical_mbps <= 0:
        raise ValueError(f"vertical_data_rate must be positive, got {vertical_mbps}")
    base = CampaignConfig.paper_default()
    return _with_sweep_metadata(
        replace(
            base,
            horizontal_data_rate_mbps=float(horizontal_mbps),
            vertical_data_rate_mbps=float(vertical_mbps),
        ),
        sweep_type="offload_data_rate",
        horizontal_data_rate_mbps=float(horizontal_mbps),
        vertical_data_rate_mbps=float(vertical_mbps),
    )


def vary_task_timeout(slots: int) -> CampaignConfig:
    """Return config with varied task timeout in slots.

    NOTE: task timeout lives in TrafficConfig (environment layer),
    not in CampaignConfig.  Returns paper_default placeholder.
    """
    if slots <= 0:
        raise ValueError(f"task_timeout must be positive, got {slots}")
    return _with_sweep_metadata(
        CampaignConfig.paper_default(),
        sweep_type="task_timeout",
        task_timeout_slots=int(slots),
    )


def vary_lstm_enabled(enabled: bool) -> CampaignConfig:
    """Return config with LSTM enabled or disabled.

    NOTE: LSTM remains locked to enabled in network config.
    This function records requested sweep intent so figure/report code can
    distinguish LSTM and no-LSTM campaigns until full disable support exists.
    """
    return _with_sweep_metadata(
        CampaignConfig.paper_default(),
        sweep_type="lstm_enabled",
        lstm_enabled=bool(enabled),
        lstm_effective_enabled=True,
    )
