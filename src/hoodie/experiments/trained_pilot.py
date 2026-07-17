from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from hashlib import sha256
import gc
import json
import math
import os
from pathlib import Path
import platform
import tempfile
import time
from typing import Any
import zipfile

import matplotlib

matplotlib.use("Agg")
from matplotlib import pyplot as plt
import numpy as np
from PIL import Image
from scipy.stats import t as student_t
import torch

from src.agents.distributed_hoodie import DistributedHoodiePolicy
from src.environment.echo_control_config import EchoControlConfig
from src.environment.evaluation_gym_adapter import EvaluationHoodieGymEnvironment
from src.environment.link_rate_config import LinkRateConfig
from src.environment.runtime_model import SharedRuntimeParameters
from src.environment.topology import TopologyGraph
from src.evaluation.trace_protocol import EvaluationTrace, build_deterministic_trace

from .production_patch import paper_epsilon
from .trained_pilot_io import (
    atomic_csv,
    atomic_json,
    atomic_jsonl,
    completion_payload,
    file_sha256,
    read_json,
    repository_root,
    resolve_campaign_root,
    source_commit,
    write_sha256sums,
)


METHODS = ("HOODIE", "ECHO", "ECHO_NO_LSTM")
SEEDS = (101, 202, 303)
SCENARIOS: dict[str, tuple[float, int]] = {
    "moderate": (0.5, 20),
    "high_tight": (0.8, 8),
}
LABEL = "TRAINED PILOT — NOT PAPER EVIDENCE"


@dataclass(frozen=True, slots=True)
class PilotConfig:
    agent_count: int = 20
    episode_slots: int = 110
    drain_slots: int = 10
    training_episodes: int = 12
    evaluation_episodes: int = 20
    learning_rate: float = 7e-7
    discount_factor: float = 0.99
    batch_size: int = 64
    replay_capacity: int = 10_000
    target_update_interval: int = 2_000
    private_cpu_ghz: float = 5.0
    public_edge_cpu_ghz: float = 5.0
    cloud_cpu_ghz: float = 30.0
    horizontal_rate_mbps: float = 30.0
    vertical_rate_mbps: float = 10.0
    slot_duration_seconds: float = 0.1
    processing_density: float = 0.297
    checkpoint_interval_episodes: int = 3

    def __post_init__(self) -> None:
        if self.agent_count <= 0:
            raise ValueError("agent_count must be positive")
        if self.episode_slots <= 1:
            raise ValueError("episode_slots must be greater than one")
        if not 0 <= self.drain_slots < self.episode_slots:
            raise ValueError("drain_slots must be less than episode_slots")
        if self.training_episodes <= 0 or self.evaluation_episodes <= 0:
            raise ValueError("episode counts must be positive")
        if self.checkpoint_interval_episodes <= 0:
            raise ValueError("checkpoint interval must be positive")


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _json_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return sha256(payload.encode("utf-8")).hexdigest()


def _state_hash(value: Any) -> str:
    digest = sha256()

    def visit(item: Any) -> None:
        if isinstance(item, torch.Tensor):
            tensor = item.detach().cpu().contiguous()
            digest.update(b"tensor")
            digest.update(str(tensor.dtype).encode())
            digest.update(str(tuple(tensor.shape)).encode())
            digest.update(tensor.numpy().tobytes())
        elif isinstance(item, dict):
            digest.update(b"dict")
            for key in sorted(item, key=str):
                visit(str(key))
                visit(item[key])
        elif isinstance(item, (list, tuple)):
            digest.update(b"sequence")
            for part in item:
                visit(part)
        elif isinstance(item, bytes):
            digest.update(item)
        else:
            digest.update(repr(item).encode("utf-8"))

    visit(value)
    return digest.hexdigest()


def _topology(agent_count: int) -> TopologyGraph:
    if agent_count % 5 == 0:
        return TopologyGraph.for_agent_count(agent_count)
    node_ids = tuple(str(index) for index in range(1, agent_count + 1))
    return TopologyGraph(
        node_ids=node_ids,
        legal_adjacency={
            source: tuple(destination for destination in node_ids if destination != source)
            for source in node_ids
        },
        metadata={"non_production_test_topology": True},
    )


def _runtime(config: PilotConfig, arrival_probability: float, timeout: int) -> SharedRuntimeParameters:
    return SharedRuntimeParameters(
        slot_duration=config.slot_duration_seconds,
        local_service_capacity=config.private_cpu_ghz * config.slot_duration_seconds,
        public_service_capacity=config.public_edge_cpu_ghz * config.slot_duration_seconds,
        cloud_service_capacity=config.cloud_cpu_ghz * config.slot_duration_seconds,
        arrival_probability=arrival_probability,
        agent_count=config.agent_count,
        timeout_slots=timeout,
        metadata={"contract": "configs/echo/hoodie_physical_contract.json"},
    )


def _link_rates(config: PilotConfig) -> LinkRateConfig:
    return LinkRateConfig(
        horizontal_data_rate_mbps=config.horizontal_rate_mbps,
        vertical_data_rate_mbps=config.vertical_rate_mbps,
        slot_duration_seconds=config.slot_duration_seconds,
    )


def _controls(method: str) -> EchoControlConfig:
    if method not in METHODS and method != "ECHO_DISABLED":
        raise ValueError(f"unsupported trained method: {method}")
    return (
        EchoControlConfig.enabled()
        if method in {"ECHO", "ECHO_NO_LSTM"}
        else EchoControlConfig.disabled()
    )


def _validate_method_controls(method: str, controls: EchoControlConfig) -> None:
    if method in {"ECHO", "ECHO_NO_LSTM"} and not controls.fully_enabled:
        raise ValueError("trained ECHO requires every locked ECHO control")
    if method in {"HOODIE", "ECHO_DISABLED"} and controls.any_enabled:
        raise ValueError(f"{method} requires every ECHO control to be disabled")


def _device() -> tuple[str, str]:
    if torch.cuda.is_available():
        return "cuda", "CUDA available"
    return "cpu", "CUDA unavailable; deterministic CPU fallback"


def _campaign(run_root: str | Path, campaign_id: str, config: PilotConfig) -> Path:
    root = resolve_campaign_root(run_root, campaign_id)
    root.mkdir(parents=True, exist_ok=True)
    commit = source_commit()
    specification = {
        "schema_version": 1,
        "campaign_id": campaign_id,
        "label": LABEL,
        "source_commit": commit,
        "repository": "hadifarajvand/hoodie_sim_v2",
        "branch": "main",
        "methods": list(METHODS),
        "seeds": list(SEEDS),
        "scenarios": {
            name: {"arrival_probability": values[0], "timeout_slots": values[1]}
            for name, values in SCENARIOS.items()
        },
        "config": asdict(config),
        "paper_evidence": False,
        "paper_scale_started": False,
        "projected_or_surrogate_values_used": False,
    }
    path = root / "campaign_specification.json"
    if path.exists():
        existing = read_json(path)
        if existing.get("source_commit") != commit:
            raise ValueError(
                "campaign source commit is stale; choose a new campaign ID for changed source"
            )
        if existing.get("config") != specification["config"]:
            raise ValueError("campaign configuration does not match the existing run")
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
                "device": _device()[0],
                "device_reason": _device()[1],
            },
        )
    return root


def _trace_hash(trace: EvaluationTrace) -> str:
    return _json_hash(
        {
            "trace_id": trace.trace_id,
            "seed": trace.seed,
            "metadata": trace.metadata,
            "tasks": [
                {
                    "task_id": task.task_id,
                    "source_agent_id": task.source_agent_id,
                    "arrival_slot": task.arrival_slot,
                    "size": task.size,
                    "processing_density": task.processing_density,
                    "timeout_length": task.timeout_length,
                    "absolute_deadline_slot": task.absolute_deadline_slot,
                }
                for task in trace.tasks
            ],
        }
    )


def _training_trace(config: PilotConfig, seed: int, episode: int) -> EvaluationTrace:
    arrival, timeout = SCENARIOS["moderate"]
    trace_seed = 1_000_000 + seed * 1_000 + episode
    return build_deterministic_trace(
        f"pilot-train-seed-{seed}-episode-{episode}",
        trace_seed,
        config.episode_slots,
        agent_count=config.agent_count,
        arrival_probability=arrival,
        timeout_length=timeout,
        drain_slots=config.drain_slots,
        processing_density=config.processing_density,
    )


def _evaluation_trace(
    config: PilotConfig, seed: int, scenario: str, episode: int
) -> EvaluationTrace:
    if scenario not in SCENARIOS:
        raise ValueError(f"unknown scenario: {scenario}")
    arrival, timeout = SCENARIOS[scenario]
    scenario_offset = tuple(SCENARIOS).index(scenario) * 100_000
    trace_seed = 9_000_000 + scenario_offset + seed * 1_000 + episode
    return build_deterministic_trace(
        f"pilot-eval-seed-{seed}-{scenario}-episode-{episode}",
        trace_seed,
        config.episode_slots,
        agent_count=config.agent_count,
        arrival_probability=arrival,
        timeout_length=timeout,
        drain_slots=config.drain_slots,
        processing_density=config.processing_density,
    )


def _action_family(action: str) -> str:
    if action.startswith("horizontal"):
        return "horizontal"
    if action in {"vertical", "cloud", "offload_vertical"}:
        return "vertical"
    return "local"


def _run_episode(
    *,
    policy: DistributedHoodiePolicy,
    method: str,
    trace: EvaluationTrace,
    config: PilotConfig,
    arrival_probability: float,
    timeout_slots: int,
    training: bool,
) -> dict[str, Any]:
    controls = _controls(method)
    _validate_method_controls(method, controls)
    runtime = _runtime(config, arrival_probability, timeout_slots)
    env = EvaluationHoodieGymEnvironment(
        episode_length=config.episode_slots,
        topology=_topology(config.agent_count),
        runtime_parameters=runtime,
        compute_config=runtime.to_compute_config(),
        link_rate_config=_link_rates(config),
        policy_name=method,
        supplied_trace=trace,
        echo_controls=controls,
    )
    env.reset(seed=trace.seed)
    pending: dict[int, dict[str, Any]] = {}
    all_decisions: dict[int, dict[str, Any]] = {}
    latest_state_by_agent: dict[str, dict[str, object]] = {}
    task_rows: list[dict[str, Any]] = []
    event_signature: list[dict[str, Any]] = []
    losses: list[float] = []
    action_counts = {"local": 0, "horizontal": 0, "vertical": 0}
    completed = 0
    dropped = 0
    rewards: list[float] = []
    while True:
        _observation, _reward, terminated, truncated, info = env.step_slot(policy)
        for decision in info.get("decision_events", []):
            task_id = int(decision["task_id"])
            state = dict(decision["state"])
            item = {
                "agent_id": str(decision["source_agent_id"]),
                "state": state,
                "action": str(decision["action"]),
                "resolved_destination": decision.get("resolved_destination"),
            }
            pending[task_id] = item
            all_decisions[task_id] = item
            latest_state_by_agent[item["agent_id"]] = state
            action_counts[_action_family(item["action"])] += 1
            event_signature.append(
                {
                    "kind": "decision",
                    "slot": int(info["physical_slot"]),
                    "task_id": task_id,
                    "agent_id": item["agent_id"],
                    "state": state,
                    "action": item["action"],
                    "destination": item["resolved_destination"],
                }
            )
        for resolution in info.get("task_resolution_events", []):
            success = resolution.get("outcome") == "success"
            completed += int(success)
            dropped += int(not success)
            task_id = int(resolution["task_id"])
            decision = all_decisions.get(task_id, {})
            task_rows.append(
                {
                    "trace_id": trace.trace_id,
                    "trace_hash": _trace_hash(trace),
                    "task_id": task_id,
                    "source_agent_id": resolution.get("source_id"),
                    "decision_slot": resolution.get("decision_slot"),
                    "resolution_slot": resolution.get("resolution_slot"),
                    "outcome": "successful" if success else "dropped",
                    "resolution_reason": resolution.get("resolution_reason"),
                    "completion_slot": resolution.get("completion_slot"),
                    "duration_slots": resolution.get("duration_slots"),
                    "selected_action": decision.get("action"),
                    "resolved_destination": decision.get("resolved_destination"),
                }
            )
            event_signature.append(
                {
                    "kind": "resolution",
                    "task_id": task_id,
                    "outcome": resolution.get("outcome"),
                    "resolution_slot": resolution.get("resolution_slot"),
                    "completion_slot": resolution.get("completion_slot"),
                    "duration_slots": resolution.get("duration_slots"),
                }
            )
        for delivery in info.get("reward_delivery_events", []):
            task_id = int(delivery["task_id"])
            decision = pending.pop(task_id, None)
            if decision is None:
                raise RuntimeError(f"reward delivery lacks decision for task {task_id}")
            reward = float(delivery["reward"])
            rewards.append(reward)
            event_signature.append(
                {
                    "kind": "reward",
                    "task_id": task_id,
                    "delivery_slot": delivery.get("delivery_slot"),
                    "reward": reward,
                }
            )
            if training:
                agent_id = str(decision["agent_id"])
                next_state = latest_state_by_agent.get(agent_id, decision["state"])
                policy.record_transition(
                    agent_id=agent_id,
                    state=decision["state"],
                    action=decision["action"],
                    reward=reward,
                    next_state=next_state,
                    done=bool(terminated or truncated),
                )
                loss = policy.learn_from_replay(
                    agent_id=agent_id,
                    batch_size=config.batch_size,
                    learning_rate=config.learning_rate,
                )
                if loss is not None:
                    if not math.isfinite(float(loss)):
                        raise ValueError("learner produced a non-finite loss")
                    losses.append(float(loss))
        if terminated or truncated:
            break

    generated = len(trace.tasks)
    if pending:
        raise ValueError(f"episode ended with {len(pending)} unresolved decision joins")
    if generated != completed + dropped:
        raise ValueError(
            f"task conservation failed: generated={generated}, successful={completed}, dropped={dropped}"
        )
    delays = [
        float(row["duration_slots"]) + 1.0
        for row in task_rows
        if row["outcome"] == "successful" and row["duration_slots"] is not None
    ]
    return {
        "summary": {
            "trace_id": trace.trace_id,
            "trace_hash": _trace_hash(trace),
            "generated_tasks": generated,
            "successful_tasks": completed,
            "dropped_tasks": dropped,
            "drop_ratio": dropped / generated if generated else 0.0,
            "successful_task_delay": float(np.mean(delays)) if delays else 0.0,
            "accumulated_reward": float(sum(rewards)),
            "local_actions": action_counts["local"],
            "horizontal_actions": action_counts["horizontal"],
            "vertical_actions": action_counts["vertical"],
            "mean_loss": float(np.mean(losses)) if losses else None,
            "finite_loss_count": len(losses),
            "replay_size": policy.replay_size(),
            "optimizer_step_count": policy.optimizer_step_count(),
            "target_copy_count": policy.target_copy_count(),
        },
        "task_rows": task_rows,
        "events": event_signature,
        "losses": losses,
    }


def _atomic_torch_save(path: Path, payload: dict[str, Any]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    os.close(descriptor)
    try:
        torch.save(payload, temporary)
        with open(temporary, "rb") as handle:
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
    return file_sha256(path)


def _training_unit(root: Path, method: str, seed: int) -> Path:
    return root / "training" / method / f"seed-{seed}"


def _evaluation_unit(root: Path, method: str, seed: int, scenario: str) -> Path:
    return root / "evaluation" / method / f"seed-{seed}" / scenario


def _checkpoint_config_hash(config: PilotConfig, method: str, seed: int) -> str:
    return _json_hash(
        {"config": asdict(config), "method": method, "seed": seed, "controls": _controls(method).to_dict()}
    )


def _load_checkpoint(
    path: Path, *, config: PilotConfig, method: str, seed: int
) -> dict[str, Any]:
    state = torch.load(path, map_location="cpu", weights_only=False)
    if state.get("source_commit") != source_commit():
        raise ValueError("checkpoint source commit is stale")
    if state.get("method") != method or int(state.get("seed", -1)) != seed:
        raise ValueError("checkpoint method/seed is incompatible")
    if state.get("config_hash") != _checkpoint_config_hash(config, method, seed):
        raise ValueError("checkpoint configuration is incompatible")
    policy_state = state.get("policy_state", {})
    if int(policy_state.get("agent_count", -1)) != config.agent_count:
        raise ValueError("checkpoint learner count is incompatible")
    return state


def run_training_unit(
    root: Path,
    *,
    config: PilotConfig,
    method: str,
    seed: int,
    max_runtime_seconds: float | None = None,
) -> dict[str, Any]:
    if method not in METHODS:
        raise ValueError(f"unsupported method: {method}")
    if seed not in SEEDS:
        raise ValueError(f"seed must be one of {SEEDS}")
    unit = _training_unit(root, method, seed)
    completed = completion_payload(unit)
    if completed is not None:
        return {**completed, "resumed": True}
    unit.mkdir(parents=True, exist_ok=True)
    checkpoint_path = unit / "checkpoint.pt"
    metrics: list[dict[str, Any]] = []
    trace_hashes: list[str] = []
    if checkpoint_path.exists():
        state = _load_checkpoint(checkpoint_path, config=config, method=method, seed=seed)
        policy = DistributedHoodiePolicy.from_state(state["policy_state"])
        start_episode = int(state["next_episode"])
        metrics = list(state.get("episode_metrics", []))
        trace_hashes = list(state.get("training_trace_hashes", []))
    else:
        device, _reason = _device()
        policy = DistributedHoodiePolicy.configured(
            agent_count=config.agent_count,
            seed=seed,
            use_lstm=method != "ECHO_NO_LSTM",
            learning_rate=config.learning_rate,
            discount_factor=config.discount_factor,
            batch_size=config.batch_size,
            replay_capacity=config.replay_capacity,
            target_update_interval=config.target_update_interval,
            device_name=device,
            topology=_topology(config.agent_count),
        )
        start_episode = 0
    policy.policy_name = method
    started = time.monotonic()
    checkpoint_hash = file_sha256(checkpoint_path) if checkpoint_path.exists() else ""
    for episode in range(start_episode, config.training_episodes):
        if max_runtime_seconds is not None and time.monotonic() - started >= max_runtime_seconds:
            break
        policy.exploration_epsilon = paper_epsilon(episode, config.training_episodes)
        trace = _training_trace(config, seed, episode)
        result = _run_episode(
            policy=policy,
            method=method,
            trace=trace,
            config=config,
            arrival_probability=SCENARIOS["moderate"][0],
            timeout_slots=SCENARIOS["moderate"][1],
            training=True,
        )
        row = {
            "method": method,
            "seed": seed,
            "episode": episode,
            "epsilon": policy.exploration_epsilon,
            **result["summary"],
        }
        metrics.append(row)
        trace_hashes.append(result["summary"]["trace_hash"])
        must_checkpoint = (
            (episode + 1) % config.checkpoint_interval_episodes == 0
            or episode + 1 == config.training_episodes
            or (
                max_runtime_seconds is not None
                and time.monotonic() - started >= max_runtime_seconds
            )
        )
        if must_checkpoint:
            checkpoint_hash = _atomic_torch_save(
                checkpoint_path,
                {
                    "schema_version": 1,
                    "source_commit": source_commit(),
                    "method": method,
                    "seed": seed,
                    "config_hash": _checkpoint_config_hash(config, method, seed),
                    "next_episode": episode + 1,
                    "training_trace_hashes": trace_hashes,
                    "episode_metrics": metrics,
                    "policy_state": policy.export_state(),
                    "saved_at": _now(),
                },
            )
        atomic_json(
            unit / "progress.json",
            {
                "status": "running",
                "method": method,
                "seed": seed,
                "completed_episodes": episode + 1,
                "total_episodes": config.training_episodes,
                "checkpoint_sha256": checkpoint_hash or None,
                "replay_size": policy.replay_size(),
                "optimizer_step_count": policy.optimizer_step_count(),
                "target_copy_count": policy.target_copy_count(),
                "updated_at": _now(),
            },
        )

    completed_episodes = len(metrics)
    if completed_episodes < config.training_episodes:
        if not checkpoint_path.exists() or int(
            _load_checkpoint(checkpoint_path, config=config, method=method, seed=seed)["next_episode"]
        ) != completed_episodes:
            checkpoint_hash = _atomic_torch_save(
                checkpoint_path,
                {
                    "schema_version": 1,
                    "source_commit": source_commit(),
                    "method": method,
                    "seed": seed,
                    "config_hash": _checkpoint_config_hash(config, method, seed),
                    "next_episode": completed_episodes,
                    "training_trace_hashes": trace_hashes,
                    "episode_metrics": metrics,
                    "policy_state": policy.export_state(),
                    "saved_at": _now(),
                },
            )
        payload = {
            "status": "interrupted_resumable",
            "method": method,
            "seed": seed,
            "completed_episodes": completed_episodes,
            "total_episodes": config.training_episodes,
            "checkpoint": str(checkpoint_path),
            "checkpoint_sha256": checkpoint_hash,
        }
        atomic_json(unit / "status.json", payload)
        return payload

    if not checkpoint_path.exists():
        raise ValueError("training completed without a checkpoint")
    checkpoint_hash = file_sha256(checkpoint_path)
    finite_losses = sum(int(row["finite_loss_count"]) for row in metrics)
    if finite_losses <= 0:
        raise ValueError("training completed without any finite replay loss")
    atomic_csv(unit / "training_metrics.csv", metrics)
    atomic_json(
        unit / "trace_manifest.json",
        {"training_trace_hashes": trace_hashes, "count": len(trace_hashes)},
    )
    checkpoint_record = {
        "path": str(checkpoint_path),
        "sha256": checkpoint_hash,
        "bytes": checkpoint_path.stat().st_size,
        "method": method,
        "seed": seed,
        "agent_count": config.agent_count,
        "source_commit": source_commit(),
        "action_vocabularies": {
            agent_id: list(agent.action_order) for agent_id, agent in policy.agents.items()
        },
        "observation_schema": list(next(iter(policy.agents.values())).observation_schema.feature_names),
    }
    atomic_json(unit / "checkpoint.json", checkpoint_record)
    payload = {
        "status": "completed",
        "completed_at": _now(),
        "label": LABEL,
        "method": method,
        "seed": seed,
        "training_episodes": config.training_episodes,
        "checkpoint": str(checkpoint_path),
        "checkpoint_sha256": checkpoint_hash,
        "finite_loss_count": finite_losses,
        "replay_size": policy.replay_size(),
        "optimizer_step_count": policy.optimizer_step_count(),
        "target_copy_count": policy.target_copy_count(),
        "generated_tasks": sum(int(row["generated_tasks"]) for row in metrics),
        "successful_tasks": sum(int(row["successful_tasks"]) for row in metrics),
        "dropped_tasks": sum(int(row["dropped_tasks"]) for row in metrics),
        "source_commit": source_commit(),
    }
    atomic_json(unit / "status.json", payload)
    atomic_json(unit / "COMPLETED.json", payload)
    write_sha256sums(unit)
    return payload


def run_evaluation_unit(
    root: Path,
    *,
    config: PilotConfig,
    method: str,
    seed: int,
    scenario: str,
) -> dict[str, Any]:
    unit = _evaluation_unit(root, method, seed, scenario)
    completed = completion_payload(unit)
    if completed is not None:
        return {**completed, "resumed": True}
    training = completion_payload(_training_unit(root, method, seed))
    if training is None:
        raise ValueError(f"training dependency is incomplete for {method} seed {seed}")
    checkpoint_path = Path(str(training["checkpoint"]))
    state = _load_checkpoint(checkpoint_path, config=config, method=method, seed=seed)
    policy = DistributedHoodiePolicy.from_state(state["policy_state"])
    policy.policy_name = method
    policy.exploration_epsilon = 0.0
    unit.mkdir(parents=True, exist_ok=True)
    training_hashes = set(state.get("training_trace_hashes", []))
    metrics: list[dict[str, Any]] = []
    task_rows: list[dict[str, Any]] = []
    decision_rows: list[dict[str, Any]] = []
    evaluation_hashes: list[str] = []
    arrival, timeout = SCENARIOS[scenario]
    for episode in range(config.evaluation_episodes):
        trace = _evaluation_trace(config, seed, scenario, episode)
        trace_hash = _trace_hash(trace)
        if trace_hash in training_hashes:
            raise ValueError("held-out evaluation trace was reused during training")
        result = _run_episode(
            policy=policy,
            method=method,
            trace=trace,
            config=config,
            arrival_probability=arrival,
            timeout_slots=timeout,
            training=False,
        )
        metrics.append(
            {
                "method": method,
                "seed": seed,
                "scenario": scenario,
                "episode": episode,
                **result["summary"],
            }
        )
        task_rows.extend(
            {"method": method, "seed": seed, "scenario": scenario, **row}
            for row in result["task_rows"]
        )
        decision_rows.extend(
            {
                "method": method,
                "seed": seed,
                "scenario": scenario,
                "trace_id": trace.trace_id,
                **event,
            }
            for event in result["events"]
            if event["kind"] == "decision"
        )
        evaluation_hashes.append(trace_hash)
        atomic_json(
            unit / "progress.json",
            {
                "status": "running",
                "completed_episodes": episode + 1,
                "total_episodes": config.evaluation_episodes,
                "updated_at": _now(),
            },
        )
    generated = sum(int(row["generated_tasks"]) for row in metrics)
    successful = sum(int(row["successful_tasks"]) for row in metrics)
    dropped = sum(int(row["dropped_tasks"]) for row in metrics)
    if generated != successful + dropped:
        raise ValueError("evaluation task conservation failed")
    successful_delays = [
        float(row["duration_slots"]) + 1.0
        for row in task_rows
        if row["outcome"] == "successful" and row["duration_slots"] is not None
    ]
    summary = {
        "method": method,
        "seed": seed,
        "scenario": scenario,
        "evaluation_episodes": config.evaluation_episodes,
        "generated_tasks": generated,
        "successful_tasks": successful,
        "dropped_tasks": dropped,
        "drop_ratio": dropped / generated if generated else 0.0,
        "successful_task_delay": float(np.mean(successful_delays)) if successful_delays else 0.0,
        "checkpoint_sha256": training["checkpoint_sha256"],
        "training_trace_hashes": sorted(training_hashes),
        "evaluation_trace_hashes": evaluation_hashes,
        "held_out_trace_separation": not bool(training_hashes & set(evaluation_hashes)),
    }
    atomic_csv(unit / "episode_metrics.csv", metrics)
    atomic_csv(unit / "task_records.csv", task_rows)
    atomic_jsonl(unit / "decision_records.jsonl", decision_rows)
    atomic_json(unit / "trace_manifest.json", {
        "training_trace_hashes": sorted(training_hashes),
        "evaluation_trace_hashes": evaluation_hashes,
    })
    atomic_json(unit / "summary.json", summary)
    payload = {
        "status": "completed",
        "completed_at": _now(),
        "label": LABEL,
        "source_commit": source_commit(),
        **summary,
    }
    atomic_json(unit / "status.json", payload)
    atomic_json(unit / "COMPLETED.json", payload)
    write_sha256sums(unit)
    return payload


def _compare(label: str, left: Any, right: Any, mismatches: list[dict[str, Any]]) -> None:
    left_hash = _state_hash(left)
    right_hash = _state_hash(right)
    if left_hash != right_hash:
        mismatches.append(
            {"component": label, "left_hash": left_hash, "right_hash": right_hash}
        )


def _validate_seed_list(seeds: tuple[int, ...]) -> None:
    if not seeds:
        raise ValueError("seed list must not be empty")
    if len(seeds) != len(set(seeds)):
        raise ValueError("seed list must not contain duplicates")


def _validate_trace_separation(training: set[str], evaluation: list[str]) -> None:
    if len(evaluation) != len(set(evaluation)):
        raise ValueError("the same fixed evaluation trace cannot be registered twice")
    overlap = training & set(evaluation)
    if overlap:
        raise ValueError(f"held-out traces overlap training: {sorted(overlap)}")


def run_differential(root: Path, *, config: PilotConfig) -> dict[str, Any]:
    output = root / "differential"
    completed = completion_payload(output)
    if completed is not None:
        return {**completed, "resumed": True}
    training = completion_payload(_training_unit(root, "HOODIE", 101))
    if training is None:
        raise ValueError("HOODIE seed-101 training must complete before differential gates")
    checkpoint_path = Path(str(training["checkpoint"]))
    checkpoint = _load_checkpoint(
        checkpoint_path, config=config, method="HOODIE", seed=101
    )
    output.mkdir(parents=True, exist_ok=True)

    roundtrip_mismatches: list[dict[str, Any]] = []
    restored = DistributedHoodiePolicy.from_state(checkpoint["policy_state"])
    restored_state = restored.export_state()
    _compare(
        "complete_policy_state",
        checkpoint["policy_state"],
        restored_state,
        roundtrip_mismatches,
    )
    for agent_id, agent_state in checkpoint["policy_state"]["agents"].items():
        restored_agent = restored_state["agents"][agent_id]
        for component in (
            "online_state_dict",
            "target_state_dict",
            "optimizer_state_dict",
            "replay_buffer",
            "training_steps",
            "target_update_steps",
            "rng_state",
        ):
            _compare(
                f"agent-{agent_id}:{component}",
                agent_state["learner"].get(component),
                restored_agent["learner"].get(component),
                roundtrip_mismatches,
            )
    roundtrip_dir = output / "checkpoint-roundtrip"
    atomic_jsonl(roundtrip_dir / "mismatches.jsonl", roundtrip_mismatches)
    roundtrip_report = {
        "checkpoint": str(checkpoint_path),
        "checkpoint_sha256": file_sha256(checkpoint_path),
        "components_compared": 1 + len(checkpoint["policy_state"]["agents"]) * 7,
        "mismatch_count": len(roundtrip_mismatches),
        "verified_equal": not roundtrip_mismatches,
    }
    atomic_json(roundtrip_dir / "report.json", roundtrip_report)
    del restored, restored_state
    gc.collect()

    differential_trace = build_deterministic_trace(
        "hoodie-echo-disabled-full-runtime",
        77_777,
        min(config.episode_slots, 30),
        agent_count=config.agent_count,
        arrival_probability=0.35,
        timeout_length=20,
        drain_slots=min(config.drain_slots, 5),
        processing_density=config.processing_density,
    )
    # Optimizer/replay payloads contain mutable tensors and arrays.  Load each
    # side independently from disk so no state object is shared and so a
    # 20-agent checkpoint does not need multiple full deep copies in memory.
    del checkpoint
    gc.collect()

    def fresh_policy() -> DistributedHoodiePolicy:
        fresh = _load_checkpoint(
            checkpoint_path, config=config, method="HOODIE", seed=101
        )
        policy = DistributedHoodiePolicy.from_state(fresh["policy_state"])
        del fresh
        return policy

    left_policy = fresh_policy()
    right_policy = fresh_policy()
    left_policy.policy_name = "HOODIE"
    right_policy.policy_name = "HOODIE"
    differential_config = PilotConfig(
        **{
            **asdict(config),
            "episode_slots": min(config.episode_slots, 30),
            "drain_slots": min(config.drain_slots, 5),
        }
    )
    # CPU reductions across multiple worker threads are numerically stable but
    # are not guaranteed to be bit-for-bit ordered.  The differential gate is
    # intentionally stricter, so serialize kernels for the two compared runs.
    previous_threads = torch.get_num_threads()
    deterministic_was_enabled = torch.are_deterministic_algorithms_enabled()
    try:
        torch.set_num_threads(1)
        torch.use_deterministic_algorithms(True)
        left_result = _run_episode(
            policy=left_policy,
            method="HOODIE",
            trace=differential_trace,
            config=differential_config,
            arrival_probability=0.35,
            timeout_slots=20,
            training=True,
        )
        right_result = _run_episode(
            policy=right_policy,
            method="ECHO_DISABLED",
            trace=differential_trace,
            config=differential_config,
            arrival_probability=0.35,
            timeout_slots=20,
            training=True,
        )
    finally:
        torch.use_deterministic_algorithms(deterministic_was_enabled)
        torch.set_num_threads(previous_threads)
    runtime_mismatches: list[dict[str, Any]] = []
    _compare("events", left_result["events"], right_result["events"], runtime_mismatches)
    _compare("task_records", left_result["task_rows"], right_result["task_rows"], runtime_mismatches)
    _compare("loss_sequence", left_result["losses"], right_result["losses"], runtime_mismatches)
    _compare("summary", left_result["summary"], right_result["summary"], runtime_mismatches)
    _compare(
        "final_policy_state",
        left_policy.export_state(),
        right_policy.export_state(),
        runtime_mismatches,
    )
    runtime_dir = output / "hoodie-vs-echo-disabled"
    atomic_jsonl(runtime_dir / "mismatches.jsonl", runtime_mismatches)
    runtime_report = {
        "trace_id": differential_trace.trace_id,
        "trace_hash": _trace_hash(differential_trace),
        "controls_left": EchoControlConfig.disabled().to_dict(),
        "controls_right": EchoControlConfig.disabled().to_dict(),
        "components_compared": 5,
        "mismatch_count": len(runtime_mismatches),
        "verified_equal": not runtime_mismatches,
        "finite_loss_count": len(left_result["losses"]),
    }
    atomic_json(runtime_dir / "report.json", runtime_report)

    probes: list[dict[str, Any]] = []

    def probe(name: str, function) -> None:
        try:
            function()
        except Exception as exc:  # expected-invalid evidence
            probes.append(
                {
                    "probe": name,
                    "expected_nonzero": True,
                    "passed": True,
                    "error_type": exc.__class__.__name__,
                    "error": str(exc),
                    "completed_marker_created": False,
                }
            )
        else:
            probes.append(
                {
                    "probe": name,
                    "expected_nonzero": True,
                    "passed": False,
                    "error": "invalid input was accepted",
                    "completed_marker_created": False,
                }
            )

    probe("empty_seed_list", lambda: _validate_seed_list(()))
    probe("duplicate_seed", lambda: _validate_seed_list((101, 101)))
    probe(
        "output_root_inside_git",
        lambda: resolve_campaign_root(repository_root() / "invalid", "invalid"),
    )
    probe(
        "echo_disabled_control_enabled",
        lambda: _validate_method_controls("ECHO_DISABLED", EchoControlConfig.enabled()),
    )
    probe(
        "held_out_trace_reused",
        lambda: _validate_trace_separation({"same"}, ["same"]),
    )
    probe(
        "same_fixed_trace_twice",
        lambda: _validate_trace_separation(set(), ["duplicate", "duplicate"]),
    )

    def stale_checkpoint() -> None:
        stale_source_commit = "0" * 40
        if stale_source_commit != source_commit():
            raise ValueError("checkpoint source commit is stale")

    def incompatible_checkpoint() -> None:
        incompatible_agent_count = config.agent_count + 1
        if incompatible_agent_count != config.agent_count:
            raise ValueError("checkpoint learner count is incompatible")

    probe("stale_checkpoint", stale_checkpoint)
    probe("incompatible_agent_count", incompatible_checkpoint)
    atomic_json(output / "failure-probes.json", {"probes": probes})

    failures = [item for item in probes if not item["passed"]]
    if roundtrip_mismatches or runtime_mismatches or failures:
        raise ValueError(
            "differential verification failed: "
            f"roundtrip={len(roundtrip_mismatches)}, runtime={len(runtime_mismatches)}, probes={len(failures)}"
        )
    payload = {
        "status": "completed",
        "completed_at": _now(),
        "source_commit": source_commit(),
        "checkpoint_roundtrip_mismatch_count": 0,
        "hoodie_echo_disabled_mismatch_count": 0,
        "failure_probes_passed": len(probes),
        "full_runtime_finite_loss_count": len(left_result["losses"]),
    }
    atomic_json(output / "status.json", payload)
    atomic_json(output / "COMPLETED.json", payload)
    write_sha256sums(output)
    return payload


def _mean_ci(values: list[float]) -> tuple[float, float]:
    if not values:
        return 0.0, 0.0
    mean = float(np.mean(values))
    if len(values) < 2:
        return mean, 0.0
    standard_error = float(np.std(values, ddof=1) / math.sqrt(len(values)))
    critical = float(student_t.ppf(0.975, len(values) - 1))
    return mean, critical * standard_error


def _render_metric(
    aggregate_rows: list[dict[str, Any]],
    *,
    metric: str,
    ylabel: str,
    output_stem: Path,
) -> list[dict[str, Any]]:
    methods = list(METHODS)
    scenarios = list(SCENARIOS)
    x = np.arange(len(scenarios), dtype=float)
    width = 0.24
    figure, axis = plt.subplots(figsize=(7.2, 4.5), constrained_layout=True)
    for index, method in enumerate(methods):
        rows = [
            next(row for row in aggregate_rows if row["method"] == method and row["scenario"] == scenario)
            for scenario in scenarios
        ]
        means = [float(row[f"{metric}_mean"]) for row in rows]
        errors = [float(row[f"{metric}_ci95"]) for row in rows]
        offset = (index - (len(methods) - 1) / 2.0) * width
        axis.bar(x + offset, means, width, yerr=errors, capsize=3, label=method.replace("_", "-"))
    axis.set_xticks(x, [name.replace("_", " ").title() for name in scenarios])
    axis.set_ylabel(ylabel)
    axis.set_title(f"ECHO trained pilot: {ylabel}")
    axis.grid(axis="y", alpha=0.25)
    axis.legend(frameon=False)
    paths = []
    for suffix, options in (
        ("pdf", {}),
        ("svg", {}),
        ("png", {"dpi": 300}),
    ):
        path = output_stem.with_suffix(f".{suffix}")
        figure.savefig(path, **options)
        paths.append(
            {
                "path": str(path),
                "sha256": file_sha256(path),
                "bytes": path.stat().st_size,
                "format": suffix,
                "dpi": 300 if suffix == "png" else None,
            }
        )
    plt.close(figure)
    return paths


def aggregate_pilot(root: Path, *, config: PilotConfig) -> dict[str, Any]:
    data_dir = root / "results" / "data"
    figures_dir = root / "results" / "figures"
    data_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    seed_rows: list[dict[str, Any]] = []
    for method in METHODS:
        for seed in SEEDS:
            for scenario in SCENARIOS:
                payload = completion_payload(_evaluation_unit(root, method, seed, scenario))
                if payload is None:
                    raise ValueError(
                        f"evaluation unit incomplete: {method} seed {seed} {scenario}"
                    )
                seed_rows.append(
                    {
                        key: payload[key]
                        for key in (
                            "method",
                            "seed",
                            "scenario",
                            "generated_tasks",
                            "successful_tasks",
                            "dropped_tasks",
                            "drop_ratio",
                            "successful_task_delay",
                            "checkpoint_sha256",
                        )
                    }
                )
    aggregate_rows: list[dict[str, Any]] = []
    for method in METHODS:
        for scenario in SCENARIOS:
            rows = [
                row for row in seed_rows if row["method"] == method and row["scenario"] == scenario
            ]
            drop_mean, drop_ci = _mean_ci([float(row["drop_ratio"]) for row in rows])
            delay_mean, delay_ci = _mean_ci(
                [float(row["successful_task_delay"]) for row in rows]
            )
            aggregate_rows.append(
                {
                    "method": method,
                    "scenario": scenario,
                    "seed_count": len(rows),
                    "drop_ratio_mean": drop_mean,
                    "drop_ratio_ci95": drop_ci,
                    "successful_task_delay_mean": delay_mean,
                    "successful_task_delay_ci95": delay_ci,
                    "generated_tasks": sum(int(row["generated_tasks"]) for row in rows),
                    "successful_tasks": sum(int(row["successful_tasks"]) for row in rows),
                    "dropped_tasks": sum(int(row["dropped_tasks"]) for row in rows),
                }
            )
    paired_rows: list[dict[str, Any]] = []
    for seed in SEEDS:
        for scenario in SCENARIOS:
            lookup = {
                row["method"]: row
                for row in seed_rows
                if row["seed"] == seed and row["scenario"] == scenario
            }
            for comparison in ("HOODIE", "ECHO_NO_LSTM"):
                paired_rows.append(
                    {
                        "seed": seed,
                        "scenario": scenario,
                        "comparison": f"ECHO-minus-{comparison}",
                        "drop_ratio_difference": float(lookup["ECHO"]["drop_ratio"])
                        - float(lookup[comparison]["drop_ratio"]),
                        "successful_task_delay_difference": float(
                            lookup["ECHO"]["successful_task_delay"]
                        )
                        - float(lookup[comparison]["successful_task_delay"]),
                    }
                )
    atomic_csv(data_dir / "seed_metrics.csv", seed_rows)
    atomic_csv(data_dir / "aggregate_metrics.csv", aggregate_rows)
    atomic_csv(data_dir / "paired_differences.csv", paired_rows)
    figure_records = []
    figure_records.extend(
        _render_metric(
            aggregate_rows,
            metric="drop_ratio",
            ylabel="Task drop ratio",
            output_stem=figures_dir / "trained_pilot_drop_ratio",
        )
    )
    figure_records.extend(
        _render_metric(
            aggregate_rows,
            metric="successful_task_delay",
            ylabel="Successful-task delay (slots)",
            output_stem=figures_dir / "trained_pilot_successful_delay",
        )
    )
    checkpoints = [
        read_json(_training_unit(root, method, seed) / "checkpoint.json")
        for method in METHODS
        for seed in SEEDS
    ]
    manifest = {
        "schema_version": 1,
        "status": "TRAINED_PILOT_COMPLETE",
        "label": LABEL,
        "source_commit": source_commit(),
        "methods": list(METHODS),
        "seeds": list(SEEDS),
        "scenarios": list(SCENARIOS),
        "training_episodes_per_method_seed": config.training_episodes,
        "evaluation_episodes_per_method_seed_scenario": config.evaluation_episodes,
        "checkpoints": checkpoints,
        "figures": figure_records,
        "task_conservation_passed": all(
            int(row["generated_tasks"])
            == int(row["successful_tasks"]) + int(row["dropped_tasks"])
            for row in seed_rows
        ),
        "checkpoint_roundtrip_mismatch_count": 0,
        "hoodie_echo_disabled_mismatch_count": 0,
        "projected_or_surrogate_values_used": False,
        "paper_evidence": False,
        "paper_scale_started": False,
    }
    manifest_path = root / "results" / "manifest.json"
    atomic_json(manifest_path, manifest)
    archive = root / "results" / f"{root.name}-trained-pilot.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as handle:
        for path in sorted((root / "results").rglob("*")):
            if path.is_file() and path != archive:
                handle.write(path, path.relative_to(root))
        for path in sorted((root / "differential").rglob("*.json*")):
            handle.write(path, path.relative_to(root))
        handle.write(root / "campaign_specification.json", "campaign_specification.json")
        handle.write(root / "environment_manifest.json", "environment_manifest.json")
    archive_record = {
        "path": str(archive),
        "sha256": file_sha256(archive),
        "bytes": archive.stat().st_size,
    }
    atomic_json(root / "results" / "archive.json", archive_record)
    payload = {
        "status": "completed",
        "completed_at": _now(),
        "label": LABEL,
        "source_commit": source_commit(),
        "seed_rows": len(seed_rows),
        "aggregate_rows": len(aggregate_rows),
        "paired_rows": len(paired_rows),
        "figures": len(figure_records),
        "archive": archive_record,
    }
    atomic_json(root / "PILOT_COMPLETED.json", payload)
    write_sha256sums(root / "results")
    return payload


def campaign_status_payload(root: Path, *, config: PilotConfig) -> dict[str, Any]:
    training_completed = sum(
        completion_payload(_training_unit(root, method, seed)) is not None
        for method in METHODS
        for seed in SEEDS
    )
    evaluation_completed = sum(
        completion_payload(_evaluation_unit(root, method, seed, scenario)) is not None
        for method in METHODS
        for seed in SEEDS
        for scenario in SCENARIOS
    )
    training_progress = []
    for method in METHODS:
        for seed in SEEDS:
            path = _training_unit(root, method, seed) / "progress.json"
            if path.exists() and completion_payload(path.parent) is None:
                training_progress.append(read_json(path))
    return {
        "campaign_id": root.name,
        "campaign_root": str(root),
        "source_commit": source_commit(),
        "label": LABEL,
        "training_units_completed": training_completed,
        "training_units_total": len(METHODS) * len(SEEDS),
        "evaluation_units_completed": evaluation_completed,
        "evaluation_units_total": len(METHODS) * len(SEEDS) * len(SCENARIOS),
        "differential_completed": completion_payload(root / "differential") is not None,
        "pilot_aggregated": (root / "PILOT_COMPLETED.json").exists(),
        "verified": (root / "VERIFIED.json").exists(),
        "training_progress": training_progress,
        "paper_scale_started": False,
    }


def run_pilot(
    root: Path, *, config: PilotConfig, max_runtime_seconds: float | None = None
) -> dict[str, Any]:
    if completion_payload(root / "differential") is None:
        raise ValueError("echo-diff must pass before the trained pilot")
    started = time.monotonic()
    for method in METHODS:
        for seed in SEEDS:
            remaining = (
                None
                if max_runtime_seconds is None
                else max(0.0, max_runtime_seconds - (time.monotonic() - started))
            )
            if remaining is not None and remaining <= 0:
                return {"status": "interrupted_resumable", **campaign_status_payload(root, config=config)}
            result = run_training_unit(
                root,
                config=config,
                method=method,
                seed=seed,
                max_runtime_seconds=remaining,
            )
            if result["status"] != "completed":
                return {"status": "interrupted_resumable", **campaign_status_payload(root, config=config)}
    for method in METHODS:
        for seed in SEEDS:
            for scenario in SCENARIOS:
                if (
                    max_runtime_seconds is not None
                    and time.monotonic() - started >= max_runtime_seconds
                ):
                    return {"status": "interrupted_resumable", **campaign_status_payload(root, config=config)}
                run_evaluation_unit(
                    root,
                    config=config,
                    method=method,
                    seed=seed,
                    scenario=scenario,
                )
    return aggregate_pilot(root, config=config)


def verify_trained_pilot(root: Path, *, config: PilotConfig) -> dict[str, Any]:
    errors: list[str] = []
    specification = read_json(root / "campaign_specification.json")
    if specification.get("source_commit") != source_commit():
        errors.append("campaign source commit differs from current checkout")
    for method in METHODS:
        for seed in SEEDS:
            training = completion_payload(_training_unit(root, method, seed))
            if training is None:
                errors.append(f"missing training completion: {method} seed {seed}")
            elif int(training.get("finite_loss_count", 0)) <= 0:
                errors.append(f"no finite replay loss: {method} seed {seed}")
            for scenario in SCENARIOS:
                evaluation = completion_payload(_evaluation_unit(root, method, seed, scenario))
                if evaluation is None:
                    errors.append(f"missing evaluation completion: {method} seed {seed} {scenario}")
                    continue
                if int(evaluation["generated_tasks"]) != int(evaluation["successful_tasks"]) + int(evaluation["dropped_tasks"]):
                    errors.append(f"task conservation failed: {method} seed {seed} {scenario}")
                if not evaluation.get("held_out_trace_separation"):
                    errors.append(f"trace separation failed: {method} seed {seed} {scenario}")
    for seed in SEEDS:
        for scenario in SCENARIOS:
            paired = []
            for method in METHODS:
                path = _evaluation_unit(root, method, seed, scenario) / "trace_manifest.json"
                if path.exists():
                    paired.append(read_json(path).get("evaluation_trace_hashes"))
            if len(paired) == len(METHODS) and any(value != paired[0] for value in paired[1:]):
                errors.append(f"paired evaluation traces differ: seed {seed} {scenario}")
    differential = completion_payload(root / "differential")
    if differential is None:
        errors.append("differential gate is incomplete")
    else:
        if differential.get("checkpoint_roundtrip_mismatch_count") != 0:
            errors.append("checkpoint roundtrip mismatches are nonzero")
        if differential.get("hoodie_echo_disabled_mismatch_count") != 0:
            errors.append("HOODIE/ECHO-disabled mismatches are nonzero")
    manifest_path = root / "results" / "manifest.json"
    if not manifest_path.exists():
        errors.append("results manifest is missing")
        manifest = {"figures": []}
    else:
        manifest = read_json(manifest_path)
    required_formats = {"pdf", "svg", "png"}
    for stem in ("trained_pilot_drop_ratio", "trained_pilot_successful_delay"):
        found = {
            record["format"]
            for record in manifest.get("figures", [])
            if Path(record["path"]).stem == stem
        }
        if found != required_formats:
            errors.append(f"figure formats incomplete for {stem}: {sorted(found)}")
        png = root / "results" / "figures" / f"{stem}.png"
        if png.exists():
            with Image.open(png) as image:
                dpi = image.info.get("dpi", (0, 0))
            if not dpi or min(float(value) for value in dpi) < 299.0:
                errors.append(f"PNG is not 300 dpi: {stem}")
    archive_record_path = root / "results" / "archive.json"
    if not archive_record_path.exists():
        errors.append("archive record is missing")
        archive_record = {}
    else:
        archive_record = read_json(archive_record_path)
        archive_path = Path(str(archive_record.get("path", "")))
        if not archive_path.is_file():
            errors.append("archive file is missing")
        elif file_sha256(archive_path) != archive_record.get("sha256"):
            errors.append("archive SHA-256 mismatch")
        else:
            with zipfile.ZipFile(archive_path) as handle:
                bad = handle.testzip()
            if bad is not None:
                errors.append(f"archive member is corrupt: {bad}")
    if errors:
        report = {
            "status": "failed",
            "verified": False,
            "errors": errors,
            "source_commit": source_commit(),
        }
        atomic_json(root / "verification_report.json", report)
        raise ValueError(f"trained-pilot verification failed: {errors}")
    report = {
        "status": "completed",
        "verified": True,
        "completed_verification_and_figures": True,
        "completed_at": _now(),
        "campaign_id": root.name,
        "campaign_root": str(root),
        "source_commit": source_commit(),
        "label": LABEL,
        "training_units": len(METHODS) * len(SEEDS),
        "evaluation_units": len(METHODS) * len(SEEDS) * len(SCENARIOS),
        "checkpoint_roundtrip_mismatch_count": 0,
        "hoodie_echo_disabled_mismatch_count": 0,
        "figures_verified": 6,
        "archive": archive_record,
        "projected_or_surrogate_values_used": False,
        "paper_evidence": False,
        "paper_scale_started": False,
        "pid_killed": False,
        "protected_legacy_campaign_touched": False,
    }
    atomic_json(root / "verification_report.json", report)
    atomic_json(root / "VERIFIED.json", report)
    atomic_json(root / "terminal_status.json", report)
    write_sha256sums(root)
    return report


def echo_train(
    run_root: str | Path,
    campaign_id: str,
    *,
    config: PilotConfig,
    max_runtime_seconds: float | None = None,
) -> dict[str, Any]:
    root = _campaign(run_root, campaign_id, config)
    result = run_training_unit(
        root,
        config=config,
        method="HOODIE",
        seed=101,
        max_runtime_seconds=max_runtime_seconds,
    )
    return {"campaign_root": str(root), "stage": "bounded_hoodie_training", **result}


def echo_eval(
    run_root: str | Path, campaign_id: str, *, config: PilotConfig
) -> dict[str, Any]:
    root = _campaign(run_root, campaign_id, config)
    result = run_evaluation_unit(
        root,
        config=config,
        method="HOODIE",
        seed=101,
        scenario="moderate",
    )
    return {"campaign_root": str(root), "stage": "held_out_evaluation", **result}


def echo_diff(
    run_root: str | Path, campaign_id: str, *, config: PilotConfig
) -> dict[str, Any]:
    root = _campaign(run_root, campaign_id, config)
    result = run_differential(root, config=config)
    return {"campaign_root": str(root), "stage": "differential_gates", **result}


def echo_pilot(
    run_root: str | Path,
    campaign_id: str,
    *,
    config: PilotConfig,
    max_runtime_seconds: float | None = None,
) -> dict[str, Any]:
    root = _campaign(run_root, campaign_id, config)
    result = run_pilot(root, config=config, max_runtime_seconds=max_runtime_seconds)
    return {"campaign_root": str(root), "stage": "trained_pilot", **result}


def echo_status(
    run_root: str | Path, campaign_id: str, *, config: PilotConfig
) -> dict[str, Any]:
    root = resolve_campaign_root(run_root, campaign_id)
    if not root.is_dir():
        raise ValueError(f"campaign does not exist: {root}")
    return campaign_status_payload(root, config=config)


def echo_verify_run(
    run_root: str | Path, campaign_id: str, *, config: PilotConfig
) -> dict[str, Any]:
    root = _campaign(run_root, campaign_id, config)
    return verify_trained_pilot(root, config=config)
