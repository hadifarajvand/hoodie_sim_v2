from __future__ import annotations

import math
from collections import deque

import numpy as np

from .decision_maker_base import DescisionMakerBase
from environment.task import Task


class BalancedCyclicOffloader(DescisionMakerBase):
    def __init__(self, number_of_actions, *args, **kwargs):
        self.number_of_actions = number_of_actions
        self._cycle = deque(self._build_cycle())

    def _build_cycle(self) -> list[int]:
        if self.number_of_actions <= 0:
            return [0]
        local = [0]
        cloud = [self.number_of_actions - 1] if self.number_of_actions > 1 else [0]
        horizontal = list(range(1, max(1, self.number_of_actions - 1)))
        return local + cloud + horizontal

    def choose_action(self, *args, **kwargs):
        action = self._cycle[0]
        self._cycle.rotate(-1)
        return int(action)


class MinimumLatencyEstimationOffloader(DescisionMakerBase):
    def __init__(
        self,
        number_of_actions: int | None = None,
        env=None,
        source_id: int | None = None,
        matchmaker=None,
        estimator_version: str = "phase3_candidate_latency_v1",
        *args,
        **kwargs,
    ):
        self.number_of_actions = number_of_actions
        self.env = env
        self.source_id = source_id
        self.matchmaker = matchmaker
        self.estimator_version = estimator_version

    def _action_space(self):
        if self.matchmaker is not None and self.source_id is not None:
            return self.matchmaker.get_action_space()
        if self.number_of_actions is None:
            return []
        actions = [0]
        if self.number_of_actions > 2:
            actions.extend(range(1, self.number_of_actions - 1))
        if self.number_of_actions > 1:
            actions.append(self.number_of_actions - 1)
        return actions

    @staticmethod
    def _service_time(required_cpu_cycles: float, capacity_per_slot: float) -> int:
        if capacity_per_slot <= 0:
            return 0
        return int(math.ceil(required_cpu_cycles / capacity_per_slot))

    def _trace(self, **kwargs) -> None:
        recorder = getattr(Task, "trace_recorder", None)
        if recorder is not None:
            recorder.note_mleo_candidate_latency(**kwargs)

    def choose_action(self, observation, public_queues, *args, **kwargs):
        if self.env is None or self.source_id is None or self.matchmaker is None:
            return 0

        task = self.env.tasks[self.source_id]
        if task is None or task.is_empty():
            return 0

        episode_id = getattr(self.env, "episode_id", 0)
        current_time = getattr(self.env, "current_time", 0)
        source_server = self.env.servers[self.source_id]
        local_wait = float(source_server.processing_queue.get_waiting_time())
        offloading_wait = float(source_server.offloading_queue.get_waiting_time())
        action_space = self.matchmaker.get_action_space()
        task_size = float(task.get_size())
        remaining_size = float(task.get_remaining_size())
        density = float(task.get_density())
        required_cpu_cycles = float(task.get_size() * task.get_density())
        arrival_time = int(task.arrival_time)
        absolute_deadline = int(task.absolute_deadline)
        timeout = int(task.timeout)

        candidate_rows = []
        for action in action_space:
            warnings: list[str] = []
            unavailable: list[str] = []
            total = None
            private_service = None
            offload_service = None
            transmission = None
            public_wait = None
            public_service = None
            cloud_wait = None
            cloud_service = None
            if action.destination_type == "local":
                private_service = self._service_time(required_cpu_cycles, source_server.private_queue_computational_capacity)
                total = local_wait + private_service
            elif action.destination_type == "horizontal_edge":
                destination = int(action.destination_node_id)
                transmission_capacity = float(source_server.offloading_capacities[destination])
                transmission = self._service_time(remaining_size, transmission_capacity)
                dest_server = self.env.servers[destination]
                public_wait = float(dest_server.estimate_public_queue_wait(self.source_id))
                active_public_queues = dest_server.public_queue_manager.get_active_queues()
                if dest_server.public_queue_manager.public_queues[self.source_id].is_empty():
                    active_public_queues += 1
                    warnings.append("public_wait/public_service use deterministic active-queue estimate")
                if active_public_queues <= 0:
                    unavailable.append("public_service_estimate")
                    public_service = 0.0
                else:
                    public_service = self._service_time(required_cpu_cycles, dest_server.public_queues_computational_capacity / active_public_queues)
                total = offloading_wait + transmission + public_wait + public_service
            elif action.destination_type == "vertical_cloud":
                transmission_capacity = float(source_server.offloading_capacities[self.env.number_of_servers])
                transmission = self._service_time(remaining_size, transmission_capacity)
                cloud = self.env.cloud
                cloud_wait = float(cloud.estimate_public_queue_wait(self.source_id))
                active_cloud_queues = cloud.public_queue_manager.get_active_queues()
                if cloud.public_queue_manager.public_queues[self.source_id].is_empty():
                    active_cloud_queues += 1
                    warnings.append("cloud_wait/cloud_service use deterministic active-queue estimate")
                if active_cloud_queues <= 0:
                    unavailable.append("cloud_service_estimate")
                    cloud_service = 0.0
                else:
                    cloud_service = self._service_time(required_cpu_cycles, cloud.computational_capacity / active_cloud_queues)
                total = offloading_wait + transmission + cloud_wait + cloud_service
            else:
                unavailable.append("candidate_latency")

            slack = None if total is None else float(absolute_deadline - current_time - total)
            violation = None if slack is None else bool(slack < 0)
            candidate_rows.append(
                {
                    "episode_id": episode_id,
                    "time": current_time,
                    "task_id": int(task.task_id),
                    "source_agent": self.source_id,
                    "raw_action_id": int(action.raw_action_id),
                    "first_stage_decision": action.first_stage_decision,
                    "destination_type": action.destination_type,
                    "destination_node_id": action.destination_node_id,
                    "is_legal_candidate": bool(action.is_valid),
                    "is_selected": False,
                    "input_data_size": task_size,
                    "remaining_size": remaining_size,
                    "processing_density": density,
                    "required_cpu_cycles": required_cpu_cycles,
                    "arrival_time": arrival_time,
                    "absolute_deadline": absolute_deadline,
                    "timeout": timeout,
                    "private_wait_estimate": local_wait if action.destination_type == "local" else None,
                    "private_service_estimate": private_service,
                    "offloading_wait_estimate": offloading_wait if action.destination_type != "local" else None,
                    "transmission_estimate": transmission,
                    "public_wait_estimate": public_wait,
                    "public_service_estimate": public_service,
                    "cloud_wait_estimate": cloud_wait,
                    "cloud_service_estimate": cloud_service,
                    "total_estimated_latency": total,
                    "deadline_slack_estimate": slack,
                    "estimated_deadline_violation": violation,
                    "estimator_version": self.estimator_version,
                    "unavailable_fields": unavailable,
                    "approximation_warnings": warnings,
                }
            )

        legal_candidates = [row for row in candidate_rows if row["is_legal_candidate"]]
        if not legal_candidates:
            return 0

        def sort_key(row):
            if row["destination_type"] == "local":
                return (row["total_estimated_latency"], 0, -1)
            if row["destination_type"] == "horizontal_edge":
                return (row["total_estimated_latency"], 1, int(row["destination_node_id"]))
            return (row["total_estimated_latency"], 2, int(row["destination_node_id"]))

        selected = min(legal_candidates, key=sort_key)
        selected_raw_action = int(selected["raw_action_id"])
        for row in candidate_rows:
            row["is_selected"] = row["raw_action_id"] == selected_raw_action
            self._trace(
                unavailable_fields=row.pop("unavailable_fields"),
                approximation_warnings=row.pop("approximation_warnings"),
                **row,
            )
        return selected_raw_action


def official_policy_map() -> dict[str, str]:
    return {
        "HOODIE": "drl",
        "RO": "random",
        "FLC": "all_local",
        "VO": "all_vertical",
        "HO": "all_horizontal",
        "BCO": "balanced_cyclic",
        "MLEO": "mleo",
    }
