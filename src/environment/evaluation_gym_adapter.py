from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from math import ceil
from typing import Any

from src.echo_queue_ordering import construct_ert_order
from src.evaluation.trace_protocol import EvaluationTrace
from src.policies.action_masking import select_legal_action
from src.policies.policy_interface import PolicyContext

from .environment import apply_policy_action
from .gym_adapter import HoodieGymEnvironment
from .link_rate_config import compute_transmission_delay, mbits_to_bits
from .offload_trace_ledger import OffloadTraceLedger
from .task import Task


@dataclass(slots=True)
class EvaluationHoodieGymEnvironment(HoodieGymEnvironment):
    """Paired-trace environment with synchronized multi-EA decisions.

    The adapter preserves the common physical simulator while enforcing the
    paper contracts that are required for fair HOODIE/ECHO evaluation:

    * every EA has an independent same-slot arrival opportunity;
    * all decisions at a slot are admitted before physical service advances;
    * each source EA owns one non-preemptive outbound transmitter even though
      tasks remain stored in destination-indexed containers internally;
    * ECHO alone reconstructs local and outbound waiting order through the
      deterministic O(q^2) ERT procedure;
    * unresolved tasks are counted as dropped at the episode horizon.
    """

    supplied_trace: EvaluationTrace | None = None
    _active_transmission_task_ids: dict[str, int] = field(default_factory=dict)

    @property
    def _echo_enabled(self) -> bool:
        return self.policy_name.upper().startswith("ECHO")

    def reset(self, seed: int | None = None):
        super().reset(seed=seed)
        self._active_transmission_task_ids.clear()
        if self.supplied_trace is None:
            return self.observe(), self._build_info()

        self.trace = self.supplied_trace
        self._pending_arrivals.clear()
        self._active_tasks.clear()
        self._current_task = None
        for blueprint in sorted(self.trace.tasks, key=self._trace_sort_key):
            self._pending_arrivals[blueprint.arrival_slot].append(blueprint)
        for blueprints in self._pending_arrivals.values():
            blueprints.sort(key=self._trace_sort_key)

        self._current_task = self._load_current_task()
        return self.observe(), self._build_info()

    def step_slot(self, policy: Any):
        if self.trace is None:
            raise RuntimeError("Environment must be reset before stepping")

        reward = 0.0
        decision_events: list[dict[str, Any]] = []
        task_resolution_events: list[dict[str, Any]] = []
        reward_delivery_events: list[dict[str, Any]] = []
        selected_action_emitted = False

        reward_delivery_events.extend(self._deliver_pending_rewards(self.current_slot))
        if reward_delivery_events:
            reward += sum(float(event["reward"]) for event in reward_delivery_events)

        # Boundary phase: remove expired waiting work, but retain resources used
        # by active non-preemptive computation and transmission.
        finalized_tasks = self._expire_waiting_tasks()
        for task in finalized_tasks:
            task_resolution_events.append(
                self._build_task_resolution_event(task, resolution_slot=self.current_slot)
            )
            self._register_pending_reward(task)

        # Decision phase: process every task whose EA has an arrival in this
        # physical slot without moving the simulator clock.
        while (
            self._current_task is not None
            and self._current_task.arrival_slot <= self.current_slot
        ):
            current_task = self._current_task
            observation = self.observe_flat(current_task)
            legal_action_mask = observation.get("legal_action_mask", {})
            context = PolicyContext(
                observation=observation,
                legal_action_mask=legal_action_mask,
                trace_history=(self.trace.trace_id,),
            )
            requested_action = policy.choose_action(context)
            selected_action = select_legal_action(context, requested_action)

            current_task.metadata["legal_action_mask"] = dict(legal_action_mask)
            current_task.metadata["selected_action_family"] = self._selected_action_family(
                selected_action
            )
            current_task.metadata["action_index"] = self._canonical_action_index(
                selected_action
            )
            current_task.metadata["decision_event_id"] = (
                f"{self.trace.trace_id}:{self.current_slot}:{current_task.task_id}"
            )
            current_task.metadata["selected_action_trace_source"] = "decision_point"
            current_task.metadata["selected_action_to_task_join_key"] = (
                f"{self.trace.trace_id}:{current_task.task_id}"
            )
            current_task.metadata["terminal_outcome_join_key"] = (
                f"{self.trace.trace_id}:{current_task.task_id}:terminal_outcome"
            )
            current_task.metadata["strategy"] = self.policy_name
            current_task.metadata["seed"] = self.seed
            current_task.metadata["agent_id"] = current_task.source_agent_id

            resolved_destination = self._resolve_destination(
                current_task, selected_action
            )
            apply_policy_action(
                current_task,
                context,
                selected_action,
                resolved_destination=resolved_destination,
            )
            decision_events.append(
                {
                    "task_id": current_task.task_id,
                    "source_agent_id": current_task.source_agent_id,
                    "decision_slot": self.current_slot,
                    "state": dict(observation),
                    "action": selected_action,
                    "legal_action_mask": dict(legal_action_mask),
                    "resolved_destination": resolved_destination,
                }
            )

            ledger = OffloadTraceLedger()
            ledger.emit("selected_action")
            self._trace_ledgers[current_task.task_id] = ledger
            self._admit_current_task(current_task)
            self._repair_link_metadata(current_task, selected_action)
            selected_action_emitted = True

            self._current_task = None
            self._current_task = self._load_current_task()

        # Scheduling phase.  HOODIE keeps FIFO source order.  ECHO reconstructs
        # the waiting prefix while any already active head remains fixed.
        if self._echo_enabled:
            self._rebuild_echo_private_orders()
            self._rank_echo_transfer_orders()
        self._prepare_execution_heads()

        # Service phase: each source transmitter and each compute resource
        # advances exactly once irrespective of the number of decisions above.
        self._progress_grouped_offloading_queues()
        service_finalized = self._progress_execution_queues()
        finalized_tasks.extend(service_finalized)
        for task in service_finalized:
            task_resolution_events.append(
                self._build_task_resolution_event(task, resolution_slot=self.current_slot)
            )
            self._register_pending_reward(task)

        if (
            not selected_action_emitted
            and not finalized_tasks
            and self._current_task is None
            and self.queue_load == 0
        ):
            reward = float("nan")

        self.engine.current_slot = self.current_slot
        self.current_slot += 1
        self._current_task = self._load_current_task()
        truncated = self.current_slot >= self.episode_length
        terminated = self._is_terminated() and not truncated

        if truncated:
            horizon_slot = max(0, self.episode_length - 1)
            horizon_drops = self._finalize_unresolved_at_horizon(horizon_slot)
            for task in horizon_drops:
                task_resolution_events.append(
                    self._build_task_resolution_event(task, resolution_slot=horizon_slot)
                )
                self._register_pending_reward(task)
            finalized_tasks.extend(horizon_drops)
            self._pending_arrivals.clear()
            self._current_task = None

        if finalized_tasks:
            self._last_finalized_tasks = list(finalized_tasks)

        if terminated or truncated:
            reward_delivery_events.extend(self._flush_pending_rewards(self.current_slot))
            if reward_delivery_events:
                reward = sum(float(event["reward"]) for event in reward_delivery_events)

        observation = self.observe()
        info = self._build_info(
            finalized_tasks=finalized_tasks,
            reward=reward,
            terminated=terminated,
            truncated=truncated,
            task_resolution_events=task_resolution_events,
            reward_delivery_events=reward_delivery_events,
        )
        info["decision_events"] = decision_events
        info["physical_slot"] = self.current_slot - 1
        info["queue_order_candidate_evaluations"] = int(
            self._metrics.get("queue_order_candidate_evaluations", 0.0)
        )
        return observation, reward, terminated, truncated, info

    def _repair_link_metadata(self, task: Task, selected_action: str) -> None:
        if selected_action.startswith("horizontal_") or selected_action in {
            "horizontal",
            "offload_horizontal",
        }:
            data_rate_bps = self.link_rate_config.horizontal_data_rate_bps
            source = "horizontal_R_H"
        elif selected_action in {"cloud", "vertical", "offload_vertical"}:
            data_rate_bps = self.link_rate_config.vertical_data_rate_bps
            source = "vertical_R_V"
        else:
            return
        payload_bits = mbits_to_bits(task.size)
        transmission_delay = compute_transmission_delay(
            payload_bits,
            data_rate_bps,
            slot_duration_seconds=self.link_rate_config.slot_duration_seconds,
            rounding_policy=self.link_rate_config.rounding_policy,
        )
        task.metadata["transmission_delay_slots"] = transmission_delay.delay_slots
        task.metadata["transmission_delay_seconds"] = transmission_delay.delay_seconds
        task.metadata["transmission_payload_bits"] = payload_bits
        task.metadata["transmission_data_rate_bps"] = data_rate_bps
        task.metadata["transmission_rate_source"] = source
        task.metadata["transmission_rounding_policy"] = (
            transmission_delay.slot_rounding_policy
        )

    def _expire_waiting_tasks(self) -> list[Task]:
        expired: list[Task] = []

        for queue in self._private_queues.values():
            active_id = None
            if queue.tasks:
                head = queue.tasks[0]
                if head.cycles_remaining < head.cycles_required:
                    active_id = head.task_id
            retained = deque()
            for task in queue.tasks:
                if task.task_id != active_id and self.current_slot > task.absolute_deadline_slot:
                    task.mark_resolution(
                        slot=self.current_slot,
                        outcome="dropped",
                        reason="private_waiting_deadline_expired",
                    )
                    expired.append(task)
                else:
                    retained.append(task)
            queue.tasks = retained
            queue.current_head_entered_at = (
                int(retained[0].metadata.get("queue_entered_at", self.current_slot))
                if retained
                else None
            )

        for (source_id, _destination), queue in self._offloading_queues.items():
            active_id = self._active_transmission_task_ids.get(source_id)
            retained = deque()
            for task in queue.tasks:
                if task.task_id != active_id and self.current_slot > task.absolute_deadline_slot:
                    task.mark_resolution(
                        slot=self.current_slot,
                        outcome="dropped",
                        reason="transfer_waiting_deadline_expired",
                    )
                    expired.append(task)
                else:
                    retained.append(task)
            queue.tasks = retained
            queue.current_head_entered_at = (
                int(retained[0].metadata.get("queue_entered_at", self.current_slot))
                if retained
                else None
            )

        for queue in self._public_queues.values():
            active_id = None
            if queue.tasks:
                head = queue.tasks[0]
                if head.cycles_remaining < head.cycles_required:
                    active_id = head.task_id
            retained = deque()
            for task in queue.tasks:
                if task.task_id != active_id and self.current_slot > task.absolute_deadline_slot:
                    task.mark_resolution(
                        slot=self.current_slot,
                        outcome="dropped",
                        reason="destination_waiting_deadline_expired",
                    )
                    expired.append(task)
                else:
                    retained.append(task)
            queue.tasks = retained
            queue.current_head_entered_at = (
                int(retained[0].metadata.get("queue_entered_at", self.current_slot))
                if retained
                else None
            )

        return expired

    def _rebuild_echo_private_orders(self) -> None:
        capacity = self.compute_config.cpu_capacity_per_slot_agent
        for queue in self._private_queues.values():
            tasks = list(queue.tasks)
            if len(tasks) <= 1:
                continue
            head = tasks[0]
            active = head.cycles_remaining < head.cycles_required
            fixed = [head] if active else []
            waiting = tasks[1:] if active else tasks
            residual = (
                max(1, int(ceil(head.cycles_remaining / capacity)))
                if active
                else 0
            )
            result = construct_ert_order(
                waiting,
                current_slot=self.current_slot,
                residual_source_slots=residual,
                service_slots=lambda task: max(
                    1, int(ceil(task.cycles_required / capacity))
                ),
                downstream_slots=lambda _task: 0,
                deadline_slot=lambda task: task.absolute_deadline_slot,
                arrival_slot=lambda task: task.arrival_slot,
                stable_id=lambda task: task.task_id,
            )
            queue.tasks = deque(fixed + list(result.ordered_items))
            queue.current_head_entered_at = int(
                queue.tasks[0].metadata.get("queue_entered_at", self.current_slot)
            )
            for estimate in result.estimates:
                estimate.item.metadata["echo_local_queue_completion_slot"] = (
                    estimate.completion_slot
                )
                estimate.item.metadata["echo_local_queue_ert_slots"] = estimate.ert_slots
                estimate.item.metadata["echo_local_queue_lateness_slots"] = (
                    estimate.lateness_slots
                )
            self._metrics["queue_order_candidate_evaluations"] = self._metrics.get(
                "queue_order_candidate_evaluations", 0.0
            ) + float(result.candidate_evaluations)

    def _rank_echo_transfer_orders(self) -> None:
        grouped: dict[str, list[Task]] = defaultdict(list)
        for (source_id, _destination), queue in self._offloading_queues.items():
            grouped[source_id].extend(queue.tasks)

        for source_id, tasks in grouped.items():
            active_id = self._active_transmission_task_ids.get(source_id)
            active = next(
                (task for task in tasks if task.task_id == active_id),
                None,
            )
            waiting = [task for task in tasks if task is not active]
            residual = 0
            if active is not None:
                started = int(active.metadata.get("transmission_started_at", self.current_slot))
                delay = int(active.metadata.get("transmission_delay_slots", 1))
                residual = max(1, started + delay - self.current_slot)
            result = construct_ert_order(
                waiting,
                current_slot=self.current_slot,
                residual_source_slots=residual,
                service_slots=lambda task: max(
                    1, int(task.metadata.get("transmission_delay_slots", 1))
                ),
                downstream_slots=self._destination_tail_slots,
                deadline_slot=lambda task: task.absolute_deadline_slot,
                arrival_slot=lambda task: task.arrival_slot,
                stable_id=lambda task: task.task_id,
            )
            for rank, estimate in enumerate(result.estimates):
                estimate.item.metadata["echo_transfer_rank"] = rank
                estimate.item.metadata["echo_transfer_completion_slot"] = (
                    estimate.completion_slot
                )
                estimate.item.metadata["echo_transfer_ert_slots"] = estimate.ert_slots
                estimate.item.metadata["echo_transfer_lateness_slots"] = (
                    estimate.lateness_slots
                )
            self._metrics["queue_order_candidate_evaluations"] = self._metrics.get(
                "queue_order_candidate_evaluations", 0.0
            ) + float(result.candidate_evaluations)

    def _destination_tail_slots(self, task: Task) -> int:
        destination = str(task.resolved_destination)
        source_id = str(task.source_agent_id)
        active_queues = [
            queue
            for (host, _source), queue in self._public_queues.items()
            if host == destination and queue.tasks
        ]
        own_queue = self._public_queues.get((destination, source_id))
        adjusted_count = len(active_queues)
        if own_queue is None or not own_queue.tasks:
            adjusted_count += 1
        adjusted_count = max(1, adjusted_count)
        capacity_pool = (
            self.compute_config.cpu_capacity_per_slot_cloud
            if destination == "cloud"
            else self.compute_config.cpu_capacity_per_slot_edge
        )
        effective_capacity = capacity_pool / float(adjusted_count)
        existing_work = (
            sum(float(item.cycles_remaining) for item in own_queue.tasks)
            if own_queue is not None
            else 0.0
        )
        waiting_slots = (
            int(ceil(existing_work / effective_capacity))
            if existing_work > 0.0
            else 0
        )
        service_slots = max(
            1, int(ceil(float(task.cycles_required) / effective_capacity))
        )
        return waiting_slots + service_slots

    def _prepare_execution_heads(self) -> None:
        for queue in self._private_queues.values():
            if queue.tasks:
                head = queue.tasks[0]
                if head.computation_start_slot is None:
                    head.computation_start_slot = self.current_slot
                    head.metadata["computation_start_slot"] = self.current_slot
        for queue in self._public_queues.values():
            if not queue.tasks or queue.current_head_entered_at == self.current_slot:
                continue
            head = queue.tasks[0]
            if head.computation_start_slot is None:
                head.computation_start_slot = self.current_slot
                head.metadata["computation_start_slot"] = self.current_slot

    def _progress_grouped_offloading_queues(self) -> None:
        sources = sorted({source for source, _destination in self._offloading_queues})
        for source_id in sources:
            queue_items = [
                (key, queue, task)
                for key, queue in self._offloading_queues.items()
                if key[0] == source_id
                for task in queue.tasks
            ]
            if not queue_items:
                self._active_transmission_task_ids.pop(source_id, None)
                continue

            active_id = self._active_transmission_task_ids.get(source_id)
            selected = next(
                (item for item in queue_items if item[2].task_id == active_id),
                None,
            )
            if selected is None:
                if self._echo_enabled:
                    selected = min(
                        queue_items,
                        key=lambda item: (
                            int(item[2].metadata.get("echo_transfer_rank", 10**9)),
                            item[2].arrival_slot,
                            item[2].task_id,
                        ),
                    )
                else:
                    selected = min(
                        queue_items,
                        key=lambda item: (
                            int(item[2].metadata.get("queue_entered_at", 0)),
                            item[2].arrival_slot,
                            item[2].task_id,
                        ),
                    )
                task = selected[2]
                self._active_transmission_task_ids[source_id] = task.task_id
                task.transmission_start_slot = self.current_slot
                task.metadata["transmission_start_slot"] = self.current_slot
                task.metadata["transmission_started_at"] = self.current_slot
                ledger = self._trace_ledgers.setdefault(
                    task.task_id, OffloadTraceLedger()
                )
                if "transmission_started" not in ledger.snapshot():
                    ledger.emit("transmission_started")
                self._record_trace_event(
                    "transmission_started",
                    task,
                    queue_type="offloading",
                    host_node_id=source_id,
                    destination=task.resolved_destination,
                    transmission_started_at=self.current_slot,
                    transmission_delay_slots=int(
                        task.metadata.get("transmission_delay_slots", 1)
                    ),
                    trace_source_component="evaluation_environment",
                )

            key, queue, task = selected
            started = int(task.metadata.get("transmission_started_at", self.current_slot))
            delay = max(1, int(task.metadata.get("transmission_delay_slots", 1)))
            if self.current_slot < started + delay - 1:
                continue

            queue.tasks.remove(task)
            queue.current_head_entered_at = (
                int(queue.tasks[0].metadata.get("queue_entered_at", self.current_slot))
                if queue.tasks
                else None
            )
            destination = str(task.resolved_destination)
            task.transmission_completion_slot = self.current_slot
            task.metadata["transmission_completion_slot"] = self.current_slot
            task.metadata["transmission_completed_at"] = self.current_slot
            public_queue = self._public_queue_for(source_id, destination)
            public_queue.enqueue(task, slot=self.current_slot)
            task.destination_admission_slot = self.current_slot + 1
            task.metadata["destination_admission_slot"] = self.current_slot + 1
            task.metadata["public_queue_admitted_at"] = self.current_slot + 1
            task.metadata["queue_type"] = "public"
            task.metadata["host_node_id"] = destination
            self._record_trace_event(
                "transmission_completed",
                task,
                queue_type="public",
                host_node_id=destination,
                destination=destination,
                transmission_started_at=started,
                transmission_completed_at=self.current_slot,
                destination_admission_slot=self.current_slot + 1,
                transmission_delay_slots=delay,
                trace_source_component="evaluation_environment",
            )
            self._trace_ledgers.setdefault(
                task.task_id, OffloadTraceLedger()
            ).emit("transmission_completed")
            self._active_transmission_task_ids.pop(source_id, None)

    def _finalize_unresolved_at_horizon(self, horizon_slot: int) -> list[Task]:
        finalized: list[Task] = []
        for task_id in sorted(self._active_tasks):
            task = self._active_tasks[task_id]
            if task.terminal_outcome is not None:
                continue
            task.mark_resolution(
                slot=horizon_slot,
                outcome="dropped",
                reason="episode_horizon_unresolved",
            )
            finalized.append(task)
        return finalized

    @staticmethod
    def _canonical_action_index(selected_action: str) -> int:
        if selected_action in {"local", "compute_local"}:
            return 0
        if selected_action.startswith("horizontal_"):
            suffix = selected_action.rsplit("_", 1)[-1]
            if suffix.isdigit():
                return int(suffix)
            return 1
        if selected_action in {"horizontal", "offload_horizontal"}:
            return 1
        if selected_action in {"cloud", "vertical", "offload_vertical"}:
            return 31
        return -1
