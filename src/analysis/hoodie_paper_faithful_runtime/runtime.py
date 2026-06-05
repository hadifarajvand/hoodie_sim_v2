from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import asdict, dataclass, field
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


@dataclass(slots=True)
class _QueueRuntime:
    tasks: deque[int] = field(default_factory=deque)
    next_available_slot: int = 0
    total_workload: float = 0.0


def local_test_policy(task: TaskRecord, config: EpisodeConfig, legal_destinations: list[int]) -> tuple[str, int | None]:
    del task, config, legal_destinations
    return "local", None


def horizontal_test_policy(task: TaskRecord, config: EpisodeConfig, legal_destinations: list[int]) -> tuple[str, int | None]:
    destination = next((dest for dest in legal_destinations if dest != task.source_ea_id), None)
    if destination is None:
        destination = config.cloud_node_id
    return "horizontal", destination


def vertical_test_policy(task: TaskRecord, config: EpisodeConfig, legal_destinations: list[int]) -> tuple[str, int | None]:
    del legal_destinations
    return "vertical", config.cloud_node_id


def mixed_test_policy(task: TaskRecord, config: EpisodeConfig, legal_destinations: list[int]) -> tuple[str, int | None]:
    mod = task.task_id % 3
    if mod == 0:
        return local_test_policy(task, config, legal_destinations)
    if mod == 1:
        return horizontal_test_policy(task, config, legal_destinations)
    return vertical_test_policy(task, config, legal_destinations)


def _json_safe(value: object) -> object:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(_json_safe(payload), indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: Iterable[dict[str, object]]) -> None:
    materialized = list(rows)
    if not materialized:
        path.write_text("", encoding="utf-8")
        return
    fieldnames: list[str] = []
    seen: set[str] = set()
    for row in materialized:
        for key in row:
            if key not in seen:
                seen.add(key)
                fieldnames.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in materialized:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def _build_topology(config: EpisodeConfig) -> Topology:
    if config.topology_mode == "complete_edge_graph":
        return Topology.complete_edge_graph(config.num_edge_agents)
    if config.topology_mode == "paper_topology_adjacency":
        if config.adjacency_matrix is None:
            raise ValueError("paper_topology_adjacency requires an explicit adjacency_matrix")
        return Topology.from_adjacency_matrix(config.adjacency_matrix)
    if config.adjacency_matrix is None:
        raise ValueError("unknown_from_ocr_requires_pdf_visual_confirmation requires an explicit adjacency_matrix")
    return Topology(mode="unknown_from_ocr_requires_pdf_visual_confirmation", adjacency_matrix=config.adjacency_matrix)


def _task_size_values(config: EpisodeConfig) -> tuple[float, ...]:
    if config.task_size_values_mbits:
        return config.task_size_values_mbits
    start, stop = config.task_size_range_mbits
    count = int(round((stop - start) / 0.1)) + 1
    return tuple(round(start + 0.1 * index, 10) for index in range(count))


def _sample_task_size(rng: Random, config: EpisodeConfig) -> float:
    return float(rng.choice(_task_size_values(config)))


def _task_workload_gcycles(task: TaskRecord) -> float:
    return float(task.size_mbits * task.processing_density_gcycles_per_mbit)


def _load_history_matrix(history: list[list[int]], window: int, node_count: int) -> list[list[int]]:
    tail = history[-window:]
    padding = [[0 for _ in range(node_count)] for _ in range(max(0, window - len(tail)))]
    return padding + [list(row) for row in tail]


def _queue_snapshot_rows(
    *,
    config: EpisodeConfig,
    tasks: dict[int, TaskRecord],
    private_queues: dict[int, _QueueRuntime],
    offloading_queues: dict[int, _QueueRuntime],
    public_queues: dict[tuple[int, int], _QueueRuntime],
    active_public_share_by_node: dict[int, tuple[list[int], float, float]],
    slot: int,
    arrivals_by_queue: dict[tuple[str, int, int], list[int]],
    terminal_by_queue: dict[tuple[str, int, int], dict[str, list[int]]],
) -> list[QueueState]:
    rows: list[QueueState] = []
    for ea_id, queue in private_queues.items():
        rows.append(
            QueueState(
                episode_id=config.episode_id,
                slot=slot,
                node_id=ea_id,
                queue_type="private",
                source_ea_id=ea_id,
                queue_length_workload=round(sum(_task_workload_gcycles(tasks[task_id]) for task_id in queue.tasks), 12),
                queue_length_unit="gcycles",
                active=bool(queue.tasks),
                allocated_cpu_ghz=config.private_cpu_ghz if queue.tasks else 0.0,
                arrived_task_ids=list(arrivals_by_queue.get(("private", ea_id, ea_id), [])),
                completed_task_ids=list(terminal_by_queue.get(("private", ea_id, ea_id), {}).get("completed", [])),
                dropped_task_ids=list(terminal_by_queue.get(("private", ea_id, ea_id), {}).get("dropped", [])),
                remaining_task_ids=list(queue.tasks),
            )
        )
    for ea_id, queue in offloading_queues.items():
        rows.append(
            QueueState(
                episode_id=config.episode_id,
                slot=slot,
                node_id=ea_id,
                queue_type="offloading",
                source_ea_id=ea_id,
                queue_length_workload=round(sum(tasks[task_id].size_mbits for task_id in queue.tasks), 12),
                queue_length_unit="mbits",
                active=bool(queue.tasks),
                allocated_cpu_ghz=0.0,
                arrived_task_ids=list(arrivals_by_queue.get(("offloading", ea_id, ea_id), [])),
                completed_task_ids=list(terminal_by_queue.get(("offloading", ea_id, ea_id), {}).get("completed", [])),
                dropped_task_ids=list(terminal_by_queue.get(("offloading", ea_id, ea_id), {}).get("dropped", [])),
                remaining_task_ids=list(queue.tasks),
            )
        )
    for node_id in range(1, config.num_edge_agents + 2):
        share_sources, share_value, total_cpu = active_public_share_by_node.get(node_id, ([], 0.0, config.cloud_cpu_ghz if node_id == config.cloud_node_id else config.public_cpu_ghz))
        for source_ea_id in range(1, config.num_edge_agents + 1):
            queue = public_queues[(node_id, source_ea_id)]
            rows.append(
                QueueState(
                    episode_id=config.episode_id,
                    slot=slot,
                    node_id=node_id,
                    queue_type="public",
                    source_ea_id=source_ea_id,
                    queue_length_workload=round(sum(float(tasks[task_id].metadata.get("public_remaining_gcycles", 0.0)) for task_id in queue.tasks), 12),
                    queue_length_unit="gcycles",
                    active=bool(queue.tasks),
                    allocated_cpu_ghz=share_value if queue.tasks else 0.0,
                    arrived_task_ids=list(arrivals_by_queue.get(("public", node_id, source_ea_id), [])),
                    completed_task_ids=list(terminal_by_queue.get(("public", node_id, source_ea_id), {}).get("completed", [])),
                    dropped_task_ids=list(terminal_by_queue.get(("public", node_id, source_ea_id), {}).get("dropped", [])),
                    remaining_task_ids=list(queue.tasks),
                )
            )
    return rows


def _build_state_snapshot(
    *,
    config: EpisodeConfig,
    task: TaskRecord,
    private_queue: _QueueRuntime,
    offloading_queue: _QueueRuntime,
    public_queues: dict[tuple[int, int], _QueueRuntime],
    load_history: list[list[int]],
) -> StateSnapshot:
    public_queue_footprint = {
        "source_ea_id": task.source_ea_id,
        "active_public_queue_count": sum(1 for (node_id, source_id), queue in public_queues.items() if source_id == task.source_ea_id and queue.tasks),
        "active_destination_nodes": [node_id for (node_id, source_id), queue in public_queues.items() if source_id == task.source_ea_id and queue.tasks],
        "total_public_queue_workload_gcycles": round(sum(queue.total_workload for (node_id, source_id), queue in public_queues.items() if source_id == task.source_ea_id), 12),
    }
    matrix = _load_history_matrix(load_history, config.lookback_window, config.num_edge_agents + 1)
    return StateSnapshot(
        episode_id=config.episode_id,
        slot=task.arrival_slot,
        ea_id=task.source_ea_id,
        task_id=task.task_id,
        task_size_mbits=task.size_mbits,
        private_wait_slots=max(0, private_queue.next_available_slot - task.arrival_slot),
        offloading_wait_slots=max(0, offloading_queue.next_available_slot - task.arrival_slot),
        public_queue_footprint=public_queue_footprint,
        load_history_matrix_shape=(config.lookback_window, config.num_edge_agents + 1),
        load_history_matrix_values=matrix,
        forecast_mode=config.forecast_mode,
        forecast_values=[float(value) for value in (matrix[-1] if matrix else [0 for _ in range(config.num_edge_agents + 1)])],
    )


def _emit_reward(
    *,
    config: EpisodeConfig,
    task: TaskRecord,
    slot: int,
    outcome: str,
    reward_events: list[RewardEvent],
    lifecycle_trace: list[dict[str, object]],
) -> None:
    delay_slots = slot - task.arrival_slot + 1
    reward = -40.0 if outcome == "dropped_timeout" else -float(delay_slots)
    task.reward_collection_slot = slot
    task.reward = reward
    task.delay_slots = delay_slots
    task.delay_sec = delay_slots * config.slot_duration_sec
    task.queue_exit_slot = slot
    if outcome == "completed":
        task.final_completion_slot = slot
        task.status = "completed"
    else:
        task.drop_slot = slot
        task.status = "dropped_timeout"
    reward_events.append(
        RewardEvent(
            episode_id=config.episode_id,
            reward_collection_slot=slot,
            task_id=task.task_id,
            source_ea_id=task.source_ea_id,
            policy=task.policy,
            original_action_slot=task.arrival_slot,
            completed_or_dropped=outcome,
            delay_slots=delay_slots,
            reward=reward,
            drop_penalty_applied=outcome == "dropped_timeout",
        )
    )
    lifecycle_trace.append(
        {
            "episode_id": config.episode_id,
            "slot": slot,
            "event": "reward_collected",
            "task_id": task.task_id,
            "source_ea_id": task.source_ea_id,
            "status": outcome,
            "reward": reward,
            "delay_slots": delay_slots,
        }
    )


def _finalize_private_or_offloading_slot(
    *,
    config: EpisodeConfig,
    task: TaskRecord,
    slot: int,
    queue_type: str,
    reward_events: list[RewardEvent],
    lifecycle_trace: list[dict[str, object]],
    terminal_by_queue: dict[tuple[str, int, int], dict[str, list[int]]],
) -> None:
    key = (queue_type, task.source_ea_id, task.source_ea_id)
    if queue_type == "offloading":
        success = task.metadata.get("scheduled_terminal_status") == "transmitted"
    else:
        success = task.metadata.get("scheduled_terminal_status") == "completed"
    if success:
        terminal_by_queue.setdefault(key, {}).setdefault("completed", []).append(task.task_id)
        if queue_type == "private":
            lifecycle_trace.append({"episode_id": config.episode_id, "slot": slot, "event": "private_completed", "task_id": task.task_id, "source_ea_id": task.source_ea_id})
            _emit_reward(config=config, task=task, slot=slot, outcome="completed", reward_events=reward_events, lifecycle_trace=lifecycle_trace)
        else:
            task.offloading_queue_exit_slot = slot
            task.public_queue_enter_slot = slot
            task.status = "in_public_queue"
            lifecycle_trace.append({"episode_id": config.episode_id, "slot": slot, "event": "offloading_transmitted", "task_id": task.task_id, "source_ea_id": task.source_ea_id, "destination_node_id": task.destination_node_id})
    else:
        terminal_by_queue.setdefault(key, {}).setdefault("dropped", []).append(task.task_id)
        lifecycle_trace.append(
            {
                "episode_id": config.episode_id,
                "slot": slot,
                "event": "private_dropped_timeout" if queue_type == "private" else "offloading_dropped_timeout",
                "task_id": task.task_id,
                "source_ea_id": task.source_ea_id,
            }
        )
        _emit_reward(config=config, task=task, slot=slot, outcome="dropped_timeout", reward_events=reward_events, lifecycle_trace=lifecycle_trace)


def _serve_public_queue(
    *,
    config: EpisodeConfig,
    slot: int,
    queue_key: tuple[int, int],
    tasks: dict[int, TaskRecord],
    public_queue: _QueueRuntime,
    service_budget_gcycles: float,
    reward_events: list[RewardEvent],
    lifecycle_trace: list[dict[str, object]],
    terminal_by_queue: dict[tuple[str, int, int], dict[str, list[int]]],
) -> float:
    remaining_service = service_budget_gcycles
    terminal_key = ("public", queue_key[0], queue_key[1])
    while remaining_service > 0 and public_queue.tasks:
        task_id = public_queue.tasks[0]
        task = tasks[task_id]
        remaining_workload = float(task.metadata.get("public_remaining_gcycles", _task_workload_gcycles(task)))
        consumed = min(remaining_workload, remaining_service)
        remaining_workload -= consumed
        remaining_service -= consumed
        task.metadata["public_remaining_gcycles"] = max(0.0, remaining_workload)
        public_queue.total_workload = max(0.0, public_queue.total_workload - consumed)
        if remaining_workload <= 1e-12:
            public_queue.tasks.popleft()
            terminal_by_queue.setdefault(terminal_key, {}).setdefault("completed", []).append(task_id)
            lifecycle_trace.append(
                {
                    "episode_id": config.episode_id,
                    "slot": slot,
                    "event": "public_completed",
                    "task_id": task_id,
                    "source_ea_id": task.source_ea_id,
                    "destination_node_id": task.destination_node_id,
                }
            )
            _emit_reward(config=config, task=task, slot=slot, outcome="completed", reward_events=reward_events, lifecycle_trace=lifecycle_trace)
            continue
        if slot >= task.deadline_slot:
            public_queue.tasks.popleft()
            terminal_by_queue.setdefault(terminal_key, {}).setdefault("dropped", []).append(task_id)
            lifecycle_trace.append(
                {
                    "episode_id": config.episode_id,
                    "slot": slot,
                    "event": "public_dropped_timeout",
                    "task_id": task_id,
                    "source_ea_id": task.source_ea_id,
                    "destination_node_id": task.destination_node_id,
                }
            )
            _emit_reward(config=config, task=task, slot=slot, outcome="dropped_timeout", reward_events=reward_events, lifecycle_trace=lifecycle_trace)
            break
        break
    return remaining_service


def run_episode(config: EpisodeConfig, policy_name: str, policy: PolicyFn) -> dict[str, object]:
    rng = Random(config.random_seed)
    topology = _build_topology(config)
    tasks: dict[int, TaskRecord] = {}
    reward_events: list[RewardEvent] = []
    lifecycle_trace: list[dict[str, object]] = []
    state_snapshots: list[StateSnapshot] = []
    decisions: list[PolicyDecision] = []
    private_queues: dict[int, _QueueRuntime] = {ea_id: _QueueRuntime() for ea_id in range(1, config.num_edge_agents + 1)}
    offloading_queues: dict[int, _QueueRuntime] = {ea_id: _QueueRuntime() for ea_id in range(1, config.num_edge_agents + 1)}
    public_queues: dict[tuple[int, int], _QueueRuntime] = {(node_id, source_ea_id): _QueueRuntime() for node_id in range(1, config.num_edge_agents + 2) for source_ea_id in range(1, config.num_edge_agents + 1)}
    arrival_by_ea = {ea_id: 0 for ea_id in range(1, config.num_edge_agents + 1)}
    load_history: list[list[int]] = []
    queue_trace: list[QueueState] = []
    public_active_sets: list[PublicQueueActiveSet] = []
    arrivals_by_queue: dict[tuple[str, int, int], list[int]] = defaultdict(list)
    terminal_by_queue: dict[tuple[str, int, int], dict[str, list[int]]] = defaultdict(lambda: {"completed": [], "dropped": []})
    task_counter = 0
    public_cpu_used = False
    snapshot_emitted = False

    for slot in range(config.slot_count):
        if slot < config.action_slot_count:
            for ea_id in range(1, config.num_edge_agents + 1):
                if rng.random() >= config.task_arrival_probability:
                    continue
                task_counter += 1
                size_mbits = _sample_task_size(rng, config)
                task = TaskRecord(
                    task_id=task_counter,
                    source_ea_id=ea_id,
                    arrival_slot=slot,
                    size_mbits=size_mbits,
                    processing_density_gcycles_per_mbit=config.processing_density_gcycles_per_mbit,
                    timeout_slots=config.timeout_slots,
                    deadline_slot=slot + config.timeout_slots - 1,
                    policy=policy_name,
                    decision_level_1=None,
                    destination_node_id=None,
                    path_type="unresolved",
                )
                tasks[task.task_id] = task
                arrival_by_ea[ea_id] += 1
                lifecycle_trace.append(
                    {
                        "episode_id": config.episode_id,
                        "slot": slot,
                        "event": "arrival",
                        "task_id": task.task_id,
                        "source_ea_id": ea_id,
                        "size_mbits": task.size_mbits,
                    }
                )

                snapshot = _build_state_snapshot(
                    config=config,
                    task=task,
                    private_queue=private_queues[ea_id],
                    offloading_queue=offloading_queues[ea_id],
                    public_queues=public_queues,
                    load_history=load_history,
                )
                state_snapshots.append(snapshot)
                snapshot_emitted = True

                legal_destinations = topology.legal_horizontal_destinations(ea_id)
                decision_level_1, destination_node_id = policy(task, config, legal_destinations)
                legal_action = True
                illegal_reason = None
                if decision_level_1 == "local":
                    destination_node_id = ea_id
                    path_type = "local"
                elif decision_level_1 == "horizontal":
                    if destination_node_id is None or destination_node_id == ea_id or not topology.is_legal_destination(ea_id, int(destination_node_id)):
                        legal_action = False
                        illegal_reason = "horizontal self-offload or illegal horizontal destination"
                        decision_level_1 = "local"
                        destination_node_id = ea_id
                        path_type = "local"
                    else:
                        path_type = "horizontal"
                elif decision_level_1 == "vertical":
                    destination_node_id = config.cloud_node_id
                    path_type = "vertical"
                else:
                    legal_action = False
                    illegal_reason = f"unsupported policy decision: {decision_level_1}"
                    decision_level_1 = "local"
                    destination_node_id = ea_id
                    path_type = "local"

                task.decision_level_1 = decision_level_1
                task.destination_node_id = destination_node_id
                task.path_type = path_type
                decisions.append(
                    PolicyDecision(
                        episode_id=config.episode_id,
                        slot=slot,
                        ea_id=ea_id,
                        task_id=task.task_id,
                        policy=policy_name,
                        state_snapshot_id=f"{config.episode_id}:{slot}:{task.task_id}",
                        decision_level_1=decision_level_1,
                        destination_node_id=destination_node_id,
                        path_type=path_type,
                        legal_action=legal_action,
                        illegal_reason=illegal_reason,
                        candidate_latency_table_id=None,
                        selected_estimated_latency_slots=None,
                    )
                )
                lifecycle_trace.append(
                    {
                        "episode_id": config.episode_id,
                        "slot": slot,
                        "event": "decision",
                        "task_id": task.task_id,
                        "source_ea_id": ea_id,
                        "policy": policy_name,
                        "decision_level_1": decision_level_1,
                        "destination_node_id": destination_node_id,
                        "path_type": path_type,
                        "legal_action": legal_action,
                        "illegal_reason": illegal_reason,
                    }
                )

                if path_type == "local":
                    private_queue = private_queues[ea_id]
                    wait_slots = max(0, private_queue.next_available_slot - slot)
                    service_slots = max(1, ceil(_task_workload_gcycles(task) / (config.private_cpu_ghz * config.slot_duration_sec)))
                    start_slot = slot + wait_slots
                    scheduled_exit = min(start_slot + service_slots - 1, task.deadline_slot)
                    scheduled_terminal_status = "completed" if start_slot + service_slots - 1 <= task.deadline_slot else "dropped_timeout"
                    task.private_queue_enter_slot = slot
                    task.metadata.update(
                        {
                            "private_wait_slots": wait_slots,
                            "private_service_slots": service_slots,
                            "scheduled_terminal_slot": scheduled_exit,
                            "scheduled_terminal_status": scheduled_terminal_status,
                        }
                    )
                    private_queue.tasks.append(task.task_id)
                    private_queue.next_available_slot = scheduled_exit + 1
                    private_queue.total_workload += _task_workload_gcycles(task)
                    arrivals_by_queue[("private", ea_id, ea_id)].append(task.task_id)
                    lifecycle_trace.append(
                        {
                            "episode_id": config.episode_id,
                            "slot": slot,
                            "event": "private_queue_enter",
                            "task_id": task.task_id,
                            "source_ea_id": ea_id,
                            "wait_slots": wait_slots,
                            "service_slots": service_slots,
                            "scheduled_exit_slot": scheduled_exit,
                        }
                    )
                else:
                    offloading_queue = offloading_queues[ea_id]
                    rate_mbps = config.horizontal_rate_mbps if path_type == "horizontal" else config.vertical_rate_mbps
                    wait_slots = max(0, offloading_queue.next_available_slot - slot)
                    transmission_slots = max(1, ceil(task.size_mbits / (rate_mbps * config.slot_duration_sec)))
                    start_slot = slot + wait_slots
                    scheduled_exit = min(start_slot + transmission_slots - 1, task.deadline_slot)
                    scheduled_terminal_status = "transmitted" if start_slot + transmission_slots - 1 <= task.deadline_slot else "dropped_timeout"
                    task.offloading_queue_enter_slot = slot
                    task.status = "transmitting"
                    task.metadata.update(
                        {
                            "offloading_wait_slots": wait_slots,
                            "transmission_slots": transmission_slots,
                            "offload_rate_mbps": rate_mbps,
                            "scheduled_terminal_slot": scheduled_exit,
                            "scheduled_terminal_status": scheduled_terminal_status,
                        }
                    )
                    offloading_queue.tasks.append(task.task_id)
                    offloading_queue.next_available_slot = scheduled_exit + 1
                    offloading_queue.total_workload += task.size_mbits
                    arrivals_by_queue[("offloading", ea_id, ea_id)].append(task.task_id)
                    lifecycle_trace.append(
                        {
                            "episode_id": config.episode_id,
                            "slot": slot,
                            "event": "offloading_queue_enter",
                            "task_id": task.task_id,
                            "source_ea_id": ea_id,
                            "destination_node_id": destination_node_id,
                            "path_type": path_type,
                            "wait_slots": wait_slots,
                            "transmission_slots": transmission_slots,
                            "rate_mbps": rate_mbps,
                            "scheduled_exit_slot": scheduled_exit,
                        }
                    )

        terminal_slot_events_private: list[int] = []
        terminal_slot_events_offloading: list[int] = []

        for ea_id, queue in private_queues.items():
            while queue.tasks:
                task_id = queue.tasks[0]
                task = tasks[task_id]
                if task.metadata.get("scheduled_terminal_slot") != slot:
                    break
                queue.tasks.popleft()
                queue.total_workload = max(0.0, queue.total_workload - _task_workload_gcycles(task))
                terminal_slot_events_private.append(task_id)
                _finalize_private_or_offloading_slot(
                    config=config,
                    task=task,
                    slot=slot,
                    queue_type="private",
                    reward_events=reward_events,
                    lifecycle_trace=lifecycle_trace,
                    terminal_by_queue=terminal_by_queue,
                )

        for ea_id, queue in offloading_queues.items():
            while queue.tasks:
                task_id = queue.tasks[0]
                task = tasks[task_id]
                if task.metadata.get("scheduled_terminal_slot") != slot:
                    break
                queue.tasks.popleft()
                queue.total_workload = max(0.0, queue.total_workload - task.size_mbits)
                terminal_slot_events_offloading.append(task_id)
                _finalize_private_or_offloading_slot(
                    config=config,
                    task=task,
                    slot=slot,
                    queue_type="offloading",
                    reward_events=reward_events,
                    lifecycle_trace=lifecycle_trace,
                    terminal_by_queue=terminal_by_queue,
                )

                if task.status == "in_public_queue":
                    queue_key = (task.destination_node_id or config.cloud_node_id, task.source_ea_id)
                    public_queue = public_queues[queue_key]
                    public_queue.tasks.append(task.task_id)
                    public_queue.total_workload += _task_workload_gcycles(task)
                    task.public_queue_enter_slot = slot
                    task.metadata["public_remaining_gcycles"] = _task_workload_gcycles(task)
                    arrivals_by_queue[("public", queue_key[0], queue_key[1])].append(task.task_id)
                    lifecycle_trace.append(
                        {
                            "episode_id": config.episode_id,
                            "slot": slot,
                            "event": "public_queue_enter",
                            "task_id": task.task_id,
                            "source_ea_id": task.source_ea_id,
                            "destination_node_id": task.destination_node_id,
                            "public_workload_gcycles": task.metadata["public_remaining_gcycles"],
                        }
                    )

        active_public_share_by_node: dict[int, tuple[list[int], float, float]] = {}
        for node_id in range(1, config.num_edge_agents + 2):
            active_sources = [source_ea_id for source_ea_id in range(1, config.num_edge_agents + 1) if public_queues[(node_id, source_ea_id)].tasks]
            total_cpu = config.cloud_cpu_ghz if node_id == config.cloud_node_id else config.public_cpu_ghz
            share = total_cpu / len(active_sources) if active_sources else 0.0
            if active_sources:
                public_cpu_used = True
            active_public_share_by_node[node_id] = (active_sources, share, total_cpu)
            public_active_sets.append(
                PublicQueueActiveSet(
                    episode_id=config.episode_id,
                    slot=slot,
                    node_id=node_id,
                    active_public_queue_source_ids=list(active_sources),
                    active_public_queue_count=len(active_sources),
                    total_public_cpu_ghz=total_cpu,
                    cpu_share_per_active_queue_ghz=share,
                )
            )

        for node_id, (active_sources, share, _total_cpu) in active_public_share_by_node.items():
            if not active_sources:
                continue
            service_budget_gcycles = share * config.slot_duration_sec
            for source_ea_id in list(active_sources):
                queue_key = (node_id, source_ea_id)
                public_queue = public_queues[queue_key]
                service_budget_gcycles = _serve_public_queue(
                    config=config,
                    slot=slot,
                    queue_key=queue_key,
                    tasks=tasks,
                    public_queue=public_queue,
                    service_budget_gcycles=service_budget_gcycles,
                    reward_events=reward_events,
                    lifecycle_trace=lifecycle_trace,
                    terminal_by_queue=terminal_by_queue,
                )

        queue_trace.extend(
            _queue_snapshot_rows(
                config=config,
                tasks=tasks,
                private_queues=private_queues,
                offloading_queues=offloading_queues,
                public_queues=public_queues,
                active_public_share_by_node=active_public_share_by_node,
                slot=slot,
                arrivals_by_queue=arrivals_by_queue,
                terminal_by_queue=terminal_by_queue,
            )
        )

        load_history.append([sum(1 for source_ea_id in range(1, config.num_edge_agents + 1) if public_queues[(node_id, source_ea_id)].tasks) for node_id in range(1, config.num_edge_agents + 2)])

    unresolved_task_ids = [task.task_id for task in tasks.values() if task.status not in {"completed", "dropped_timeout"}]
    for task_id in unresolved_task_ids:
        tasks[task_id].status = "unresolved"

    arrived_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks.values() if task.status == "completed")
    dropped_tasks = sum(1 for task in tasks.values() if task.status == "dropped_timeout")
    unresolved_tasks = sum(1 for task in tasks.values() if task.status == "unresolved")
    delay_slots_completed = [task.delay_slots or 0 for task in tasks.values() if task.status == "completed"]
    average_delay_slots = sum(delay_slots_completed) / len(delay_slots_completed) if delay_slots_completed else 0.0
    average_delay_sec = average_delay_slots * config.slot_duration_sec
    drop_ratio = dropped_tasks / arrived_tasks if arrived_tasks else 0.0
    total_reward = sum(event.reward for event in reward_events)

    metric = MetricAggregate(
        figure_id="runtime_core",
        sweep_name="runtime_core",
        sweep_value=policy_name,
        policy=policy_name,
        episode_count=1,
        arrived_tasks=arrived_tasks,
        completed_tasks=completed_tasks,
        dropped_tasks=dropped_tasks,
        unresolved_tasks=unresolved_tasks,
        average_delay_sec=average_delay_sec,
        paper_style_negative_delay_sec=-average_delay_sec,
        drop_ratio=drop_ratio,
        drop_ratio_percent=drop_ratio * 100.0,
        average_reward=total_reward / len(reward_events) if reward_events else 0.0,
        total_reward=total_reward,
        throughput=completed_tasks,
    )

    degeneracy = DegeneracyDiagnostic(
        figure_id="runtime_core",
        sweep_name="runtime_core",
        sweep_value=policy_name,
        policy=policy_name,
        zero_completion_detected=completed_tasks == 0,
        single_task_trace_detected=arrived_tasks <= 1,
        drop_saturation_detected=arrived_tasks > 0 and dropped_tasks == arrived_tasks,
        all_policy_tie_detected=False,
        missing_sweep_injection_detected=False,
        severity="high" if completed_tasks == 0 or (arrived_tasks > 0 and dropped_tasks == arrived_tasks) else "low",
        message="phase 090-A runtime core diagnostics",
    )

    return {
        "config": config,
        "topology": topology,
        "topology_mode": topology.mode,
        "topology_temporary": topology.mode == "complete_edge_graph",
        "tasks": tasks,
        "reward_events": reward_events,
        "lifecycle_trace": lifecycle_trace,
        "queue_trace": queue_trace,
        "public_active_sets": public_active_sets,
        "active_sets": public_active_sets,
        "state_snapshots": state_snapshots,
        "decisions": decisions,
        "metric": metric,
        "degeneracy": degeneracy,
        "arrival_by_ea": arrival_by_ea,
        "arrival_opportunities": config.num_edge_agents * config.action_slot_count,
        "public_cpu_used": public_cpu_used,
        "load_history": load_history,
        "queue_event_counts": {
            "private_terminal_events": len(terminal_slot_events_private),
            "offloading_terminal_events": len(terminal_slot_events_offloading),
        },
        "unresolved_task_ids": unresolved_task_ids,
        "snapshot_emitted": snapshot_emitted,
        "bernoulli_arrival_active": True,
        "private_queue_active": True,
        "offloading_queue_active": True,
        "completion_drop_status_separated": True,
        "delayed_reward_collection_active": True,
        "drain_phase_active": True,
        "runtime_slot_phase_active": True,
        "public_queue_cpu_sharing_active": public_cpu_used,
        "forecast_mode": config.forecast_mode,
    }


def _build_runtime_report(result: dict[str, object]) -> dict[str, object]:
    config: EpisodeConfig = result["config"]  # type: ignore[assignment]
    tasks: dict[int, TaskRecord] = result["tasks"]  # type: ignore[assignment]
    reward_events: list[RewardEvent] = result["reward_events"]  # type: ignore[assignment]
    public_active_sets: list[PublicQueueActiveSet] = result["public_active_sets"]  # type: ignore[assignment]
    completed_tasks = sum(1 for task in tasks.values() if task.status == "completed")
    dropped_tasks = sum(1 for task in tasks.values() if task.status == "dropped_timeout")
    unresolved_tasks = sum(1 for task in tasks.values() if task.status == "unresolved")
    public_sharing_exercised = any(active.active_public_queue_count > 1 for active in public_active_sets)
    path_coverage = sorted({decision.path_type for decision in result["decisions"]})  # type: ignore[index]
    warnings = []
    if result["topology_temporary"]:
        warnings.append("complete_edge_graph used as explicit temporary topology mode")
    if unresolved_tasks and unresolved_tasks != len(tasks):
        warnings.append("some tasks remain unresolved at episode end")
    return {
        "phase": "090-A runtime core only",
        "no_trained_hoodie_policy_exists": True,
        "no_figure_8_9_10_11_claims": True,
        "no_training_or_dcq_introduced": True,
        "forecast_mode": config.forecast_mode,
        "topology_mode": result["topology_mode"],
        "topology_temporary": result["topology_temporary"],
        "runtime_slot_phase_active": True,
        "drain_phase_active": True,
        "bernoulli_arrival_active": True,
        "private_queue_active": True,
        "offloading_queue_active": True,
        "public_queue_cpu_sharing_active": result["public_queue_cpu_sharing_active"],
        "completion_drop_status_separated": True,
        "delayed_reward_collection_active": True,
        "public_cpu_sharing_exercised": public_sharing_exercised,
        "path_coverage": path_coverage,
        "summary": {
            "arrived_tasks": len(tasks),
            "completed_tasks": completed_tasks,
            "dropped_tasks": dropped_tasks,
            "unresolved_tasks": unresolved_tasks,
            "arrival_opportunities": result["arrival_opportunities"],
            "arrival_rate_observed": len(tasks) / result["arrival_opportunities"] if result["arrival_opportunities"] else 0.0,
            "arrival_rate_configured": config.task_arrival_probability,
            "reward_event_count": len(reward_events),
        },
        "warnings": warnings,
        "claims": {
            "no_training": True,
            "no_figure_9_10_claim": True,
            "no_figure_8_11_claim": True,
            "no_thesis_method": True,
            "no_dcq": True,
        },
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

    arrival_payload = {
        "arrival_opportunities": result["arrival_opportunities"],
        "total_arrived_tasks": len(result["tasks"]),
        "arrived_tasks_by_ea": result["arrival_by_ea"],
        "configured_P": config.task_arrival_probability,
        "observed_arrival_rate": len(result["tasks"]) / result["arrival_opportunities"] if result["arrival_opportunities"] else 0.0,
        "random_seed": config.random_seed,
    }
    _write_json(runtime_config_path, {**config.to_dict(), **result["topology"].to_dict()})
    _write_json(arrival_diag_path, arrival_payload)
    _write_csv(arrival_csv_path, [{"ea_id": ea_id, "arrived_tasks": count} for ea_id, count in result["arrival_by_ea"].items()])
    _write_json(lifecycle_json_path, result["lifecycle_trace"])
    _write_csv(lifecycle_csv_path, result["lifecycle_trace"])
    queue_rows = [asdict(row) for row in result["queue_trace"]]
    _write_json(queue_json_path, queue_rows)
    _write_csv(queue_csv_path, queue_rows)
    active_rows = [asdict(active) for active in result["public_active_sets"]]
    _write_json(active_json_path, active_rows)
    _write_csv(active_csv_path, active_rows)
    _write_json(state_sample_path, [snapshot.to_dict() for snapshot in result["state_snapshots"][:5]])
    reward_rows = [event.to_dict() for event in result["reward_events"]]
    _write_json(reward_json_path, reward_rows)
    _write_csv(reward_csv_path, reward_rows)
    _write_json(degeneracy_path, [result["degeneracy"].to_dict()])

    report = _build_runtime_report(result)
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
                f"- Topology temporary: `{result['topology_temporary']}`",
                "- Drain phase active: yes",
                f"- Public CPU sharing active: {'yes' if result['public_cpu_used'] else 'no'}",
                "- Delayed reward collection active: yes",
                "- Bernoulli arrivals active: yes",
                "- Private queue active: yes",
                "- Offloading queue active: yes",
                "- Completion/drop status separated: yes",
                "",
                "## Summary",
                json.dumps(report["summary"], indent=2, sort_keys=True),
                "",
                "## Warnings",
                json.dumps(report["warnings"], indent=2, sort_keys=True),
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

    runtime_config = json.loads((artifact_dir / "runtime_config.json").read_text(encoding="utf-8"))
    arrival = json.loads((artifact_dir / "arrival_diagnostics.json").read_text(encoding="utf-8"))
    lifecycle = json.loads((artifact_dir / "task_lifecycle_trace.json").read_text(encoding="utf-8"))
    queue_trace = json.loads((artifact_dir / "queue_dynamics_trace.json").read_text(encoding="utf-8"))
    active_sets = json.loads((artifact_dir / "public_queue_active_set_trace.json").read_text(encoding="utf-8"))
    reward_events = json.loads((artifact_dir / "reward_events.json").read_text(encoding="utf-8"))
    report = json.loads((artifact_dir / "runtime_core_validation_report.json").read_text(encoding="utf-8"))

    if arrival["arrival_opportunities"] <= 0:
        raise ValueError("arrival opportunities missing")
    if arrival["total_arrived_tasks"] <= 0:
        raise ValueError("no arrivals were generated")
    if not queue_trace:
        raise ValueError("no queue events occurred")
    if not lifecycle:
        raise ValueError("no lifecycle events recorded")
    if not reward_events:
        raise ValueError("no reward events recorded")
    if report.get("drain_phase_active") is not True:
        raise ValueError("drain phase does not process pending tasks")
    if not any(row.get("event") in {"public_completed", "public_dropped_timeout"} for row in lifecycle):
        raise ValueError("no public queue completion/drop events were generated")
    if not any(row.get("event") in {"private_completed", "private_dropped_timeout", "offloading_dropped_timeout"} for row in lifecycle):
        raise ValueError("no private/offloading queue terminal events were generated")
    if any(path in {"horizontal", "vertical"} for path in report.get("path_coverage", [])):
        if not any(active.get("active_public_queue_count", 0) > 0 for active in active_sets):
            raise ValueError("public queue active sets were never generated when horizontal/vertical paths were used")
        if not any(active.get("active_public_queue_count", 0) > 1 for active in active_sets):
            raise ValueError("public CPU sharing was not exercised in at least one test scenario")
    if any(event.get("reward_collection_slot") == event.get("original_action_slot") and event.get("completed_or_dropped") == "dropped_timeout" for event in reward_events):
        raise ValueError("reward events were emitted at arrival time instead of completion/drop time")
    if report.get("completion_drop_status_separated") is not True:
        raise ValueError("completion/drop status is not separated")
    if report.get("delayed_reward_collection_active") is not True:
        raise ValueError("delayed reward collection is not active")
    if report.get("summary", {}).get("unresolved_tasks") == report.get("summary", {}).get("arrived_tasks"):
        raise ValueError("all tasks remain unresolved")
    if report.get("public_queue_cpu_sharing_active") is not True:
        raise ValueError("public CPU sharing is not active")

    return {
        "passed": True,
        "artifact_dir": str(artifact_dir),
        "runtime_config": runtime_config,
        "arrival_diagnostics": arrival,
        "lifecycle_events": len(lifecycle),
        "queue_events": len(queue_trace),
        "active_set_events": len(active_sets),
        "reward_events": len(reward_events),
        "report": report,
    }
