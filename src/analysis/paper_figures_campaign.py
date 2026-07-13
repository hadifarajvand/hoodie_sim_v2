from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from src.analysis.figure_generator import generate_all_figures
from src.analysis.full_training_reproduction_campaign.config import (
    CampaignConfig,
    READINESS_MANUAL_APPROVAL_APPROVED,
)
from src.analysis.full_training_reproduction_campaign.trainer import DDQNTrainer
from src.environment.runtime_model import SharedRuntimeParameters
from src.environment.topology import TopologyGraph
from src.evaluation.config import EvaluationConfig
from src.evaluation.runner import EvaluationRunner
from src.policies.bco import BalancedCooperationOffloadingPolicy
from src.policies.flc import FullLocalComputingPolicy
from src.policies.ho import HorizontalOffloadingPolicy
from src.policies.mleo import MinimumLatencyEstimateOffloadingPolicy
from src.policies.ro import RandomOffloadingPolicy
from src.policies.vo import VerticalOffloadingPolicy

OUTPUT_DIR = Path("artifacts/analysis/paper-figures-campaign")


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False)


def _base_config() -> CampaignConfig:
    config = CampaignConfig.paper_default()
    config.readiness_manual_approval_status = READINESS_MANUAL_APPROVAL_APPROVED
    config.readiness_manual_approval_reference = "paper-figures-campaign"
    config.full_campaign_enabled = False
    config.pilot_episode_length = 110
    config.evaluation_episode_length = 110
    return config


def _set_sweep_metadata(config: CampaignConfig, **metadata: Any) -> None:
    config.sweep_metadata = dict(metadata)


def _run_training(label: str, config: CampaignConfig, *, episodes: int, episode_length: int) -> dict[str, Any]:
    trainer = DDQNTrainer(config)
    result = trainer.run_pilot(episodes=episodes, episode_length=episode_length)
    metrics = trainer.training_metrics_to_dict()
    evaluation = dict(result.evaluation_summary)
    metrics.setdefault("average_delays", [])
    metrics.setdefault("drop_ratios", [])
    if not metrics["average_delays"]:
        metrics["average_delays"] = [float(evaluation.get("mean_completion_delay", 0.0))]
    if not metrics["drop_ratios"]:
        metrics["drop_ratios"] = [float(evaluation.get("drop_ratio", 0.0))]
    return {
        "experiment_label": label,
        "config": config.to_dict(),
        "training_metrics": metrics,
        "result": result.to_dict(),
    }


def _write_sweep_results(path: Path, results: list[dict[str, Any]]) -> None:
    path.mkdir(parents=True, exist_ok=True)
    (path / "sweep_results.json").write_text(_json_dump(results), encoding="utf-8")


def _quick_or_full(value: int, *, quick: bool) -> int:
    return min(value, 30) if quick else value


DEFAULT_MANUAL_EPISODES = 2000


def run_figure_8(output_dir: Path, *, quick: bool) -> list[dict[str, Any]]:
    episodes = _quick_or_full(DEFAULT_MANUAL_EPISODES, quick=quick)
    results: list[dict[str, Any]] = []
    for lr in [1e-9, 5e-9, 1e-8, 1e-7, 5e-7, 7e-7]:
        config = _base_config()
        config.learning_rate = lr
        _set_sweep_metadata(config, sweep_type="learning_rate", learning_rate=lr)
        results.append(_run_training(f"alpha_lr={lr:g}", config, episodes=episodes, episode_length=110))
    for gamma in [0.2, 0.4, 0.6, 0.8, 0.99]:
        config = _base_config()
        config.gamma = gamma
        _set_sweep_metadata(config, sweep_type="discount_factor", discount_factor=gamma)
        results.append(_run_training(f"gamma={gamma:g}", config, episodes=episodes, episode_length=110))
    _write_sweep_results(output_dir / "figure_8_sweep", results)
    return results


def run_figure_9(output_dir: Path, *, quick: bool) -> list[dict[str, Any]]:
    episodes = _quick_or_full(DEFAULT_MANUAL_EPISODES, quick=quick)
    results: list[dict[str, Any]] = []
    for arrival_probability in [0.1, 0.3, 0.5, 0.7, 0.9]:
        for n_agents in [10, 15, 20]:
            config = _base_config()
            config.arrival_probability = arrival_probability
            config.agent_count = n_agents
            _set_sweep_metadata(
                config,
                sweep_type="arrival_probability",
                arrival_probability=arrival_probability,
                num_drl_agents=n_agents,
            )
            results.append(_run_training(f"P={arrival_probability:g}, N={n_agents}", config, episodes=episodes, episode_length=110))
    for cpu_capacity in [4, 5, 6, 7, 8, 9]:
        for n_agents in [10, 15, 20]:
            config = _base_config()
            config.local_cpu_ghz = cpu_capacity
            config.public_cpu_ghz = cpu_capacity
            config.agent_count = n_agents
            _set_sweep_metadata(config, sweep_type="cpu_capacity", cpu_capacity=cpu_capacity, num_drl_agents=n_agents)
            results.append(_run_training(f"CPU={cpu_capacity}GHz N={n_agents}", config, episodes=episodes, episode_length=110))
    for name, size_range, probability in [
        ("moderate", [1, 3], 0.5),
        ("heavy", [2, 5], 0.7),
        ("extreme", [3, 7], 0.9),
    ]:
        for n_agents in [10, 15, 20, 25, 30]:
            config = _base_config()
            config.arrival_probability = probability
            config.agent_count = n_agents
            _set_sweep_metadata(
                config,
                sweep_type="num_drl_agents",
                traffic_scenario=name,
                task_size_mbits=size_range,
                arrival_probability=probability,
                num_drl_agents=n_agents,
            )
            results.append(_run_training(f"{name}, N={n_agents}", config, episodes=episodes, episode_length=110))
    for name, rh, rv in [
        ("balanced", 30.0, 10.0),
        ("horizontal-centric", 40.0, 10.0),
        ("vertical-centric", 10.0, 30.0),
    ]:
        for n_agents in [10, 15, 20, 25, 30]:
            config = _base_config()
            config.horizontal_data_rate_mbps = rh
            config.vertical_data_rate_mbps = rv
            config.agent_count = n_agents
            _set_sweep_metadata(
                config,
                sweep_type="offload_data_rate",
                data_rate_scenario=name,
                horizontal_data_rate_mbps=rh,
                vertical_data_rate_mbps=rv,
                num_drl_agents=n_agents,
            )
            results.append(_run_training(f"{name} rates, N={n_agents}", config, episodes=episodes, episode_length=110))
    _write_sweep_results(output_dir / "figure_9_sensitivity", results)
    return results


BASELINE_POLICY_FACTORIES = {
    "RO": RandomOffloadingPolicy,
    "FLC": FullLocalComputingPolicy,
    "VO": VerticalOffloadingPolicy,
    "HO": HorizontalOffloadingPolicy,
    "BCO": BalancedCooperationOffloadingPolicy,
    "MLEO": MinimumLatencyEstimateOffloadingPolicy,
}


def _real_baseline_metrics(label: str, policy_name: str, sweep_type: str, x_value: float, *, episodes: int, seed: int) -> dict[str, Any]:
    policy_factory = BASELINE_POLICY_FACTORIES[policy_name]
    try:
        policy = policy_factory(seed=seed)
    except TypeError:
        policy = policy_factory()
    result = EvaluationRunner(
        policy=policy,
        config=EvaluationConfig(
            policy_name=policy_name,
            seed=seed,
            trace_id=f"figure10-{policy_name.lower()}-{sweep_type}-{x_value}",
            episode_count=episodes,
            episode_length=110,
        ),
        topology=TopologyGraph.from_approved_assumption_registry(),
        runtime_parameters=SharedRuntimeParameters(),
    ).run()
    aggregate = result["aggregate"]
    per_trace = result["per_trace"]
    action_counts: dict[int, int] = {}
    for trace in per_trace:
        for record in trace.get("raw_records", []):
            action = str(record.get("selected_action"))
            if action in {"local", "compute_local"}:
                action_index = 0
            elif action in {"cloud", "vertical", "offload_vertical"}:
                action_index = 21
            else:
                action_index = 1
            action_counts[action_index] = action_counts.get(action_index, 0) + 1
    return {
        "experiment_label": label,
        "config": {"sweep_metadata": {"sweep_type": sweep_type, sweep_type: x_value, "policy": policy_name, "baseline_real": True}},
        "training_metrics": {
            "episode_rewards": [],
            "action_counts": [action_counts],
            "average_delays": [float(aggregate.get("average_delay", 0.0))],
            "drop_ratios": [float(aggregate.get("drop_ratio", 0.0))],
            "completion_delays": [float(aggregate.get("average_delay", 0.0))],
        },
        "evaluation_result": {
            "metadata": result.get("metadata", {}),
            "aggregate": aggregate,
            "trace_count": len(per_trace),
        },
    }


def run_figure_10(output_dir: Path, *, quick: bool) -> list[dict[str, Any]]:
    episodes = _quick_or_full(DEFAULT_MANUAL_EPISODES, quick=quick)
    policies = ["RO", "FLC", "VO", "HO", "BCO", "MLEO", "HOODIE"]
    results: list[dict[str, Any]] = []
    for probability in [0.1, 0.3, 0.5, 0.7, 0.9]:
        for policy in policies:
            if policy == "HOODIE":
                config = _base_config()
                config.arrival_probability = probability
                _set_sweep_metadata(config, sweep_type="arrival_probability", arrival_probability=probability, policy=policy)
                result = _run_training(f"{policy} P={probability:g}", config, episodes=episodes, episode_length=110)
            else:
                result = _real_baseline_metrics(f"{policy} P={probability:g}", policy, "arrival_probability", probability, episodes=episodes, seed=101 + int(probability * 100))
            results.append(result)
    for cpu_capacity in [3, 4, 5, 6, 7]:
        for policy in policies:
            if policy == "HOODIE":
                config = _base_config()
                config.local_cpu_ghz = cpu_capacity
                config.public_cpu_ghz = cpu_capacity
                _set_sweep_metadata(config, sweep_type="cpu_capacity", cpu_capacity=cpu_capacity, policy=policy)
                result = _run_training(f"{policy} CPU={cpu_capacity}", config, episodes=episodes, episode_length=110)
            else:
                result = _real_baseline_metrics(f"{policy} CPU={cpu_capacity}", policy, "cpu_capacity", cpu_capacity, episodes=episodes, seed=201 + cpu_capacity)
            results.append(result)
    for timeout_slots in [16, 18, 20, 22, 24, 96, 98, 100, 102, 104]:
        for policy in policies:
            if policy == "HOODIE":
                config = _base_config()
                config.timeout_slots = timeout_slots
                _set_sweep_metadata(config, sweep_type="task_timeout", task_timeout_slots=timeout_slots, policy=policy)
                result = _run_training(f"{policy} timeout={timeout_slots}", config, episodes=episodes, episode_length=110)
            else:
                result = _real_baseline_metrics(f"{policy} timeout={timeout_slots}", policy, "task_timeout", timeout_slots, episodes=episodes, seed=301 + timeout_slots)
            results.append(result)
    _write_sweep_results(output_dir / "figure_10_baselines", results)
    return results


def run_figure_11(output_dir: Path, *, quick: bool) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    episodes = _quick_or_full(DEFAULT_MANUAL_EPISODES, quick=quick)
    with_lstm = _base_config()
    with_lstm.lstm_enabled = True
    _set_sweep_metadata(with_lstm, sweep_type="lstm_ablation", lstm_enabled=True, lstm_effective_enabled=True)
    without_lstm = _base_config()
    without_lstm.lstm_enabled = False
    _set_sweep_metadata(without_lstm, sweep_type="lstm_ablation", lstm_enabled=False, lstm_effective_enabled=True)
    with_results = [_run_training("with_lstm", with_lstm, episodes=episodes, episode_length=110)]
    without_results = [_run_training("without_lstm", without_lstm, episodes=episodes, episode_length=110)]
    _write_sweep_results(output_dir / "figure_11_lstm", with_results)
    _write_sweep_results(output_dir / "figure_11_no_lstm", without_results)
    return with_results, without_results


def run_campaign(*, output_dir: Path = OUTPUT_DIR, quick: bool = True) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    fig8 = run_figure_8(output_dir, quick=quick)
    fig9 = run_figure_9(output_dir, quick=quick)
    fig10 = run_figure_10(output_dir, quick=quick)
    fig11_lstm, fig11_no_lstm = run_figure_11(output_dir, quick=quick)

    combined_dir = output_dir / "combined_sweeps"
    combined_results = fig8 + fig9 + fig10
    _write_sweep_results(combined_dir, combined_results)
    figures_dir = output_dir / "figures"
    generate_all_figures(
        str(combined_dir),
        str(figures_dir),
        lstm_sweep_dir=str(output_dir / "figure_11_lstm"),
        no_lstm_sweep_dir=str(output_dir / "figure_11_no_lstm"),
    )

    manifest = {
        "mode": "quick" if quick else "full",
        "output_dir": str(output_dir),
        "figure_8_experiment_count": len(fig8),
        "figure_9_experiment_count": len(fig9),
        "figure_10_experiment_count": len(fig10),
        "figure_11_experiment_count": len(fig11_lstm) + len(fig11_no_lstm),
        "figures": sorted(str(path) for path in figures_dir.glob("*.png")),
        "paper_parameters": {
            "P_default": 0.5,
            "R_H_mbps": 30.0,
            "R_V_mbps": 10.0,
            "task_size_mbits": [2.0, 5.0, 0.1],
            "processing_density_gcycles_per_mbit": 0.297,
            "N_default": 20,
            "private_public_cpu_gcycles_per_slot": 0.5,
            "cloud_cpu_gcycles_per_slot": 3.0,
            "episodes_full": 5000,
            "episode_length_slots": 110,
            "slot_duration_seconds": 0.1,
            "timeout_slots": 20,
            "learning_rate_default": 7e-7,
            "gamma_default": 0.99,
            "batch_size": 64,
            "replay_memory_capacity": 10000,
        },
    }
    (output_dir / "run-manifest.json").write_text(_json_dump(manifest), encoding="utf-8")
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run HOODIE paper Figures 8-11 campaign.")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--full", action="store_true", help="Run paper episode counts instead of quick smoke counts.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    manifest = run_campaign(output_dir=args.output_dir, quick=not args.full)
    if args.json:
        print(_json_dump(manifest))
    else:
        print(f"Wrote {args.output_dir / 'run-manifest.json'}")
        for figure in manifest["figures"]:
            print(f"Wrote {figure}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
