from __future__ import annotations

from dataclasses import asdict, fields, replace
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import platform
import shutil
import signal
import time
import traceback
from typing import Any

import torch

from src.agents.distributed_hoodie import DistributedHoodiePolicy
from src.environment.evaluation_gym_adapter import EvaluationHoodieGymEnvironment
from src.environment.topology import TopologyGraph
from src.evaluation.policy_registry import PolicyRegistry
from src.evaluation.runner import EvaluationRunner
from src.evaluation.trace_protocol import build_deterministic_trace

from . import job_matrix as matrix
from . import production_campaign as legacy
from .contract_mapping import (
    build_environment_config,
    build_evaluation_config,
    build_link_rate_config,
    build_training_config,
    validate_contract_mapping,
)
from .matrix_patch import install_matrix_patch
from .provenance import build_provenance_manifest, provenance_hash
from .schemas import DecisionRecord, TaskRecord, TrainingHistoryRecord, TransitionRecord

_INSTALLED = False


def paper_epsilon(episode_index: int, episode_count: int) -> float:
    if episode_count <= 0:
        raise ValueError("episode_count must be positive")
    if episode_index < 0:
        raise ValueError("episode_index must be non-negative")
    if episode_index >= episode_count / 2.0:
        return 0.0
    return max(0.0, 1.0 - (2.0 * float(episode_index) / float(episode_count)))


def _agent_count(row: matrix.ProductionJobRow) -> int:
    values = row.topology_contract.get("agent_counts", [20])
    if isinstance(values, (list, tuple)):
        if len(values) != 1:
            raise ValueError("one job must resolve to one agent count")
        return int(values[0])
    return int(values)


def _task_sizes(row: matrix.ProductionJobRow) -> tuple[float, ...] | None:
    values = row.workload_contract.get("task_size_mbits")
    if values is None:
        scenario = row.workload_contract.get("traffic_scenario")
        if isinstance(scenario, dict):
            values = scenario.get("task_size_mbits")
    if values is None:
        return None
    if not isinstance(values, (list, tuple)):
        raise ValueError("task_size_mbits must be a list or tuple")
    return tuple(float(value) for value in values)


def _processing_density(row: matrix.ProductionJobRow) -> float:
    return float(row.workload_contract.get("processing_density_gcycles_per_mbit", 0.297))


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


def _load_rows(path: Path, campaign_id: str) -> list[matrix.ProductionJobRow]:
    allowed = {field.name for field in fields(matrix.ProductionJobRow)}
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = [
        matrix.ProductionJobRow(**{key: value for key, value in row.items() if key in allowed})
        for row in payload
    ]
    return [replace(row, campaign_id=campaign_id) for row in rows]


def _default_rows(campaign_id: str) -> list[matrix.ProductionJobRow]:
    install_matrix_patch()
    rows = matrix.build_production_job_matrix(campaign_id)
    matrix.validate_production_job_matrix(rows)
    return rows


def _build_trace(row: matrix.ProductionJobRow, *, episode_index: int = 0):
    source_contract = legacy._panel_contract(row.panel_id)
    runtime = build_environment_config(row, source_contract)
    panel = legacy._panel_contract(row.panel_id)
    slots = int(
        (row.training_contract if row.job_type == "training" else row.evaluation_contract).get(
            "slots_per_episode", panel.get("slots_per_episode", 110)
        )
    )
    drain = int(
        (row.training_contract if row.job_type == "training" else row.evaluation_contract).get(
            "drain_slots", panel.get("drain_slots", 10)
        )
    )
    trace = build_deterministic_trace(
        trace_id=f"{row.trace_bank_id}-{episode_index}",
        seed=int(row.seed or 0) + episode_index,
        episode_length=slots,
        agent_count=runtime.agent_count,
        arrival_probability=runtime.arrival_probability,
        timeout_length=runtime.timeout_slots,
        drain_slots=drain,
        task_sizes=_task_sizes(row),
        processing_density=_processing_density(row),
    )
    records = [
        legacy.TraceRecord(
            task_identity=legacy.TaskIdentity(
                str(task.task_id), str(task.source_agent_id), f"ea-{task.source_agent_id}"
            ),
            workload=legacy.TaskWorkload(
                int(round(task.size)), int(task.timeout_length), int(task.arrival_slot)
            ),
            decision_seed=int(row.seed or 0) + episode_index,
        )
        for task in trace.tasks
    ]
    registry = legacy.TraceRegistry.from_records(
        trace.trace_id, records, source_hash=row.source_contract_hash
    )
    return registry, {
        "trace": trace,
        "records": records,
        "trace_hash": registry.hash(),
        "spec": {
            "agent_count": runtime.agent_count,
            "arrival_probability": runtime.arrival_probability,
            "timeout_slots": runtime.timeout_slots,
            "episode_length": slots,
            "drain_slots": drain,
            "task_sizes": _task_sizes(row),
            "processing_density": _processing_density(row),
        },
    }


def _policy_from_checkpoint(
    row: matrix.ProductionJobRow, checkpoint_state: dict[str, Any] | None
):
    if row.policy != "HOODIE":
        return PolicyRegistry.resolve(row.policy)
    if checkpoint_state is None:
        raise ValueError(f"HOODIE evaluation job {row.job_id} requires a checkpoint")
    policy = DistributedHoodiePolicy.from_state(checkpoint_state)
    expected = _agent_count(row)
    if len(policy.agents) != expected:
        raise ValueError(
            f"checkpoint learner count {len(policy.agents)} does not match evaluation topology {expected}"
        )
    policy.use_lstm = row.variant != "hoodie_no_lstm"
    policy.exploration_epsilon = 0.0
    return policy


def _checkpoint_record(
    job_dir: Path,
    row: matrix.ProductionJobRow,
    *,
    source_commit: str,
    checkpoint_id: str,
) -> dict[str, Any]:
    checkpoint_path = job_dir / "internal_checkpoints" / checkpoint_id / "checkpoint.pt"
    checkpoint_state = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    file_hash = sha256(checkpoint_path.read_bytes()).hexdigest()
    campaign_dir = job_dir.parent.parent
    registry = legacy._load_campaign_checkpoint_registry(campaign_dir)
    record = {
        "training_job_id": row.job_id,
        "checkpoint_id": checkpoint_id,
        "checkpoint_path": str(checkpoint_path),
        "checkpoint_hash": file_hash,
        "policy": row.policy,
        "variant": row.variant,
        "seed": int(row.seed or 0),
        "agent_count": _agent_count(row),
        "backend_type": str(checkpoint_state.get("backend_type", "legacy_unknown")),
        "device_string": str(checkpoint_state.get("device_string", "unknown")),
        "source_commit": source_commit,
        "source_contract_hash": row.source_contract_hash,
        "job_spec_hash": legacy._hash(asdict(row)),
        "scientifically_complete": True,
    }
    registry = [item for item in registry if item.get("training_job_id") != row.job_id]
    registry.append(record)
    legacy._write_campaign_checkpoint_registry(campaign_dir, registry)
    legacy._write_json(job_dir / "selected_checkpoint.json", record)
    return record


def _resolve_checkpoint(campaign_dir: Path, row: matrix.ProductionJobRow) -> dict[str, Any] | None:
    if not row.checkpoint_dependency:
        return None
    record = legacy._resolve_training_checkpoint(campaign_dir, row)
    if record is None:
        return None
    if int(record.get("agent_count", _agent_count(row))) != _agent_count(row):
        raise ValueError("checkpoint topology/learner count mismatch")
    checkpoint_path = Path(str(record["checkpoint_path"]))
    actual_hash = sha256(checkpoint_path.read_bytes()).hexdigest()
    expected_hash = str(record.get("checkpoint_hash", ""))
    if expected_hash and actual_hash != expected_hash:
        raise ValueError("checkpoint file hash mismatch")
    state = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    return {**state, "checkpoint_record": record}


def _prune_checkpoints(job_dir: Path, keep: int = 2) -> None:
    checkpoint_root = job_dir / "internal_checkpoints"
    if not checkpoint_root.exists():
        return
    directories = sorted(
        (path for path in checkpoint_root.iterdir() if path.is_dir()),
        key=lambda path: path.stat().st_mtime,
    )
    for path in directories[:-keep]:
        shutil.rmtree(path)


def _checkpoint_policy(
    *,
    policy: DistributedHoodiePolicy,
    row: matrix.ProductionJobRow,
    job_dir: Path,
    source_commit: str,
    next_episode: int,
    episode_rewards: list[float],
    selection_value: float,
) -> str:
    policy_state = policy.export_state()
    checkpoint_id = legacy._hash(
        {
            "job_id": row.job_id,
            "source": source_commit,
            "next_episode": next_episode,
            "policy_hash": _state_hash(policy_state),
        }
    )[:24]
    checkpoint_state = {
        "schema_version": 2,
        "checkpoint_id": checkpoint_id,
        "next_episode": next_episode,
        "episode_rewards": list(episode_rewards),
        "policy_state": policy_state,
        "backend_type": policy_state["backend_type"],
        "device_string": policy_state["device_string"],
    }
    agents_state = policy_state["agents"]
    online = {key: value["learner"]["online_state_dict"] for key, value in agents_state.items()}
    target = {key: value["learner"]["target_state_dict"] for key, value in agents_state.items()}
    optimizer = {key: value["learner"]["optimizer_state_dict"] for key, value in agents_state.items()}
    replay = {key: value["learner"]["replay_buffer"] for key, value in agents_state.items()}
    legacy._write_internal_checkpoint(
        job_dir,
        checkpoint_state=checkpoint_state,
        metadata={
            "checkpoint_id": checkpoint_id,
            "training_job_id": row.job_id,
            "policy": row.policy,
            "variant": row.variant,
            "training_seed": int(row.seed or 0),
            "selected_episode": max(0, next_episode - 1),
            "selection_rule": "latest_completed_episode",
            "selection_metric": "accumulated_reward",
            "selection_value": float(selection_value),
            "online_network_hash": _state_hash(online),
            "target_network_hash": _state_hash(target),
            "optimizer_state_hash": _state_hash(optimizer),
            "replay_state_hash": _state_hash(replay),
            "RNG_state_hash": _state_hash(
                {key: value["learner"].get("rng_state") for key, value in agents_state.items()}
            ),
            "LSTM_state_hash": None
            if row.variant == "hoodie_no_lstm"
            else _state_hash({key: value.get("causal_history", []) for key, value in agents_state.items()}),
            "configuration_hash": row.config_hash,
            "topology_hash": legacy._hash(row.topology_contract),
            "workload_hash": legacy._hash(row.workload_contract),
            "source_contract_hash": row.source_contract_hash,
            "source_commit": source_commit,
        },
    )
    _prune_checkpoints(job_dir)
    return checkpoint_id


def _load_csv(path: Path) -> list[dict[str, Any]]:
    return legacy._load_csv_rows(path)


def _run_training_job(
    row: matrix.ProductionJobRow,
    job_dir: Path,
    *,
    source_commit: str,
    max_runtime_seconds: float | None = None,
) -> legacy.JobExecutionResult:
    source_contract = legacy._panel_contract(row.panel_id)
    mismatches = validate_contract_mapping(row, source_contract)
    if mismatches:
        raise ValueError(f"training contract mismatches: {mismatches}")
    initial_registry, initial_bundle = _build_trace(row)
    config = build_training_config(
        row, source_contract, trace_hash=initial_bundle["trace_hash"], output_dir=job_dir
    )
    runtime = build_environment_config(row, source_contract)
    topology = TopologyGraph.for_agent_count(runtime.agent_count)
    link_rate = build_link_rate_config(row, source_contract)
    attempt = (
        int(json.loads((job_dir / "status.json").read_text(encoding="utf-8")).get("attempt", 1))
        if (job_dir / "status.json").exists()
        else 1
    )

    history_rows = _load_csv(job_dir / "training_history.csv")
    metric_rows = _load_csv(job_dir / "training_metrics.csv")
    resume_state = legacy._load_internal_checkpoint_state(job_dir)
    if resume_state is not None:
        policy = DistributedHoodiePolicy.from_state(resume_state)
        if len(policy.agents) != runtime.agent_count:
            raise ValueError("resume checkpoint agent count mismatch")
        episode_start = int(resume_state.get("next_episode", 0))
        episode_rewards = [float(value) for value in resume_state.get("episode_rewards", [])]
        history_rows = [row_ for row_ in history_rows if int(row_["episode_or_step"]) < episode_start]
        metric_rows = [row_ for row_ in metric_rows if int(row_["episode"]) < episode_start]
    else:
        policy = DistributedHoodiePolicy.configured(
            agent_count=runtime.agent_count,
            seed=int(row.seed or 0),
            use_lstm=row.variant != "hoodie_no_lstm",
            learning_rate=config.learning_rate,
            discount_factor=config.discount_factor,
            batch_size=config.batch_size,
            replay_capacity=config.replay_buffer_capacity,
            target_update_interval=config.target_network_update_frequency,
            device_name=config.device,
        )
        episode_start = 0
        episode_rewards = []

    interrupted = False

    def handle_signal(_signum, _frame):
        nonlocal interrupted
        interrupted = True

    previous_int = signal.signal(signal.SIGINT, handle_signal)
    previous_term = signal.signal(signal.SIGTERM, handle_signal)
    start_time = time.time()
    last_checkpoint_id = str(resume_state.get("checkpoint_id", "")) if resume_state else ""
    checkpoint_interval = max(1, min(100, config.episode_count // 100 or 1))
    latest_trace_hash = initial_registry.hash()
    try:
        for episode_index in range(episode_start, config.episode_count):
            if interrupted or (
                max_runtime_seconds is not None
                and time.time() - start_time >= max_runtime_seconds
            ):
                interrupted = True
                break
            policy.exploration_epsilon = paper_epsilon(episode_index, config.episode_count)
            registry, bundle = _build_trace(row, episode_index=episode_index)
            latest_trace_hash = registry.hash()
            trace = bundle["trace"]
            env = EvaluationHoodieGymEnvironment(
                episode_length=config.episode_length,
                topology=topology,
                runtime_parameters=runtime,
                compute_config=runtime.to_compute_config(),
                link_rate_config=link_rate,
                policy_name="HOODIE",
                supplied_trace=trace,
            )
            env.reset(seed=trace.seed)
            decisions: dict[int, dict[str, Any]] = {}
            latest_state_by_agent: dict[str, dict[str, object]] = {}
            episode_reward = 0.0
            losses: list[float] = []
            completed = 0
            dropped = 0
            delays: list[float] = []
            action_counts = {"local": 0, "horizontal": 0, "vertical": 0}
            slot_index = 0
            while True:
                if interrupted or (
                    max_runtime_seconds is not None
                    and time.time() - start_time >= max_runtime_seconds
                ):
                    interrupted = True
                    break
                observation, reward, terminated, truncated, info = env.step_slot(policy)
                if isinstance(reward, (int, float)) and math.isfinite(float(reward)):
                    episode_reward += float(reward)
                slot_index = int(getattr(env, "current_slot", slot_index + 1))
                for decision in info.get("decision_events", []):
                    task_id = int(decision["task_id"])
                    agent_id = str(decision["source_agent_id"])
                    state = dict(decision.get("state", {}))
                    action = str(decision.get("action", "local"))
                    decisions[task_id] = {
                        "agent_id": agent_id,
                        "state": state,
                        "action": action,
                    }
                    latest_state_by_agent[agent_id] = state
                    family = "horizontal" if action.startswith("horizontal") else (
                        "vertical" if action in {"vertical", "cloud", "offload_vertical"} else "local"
                    )
                    action_counts[family] += 1
                for resolution in info.get("task_resolution_events", []):
                    if resolution.get("outcome") == "success":
                        completed += 1
                        delays.append(float(resolution.get("duration_slots", 0)) + 1.0)
                    else:
                        dropped += 1
                for delivery in info.get("reward_delivery_events", []):
                    task_id = int(delivery["task_id"])
                    decision = decisions.pop(task_id, None)
                    if decision is None:
                        continue
                    agent_id = str(decision["agent_id"])
                    next_state = latest_state_by_agent.get(agent_id, decision["state"])
                    policy.record_transition(
                        agent_id=agent_id,
                        state=decision["state"],
                        action=decision["action"],
                        reward=float(delivery["reward"]),
                        next_state=next_state,
                        done=bool(terminated or truncated),
                    )
                    loss = policy.learn_from_replay(
                        agent_id=agent_id,
                        batch_size=config.batch_size,
                        learning_rate=config.learning_rate,
                    )
                    if loss is not None and math.isfinite(loss):
                        losses.append(float(loss))
                legacy._write_progress(
                    job_dir,
                    {
                        "campaign_id": row.campaign_id,
                        "job_id": row.job_id,
                        "attempt": attempt,
                        "phase": "training",
                        "current_episode": episode_index,
                        "total_episodes": config.episode_count,
                        "current_slot": slot_index,
                        "total_slots_per_episode": config.episode_length,
                        "completed_environment_steps": episode_index * config.episode_length + slot_index,
                        "generated_tasks": completed + dropped + len(decisions),
                        "completed_tasks": completed,
                        "dropped_tasks": dropped,
                        "replay_size": policy.replay_size(),
                        "optimizer_step_count": policy.optimizer_step_count(),
                        "target_copy_count": policy.target_copy_count(),
                        "epsilon": policy.exploration_epsilon,
                        "most_recent_finite_loss": losses[-1] if losses else None,
                        "accumulated_reward": episode_reward,
                        "latest_internal_checkpoint": last_checkpoint_id,
                        "heartbeat_timestamp": time.time(),
                        "elapsed_seconds": time.time() - start_time,
                        "worker_pid": os.getpid(),
                        "supervisor_pid": os.getppid(),
                        "backend_device": policy.device_string(),
                    },
                )
                if terminated or truncated:
                    break
            if interrupted:
                last_checkpoint_id = _checkpoint_policy(
                    policy=policy,
                    row=row,
                    job_dir=job_dir,
                    source_commit=source_commit,
                    next_episode=episode_index,
                    episode_rewards=episode_rewards,
                    selection_value=episode_rewards[-1] if episode_rewards else 0.0,
                )
                break

            episode_rewards.append(episode_reward)
            mean_loss = sum(losses) / len(losses) if losses else 0.0
            history_rows.append(
                asdict(
                    TrainingHistoryRecord(
                        episode_or_step=episode_index,
                        loss=mean_loss,
                        epsilon=policy.exploration_epsilon,
                        replay_size=policy.replay_size(),
                        target_update_count=policy.target_copy_count(),
                        checkpoint_id=last_checkpoint_id,
                    )
                )
            )
            offered = completed + dropped
            metric_rows.append(
                {
                    "episode": episode_index,
                    "accumulated_reward": episode_reward,
                    "average_delay": sum(delays) / len(delays) if delays else 0.0,
                    "drop_ratio": dropped / offered if offered else 0.0,
                    "throughput": completed,
                    "completed_tasks": completed,
                    "dropped_tasks": dropped,
                    "offered_tasks": offered,
                    "local_actions": action_counts["local"],
                    "horizontal_actions": action_counts["horizontal"],
                    "vertical_actions": action_counts["vertical"],
                    "mean_loss": mean_loss,
                    "epsilon": policy.exploration_epsilon,
                }
            )
            should_checkpoint = (
                (episode_index + 1) % checkpoint_interval == 0
                or episode_index + 1 == config.episode_count
            )
            if should_checkpoint:
                last_checkpoint_id = _checkpoint_policy(
                    policy=policy,
                    row=row,
                    job_dir=job_dir,
                    source_commit=source_commit,
                    next_episode=episode_index + 1,
                    episode_rewards=episode_rewards,
                    selection_value=episode_reward,
                )
                history_rows[-1]["checkpoint_id"] = last_checkpoint_id
            legacy._write_csv(job_dir / "training_history.csv", history_rows)
            legacy._write_csv(job_dir / "training_metrics.csv", metric_rows)
            if os.environ.get("HOODIE_TEST_BOUNDARY") == "1":
                interrupted = True
                break

        training_hash = legacy._write_csv(job_dir / "training_history.csv", history_rows)
        metrics_hash = legacy._write_csv(job_dir / "training_metrics.csv", metric_rows)
        empty_hash = legacy._write_csv(job_dir / "task_records.csv", [])
        legacy._write_csv(job_dir / "decision_records.csv", [])
        legacy._write_csv(job_dir / "transition_records.csv", [])
        legacy._ensure_schema(job_dir / "training_history.schema.json", history_rows)
        legacy._ensure_schema(job_dir / "training_metrics.schema.json", metric_rows)
        if interrupted:
            legacy._write_json(
                job_dir / "status.json",
                legacy._job_status_payload(
                    campaign_id=row.campaign_id,
                    row=row,
                    status="interrupted_resumable",
                    source_commit=source_commit,
                    attempt=attempt,
                    trace_hash=latest_trace_hash,
                    dataset_hashes={"training_history": training_hash, "training_metrics": metrics_hash},
                ),
            )
            return legacy.JobExecutionResult(
                row.job_id,
                row.job_type,
                "interrupted_resumable",
                job_dir,
                last_checkpoint_id,
                latest_trace_hash,
                (training_hash, metrics_hash),
                {"episode_rewards": episode_rewards},
            )

        if len(history_rows) != config.episode_count:
            raise ValueError("training ended without the required episode count")
        checkpoint_selection = {
            "checkpoint_id": last_checkpoint_id,
            "selection_rule": "final_episode",
            "selection_metric": "accumulated_reward",
            "selection_value": float(episode_rewards[-1]),
        }
        provenance = build_provenance_manifest(
            source_commit=source_commit,
            source_contract_hash=row.source_contract_hash,
            panel_contract_hash=legacy._hash(source_contract),
            job_spec_hash=legacy._hash(asdict(row)),
            topology_hash=topology.topology_hash(),
            physical_hash=legacy._hash(row.physical_contract),
            workload_hash=legacy._hash(row.workload_contract),
            training_hash=training_hash,
            evaluation_hash="",
            trace_hash=latest_trace_hash,
            checkpoint_hash=last_checkpoint_id,
            dataset_hashes=(training_hash, metrics_hash, empty_hash),
        )
        legacy._write_json(
            job_dir / "provenance.json",
            {"manifest": asdict(provenance), "hash": provenance_hash(provenance)},
        )
        legacy._write_json(job_dir / "checkpoint_selection.json", checkpoint_selection)
        legacy.validate_training_outputs_before_completion(job_dir, row)
        legacy._write_json(
            job_dir / "status.json",
            {
                **legacy._job_status_payload(
                    campaign_id=row.campaign_id,
                    row=row,
                    status="completed",
                    source_commit=source_commit,
                    checkpoint_hash=last_checkpoint_id,
                    trace_hash=latest_trace_hash,
                    dataset_hashes={"training_history": training_hash, "training_metrics": metrics_hash},
                    completed_at=time.time(),
                ),
                "completion_marker": True,
            },
        )
        _checkpoint_record(
            job_dir, row, source_commit=source_commit, checkpoint_id=last_checkpoint_id
        )
        legacy._write_completion_marker(job_dir)
        legacy.validate_completed_training_job(job_dir, row)
        return legacy.JobExecutionResult(
            row.job_id,
            row.job_type,
            "completed",
            job_dir,
            last_checkpoint_id,
            latest_trace_hash,
            (training_hash, metrics_hash),
            {"episode_rewards": episode_rewards},
        )
    finally:
        signal.signal(signal.SIGINT, previous_int)
        signal.signal(signal.SIGTERM, previous_term)


def _run_evaluation_job(
    row: matrix.ProductionJobRow,
    job_dir: Path,
    *,
    source_commit: str,
    checkpoint_state: dict[str, Any] | None = None,
) -> legacy.JobExecutionResult:
    source_contract = legacy._panel_contract(row.panel_id)
    mismatches = validate_contract_mapping(row, source_contract)
    if mismatches:
        raise ValueError(f"evaluation contract mismatches: {mismatches}")
    runtime = build_environment_config(row, source_contract)
    topology = TopologyGraph.for_agent_count(runtime.agent_count)
    link_rate = build_link_rate_config(row, source_contract)
    config = build_evaluation_config(
        row, source_contract, trace_id=row.trace_bank_id, output_dir=job_dir
    )
    policy = _policy_from_checkpoint(row, checkpoint_state) if row.policy == "HOODIE" else PolicyRegistry.resolve(row.policy)
    result = EvaluationRunner(
        policy=policy,
        config=config,
        topology=topology,
        runtime_parameters=runtime,
        link_rate_config=link_rate,
        task_sizes=_task_sizes(row),
        processing_density=_processing_density(row),
    ).run()
    checkpoint_hash = (
        str((checkpoint_state or {}).get("checkpoint_record", {}).get("checkpoint_hash", ""))
        if checkpoint_state is not None
        else "baseline-no-checkpoint"
    ) or "baseline-no-checkpoint"
    metrics_rows: list[dict[str, Any]] = []
    task_rows: list[dict[str, Any]] = []
    decision_rows: list[dict[str, Any]] = []
    trace_hashes: list[str] = []
    for trace_index, trace_metric in enumerate(result["per_trace"]):
        raw_records = list(trace_metric.get("raw_records", []))
        rewards = [
            -float(record["delay"])
            if record.get("terminal_outcome") == "completed" and record.get("delay") is not None
            else -40.0
            for record in raw_records
        ]
        action_counts = {"local": 0, "horizontal": 0, "vertical": 0}
        for record in raw_records:
            action = str(record.get("selected_action") or "local")
            family = "horizontal" if action.startswith("horizontal") else (
                "vertical" if action in {"vertical", "cloud", "offload_vertical"} else "local"
            )
            action_counts[family] += 1
        metrics_rows.append(
            {
                "episode": trace_index,
                "trace_id": trace_metric["trace_id"],
                "average_reward": sum(rewards) / len(rewards) if rewards else 0.0,
                "average_delay": float(trace_metric["average_delay"]),
                "drop_ratio": float(trace_metric["drop_ratio"]),
                "throughput": int(trace_metric["throughput"]),
                "completed_tasks": int(trace_metric["completed_tasks"]),
                "dropped_tasks": int(trace_metric["dropped_tasks"]),
                "total_tasks": int(trace_metric["total_tasks"]),
                "local_actions": action_counts["local"],
                "horizontal_actions": action_counts["horizontal"],
                "vertical_actions": action_counts["vertical"],
            }
        )
        trace_hash = legacy._hash(
            {
                "trace_id": trace_metric["trace_id"],
                "seed": int(row.seed or 0) + trace_index,
                "topology": topology.topology_hash(),
                "workload": row.workload_contract,
            }
        )
        trace_hashes.append(trace_hash)
        for record in raw_records:
            arrival = int(record["arrival_slot"])
            delay = record.get("delay")
            task_reward = -float(delay) if delay is not None else -40.0
            task_rows.append(
                asdict(
                    TaskRecord(
                        campaign_id=row.campaign_id,
                        panel_id=row.panel_id,
                        job_id=row.job_id,
                        run_id=str(trace_metric["trace_id"]),
                        policy=row.policy,
                        variant=row.variant,
                        seed=int(row.seed or 0) + trace_index,
                        trace_hash=trace_hash,
                        task_id=str(record["task_id"]),
                        source_agent="recorded-in-trace",
                        arrival_slot=arrival,
                        workload={"task_sizes": _task_sizes(row), "processing_density": _processing_density(row)},
                        deadline=arrival + runtime.timeout_slots - 1,
                        decision_slot=arrival,
                        selected_action=str(record.get("selected_action") or "local"),
                        destination=str(record.get("resolved_destination") or "self"),
                        completion_or_drop_slot=record.get("completion_slot"),
                        outcome=str(record.get("terminal_outcome") or "dropped"),
                        queue_delay=None,
                        transmission_delay=None,
                        service_delay=None,
                        end_to_end_delay=float(delay) if delay is not None else None,
                        reward=task_reward,
                        learner_owner=row.policy,
                        config_hash=row.config_hash,
                        source_hash=row.source_contract_hash,
                        checkpoint_hash=checkpoint_hash,
                    )
                )
            )
            decision_rows.append(
                asdict(
                    DecisionRecord(
                        observation_ref=f"{trace_metric['trace_id']}:{record['task_id']}",
                        legal_action_mask={},
                        selected_action=str(record.get("selected_action") or "local"),
                        exploration=False,
                        forecast_fields={"use_lstm": row.variant != "hoodie_no_lstm"},
                        q_value_summary={},
                        policy_metadata={"policy": row.policy, "variant": row.variant},
                    )
                )
            )
    evaluation_hash = legacy._write_csv(job_dir / "evaluation_metrics.csv", metrics_rows)
    task_hash = legacy._write_csv(job_dir / "task_records.csv", task_rows)
    decision_hash = legacy._write_csv(job_dir / "decision_records.csv", decision_rows)
    transition_hash = legacy._write_csv(job_dir / "transition_records.csv", [])
    legacy._ensure_schema(job_dir / "evaluation_metrics.schema.json", metrics_rows)
    legacy._ensure_schema(job_dir / "task_records.schema.json", task_rows)
    legacy._ensure_schema(job_dir / "decision_records.schema.json", decision_rows)
    aggregate = dict(result["aggregate"])
    aggregate["average_reward"] = (
        sum(float(row_["average_reward"]) for row_ in metrics_rows) / len(metrics_rows)
        if metrics_rows
        else 0.0
    )
    aggregate_hash = legacy._write_json(job_dir / "aggregate.json", aggregate)
    combined_trace_hash = legacy._hash(trace_hashes)
    provenance = build_provenance_manifest(
        source_commit=source_commit,
        source_contract_hash=row.source_contract_hash,
        panel_contract_hash=legacy._hash(source_contract),
        job_spec_hash=legacy._hash(asdict(row)),
        topology_hash=topology.topology_hash(),
        physical_hash=legacy._hash({**row.physical_contract, "link_rates": link_rate.to_dict()}),
        workload_hash=legacy._hash(row.workload_contract),
        training_hash="",
        evaluation_hash=evaluation_hash,
        trace_hash=combined_trace_hash,
        checkpoint_hash=checkpoint_hash,
        dataset_hashes=(evaluation_hash, task_hash, decision_hash, transition_hash, aggregate_hash),
    )
    legacy._write_json(
        job_dir / "provenance.json",
        {"manifest": asdict(provenance), "hash": provenance_hash(provenance)},
    )
    legacy.validate_evaluation_outputs_before_completion(job_dir, row)
    legacy._write_json(
        job_dir / "status.json",
        {
            **legacy._job_status_payload(
                campaign_id=row.campaign_id,
                row=row,
                status="completed",
                source_commit=source_commit,
                checkpoint_hash=checkpoint_hash,
                trace_hash=combined_trace_hash,
                dataset_hashes={
                    "evaluation_metrics": evaluation_hash,
                    "task_records": task_hash,
                    "decision_records": decision_hash,
                    "aggregate": aggregate_hash,
                },
                completed_at=time.time(),
            ),
            "completion_marker": True,
        },
    )
    legacy._write_completion_marker(job_dir)
    legacy.validate_completed_evaluation_job(job_dir, row)
    return legacy.JobExecutionResult(
        row.job_id,
        row.job_type,
        "completed",
        job_dir,
        None,
        combined_trace_hash,
        (evaluation_hash, task_hash, decision_hash, aggregate_hash),
        aggregate,
    )


class CheckpointResolver:
    def __init__(self, campaign_dir: Path) -> None:
        self.campaign_dir = campaign_dir

    def resolve(self, row: matrix.ProductionJobRow) -> dict[str, Any] | None:
        return _resolve_checkpoint(self.campaign_dir, row)


def execute_matrix_job(
    *,
    row: matrix.ProductionJobRow,
    campaign_dir: Path,
    source_commit: str,
    max_runtime_seconds: float | None,
    checkpoint_resolver: CheckpointResolver | None = None,
) -> legacy.JobExecutionResult:
    row = replace(row, campaign_id=campaign_dir.name)
    job_dir = campaign_dir / "jobs" / row.job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    prior_attempt = 0
    if (job_dir / "status.json").exists():
        prior_attempt = int(json.loads((job_dir / "status.json").read_text(encoding="utf-8")).get("attempt", 0))
    legacy._write_json(
        job_dir / "status.json",
        legacy._job_status_payload(
            campaign_id=campaign_dir.name,
            row=row,
            status="running",
            source_commit=source_commit,
            attempt=prior_attempt + 1,
            started_at=time.time(),
        ),
    )
    if row.job_type == "training":
        return _run_training_job(
            row,
            job_dir,
            source_commit=source_commit,
            max_runtime_seconds=max_runtime_seconds,
        )
    resolver = checkpoint_resolver or CheckpointResolver(campaign_dir)
    checkpoint_state = resolver.resolve(row)
    return _run_evaluation_job(
        row, job_dir, source_commit=source_commit, checkpoint_state=checkpoint_state
    )


def _rows_for_campaign(
    campaign_id: str, matrix_path: Path | None
) -> list[matrix.ProductionJobRow]:
    rows = _load_rows(matrix_path, campaign_id) if matrix_path is not None else _default_rows(campaign_id)
    if len({row.job_id for row in rows}) != len(rows):
        raise ValueError("duplicate job IDs in execution matrix")
    training_ids = {row.job_id for row in rows if row.job_type == "training"}
    missing = {
        row.checkpoint_dependency
        for row in rows
        if row.checkpoint_dependency and row.checkpoint_dependency not in training_ids
    }
    if missing:
        raise ValueError(f"unresolved checkpoint dependencies: {sorted(missing)}")
    return rows


def _write_campaign_registry(
    campaign_dir: Path,
    rows: list[matrix.ProductionJobRow],
    results: list[legacy.JobExecutionResult],
    source_commit: str,
) -> None:
    legacy._write_json(
        campaign_dir / "campaign_specification.json",
        {
            "campaign_id": campaign_dir.name,
            "source_commit": source_commit,
            "expanded_job_count": len(rows),
            "training_jobs": sum(row.job_type == "training" for row in rows),
            "evaluation_jobs": sum(row.job_type == "evaluation" for row in rows),
            "matrix_hash": legacy._hash([asdict(row) for row in rows]),
        },
    )
    legacy._write_json(campaign_dir / "source_contract_snapshot.json", legacy._source_contract_snapshot())
    legacy._write_json(campaign_dir / "job_plan.json", [asdict(row) for row in rows])
    legacy._write_json(
        campaign_dir / "environment_manifest.json",
        {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "pytorch": torch.__version__,
        },
    )
    snapshot = legacy._source_contract_snapshot()
    legacy._write_json(
        campaign_dir / "source_manifest.json",
        {"source_commit": source_commit, "source_contract_hash": snapshot["source_hash"]},
    )
    legacy._write_json(
        campaign_dir / "trace_registry.json",
        {
            "trace_banks": sorted({row.trace_bank_id for row in rows}),
            "trace_hashes": sorted({result.trace_hash for result in results if result.trace_hash}),
        },
    )
    status = campaign_status(campaign_dir.name, campaign_dir.parent)
    legacy._write_json(campaign_dir / "status.json", status)


def _dependency_available(campaign_dir: Path, row: matrix.ProductionJobRow) -> bool:
    if not row.checkpoint_dependency:
        return True
    return any(
        item.get("training_job_id") == row.checkpoint_dependency
        and item.get("scientifically_complete")
        and Path(str(item.get("checkpoint_path", ""))).exists()
        for item in legacy._load_campaign_checkpoint_registry(campaign_dir)
    )


def run_production_campaign(
    *,
    campaign_id: str,
    output_dir: Path | None = None,
    max_jobs: int | None = None,
    max_runtime_seconds: float | None = None,
    job_id: str | None = None,
    allow_paused_recovery: bool = False,
    matrix_path: Path | None = None,
) -> dict[str, Any]:
    rows = _rows_for_campaign(campaign_id, matrix_path)
    if job_id is not None:
        rows = [row for row in rows if row.job_id == job_id]
        if not rows:
            raise ValueError(f"unknown job_id: {job_id}")
    root = legacy._CAMPAIGNS_ROOT if output_dir is None else output_dir
    campaign_dir = root / campaign_id
    campaign_dir.mkdir(parents=True, exist_ok=True)
    pause_request = campaign_dir / "pause.request"
    if pause_request.exists() and not allow_paused_recovery:
        raise RuntimeError("campaign is paused; pass --allow-paused-recovery only for an intentional recovery")
    source_commit = legacy._source_commit()
    legacy._write_contract_audits(rows, campaign_dir)
    results: list[legacy.JobExecutionResult] = []
    resolver = CheckpointResolver(campaign_dir)
    start_time = time.time()
    for row in rows:
        if max_jobs is not None and len(results) >= max_jobs:
            break
        elapsed = time.time() - start_time
        if max_runtime_seconds is not None and elapsed >= max_runtime_seconds:
            break
        job_dir = campaign_dir / "jobs" / row.job_id
        if legacy.classify_job_state(job_dir).value == "completed" and (job_dir / "completion.marker").exists():
            continue
        if row.job_type == "evaluation" and not _dependency_available(campaign_dir, row):
            continue
        remaining = None if max_runtime_seconds is None else max(0.0, max_runtime_seconds - elapsed)
        try:
            result = execute_matrix_job(
                row=row,
                campaign_dir=campaign_dir,
                source_commit=source_commit,
                max_runtime_seconds=remaining,
                checkpoint_resolver=resolver,
            )
            results.append(result)
        except Exception as exc:
            job_dir.mkdir(parents=True, exist_ok=True)
            legacy._write_json(
                job_dir / "status.json",
                legacy._job_status_payload(
                    campaign_id=campaign_id,
                    row=replace(row, campaign_id=campaign_id),
                    status="failed",
                    source_commit=source_commit,
                    failure_type=exc.__class__.__name__,
                    failure_message=str(exc),
                    failure_traceback=traceback.format_exc(),
                ),
            )
    _write_campaign_registry(campaign_dir, _rows_for_campaign(campaign_id, matrix_path), results, source_commit)
    status = campaign_status(campaign_id, root, matrix_path=matrix_path)
    return {
        "campaign_id": campaign_id,
        "source_commit": source_commit,
        "jobs_executed_this_invocation": len(results),
        "max_jobs": max_jobs,
        "max_runtime_seconds": max_runtime_seconds,
        **status,
    }


def campaign_status(
    campaign_id: str,
    output_dir: Path | None = None,
    matrix_path: Path | None = None,
) -> dict[str, Any]:
    root = legacy._CAMPAIGNS_ROOT if output_dir is None else output_dir
    campaign_dir = root / campaign_id
    plan_path = campaign_dir / "job_plan.json"
    if plan_path.exists() and matrix_path is None:
        rows = _load_rows(plan_path, campaign_id)
    else:
        rows = _rows_for_campaign(campaign_id, matrix_path)
    counts = {
        key: 0
        for key in (
            "pending",
            "running",
            "completed",
            "failed",
            "stale",
            "corrupt",
            "quarantined",
            "blocked_dependency",
            "interrupted_resumable",
            "scientifically_incomplete",
        )
    }
    for row in rows:
        job_dir = campaign_dir / "jobs" / row.job_id
        if not job_dir.exists():
            key = "blocked_dependency" if row.job_type == "evaluation" and not _dependency_available(campaign_dir, row) else "pending"
            counts[key] += 1
            continue
        state = legacy.classify_job_state(job_dir).value
        key = state if state in counts else "corrupt"
        counts[key] += 1
    return {
        "campaign_id": campaign_id,
        "total": len(rows),
        "training_jobs": sum(row.job_type == "training" for row in rows),
        "evaluation_jobs": sum(row.job_type == "evaluation" for row in rows),
        **{f"{key}_jobs": value for key, value in counts.items()},
    }


def resume_production_campaign(
    campaign_id: str,
    output_dir: Path | None = None,
    *,
    max_jobs: int | None = None,
    max_runtime_seconds: float | None = None,
    job_id: str | None = None,
    allow_paused_recovery: bool = False,
    matrix_path: Path | None = None,
) -> dict[str, Any]:
    return run_production_campaign(
        campaign_id=campaign_id,
        output_dir=output_dir,
        max_jobs=max_jobs,
        max_runtime_seconds=max_runtime_seconds,
        job_id=job_id,
        allow_paused_recovery=allow_paused_recovery,
        matrix_path=matrix_path,
    )


def install_production_patch() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    install_matrix_patch()
    legacy._build_trace = _build_trace
    legacy._policy_for_row = _policy_from_checkpoint
    legacy._run_training_job = _run_training_job
    legacy._run_evaluation_job = _run_evaluation_job
    legacy._register_training_checkpoint = _checkpoint_record
    legacy.CheckpointResolver = CheckpointResolver
    legacy.execute_matrix_job = execute_matrix_job
    legacy._update_campaign_registry = _write_campaign_registry
    legacy.run_production_campaign = run_production_campaign
    legacy.campaign_status = campaign_status
    legacy.resume_production_campaign = resume_production_campaign
    _INSTALLED = True
