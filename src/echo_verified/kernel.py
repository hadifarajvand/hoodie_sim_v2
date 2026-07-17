from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass, field
import math
import random
import time
from typing import Iterable, Literal, Sequence

from .control import (
    RouteEstimate,
    WaitingTask,
    apply_deadline_drop_penalty,
    assert_task_conservation,
    build_effective_route_set,
    masked_epsilon_greedy,
    select_next_waiting_task,
)

ROUTES: tuple[str, ...] = ("local", "horizontal", "cloud")
MethodName = Literal["HOODIE", "ECHO", "ECHO_DISABLED"]


@dataclass(frozen=True, slots=True)
class PilotKernelConfig:
    slot_duration_seconds: float = 0.1
    decision_slots: int = 20
    drain_slots: int = 12
    local_cpu_ghz: float = 5.0
    edge_public_cpu_ghz: float = 5.0
    cloud_cpu_ghz: float = 30.0
    horizontal_rate_mbps: float = 30.0
    vertical_rate_mbps: float = 10.0
    processing_density_gcycles_per_mbit: float = 0.297
    inherited_drop_cost: float = 40.0
    echo_deadline_drop_penalty: float = 40.0
    agent_count: int = 2

    def __post_init__(self) -> None:
        if self.agent_count != 2:
            raise ValueError("the bounded verified pilot currently supports exactly two EAs")
        if self.decision_slots <= 0 or self.drain_slots <= 0:
            raise ValueError("decision_slots and drain_slots must be positive")
        if self.slot_duration_seconds <= 0:
            raise ValueError("slot duration must be positive")
        for value in (
            self.local_cpu_ghz,
            self.edge_public_cpu_ghz,
            self.cloud_cpu_ghz,
            self.horizontal_rate_mbps,
            self.vertical_rate_mbps,
            self.processing_density_gcycles_per_mbit,
        ):
            if value <= 0:
                raise ValueError("physical capacities and density must be positive")

    @property
    def local_capacity_gcycles_per_slot(self) -> float:
        return self.local_cpu_ghz * self.slot_duration_seconds

    @property
    def edge_public_capacity_gcycles_per_slot(self) -> float:
        return self.edge_public_cpu_ghz * self.slot_duration_seconds

    @property
    def cloud_capacity_gcycles_per_slot(self) -> float:
        return self.cloud_cpu_ghz * self.slot_duration_seconds


@dataclass(frozen=True, slots=True)
class TaskBlueprint:
    task_id: str
    source_id: int
    arrival_slot: int
    deadline_slot: int
    size_mbits: float
    q_values: tuple[float, float, float]


@dataclass(slots=True)
class RuntimeTask:
    blueprint: TaskBlueprint
    cycles_required: float
    selected_route: str | None = None
    selected_destination: str | None = None
    selected_route_index: int | None = None
    physical_mask: tuple[bool, bool, bool] = (True, True, True)
    effective_mask: tuple[bool, bool, bool] = (True, True, True)
    route_predictions: dict[str, int] = field(default_factory=dict)
    route_ert: dict[str, int] = field(default_factory=dict)
    fallback_used: bool = False
    filtered_route_count: int = 0
    remaining_local_cycles: float = 0.0
    remaining_destination_cycles: float = 0.0
    remaining_tx_slots: int = 0
    private_queue_entered_slot: int | None = None
    outbound_queue_entered_slot: int | None = None
    destination_queue_entered_slot: int | None = None
    source_service_started_slot: int | None = None
    destination_service_started_slot: int | None = None
    completion_slot: int | None = None
    outcome: Literal["successful", "dropped"] | None = None
    reward: float | None = None
    location: str = "pending_arrival"
    queue_order_difference: bool = False
    queue_fallback_used: bool = False

    @property
    def task_id(self) -> str:
        return self.blueprint.task_id

    @property
    def source_id(self) -> int:
        return self.blueprint.source_id

    @property
    def arrival_slot(self) -> int:
        return self.blueprint.arrival_slot

    @property
    def deadline_slot(self) -> int:
        return self.blueprint.deadline_slot

    @property
    def size_mbits(self) -> float:
        return self.blueprint.size_mbits

    @property
    def q_values(self) -> tuple[float, float, float]:
        return self.blueprint.q_values

    @property
    def resolved(self) -> bool:
        return self.outcome is not None


@dataclass(frozen=True, slots=True)
class EpisodeResult:
    method: MethodName
    trace_id: str
    seed: int
    scenario: str
    tasks: tuple[dict[str, object], ...]
    metrics: dict[str, object]
    diagnostics: dict[str, object]


class PairedPhysicalKernel:
    """Small, transparent slot kernel for contract validation and paired pilot data.

    This is deliberately not the publication-scale HOODIE learner. It isolates the
    inherited physical lifecycle and the exact ECHO control differences on paired
    traces so integration errors can be found before DRL training is allowed.
    """

    def __init__(
        self,
        *,
        method: MethodName,
        trace_id: str,
        seed: int,
        scenario: str,
        blueprints: Sequence[TaskBlueprint],
        config: PilotKernelConfig | None = None,
    ) -> None:
        self.method = method
        self.trace_id = trace_id
        self.seed = int(seed)
        self.scenario = scenario
        self.config = config or PilotKernelConfig()
        self.controls_enabled = method == "ECHO"
        self.rng = random.Random(self.seed)
        self.tasks: dict[str, RuntimeTask] = {
            item.task_id: RuntimeTask(
                blueprint=item,
                cycles_required=(
                    item.size_mbits * self.config.processing_density_gcycles_per_mbit
                ),
            )
            for item in blueprints
        }
        if len(self.tasks) != len(blueprints):
            raise ValueError("task IDs must be unique")
        self.arrivals: dict[int, list[str]] = defaultdict(list)
        for item in blueprints:
            if item.source_id not in range(self.config.agent_count):
                raise ValueError(f"invalid source ID: {item.source_id}")
            if item.arrival_slot < 0 or item.arrival_slot >= self.config.decision_slots:
                raise ValueError(f"arrival outside decision window: {item}")
            if item.deadline_slot < item.arrival_slot:
                raise ValueError(f"deadline before arrival: {item}")
            self.arrivals[item.arrival_slot].append(item.task_id)
        for values in self.arrivals.values():
            values.sort()

        self.private_waiting: dict[int, list[str]] = defaultdict(list)
        self.outbound_waiting: dict[int, list[str]] = defaultdict(list)
        self.local_active: dict[int, str | None] = {
            source: None for source in range(self.config.agent_count)
        }
        self.tx_active: dict[int, str | None] = {
            source: None for source in range(self.config.agent_count)
        }
        self.pending_destination_admissions: dict[int, list[str]] = defaultdict(list)
        self.destination_queues: dict[tuple[str, int], list[str]] = defaultdict(list)
        self.action_counts = {route: 0 for route in ROUTES}
        self.route_candidates = 0
        self.routes_filtered = 0
        self.fallback_count = 0
        self.queue_opportunities = 0
        self.queue_order_differences = 0
        self.queue_fallback_count = 0
        self.route_control_ns = 0
        self.queue_control_ns = 0
        self.prediction_errors: dict[str, list[int]] = defaultdict(list)
        self.event_ledger: list[dict[str, object]] = []

    def _peer_destination(self, source_id: int) -> str:
        return f"edge_{1 - source_id}"

    def _destination_for_route(self, source_id: int, route: str) -> str | None:
        if route == "local":
            return None
        if route == "horizontal":
            return self._peer_destination(source_id)
        if route == "cloud":
            return "cloud"
        raise ValueError(route)

    def _service_slots_local(self, task: RuntimeTask) -> int:
        return max(
            1,
            math.ceil(
                task.cycles_required / self.config.local_capacity_gcycles_per_slot
                - 1e-12
            ),
        )

    def _transmission_slots(self, task: RuntimeTask, route: str | None = None) -> int:
        route = route or task.selected_route
        if route == "horizontal":
            rate = self.config.horizontal_rate_mbps
        elif route == "cloud":
            rate = self.config.vertical_rate_mbps
        else:
            raise ValueError(f"transmission requested for route {route!r}")
        mbits_per_slot = rate * self.config.slot_duration_seconds
        return max(1, math.ceil(task.size_mbits / mbits_per_slot - 1e-12))

    def _remaining_local_slots(self, task_id: str | None) -> int:
        if task_id is None:
            return 0
        task = self.tasks[task_id]
        return max(
            1,
            math.ceil(
                task.remaining_local_cycles
                / self.config.local_capacity_gcycles_per_slot
                - 1e-12
            ),
        )

    def _destination_capacity(self, destination: str) -> float:
        return (
            self.config.cloud_capacity_gcycles_per_slot
            if destination == "cloud"
            else self.config.edge_public_capacity_gcycles_per_slot
        )

    def _destination_active_source_count(
        self, destination: str, candidate_source: int | None = None
    ) -> int:
        active_sources = {
            source
            for (dest, source), queue in self.destination_queues.items()
            if dest == destination and queue
        }
        if candidate_source is not None:
            active_sources.add(candidate_source)
        return max(1, len(active_sources))

    def _destination_backlog_cycles(self, destination: str, source_id: int) -> float:
        return sum(
            self.tasks[task_id].remaining_destination_cycles
            for task_id in self.destination_queues.get((destination, source_id), ())
        )

    def _estimated_destination_components(
        self, task: RuntimeTask, destination: str
    ) -> tuple[int, int, int]:
        load = self._destination_active_source_count(destination, task.source_id)
        capacity = self._destination_capacity(destination)
        backlog = self._destination_backlog_cycles(destination, task.source_id)
        wait_slots = math.ceil(backlog * load / capacity - 1e-12) if backlog else 0
        service_slots = max(
            1, math.ceil(task.cycles_required * load / capacity - 1e-12)
        )
        return wait_slots, service_slots, load

    def _ordered_waiting_ids_for_estimate(
        self,
        *,
        source_id: int,
        kind: Literal["local", "outbound"],
        candidate: RuntimeTask,
        slot: int,
        candidate_route: str,
    ) -> list[str]:
        queue = (
            self.private_waiting[source_id]
            if kind == "local"
            else self.outbound_waiting[source_id]
        )
        ordered_ids = list(queue) + [candidate.task_id]
        if not self.controls_enabled:
            return ordered_ids

        scored: list[tuple[tuple[object, ...], str]] = []
        for task_id in ordered_ids:
            task = candidate if task_id == candidate.task_id else self.tasks[task_id]
            if kind == "local":
                completion = slot + self._service_slots_local(task) - 1
            else:
                route = candidate_route if task_id == candidate.task_id else task.selected_route
                if route not in {"horizontal", "cloud"}:
                    raise AssertionError("outbound task lacks committed remote route")
                destination = self._destination_for_route(task.source_id, route)
                assert destination is not None
                wait, service, _load = self._estimated_destination_components(
                    task, destination
                )
                completion = (
                    slot
                    + self._transmission_slots(task, route)
                    + wait
                    + service
                    - 1
                )
            ert = task.deadline_slot - completion
            if ert >= 0:
                key: tuple[object, ...] = (
                    0,
                    ert,
                    task.arrival_slot,
                    task.task_id,
                )
            else:
                key = (1, -ert, task.arrival_slot, task.task_id)
            scored.append((key, task_id))
        return [task_id for _key, task_id in sorted(scored)]

    def _source_wait_slots_for_candidate(
        self,
        *,
        task: RuntimeTask,
        route: str,
        slot: int,
    ) -> int:
        source = task.source_id
        if route == "local":
            residual = self._remaining_local_slots(self.local_active[source])
            order = self._ordered_waiting_ids_for_estimate(
                source_id=source,
                kind="local",
                candidate=task,
                slot=slot,
                candidate_route=route,
            )
            preceding = order[: order.index(task.task_id)]
            return residual + sum(
                self._service_slots_local(self.tasks[task_id])
                for task_id in preceding
            )

        active_id = self.tx_active[source]
        residual = self.tasks[active_id].remaining_tx_slots if active_id else 0
        order = self._ordered_waiting_ids_for_estimate(
            source_id=source,
            kind="outbound",
            candidate=task,
            slot=slot,
            candidate_route=route,
        )
        preceding = order[: order.index(task.task_id)]
        return residual + sum(
            self._transmission_slots(self.tasks[task_id]) for task_id in preceding
        )

    def _route_estimates(self, task: RuntimeTask, slot: int) -> tuple[RouteEstimate, ...]:
        estimates: list[RouteEstimate] = []
        local_wait = self._source_wait_slots_for_candidate(
            task=task, route="local", slot=slot
        )
        local_completion = slot + local_wait + self._service_slots_local(task) - 1
        estimates.append(
            RouteEstimate("local", 0, local_completion, task.deadline_slot, True)
        )
        for index, route in ((1, "horizontal"), (2, "cloud")):
            destination = self._destination_for_route(task.source_id, route)
            assert destination is not None
            outbound_wait = self._source_wait_slots_for_candidate(
                task=task, route=route, slot=slot
            )
            dest_wait, dest_service, _load = self._estimated_destination_components(
                task, destination
            )
            completion = (
                slot
                + outbound_wait
                + self._transmission_slots(task, route)
                + dest_wait
                + dest_service
                - 1
            )
            estimates.append(
                RouteEstimate(route, index, completion, task.deadline_slot, True)
            )
        return tuple(estimates)

    def _admit_arrival(self, task_id: str, slot: int) -> None:
        task = self.tasks[task_id]
        started = time.perf_counter_ns()
        estimates = self._route_estimates(task, slot)
        self.route_candidates += len(estimates)
        if self.controls_enabled:
            effective = build_effective_route_set(estimates)
            mask = effective.mask
            task.fallback_used = effective.fallback_route_id is not None
            task.filtered_route_count = len(effective.filtered_route_ids)
            self.routes_filtered += task.filtered_route_count
            self.fallback_count += int(task.fallback_used)
        else:
            mask = (True, True, True)
        selected_index = masked_epsilon_greedy(
            task.q_values, mask, epsilon=0.0, rng=self.rng
        )
        self.route_control_ns += time.perf_counter_ns() - started
        selected_route = ROUTES[selected_index]
        task.selected_route = selected_route
        task.selected_route_index = selected_index
        task.selected_destination = self._destination_for_route(task.source_id, selected_route)
        task.effective_mask = tuple(bool(value) for value in mask)  # type: ignore[assignment]
        task.route_predictions = {
            estimate.route_id: estimate.predicted_completion_slot for estimate in estimates
        }
        task.route_ert = {estimate.route_id: estimate.ert_slots for estimate in estimates}
        self.action_counts[selected_route] += 1

        if selected_route == "local":
            task.remaining_local_cycles = task.cycles_required
            task.private_queue_entered_slot = slot
            task.location = "private_waiting"
            self.private_waiting[task.source_id].append(task.task_id)
        else:
            task.remaining_tx_slots = self._transmission_slots(task, selected_route)
            task.remaining_destination_cycles = task.cycles_required
            task.outbound_queue_entered_slot = slot
            task.location = "outbound_waiting"
            self.outbound_waiting[task.source_id].append(task.task_id)

        self.event_ledger.append(
            {
                "slot": slot,
                "event": "arrival_route_committed",
                "task_id": task.task_id,
                "method": self.method,
                "selected_route": selected_route,
                "selected_destination": task.selected_destination or "self",
                "effective_mask": ";".join("1" if value else "0" for value in mask),
                "fallback_used": task.fallback_used,
            }
        )

    def _select_local_waiting(self, source: int, slot: int) -> str:
        queue = self.private_waiting[source]
        fifo_head = queue[0]
        if not self.controls_enabled:
            selected = fifo_head
            queue_fallback = False
        else:
            started = time.perf_counter_ns()
            result = select_next_waiting_task(
                [
                    WaitingTask(
                        task_id=task_id,
                        arrival_slot=self.tasks[task_id].arrival_slot,
                        deadline_slot=self.tasks[task_id].deadline_slot,
                        source_service_slots=self._service_slots_local(
                            self.tasks[task_id]
                        ),
                    )
                    for task_id in queue
                ],
                current_slot=slot,
            )
            self.queue_control_ns += time.perf_counter_ns() - started
            if result.selected is None:
                raise AssertionError("non-empty local queue produced no selection")
            selected = result.selected.task_id
            queue_fallback = result.used_minimum_lateness
        self.queue_opportunities += 1
        differs = selected != fifo_head
        self.queue_order_differences += int(differs)
        self.queue_fallback_count += int(queue_fallback)
        task = self.tasks[selected]
        task.queue_order_difference = task.queue_order_difference or differs
        task.queue_fallback_used = task.queue_fallback_used or queue_fallback
        queue.remove(selected)
        return selected

    def _select_outbound_waiting(self, source: int, slot: int) -> str:
        queue = self.outbound_waiting[source]
        fifo_head = queue[0]
        if not self.controls_enabled:
            selected = fifo_head
            queue_fallback = False
        else:
            started = time.perf_counter_ns()
            waiting: list[WaitingTask] = []
            for task_id in queue:
                task = self.tasks[task_id]
                assert task.selected_route in {"horizontal", "cloud"}
                assert task.selected_destination is not None
                dest_wait, dest_service, _load = self._estimated_destination_components(
                    task, task.selected_destination
                )
                waiting.append(
                    WaitingTask(
                        task_id=task.task_id,
                        arrival_slot=task.arrival_slot,
                        deadline_slot=task.deadline_slot,
                        source_service_slots=self._transmission_slots(task),
                        downstream_slots=dest_wait + dest_service,
                    )
                )
            result = select_next_waiting_task(waiting, current_slot=slot)
            self.queue_control_ns += time.perf_counter_ns() - started
            if result.selected is None:
                raise AssertionError("non-empty outbound queue produced no selection")
            selected = result.selected.task_id
            queue_fallback = result.used_minimum_lateness
        self.queue_opportunities += 1
        differs = selected != fifo_head
        self.queue_order_differences += int(differs)
        self.queue_fallback_count += int(queue_fallback)
        task = self.tasks[selected]
        task.queue_order_difference = task.queue_order_difference or differs
        task.queue_fallback_used = task.queue_fallback_used or queue_fallback
        queue.remove(selected)
        return selected

    def _start_idle_source_resources(self, slot: int) -> None:
        for source in range(self.config.agent_count):
            if self.local_active[source] is None and self.private_waiting[source]:
                selected = self._select_local_waiting(source, slot)
                self.local_active[source] = selected
                task = self.tasks[selected]
                task.source_service_started_slot = slot
                task.location = "local_active"
                self.event_ledger.append(
                    {"slot": slot, "event": "local_service_started", "task_id": selected}
                )
            if self.tx_active[source] is None and self.outbound_waiting[source]:
                selected = self._select_outbound_waiting(source, slot)
                self.tx_active[source] = selected
                task = self.tasks[selected]
                task.source_service_started_slot = slot
                task.location = "tx_active"
                self.event_ledger.append(
                    {"slot": slot, "event": "transmission_started", "task_id": selected}
                )

    def _admit_completed_transmissions(self, slot: int) -> None:
        for task_id in sorted(self.pending_destination_admissions.pop(slot, [])):
            task = self.tasks[task_id]
            if task.resolved:
                continue
            assert task.selected_destination is not None
            queue = self.destination_queues[(task.selected_destination, task.source_id)]
            queue.append(task_id)
            task.destination_queue_entered_slot = slot
            task.location = "destination_waiting"
            self.event_ledger.append(
                {
                    "slot": slot,
                    "event": "destination_admitted",
                    "task_id": task_id,
                    "destination": task.selected_destination,
                }
            )

    def _execute_slot(self, slot: int) -> list[str]:
        completed: list[str] = []
        for source, task_id in tuple(self.local_active.items()):
            if task_id is None:
                continue
            task = self.tasks[task_id]
            task.remaining_local_cycles = max(
                0.0,
                task.remaining_local_cycles
                - self.config.local_capacity_gcycles_per_slot,
            )
            if task.remaining_local_cycles <= 1e-12:
                completed.append(task_id)
                self.local_active[source] = None

        for source, task_id in tuple(self.tx_active.items()):
            if task_id is None:
                continue
            task = self.tasks[task_id]
            task.remaining_tx_slots -= 1
            if task.remaining_tx_slots <= 0:
                self.tx_active[source] = None
                task.location = "pending_destination_admission"
                self.pending_destination_admissions[slot + 1].append(task_id)
                self.event_ledger.append(
                    {
                        "slot": slot,
                        "event": "transmission_completed",
                        "task_id": task_id,
                        "admission_slot": slot + 1,
                    }
                )

        destinations = sorted({destination for destination, _source in self.destination_queues})
        for destination in destinations:
            active_queues: list[tuple[int, list[str]]] = []
            for (dest, source), queue in sorted(self.destination_queues.items()):
                if dest != destination or not queue:
                    continue
                head = self.tasks[queue[0]]
                if head.destination_queue_entered_slot == slot:
                    continue
                active_queues.append((source, queue))
            if not active_queues:
                continue
            share = self._destination_capacity(destination) / len(active_queues)
            completed_heads: list[tuple[int, str]] = []
            for source, queue in active_queues:
                task_id = queue[0]
                task = self.tasks[task_id]
                if task.destination_service_started_slot is None:
                    task.destination_service_started_slot = slot
                task.location = "destination_active"
                task.remaining_destination_cycles = max(
                    0.0, task.remaining_destination_cycles - share
                )
                if task.remaining_destination_cycles <= 1e-12:
                    completed_heads.append((source, task_id))
            for source, task_id in completed_heads:
                queue = self.destination_queues[(destination, source)]
                if not queue or queue[0] != task_id:
                    raise AssertionError("destination FIFO head changed during a slot")
                queue.pop(0)
                completed.append(task_id)
        return completed

    def _base_reward(self, task: RuntimeTask, outcome: str, slot: int) -> float:
        if outcome == "successful":
            delay_seconds = (
                slot - task.arrival_slot + 1
            ) * self.config.slot_duration_seconds
            return -float(delay_seconds)
        return -float(self.config.inherited_drop_cost)

    def _resolve_success(self, task_id: str, slot: int) -> None:
        task = self.tasks[task_id]
        if task.resolved:
            raise AssertionError(f"task resolved twice: {task_id}")
        task.completion_slot = slot
        task.outcome = "successful"
        base = self._base_reward(task, "successful", slot)
        task.reward = apply_deadline_drop_penalty(
            base,
            dropped=False,
            fixed_penalty=(
                self.config.echo_deadline_drop_penalty
                if self.controls_enabled
                else 0.0
            ),
        )
        task.location = "resolved"
        selected = task.selected_route
        if selected is not None and selected in task.route_predictions:
            self.prediction_errors[selected].append(
                slot - task.route_predictions[selected]
            )
        self.event_ledger.append(
            {"slot": slot, "event": "task_success", "task_id": task_id}
        )

    def _remove_from_structures(self, task_id: str) -> None:
        task = self.tasks[task_id]
        source = task.source_id
        if self.local_active[source] == task_id:
            self.local_active[source] = None
        if self.tx_active[source] == task_id:
            self.tx_active[source] = None
        for queue in (self.private_waiting[source], self.outbound_waiting[source]):
            if task_id in queue:
                queue.remove(task_id)
        for slot, values in list(self.pending_destination_admissions.items()):
            if task_id in values:
                values.remove(task_id)
            if not values:
                self.pending_destination_admissions.pop(slot, None)
        for key, queue in self.destination_queues.items():
            if task_id in queue:
                queue.remove(task_id)

    def _resolve_drop(self, task_id: str, slot: int) -> None:
        task = self.tasks[task_id]
        if task.resolved:
            return
        self._remove_from_structures(task_id)
        task.outcome = "dropped"
        base = self._base_reward(task, "dropped", slot)
        task.reward = apply_deadline_drop_penalty(
            base,
            dropped=self.controls_enabled,
            fixed_penalty=self.config.echo_deadline_drop_penalty,
        )
        task.location = "resolved"
        self.event_ledger.append(
            {"slot": slot, "event": "task_drop", "task_id": task_id}
        )

    def _drop_expired_at_end_of_slot(self, slot: int) -> None:
        for task in sorted(self.tasks.values(), key=lambda item: item.task_id):
            if task.resolved or task.arrival_slot > slot:
                continue
            if task.deadline_slot == slot:
                self._resolve_drop(task.task_id, slot)

    def _task_record(self, task: RuntimeTask) -> dict[str, object]:
        if task.outcome is None or task.reward is None:
            raise AssertionError(f"unresolved task: {task.task_id}")
        successful = task.outcome == "successful"
        actual_delay_slots = (
            task.completion_slot - task.arrival_slot + 1
            if task.completion_slot is not None
            else None
        )
        return {
            "trace_id": self.trace_id,
            "seed": self.seed,
            "scenario": self.scenario,
            "method": self.method,
            "task_id": task.task_id,
            "source": task.source_id,
            "arrival_slot": task.arrival_slot,
            "deadline_slot": task.deadline_slot,
            "size_mbits": task.size_mbits,
            "processing_density_gcycles_per_mbit": self.config.processing_density_gcycles_per_mbit,
            "q_local": task.q_values[0],
            "q_horizontal": task.q_values[1],
            "q_cloud": task.q_values[2],
            "predicted_local_completion": task.route_predictions.get("local"),
            "predicted_horizontal_completion": task.route_predictions.get("horizontal"),
            "predicted_cloud_completion": task.route_predictions.get("cloud"),
            "ert_local": task.route_ert.get("local"),
            "ert_horizontal": task.route_ert.get("horizontal"),
            "ert_cloud": task.route_ert.get("cloud"),
            "effective_mask": ";".join("1" if value else "0" for value in task.effective_mask),
            "fallback_used": task.fallback_used,
            "selected_route": task.selected_route,
            "selected_destination": task.selected_destination or "self",
            "queue_order_difference": task.queue_order_difference,
            "queue_fallback_used": task.queue_fallback_used,
            "completion_slot": task.completion_slot,
            "successful": successful,
            "dropped": not successful,
            "successful_delay_slots": actual_delay_slots,
            "successful_delay_seconds": (
                actual_delay_slots * self.config.slot_duration_seconds
                if actual_delay_slots is not None
                else None
            ),
            "reward": task.reward,
        }

    def run(self) -> EpisodeResult:
        max_deadline = max(
            (task.deadline_slot for task in self.tasks.values()),
            default=self.config.decision_slots - 1,
        )
        final_slot = max(
            self.config.decision_slots + self.config.drain_slots - 1,
            max_deadline,
        )
        for slot in range(final_slot + 1):
            self._admit_completed_transmissions(slot)
            for task_id in self.arrivals.get(slot, ()):
                self._admit_arrival(task_id, slot)
            self._start_idle_source_resources(slot)
            completed = self._execute_slot(slot)
            for task_id in sorted(set(completed)):
                task = self.tasks[task_id]
                if slot <= task.deadline_slot:
                    self._resolve_success(task_id, slot)
                else:
                    self._resolve_drop(task_id, slot)
            self._drop_expired_at_end_of_slot(slot)

        unresolved = [task.task_id for task in self.tasks.values() if not task.resolved]
        if unresolved:
            raise AssertionError(f"unresolved tasks after drain: {unresolved}")
        records = tuple(
            self._task_record(task)
            for task in sorted(self.tasks.values(), key=lambda item: item.task_id)
        )
        generated = len(records)
        successful = sum(bool(row["successful"]) for row in records)
        dropped = sum(bool(row["dropped"]) for row in records)
        assert_task_conservation(
            generated=generated, successful=successful, dropped=dropped
        )
        delays = [
            float(row["successful_delay_seconds"])
            for row in records
            if row["successful_delay_seconds"] is not None
        ]
        metrics: dict[str, object] = {
            "generated": generated,
            "successful": successful,
            "dropped": dropped,
            "drop_ratio": dropped / generated if generated else 0.0,
            "average_successful_delay_seconds": (
                sum(delays) / len(delays) if delays else 0.0
            ),
            "accumulated_reward": sum(float(row["reward"]) for row in records),
            "action_local": self.action_counts["local"],
            "action_horizontal": self.action_counts["horizontal"],
            "action_cloud": self.action_counts["cloud"],
        }
        signed_errors = [
            value for values in self.prediction_errors.values() for value in values
        ]
        diagnostics: dict[str, object] = {
            "route_filter_fraction": (
                self.routes_filtered / self.route_candidates
                if self.route_candidates
                else 0.0
            ),
            "fallback_frequency": (
                self.fallback_count / generated if generated else 0.0
            ),
            "source_queue_order_difference_fraction": (
                self.queue_order_differences / self.queue_opportunities
                if self.queue_opportunities
                else 0.0
            ),
            "queue_minimum_lateness_frequency": (
                self.queue_fallback_count / self.queue_opportunities
                if self.queue_opportunities
                else 0.0
            ),
            "mean_route_control_ns_per_arrival": (
                self.route_control_ns / generated if generated else 0.0
            ),
            "mean_queue_control_ns_per_opportunity": (
                self.queue_control_ns / self.queue_opportunities
                if self.queue_opportunities
                else 0.0
            ),
            "completion_estimation_signed_error_slots": (
                sum(signed_errors) / len(signed_errors) if signed_errors else 0.0
            ),
            "completion_estimation_mae_slots": (
                sum(abs(value) for value in signed_errors) / len(signed_errors)
                if signed_errors
                else 0.0
            ),
            "ert_in_neural_observation": False,
            "destination_queue_order": "FIFO",
            "destination_capacity_rule": "equal_share_no_same_slot_redistribution",
            "active_service_preemption": False,
        }
        return EpisodeResult(
            method=self.method,
            trace_id=self.trace_id,
            seed=self.seed,
            scenario=self.scenario,
            tasks=records,
            metrics=metrics,
            diagnostics=diagnostics,
        )


def generate_trace(
    *,
    seed: int,
    episode_index: int,
    scenario: str,
    config: PilotKernelConfig,
    arrival_probability: float,
    timeout_slots: int,
) -> tuple[TaskBlueprint, ...]:
    if not 0.0 <= arrival_probability <= 1.0:
        raise ValueError("arrival_probability must be in [0, 1]")
    if timeout_slots <= 0:
        raise ValueError("timeout_slots must be positive")
    rng = random.Random(seed * 1_000_003 + episode_index * 97 + 11)
    tasks: list[TaskBlueprint] = []
    counter = 0
    for slot in range(config.decision_slots):
        for source in range(config.agent_count):
            if rng.random() >= arrival_probability:
                continue
            counter += 1
            size = rng.choice((2.0, 2.5, 3.0, 4.0, 5.0))
            # Shared learned-Q proxy. Both methods receive identical values.
            # Remote actions are often attractive, which lets ECHO filtering be
            # exercised under congestion without manufacturing expected outcomes.
            q_local = 1.0 + rng.uniform(-0.15, 0.25) - 0.04 * size
            q_horizontal = 2.1 + rng.uniform(-0.25, 0.35) + 0.03 * size
            q_cloud = 1.8 + rng.uniform(-0.20, 0.30) + 0.02 * size
            tasks.append(
                TaskBlueprint(
                    task_id=f"{scenario}-s{seed}-e{episode_index}-t{counter:04d}",
                    source_id=source,
                    arrival_slot=slot,
                    deadline_slot=slot + timeout_slots - 1,
                    size_mbits=size,
                    q_values=(q_local, q_horizontal, q_cloud),
                )
            )
    return tuple(tasks)


def assert_echo_disabled_equivalence(
    hoodie: EpisodeResult, echo_disabled: EpisodeResult
) -> None:
    if hoodie.trace_id != echo_disabled.trace_id or hoodie.seed != echo_disabled.seed:
        raise AssertionError("equivalence results are not paired")
    ignored = {"method"}
    hoodie_rows = [
        {key: value for key, value in row.items() if key not in ignored}
        for row in hoodie.tasks
    ]
    disabled_rows = [
        {key: value for key, value in row.items() if key not in ignored}
        for row in echo_disabled.tasks
    ]
    if hoodie_rows != disabled_rows:
        raise AssertionError("ECHO-disabled task ledger differs from HOODIE")
    if hoodie.metrics != echo_disabled.metrics:
        raise AssertionError("ECHO-disabled metrics differ from HOODIE")


def episode_result_to_dict(result: EpisodeResult) -> dict[str, object]:
    return {
        "method": result.method,
        "trace_id": result.trace_id,
        "seed": result.seed,
        "scenario": result.scenario,
        "tasks": list(result.tasks),
        "metrics": result.metrics,
        "diagnostics": result.diagnostics,
    }
