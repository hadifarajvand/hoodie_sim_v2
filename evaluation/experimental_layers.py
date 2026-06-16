from __future__ import annotations

import csv
import hashlib
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import mean, pstdev
from typing import Any, Iterable, Protocol

import numpy as np

from evaluation.baseline_runner import (
    BaselineExecutionEngine,
    BaselineScenario,
    GreedyLatencyBaselinePolicy,
    RandomOffloadingBaselinePolicy,
    FIFOQueueBaselinePolicy,
    scenario_catalog,
)

try:  # pragma: no cover - optional dependency path
    from training.hoodie_runtime_checkpoint_loader import load_hoodie_checkpoint_with_metadata
except Exception:  # pragma: no cover
    load_hoodie_checkpoint_with_metadata = None


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True))


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode("utf-8")).hexdigest()


class UnifiedPolicyInterface(Protocol):
    name: str

    def select_action(self, state: dict[str, Any], rng: np.random.Generator, task: Any | None = None) -> int: ...

    def update_metrics(self, trace: dict[str, Any]) -> None: ...

    def choose(self, *, task: Any, state: dict[str, Any], rng: np.random.Generator, scenario: BaselineScenario) -> int: ...


class _UnifiedPolicyBase:
    name: str = "policy"

    def update_metrics(self, trace: dict[str, Any]) -> None:
        self.last_metrics = trace

    def choose(self, *, task: Any, state: dict[str, Any], rng: np.random.Generator, scenario: BaselineScenario) -> int:
        return self.select_action(state, rng, task=task)


class FIFOUnifiedPolicy(_UnifiedPolicyBase):
    name = "FIFO"

    def select_action(self, state: dict[str, Any], rng: np.random.Generator, task: Any | None = None) -> int:
        return 0


class RandomOffloadingUnifiedPolicy(_UnifiedPolicyBase):
    name = "RO"

    def select_action(self, state: dict[str, Any], rng: np.random.Generator, task: Any | None = None) -> int:
        action_count = int(state.get("action_count", len(state.get("queue_work", {}))))
        return int(rng.integers(0, max(1, action_count)))


class GreedyLatencyUnifiedPolicy(_UnifiedPolicyBase):
    name = "GreedyLatency"

    def select_action(self, state: dict[str, Any], rng: np.random.Generator, task: Any | None = None) -> int:
        queue_work = state.get("queue_work", {})
        capacities = state.get("capacities", {})
        best_action = 0
        best_score = None
        for node_id in sorted(queue_work.keys()):
            score = float(queue_work[node_id]) / max(float(capacities.get(node_id, 1.0)), 1e-9)
            if task is not None and hasattr(task, "size"):
                score += float(task.size) / max(float(capacities.get(node_id, 1.0)), 1e-9)
            if best_score is None or score < best_score or (math.isclose(score, best_score) and node_id < best_action):
                best_score = score
                best_action = int(node_id)
        return int(best_action)


class HoodieFrozenPolicy(_UnifiedPolicyBase):
    name = "HOODIE"

    def __init__(self, checkpoint_path: str | Path | None = None, fallback_policy: UnifiedPolicyInterface | None = None) -> None:
        self.checkpoint_path = Path(checkpoint_path) if checkpoint_path else None
        self.fallback_policy = fallback_policy or GreedyLatencyUnifiedPolicy()
        self.loaded_model = None
        self.metadata_report: dict[str, Any] = {}
        if self.checkpoint_path and load_hoodie_checkpoint_with_metadata is not None and self.checkpoint_path.exists():
            self.loaded_model, self.metadata_report = load_hoodie_checkpoint_with_metadata(self.checkpoint_path)

    def select_action(self, state: dict[str, Any], rng: np.random.Generator, task: Any | None = None) -> int:
        if self.loaded_model is not None and hasattr(self.loaded_model, "predict"):
            vector = np.asarray(state.get("state_vector", []), dtype=np.float32).reshape(1, -1)
            try:
                q_values = np.asarray(self.loaded_model.predict(vector))[0]
                return int(np.argmax(q_values))
            except Exception:
                return self.fallback_policy.select_action(state, rng, task=task)
        return self.fallback_policy.select_action(state, rng, task=task)


class ForecastInjectionGate:
    def __init__(self, enabled: bool = False, queue_bias: float = 0.15, offloading_bias: float = 0.1, cpu_weight: float = 0.1) -> None:
        self.enabled = bool(enabled)
        self.queue_bias = float(queue_bias)
        self.offloading_bias = float(offloading_bias)
        self.cpu_weight = float(cpu_weight)

    def inject(self, state: dict[str, Any], forecast: dict[str, Any] | None = None) -> dict[str, Any]:
        if not self.enabled:
            return dict(state)
        transformed = dict(state)
        queue_work = dict(transformed.get("queue_work", {}))
        capacities = dict(transformed.get("capacities", {}))
        forecast = forecast or {}
        predicted = forecast.get("predicted_next_load")
        if predicted is None:
            predicted = forecast.get("load")
        if predicted is not None:
            predicted = np.asarray(predicted, dtype=np.float32).reshape(-1)
            for idx, value in enumerate(predicted):
                if idx in queue_work:
                    queue_work[idx] = float(queue_work[idx]) * (1.0 + self.queue_bias * float(value))
                if idx in capacities:
                    capacities[idx] = float(capacities[idx]) * (1.0 + self.cpu_weight * (1.0 - float(value)))
        transformed["queue_work"] = queue_work
        transformed["capacities"] = capacities
        transformed["forecast_injection_enabled"] = True
        transformed["forecast_injection_bias"] = {
            "queue_bias": self.queue_bias,
            "offloading_bias": self.offloading_bias,
            "cpu_weight": self.cpu_weight,
        }
        return transformed


@dataclass
class EpisodeLog:
    episode_id: int
    policy_version_id: str
    cumulative_reward: float
    step_counter: int
    decay_memory_buffer: list[float]
    reward_trace: list[float]
    trace: dict[str, Any]


class TemporalRewardAggregator:
    def __init__(self, window: int = 5, smoothing: float = 0.2) -> None:
        if window <= 0:
            raise ValueError("window must be positive")
        if not (0.0 < smoothing <= 1.0):
            raise ValueError("smoothing must be in (0, 1]")
        self.window = int(window)
        self.smoothing = float(smoothing)
        self.policy_history: dict[str, list[float]] = {}

    def update(self, policy_name: str, episode_reward: float) -> dict[str, Any]:
        history = self.policy_history.setdefault(policy_name, [])
        history.append(float(episode_reward))
        window_values = history[-self.window :]
        moving_average = float(mean(window_values))
        ema = float(history[0])
        for value in history[1:]:
            ema = self.smoothing * float(value) + (1.0 - self.smoothing) * ema
        return {
            "policy_name": policy_name,
            "episode_reward": float(episode_reward),
            "moving_average": moving_average,
            "exponential_smoothing": ema,
            "final_convergence_metric": float(history[-1] - moving_average),
            "episode_index": len(history) - 1,
        }


class SimulationEpochLayer:
    def __init__(self, *, policy_name: str, scenario: BaselineScenario, fig_gate: ForecastInjectionGate | None = None, checkpoint_path: str | Path | None = None) -> None:
        self.policy_name = policy_name
        self.scenario = scenario
        self.fig_gate = fig_gate
        self.checkpoint_path = checkpoint_path

    def run(self, episode_id: int, seed: int) -> EpisodeLog:
        return run_simulation_epoch(
            episode_id=episode_id,
            scenario=self.scenario,
            policy_name=self.policy_name,
            seed=seed,
            fig_gate=self.fig_gate,
            checkpoint_path=self.checkpoint_path,
        )


@dataclass(frozen=True)
class ExperimentConfig:
    lambda_arrival: float
    cpu_capacity: float
    num_agents: int
    network_delay: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def config_id(self) -> str:
        return f"lam{self.lambda_arrival}_cpu{self.cpu_capacity}_agents{self.num_agents}_net{self.network_delay}"


@dataclass(frozen=True)
class ScenarioSpec:
    scenario_id: str
    lambda_arrival: list[float]
    cpu_capacity: list[float]
    num_agents: list[int]
    network_delay: list[float]


def build_experiment_matrix(spec: ScenarioSpec) -> list[ExperimentConfig]:
    configs: list[ExperimentConfig] = []
    for lam in spec.lambda_arrival:
        for cpu in spec.cpu_capacity:
            for agents in spec.num_agents:
                for delay in spec.network_delay:
                    configs.append(ExperimentConfig(float(lam), float(cpu), int(agents), float(delay)))
    return configs


def _scenario_from_config(config: ExperimentConfig) -> BaselineScenario:
    num_edge_nodes = max(1, int(config.num_agents))
    edge_cap = tuple(float(config.cpu_capacity) for _ in range(num_edge_nodes))
    return BaselineScenario(
        scenario_id=config.config_id,
        description="experimental matrix scenario",
        num_edge_nodes=num_edge_nodes,
        arrival_slots=100,
        drain_slots=10,
        task_size_range=(1, 4),
        deadline_range=(6, 12),
        edge_cpu_capacities=edge_cap,
        cloud_cpu_capacity=float(config.cpu_capacity) * 2.0,
        arrival_rate_schedule={"type": "constant", "rate": float(config.lambda_arrival)},
        queue_order=tuple(range(num_edge_nodes + 1)),
    )


def _policy_from_name(name: str, *, checkpoint_path: str | Path | None = None, fig_gate: ForecastInjectionGate | None = None):
    if name == "FIFO":
        base = FIFOUnifiedPolicy()
    elif name == "RO":
        base = RandomOffloadingUnifiedPolicy()
    elif name == "GreedyLatency":
        base = GreedyLatencyUnifiedPolicy()
    elif name == "HOODIE":
        base = HoodieFrozenPolicy(checkpoint_path=checkpoint_path)
    else:
        raise ValueError(f"unsupported policy {name!r}")

    if fig_gate is None or not fig_gate.enabled:
        return base

    class FIGWrappedPolicy(_UnifiedPolicyBase):
        name = base.name

        def select_action(self, state: dict[str, Any], rng: np.random.Generator, task: Any | None = None) -> int:
            queue_work = state.get("queue_work", {})
            forecast = {
                "predicted_next_load": np.asarray([float(v) for _, v in sorted(queue_work.items())], dtype=np.float32)
            }
            injected = fig_gate.inject(state, forecast=forecast)
            return base.select_action(injected, rng, task=task)

        def update_metrics(self, trace: dict[str, Any]) -> None:
            base.update_metrics(trace)

    return FIGWrappedPolicy()


def run_simulation_epoch(
    *,
    episode_id: int,
    scenario: BaselineScenario,
    policy_name: str,
    seed: int,
    fig_gate: ForecastInjectionGate | None = None,
    checkpoint_path: str | Path | None = None,
) -> EpisodeLog:
    policy = _policy_from_name(policy_name, checkpoint_path=checkpoint_path, fig_gate=fig_gate)
    engine = BaselineExecutionEngine(scenario, policy, seed)
    result = engine.run()
    reward_trace = [float(result["reward_proxy"])]
    return EpisodeLog(
        episode_id=episode_id,
        policy_version_id=f"{policy_name}:seed:{seed}:fig:{int(bool(fig_gate and fig_gate.enabled))}",
        cumulative_reward=float(result["reward_proxy"]),
        step_counter=int(scenario.total_slots),
        decay_memory_buffer=reward_trace[-5:],
        reward_trace=reward_trace,
        trace=result,
    )


def _write_plot(path: Path, x: list[float], y_by_label: dict[str, list[float]], title: str, xlabel: str, ylabel: str) -> None:
    import matplotlib

    matplotlib.use("Agg", force=True)
    import matplotlib.pyplot as plt

    path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(8, 5))
    for label, y in y_by_label.items():
        plt.plot(x, y, marker="o", label=label)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()


def run_experimental_suite(
    output_dir: str | Path,
    *,
    scenario_spec: ScenarioSpec | None = None,
    policies: Iterable[str] = ("FIFO", "GreedyLatency", "RO", "HOODIE"),
    seed_count: int = 10,
    fig_enabled: bool = False,
    checkpoint_path: str | Path | None = None,
) -> dict[str, Any]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    scenario_spec = scenario_spec or ScenarioSpec(
        scenario_id="default",
        lambda_arrival=[0.25, 0.6, 1.0],
        cpu_capacity=[1.0, 2.0],
        num_agents=[2, 3],
        network_delay=[0.0, 1.0],
    )
    configs = build_experiment_matrix(scenario_spec)
    seeds = list(range(seed_count))
    fig_gate = ForecastInjectionGate(enabled=fig_enabled)
    aggregator = TemporalRewardAggregator(window=5, smoothing=0.2)
    reward_rows: list[dict[str, Any]] = []
    sweep_rows: list[dict[str, Any]] = []
    baseline_rows: list[dict[str, Any]] = []
    lstm_rows: list[dict[str, Any]] = []

    for config in configs:
        scenario = _scenario_from_config(config)
        for policy_name in policies:
            seed_rewards: list[float] = []
            for seed in seeds:
                epoch = run_simulation_epoch(
                    episode_id=seed,
                    scenario=scenario,
                    policy_name=policy_name,
                    seed=seed,
                    fig_gate=fig_gate if fig_enabled else None,
                    checkpoint_path=checkpoint_path,
                )
                seed_rewards.append(epoch.cumulative_reward)
                summary = aggregator.update(policy_name, epoch.cumulative_reward)
                reward_rows.append(
                    {
                        "config_id": config.config_id,
                        "policy_name": policy_name,
                        "episode_id": seed,
                        "reward": epoch.cumulative_reward,
                        "moving_average": summary["moving_average"],
                        "exponential_smoothing": summary["exponential_smoothing"],
                        "policy_version_id": epoch.policy_version_id,
                        "seed": seed,
                        "fig_enabled": bool(fig_enabled),
                    }
                )
            sweep_rows.append(
                {
                    "config_id": config.config_id,
                    "lambda_arrival": config.lambda_arrival,
                    "cpu_capacity": config.cpu_capacity,
                    "num_agents": config.num_agents,
                    "network_delay": config.network_delay,
                    "policy_name": policy_name,
                    "avg_delay": float(np.mean([max(0.0, -reward) for reward in seed_rewards])),
                    "drop_rate": float(np.mean([1.0 if reward < 0 else 0.0 for reward in seed_rewards])),
                    "reward_curve": json.dumps(seed_rewards),
                    "energy_cost": float(config.cpu_capacity * config.num_agents * (1.0 + config.network_delay)),
                }
            )
            baseline_rows.append(
                {
                    "config_id": config.config_id,
                    "policy_name": policy_name,
                    "mean_reward": float(np.mean(seed_rewards)),
                    "std_reward": float(np.std(seed_rewards)) if len(seed_rewards) > 1 else 0.0,
                    "ci95_low": float(np.mean(seed_rewards) - 1.96 * (np.std(seed_rewards) / math.sqrt(len(seed_rewards)))) if len(seed_rewards) > 1 else float(np.mean(seed_rewards)),
                    "ci95_high": float(np.mean(seed_rewards) + 1.96 * (np.std(seed_rewards) / math.sqrt(len(seed_rewards)))) if len(seed_rewards) > 1 else float(np.mean(seed_rewards)),
                }
            )
            lstm_rows.append(
                {
                    "config_id": config.config_id,
                    "policy_name": policy_name,
                    "fig_enabled": False,
                    "mean_reward": float(np.mean(seed_rewards)),
                }
            )
            if fig_enabled:
                fig_rewards = [
                    run_simulation_epoch(
                        episode_id=seed,
                        scenario=scenario,
                        policy_name=policy_name,
                        seed=seed,
                        fig_gate=ForecastInjectionGate(enabled=True),
                        checkpoint_path=checkpoint_path,
                    ).cumulative_reward
                    for seed in seeds
                ]
                lstm_rows.append(
                    {
                        "config_id": config.config_id,
                        "policy_name": policy_name,
                        "fig_enabled": True,
                        "mean_reward": float(np.mean(fig_rewards)),
                    }
                )

    training_curve_path = output_dir / "training_curves.csv"
    sweep_table_path = output_dir / "parameter_sweep_table.csv"
    baseline_table_path = output_dir / "baseline_comparison_table.csv"
    lstm_analysis_path = output_dir / "lstm_effect_analysis.csv"
    _write_csv(training_curve_path, reward_rows)
    _write_csv(sweep_table_path, sweep_rows)
    _write_csv(baseline_table_path, baseline_rows)
    _write_csv(lstm_analysis_path, lstm_rows)

    if reward_rows:
        labels = sorted({row["policy_name"] for row in reward_rows})
        x = list(range(seed_count))
        plot_data = {label: [row["reward"] for row in reward_rows if row["policy_name"] == label][:seed_count] for label in labels}
        _write_plot(output_dir / "training_curves.png", x, plot_data, "Training Curves", "episode", "reward")
    if sweep_rows:
        x = list(range(len(sweep_rows)))
        y = {"avg_delay": [float(row["avg_delay"]) for row in sweep_rows]}
        _write_plot(output_dir / "parameter_sweep.png", x, y, "Parameter Sweep", "config index", "avg delay")
    if baseline_rows:
        labels = sorted({row["policy_name"] for row in baseline_rows})
        x = list(range(len(labels)))
        y = {"mean_reward": [float(np.mean([row["mean_reward"] for row in baseline_rows if row["policy_name"] == label])) for label in labels]}
        _write_plot(output_dir / "baseline_comparison.png", x, y, "Baseline Comparison", "policy", "mean reward")
    if lstm_rows:
        labels = ["off", "on"] if fig_enabled else ["off"]
        x = list(range(len(labels)))
        off_mean = float(np.mean([row["mean_reward"] for row in lstm_rows if not row["fig_enabled"]])) if lstm_rows else 0.0
        on_mean = float(np.mean([row["mean_reward"] for row in lstm_rows if row["fig_enabled"]])) if any(row["fig_enabled"] for row in lstm_rows) else off_mean
        y = {"mean_reward": [off_mean] if not fig_enabled else [off_mean, on_mean]}
        _write_plot(output_dir / "lstm_effect_analysis.png", x, y, "FIG ON/OFF Analysis", "gate", "mean reward")

    manifest = {
        "model": "Experimental wrapper layers",
        "seed_count": seed_count,
        "scenario_count": len(configs),
        "policy_names": list(policies),
        "fig_enabled": bool(fig_enabled),
        "config_hash": _hash({"scenario_spec": asdict(scenario_spec), "policies": list(policies), "seed_count": seed_count, "fig_enabled": fig_enabled}),
        "outputs": {
            "training_curves.csv": str(training_curve_path),
            "parameter_sweep_table.csv": str(sweep_table_path),
            "baseline_comparison_table.csv": str(baseline_table_path),
            "lstm_effect_analysis.csv": str(lstm_analysis_path),
            "training_curves.png": str(output_dir / "training_curves.png"),
            "parameter_sweep.png": str(output_dir / "parameter_sweep.png"),
            "baseline_comparison.png": str(output_dir / "baseline_comparison.png"),
            "lstm_effect_analysis.png": str(output_dir / "lstm_effect_analysis.png"),
        },
        "deterministic": True,
        "evaluation_only": True,
        "paper_claims_made": False,
    }
    _write_json(output_dir / "experimental_layers_manifest.json", manifest)
    return {
        "manifest": manifest,
        "training_curves": reward_rows,
        "parameter_sweep": sweep_rows,
        "baseline_comparison": baseline_rows,
        "lstm_effect": lstm_rows,
    }
