from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Iterable


@dataclass
class TaskLifecycleRecord:
    task_id: int
    episode_id: int | None = None
    arrival_time: int | None = None
    source_node: int | None = None
    queue_enter_time: int | None = None
    service_start_time: int | None = None
    service_end_time: int | None = None
    completion_time: int | None = None
    drop_time: int | None = None
    selected_action: int | None = None
    processing_node: int | None = None
    latency: float | None = None
    waiting_time: float | None = None
    service_time: float | None = None
    final_status: str = "pending"
    drop_reason: str | None = None


@dataclass
class QueueTraceRecord:
    episode_id: int
    time: int
    node_id: int
    queue_type: str
    queue_length: float
    arrivals: int = 0
    departures: int = 0
    drops: int = 0
    cpu_allocated: float | None = None


@dataclass
class ActionTraceRecord:
    episode_id: int
    time: int
    agent_id: int
    observation_shape: list[int]
    selected_action: int
    target_node: int | None
    reward_received: float


@dataclass
class EpisodeMetricRecord:
    episode_id: int
    total_tasks: int
    completed_tasks: int
    dropped_tasks: int
    pending_tasks: int
    average_latency: float | None
    average_waiting_time: float | None
    average_service_time: float | None
    drop_ratio: float
    average_queue_length: float | None
    total_reward: float
    mean_reward: float


class TraceRecorder:
    def __init__(self) -> None:
        self.task_records: dict[int, TaskLifecycleRecord] = {}
        self.queue_traces: list[QueueTraceRecord] = []
        self.action_traces: list[ActionTraceRecord] = []
        self.episode_metrics: list[EpisodeMetricRecord] = []
        self._queue_length_history: dict[int, list[float]] = defaultdict(list)
        self._episode_id: int | None = None

    def start_episode(self, episode_id: int) -> None:
        self._episode_id = episode_id

    def ensure_task(self, task_id: int) -> TaskLifecycleRecord:
        return self.task_records.setdefault(task_id, TaskLifecycleRecord(task_id=task_id))

    def note_task_arrival(self, task: Any, episode_id: int, source_node: int, arrival_time: int) -> None:
        record = self.ensure_task(task.task_id)
        record.episode_id = episode_id
        record.arrival_time = arrival_time
        record.source_node = source_node

    def note_queue_enter(
        self,
        task: Any,
        episode_id: int,
        time: int,
        node_id: int,
        queue_type: str,
    ) -> None:
        record = self.ensure_task(task.task_id)
        record.episode_id = episode_id
        if record.queue_enter_time is None:
            record.queue_enter_time = time
        if record.processing_node is None:
            record.processing_node = node_id
        task.queue_enter_time = record.queue_enter_time

    def note_service_start(self, task: Any, episode_id: int, time: int, node_id: int, queue_type: str) -> None:
        record = self.ensure_task(task.task_id)
        record.episode_id = episode_id
        if record.service_start_time is None:
            record.service_start_time = time
        if record.processing_node is None:
            record.processing_node = node_id
        task.service_start_time = record.service_start_time

    def note_service_end(self, task: Any, episode_id: int, time: int, node_id: int, queue_type: str) -> None:
        record = self.ensure_task(task.task_id)
        record.episode_id = episode_id
        record.service_end_time = time
        if record.service_start_time is not None:
            record.service_time = max(0, time - record.service_start_time)
        if record.arrival_time is not None:
            record.latency = max(0, time - record.arrival_time)
            if record.service_start_time is not None:
                record.waiting_time = max(0, record.service_start_time - record.arrival_time)
        task.service_end_time = time
        task.completion_time = time
        task.final_status = "completed"

    def note_drop(self, task: Any, episode_id: int, time: int, node_id: int, queue_type: str, reason: str | None = None) -> None:
        record = self.ensure_task(task.task_id)
        record.episode_id = episode_id
        record.drop_time = time
        record.final_status = "dropped"
        record.drop_reason = reason
        if record.arrival_time is not None:
            record.latency = max(0, time - record.arrival_time)
        task.drop_time = time
        task.final_status = "dropped"
        task.drop_reason = reason

    def note_action(
        self,
        episode_id: int,
        time: int,
        agent_id: int,
        observation_shape: Iterable[int],
        selected_action: int,
        target_node: int | None,
        reward_received: float,
    ) -> None:
        for record in self.task_records.values():
            if record.episode_id == episode_id and record.source_node == agent_id and record.arrival_time == time:
                record.selected_action = int(selected_action)
                if target_node is not None and record.processing_node is None:
                    record.processing_node = int(target_node)
        self.action_traces.append(
            ActionTraceRecord(
                episode_id=episode_id,
                time=time,
                agent_id=agent_id,
                observation_shape=list(observation_shape),
                selected_action=int(selected_action),
                target_node=None if target_node is None else int(target_node),
                reward_received=float(reward_received),
            )
        )

    def note_queue_trace(
        self,
        episode_id: int,
        time: int,
        node_id: int,
        queue_type: str,
        queue_length: float,
        arrivals: int = 0,
        departures: int = 0,
        drops: int = 0,
        cpu_allocated: float | None = None,
    ) -> None:
        self.queue_traces.append(
            QueueTraceRecord(
                episode_id=episode_id,
                time=time,
                node_id=node_id,
                queue_type=queue_type,
                queue_length=float(queue_length),
                arrivals=int(arrivals),
                departures=int(departures),
                drops=int(drops),
                cpu_allocated=None if cpu_allocated is None else float(cpu_allocated),
            )
        )
        self._queue_length_history[episode_id].append(float(queue_length))

    def finalize_episode(self, episode_id: int, total_reward: float, mean_reward: float) -> EpisodeMetricRecord:
        records = [r for r in self.task_records.values() if r.episode_id == episode_id]
        total_tasks = len(records)
        completed = sum(1 for r in records if r.final_status == "completed")
        dropped = sum(1 for r in records if r.final_status == "dropped")
        pending = sum(1 for r in records if r.final_status == "pending")
        latencies = [r.latency for r in records if r.latency is not None]
        waits = [r.waiting_time for r in records if r.waiting_time is not None]
        service_times = [r.service_time for r in records if r.service_time is not None]
        avg_queue_length = None
        if episode_id in self._queue_length_history and self._queue_length_history[episode_id]:
            avg_queue_length = sum(self._queue_length_history[episode_id]) / len(self._queue_length_history[episode_id])
        metric = EpisodeMetricRecord(
            episode_id=episode_id,
            total_tasks=total_tasks,
            completed_tasks=completed,
            dropped_tasks=dropped,
            pending_tasks=pending,
            average_latency=(sum(latencies) / len(latencies)) if latencies else None,
            average_waiting_time=(sum(waits) / len(waits)) if waits else None,
            average_service_time=(sum(service_times) / len(service_times)) if service_times else None,
            drop_ratio=(dropped / total_tasks) if total_tasks else 0.0,
            average_queue_length=avg_queue_length,
            total_reward=float(total_reward),
            mean_reward=float(mean_reward),
        )
        self.episode_metrics.append(metric)
        return metric

    def export(self, output_dir: str | Path) -> None:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        self._write_csv(output_dir / "task_lifecycle.csv", [asdict(r) for r in self.task_records.values()])
        self._write_csv(output_dir / "queue_trace.csv", [asdict(r) for r in self.queue_traces])
        self._write_csv(output_dir / "action_trace.csv", [asdict(r) for r in self.action_traces])
        self._write_csv(output_dir / "episode_metrics.csv", [asdict(r) for r in self.episode_metrics])

    def _write_csv(self, path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        if not rows:
            path.write_text("")
            return
        fieldnames = list(rows[0].keys())
        with path.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def validate(self, episode_id: int) -> list[str]:
        errors: list[str] = []
        records = [r for r in self.task_records.values() if r.episode_id == episode_id]
        task_ids = [r.task_id for r in records]
        if len(task_ids) != len(set(task_ids)):
            errors.append("task_id uniqueness violated")
        for r in records:
            if r.final_status not in {"completed", "dropped", "pending"}:
                errors.append(f"invalid final status for task {r.task_id}")
            if r.latency is not None and r.latency < 0:
                errors.append(f"negative latency for task {r.task_id}")
            if r.waiting_time is not None and r.waiting_time < 0:
                errors.append(f"negative waiting time for task {r.task_id}")
            if r.service_time is not None and r.service_time < 0:
                errors.append(f"negative service time for task {r.task_id}")
            if r.service_start_time is not None and r.queue_enter_time is not None and r.service_start_time < r.queue_enter_time:
                errors.append(f"service start before queue enter for task {r.task_id}")
            if r.completion_time is not None and r.arrival_time is not None and r.completion_time < r.arrival_time:
                errors.append(f"completion before arrival for task {r.task_id}")
        for q in self.queue_traces:
            if q.queue_length < 0:
                errors.append(f"negative queue length at node {q.node_id} time {q.time}")
            if not (0.0 <= q.arrivals or q.arrivals == 0):
                errors.append("invalid arrivals count")
        for m in self.episode_metrics:
            if not (0.0 <= m.drop_ratio <= 1.0):
                errors.append(f"invalid drop ratio for episode {m.episode_id}")
            if m.completed_tasks + m.dropped_tasks + m.pending_tasks != m.total_tasks:
                errors.append(f"count mismatch for episode {m.episode_id}")
        return errors
