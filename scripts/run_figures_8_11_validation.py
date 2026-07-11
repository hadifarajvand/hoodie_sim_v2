#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from src.analysis.experiment_runner import ExperimentResult, save_sweep_results, run_experiment
from src.analysis.figure_generator import (
    plot_figure_8_reward_timecourse,
    plot_figure_9_parameter_sweep,
    plot_figure_10_offloading_schemes,
    plot_figure_11_lstm_comparison,
)
from src.analysis.paper_figures_campaign import DEFAULT_MANUAL_EPISODES, run_figure_10, run_figure_11
from src.analysis.full_training_reproduction_campaign.config import CampaignConfig


DEFAULT_EPISODES = DEFAULT_MANUAL_EPISODES


def _paper_config(**overrides: Any) -> CampaignConfig:
    config = CampaignConfig.paper_default()
    metadata = dict(config.sweep_metadata)
    metadata.update(overrides.pop("sweep_metadata", {}))
    for key, value in overrides.items():
        setattr(config, key, value)
    config.sweep_metadata = metadata
    return config


def _run_labeled(label: str, config: CampaignConfig, episodes: int, episode_length: int) -> ExperimentResult:
    result = run_experiment(config, episodes=episodes, episode_length=episode_length)
    result.experiment_label = label
    return result


def _save_csv(results: list[ExperimentResult], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "experiment_label",
                "sweep_type",
                "learning_rate",
                "gamma",
                "horizontal_data_rate_mbps",
                "vertical_data_rate_mbps",
                "episodes",
                "mean_reward",
                "mean_average_delay_slots",
                "mean_drop_ratio",
                "completed_tasks",
                "dropped_tasks",
                "optimizer_steps",
            ],
        )
        writer.writeheader()
        for row in results:
            metrics = row.training_metrics
            rewards = metrics.get("episode_rewards", [])
            delays = metrics.get("average_delays", [])
            drops = metrics.get("drop_ratios", [])
            writer.writerow(
                {
                    "experiment_label": row.experiment_label,
                    "sweep_type": row.config.sweep_metadata.get("sweep_type", ""),
                    "learning_rate": row.config.learning_rate,
                    "gamma": row.config.gamma,
                    "horizontal_data_rate_mbps": row.config.horizontal_data_rate_mbps,
                    "vertical_data_rate_mbps": row.config.vertical_data_rate_mbps,
                    "episodes": len(rewards),
                    "mean_reward": sum(rewards) / max(len(rewards), 1),
                    "mean_average_delay_slots": sum(delays) / max(len(delays), 1),
                    "mean_drop_ratio": sum(drops) / max(len(drops), 1),
                    "completed_tasks": sum(metrics.get("completed_counts", [])),
                    "dropped_tasks": sum(metrics.get("dropped_counts", [])),
                    "optimizer_steps": row.result.optimizer_step_count,
                }
            )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run bounded HOODIE Figure 8-11 validation sweeps")
    parser.add_argument("--output-dir", default="artifacts/analysis/figure8-11-validation")
    parser.add_argument("--episodes", type=int, default=DEFAULT_EPISODES)
    parser.add_argument("--episode-length", type=int, default=50)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    sweep_dir = output_dir / "sweep"
    fig_dir = output_dir / "figures"
    lstm_dir = output_dir / "lstm"
    no_lstm_dir = output_dir / "no_lstm"
    fig_dir.mkdir(parents=True, exist_ok=True)

    results: list[ExperimentResult] = []

    for lr in [1e-9, 5e-9, 1e-8, 1e-7, 5e-7, 7e-7]:
        config = _paper_config(
            learning_rate=lr,
            sweep_metadata={"sweep_type": "learning_rate", "learning_rate": lr},
        )
        results.append(_run_labeled(f"figure8_lr_{lr:g}", config, args.episodes, args.episode_length))

    for gamma in [0.2, 0.4, 0.6, 0.8, 0.99]:
        config = _paper_config(
            gamma=gamma,
            sweep_metadata={"sweep_type": "discount_factor", "gamma": gamma},
        )
        results.append(_run_labeled(f"figure8_gamma_{gamma:g}", config, args.episodes, args.episode_length))

    for p in [0.1, 0.3, 0.5, 0.7, 0.9]:
        for agents in [10, 15, 20]:
            config = _paper_config(
                arrival_probability=p,
                agent_count=agents,
                sweep_metadata={
                    "sweep_type": "arrival_probability",
                    "arrival_probability": p,
                    "num_drl_agents": agents,
                    "traffic_scenario": {10: "Moderate Traffic", 15: "Heavy Traffic", 20: "Extreme Traffic"}[agents],
                    "implementation_status": "wired_to_TraceProtocol",
                },
            )
            results.append(_run_labeled(f"figure9_arrival_p{p:g}_n{agents}", config, args.episodes, args.episode_length))

    for cpu in [4, 5, 6, 7, 8, 9]:
        config = _paper_config(
            local_cpu_ghz=cpu,
            public_cpu_ghz=cpu,
            sweep_metadata={
                "sweep_type": "cpu_capacity",
                "cpu_capacity": cpu,
                "implementation_status": "wired_to_ComputeConfig",
            },
        )
        results.append(_run_labeled(f"figure9_cpu_{cpu:g}GHz", config, args.episodes, args.episode_length))

    for agents in [10, 15, 20, 25, 30]:
        config = _paper_config(
            agent_count=agents,
            sweep_metadata={
                "sweep_type": "num_drl_agents",
                "num_drl_agents": agents,
                "traffic_scenario": {10: "Moderate Traffic", 15: "Heavy Traffic", 20: "Extreme Traffic", 25: "Heavy Traffic", 30: "Extreme Traffic"}[agents],
                "implementation_status": "wired_to_TraceProtocol",
            },
        )
        results.append(_run_labeled(f"figure9_agents_{agents}", config, args.episodes, args.episode_length))

    for label, rh, rv in [("balanced", 10, 30), ("horizontal_centric", 20, 20), ("vertical_centric", 5, 40)]:
        config = _paper_config(
            horizontal_data_rate_mbps=rh,
            vertical_data_rate_mbps=rv,
            sweep_metadata={
                "sweep_type": "offload_data_rate",
                "horizontal_data_rate_mbps": rh,
                "vertical_data_rate_mbps": rv,
                "data_rate_scenario": {"balanced": "Balanced", "horizontal_centric": "Horizontal-centric", "vertical_centric": "Vertical-centric"}[label],
                "implementation_status": "wired_to_LinkRateConfig",
            },
        )
        results.append(_run_labeled(f"figure9_rate_{label}", config, args.episodes, args.episode_length))

    for timeout in [16, 20, 24]:
        config = _paper_config(
            timeout_slots=timeout,
            sweep_metadata={
                "sweep_type": "task_timeout",
                "task_timeout_slots": timeout,
                "implementation_status": "wired_to_TraceProtocol",
            }
        )
        results.append(_run_labeled(f"figure10_timeout_{timeout}", config, args.episodes, args.episode_length))

    save_sweep_results(results, str(sweep_dir))
    _save_csv(results, output_dir / "figure8_11_validation_summary.csv")

    print("[validation] figure8 render")
    serialized = json.loads((sweep_dir / "sweep_results.json").read_text(encoding="utf-8"))
    plot_figure_8_reward_timecourse(serialized, str(fig_dir / "figure8_reward_timecourse.png"), "Figure 8: Bounded HOODIE Training Reward")
    print("[validation] figure8 done")

    print("[validation] figure9 render")
    plot_figure_9_parameter_sweep(serialized, str(fig_dir / "figure9_parameter_sweep.png"), "Figure 9: Bounded HOODIE Parameter Sweeps")
    print("[validation] figure9 done")

    print("[validation] figure10 run + render")
    figure10_results = run_figure_10(output_dir, quick=True)
    figure10_dir = output_dir / "figure_10_baselines"
    plot_figure_10_offloading_schemes(
        json.loads((figure10_dir / "sweep_results.json").read_text(encoding="utf-8")),
        str(fig_dir / "figure10_offloading_schemes.png"),
        "Figure 10: Bounded HOODIE Delay/Drop Sweeps",
    )
    print(f"[validation] figure10 done: {len(figure10_results)} experiments")

    print("[validation] figure11 run + render")
    figure11_with, figure11_without = run_figure_11(output_dir, quick=True)
    figure11_lstm_dir = output_dir / "figure_11_lstm"
    figure11_no_lstm_dir = output_dir / "figure_11_no_lstm"
    plot_figure_11_lstm_comparison(
        json.loads((figure11_lstm_dir / "sweep_results.json").read_text(encoding="utf-8")),
        json.loads((figure11_no_lstm_dir / "sweep_results.json").read_text(encoding="utf-8")),
        str(fig_dir / "figure11_lstm_comparison.png"),
        "Figure 11: LSTM Ablation Gate",
    )
    print(f"[validation] figure11 done: with={len(figure11_with)} without={len(figure11_without)}")

    return 0

    manifest = {
        "status": "bounded_validation_complete",
        "episodes_per_experiment": args.episodes,
        "episode_length": args.episode_length,
        "paper_mechanisms_exercised": [
            "distributed DDQN trainer",
            "dueling LSTM HOODIE network path",
            "double-DQN target network update",
            "experience replay",
            "Figure 7 topology registry",
            "paper default link rates and altered link-rate sweeps",
            "baseline policy evaluation matrix",
            "delayed rewards and timeout/drop metrics",
        ],
        "known_gaps": [
            "Full 5000-episode paper campaign not run by this bounded ASAP validation.",
            "Figure 10 uses the paper comparison path, not the old DDQN-only sweep.",
        ],
        "outputs": {
            "sweep_json": str(sweep_dir / "sweep_results.json"),
            "summary_csv": str(output_dir / "figure8_11_validation_summary.csv"),
            "figures": sorted(str(path) for path in fig_dir.glob("*.png")),
        },
    }
    (output_dir / "validation_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
