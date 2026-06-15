from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar

import numpy as np


def _require_non_negative_int(name: str, value: int) -> None:
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a non-negative integer")


def _require_positive_int(name: str, value: int) -> None:
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")


def _require_positive_float(name: str, value: float) -> None:
    if not isinstance(value, (int, float)) or float(value) <= 0:
        raise ValueError(f"{name} must be a positive number")


@dataclass
class Task:
    """HOODIE task record with explicit paper-aligned fields.

    The legacy runtime still expects several older attribute names, so this
    class keeps compatibility aliases while making the paper variables explicit.
    """

    next_task_id: ClassVar[int] = 1
    trace_recorder: ClassVar[Any] = None

    task_id: int | None = None
    source_node_id: int | None = None
    service_id: int | None = None
    input_data_size: float | None = None
    processing_density: float | None = None
    required_cpu_cycles: float | None = None
    arrival_time: int | None = None
    timeout: int | None = None
    deadline_slot: int | None = None
    absolute_deadline: int | None = None
    routing_metadata: dict[str, Any] = field(default_factory=dict)
    target_server_id: int | None = None
    priority: int = 1
    drop_penalty: int = 1

    # Legacy / runtime fields.
    remain: float = 0.0
    queue_enter_time: int | None = None
    service_start_time: int | None = None
    service_end_time: int | None = None
    completion_time: int | None = None
    drop_time: int | None = None
    selected_action: Any = None
    processing_node: int | None = None
    latency: float | None = None
    waiting_time: float | None = None
    service_time: float | None = None
    final_status: str = "pending"
    drop_reason: str | None = None
    empty: bool = False
    paper_w_priv: int | None = None
    paper_psi_priv: int | None = None
    paper_private_queue_enter_time: int | None = None
    paper_private_service_time: int | None = None
    paper_private_deadline_slot: int | None = None
    paper_private_final_status: str | None = None

    def __init__(
        self,
        size: float | None = None,
        arrival_time: int = 0,
        timeout_delay: int = 10,
        priotiry: int = 1,
        computational_density: float = 1,
        drop_penalty: int = 1,
        origin_server_id: int | None = None,
        target_server_id: int | None = None,
        task_id: int | None = None,
        *,
        input_data_size: float | None = None,
        service_id: int | None = None,
        processing_density: float | None = None,
        timeout: int | None = None,
        source_node_id: int | None = None,
        routing_metadata: dict[str, Any] | None = None,
    ) -> None:
        if size is None and input_data_size is None:
            self.empty = True
            self.task_id = None
            self.routing_metadata = {}
            return

        raw_size = float(input_data_size if input_data_size is not None else size)
        raw_density = float(processing_density if processing_density is not None else computational_density)
        raw_timeout = int(timeout if timeout is not None else timeout_delay)
        raw_arrival = int(arrival_time)
        raw_priority = int(priotiry)

        _require_positive_float("input_data_size", raw_size)
        _require_positive_float("processing_density", raw_density)
        _require_non_negative_int("arrival_time", raw_arrival)
        _require_positive_int("timeout", raw_timeout)
        if task_id is not None:
            _require_non_negative_int("task_id", int(task_id))
        if source_node_id is not None:
            _require_non_negative_int("source_node_id", int(source_node_id))
        if target_server_id is not None:
            _require_non_negative_int("target_server_id", int(target_server_id))

        self.task_id = task_id if task_id is not None else Task.next_task_id
        Task.next_task_id = max(Task.next_task_id, self.task_id + 1)

        self.input_data_size = raw_size
        self.size = raw_size  # legacy alias
        self.remain = raw_size
        self.processing_density = raw_density
        self.computational_density = raw_density  # legacy alias
        self.required_cpu_cycles = raw_size * raw_density
        self.arrival_time = raw_arrival
        self.timeout = raw_timeout
        self.timeout_delay = raw_timeout  # legacy alias
        self.deadline_slot = raw_arrival + raw_timeout - 1
        self.absolute_deadline = self.deadline_slot
        self.timeout_instance = self.deadline_slot  # legacy alias
        self.service_id = service_id
        self.service_type_id = service_id  # optional convenience alias
        self.source_node_id = source_node_id if source_node_id is not None else origin_server_id
        self.origin_server_id = self.source_node_id  # legacy alias
        self.target_server_id = target_server_id
        self.priority = raw_priority
        self.priotiry = raw_priority  # legacy alias
        self.drop_penalty = int(drop_penalty)
        self.routing_metadata = dict(routing_metadata or {})

        self.queue_enter_time = None
        self.service_start_time = None
        self.service_end_time = None
        self.completion_time = None
        self.drop_time = None
        self.selected_action = None
        self.processing_node = None
        self.latency = None
        self.waiting_time = None
        self.service_time = None
        self.final_status = "pending"
        self.drop_reason = None
        self.empty = False
        self.paper_w_priv = None
        self.paper_psi_priv = None
        self.paper_private_queue_enter_time = None
        self.paper_private_service_time = None
        self.paper_private_deadline_slot = None
        self.paper_private_final_status = None

    def validate(self) -> None:
        if self.empty:
            raise ValueError("empty task cannot be validated")
        _require_positive_float("input_data_size", self.input_data_size)
        _require_positive_float("processing_density", self.processing_density)
        _require_non_negative_int("arrival_time", self.arrival_time)
        _require_positive_int("timeout", self.timeout)
        if self.deadline_slot != self.arrival_time + self.timeout - 1:
            raise ValueError("deadline_slot must equal arrival_time + timeout - 1")
        expected_cycles = self.input_data_size * self.processing_density
        if not np.isclose(self.required_cpu_cycles, expected_cycles):
            raise ValueError("required_cpu_cycles must equal input_data_size * processing_density")

    def drop_task(self, drop_time: int | None = None, reason: str | None = None) -> int:
        self.empty = True
        if drop_time is not None:
            self.drop_time = drop_time
        self.final_status = "dropped"
        self.drop_reason = reason
        return self.drop_penalty

    def finish_task(self, finish_time: int) -> int:
        self.empty = True
        self.service_end_time = finish_time
        self.completion_time = finish_time
        self.final_status = "completed"
        if self.service_start_time is not None:
            self.service_time = max(0, finish_time - self.service_start_time)
        if self.arrival_time is not None:
            self.latency = max(0, finish_time - self.arrival_time)
            if self.service_start_time is not None:
                self.waiting_time = max(0, self.service_start_time - self.arrival_time)
        return finish_time - self.arrival_time

    def is_empty(self) -> bool:
        return self.empty

    def process(self, capacity, time):
        self.remain -= capacity / self.computational_density
        if self.remain <= 0:
            return self.finish_task(time)
        return 0

    def public_process(self, capacity, time):
        computational_capacity = capacity
        task_processed = computational_capacity / self.computational_density
        self.remain -= task_processed
        if self.remain <= 0:
            task_processed += self.remain
            return self.finish_task(time), task_processed
        return 0, task_processed

    def transmit(self, offloading_capacity):
        if self.target_server_id is None:
            destination = self.routing_metadata.get("paper_destination_node_id")
            if destination is None:
                raise ValueError("offloaded task is missing a resolved destination")
            self.target_server_id = int(destination)
        self.remain -= offloading_capacity
        if self.remain <= 0:
            transmitted_task = Task(
                size=self.input_data_size,
                arrival_time=self.arrival_time,
                timeout_delay=self.timeout,
                priotiry=self.priority,
                computational_density=self.processing_density,
                drop_penalty=self.drop_penalty,
                origin_server_id=self.source_node_id,
                target_server_id=self.target_server_id,
                task_id=self.task_id,
                input_data_size=self.input_data_size,
                service_id=self.service_id,
                processing_density=self.processing_density,
                timeout=self.timeout,
                source_node_id=self.source_node_id,
                routing_metadata=self.routing_metadata,
            )
            transmitted_task.queue_enter_time = self.queue_enter_time
            transmitted_task.service_start_time = self.service_start_time
            transmitted_task.processing_node = self.processing_node
            self.empty = True
            return transmitted_task
        return None

    def get_size(self):
        assert not self.empty
        return self.size

    def get_relative_timeout(self):
        assert not self.empty
        return self.timeout_delay

    def get_timeout(self):
        assert not self.empty
        return self.timeout_instance

    def get_remaining_size(self):
        assert not self.empty
        return self.remain

    def get_density(self):
        assert not self.empty
        return self.computational_density

    def get_priority(self):
        assert not self.empty
        return self.priotiry

    def get_target_server_id(self):
        assert not self.empty
        return self.target_server_id

    def get_origin_server_id(self):
        assert not self.empty
        return self.origin_server_id

    def set_origin_server_id(self, origin_server_id):
        assert not self.empty
        self.origin_server_id = origin_server_id
        self.source_node_id = origin_server_id

    def set_target_server_id(self, target_server_id: int) -> None:
        assert not self.empty
        self.target_server_id = target_server_id

    def copy(self):
        copied = Task(
            size=self.size,
            arrival_time=self.arrival_time,
            timeout_delay=self.timeout_delay,
            priotiry=self.priotiry,
            computational_density=self.computational_density,
            drop_penalty=self.drop_penalty,
            origin_server_id=self.origin_server_id,
            target_server_id=self.target_server_id,
            task_id=self.task_id,
            input_data_size=self.input_data_size,
            service_id=self.service_id,
            processing_density=self.processing_density,
            timeout=self.timeout,
            source_node_id=self.source_node_id,
            routing_metadata=self.routing_metadata,
        )
        copied.queue_enter_time = self.queue_enter_time
        copied.service_start_time = self.service_start_time
        copied.service_end_time = self.service_end_time
        copied.completion_time = self.completion_time
        copied.drop_time = self.drop_time
        copied.selected_action = self.selected_action
        copied.processing_node = self.processing_node
        copied.latency = self.latency
        copied.waiting_time = self.waiting_time
        copied.service_time = self.service_time
        copied.final_status = self.final_status
        copied.drop_reason = self.drop_reason
        copied.empty = self.empty
        copied.paper_w_priv = self.paper_w_priv
        copied.paper_psi_priv = self.paper_psi_priv
        copied.paper_private_queue_enter_time = self.paper_private_queue_enter_time
        copied.paper_private_service_time = self.paper_private_service_time
        copied.paper_private_deadline_slot = self.paper_private_deadline_slot
        copied.paper_private_final_status = self.paper_private_final_status
        return copied

    def get_features(self):
        return np.array([self.size])

    def get_number_of_features(self):
        features = self.get_features()
        return len(features)
