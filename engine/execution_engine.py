from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from .euls_core import ActionDecision, SimulationScenario, Task, deterministic_rng
from .event_system import EventType, SimulationEvent
from .logger import TraceLogger
from .queue_manager import QueueManager
from .dal.registry import AgentRegistry


class DeterministicSimulationEngine:
    def __init__(
        self,
        scenario: SimulationScenario,
        policy: Any,
        output_dir: str | Path,
        agent_registry: AgentRegistry | None = None,
    ) -> None:
        self.scenario = scenario
        self.policy = policy
        self.output_dir = Path(output_dir)
        self.rng = deterministic_rng(scenario.seed)
        self.logger = TraceLogger(self.output_dir)
        self.queue_manager = QueueManager(scenario.edge_cpu_slots, scenario.cloud_cpu_slots)
        self.agent_registry = agent_registry
        self.task_counter = 0
        self.tasks: dict[int, Task] = {}
        self._sequence_id = 0

    def _next_sequence(self) -> int:
        self._sequence_id += 1
        return self._sequence_id

    def _arrival_rate(self, time: int) -> float:
        workload = self.scenario.workload
        if workload.burst_rate is not None and workload.burst_start is not None and workload.burst_end is not None:
            if workload.burst_start <= time < workload.burst_end:
                return float(workload.burst_rate)
        return float(workload.arrival_rate)

    def _sample_task(self, time: int, source_node: int) -> Task:
        self.task_counter += 1
        size = float(self.rng.integers(self.scenario.task_size_range[0], self.scenario.task_size_range[1] + 1))
        deadline = int(self.rng.integers(self.scenario.deadline_range[0], self.scenario.deadline_range[1] + 1)) + time
        return Task(
            task_id=self.task_counter,
            arrival_time=time,
            workload_size=size,
            deadline=deadline,
            priority_class=0,
            data_size=size,
            source_node=source_node,
        )

    def _cpu_state(self) -> dict[str, Any]:
        return self.queue_manager.cpu_snapshot()

    def _queue_state(self) -> dict[str, Any]:
        return self.queue_manager.snapshot()

    def _state(self, time: int) -> dict[str, Any]:
        active_load = self.queue_manager.active_load_vector()
        return {
            "time": time,
            "queue_lengths": {node.node_id: len(node.queue) + len(node.running_tasks) for node in self.queue_manager.all_nodes},
            "queue_work": {node.node_id: float(work) for node, work in zip(self.queue_manager.all_nodes, active_load, strict=False)},
            "cpu_utilization": {node.node_id: len(node.running_tasks) / max(1, node.cpu_slots) for node in self.queue_manager.all_nodes},
            "neighbor_load": {node.node_id: float(work) for node, work in zip(self.queue_manager.all_nodes, active_load, strict=False)},
        }

    def _decision(self, task: Task, state: dict[str, Any]) -> ActionDecision:
        if self.agent_registry is not None:
            agent = self.agent_registry.get(task.source_node)
            if agent is not None:
                return agent.decide(
                    {"task": task, "event_type": EventType.TASK_OFFLOAD_DECISION},
                    {
                        "state": state,
                        "scenario": self.scenario,
                        "rng": self.rng,
                        "agent_id": task.source_node,
                    },
                )
        decision = self.policy.select_action(state)
        if isinstance(decision, ActionDecision):
            return decision
        return ActionDecision.local(getattr(self.policy, "name", "FIFO"))

    def _log(self, time: int, task: Task, event_type: EventType, node_id: int | None, decision_metadata: dict[str, Any] | None = None) -> None:
        self.logger.record(
            SimulationEvent(
                timestamp=time,
                sequence_id=self._next_sequence(),
                task_id=task.task_id,
                node_id=node_id,
                event_type=event_type,
                queue_snapshot=self._queue_state(),
                cpu_state_snapshot=self._cpu_state(),
                decision_metadata=decision_metadata or {},
                policy_name=getattr(self.policy, "name", None),
                seed=self.scenario.seed,
            )
        )

    def _sync_agent_state(self, node_id: int) -> None:
        if self.agent_registry is None:
            return
        agent = self.agent_registry.get(node_id)
        if agent is None:
            return
        node = self.queue_manager.all_nodes[node_id]
        agent.state.queue_reference = node.queue
        agent.state.cpu_slots = int(node.cpu_slots)
        agent.state.active_tasks = [task.task_id for task in node.running_tasks]

    def _dispatch_started(self, time: int, started: list[Task]) -> None:
        for task in started:
            self._log(time, task, EventType.TASK_START, task.assigned_node, {"queue_length": len(self.queue_manager.all_nodes[task.assigned_node].queue)})

    def _dispatch_finished(self, time: int, finished: list[Task]) -> None:
        for task in finished:
            self._log(time, task, EventType.TASK_FINISH, task.assigned_node, {"latency": task.latency})

    def run(self) -> dict[str, Any]:
        completed: list[Task] = []
        for time in range(self.scenario.horizon):
            arrivals_per_node = max(0, int(round(self._arrival_rate(time))))
            for source_node in range(self.scenario.num_edge_nodes):
                for _ in range(arrivals_per_node):
                    task = self._sample_task(time, source_node)
                    self.tasks[task.task_id] = task
                    self._log(time, task, EventType.TASK_ARRIVAL, source_node, {"arrival_rate": self._arrival_rate(time)})
                    state = self._state(time)
                    action = self._decision(task, state)
                    target = source_node if action.kind == "LOCAL" else (self.scenario.num_edge_nodes if action.kind == "CLOUD" else int(action.target_node))
                    task.offloading_decision = action.label
                    self._log(time, task, EventType.TASK_ENQUEUE, target, {"action": action.label, "target_node": target})
                    self.queue_manager.enqueue(task, target)
                    self._sync_agent_state(target)
                    started = self.queue_manager.start_if_idle(target, time)
                    if started is not None:
                        self._sync_agent_state(target)
                        self._log(time, started, EventType.TASK_START, target, {"queue_length": len(self.queue_manager.all_nodes[target].queue)})

            finished = self.queue_manager.step(time)
            completed.extend(finished)
            self._dispatch_finished(time, finished)
            for task in finished:
                node_id = task.assigned_node
                self._sync_agent_state(node_id)
                started = self.queue_manager.start_if_idle(node_id, time)
                if started is not None:
                    self._sync_agent_state(node_id)
                    self._log(time, started, EventType.TASK_START, node_id, {"queue_length": len(self.queue_manager.all_nodes[node_id].queue)})

            self.logger.record_state(
                {
                    "time": time,
                    "queue_lengths": {node.node_id: len(node.queue) + len(node.running_tasks) for node in self.queue_manager.all_nodes},
                    "cpu_state": {node.node_id: len(node.running_tasks) for node in self.queue_manager.all_nodes},
                }
            )

        while any(node.queue or node.running_tasks for node in self.queue_manager.all_nodes):
            time = self.scenario.horizon + len(completed)
            finished = self.queue_manager.step(time)
            if not finished:
                break
            completed.extend(finished)
            self._dispatch_finished(time, finished)

        metrics = {
            "tasks": [task.runtime_snapshot() for task in self.tasks.values()],
            "latency": [float(task.latency) for task in self.tasks.values() if task.latency is not None],
            "waiting_time": [float(task.waiting_time) for task in self.tasks.values() if task.waiting_time is not None],
            "service_time": [float(task.service_time) for task in self.tasks.values() if task.service_time is not None],
            "queue_length_over_time": self.logger.state_snapshots,
        }
        self.logger.metrics = metrics
        files = self.logger.write("run", self.scenario.to_dict(), self.scenario.seed)
        return {
            "trace_path": files["trace.json"],
            "metrics_path": files["metrics.json"],
            "state_path": files["state.json"],
            "event_hash": self.logger.event_hash(),
            "events": [event.to_dict() for event in self.logger.events],
            "metrics": metrics,
        }
