#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from src.analysis.experiment_runner import run_experiment, save_sweep_results
from src.analysis.figure_generator import plot_figure_9_parameter_sweep
from src.analysis.full_training_reproduction_campaign.config import CampaignConfig


def _paper_config(**overrides: Any) -> CampaignConfig:
    config = CampaignConfig.paper_default()
    metadata = dict(config.sweep_metadata)
    metadata.update(overrides.pop("sweep_metadata", {}))
    for key, value in overrides.items():
        setattr(config, key, value)
    config.sweep_metadata = metadata
    return config


def _run_labeled(label: str, config: CampaignConfig, episodes: int, episode_length: int):
    result = run_experiment(config, episodes=episodes, episode_length=episode_length)
    result.experiment_label = label
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Figure 9 only")
    parser.add_argument("--output-dir", default="artifacts/analysis/figure9-only")
    parser.add_argument("--episodes", type=int, default=5)
    parser.add_argument("--episode-length", type=int, default=50)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    sweep_dir = output_dir / "sweep"
    fig_dir = output_dir / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    print("[figure9] build sweep")
    results = []
    for p in [0.1, 0.3, 0.5, 0.7, 0.9]:
        for agents in [10, 15, 20]:
            config = _paper_config(
                arrival_probability=p,
                agent_count=agents,
                sweep_metadata={
                    "sweep_type": "arrival_probability",
                    "arrival_probability": p,
                    "num_drl_agents": agents,
                    "traffic_scenario": {10: "moderate traffic", 15: "heavy traffic", 20: "extreme traffic"}[agents],
                    "implementation_status": "wired_to_TraceProtocol",
                },
            )
            print(f"[figure9] arrival p={p:g} agents={agents}")
            results.append(_run_labeled(f"figure9_arrival_p{p:g}_n{agents}", config, args.episodes, args.episode_length))

    for cpu in [4, 5, 6, 7, 8, 9]:
        for agents in [10, 15, 20]:
            config = _paper_config(
                local_cpu_ghz=cpu,
                public_cpu_ghz=cpu,
                agent_count=agents,
                sweep_metadata={
                    "sweep_type": "cpu_capacity",
                    "cpu_capacity": cpu,
                    "num_drl_agents": agents,
                    "implementation_status": "wired_to_ComputeConfig",
                },
            )
            print(f"[figure9] cpu={cpu} agents={agents}")
            results.append(_run_labeled(f"figure9_cpu_{cpu:g}GHz_n{agents}", config, args.episodes, args.episode_length))

    for traffic in [(10, "moderate traffic"), (15, "heavy traffic"), (20, "extreme traffic")]:
        agents, traffic_label = traffic
        config = _paper_config(
            agent_count=agents,
            sweep_metadata={
                "sweep_type": "num_drl_agents",
                "num_drl_agents": agents,
                "traffic_scenario": traffic_label,
                "implementation_status": "wired_to_TraceProtocol",
            },
        )
        print(f"[figure9] agents={agents} traffic={traffic_label}")
        results.append(_run_labeled(f"figure9_agents_{agents}_{traffic_label.replace(' ', '_')}", config, args.episodes, args.episode_length))

    for label, rh, rv in [("balanced", 10, 30), ("horizontal_centric", 20, 20), ("vertical_centric", 5, 40)]:
        for agents in [10, 15, 20]:
            config = _paper_config(
                horizontal_data_rate_mbps=rh,
                vertical_data_rate_mbps=rv,
                agent_count=agents,
                sweep_metadata={
                    "sweep_type": "offload_data_rate",
                    "horizontal_data_rate_mbps": rh,
                    "vertical_data_rate_mbps": rv,
                    "num_drl_agents": agents,
                    "data_rate_scenario": label,
                    "implementation_status": "wired_to_LinkRateConfig",
                },
            )
            print(f"[figure9] rate={label} agents={agents}")
            results.append(_run_labeled(f"figure9_rate_{label}_{agents}", config, args.episodes, args.episode_length))

    save_sweep_results(results, str(sweep_dir))
    (output_dir / "figure9_summary.json").write_text(json.dumps({"episodes": args.episodes, "count": len(results)}, indent=2) + "\n", encoding="utf-8")

    print("[figure9] render")
    plot_figure_9_parameter_sweep(json.loads((sweep_dir / "sweep_results.json").read_text(encoding="utf-8")), str(fig_dir / "figure9_parameter_sweep.png"), "Figure 9: Parameter sweeps")
    print("[figure9] done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
