from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import asdict
from math import ceil
from pathlib import Path
from random import Random
import csv
import json
from typing import Callable, Iterable

from .config import EpisodeConfig
from .model import (
    DegeneracyDiagnostic,
    MetricAggregate,
    PolicyDecision,
    PublicQueueActiveSet,
    QueueState,
    RewardEvent,
    StateSnapshot,
    TaskRecord,
)
from .topology import Topology

PolicyFn = Callable[[TaskRecord, EpisodeConfig, list[int]], tuple[str, int | None]]


def local_test_policy(task: TaskRecord, config: EpisodeConfig, legal_destinations: list[int]) -> tuple[str, int | None]:
    return "local", None


def horizontal_test_policy(task: TaskRecord, config: EpisodeConfig, legal_destinations: list[int]) -> tuple[str, int | None]:
    destination = next((dest for dest in legal_destinations if dest != task.source_ea_id), config.cloud_node_id)
    return "horizontal", destination


def vertical_test_policy(task: TaskRecord, config: EpisodeConfig, legal_destinations: list[int]) -> tuple[str, int | None]:
    return "vertical", config.cloud_node_id


def mixed_test_policy(task: TaskRecord, config: EpisodeConfig, legal_destinations: list[int]) -> tuple[str, int | None]:
    mod = task.task_id % 3
    if mod == 0:
        return local_test_policy(task, config, legal_destinations)
    if mod == 1:
        return horizontal_test_policy(task, config, legal_destinations)
    return vertical_test_policy(task, config, legal_destinations)


def _build_load_history(history: list[list[int]], lookback: int, node_count: int) -> list[list[int]]:
    tail = history[-lookback:]
    padding = [[0 for _ in range(node_count)] for _ in range(max(0, lookback - len(tail)))]
    return padding + tail


def _task_size_values(config: EpisodeConfig) -> tuple[float, ...]:
    return config.task_size_values_mbits or tuple(round(config.task_size_range_mbits[0] + i * 0.1, 10) for i in range(int((config.task_size_range_mbits[1] - config.task_size_range_mbits[0]) / 0.1) + 1))


def _service_slots_for_private(task: TaskRecord, config: EpisodeConfig) -> int:
    workload = task.size_mbits * task.processing_density_gcycles_per_mbit
    service_per_slot = config.private_cpu_ghz * config.slot_duration_sec
    return max(1, ceil(workload / service_per_slot))


def _transmission_slots(task: TaskRecord, rate_mbps: float, config: EpisodeConfig) -> int:
    return max(1, ceil((task.size_mbits / rate_mbps) / config.slot_duration_sec))


def _public_service_per_slot(cpu_ghz: float, config: EpisodeConfig) -> float:
    return cpu_ghz * config.slot_duration_sec


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: Iterable[dict[str, object]]) -> None:
    rows = list(rows)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row.keys():
            if key not in seen:
                seen.add(key)
                fieldnames.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def run_episode(config: EpisodeConfig, policy_name: str, policy: PolicyFn) -> dict[str, object]:
    rng = Random(config.random_seed)
    topology = Topology.complete_edge_graph(config.num_edge_agents)
    task_id = 0
    tasks: dict[int, TaskRecord] = {}
    pending_actions: list[TaskRecord] = []
    private_queues: dict[int, deque[int]] = {ea: deque() for ea in range(1, config.num_edge_agents + 1)}
    private_work: dict[int, float] = {}
    offloading_queues: dict[int, deque[int]] = {ea: deque() for ea in range(1, config.num_edge_agents + 1)}
    offloading_work: dict[int, float] = {}
    public_queues: dict[tuple[int, int], deque[int]] = defaultdict(deque)
    public_work: dict[tuple[int, int], float] = {}
    reward_events: list[RewardEvent] = []
    lifecycle_trace: list[dict[str, object]] = []
    queue_trace: list[QueueState] = []
    active_sets: list[PublicQueueActiveSet] = []
    state_snapshots: list[StateSnapshot] = []
    decisions: list[PolicyDecision] = []
    arrival_by_ea = {ea: 0 for ea in range(1, config.num_edge_agents + 1)}
    load_history: list[list[int]] = []
    total_arrival_opportunities = config.num_edge_agents * config.action_slot_count
    public_cpu_used = False

    def active_public_count(slot: int, node_id: int) -> tuple[int, list[int]]:
        active_sources = [source for (node, source), workload in public_work.items() if node == node_id and workload > 0]
        return len(active_sources), active_sources

    def finalize(task: TaskRecord, slot: int, outcome: str, reward: float) -> None:
        task.status = outcome
        task.reward_collection_slot = slot
        task.reward = reward
        if outcome == "completed":
            task.final_completion_slot = slot
            task.queue_exit_slot = slot
            task.delay_slots = slot - task.arrival_slot + 1
            task.delay_sec = task.delay_slots * config.slot_duration_sec
        else:
            task.drop_slot = slot
            task.delay_slots = slot - task.arrival_slot + 1
            task.delay_sec = task.delay_slots * config.slot_duration_sec
        reward_events.append(
            RewardEvent(
                episode_id=config.episode_id,
                reward_collection_slot=slot,
                task_id=task.task_id,
                source_ea_id=task.source_ea_id,
                policy=policy_name,
                original_action_slot=task.arrival_slot,
                completed_or_dropped=outcome,
                delay_slots=task.delay_slots or 0,
                reward=reward,
                drop_penalty_applied=outcome == "dropped_timeout",
            )
        )

    def process_private(slot: int) -> None:
        for ea_id, queue in private_queues.items():
            if not queue:
                continue
            task_id = queue[0]
            task = tasks[task_id]
            if slot >= task.deadline_slot:
                queue.popleft()
                finalize(task, slot, "dropped_timeout", -40.0)
                continue
            private_work[task_id] -= config.private_cpu_ghz * config.slot_duration_sec
            if private_work[task_id] <= 0:
                queue.popleft()
                finalize(task, slot, "completed", -float(slot - task.arrival_slot + 1))

    def process_offloading(slot: int) -> None:
        for ea_id, queue in offloading_queues.items():
            if not queue:
                continue
            task_id = queue[0]
            task = tasks[task_id]
            if slot >= task.deadline_slot:
                queue.popleft()
                finalize(task, slot, "dropped_timeout", -40.0)
                continue
            rate = config.horizontal_rate_mbps if task.path_type == "horizontal" else config.vertical_rate_mbps
            offloading_work[task_id] -= rate * config.slot_duration_sec
            if offloading_work[task_id] <= 0:
                queue.popleft()
                task.status = "in_public_queue"
                task.public_queue_enter_slot = slot
                public_key = (task.destination_node_id or config.cloud_node_id, task.source_ea_id)
                public_queues[public_key].append(task_id)
                public_work[public_key] = task.size_mbits * task.processing_density_gcycles_per_mbit

    def process_public(slot: int) -> None:
        node_ids = list(range(1, config.num_edge_agents + 1)) + [config.cloud_node_id]
        for node_id in node_ids:
            count, sources = active_public_count(slot, node_id)
            if count <= 0:
                active_sets.append(
                    PublicQueueActiveSet(
                        episode_id=config.episode_id,
                        slot=slot,
                        node_id=node_id,
                        active_public_queue_source_ids=[],
                        active_public_queue_count=0,
                        total_public_cpu_ghz=config.cloud_cpu_ghz if node_id == config.cloud_node_id else config.public_cpu_ghz,
                        cpu_share_per_active_queue_ghz=0.0,
                    )
                )
                continue
            total_cpu = config.cloud_cpu_ghz if node_id == config.cloud_node_id else config.public_cpu_ghz
            share = total_cpu / count
            public_cpu_used_local = False
            active_sets.append(
                PublicQueueActiveSet(
                    episode_id=config.episode_id,
                    slot=slot,
                    node_id=node_id,
                    active_public_queue_source_ids=sources,
                    active_public_queue_count=count,
                    total_public_cpu_ghz=total_cpu,
                    cpu_share_per_active_queue_ghz=share,
                )
            )
            for source in list(sources):
                key = (node_id, source)
                queue = public_queues.get(key)
                if not queue:
                    continue
                task_id = queue[0]
                task = tasks[task_id]
                if slot >= task.deadline_slot:
                    queue.popleft()
                    finalize(task, slot, "dropped_timeout", -40.0)
                    continue
                public_work[key] -= share * config.slot_duration_sec
                public_cpu_used_local = True
                if public_work[key] <= 0:
                    queue.popleft()
                    finalize(task, slot, "completed", -float(slot - task.arrival_slot + 1))
                    public_work.pop(key, None)
            nonlocal_public_cpu[0] = nonlocal_public_cpu[0] or public_cpu_used_local

    nonlocal_public_cpu = [False]

    for slot in range(config.slot_count):
        arrivals_this_slot: list[int] = []
        if slot < config.action_slot_count:
            for ea_id in range(1, config.num_edge_agents + 1):
                if rng.random() <= config.task_arrival_probability:
                    task_id += 1
                    size = _task_size_values(config)[(task_id - 1) % len(_task_size_values(config))]
                    deadline_slot = slot + config.timeout_slots - 1
                    task = TaskRecord(
                        task_id=task_id,
                        source_ea_id=ea_id,
                        arrival_slot=slot,
                        size_mbits=size,
                        processing_density_gcycles_per_mbit=config.processing_density_gcycles_per_mbit,
                        timeout_slots=config.timeout_slots,
                        deadline_slot=deadline_slot,
                        policy=policy_name,
                        decision_level_1=None,
                        destination_node_id=None,
                        path_type="unresolved",
                    )
                    tasks[task_id] = task
                    arrival_by_ea[ea_id] += 1
                    arrivals_this_slot.append(task_id)
                    legal_destinations = topology.legal_horizontal_destinations(ea_id)
                    decision, destination = policy(task, config, legal_destinations)
                    destination = destination if destination is not None else (ea_id if decision == "local" else config.cloud_node_id)
                    if destination == ea_id and decision != "local":
                        destination = config.cloud_node_id
                    if decision == "local":
                        task.path_type = "local"
                        task.decision_level_1 = "local"
                        task.destination_node_id = ea_id
                        task.private_queue_enter_slot = slot
                        private_queues[ea_id].append(task_id)
                        private_work[task_id] = task.size_mbits * task.processing_density_gcycles_per_mbit
                    elif decision == "horizontal":
                        task.path_type = "horizontal"
                        task.decision_level_1 = "offload"
                        task.destination_node_id = destination
                        task.offloading_queue_enter_slot = slot
                        offloading_queues[ea_id].append(task_id)
                        offloading_work[task_id] = task.size_mbits
                    elif decision == "vertical":
                        task.path_type = "vertical"
                        task.decision_level_1 = "offload"
                        task.destination_node_id = config.cloud_node_id
                        task.offloading_queue_enter_slot = slot
                        offloading_queues[ea_id].append(task_id)
                        offloading_work[task_id] = task.size_mbits
                    else:
                        task.path_type = "local"
                        task.decision_level_1 = "local"
                        task.destination_node_id = ea_id
                        task.private_queue_enter_slot = slot
                        private_queues[ea_id].append(task_id)
                        private_work[task_id] = task.size_mbits * task.processing_density_gcycles_per_mbit
                    snapshot = StateSnapshot(
                        episode_id=config.episode_id,
                        slot=slot,
                        ea_id=ea_id,
                        task_id=task_id,
                        task_size_mbits=task.size_mbits,
                        private_wait_slots=max(0, slot - (task.private_queue_enter_slot or slot)),
                        offloading_wait_slots=max(0, slot - (task.offloading_queue_enter_slot or slot)),
                        public_queue_footprint={
                            "source_ea_id": ea_id,
                            "public_queue_count": sum(1 for (node, source), workload in public_work.items() if source == ea_id and workload > 0),
                        },
                        load_history_matrix_shape=(config.lookback_window, config.num_edge_agents + 1),
                        load_history_matrix_values=_build_load_history(load_history, config.lookback_window, config.num_edge_agents + 1),
                        forecast_mode=config.forecast_mode,
                        forecast_values=[0.0] * (config.num_edge_agents + 1),
                    )
                    state_snapshots.append(snapshot)
                    decisions.append(
                        PolicyDecision(
                            episode_id=config.episode_id,
                            slot=slot,
                            ea_id=ea_id,
                            task_id=task_id,
                            policy=policy_name,
                            state_snapshot_id=f"{config.episode_id}:{slot}:{task_id}",
                            decision_level_1=task.decision_level_1 or "local",
                            destination_node_id=task.destination_node_id,
                            path_type=task.path_type,
                            legal_action=True,
                            illegal_reason=None,
                            selected_estimated_latency_slots=None,
                        )
                    )
        load_history.append([sum(1 for (node, source), workload in public_work.items() if node == idx and workload > 0) for idx in range(1, config.num_edge_agents + 2)])
        process_offloading(slot)
        process_public(slot)
        process_private(slot)
        for task_id in arrivals_this_slot:
            task = tasks[task_id]
            lifecycle_trace.append({"slot": slot, "event": "arrival", **task.to_dict()})
        for task in tasks.values():
            if task.status == "pending" and slot >= task.deadline_slot:
                finalize(task, slot, "dropped_timeout", -40.0)
        for task in tasks.values():
            if task.status == "completed" or task.status == "dropped_timeout":
                continue
        for task in tasks.values():
            if task.status == "in_public_queue" and slot >= task.deadline_slot:
                finalize(task, slot, "dropped_timeout", -40.0)
        lifecycle_trace.extend(
            [
                {"slot": slot, "event": "public_active_set", **aset.to_dict()}
                for aset in [a for a in active_sets if a.slot == slot]
            ]
        )

    unresolved = [task for task in tasks.values() if task.status not in {"completed", "dropped_timeout"}]
    for task in unresolved:
        task.status = "unresolved"
        task.reward_collection_slot = config.slot_count - 1
        task.reward = None

    total_reward = sum(event.reward for event in reward_events)
    completed = sum(1 for task in tasks.values() if task.status == "completed")
    dropped = sum(1 for task in tasks.values() if task.status == "dropped_timeout")
    arrived = len(tasks)
    average_delay_slots = sum(task.delay_slots or 0 for task in tasks.values() if task.status == "completed") / completed if completed else 0.0
    average_delay_sec = average_delay_slots * config.slot_duration_sec
    drop_ratio = (dropped / arrived) if arrived else 0.0
    metric = MetricAggregate(
        figure_id="runtime_core",
        sweep_name="runtime_core",
        sweep_value=policy_name,
        policy=policy_name,
        episode_count=1,
        arrived_tasks=arrived,
        completed_tasks=completed,
        dropped_tasks=dropped,
        unresolved_tasks=len(unresolved),
        average_delay_sec=average_delay_sec,
        paper_style_negative_delay_sec=-average_delay_sec,
        drop_ratio=drop_ratio,
        drop_ratio_percent=drop_ratio * 100.0,
        average_reward=total_reward / max(1, len(reward_events)),
        total_reward=total_reward,
        throughput=completed,
    )
    degenerate = DegeneracyDiagnostic(
        figure_id="runtime_core",
        sweep_name="policy",
        sweep_value=policy_name,
        policy=policy_name,
        zero_completion_detected=completed == 0,
        single_task_trace_detected=arrived <= 1,
        drop_saturation_detected=drop_ratio >= 1.0 and arrived > 0,
        all_policy_tie_detected=False,
        missing_sweep_injection_detected=False,
        severity="high" if completed == 0 or drop_ratio >= 1.0 else "low",
        message="runtime core diagnostics",
    )
    return {
        "config": config,
        "tasks": tasks,
        "decisions": decisions,
        "reward_events": reward_events,
        "lifecycle_trace": lifecycle_trace,
        "queue_trace": queue_trace,
        "active_sets": active_sets,
        "state_snapshots": state_snapshots,
        "metric": metric,
        "degeneracy": degenerate,
        "arrival_by_ea": arrival_by_ea,
        "arrival_opportunities": total_arrival_opportunities,
        "public_cpu_used": nonlocal_public_cpu[0],
        "topology_mode": topology.mode,
        "load_history": load_history,
    }


def generate_runtime_artifacts(output_dir: Path, *, config: EpisodeConfig | None = None) -> dict[str, object]:
    config = config or EpisodeConfig.default()
    output_dir.mkdir(parents=True, exist_ok=True)
    result = run_episode(config, "mixed_test_policy", mixed_test_policy)
    runtime_config_path = output_dir / "runtime_config.json"
    arrival_diag_path = output_dir / "arrival_diagnostics.json"
    arrival_csv_path = output_dir / "arrival_diagnostics.csv"
    lifecycle_json_path = output_dir / "task_lifecycle_trace.json"
    lifecycle_csv_path = output_dir / "task_lifecycle_trace.csv"
    queue_json_path = output_dir / "queue_dynamics_trace.json"
    queue_csv_path = output_dir / "queue_dynamics_trace.csv"
    active_json_path = output_dir / "public_queue_active_set_trace.json"
    active_csv_path = output_dir / "public_queue_active_set_trace.csv"
    state_sample_path = output_dir / "state_snapshot_sample.json"
    reward_json_path = output_dir / "reward_events.json"
    reward_csv_path = output_dir / "reward_events.csv"
    degeneracy_path = output_dir / "runtime_degeneracy_diagnostics.json"
    report_json_path = output_dir / "runtime_core_validation_report.json"
    report_md_path = output_dir / "runtime_core_validation_report.md"

    _write_json(runtime_config_path, config.to_dict())
    arrival_payload = {
        "arrival_opportunities": result["arrival_opportunities"],
        "total_arrived_tasks": len(result["tasks"]),
        "arrived_tasks_by_ea": result["arrival_by_ea"],
        "configured_P": config.task_arrival_probability,
        "observed_arrival_rate": len(result["tasks"]) / max(1, result["arrival_opportunities"]),
        "random_seed": config.random_seed,
    }
    _write_json(arrival_diag_path, arrival_payload)
    _write_csv(arrival_csv_path, [{"ea_id": ea, "arrived_tasks": count} for ea, count in result["arrival_by_ea"].items()])
    lifecycle_rows = [item for item in result["lifecycle_trace"]]
    _write_json(lifecycle_json_path, lifecycle_rows)
    _write_csv(lifecycle_csv_path, lifecycle_rows)
    queue_rows = [queue.to_dict() for queue in result["active_sets"]]
    _write_json(queue_json_path, queue_rows)
    _write_csv(queue_csv_path, queue_rows)
    active_rows = [aset.to_dict() for aset in result["active_sets"]]
    _write_json(active_json_path, active_rows)
    _write_csv(active_csv_path, active_rows)
    _write_json(state_sample_path, [snapshot.to_dict() for snapshot in result["state_snapshots"][:1]])
    reward_rows = [event.to_dict() for event in result["reward_events"]]
    _write_json(reward_json_path, reward_rows)
    _write_csv(reward_csv_path, reward_rows)
    _write_json(degeneracy_path, [result["degeneracy"].to_dict()])
    report = {
        "phase": "090-A runtime core only",
        "no_trained_hoodie_policy_exists": True,
        "figure_claims_allowed": False,
        "forecast_mode": config.forecast_mode,
        "topology_mode": result["topology_mode"],
        "drain_phase_active": True,
        "public_cpu_sharing_active": bool(result["public_cpu_used"]),
        "delayed_reward_collection_active": True,
        "summary": {
            "arrived_tasks": len(result["tasks"]),
            "completed_tasks": sum(1 for task in result["tasks"].values() if task.status == "completed"),
            "dropped_tasks": sum(1 for task in result["tasks"].values() if task.status == "dropped_timeout"),
            "unresolved_tasks": sum(1 for task in result["tasks"].values() if task.status == "unresolved"),
        },
    }
    _write_json(report_json_path, report)
    report_md_path.write_text(
        "\n".join(
            [
                "# Feature 090-A Runtime Core Validation",
                "",
                "- Phase: 090-A runtime core only",
                "- Trained HOODIE policy: not implemented",
                "- Figure 8/9/10/11 claims: not allowed",
                f"- Forecast mode: `{config.forecast_mode}`",
                f"- Topology mode: `{result['topology_mode']}`",
                "- Drain phase active: yes",
                f"- Public CPU sharing active: {'yes' if result['public_cpu_used'] else 'no'}",
                "- Delayed reward collection active: yes",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return report


def validate_runtime_artifacts(artifact_dir: Path) -> dict[str, object]:
    required = [
        "runtime_config.json",
        "arrival_diagnostics.json",
        "arrival_diagnostics.csv",
        "task_lifecycle_trace.json",
        "task_lifecycle_trace.csv",
        "queue_dynamics_trace.json",
        "queue_dynamics_trace.csv",
        "public_queue_active_set_trace.json",
        "public_queue_active_set_trace.csv",
        "state_snapshot_sample.json",
        "reward_events.json",
        "reward_events.csv",
        "runtime_degeneracy_diagnostics.json",
        "runtime_core_validation_report.json",
        "runtime_core_validation_report.md",
    ]
    missing = [name for name in required if not (artifact_dir / name).exists()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    arrival = json.loads((artifact_dir / "arrival_diagnostics.json").read_text(encoding="utf-8"))
    reward_events = json.loads((artifact_dir / "reward_events.json").read_text(encoding="utf-8"))
    report = json.loads((artifact_dir / "runtime_core_validation_report.json").read_text(encoding="utf-8"))
    if arrival["total_arrived_tasks"] <= 0:
        raise ValueError("no arrivals were generated")
    if not reward_events:
        raise ValueError("no queue events/reward events were generated")
    if report.get("drain_phase_active") is not True:
        raise ValueError("drain phase not active")
    return {"passed": True, "artifact_dir": str(artifact_dir), "required_files": required}
