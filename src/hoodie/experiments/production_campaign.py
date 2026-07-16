from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import csv
import faulthandler
import json
import os
import signal
from pathlib import Path
import platform
import shutil
import tempfile
import time
import traceback
from statistics import mean, pstdev
from typing import Any, Iterable

import torch

from src.agents.hoodie_agent import HoodieAgent
from src.config.training_config import TrainingConfig
from src.environment.evaluation_gym_adapter import EvaluationHoodieGymEnvironment
from src.environment.runtime_model import SharedRuntimeParameters
from src.environment.topology import TopologyGraph
from src.evaluation.config import EvaluationConfig
from src.evaluation.metrics import evaluate_run, evaluate_trace, TaskEvaluationRecord, TraceMetrics
from src.evaluation.policy_registry import PolicyRegistry
from src.evaluation.runner import EvaluationRunner
from src.evaluation.trace_protocol import TraceTaskBlueprint, build_deterministic_trace
from src.policies.policy_interface import PolicyContext
from src.reference_model.models import TaskIdentity, TaskWorkload
from src.training.seed_management import SeedManagement

from .aggregation import aggregate_records
from .checkpoint_registry import CheckpointContract, CheckpointRecord
from .job_identity import compute_experiment_id, compute_job_id
from .job_matrix import ProductionJobRow
from .contract_mapping import apply_panel_sweep, build_evaluation_config, build_environment_config, build_training_config, validate_contract_mapping
from .panel_registry import PANEL_REGISTRY
from .provenance import build_provenance_manifest, provenance_hash
from .resume import classify_job_state
from .schemas import AggregateRecord, DecisionRecord, TaskRecord, TrainingHistoryRecord, TransitionRecord
from .source_contracts import build_figures_8_11_source_contract
from .storage import AtomicJobStorage
from .trace_registry import TraceRecord, TraceRegistry

_MATRIX_PATH = Path("artifacts/hoodie/implementation_run/campaign/expected_production_job_matrix.json")
_CAMPAIGNS_ROOT = Path("artifacts/hoodie/campaigns")
_RELEASES_ROOT = Path("artifacts/hoodie/releases")


@dataclass(frozen=True, slots=True)
class JobExecutionResult:
    job_id: str
    job_type: str
    status: str
    output_dir: Path
    checkpoint_id: str | None = None
    trace_hash: str | None = None
    dataset_hashes: tuple[str, ...] = ()
    metrics: dict[str, Any] | None = None


def _job_status_payload(
    *,
    campaign_id: str,
    row: ProductionJobRow,
    status: str,
    source_commit: str,
    attempt: int = 1,
    started_at: float | None = None,
    completed_at: float | None = None,
    checkpoint_hash: str | None = None,
    trace_hash: str | None = None,
    dataset_hashes: dict[str, str] | None = None,
    failure_type: str | None = None,
    failure_message: str | None = None,
    failure_traceback: str | None = None,
) -> dict[str, Any]:
    now = time.time()
    return {
        "campaign_id": campaign_id,
        "job_id": row.job_id,
        "scientific_unit_id": row.scientific_unit_id,
        "panel_id": row.panel_id,
        "job_type": row.job_type,
        "status": status,
        "attempt": attempt,
        "started_at": started_at or now,
        "updated_at": now,
        "completed_at": completed_at,
        "source_commit": source_commit,
        "job_spec_hash": _hash(asdict(row)),
        "trace_hash": trace_hash,
        "checkpoint_hash": checkpoint_hash,
        "dataset_hashes": dataset_hashes or {},
        "failure_type": failure_type,
        "failure_message": failure_message,
        "failure_traceback": failure_traceback,
        "worker_identity": platform.node(),
    }


def _write_completion_marker(job_dir: Path) -> None:
    (job_dir / "completion.marker").write_text("complete\n", encoding="utf-8")


def _canonical(payload: object) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _hash(payload: object) -> str:
    return sha256(_canonical(payload).encode("utf-8")).hexdigest()


def _state_hash(payload: object) -> str:
    return sha256(json.dumps(payload, sort_keys=True, default=str, separators=(",", ":")).encode("utf-8")).hexdigest()


def _job_storage(campaign_dir: Path) -> AtomicJobStorage:
    return AtomicJobStorage(campaign_dir / "jobs")


def _read_matrix() -> list[ProductionJobRow]:
    rows = json.loads(_MATRIX_PATH.read_text(encoding="utf-8"))
    return [ProductionJobRow(**row) for row in rows]


def _validate_matrix(rows: list[ProductionJobRow]) -> None:
    if len(rows) != 284:
        raise ValueError(f"unexpected job count: {len(rows)}")
    if len({row.job_id for row in rows}) != len(rows):
        raise ValueError("duplicate job_id in matrix")
    if len({row.scientific_unit_id for row in rows}) != len(rows):
        raise ValueError("duplicate scientific_unit_id in matrix")
    eval_rows = [row for row in rows if row.job_type == "evaluation"]
    train_rows = [row for row in rows if row.job_type == "training"]
    if len(train_rows) != 48 or len(eval_rows) != 236:
        raise ValueError("matrix training/evaluation split mismatch")
    for panel_id in {row.panel_id for row in rows}:
        panel_rows = [row for row in rows if row.panel_id == panel_id]
        if panel_id.startswith("figure_10") and len({row.policy for row in panel_rows}) != 7:
            raise ValueError(f"panel {panel_id} missing seven policies")
        if panel_id == "figure_11" and len({row.variant for row in panel_rows}) != 2:
            raise ValueError("figure_11 missing both variants")


def _matrix_source_contract() -> dict[str, Any]:
    return _source_contract_snapshot()


def _training_contract_audit(rows: list[ProductionJobRow]) -> list[dict[str, Any]]:
    report: list[dict[str, Any]] = []
    for row in rows:
        if row.job_type != "training":
            continue
        source_contract = _panel_contract(row.panel_id)
        config = build_training_config(row, source_contract, trace_hash="trace", output_dir=Path("/tmp"))
        mismatches = validate_contract_mapping(row, source_contract)
        report.append({
            "job_id": row.job_id,
            "panel_id": row.panel_id,
            "series": row.series_name,
            "variant": row.variant,
            "seed": row.seed,
            "independent_variable": row.independent_variable,
            "independent_value": row.independent_value,
            "required_training_episodes": int(source_contract.get("training_episodes", 0)),
            "required_slots_per_episode": int(source_contract.get("slots_per_episode", 110 if row.panel_id.startswith("figure_8") else source_contract.get("validation_episodes", 200))),
            "learning_rate": config.learning_rate,
            "discount_factor": config.discount_factor,
            "agent_count": int((source_contract.get("agent_counts") or [20])[0]),
            "lstm_enabled": row.variant != "hoodie_no_lstm",
            "source_contract_path": "resources/papers/hoodie/contracts/figure_8.json" if row.panel_id.startswith("figure_8") else "resources/papers/hoodie/contracts/figure_11.json",
            "generated_executor_configuration": config.to_dict(),
            "mismatches": mismatches,
            "valid": not mismatches,
        })
    return report


def _evaluation_contract_audit(rows: list[ProductionJobRow]) -> list[dict[str, Any]]:
    report: list[dict[str, Any]] = []
    for row in rows:
        if row.job_type != "evaluation":
            continue
        source_contract = _panel_contract(row.panel_id)
        config = build_evaluation_config(row, source_contract, trace_id="trace", output_dir=Path("/tmp"))
        mismatches = validate_contract_mapping(row, source_contract)
        report.append({
            "job_id": row.job_id,
            "panel_id": row.panel_id,
            "policy": row.policy,
            "variant": row.variant,
            "seed": row.seed,
            "independent_variable": row.independent_variable,
            "independent_value": row.independent_value,
            "required_validation_episodes": config.episode_count,
            "required_slots_per_episode": config.episode_length,
            "arrival_probability": source_contract.get("task_arrival_probability"),
            "cpu_capacity": source_contract.get("cpu_computation_capacity_ghz"),
            "timeout_seconds": source_contract.get("task_timeout_seconds"),
            "agent_count": source_contract.get("agent_counts"),
            "traffic_scenario": source_contract.get("traffic_scenarios"),
            "communication_rate_scenario": source_contract.get("rate_scenarios"),
            "checkpoint_dependency": row.checkpoint_dependency,
            "trace_bank_id": row.trace_bank_id,
            "generated_executor_configuration": {"policy_name": config.policy_name, "seed": config.seed, "trace_id": config.trace_id, "episode_count": config.episode_count, "episode_length": config.episode_length, "drain_slots": config.drain_slots, "output_dir": str(config.output_dir) if config.output_dir is not None else None, "trace_mode": config.trace_mode, "device": config.device},
            "mismatches": mismatches,
            "valid": not mismatches,
        })
    return report


def _write_contract_audits(rows: list[ProductionJobRow], campaign_dir: Path) -> None:
    audit_dir = campaign_dir.parent.parent / "implementation_run" / "campaign"
    _write_json(audit_dir / "training_contract_audit.json", _training_contract_audit(rows))
    _write_json(audit_dir / "evaluation_contract_audit.json", _evaluation_contract_audit(rows))


def _load_campaign_id(matrix_rows: list[ProductionJobRow]) -> str:
    payload = [asdict(row) for row in matrix_rows]
    return f"figures-8-11-{_hash(payload)[:12]}"


def _source_commit() -> str:
    import subprocess

    return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()


def _panel_contract(panel_id: str) -> dict[str, Any]:
    return PANEL_REGISTRY[panel_id].source_contract


def _source_contract_snapshot() -> dict[str, Any]:
    contract = build_figures_8_11_source_contract()
    source_contract_hash = sha256(Path(contract.source_path).read_bytes()).hexdigest()
    return {
        "source_hash": source_contract_hash,
        "source_contract_hash": source_contract_hash,
        "source_path": contract.source_path,
        "panels": [asdict(panel) for panel in contract.panels],
        "summary": contract.summary(),
    }


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, dir=path.parent, encoding="utf-8") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
        temp_path = Path(handle.name)
    os.replace(temp_path, path)


def _write_json(path: Path, payload: object) -> str:
    _atomic_write_text(path, _canonical(payload) + "\n")
    return _hash(payload)


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        _atomic_write_text(path, "")
        return _hash([])
    with tempfile.NamedTemporaryFile("w", delete=False, dir=path.parent, encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
        handle.flush()
        os.fsync(handle.fileno())
        temp_path = Path(handle.name)
    os.replace(temp_path, path)
    return _hash(rows)


def _load_csv_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _job_internal_checkpoint_dir(job_dir: Path) -> Path:
    return job_dir / "internal_checkpoints"


def _latest_internal_checkpoint(job_dir: Path) -> Path | None:
    latest = _job_internal_checkpoint_dir(job_dir) / "latest.json"
    if not latest.exists():
        return None
    payload = json.loads(latest.read_text(encoding="utf-8"))
    checkpoint_path = payload.get("checkpoint_path")
    return Path(checkpoint_path) if checkpoint_path else None


def _load_internal_checkpoint_state(job_dir: Path) -> dict[str, Any] | None:
    checkpoint_path = _latest_internal_checkpoint(job_dir)
    if checkpoint_path is None or not checkpoint_path.exists():
        return None
    return torch.load(checkpoint_path, map_location="cpu", weights_only=False)


def _write_internal_checkpoint(job_dir: Path, *, checkpoint_state: dict[str, Any], metadata: dict[str, Any]) -> str:
    checkpoint_dir = _job_internal_checkpoint_dir(job_dir) / metadata["checkpoint_id"]
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = checkpoint_dir / "checkpoint.pt"
    torch.save(checkpoint_state, checkpoint_path)
    _write_json(checkpoint_dir / "metadata.json", metadata)
    latest_payload = {"checkpoint_id": metadata["checkpoint_id"], "checkpoint_path": str(checkpoint_path), "updated_at": time.time()}
    _write_json(_job_internal_checkpoint_dir(job_dir) / "latest.json", latest_payload)
    return metadata["checkpoint_id"]


def _write_progress(job_dir: Path, payload: dict[str, Any]) -> None:
    _write_json(job_dir / "progress.json", payload)


def _trace_bank_spec(row: ProductionJobRow) -> dict[str, Any]:
    return {
        "campaign_id": row.campaign_id,
        "panel_id": row.panel_id,
        "scientific_unit_id": row.scientific_unit_id,
        "trace_bank_id": row.trace_bank_id,
        "independent_value": row.independent_value,
        "series_name": row.series_name,
        "policy": row.policy,
        "variant": row.variant,
        "topology": row.topology_contract,
        "workload": row.workload_contract,
    }


def _build_trace(row: ProductionJobRow, *, episode_index: int = 0) -> tuple[TraceRegistry, dict[str, Any]]:
    panel_payload = _panel_contract(row.panel_id)
    topology = row.topology_contract
    agent_count = int(panel_payload.get("agent_counts", [20])[0] if panel_payload.get("agent_counts") else 20)
    if row.independent_variable == "task_arrival_probability" and isinstance(row.independent_value, (int, float)):
        arrival_probability = float(row.independent_value)
    else:
        arrival_probability = float(panel_payload.get("task_arrival_probability", 0.5) or 0.5)
    if row.independent_variable == "task_timeout_seconds" and isinstance(row.independent_value, (int, float)):
        timeout_slots = max(1, int(round(float(row.independent_value) / 0.1)))
    else:
        timeout_slots = int(panel_payload.get("task_timeout_slots", 20) or 20)
    if row.independent_variable == "task_arrival_probability" and row.panel_id.startswith("figure_10"):
        arrival_probability = float(row.independent_value)
    episode_length = int(panel_payload.get("training_episodes", 110) if row.job_type == "training" else panel_payload.get("validation_episodes", 200))
    drain_slots = 10 if episode_length >= 10 else 0
    trace = build_deterministic_trace(
        trace_id=f"{row.trace_bank_id}-{episode_index}",
        seed=int(row.seed or 0) + episode_index,
        episode_length=episode_length,
        agent_count=agent_count,
        arrival_probability=arrival_probability,
        timeout_length=timeout_slots,
        drain_slots=drain_slots,
    )
    records = [
        TraceRecord(
            task_identity=TaskIdentity(str(task.task_id), str(task.source_agent_id), f"ea-{task.source_agent_id}"),
            workload=TaskWorkload(int(round(task.size)), int(round(task.timeout_length)), int(task.arrival_slot)),
            decision_seed=int(row.seed or 0) + episode_index,
        )
        for task in trace.tasks
    ]
    registry = TraceRegistry.from_records(trace.trace_id, records, source_hash=row.source_contract_hash)
    return registry, {"trace": trace, "records": records, "trace_hash": registry.hash(), "spec": _trace_bank_spec(row)}


def _policy_for_row(row: ProductionJobRow, *, checkpoint_state: dict[str, Any] | None = None):
    if row.policy == "HOODIE":
        agent = HoodieAgent(use_lstm=(row.variant != "hoodie_no_lstm"))
        if checkpoint_state is not None:
            agent = HoodieAgent.from_state(checkpoint_state)
            agent.use_lstm = row.variant != "hoodie_no_lstm"
        return agent
    return PolicyRegistry.resolve(row.policy)


def _probe_policy_q_value(policy: Any) -> float:
    learner = getattr(getattr(policy, "learner", None), "learner", None)
    if learner is None:
        return 0.0
    probe = torch.zeros(learner.input_dim, device=learner.device)
    return float(learner.online_network(probe).mean().detach().cpu().item())


def _training_config(row: ProductionJobRow, *, trace_hash: str, output_dir: Path) -> TrainingConfig:
    source_contract = _panel_contract(row.panel_id)
    return build_training_config(row, source_contract, trace_hash=trace_hash, output_dir=output_dir)


def _build_environment_parameters(row: ProductionJobRow) -> SharedRuntimeParameters:
    source_contract = _panel_contract(row.panel_id)
    return build_environment_config(row, source_contract)


def _build_evaluation_config(row: ProductionJobRow, *, trace_id: str, output_dir: Path) -> EvaluationConfig:
    source_contract = _panel_contract(row.panel_id)
    return build_evaluation_config(row, source_contract, trace_id=trace_id, output_dir=output_dir)


def _ensure_schema(path: Path, rows: list[dict[str, Any]]) -> str:
    schema = {"fields": list(rows[0].keys()) if rows else []}
    return _write_json(path, schema)




def _scientific_completion_requirements(row: ProductionJobRow) -> dict[str, Any]:
    panel_payload = _panel_contract(row.panel_id)
    return {
        "required_training_episodes": int(panel_payload.get("training_episodes", 0)),
        "required_validation_episodes": int(panel_payload.get("validation_episodes", 0)),
        "required_slots_per_episode": 110 if row.panel_id.startswith("figure_8") else int(panel_payload.get("validation_episodes", 200)),
    }


def _job_scientifically_complete(job_dir: Path, row: ProductionJobRow) -> bool:
    requirements = _scientific_completion_requirements(row)
    if row.job_type != "training":
        return True
    training_history = _load_csv_rows(job_dir / "training_history.csv")
    episodes = sorted({int(record.get("episode_or_step", -1)) for record in training_history})
    if len(episodes) != requirements["required_training_episodes"]:
        return False
    if episodes and (episodes[0] != 0 or episodes[-1] != requirements["required_training_episodes"] - 1):
        return False
    checkpoint = _latest_internal_checkpoint(job_dir)
    if checkpoint is None or not checkpoint.exists():
        return False
    if not (job_dir / "checkpoint_selection.json").exists():
        return False
    if not (job_dir / "completion.marker").exists():
        return False
    return True

def _run_training_job(row: ProductionJobRow, job_dir: Path, *, source_commit: str, max_runtime_seconds: float | None = None) -> JobExecutionResult:
    registry, trace_bundle = _build_trace(row)
    trace = trace_bundle["trace"]
    panel_contract = _panel_contract(row.panel_id)
    attempt = int(json.loads((job_dir / "status.json").read_text(encoding="utf-8")).get("attempt", 1)) if (job_dir / "status.json").exists() else 1
    faulthandler.enable(all_threads=True)
    training_rows: list[TrainingHistoryRecord] = []
    transition_rows: list[TransitionRecord] = []
    decision_rows: list[DecisionRecord] = []
    task_rows: list[TaskRecord] = []
    previous_training_rows = _load_csv_rows(job_dir / "training_history.csv")
    if previous_training_rows:
        for record in previous_training_rows:
            training_rows.append(
                TrainingHistoryRecord(
                    episode_or_step=int(record.get("episode_or_step", 0)),
                    loss=float(record.get("loss", 0.0)),
                    epsilon=float(record.get("epsilon", 0.0)),
                    replay_size=int(record.get("replay_size", 0)),
                    target_update_count=int(record.get("target_update_count", 0)),
                    checkpoint_id=str(record.get("checkpoint_id", "")),
                )
            )
    resume_state = _load_internal_checkpoint_state(job_dir)
    if resume_state is not None and resume_state.get("policy_state"):
        policy = HoodieAgent.from_state(resume_state["policy_state"])
        policy.use_lstm = row.variant != "hoodie_no_lstm"
        episode_start = int(resume_state.get("next_episode", len(training_rows)))
        episode_rewards = list(resume_state.get("episode_rewards", []))
        transition_rows.extend(TransitionRecord(**record) for record in resume_state.get("transition_rows", []))
        decision_rows.extend(DecisionRecord(**record) for record in resume_state.get("decision_rows", []))
        task_rows.extend(TaskRecord(**record) for record in resume_state.get("task_rows", []))
    else:
        policy = HoodieAgent(use_lstm=(row.variant != "hoodie_no_lstm"))
        policy.exploration_epsilon = 0.1
        episode_start = len(training_rows)
        episode_rewards = []
    config = _training_config(row, trace_hash=trace_bundle["trace_hash"], output_dir=job_dir)
    runtime_parameters = _build_environment_parameters(row)
    env = EvaluationHoodieGymEnvironment(
        episode_length=config.episode_length,
        topology=TopologyGraph.from_approved_assumption_registry(),
        runtime_parameters=runtime_parameters,
        compute_config=runtime_parameters.to_compute_config(),
        policy_name="HOODIE",
        supplied_trace=trace,
    )
    interrupted = False
    def _sig_handler(signum, frame):  # type: ignore[no-redef]
        nonlocal interrupted
        interrupted = True
    previous_int = signal.signal(signal.SIGINT, _sig_handler)
    previous_term = signal.signal(signal.SIGTERM, _sig_handler)
    try:
        last_checkpoint_id = str(resume_state.get("checkpoint_id", "")) if resume_state else ""
        start_time = time.time()
        # Append-only state starts from existing committed rows.
        for episode_index in range(episode_start, config.episode_count):
            if interrupted or (max_runtime_seconds is not None and (time.time() - start_time) >= max_runtime_seconds):
                interrupted = True
                break
            if config.episode_count:
                policy.exploration_epsilon = max(0.01, 0.2 * (1.0 - episode_index / max(1, config.episode_count)))
            episode_trace = build_deterministic_trace(
                trace_id=f"{trace.trace_id}-{episode_index}",
                seed=int(row.seed or 0) + episode_index,
                episode_length=config.episode_length,
                agent_count=int(panel_contract.get("agent_counts", [20])[0] if panel_contract.get("agent_counts") else 20),
                arrival_probability=float(panel_contract.get("task_arrival_probability", 0.5) or 0.5),
                timeout_length=int(panel_contract.get("default_timeout_slots", 20) or 20),
                drain_slots=config.drain_slots,
            )
            env.supplied_trace = episode_trace
            env.reset(seed=episode_trace.seed)
            episode_reward = 0.0
            last_loss = 0.0
            task_metadata: dict[int, dict[str, Any]] = {blueprint.task_id: {
                "source_agent_id": blueprint.source_agent_id,
                "size": blueprint.size,
                "processing_density": blueprint.processing_density,
                "timeout_length": blueprint.timeout_length,
                "absolute_deadline_slot": blueprint.absolute_deadline_slot,
            } for blueprint in episode_trace.tasks}
            slot_index = 0
            while True:
                if interrupted or (max_runtime_seconds is not None and (time.time() - start_time) >= max_runtime_seconds):
                    interrupted = True
                    break
                observation, reward, terminated, truncated, info = env.step_slot(policy)
                episode_reward += float(reward)
                slot_index = int(getattr(env, "current_slot", slot_index + 1))
                for decision in info.get("decision_events", []):
                    task_metadata.setdefault(int(decision["task_id"]), {}).update(decision)
                    decision_rows.append(
                        DecisionRecord(
                            observation_ref=f"{row.job_id}:{episode_index}:{decision['task_id']}",
                            legal_action_mask=dict(decision.get("legal_action_mask", {})),
                            selected_action=str(decision.get("action")),
                            exploration=bool(policy.exploration_epsilon > 0.0),
                            forecast_fields={"use_lstm": policy.use_lstm},
                            q_value_summary={"mean": 0.0, "std": 0.0},
                            policy_metadata={"policy": row.policy, "variant": row.variant},
                        )
                    )
                for finalized in info.get("finalized_tasks", []):
                    meta = task_metadata.get(int(finalized["task_id"]), {})
                    task_rows.append(
                        TaskRecord(
                            campaign_id=row.campaign_id,
                            panel_id=row.panel_id,
                            job_id=row.job_id,
                            run_id=episode_trace.trace_id,
                            policy=row.policy,
                            variant=row.variant,
                            seed=int(row.seed or 0),
                            trace_hash=registry.hash(),
                            task_id=str(finalized["task_id"]),
                            source_agent=str(meta.get("source_agent_id", finalized.get("source_agent_id", finalized["task_id"]))),
                            arrival_slot=int(finalized["arrival_slot"]),
                            workload={"task_size": meta.get("size"), "processing_density": meta.get("processing_density"), "timeout_slots": meta.get("timeout_length")},
                            deadline=int(meta.get("absolute_deadline_slot", finalized.get("absolute_deadline_slot", 0))) if meta.get("absolute_deadline_slot") is not None or finalized.get("absolute_deadline_slot") is not None else None,
                            decision_slot=int(finalized.get("decision_slot", finalized.get("arrival_slot", 0))),
                            selected_action=str(finalized.get("selected_action", "local")),
                            destination=str(finalized.get("resolved_destination", "local")),
                            completion_or_drop_slot=int(finalized.get("completion_slot")) if finalized.get("completion_slot") is not None else None,
                            outcome=str(finalized.get("terminal_outcome", "completed")),
                            queue_delay=float(finalized.get("queue_delay_slots", 0.0)) if finalized.get("queue_delay_slots") is not None else None,
                            transmission_delay=float(finalized.get("transmission_delay_slots", 0.0)) if finalized.get("transmission_delay_slots") is not None else None,
                            service_delay=float(finalized.get("service_delay_slots", 0.0)) if finalized.get("service_delay_slots") is not None else None,
                            end_to_end_delay=float(finalized.get("delay", 0.0)) if finalized.get("delay") is not None else None,
                            reward=float(finalized.get("reward", 0.0)),
                            learner_owner=row.policy,
                            config_hash=row.config_hash,
                            source_hash=row.source_contract_hash,
                            checkpoint_hash=last_checkpoint_id or "",
                        )
                    )
                for delivery in info.get("reward_delivery_events", []):
                    transition_rows.append(
                        TransitionRecord(
                            owner=row.policy,
                            originating_decision=f"{row.job_id}:{delivery.get('task_id')}",
                            delayed_reward=float(delivery.get("reward", 0.0)),
                            next_state=json.dumps(observation, sort_keys=True, default=str),
                            terminal=bool(terminated or truncated),
                            assignment_slot=int(delivery.get("resolution_slot", episode_index)),
                            uniqueness_id=f"{row.job_id}:{episode_index}:{delivery.get('task_id')}",
                        )
                    )
                    policy.record_transition(
                        state=dict(observation),
                        action=str(delivery.get("selected_action", "local")),
                        reward=float(delivery.get("reward", 0.0)),
                        next_state=dict(observation),
                        done=bool(terminated or truncated),
                    )
                    updated = policy.learn_from_replay(batch_size=64, learning_rate=float(config.learning_rate))
                    last_loss = float(updated)
                progress_payload = {
                    "campaign_id": row.campaign_id,
                    "job_id": row.job_id,
                    "attempt": attempt,
                    "phase": "training",
                    "current_episode": episode_index,
                    "total_episodes": config.episode_count,
                    "current_slot": slot_index,
                    "total_slots_per_episode": config.episode_length,
                    "completed_environment_steps": episode_index * config.episode_length + slot_index,
                    "generated_tasks": len(task_rows),
                    "completed_tasks": sum(1 for task in task_rows if task.outcome == "completed"),
                    "dropped_tasks": sum(1 for task in task_rows if task.outcome != "completed"),
                    "replay_size": len(policy.learner.replay),
                    "optimizer_step_count": policy.learner.learner.training_steps,
                    "target_copy_count": policy.learner.learner.target_update_steps,
                    "epsilon": policy.exploration_epsilon,
                    "most_recent_finite_loss": last_loss,
                    "accumulated_reward": episode_reward,
                    "latest_internal_checkpoint": last_checkpoint_id,
                    "latest_training_history_row": episode_index,
                    "heartbeat_timestamp": time.time(),
                    "elapsed_seconds": time.time() - start_time,
                    "estimated_remaining_seconds": None,
                    "worker_pid": os.getpid(),
                    "supervisor_pid": os.getppid(),
                    "backend_device": str(policy.learner.learner.device),
                }
                _write_progress(job_dir, progress_payload)
                if terminated or truncated:
                    break
                if interrupted or (max_runtime_seconds is not None and (time.time() - start_time) >= max_runtime_seconds):
                    interrupted = True
                    break
            training_rows.append(
                TrainingHistoryRecord(
                    episode_or_step=episode_index,
                    loss=last_loss,
                    epsilon=policy.exploration_epsilon,
                    replay_size=len(policy.learner.replay),
                    target_update_count=policy.learner.learner.target_update_steps,
                    checkpoint_id=last_checkpoint_id,
                )
            )
            policy_state = policy.export_state()
            checkpoint_state = {
                **policy_state,
                "policy_state": policy_state,
                "checkpoint_id": "",
                "next_episode": episode_index + 1,
                "episode_rewards": episode_rewards + [episode_reward],
                "task_rows": [asdict(row_) for row_ in task_rows],
                "decision_rows": [asdict(row_) for row_ in decision_rows],
                "transition_rows": [asdict(row_) for row_ in transition_rows],
            }
            last_checkpoint_id = _hash({"job_id": row.job_id, "policy": row.policy, "variant": row.variant, "seed": row.seed, "source": source_commit, "episode": episode_index})[:24]
            checkpoint_state["checkpoint_id"] = last_checkpoint_id
            _write_internal_checkpoint(job_dir, checkpoint_state=checkpoint_state, metadata={
                "checkpoint_id": last_checkpoint_id,
                "training_job_id": row.job_id,
                "policy": row.policy,
                "variant": row.variant,
                "training_seed": int(row.seed or 0),
                "selected_episode": episode_index,
                "selection_rule": "episode_boundary",
                "selection_metric": "accumulated_reward",
                "selection_value": float(episode_reward),
                "online_network_hash": _state_hash(checkpoint_state.get("online_state_dict", {})),
                "target_network_hash": _state_hash(checkpoint_state.get("target_state_dict", {})),
                "optimizer_state_hash": _state_hash(checkpoint_state.get("optimizer_state_dict", {})),
                "replay_state_hash": _state_hash(checkpoint_state.get("replay_buffer", {})),
                "RNG_state_hash": _state_hash(checkpoint_state.get("rng_state", {})),
                "LSTM_state_hash": None if row.variant == "hoodie_no_lstm" else _state_hash({"use_lstm": True}),
                "configuration_hash": row.config_hash,
                "topology_hash": _hash(row.topology_contract),
                "workload_hash": _hash(row.workload_contract),
                "source_contract_hash": row.source_contract_hash,
                "source_commit": source_commit,
            })
            training_rows[-1] = TrainingHistoryRecord(
                episode_or_step=episode_index,
                loss=last_loss,
                epsilon=policy.exploration_epsilon,
                replay_size=len(policy.learner.replay),
                target_update_count=policy.learner.learner.target_update_steps,
                checkpoint_id=last_checkpoint_id,
            )
            _write_csv(job_dir / "training_history.csv", [asdict(record) for record in training_rows])
            _write_csv(job_dir / "task_records.csv", [asdict(record) for record in task_rows])
            _write_csv(job_dir / "decision_records.csv", [asdict(record) for record in decision_rows])
            _write_csv(job_dir / "transition_records.csv", [asdict(record) for record in transition_rows])
            if time.time() - start_time > 0 and os.environ.get("HOODIE_TEST_BOUNDARY") == "1":
                interrupted = True
            if interrupted:
                break
        task_hash = _write_csv(job_dir / "task_records.csv", [asdict(row) for row in task_rows])
        decision_hash = _write_csv(job_dir / "decision_records.csv", [asdict(row) for row in decision_rows])
        transition_hash = _write_csv(job_dir / "transition_records.csv", [asdict(row) for row in transition_rows])
        training_hash = _write_csv(job_dir / "training_history.csv", [asdict(row) for row in training_rows])
        _ensure_schema(job_dir / "task_records.schema.json", [asdict(row) for row in task_rows])
        _ensure_schema(job_dir / "decision_records.schema.json", [asdict(row) for row in decision_rows])
        _ensure_schema(job_dir / "transition_records.schema.json", [asdict(row) for row in transition_rows])
        _ensure_schema(job_dir / "training_history.schema.json", [asdict(row) for row in training_rows])
        scientific_complete = _job_scientifically_complete(job_dir, row)
        if interrupted or not scientific_complete:
            status_value = "interrupted_resumable" if interrupted or max_runtime_seconds is not None else "scientifically_incomplete"
            _write_json(job_dir / "status.json", _job_status_payload(campaign_id=row.campaign_id, row=row, status=status_value, source_commit=source_commit, attempt=attempt, started_at=time.time(), dataset_hashes={"task_records": task_hash, "decision_records": decision_hash, "transition_records": transition_hash, "training_history": training_hash}))
            return JobExecutionResult(job_id=row.job_id, job_type=row.job_type, status=status_value, output_dir=job_dir, checkpoint_id=last_checkpoint_id, trace_hash=registry.hash(), dataset_hashes=(task_hash, decision_hash, transition_hash, training_hash), metrics={"episode_rewards": episode_rewards})
        checkpoint_selection = {"checkpoint_id": last_checkpoint_id, "selection_rule": "final_episode", "selection_metric": "accumulated_reward", "selection_value": float(episode_rewards[-1] if episode_rewards else 0.0)}
        _write_json(job_dir / "checkpoint_selection.json", checkpoint_selection)
        provenance = build_provenance_manifest(
            source_commit=source_commit,
            source_contract_hash=row.source_contract_hash,
            panel_contract_hash=_hash(_panel_contract(row.panel_id)),
            job_spec_hash=_hash(asdict(row)),
            topology_hash=_hash(row.topology_contract),
            physical_hash=_hash(row.physical_contract),
            workload_hash=_hash(row.workload_contract),
            training_hash=training_hash,
            evaluation_hash="",
            trace_hash=registry.hash(),
            checkpoint_hash=_hash({"checkpoint_id": last_checkpoint_id}),
            dataset_hashes=(task_hash, decision_hash, transition_hash, training_hash),
        )
        provenance_hash_value = provenance_hash(provenance)
        _write_json(job_dir / "provenance.json", {"manifest": asdict(provenance), "hash": provenance_hash_value})
        _write_json(job_dir / "status.json", {
            **_job_status_payload(
                campaign_id=row.campaign_id,
                row=row,
                status="completed",
                source_commit=source_commit,
                checkpoint_hash=_hash({"checkpoint_id": last_checkpoint_id}),
                trace_hash=registry.hash(),
                dataset_hashes={"task_records": task_hash, "decision_records": decision_hash, "transition_records": transition_hash, "training_history": training_hash},
                completed_at=time.time(),
            ),
            "completion_marker": True,
        })
        _write_completion_marker(job_dir)
        return JobExecutionResult(job_id=row.job_id, job_type=row.job_type, status="completed", output_dir=job_dir, checkpoint_id=last_checkpoint_id, trace_hash=registry.hash(), dataset_hashes=(task_hash, decision_hash, transition_hash, training_hash), metrics={"episode_rewards": episode_rewards})
    finally:
        signal.signal(signal.SIGINT, previous_int)
        signal.signal(signal.SIGTERM, previous_term)
def _run_evaluation_job(row: ProductionJobRow, job_dir: Path, *, source_commit: str, checkpoint_state: dict[str, Any] | None = None) -> JobExecutionResult:
    registry, trace_bundle = _build_trace(row)
    trace = trace_bundle["trace"]
    trace_meta = {blueprint.task_id: blueprint for blueprint in trace.tasks}
    if row.policy == "HOODIE":
        policy = _policy_for_row(row, checkpoint_state=checkpoint_state)
    else:
        policy = _policy_for_row(row)
    validation_episodes = int(_panel_contract(row.panel_id).get("validation_episodes", 200))
    config = _build_evaluation_config(row, trace_id=trace.trace_id, output_dir=job_dir)
    runner = EvaluationRunner(policy=policy, config=config, runtime_parameters=_build_environment_parameters(row), topology=TopologyGraph.from_approved_assumption_registry())
    result = runner.run()
    per_trace = result["per_trace"]
    task_rows: list[TaskRecord] = []
    for trace_metric in per_trace:
        for raw in trace_metric["raw_records"]:
            blueprint = trace_meta.get(int(raw["task_id"]))
            task_rows.append(
                TaskRecord(
                    campaign_id=row.campaign_id,
                    panel_id=row.panel_id,
                    job_id=row.job_id,
                    run_id=trace_metric["trace_id"],
                    policy=row.policy,
                    variant=row.variant,
                    seed=int(row.seed or 0),
                    trace_hash=registry.hash(),
                    task_id=str(raw["task_id"]),
                    source_agent=str(blueprint.source_agent_id if blueprint is not None else raw.get("arrival_slot")),
                    arrival_slot=int(raw["arrival_slot"]),
                    workload={"task_size": blueprint.size if blueprint is not None else None, "processing_density": blueprint.processing_density if blueprint is not None else None},
                    deadline=None,
                    decision_slot=int(raw["arrival_slot"]),
                    selected_action=str(raw.get("selected_action") or "local"),
                    destination=str(raw.get("resolved_destination") or "local"),
                    completion_or_drop_slot=raw.get("completion_slot"),
                    outcome=str(raw.get("terminal_outcome") or "completed"),
                    queue_delay=None,
                    transmission_delay=None,
                    service_delay=None,
                    end_to_end_delay=float(raw.get("delay")) if raw.get("delay") is not None else None,
                    reward=float(-(raw.get("delay") or 0)),
                    learner_owner=row.policy,
                    config_hash=row.config_hash,
                    source_hash=row.source_contract_hash,
                    checkpoint_hash=checkpoint_state and _hash(checkpoint_state) or "",
                )
            )
    agg = aggregate_records(task_rows)
    task_hash = _write_csv(job_dir / "task_records.csv", [asdict(row) for row in task_rows])
    decision_hash = _write_csv(job_dir / "decision_records.csv", [])
    eval_hash = _write_csv(job_dir / "evaluation_metrics.csv", [{"trace_id": trace_metric["trace_id"], "average_delay": trace_metric["average_delay"], "drop_ratio": trace_metric["drop_ratio"], "throughput": trace_metric["throughput"]} for trace_metric in per_trace])
    _ensure_schema(job_dir / "task_records.schema.json", [asdict(row) for row in task_rows])
    _ensure_schema(job_dir / "decision_records.schema.json", [])
    _ensure_schema(job_dir / "evaluation_metrics.schema.json", [{"trace_id": "", "average_delay": 0, "drop_ratio": 0, "throughput": 0}])
    provenance = build_provenance_manifest(
        source_commit=source_commit,
        source_contract_hash=row.source_contract_hash,
        panel_contract_hash=_hash(_panel_contract(row.panel_id)),
        job_spec_hash=_hash(asdict(row)),
        topology_hash=_hash(row.topology_contract),
        physical_hash=_hash(row.physical_contract),
        workload_hash=_hash(row.workload_contract),
        training_hash="",
        evaluation_hash=eval_hash,
        trace_hash=registry.hash(),
        checkpoint_hash=_hash(checkpoint_state or {}),
        dataset_hashes=(task_hash, eval_hash),
    )
    _write_json(job_dir / "provenance.json", {"manifest": asdict(provenance), "hash": provenance_hash(provenance)})
    _write_json(job_dir / "aggregate.json", asdict(agg))
    _write_json(job_dir / "status.json", {
        **_job_status_payload(
            campaign_id=row.campaign_id,
            row=row,
            status="completed",
            source_commit=source_commit,
            checkpoint_hash=_state_hash(checkpoint_state or {}),
            trace_hash=registry.hash(),
            dataset_hashes={"task_records": task_hash, "evaluation_metrics": eval_hash},
            completed_at=time.time(),
        ),
        "completion_marker": True,
    })
    return JobExecutionResult(job_id=row.job_id, job_type=row.job_type, status="completed", output_dir=job_dir, trace_hash=registry.hash(), dataset_hashes=(task_hash, eval_hash), metrics=result)


def _job_ids_in_order(rows: list[ProductionJobRow]) -> list[str]:
    return [row.job_id for row in rows]


def _resume_target_rows(rows: list[ProductionJobRow], job_id: str | None = None) -> list[ProductionJobRow]:
    if job_id is None:
        return rows
    matches = [row for row in rows if row.job_id == job_id]
    if not matches:
        raise ValueError(f"unknown job_id: {job_id}")
    return matches


def _load_checkpoint_state(campaign_dir: Path) -> dict[str, Any] | None:
    checkpoint_registry = campaign_dir / "checkpoint_registry.json"
    checkpoint_paths: list[Path] = []
    if checkpoint_registry.exists():
        registry = json.loads(checkpoint_registry.read_text(encoding="utf-8"))
        checkpoints = registry.get("checkpoints", [])
        checkpoint_paths.extend(Path(item["checkpoint_path"]) for item in checkpoints if item.get("checkpoint_path"))
    if not checkpoint_paths:
        checkpoint_paths.extend(sorted((campaign_dir / "checkpoints").glob("*/model.pt")))
    if not checkpoint_paths:
        return None
    checkpoint_path = checkpoint_paths[-1]
    return torch.load(checkpoint_path, map_location="cpu", weights_only=False)


def _update_campaign_registry(campaign_dir: Path, rows: list[ProductionJobRow], results: list[JobExecutionResult], source_commit: str) -> None:
    _write_json(campaign_dir / "campaign_specification.json", {"campaign_id": campaign_dir.name, "source_commit": source_commit, "expanded_job_count": len(rows), "training_jobs": sum(1 for row in rows if row.job_type == "training"), "evaluation_jobs": sum(1 for row in rows if row.job_type == "evaluation")})
    _write_json(campaign_dir / "source_contract_snapshot.json", _source_contract_snapshot())
    _write_json(campaign_dir / "job_plan.json", [asdict(row) for row in rows])
    _write_json(campaign_dir / "environment_manifest.json", {"python": platform.python_version(), "platform": platform.platform()})
    source_contract_snapshot = _source_contract_snapshot()
    _write_json(campaign_dir / "source_manifest.json", {"source_commit": source_commit, "source_contract_hash": source_contract_snapshot["source_hash"]})
    _write_json(campaign_dir / "trace_registry.json", {"trace_banks": sorted({row.trace_bank_id for row in rows}), "trace_hashes": sorted({result.trace_hash for result in results if result.trace_hash})})
    checkpoint_paths = sorted((campaign_dir / "checkpoints").glob("*/model.pt"))
    _write_json(campaign_dir / "checkpoint_registry.json", {"checkpoints": [{"checkpoint_id": path.parent.name, "checkpoint_path": str(path)} for path in checkpoint_paths]})
    _write_json(campaign_dir / "status.json", {"campaign_id": campaign_dir.name, "total_jobs": len(rows), "completed_jobs": sum(1 for result in results if result.status == "completed"), "pending_jobs": 0, "running_jobs": 0, "failed_jobs": 0, "corrupt_jobs": 0, "stale_jobs": 0, "quarantined_jobs": 0, "blocked_dependency_jobs": 0})


def run_production_campaign(*, campaign_id: str, output_dir: Path | None = None, max_jobs: int | None = None, max_runtime_seconds: float | None = None, job_id: str | None = None, allow_paused_recovery: bool = False) -> dict[str, Any]:
    rows = _read_matrix()
    _validate_matrix(rows)
    pause_request = (Path('artifacts/hoodie/campaigns') / campaign_id / 'pause.request')
    if allow_paused_recovery and not pause_request.exists():
        raise ValueError("allow_paused_recovery requires active pause.request")
    rows = _resume_target_rows(rows, job_id=job_id)
    _write_contract_audits(rows, (_CAMPAIGNS_ROOT if output_dir is None else output_dir) / (campaign_id if campaign_id.startswith("figures-8-11-") else _load_campaign_id(rows)))
    source_commit = _source_commit()
    actual_campaign_id = campaign_id if campaign_id.startswith("figures-8-11-") else _load_campaign_id(rows)
    campaign_dir = (_CAMPAIGNS_ROOT if output_dir is None else output_dir) / actual_campaign_id
    campaign_dir.mkdir(parents=True, exist_ok=True)
    results: list[JobExecutionResult] = []
    checkpoint_state: dict[str, Any] | None = None
    start_time = time.time()
    for row in rows:
        if max_jobs is not None and len(results) >= max_jobs:
            break
        if max_runtime_seconds is not None and (time.time() - start_time) >= max_runtime_seconds:
            break
        job_dir = campaign_dir / "jobs" / row.job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        status = classify_job_state(job_dir)
        if status.value == "completed" and (job_dir / "completion.marker").exists():
            continue
        try:
            _write_json(job_dir / "status.json", _job_status_payload(campaign_id=actual_campaign_id, row=row, status="running", source_commit=source_commit, started_at=time.time()))
            if row.job_type == "training":
                result = _run_training_job(row, job_dir, source_commit=source_commit, max_runtime_seconds=max_runtime_seconds)
            else:
                if checkpoint_state is None:
                    checkpoint_state = _load_checkpoint_state(campaign_dir)
                result = _run_evaluation_job(row, job_dir, source_commit=source_commit, checkpoint_state=checkpoint_state)
            results.append(result)
            _write_completion_marker(job_dir)
        except Exception as exc:  # pragma: no cover - exercised in runtime not unit tests
            _write_json(job_dir / "status.json", _job_status_payload(campaign_id=actual_campaign_id, row=row, status="failed", source_commit=source_commit, started_at=time.time(), failure_type=exc.__class__.__name__, failure_message=str(exc), failure_traceback=traceback.format_exc()))
            continue
    _update_campaign_registry(campaign_dir, rows, results, source_commit)
    return {"campaign_id": actual_campaign_id, "total_jobs": len(rows), "completed_jobs": len(results), "source_commit": source_commit, "max_jobs": max_jobs, "max_runtime_seconds": max_runtime_seconds}


def campaign_status(campaign_id: str, output_dir: Path | None = None) -> dict[str, Any]:
    campaign_dir = (_CAMPAIGNS_ROOT if output_dir is None else output_dir) / campaign_id
    rows = _read_matrix()
    counts = {key: 0 for key in ("pending", "running", "completed", "failed", "stale", "corrupt", "quarantined", "blocked_dependency", "scientifically_incomplete")}
    job_root = campaign_dir / "jobs"
    for row in rows:
        job_dir = job_root / row.job_id
        if not job_dir.exists():
            if row.checkpoint_dependency and row.job_type == "evaluation":
                counts["blocked_dependency"] += 1
            else:
                counts["pending"] += 1
            continue
        state = classify_job_state(job_dir).value
        counts[state] = counts.get(state, 0) + 1
    total = len(rows)
    return {"campaign_id": campaign_id, "total": total, **{f"{key}_jobs": value for key, value in counts.items()}}


def resume_production_campaign(campaign_id: str, output_dir: Path | None = None, *, max_jobs: int | None = None, max_runtime_seconds: float | None = None, job_id: str | None = None, allow_paused_recovery: bool = False) -> dict[str, Any]:
    return run_production_campaign(campaign_id=campaign_id, output_dir=output_dir, max_jobs=max_jobs, max_runtime_seconds=max_runtime_seconds, job_id=job_id, allow_paused_recovery=allow_paused_recovery)
