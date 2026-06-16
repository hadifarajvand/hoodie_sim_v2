from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any
import json
import math

import numpy as np

from .euls_core import ActionDecision, SimulationScenario, Task, deterministic_rng
from .event_system import EventType, SimulationEvent
from .logger import TraceLogger
from .policies import PolicyInterface
from .queue_manager import QueueManager
from .replay_engine import ReplayEngine
from reward_contract import compute_mrs_reward


class DeterministicSimulationEngine:
    def __init__(self, scenario: SimulationScenario, policy: PolicyInterface, output_dir: str | Path) -> None:
        self.scenario = scenario
        self.policy = policy
        self.output_dir = Path(output_dir)
        self.rng = deterministic_rng(scenario.seed)
        self.queue_manager = QueueManager(scenario.edge_cpu_slots, scenario.cloud_cpu_slots)
        self.logger = TraceLogger(self.output_dir)
        self._seq = 0
        self.tasks: dict[int, Task] = {}
        self.alpha = 1.0
        self.beta = 5.0
        self.net_le = 1.0
        self.net_ec = 2.0
        self.service_rates = {
            **{node_id: float(rate) for node_id, rate in enumerate(scenario.edge_cpu_slots)},
            self.scenario.num_edge_nodes: float(scenario.cloud_cpu_slots),
        }

    def _next_seq(self) -> int:
        self._seq += 1
        return self._seq

    def _state(self, task: Task) -> dict[str, Any]:
        return {
            "d_i": float(task.workload_size),
            "l_i": float(task.data_size),
            "q_local": float(len(self.queue_manager.nodes[task.source_node].queue)),
            "q_edge": float(sum(len(node.queue) for node in self.queue_manager.nodes)),
            "q_cloud": float(len(self.queue_manager.cloud.queue)),
            "b_local": float(len(self.queue_manager.nodes[task.source_node].running_tasks)),
            "b_edge": float(sum(len(node.running_tasks) for node in self.queue_manager.nodes)),
            "b_cloud": float(len(self.queue_manager.cloud.running_tasks)),
            "net_le": float(self.net_le),
            "net_ec": float(self.net_ec),
        }

    def _service_time(self, workload_size: float, rate: float) -> float:
        return float(workload_size / max(rate, 1e-9))

    def _reward(self, task: Task) -> float:
        return compute_mrs_reward(
            arrival_time=int(task.arrival_time),
            completion_time=int(task.finish_time or task.arrival_time),
            deadline=int(task.deadline),
            alpha=self.alpha,
            beta=self.beta,
        )

    def _arrival_tasks(self, time: int) -> list[Task]:
        count = int(self.rng.poisson(self.scenario.workload.arrival_rate))
        tasks = []
        for _ in range(count):
            source = int(self.rng.integers(0, self.scenario.num_edge_nodes))
            task = Task(
                task_id=len(self.tasks) + 1,
                arrival_time=time,
                workload_size=float(self.rng.integers(self.scenario.task_size_range[0], self.scenario.task_size_range[1] + 1)),
                deadline=int(self.rng.integers(self.scenario.deadline_range[0], self.scenario.deadline_range[1] + 1)),
                priority_class=0,
                data_size=float(self.rng.integers(self.scenario.task_size_range[0], self.scenario.task_size_range[1] + 1)),
                source_node=source,
            )
            self.tasks[task.task_id] = task
            tasks.append(task)
        return tasks

    def _apply_action(self, task: Task, action: int) -> int:
        if action not in {0, 1, 2}:
            raise ValueError("action must be 0, 1, or 2")
        if action == 0:
            return task.source_node
        if action == 1:
            return min(task.source_node + 1, self.scenario.num_edge_nodes - 1)
        return self.scenario.num_edge_nodes

    def _log_event(self, timestamp: int, task: Task, node_id: int, event_type: EventType) -> None:
        event = SimulationEvent(
            timestamp=timestamp,
            sequence_id=self._next_seq(),
            task_id=task.task_id,
            node_id=node_id,
            event_type=event_type,
            queue_snapshot=self.queue_manager.snapshot(),
            cpu_state_snapshot=self.queue_manager.cpu_snapshot(),
            decision_metadata={"policy_name": self.policy.name},
        )
        self.logger.record(event)

    def run(self) -> dict[str, Any]:
        for time in range(self.scenario.horizon):
            for task in self._arrival_tasks(time):
                self._log_event(time, task, task.source_node, EventType.TASK_ARRIVAL)
                state = self._state(task)
                decision = self.policy.select_action(state)
                if decision.kind == "LOCAL":
                    action = 0
                elif decision.kind == "EDGE":
                    action = 1
                else:
                    action = 2
                node_id = self._apply_action(task, action)
                self._log_event(time, task, node_id, EventType.TASK_ENQUEUE)
                self.queue_manager.enqueue(task, node_id)
            finished = self.queue_manager.step(time)
            for task in finished:
                self._log_event(time, task, int(task.assigned_node or 0), EventType.TASK_FINISH)

        while any(node.queue or node.running_tasks for node in self.queue_manager.all_nodes):
            time = self.scenario.horizon
            finished = self.queue_manager.step(time)
            for task in finished:
                self._log_event(time, task, int(task.assigned_node or 0), EventType.TASK_FINISH)
            self.scenario = SimulationScenario(**{**self.scenario.to_dict(), "horizon": self.scenario.horizon + 1})

        metrics = self._build_metrics()
        self.logger.metrics = metrics
        paths = self.logger.write(self.scenario.scenario_id, self.scenario.to_dict(), self.scenario.seed)
        return {
            "event_hash": self.logger.event_hash(),
            "trace_path": paths["trace.json"],
            "metrics_path": paths["metrics.json"],
            "state_path": paths["state.json"],
        }

    def _log_node_step(self, node_id: int, current_time: int) -> None:
        finished = self.queue_manager.step(current_time)
        for task in finished:
            task.latency = float((task.finish_time or current_time) - task.arrival_time + 1)
            task.violation_flag = bool((task.finish_time or current_time) > task.deadline)
            self._log_event(current_time, task, node_id, EventType.TASK_FINISH)

    def _build_metrics(self) -> dict[str, Any]:
        latencies = [task.latency for task in self.tasks.values() if task.latency is not None]
        violations = [1 for task in self.tasks.values() if task.violation_flag]
        return {
            "average_latency": float(np.mean(latencies)) if latencies else 0.0,
            "violation_ratio": float(sum(violations) / max(1, len(self.tasks))),
            "queue_growth_behavior": [len(node.queue) for node in self.queue_manager.all_nodes],
        }
