from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import json
import math
from pathlib import Path
import platform
import shutil
import tempfile
from typing import Any, Callable
import zipfile

import matplotlib

matplotlib.use("Agg")
from matplotlib import pyplot as plt
import numpy as np
from PIL import Image
import torch

from src.agents.distributed_hoodie import DistributedHoodiePolicy
from src.environment.echo_control_config import EchoControlConfig
from src.environment.evaluation_gym_adapter import EvaluationHoodieGymEnvironment
from src.environment.link_rate_config import LinkRateConfig
from src.environment.runtime_model import SharedRuntimeParameters
from src.environment.topology import TopologyGraph
from src.evaluation.policy_registry import PolicyRegistry
from src.evaluation.trace_protocol import EvaluationTrace, build_deterministic_trace
from src.policies.ro import RandomOffloadingPolicy

from .trained_pilot_io import (
    atomic_csv,
    atomic_json,
    file_sha256,
    read_json,
    repository_root,
    resolve_campaign_root,
    source_commit,
    write_sha256sums,
)


LABEL = "FULL-MATRIX EXECUTION SMOKE — NOT PAPER EVIDENCE"
MAIN_METHODS = ("ECHO", "HOODIE", "RO", "FLC", "VO", "HO", "BCO", "MLEO")
ABLATION_METHODS = ("ECHO", "ECHO-NoLSTM")
LEARNED_METHODS = ("ECHO", "HOODIE", "ECHO-NoLSTM")
PANEL_IDS = tuple(
    [f"figure_5{letter}" for letter in "ab"]
    + [f"figure_6{letter}" for letter in "abcde"]
    + [f"figure_7{letter}" for letter in "abcdef"]
    + [f"figure_8{letter}" for letter in "ab"]
)


@dataclass(frozen=True, slots=True)
class FullMatrixSmokeConfig:
    training_episodes: int = 3
    evaluation_episodes: int = 1
    episode_slots: int = 16
    drain_slots: int = 4
    batch_size: int = 4
    replay_capacity: int = 256
    target_update_interval: int = 8
    hidden_dims: tuple[int, ...] = (32, 32)
    lookback: int = 3
    lstm_hidden: int = 4
    learning_rate: float = 7e-7
    discount_factor: float = 0.99
    slot_duration_seconds: float = 0.1
    processing_density: float = 0.297

    def __post_init__(self) -> None:
        if self.training_episodes <= 0 or self.evaluation_episodes <= 0:
            raise ValueError("smoke episode counts must be positive")
        if not 0 < self.drain_slots < self.episode_slots:
            raise ValueError("smoke drain slots must be inside the episode")
        if self.batch_size <= 0 or self.replay_capacity < self.batch_size:
            raise ValueError("invalid smoke replay configuration")


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _paper_axes() -> dict[str, Any]:
    return read_json(repository_root() / "configs/echo/full_matrix_smoke.json")[
        "paper_axes"
    ]


def _topology(agent_count: int) -> TopologyGraph:
    return TopologyGraph.for_agent_count(agent_count)


def _campaign(
    run_root: str | Path, campaign_id: str, config: FullMatrixSmokeConfig
) -> Path:
    root = resolve_campaign_root(run_root, campaign_id)
    root.mkdir(parents=True, exist_ok=True)
    specification = {
        "schema_version": 1,
        "campaign_id": campaign_id,
        "label": LABEL,
        "source_commit": source_commit(),
        "methods": {
            "main_comparison": list(MAIN_METHODS),
            "ablation_only": list(ABLATION_METHODS),
        },
        "panel_ids": list(PANEL_IDS),
        "smoke_config": {
            field: getattr(config, field)
            for field in config.__dataclass_fields__
        },
        "paper_axes": _paper_axes(),
        "paper_evidence": False,
        "paper_scale_started": False,
        "projected_or_surrogate_values_used": False,
    }
    path = root / "campaign_specification.json"
    if path.exists():
        existing = read_json(path)
        if existing != json.loads(json.dumps(specification)):
            raise ValueError("existing smoke campaign does not match this source/configuration")
    else:
        atomic_json(path, specification)
        atomic_json(
            root / "environment_manifest.json",
            {
                "created_at": _now(),
                "python": platform.python_version(),
                "platform": platform.platform(),
                "torch": torch.__version__,
                "numpy": np.__version__,
                "device": "cuda" if torch.cuda.is_available() else "cpu",
            },
        )
        shutil.copy2(
            repository_root() / "configs/echo/full_matrix_smoke.json",
            root / "full_matrix_smoke_config.json",
        )
        for name in (
            "authoritative_source_lock.json",
            "figures_5_8_contract.json",
            "locked_evaluation_protocol.json",
            "locked_method_contract.json",
        ):
            shutil.copy2(
                repository_root() / "configs/echo" / name,
                root / name,
            )
    return root


def _runtime(
    config: FullMatrixSmokeConfig,
    *,
    agent_count: int,
    arrival_probability: float,
    timeout_seconds: float,
    cpu_ghz: float = 5.0,
) -> SharedRuntimeParameters:
    return SharedRuntimeParameters(
        slot_duration=config.slot_duration_seconds,
        local_service_capacity=cpu_ghz * config.slot_duration_seconds,
        public_service_capacity=cpu_ghz * config.slot_duration_seconds,
        cloud_service_capacity=30.0 * config.slot_duration_seconds,
        arrival_probability=arrival_probability,
        agent_count=agent_count,
        timeout_slots=max(1, round(timeout_seconds / config.slot_duration_seconds)),
        metadata={"contract": "configs/echo/hoodie_physical_contract.json"},
    )


def _trace(
    config: FullMatrixSmokeConfig,
    *,
    trace_id: str,
    seed: int,
    agent_count: int,
    arrival_probability: float,
    timeout_seconds: float,
    task_sizes: tuple[float, ...] | None = None,
) -> EvaluationTrace:
    return build_deterministic_trace(
        trace_id,
        seed,
        config.episode_slots,
        agent_count=agent_count,
        arrival_probability=arrival_probability,
        timeout_length=max(1, round(timeout_seconds / config.slot_duration_seconds)),
        drain_slots=config.drain_slots,
        processing_density=config.processing_density,
        task_sizes=task_sizes,
    )


def _link_rates(
    config: FullMatrixSmokeConfig, horizontal: float, vertical: float
) -> LinkRateConfig:
    return LinkRateConfig(
        horizontal_data_rate_mbps=horizontal,
        vertical_data_rate_mbps=vertical,
        slot_duration_seconds=config.slot_duration_seconds,
    )


def _controls(method: str) -> EchoControlConfig:
    if method in {"ECHO", "ECHO-NoLSTM"}:
        return EchoControlConfig.enabled()
    return EchoControlConfig.disabled()


def _action_family(action: str) -> str:
    if action.startswith("horizontal"):
        return "horizontal"
    if action in {"vertical", "cloud", "offload_vertical"}:
        return "vertical"
    return "local"


def _run_episode(
    *,
    policy: Any,
    method: str,
    trace: EvaluationTrace,
    config: FullMatrixSmokeConfig,
    agent_count: int,
    arrival_probability: float,
    timeout_seconds: float,
    cpu_ghz: float = 5.0,
    horizontal_rate: float = 30.0,
    vertical_rate: float = 10.0,
    training: bool = False,
    learning_rate: float | None = None,
) -> dict[str, Any]:
    runtime = _runtime(
        config,
        agent_count=agent_count,
        arrival_probability=arrival_probability,
        timeout_seconds=timeout_seconds,
        cpu_ghz=cpu_ghz,
    )
    env = EvaluationHoodieGymEnvironment(
        episode_length=config.episode_slots,
        topology=_topology(agent_count),
        runtime_parameters=runtime,
        compute_config=runtime.to_compute_config(),
        link_rate_config=_link_rates(config, horizontal_rate, vertical_rate),
        policy_name=method,
        supplied_trace=trace,
        echo_controls=_controls(method),
    )
    env.reset(seed=trace.seed)
    pending: dict[int, dict[str, Any]] = {}
    latest_state: dict[str, dict[str, object]] = {}
    task_rows: list[dict[str, Any]] = []
    decision_rows: list[dict[str, Any]] = []
    rewards: list[float] = []
    losses: list[float] = []
    action_counts = {"local": 0, "horizontal": 0, "vertical": 0}
    while True:
        _observation, _reward, terminated, truncated, info = env.step_slot(policy)
        for decision in info.get("decision_events", []):
            task_id = int(decision["task_id"])
            agent_id = str(decision["source_agent_id"])
            action = str(decision["action"])
            state = dict(decision["state"])
            pending[task_id] = {"agent_id": agent_id, "action": action, "state": state}
            latest_state[agent_id] = state
            action_counts[_action_family(action)] += 1
            legal = dict(decision.get("legal_action_mask", {}))
            decision_rows.append(
                {
                    "trace_id": trace.trace_id,
                    "task_id": task_id,
                    "source_agent_id": agent_id,
                    "decision_slot": decision["decision_slot"],
                    "selected_action": action,
                    "selected_action_legal": bool(legal.get(action, False)),
                    "resolved_destination": decision.get("resolved_destination"),
                }
            )
        for resolution in info.get("task_resolution_events", []):
            task_id = int(resolution["task_id"])
            decision = pending.get(task_id, {})
            task_rows.append(
                {
                    "trace_id": trace.trace_id,
                    "task_id": task_id,
                    "source_agent_id": resolution.get("source_id"),
                    "outcome": "successful" if resolution.get("outcome") == "success" else "dropped",
                    "duration_slots": resolution.get("duration_slots"),
                    "selected_action": decision.get("action"),
                    "completion_slot": resolution.get("completion_slot"),
                }
            )
        for delivery in info.get("reward_delivery_events", []):
            task_id = int(delivery["task_id"])
            decision = pending.pop(task_id, None)
            if decision is None:
                raise RuntimeError(f"reward delivery lacks decision for task {task_id}")
            reward = float(delivery["reward"])
            rewards.append(reward)
            if training:
                next_state = latest_state.get(decision["agent_id"], decision["state"])
                policy.record_transition(
                    agent_id=decision["agent_id"],
                    state=decision["state"],
                    action=decision["action"],
                    reward=reward,
                    next_state=next_state,
                    done=bool(terminated or truncated),
                )
                loss = policy.learn_from_replay(
                    agent_id=decision["agent_id"],
                    batch_size=config.batch_size,
                    learning_rate=(
                        config.learning_rate if learning_rate is None else learning_rate
                    ),
                )
                if loss is not None:
                    if not math.isfinite(float(loss)):
                        raise ValueError("non-finite learner loss in full-matrix smoke")
                    losses.append(float(loss))
        if terminated or truncated:
            break
    generated = len(trace.tasks)
    successful = sum(row["outcome"] == "successful" for row in task_rows)
    dropped = sum(row["outcome"] == "dropped" for row in task_rows)
    if pending or generated != successful + dropped:
        raise ValueError("full-matrix smoke task accounting failed")
    delays = [
        float(row["duration_slots"]) + 1.0
        for row in task_rows
        if row["outcome"] == "successful" and row["duration_slots"] is not None
    ]
    return {
        "summary": {
            "trace_id": trace.trace_id,
            "trace_seed": trace.seed,
            "generated_tasks": generated,
            "successful_tasks": successful,
            "dropped_tasks": dropped,
            "drop_ratio": dropped / generated if generated else 0.0,
            "successful_task_delay": float(np.mean(delays)) if delays else 0.0,
            "accumulated_reward": float(sum(rewards)),
            "local_actions": action_counts["local"],
            "horizontal_actions": action_counts["horizontal"],
            "vertical_actions": action_counts["vertical"],
            "finite_loss_count": len(losses),
        },
        "tasks": task_rows,
        "decisions": decision_rows,
    }


def _new_policy(
    method: str,
    agent_count: int,
    seed: int,
    config: FullMatrixSmokeConfig,
    *,
    learning_rate: float | None = None,
    discount_factor: float | None = None,
) -> DistributedHoodiePolicy:
    policy = DistributedHoodiePolicy.configured(
        agent_count=agent_count,
        seed=seed,
        use_lstm=method != "ECHO-NoLSTM",
        learning_rate=learning_rate or config.learning_rate,
        discount_factor=discount_factor or config.discount_factor,
        batch_size=config.batch_size,
        replay_capacity=config.replay_capacity,
        target_update_interval=config.target_update_interval,
        hidden_dims=config.hidden_dims,
        lookback=config.lookback,
        lstm_hidden=config.lstm_hidden,
        device_name="cpu",
        topology=_topology(agent_count),
    )
    policy.policy_name = method
    return policy


def _checkpoint_key(
    method: str,
    agent_count: int,
    seed: int,
    learning_rate: float,
    discount_factor: float,
) -> str:
    return (
        f"{method.lower().replace('-', '_')}-n{agent_count}-seed{seed}"
        f"-lr{learning_rate:.0e}-g{discount_factor:g}"
    )


def _train_checkpoint(
    root: Path,
    *,
    method: str,
    agent_count: int,
    seed: int,
    config: FullMatrixSmokeConfig,
    learning_rate: float | None = None,
    discount_factor: float | None = None,
) -> tuple[DistributedHoodiePolicy, list[dict[str, Any]], dict[str, Any]]:
    lr = learning_rate if learning_rate is not None else config.learning_rate
    gamma = discount_factor if discount_factor is not None else config.discount_factor
    key = _checkpoint_key(method, agent_count, seed, lr, gamma)
    directory = root / "checkpoints" / key
    checkpoint_path = directory / "checkpoint.pt"
    metrics_path = directory / "training_metrics.csv"
    record_path = directory / "checkpoint.json"
    if checkpoint_path.exists() and metrics_path.exists() and record_path.exists():
        state = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
        if state.get("source_commit") != source_commit():
            raise ValueError(f"stale smoke checkpoint: {key}")
        policy = DistributedHoodiePolicy.from_state(state["policy_state"])
        policy.policy_name = method
        import csv

        with metrics_path.open(newline="", encoding="utf-8") as handle:
            metrics = list(csv.DictReader(handle))
        return policy, metrics, read_json(record_path)
    directory.mkdir(parents=True, exist_ok=True)
    policy = _new_policy(
        method,
        agent_count,
        seed,
        config,
        learning_rate=lr,
        discount_factor=gamma,
    )
    metrics: list[dict[str, Any]] = []
    for episode in range(config.training_episodes):
        policy.exploration_epsilon = max(0.05, 1.0 - episode / config.training_episodes)
        trace = _trace(
            config,
            trace_id=f"smoke-train-{key}-episode-{episode}",
            seed=1_000_000 + seed * 100 + episode,
            agent_count=agent_count,
            arrival_probability=0.5,
            timeout_seconds=2.0,
        )
        result = _run_episode(
            policy=policy,
            method=method,
            trace=trace,
            config=config,
            agent_count=agent_count,
            arrival_probability=0.5,
            timeout_seconds=2.0,
            training=True,
            learning_rate=lr,
        )
        metrics.append(
            {
                "method": method,
                "agent_count": agent_count,
                "seed": seed,
                "episode": episode,
                "learning_rate": lr,
                "discount_factor": gamma,
                **result["summary"],
            }
        )
        torch.save(
            {
                "source_commit": source_commit(),
                "next_episode": episode + 1,
                "policy_state": policy.export_state(),
            },
            checkpoint_path,
        )
        atomic_json(
            directory / "progress.json",
            {
                "status": "running",
                "completed_episodes": episode + 1,
                "total_episodes": config.training_episodes,
                "updated_at": _now(),
            },
        )
    atomic_csv(metrics_path, metrics)
    record = {
        "key": key,
        "method": method,
        "agent_count": agent_count,
        "seed": seed,
        "learning_rate": lr,
        "discount_factor": gamma,
        "training_episodes": config.training_episodes,
        "checkpoint": str(checkpoint_path),
        "checkpoint_sha256": file_sha256(checkpoint_path),
        "finite_loss_count": sum(int(row["finite_loss_count"]) for row in metrics),
        "source_commit": source_commit(),
    }
    if record["finite_loss_count"] <= 0:
        raise ValueError(f"checkpoint {key} completed without a finite replay loss")
    atomic_json(record_path, record)
    atomic_json(directory / "COMPLETED.json", {"status": "completed", **record})
    return policy, metrics, record


def _fresh_learned_policy(record: dict[str, Any], method: str) -> DistributedHoodiePolicy:
    state = torch.load(record["checkpoint"], map_location="cpu", weights_only=False)
    policy = DistributedHoodiePolicy.from_state(state["policy_state"])
    policy.policy_name = method
    policy.exploration_epsilon = 0.0
    return policy


def _policy_factory(
    method: str, record: dict[str, Any] | None, seed: int
) -> Callable[[], Any]:
    if method in LEARNED_METHODS:
        if record is None:
            raise ValueError(f"missing learned checkpoint for {method}")
        return lambda: _fresh_learned_policy(record, method)
    return lambda: (
        PolicyRegistry.resolve(method)
        if method != "RO"
        else RandomOffloadingPolicy(seed=seed)
    )


def _evaluation_row(
    *,
    panel_id: str,
    series: str,
    x_name: str,
    x_value: float,
    method: str,
    result: dict[str, Any],
    checkpoint_sha256: str | None,
) -> dict[str, Any]:
    summary = result["summary"]
    return {
        "panel_id": panel_id,
        "series": series,
        "method": method,
        "seed": 101,
        "x_name": x_name,
        "x_value": x_value,
        "metric": "",
        "metric_value": 0.0,
        "trace_id": summary["trace_id"],
        "trace_seed": summary["trace_seed"],
        "generated_tasks": summary["generated_tasks"],
        "successful_tasks": summary["successful_tasks"],
        "dropped_tasks": summary["dropped_tasks"],
        "drop_ratio": summary["drop_ratio"],
        "successful_task_delay": summary["successful_task_delay"],
        "accumulated_reward": summary["accumulated_reward"],
        "local_actions": summary["local_actions"],
        "horizontal_actions": summary["horizontal_actions"],
        "vertical_actions": summary["vertical_actions"],
        "checkpoint_sha256": checkpoint_sha256 or "",
        "decision_count": len(result["decisions"]),
        "illegal_selected_action_count": sum(
            not bool(row["selected_action_legal"]) for row in result["decisions"]
        ),
        "task_record_count": len(result["tasks"]),
    }


def _evaluate_methods(
    *,
    panel_id: str,
    methods: tuple[str, ...],
    series: str,
    x_name: str,
    x_value: float,
    trace: EvaluationTrace,
    config: FullMatrixSmokeConfig,
    agent_count: int,
    arrival_probability: float,
    timeout_seconds: float,
    records: dict[tuple[str, int], dict[str, Any]],
    cpu_ghz: float = 5.0,
    horizontal_rate: float = 30.0,
    vertical_rate: float = 10.0,
) -> list[dict[str, Any]]:
    rows = []
    for method in methods:
        record = records.get((method, agent_count))
        policy = _policy_factory(method, record, trace.seed)()
        result = _run_episode(
            policy=policy,
            method=method,
            trace=trace,
            config=config,
            agent_count=agent_count,
            arrival_probability=arrival_probability,
            timeout_seconds=timeout_seconds,
            cpu_ghz=cpu_ghz,
            horizontal_rate=horizontal_rate,
            vertical_rate=vertical_rate,
        )
        rows.append(
            _evaluation_row(
                panel_id=panel_id,
                series=series,
                x_name=x_name,
                x_value=x_value,
                method=method,
                result=result,
                checkpoint_sha256=record.get("checkpoint_sha256") if record else None,
            )
        )
    return rows


def _render_composite(
    rows: list[dict[str, Any]], figure_id: str, panels: tuple[str, ...], output: Path
) -> list[dict[str, Any]]:
    if len(panels) <= 2:
        nrows, ncols = 1, len(panels)
    else:
        ncols = 3
        nrows = math.ceil(len(panels) / ncols)
    figure, axes = plt.subplots(
        nrows, ncols, figsize=(5.2 * ncols, 3.8 * nrows), squeeze=False, constrained_layout=True
    )
    flat = list(axes.flat)
    for axis, panel_id in zip(flat, panels):
        panel_rows = [row for row in rows if row["panel_id"] == panel_id]
        series_names = list(dict.fromkeys(str(row["series"]) for row in panel_rows))
        for series in series_names:
            selected = [row for row in panel_rows if row["series"] == series]
            selected.sort(key=lambda row: float(row["x_value"]))
            axis.plot(
                [float(row["x_value"]) for row in selected],
                [float(row["metric_value"]) for row in selected],
                marker="o",
                linewidth=1.4,
                label=series,
            )
        axis.set_title(panel_id.replace("_", " ").title())
        axis.set_xlabel(str(panel_rows[0]["x_name"]) if panel_rows else "")
        axis.set_ylabel(str(panel_rows[0]["metric"]) if panel_rows else "")
        axis.grid(alpha=0.25)
        if len(series_names) > 1:
            axis.legend(fontsize=7, frameon=False)
    for axis in flat[len(panels) :]:
        axis.set_visible(False)
    figure.suptitle(f"{figure_id.upper()} — full-matrix execution smoke (not paper evidence)")
    records = []
    for suffix, options in (("pdf", {}), ("svg", {}), ("png", {"dpi": 300})):
        path = output.with_suffix(f".{suffix}")
        figure.savefig(path, **options)
        records.append(
            {
                "figure_id": figure_id,
                "path": str(path),
                "format": suffix,
                "dpi": 300 if suffix == "png" else None,
                "sha256": file_sha256(path),
                "bytes": path.stat().st_size,
            }
        )
    plt.close(figure)
    return records


def _render_topology(root: Path) -> list[dict[str, Any]]:
    topology = _topology(20)
    figure, axis = plt.subplots(figsize=(7.2, 7.2), constrained_layout=True)
    nodes = list(topology.node_ids)
    angles = np.linspace(0, 2 * np.pi, len(nodes), endpoint=False)
    positions = {node: (math.cos(angle), math.sin(angle)) for node, angle in zip(nodes, angles)}
    drawn: set[tuple[str, str]] = set()
    for source in nodes:
        for destination in topology.legal_horizontal_destinations(source):
            edge = tuple(sorted((source, destination)))
            if edge in drawn:
                continue
            drawn.add(edge)
            x = [positions[source][0], positions[destination][0]]
            y = [positions[source][1], positions[destination][1]]
            axis.plot(x, y, color="#9aa0a6", linewidth=0.6, zorder=1)
    for node, (x, y) in positions.items():
        axis.scatter([x], [y], s=120, color="#1769aa", zorder=2)
        axis.text(x, y, node, color="white", ha="center", va="center", fontsize=7, zorder=3)
    axis.set_title("Figure 4 — simulator topology (20 Edge Agents)")
    axis.set_aspect("equal")
    axis.axis("off")
    output = root / "results/figures/figure_4_topology"
    records = []
    for suffix, options in (("pdf", {}), ("svg", {}), ("png", {"dpi": 300})):
        path = output.with_suffix(f".{suffix}")
        figure.savefig(path, **options)
        records.append(
            {
                "figure_id": "figure_4",
                "path": str(path),
                "format": suffix,
                "dpi": 300 if suffix == "png" else None,
                "sha256": file_sha256(path),
                "bytes": path.stat().st_size,
            }
        )
    plt.close(figure)
    return records


def _run_matrix(root: Path, config: FullMatrixSmokeConfig) -> dict[str, Any]:
    axes = _paper_axes()
    data_dir = root / "results/data"
    figures_dir = root / "results/figures"
    data_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    records: dict[tuple[str, int], dict[str, Any]] = {}
    all_checkpoint_records: dict[str, dict[str, Any]] = {}
    training_rows: list[dict[str, Any]] = []

    for agent_count in axes["agent_counts"]:
        _policy, metrics, record = _train_checkpoint(
            root,
            method="ECHO",
            agent_count=int(agent_count),
            seed=101,
            config=config,
        )
        records[("ECHO", int(agent_count))] = record
        all_checkpoint_records[record["key"]] = record
        training_rows.extend(metrics)
    for method in ("HOODIE", "ECHO-NoLSTM"):
        _policy, metrics, record = _train_checkpoint(
            root, method=method, agent_count=20, seed=101, config=config
        )
        records[(method, 20)] = record
        all_checkpoint_records[record["key"]] = record
        training_rows.extend(metrics)

    figure5_rows: list[dict[str, Any]] = []
    for panel_id, values, parameter in (
        ("figure_5a", axes["learning_rates"], "learning_rate"),
        ("figure_5b", axes["discount_factors"], "discount_factor"),
    ):
        for value in values:
            kwargs = {parameter: float(value)}
            _policy, metrics, record = _train_checkpoint(
                root,
                method="ECHO",
                agent_count=20,
                seed=201,
                config=config,
                **kwargs,
            )
            all_checkpoint_records[record["key"]] = record
            for row in metrics:
                figure5_rows.append(
                    {
                        "panel_id": panel_id,
                        "series": f"{parameter}={float(value):g}",
                        "method": "ECHO",
                        "seed": 201,
                        "x_name": "training episode",
                        "x_value": float(row["episode"]),
                        "metric": "accumulated reward",
                        "metric_value": float(row["accumulated_reward"]),
                        "generated_tasks": int(row["generated_tasks"]),
                        "successful_tasks": int(row["successful_tasks"]),
                        "dropped_tasks": int(row["dropped_tasks"]),
                        "trace_id": row["trace_id"],
                    }
                )
    atomic_json(root / "stages/training_completed.json", {"status": "completed", "at": _now()})

    figure6_rows: list[dict[str, Any]] = []
    for probability in axes["arrival_probabilities"]:
        for agent_count in (10, 15, 20):
            trace = _trace(
                config,
                trace_id=f"smoke-figure6a-p{probability}-n{agent_count}",
                seed=6_000_000 + int(probability * 100) * 100 + agent_count,
                agent_count=agent_count,
                arrival_probability=float(probability),
                timeout_seconds=2.0,
            )
            row = _evaluate_methods(
                panel_id="figure_6a",
                methods=("ECHO",),
                series=f"N={agent_count}",
                x_name="arrival probability",
                x_value=float(probability),
                trace=trace,
                config=config,
                agent_count=agent_count,
                arrival_probability=float(probability),
                timeout_seconds=2.0,
                records=records,
            )[0]
            row.update(metric="average reward", metric_value=row["accumulated_reward"])
            figure6_rows.append(row)
        trace = _trace(
            config,
            trace_id=f"smoke-figure6b-p{probability}-n20",
            seed=6_100_000 + int(probability * 100),
            agent_count=20,
            arrival_probability=float(probability),
            timeout_seconds=2.0,
        )
        base = _evaluate_methods(
            panel_id="figure_6b",
            methods=("ECHO",),
            series="ECHO",
            x_name="arrival probability",
            x_value=float(probability),
            trace=trace,
            config=config,
            agent_count=20,
            arrival_probability=float(probability),
            timeout_seconds=2.0,
            records=records,
        )[0]
        for family, column in (
            ("local", "local_actions"),
            ("horizontal", "horizontal_actions"),
            ("vertical", "vertical_actions"),
        ):
            row = dict(base)
            row.update(series=family, metric="selected actions", metric_value=row[column])
            figure6_rows.append(row)
    for cpu in axes["figure_6_cpu_ghz"]:
        for agent_count in (10, 15, 20):
            trace = _trace(
                config,
                trace_id=f"smoke-figure6c-cpu{cpu}-n{agent_count}",
                seed=6_200_000 + int(cpu) * 100 + agent_count,
                agent_count=agent_count,
                arrival_probability=0.5,
                timeout_seconds=2.0,
            )
            row = _evaluate_methods(
                panel_id="figure_6c",
                methods=("ECHO",),
                series=f"N={agent_count}",
                x_name="EA CPU (GHz)",
                x_value=float(cpu),
                trace=trace,
                config=config,
                agent_count=agent_count,
                arrival_probability=0.5,
                timeout_seconds=2.0,
                cpu_ghz=float(cpu),
                records=records,
            )[0]
            row.update(metric="average reward", metric_value=row["accumulated_reward"])
            figure6_rows.append(row)
    for profile, values in axes["traffic_profiles"].items():
        for agent_count in axes["agent_counts"]:
            trace = _trace(
                config,
                trace_id=f"smoke-figure6d-{profile}-n{agent_count}",
                seed=6_300_000 + list(axes["traffic_profiles"]).index(profile) * 1000 + int(agent_count),
                agent_count=int(agent_count),
                arrival_probability=float(values["arrival_probability"]),
                timeout_seconds=2.0,
                task_sizes=tuple(float(value) for value in values["task_sizes_mbits"]),
            )
            row = _evaluate_methods(
                panel_id="figure_6d",
                methods=("ECHO",),
                series=profile,
                x_name="number of EAs",
                x_value=float(agent_count),
                trace=trace,
                config=config,
                agent_count=int(agent_count),
                arrival_probability=float(values["arrival_probability"]),
                timeout_seconds=2.0,
                records=records,
            )[0]
            row.update(metric="average reward", metric_value=row["accumulated_reward"])
            figure6_rows.append(row)
    for profile, values in axes["rate_profiles_mbps"].items():
        for agent_count in axes["agent_counts"]:
            trace = _trace(
                config,
                trace_id=f"smoke-figure6e-{profile}-n{agent_count}",
                seed=6_400_000 + list(axes["rate_profiles_mbps"]).index(profile) * 1000 + int(agent_count),
                agent_count=int(agent_count),
                arrival_probability=0.5,
                timeout_seconds=2.0,
            )
            row = _evaluate_methods(
                panel_id="figure_6e",
                methods=("ECHO",),
                series=profile,
                x_name="number of EAs",
                x_value=float(agent_count),
                trace=trace,
                config=config,
                agent_count=int(agent_count),
                arrival_probability=0.5,
                timeout_seconds=2.0,
                horizontal_rate=float(values["horizontal"]),
                vertical_rate=float(values["vertical"]),
                records=records,
            )[0]
            row.update(metric="average reward", metric_value=row["accumulated_reward"])
            figure6_rows.append(row)
    atomic_json(root / "stages/figure_6_completed.json", {"status": "completed", "rows": len(figure6_rows)})

    figure7_rows: list[dict[str, Any]] = []
    panel_specs = (
        ("figure_7a", "arrival probability", axes["arrival_probabilities"], 10.0, 5.0),
        ("figure_7b", "EA CPU (GHz)", axes["figure_7_cpu_ghz"], 10.0, None),
        ("figure_7c", "timeout (seconds)", axes["figure_7_delay_timeouts_seconds"], None, 5.0),
        ("figure_7d", "arrival probability", axes["arrival_probabilities"], 2.0, 5.0),
        ("figure_7e", "EA CPU (GHz)", axes["figure_7_cpu_ghz"], 2.0, None),
        ("figure_7f", "timeout (seconds)", axes["figure_7_drop_timeouts_seconds"], None, 5.0),
    )
    for panel_id, x_name, values, fixed_timeout, fixed_cpu in panel_specs:
        for value in values:
            probability = float(value) if "arrival" in x_name else 0.5
            timeout = float(value) if "timeout" in x_name else float(fixed_timeout)
            cpu = float(value) if "CPU" in x_name else float(fixed_cpu)
            trace = _trace(
                config,
                trace_id=f"smoke-{panel_id}-{value}",
                seed=7_000_000 + PANEL_IDS.index(panel_id) * 1000 + list(values).index(value),
                agent_count=20,
                arrival_probability=probability,
                timeout_seconds=timeout,
            )
            rows = _evaluate_methods(
                panel_id=panel_id,
                methods=MAIN_METHODS,
                series="",
                x_name=x_name,
                x_value=float(value),
                trace=trace,
                config=config,
                agent_count=20,
                arrival_probability=probability,
                timeout_seconds=timeout,
                cpu_ghz=cpu,
                records=records,
            )
            for row in rows:
                is_delay = panel_id in {"figure_7a", "figure_7b", "figure_7c"}
                row.update(
                    series=row["method"],
                    metric="negative successful-task delay" if is_delay else "task drop ratio",
                    metric_value=-float(row["successful_task_delay"]) if is_delay else float(row["drop_ratio"]),
                )
                figure7_rows.append(row)
    atomic_json(root / "stages/figure_7_completed.json", {"status": "completed", "rows": len(figure7_rows)})

    figure8_rows: list[dict[str, Any]] = []
    for method in ABLATION_METHODS:
        record = records[(method, 20)]
        metrics_path = Path(record["checkpoint"]).with_name("training_metrics.csv")
        import csv

        with metrics_path.open(newline="", encoding="utf-8") as handle:
            metrics = list(csv.DictReader(handle))
        for row in metrics:
            figure8_rows.append(
                {
                    "panel_id": "figure_8a",
                    "series": method,
                    "method": method,
                    "seed": 101,
                    "x_name": "training episode",
                    "x_value": float(row["episode"]),
                    "metric": "negative successful-task delay",
                    "metric_value": -float(row["successful_task_delay"]),
                    "generated_tasks": int(row["generated_tasks"]),
                    "successful_tasks": int(row["successful_tasks"]),
                    "dropped_tasks": int(row["dropped_tasks"]),
                    "trace_id": row["trace_id"],
                }
            )
    for probability in axes["arrival_probabilities"]:
        trace = _trace(
            config,
            trace_id=f"smoke-figure8b-p{probability}",
            seed=8_000_000 + int(probability * 100),
            agent_count=20,
            arrival_probability=float(probability),
            timeout_seconds=1.0,
        )
        rows = _evaluate_methods(
            panel_id="figure_8b",
            methods=ABLATION_METHODS,
            series="",
            x_name="arrival probability",
            x_value=float(probability),
            trace=trace,
            config=config,
            agent_count=20,
            arrival_probability=float(probability),
            timeout_seconds=1.0,
            records=records,
        )
        for row in rows:
            row.update(
                series=row["method"],
                metric="negative successful-task delay",
                metric_value=-float(row["successful_task_delay"]),
            )
            figure8_rows.append(row)
    atomic_json(root / "stages/figure_8_completed.json", {"status": "completed", "rows": len(figure8_rows)})

    all_rows = figure5_rows + figure6_rows + figure7_rows + figure8_rows
    panel_fields = (
        "panel_id",
        "series",
        "method",
        "seed",
        "x_name",
        "x_value",
        "metric",
        "metric_value",
        "trace_id",
        "trace_seed",
        "generated_tasks",
        "successful_tasks",
        "dropped_tasks",
        "drop_ratio",
        "successful_task_delay",
        "accumulated_reward",
        "local_actions",
        "horizontal_actions",
        "vertical_actions",
        "checkpoint_sha256",
        "decision_count",
        "illegal_selected_action_count",
        "task_record_count",
    )
    normalized_rows = [
        {field: row.get(field, "") for field in panel_fields} for row in all_rows
    ]
    atomic_csv(data_dir / "panel_values.csv", normalized_rows)
    atomic_csv(data_dir / "seed_level_values.csv", normalized_rows)
    atomic_csv(data_dir / "training_metrics.csv", training_rows)
    aggregate_rows = [
        {
            "panel_id": row["panel_id"],
            "series": row["series"],
            "method": row["method"],
            "x_name": row["x_name"],
            "x_value": row["x_value"],
            "seed_count": 1,
            "mean": row["metric_value"],
            "ci95": 0.0,
            "generated_tasks": row["generated_tasks"],
            "successful_tasks": row["successful_tasks"],
            "dropped_tasks": row["dropped_tasks"],
        }
        for row in all_rows
    ]
    atomic_csv(data_dir / "mean_ci95.csv", aggregate_rows)

    figure_records = _render_topology(root)
    figure_records += _render_composite(
        figure5_rows, "figure_5", ("figure_5a", "figure_5b"), figures_dir / "figure_5_learning_parameters"
    )
    figure_records += _render_composite(
        figure6_rows,
        "figure_6",
        tuple(f"figure_6{letter}" for letter in "abcde"),
        figures_dir / "figure_6_behavior_scalability",
    )
    figure_records += _render_composite(
        figure7_rows,
        "figure_7",
        tuple(f"figure_7{letter}" for letter in "abcdef"),
        figures_dir / "figure_7_baseline_comparison",
    )
    figure_records += _render_composite(
        figure8_rows, "figure_8", ("figure_8a", "figure_8b"), figures_dir / "figure_8_lstm_ablation"
    )
    return {
        "rows": all_rows,
        "aggregate_rows": aggregate_rows,
        "figure_records": figure_records,
        "checkpoint_records": list(all_checkpoint_records.values()),
    }


def _verify_matrix(root: Path, result: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    rows = result["rows"]
    if {row["panel_id"] for row in rows} != set(PANEL_IDS):
        errors.append("the 15-panel manuscript matrix is incomplete")
    axes = _paper_axes()
    for panel_id in (f"figure_7{letter}" for letter in "abcdef"):
        panel_rows = [row for row in rows if row["panel_id"] == panel_id]
        expected_points = 5
        if len(panel_rows) != expected_points * len(MAIN_METHODS):
            errors.append(f"{panel_id} does not contain all methods at all points")
        for value in {row["x_value"] for row in panel_rows}:
            methods = {row["method"] for row in panel_rows if row["x_value"] == value}
            if methods != set(MAIN_METHODS):
                errors.append(f"{panel_id} point {value} has method mismatch")
            traces = {row["trace_id"] for row in panel_rows if row["x_value"] == value}
            if len(traces) != 1:
                errors.append(f"{panel_id} point {value} is not trace-paired")
    for row in rows:
        if int(row["generated_tasks"]) != int(row["successful_tasks"]) + int(row["dropped_tasks"]):
            errors.append(f"task conservation failed in {row['panel_id']}")
            break
        if int(row.get("illegal_selected_action_count") or 0) != 0:
            errors.append(f"illegal selected action in {row['panel_id']}")
            break
    for panel_id in ("figure_8a", "figure_8b"):
        methods = {row["method"] for row in rows if row["panel_id"] == panel_id}
        if methods != set(ABLATION_METHODS):
            errors.append(f"{panel_id} ablation methods are incorrect")
    figure_records = result["figure_records"]
    for figure_id in ("figure_4", "figure_5", "figure_6", "figure_7", "figure_8"):
        formats = {record["format"] for record in figure_records if record["figure_id"] == figure_id}
        if formats != {"pdf", "svg", "png"}:
            errors.append(f"incomplete figure formats for {figure_id}")
        png_records = [record for record in figure_records if record["figure_id"] == figure_id and record["format"] == "png"]
        if png_records:
            with Image.open(png_records[0]["path"]) as image:
                dpi = image.info.get("dpi", (0, 0))
            if not dpi or min(float(value) for value in dpi) < 299:
                errors.append(f"PNG is not 300 dpi for {figure_id}")
    if len(result["checkpoint_records"]) != 17:
        errors.append(
            "expected 17 unique checkpoints covering topology, learning-rate, "
            "discount-factor, HOODIE, and no-LSTM execution paths"
        )
    return {
        "status": "failed" if errors else "completed",
        "verified": not errors,
        "errors": errors,
        "panels_verified": len(PANEL_IDS),
        "main_methods_verified": list(MAIN_METHODS),
        "ablation_methods_verified": list(ABLATION_METHODS),
        "figure_files_verified": len(figure_records),
        "paper_protocol": {
            "training_episodes": 5000,
            "seeds": 10,
            "held_out_episodes_per_seed_and_point": 200,
            "episode_slots": 110,
        },
        "smoke_protocol": {
            "training_episodes": 3,
            "seeds": 1,
            "held_out_episodes_per_point": 1,
            "episode_slots": 16,
        },
        "paper_evidence": False,
        "paper_scale_started": False,
        "projected_or_surrogate_values_used": False,
        "axis_contract_loaded": bool(axes),
    }


def run_full_matrix_smoke(
    run_root: str | Path,
    campaign_id: str,
    *,
    config: FullMatrixSmokeConfig | None = None,
) -> dict[str, Any]:
    resolved = config or FullMatrixSmokeConfig()
    root = _campaign(run_root, campaign_id, resolved)
    terminal = root / "terminal_status.json"
    if terminal.exists() and read_json(terminal).get("verified"):
        return {**read_json(terminal), "resumed": True}
    result = _run_matrix(root, resolved)
    verification = _verify_matrix(root, result)
    atomic_json(root / "verification_report.json", verification)
    if not verification["verified"]:
        raise ValueError(f"full-matrix smoke verification failed: {verification['errors']}")
    manifest = {
        "schema_version": 1,
        "status": "FULL_MATRIX_SMOKE_COMPLETE",
        "label": LABEL,
        "campaign_id": campaign_id,
        "source_commit": source_commit(),
        "methods": {
            "main_comparison": list(MAIN_METHODS),
            "ablation_only": list(ABLATION_METHODS),
        },
        "panel_ids": list(PANEL_IDS),
        "checkpoints": result["checkpoint_records"],
        "figures": result["figure_records"],
        **verification,
    }
    atomic_json(root / "results/manifest.json", manifest)
    archive = root / "results" / f"{campaign_id}-full-matrix-smoke.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as handle:
        for path in sorted(root.rglob("*")):
            if path.is_file() and path != archive and "checkpoints" not in path.parts:
                handle.write(path, path.relative_to(root))
    archive_record = {
        "path": str(archive),
        "sha256": file_sha256(archive),
        "bytes": archive.stat().st_size,
    }
    atomic_json(root / "results/archive.json", archive_record)
    terminal_payload = {
        **verification,
        "status": "completed",
        "completed_verification_and_figures": True,
        "completed_at": _now(),
        "campaign_id": campaign_id,
        "campaign_root": str(root),
        "source_commit": source_commit(),
        "label": LABEL,
        "archive": archive_record,
        "next_authorized_stage": "fresh resumable full-matrix pilot; 5000-episode paper campaign remains gated",
    }
    atomic_json(root / "VERIFIED.json", terminal_payload)
    atomic_json(root / "terminal_status.json", terminal_payload)
    write_sha256sums(root)
    return terminal_payload
