from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Iterable

import numpy as np


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
    drop_penalty: float | None = None


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
    raw_action_id: int | None = None
    first_stage_decision: str | None = None
    destination_node_id: int | None = None
    destination_type: str | None = None
    is_valid: bool | None = None
    invalid_reason: str | None = None
    adjacency_allowed: bool | None = None
    cloud_target: bool | None = None
    d_n_1: int | None = None
    d_nk_2: dict[int, int] | None = None


@dataclass
class PaperStateTraceRecord:
    episode_id: int
    time: int
    agent_id: int
    task_id: int | None
    eta_n: float | None
    w_priv_n: float | None
    w_off_n: float | None
    l_pub_n_prev_json: str
    active_load_vector_json: str
    L_t_json: str
    predicted_next_load_json: str | None
    predicted_next_load_method: str
    paper_lstm_forecast: bool
    unavailable_fields_json: str
    approximation_warnings_json: str
    state_vector_json: str
    state_dim: int


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


@dataclass
class PendingTransitionTraceRecord:
    task_id: int
    episode_id: int | None
    source_agent: int
    arrival_time: int
    decision_time: int
    state_at_decision_json: str
    lstm_state_at_decision_json: str
    action_at_decision: int
    selected_target_node: int | None
    raw_action_id: int | None
    first_stage_decision: str | None
    destination_type: str | None
    destination_node_id: int | None
    immediate_next_state_after_action_json: str
    immediate_next_lstm_state_after_action_json: str
    created_by_policy: str | None
    replay_pairing_status: str


@dataclass
class DelayedRewardEventRecord:
    task_id: int
    episode_id: int | None
    source_agent: int
    decision_time: int
    final_status: str
    completion_time: int | None
    drop_time: int | None
    delay: int | None
    reward: float
    drop_penalty: float | None
    reward_reason: str
    paired_transition_found: bool
    replay_inserted: bool
    replay_pairing_status: str
    reward_timing_convention: str


@dataclass
class MleoCandidateLatencyRecord:
    episode_id: int
    time: int
    task_id: int
    source_agent: int
    raw_action_id: int
    first_stage_decision: str
    destination_type: str
    destination_node_id: int | None
    is_legal_candidate: bool
    is_selected: bool
    input_data_size: float
    remaining_size: float
    processing_density: float
    required_cpu_cycles: float
    arrival_time: int
    absolute_deadline: int
    timeout: int
    private_wait_estimate: float | None
    private_service_estimate: float | None
    offloading_wait_estimate: float | None
    transmission_estimate: float | None
    public_wait_estimate: float | None
    public_service_estimate: float | None
    cloud_wait_estimate: float | None
    cloud_service_estimate: float | None
    total_estimated_latency: float | None
    deadline_slack_estimate: float | None
    estimated_deadline_violation: bool | None
    estimator_version: str
    unavailable_fields_json: str
    approximation_warnings_json: str


class TraceRecorder:
    def __init__(self, trace_level: str = "full") -> None:
        self.trace_level = trace_level
        self.task_records: dict[int, TaskLifecycleRecord] = {}
        self.queue_traces: list[QueueTraceRecord] = []
        self.action_traces: list[ActionTraceRecord] = []
        self.pending_transition_traces: list[PendingTransitionTraceRecord] = []
        self.delayed_reward_event_traces: list[DelayedRewardEventRecord] = []
        self.mleo_candidate_latency_traces: list[MleoCandidateLatencyRecord] = []
        self.paper_state_traces: list[PaperStateTraceRecord] = []
        self.episode_metrics: list[EpisodeMetricRecord] = []
        self.pending_transitions: dict[int, PendingTransitionTraceRecord] = {}
        self._resolved_delayed_reward_task_ids: set[int] = set()
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
        record.drop_penalty = getattr(task, "drop_penalty", None)

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
        record.completion_time = time
        record.final_status = "completed"
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

    def resolve_delayed_reward_candidates(self, episode_id: int) -> list[dict[str, Any]]:
        from reward_contract import compute_delayed_reward

        resolved: list[dict[str, Any]] = []
        for record in self.task_records.values():
            if record.episode_id != episode_id:
                continue
            if record.task_id in self._resolved_delayed_reward_task_ids:
                continue
            if record.final_status not in {"completed", "dropped"}:
                continue
            pending = self.pending_transitions.get(record.task_id)
            paired = pending is not None
            reward_computation = compute_delayed_reward(
                final_status=record.final_status,
                arrival_time=record.arrival_time,
                completion_time=record.completion_time,
                drop_penalty=float(record.drop_penalty if record.drop_penalty is not None else 40.0),
            )
            resolved.append(
                {
                    "task_id": record.task_id,
                    "episode_id": record.episode_id,
                    "source_agent": record.source_node,
                    "decision_time": pending.decision_time if pending is not None else (record.queue_enter_time if record.queue_enter_time is not None else 0),
                    "final_status": record.final_status,
                    "completion_time": record.completion_time,
                    "drop_time": record.drop_time,
                    "delay": reward_computation.delay,
                    "reward": reward_computation.reward,
                    "drop_penalty": reward_computation.drop_penalty,
                    "reward_reason": reward_computation.reward_reason,
                    "paired_transition_found": paired,
                    "replay_inserted": False,
                    "replay_pairing_status": "paired" if paired else "unpaired",
                    "reward_timing_convention": reward_computation.reward_timing_convention,
                    "pending_transition": pending,
                }
            )
            self._resolved_delayed_reward_task_ids.add(record.task_id)
        return resolved

    def note_action(
        self,
        episode_id: int,
        time: int,
        agent_id: int,
        observation_shape: Iterable[int],
        selected_action: int,
        target_node: int | None,
        reward_received: float,
        first_stage_decision: str | None = None,
        destination_node_id: int | None = None,
        destination_type: str | None = None,
        is_valid: bool | None = None,
        invalid_reason: str | None = None,
        adjacency_allowed: bool | None = None,
        cloud_target: bool | None = None,
        d_n_1: int | None = None,
        d_nk_2: dict[int, int] | None = None,
    ) -> None:
        for record in self.task_records.values():
            if record.episode_id == episode_id and record.source_node == agent_id and record.arrival_time == time:
                record.selected_action = int(selected_action)
                if target_node is not None and record.processing_node is None:
                    record.processing_node = int(target_node)
        if first_stage_decision is None:
            first_stage_decision = "local" if target_node == agent_id else "offload"
        if destination_node_id is None:
            destination_node_id = target_node
        if destination_type is None:
            if destination_node_id is None or destination_node_id == agent_id:
                destination_type = "local"
            else:
                destination_type = "horizontal_edge"
        if is_valid is None:
            is_valid = True
        if adjacency_allowed is None:
            adjacency_allowed = destination_type != "invalid"
        if cloud_target is None:
            cloud_target = destination_type == "vertical_cloud"
        if d_n_1 is None:
            d_n_1 = 0 if first_stage_decision == "local" else 1
        self.action_traces.append(
            ActionTraceRecord(
                episode_id=episode_id,
                time=time,
                agent_id=agent_id,
                observation_shape=list(observation_shape),
                selected_action=int(selected_action),
                target_node=None if target_node is None else int(target_node),
                reward_received=float(reward_received),
                raw_action_id=int(selected_action),
                first_stage_decision=first_stage_decision,
                destination_node_id=None if destination_node_id is None else int(destination_node_id),
                destination_type=destination_type,
                is_valid=bool(is_valid),
                invalid_reason=invalid_reason,
                adjacency_allowed=adjacency_allowed,
                cloud_target=cloud_target,
                d_n_1=d_n_1,
                d_nk_2=d_nk_2,
            )
        )

    def note_pending_transition(
        self,
        task_id: int,
        episode_id: int | None,
        source_agent: int,
        arrival_time: int,
        decision_time: int,
        state_at_decision: Any,
        lstm_state_at_decision: Any,
        action_at_decision: int,
        selected_target_node: int | None,
        raw_action_id: int | None,
        first_stage_decision: str | None,
        destination_type: str | None,
        destination_node_id: int | None,
        immediate_next_state_after_action: Any,
        immediate_next_lstm_state_after_action: Any,
        created_by_policy: str | None,
        replay_pairing_status: str,
    ) -> None:
        record = PendingTransitionTraceRecord(
            task_id=task_id,
            episode_id=episode_id,
            source_agent=source_agent,
            arrival_time=arrival_time,
            decision_time=decision_time,
            state_at_decision_json=json.dumps(np.asarray(state_at_decision).tolist()),
            lstm_state_at_decision_json=json.dumps(np.asarray(lstm_state_at_decision).tolist()),
            action_at_decision=int(action_at_decision),
            selected_target_node=selected_target_node,
            raw_action_id=raw_action_id,
            first_stage_decision=first_stage_decision,
            destination_type=destination_type,
            destination_node_id=destination_node_id,
            immediate_next_state_after_action_json=json.dumps(np.asarray(immediate_next_state_after_action).tolist()),
            immediate_next_lstm_state_after_action_json=json.dumps(np.asarray(immediate_next_lstm_state_after_action).tolist()),
            created_by_policy=created_by_policy,
            replay_pairing_status=replay_pairing_status,
        )
        self.pending_transition_traces.append(record)
        self.pending_transitions[task_id] = record

    def note_delayed_reward_event(
        self,
        task_id: int,
        episode_id: int | None,
        source_agent: int,
        decision_time: int,
        final_status: str,
        completion_time: int | None,
        drop_time: int | None,
        delay: int | None,
        reward: float,
        drop_penalty: float | None,
        reward_reason: str,
        paired_transition_found: bool,
        replay_inserted: bool,
        replay_pairing_status: str,
        reward_timing_convention: str,
    ) -> None:
        self.delayed_reward_event_traces.append(
            DelayedRewardEventRecord(
                task_id=task_id,
                episode_id=episode_id,
                source_agent=source_agent,
                decision_time=decision_time,
                final_status=final_status,
                completion_time=completion_time,
                drop_time=drop_time,
                delay=delay,
                reward=float(reward),
                drop_penalty=drop_penalty,
                reward_reason=reward_reason,
                paired_transition_found=bool(paired_transition_found),
                replay_inserted=bool(replay_inserted),
                replay_pairing_status=replay_pairing_status,
                reward_timing_convention=reward_timing_convention,
            )
        )

    def note_paper_state(
        self,
        episode_id: int,
        time: int,
        agent_id: int,
        task_id: int | None,
        eta_n: float | None,
        w_priv_n: float | None,
        w_off_n: float | None,
        l_pub_n_prev: Any,
        active_load_vector: Any,
        load_history: Any,
        predicted_next_load: Any | None,
        predicted_next_load_method: str,
        paper_lstm_forecast: bool,
        unavailable_fields: list[str],
        approximation_warnings: list[str],
        state_vector: Any,
    ) -> None:
        if self.trace_level != "summary":
            self.paper_state_traces.append(
                PaperStateTraceRecord(
                    episode_id=episode_id,
                    time=time,
                    agent_id=agent_id,
                    task_id=task_id,
                    eta_n=None if eta_n is None else float(eta_n),
                    w_priv_n=None if w_priv_n is None else float(w_priv_n),
                    w_off_n=None if w_off_n is None else float(w_off_n),
                    l_pub_n_prev_json=json.dumps(np.asarray(l_pub_n_prev).tolist()),
                    active_load_vector_json=json.dumps(np.asarray(active_load_vector).tolist()),
                    L_t_json=json.dumps(np.asarray(load_history).tolist()),
                    predicted_next_load_json=None if predicted_next_load is None else json.dumps(np.asarray(predicted_next_load).tolist()),
                    predicted_next_load_method=predicted_next_load_method,
                    paper_lstm_forecast=bool(paper_lstm_forecast),
                    unavailable_fields_json=json.dumps(list(unavailable_fields)),
                    approximation_warnings_json=json.dumps(list(approximation_warnings)),
                    state_vector_json=json.dumps(np.asarray(state_vector).tolist()),
                    state_dim=int(np.asarray(state_vector).reshape(-1).shape[0]),
                )
            )

    def note_mleo_candidate_latency(
        self,
        episode_id: int,
        time: int,
        task_id: int,
        source_agent: int,
        raw_action_id: int,
        first_stage_decision: str,
        destination_type: str,
        destination_node_id: int | None,
        is_legal_candidate: bool,
        is_selected: bool,
        input_data_size: float,
        remaining_size: float,
        processing_density: float,
        required_cpu_cycles: float,
        arrival_time: int,
        absolute_deadline: int,
        timeout: int,
        private_wait_estimate: float | None,
        private_service_estimate: float | None,
        offloading_wait_estimate: float | None,
        transmission_estimate: float | None,
        public_wait_estimate: float | None,
        public_service_estimate: float | None,
        cloud_wait_estimate: float | None,
        cloud_service_estimate: float | None,
        total_estimated_latency: float | None,
        deadline_slack_estimate: float | None,
        estimated_deadline_violation: bool | None,
        estimator_version: str,
        unavailable_fields: list[str],
        approximation_warnings: list[str],
    ) -> None:
        if self.trace_level != "summary":
            self.mleo_candidate_latency_traces.append(
                MleoCandidateLatencyRecord(
                    episode_id=episode_id,
                    time=time,
                    task_id=task_id,
                    source_agent=source_agent,
                    raw_action_id=raw_action_id,
                    first_stage_decision=first_stage_decision,
                    destination_type=destination_type,
                    destination_node_id=destination_node_id,
                    is_legal_candidate=bool(is_legal_candidate),
                    is_selected=bool(is_selected),
                    input_data_size=float(input_data_size),
                    remaining_size=float(remaining_size),
                    processing_density=float(processing_density),
                    required_cpu_cycles=float(required_cpu_cycles),
                    arrival_time=int(arrival_time),
                    absolute_deadline=int(absolute_deadline),
                    timeout=int(timeout),
                    private_wait_estimate=private_wait_estimate,
                    private_service_estimate=private_service_estimate,
                    offloading_wait_estimate=offloading_wait_estimate,
                    transmission_estimate=transmission_estimate,
                    public_wait_estimate=public_wait_estimate,
                    public_service_estimate=public_service_estimate,
                    cloud_wait_estimate=cloud_wait_estimate,
                    cloud_service_estimate=cloud_service_estimate,
                    total_estimated_latency=total_estimated_latency,
                    deadline_slack_estimate=deadline_slack_estimate,
                    estimated_deadline_violation=estimated_deadline_violation,
                    estimator_version=estimator_version,
                    unavailable_fields_json=json.dumps(list(unavailable_fields)),
                    approximation_warnings_json=json.dumps(list(approximation_warnings)),
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
        if self.trace_level != "summary":
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
        if self.trace_level != "summary":
            self._write_csv(output_dir / "queue_trace.csv", [asdict(r) for r in self.queue_traces])
        self._write_csv(output_dir / "action_trace.csv", [asdict(r) for r in self.action_traces])
        self._write_csv(output_dir / "pending_transition_trace.csv", [asdict(r) for r in self.pending_transition_traces])
        self._write_csv(output_dir / "delayed_reward_event_trace.csv", [asdict(r) for r in self.delayed_reward_event_traces])
        if self.trace_level != "summary":
            self._write_csv(output_dir / "mleo_candidate_latency_trace.csv", [asdict(r) for r in self.mleo_candidate_latency_traces])
            self._write_csv(output_dir / "paper_state_trace.csv", [asdict(r) for r in self.paper_state_traces])
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
