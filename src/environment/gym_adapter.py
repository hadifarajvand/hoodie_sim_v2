from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Literal
from typing import Any

from src.echo_action_space import build_echo_action_space, build_physical_action_mask
from src.echo_ert import EchoCandidateEstimate, estimate_local_queue, estimate_offload_candidate
from src.echo_types import EchoTaskSpec
from src.evaluation.trace_protocol import EvaluationTrace, TraceTaskBlueprint, build_deterministic_trace
from src.policies.action_masking import select_legal_action
from src.policies.policy_interface import PolicyContext

from .environment import apply_policy_action, finalize_task_runtime_state_with_parameters
from .compute_config import ComputeConfig
from .execution_helper import step_execution
from .offload_trace_ledger import OffloadTraceLedger
from .offloading_queue import OffloadingQueue
from .offload_trace_schema import OFFLOAD_LIFECYCLE_EVENTS
from .link_rate_config import LinkRateConfig, compute_transmission_delay, mbits_to_bits
from .private_queue import PrivateQueue
from .public_queue import PublicQueue
from .reward_timing import emit_delayed_reward, reward_for_terminal_task
from .runtime_model import SharedRuntimeParameters, advance_shared_runtime
from .lifecycle_trace import LifecycleTraceConfig, LifecycleTraceRecorder
from .slot_engine import SlotEngine
from .task import Task
from .topology import TopologyGraph
from .trace_source import TraceSource


@dataclass(slots=True)
class StepTraceRecord:
    task_id: int
    arrival_slot: int
    selected_action: str | None
    resolved_destination: str | None
    terminal_outcome: str | None
    completion_slot: int | None
    reward: float


@dataclass(frozen=True, slots=True)
class TaskResolutionEvent:
    task_id: int
    source_id: int
    decision_slot: int
    resolution_slot: int
    outcome: Literal["success", "drop"]
    resolution_reason: str
    selected_action: int
    selected_destination: str | None
    completion_slot: int | None
    duration_slots: int
    risk_penalty: float
    drop_indicator: int
    task_reward: float


@dataclass(slots=True)
class PendingReward:
    task_id: int
    decision_slot: int
    resolution_slot: int
    reward: float
    delivered: bool = False


@dataclass(slots=True)
class HoodieGymEnvironment:
    """Owns all episode and slot lifecycle orchestration for the Gym-style boundary."""

    episode_length: int
    topology: TopologyGraph | None = None
    runtime_parameters: SharedRuntimeParameters = field(default_factory=SharedRuntimeParameters)
    compute_config: ComputeConfig = field(default_factory=ComputeConfig)
    trace_source: TraceSource | None = None
    trace_config: LifecycleTraceConfig = field(default_factory=LifecycleTraceConfig)
    trace_recorder: LifecycleTraceRecorder = field(default_factory=LifecycleTraceRecorder)
    link_rate_config: LinkRateConfig = field(default_factory=LinkRateConfig)
    policy_name: str = "HOODIE"
    engine: SlotEngine = field(default_factory=SlotEngine)
    current_slot: int = 0
    seed: int | None = None
    trace: EvaluationTrace | None = None
    _current_task: Task | None = None
    _pending_arrivals: dict[int, list[TraceTaskBlueprint]] = field(default_factory=lambda: defaultdict(list))
    _private_queues: dict[str, PrivateQueue] = field(default_factory=dict)
    _offloading_queues: dict[tuple[str, str], OffloadingQueue] = field(default_factory=dict)
    _public_queues: dict[tuple[str, str], PublicQueue] = field(default_factory=dict)
    _active_tasks: dict[int, Task] = field(default_factory=dict)
    _history: list[StepTraceRecord] = field(default_factory=list)
    _trace_ledgers: dict[int, OffloadTraceLedger] = field(default_factory=dict)
    _pending_reward_tasks: list[Task] = field(default_factory=list)
    _pending_reward_ledger: dict[int, PendingReward] = field(default_factory=dict)
    _last_finalized_tasks: list[Task] = field(default_factory=list)
    _metrics: dict[str, float] = field(default_factory=lambda: {"completed": 0.0, "dropped": 0.0, "reward": 0.0})
    _drain_mode: bool = False

    def reset(self, seed: int | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
        self.seed = seed
        self.current_slot = 0
        self._current_task = None
        self._pending_arrivals.clear()
        self._private_queues.clear()
        self._offloading_queues.clear()
        self._public_queues.clear()
        self._active_tasks.clear()
        self._history.clear()
        self._trace_ledgers.clear()
        self._pending_reward_tasks.clear()
        self._pending_reward_ledger.clear()
        self._last_finalized_tasks.clear()
        self._metrics = {"completed": 0.0, "dropped": 0.0, "reward": 0.0}
        self._drain_mode = False
        self.engine.current_slot = 0
        self.link_rate_config.__post_init__()
        self.trace_recorder = LifecycleTraceRecorder(enabled=self.trace_config.trace_enabled)

        trace_id = self.trace_source.identifier if self.trace_source is not None else f"{self.policy_name.lower()}-{seed if seed is not None else 0}"
        if seed is None and self.trace_source is not None and self.trace_source.mode == "trace_bank":
            loaded = self.trace_source.load()
            if isinstance(loaded, dict) and "tasks" in loaded:
                self.trace = self._trace_from_loaded_payload(trace_id, loaded)
            else:
                self.trace = build_deterministic_trace(trace_id, 0, self.episode_length)
        else:
            self.trace = build_deterministic_trace(trace_id, seed or 0, self.episode_length)
        for blueprint in sorted(self.trace.tasks, key=self._trace_sort_key):
            self._pending_arrivals[blueprint.arrival_slot].append(blueprint)
        for blueprints in self._pending_arrivals.values():
            blueprints.sort(key=self._trace_sort_key)
        self._current_task = self._load_current_task()
        observation = self.observe()
        info = self._build_info()
        return observation, info

    @property
    def current_task(self) -> Task | None:
        return self._current_task

    def observe(self) -> dict[str, Any]:
        current_task = self._current_task
        if current_task is None:
            return {}
        agent_id = str(current_task.source_agent_id)
        return {
            agent_id: self._agent_observation(current_task),
        }

    def observe_flat(self, task: Task | None = None) -> dict[str, Any]:
        current_task = task or self._current_task
        observation: dict[str, Any] = {
            "slot": self.current_slot,
            "queue_load": float(self.queue_load),
            "load_hint": float(self.queue_load),
            "history_length": len(self._history),
        }
        if current_task is None:
            observation["fallback_hints"] = {}
            observation["legal_action_mask"] = {}
            observation["echo_state_vector"] = ()
            observation["echo_state_schema"] = ()
            observation["echo_action_ids"] = ()
            observation["echo_candidate_ert"] = {}
            return observation
        observation.update(self._agent_observation(current_task))
        return observation

    def _agent_observation(self, task: Task) -> dict[str, Any]:
        legal_action_mask = self.legal_action_mask(task)
        echo_view = self._echo_observation(task, legal_action_mask)
        return {
            "slot": self.current_slot,
            "queue_load": float(self.queue_load),
            "load_hint": float(self.queue_load),
            "history_length": len(self._history),
            "task_id": task.task_id,
            "source_agent_id": task.source_agent_id,
            "arrival_slot": task.arrival_slot,
            "size": task.size,
            "processing_density": task.processing_density,
            "cycles_required": task.cycles_required,
            "cycles_remaining": task.cycles_remaining,
            "timeout_length": task.timeout_length,
            "absolute_deadline_slot": task.absolute_deadline_slot,
            "topology": self.topology.legal_adjacency.get(str(task.source_agent_id), ()) if self.topology is not None else (),
            "legal_action_mask": legal_action_mask,
            "fallback_hints": self._fallback_hints(task, legal_action_mask),
            "latency_estimates": self._latency_estimates(task, legal_action_mask),
            "balance_hint": self._balance_hints(task, legal_action_mask),
            "echo_state_vector": echo_view["state_vector"],
            "echo_state_schema": echo_view["state_schema"],
            "echo_action_ids": echo_view["action_ids"],
            "echo_candidate_ert": echo_view["candidate_ert"],
            "echo_deadline_mask": echo_view["deadline_mask"],
        }

    def legal_action_mask(self, task: Task | None = None) -> dict[str, bool]:
        if task is None and self._current_task is None:
            return {}
        current_task = task or self._current_task
        source_id = str(current_task.source_agent_id)
        legal = {
            "local": True,
            "compute_local": True,
            "horizontal": False,
            "offload_horizontal": False,
            "vertical": False,
            "offload_vertical": False,
        }
        if self.topology is None:
            legal["horizontal"] = True
            legal["offload_horizontal"] = True
            legal["vertical"] = True
            legal["offload_vertical"] = True
            return legal
        allowed = self.topology.legal_horizontal_destinations(source_id)
        legal["horizontal"] = bool(allowed)
        legal["offload_horizontal"] = legal["horizontal"]
        legal["vertical"] = True
        legal["offload_vertical"] = True
        if self.policy_name.startswith("ECHO"):
            return self._echo_deadline_valid_mask(current_task, legal)
        return legal

    def step(self, action: str | None) -> tuple[dict[str, Any], float, bool, bool, dict[str, Any]]:
        if self.trace is None:
            raise RuntimeError("Environment must be reset before stepping")
        reward = 0.0
        task_resolution_events: list[dict[str, Any]] = []
        reward_delivery_events: list[dict[str, Any]] = []
        current_task = self._current_task
        selected_action_emitted = False
        reward_delivery_events.extend(self._deliver_pending_rewards(self.current_slot))
        if reward_delivery_events:
            reward += sum(float(event["reward"]) for event in reward_delivery_events)
        if current_task is not None:
            if action is None:
                raise ValueError("An action is required while a task is pending")
            legal_action_mask = self.legal_action_mask(current_task)
            current_task.metadata["legal_action_mask"] = dict(legal_action_mask)
            context = PolicyContext(
                observation=self.observe_flat(current_task),
                legal_action_mask=legal_action_mask,
                trace_history=(self.trace.trace_id,),
            )
            selected_action = select_legal_action(context, action)
            current_task.metadata["selected_action_family"] = self._selected_action_family(selected_action)
            if selected_action.startswith("horizontal_"):
                current_task.metadata["action_index"] = 1
            elif selected_action == "cloud":
                current_task.metadata["action_index"] = 2
            else:
                current_task.metadata["action_index"] = {"local": 0, "compute_local": 0, "horizontal": 1, "offload_horizontal": 1, "vertical": 2, "offload_vertical": 2}.get(selected_action)
            current_task.metadata["decision_event_id"] = f"{self.trace.trace_id}:{self.current_slot}:{current_task.task_id}"
            current_task.metadata["selected_action_trace_source"] = "decision_point"
            current_task.metadata["selected_action_to_task_join_key"] = f"{self.trace.trace_id}:{current_task.task_id}"
            current_task.metadata["terminal_outcome_join_key"] = f"{self.trace.trace_id}:{current_task.task_id}:terminal_outcome"
            current_task.metadata["strategy"] = self.policy_name
            current_task.metadata["seed"] = self.seed
            current_task.metadata["agent_id"] = current_task.source_agent_id
            resolved_destination = self._resolve_destination(current_task, selected_action)
            apply_policy_action(current_task, context, selected_action, resolved_destination=resolved_destination)
            ledger = OffloadTraceLedger()
            ledger.emit("selected_action")
            self._trace_ledgers[current_task.task_id] = ledger
            self._admit_current_task(current_task)
            self._current_task = None
            selected_action_emitted = True

        finalized_tasks = self._progress_offloading_queues()
        finalized_tasks.extend(self._progress_execution_queues())
        if finalized_tasks:
            self._last_finalized_tasks = list(finalized_tasks)
        for task in finalized_tasks:
            event = self._build_task_resolution_event(task, resolution_slot=self.current_slot)
            task_resolution_events.append(event)
            self._register_pending_reward(task)

        if (
            not selected_action_emitted
            and not finalized_tasks
            and current_task is None
            and self.queue_load == 0
        ):
            reward = float("nan")

        self.engine.current_slot = self.current_slot
        self.current_slot += 1
        self._current_task = self._load_current_task()
        truncated = self.current_slot >= self.episode_length
        terminated = self._is_terminated() and not truncated
        if terminated or truncated:
            reward_delivery_events.extend(self._flush_pending_rewards(self.current_slot))
            if reward_delivery_events:
                reward = sum(float(event["reward"]) for event in reward_delivery_events)
        if truncated and not terminated:
            self._record_pending_at_horizon_events()
        observation = self.observe()
        info = self._build_info(
            finalized_tasks=finalized_tasks or (self._last_finalized_tasks if (terminated or truncated) else []),
            reward=reward,
            terminated=terminated,
            truncated=truncated,
            task_resolution_events=task_resolution_events,
            reward_delivery_events=reward_delivery_events,
        )
        return observation, reward, terminated, truncated, info

    @property
    def queue_load(self) -> int:
        return sum(len(queue.tasks) for queue in self._private_queues.values()) + sum(
            len(queue.tasks) for queue in self._offloading_queues.values()
        ) + sum(len(queue.tasks) for queue in self._public_queues.values())

    def _load_current_task(self) -> Task | None:
        eligible_slots = sorted(slot for slot, blueprints in self._pending_arrivals.items() if blueprints and slot <= self.current_slot)
        if not eligible_slots:
            if self._current_task is None and self.queue_load > 0:
                self._drain_mode = True
            return None
        arrival_slot = eligible_slots[0]
        blueprints = self._pending_arrivals[arrival_slot]
        blueprint = blueprints.pop(0)
        if not blueprints:
            self._pending_arrivals.pop(arrival_slot, None)
        task = blueprint.build()
        self._active_tasks[task.task_id] = task
        self._record_trace_event(
            "task_generated",
            task,
            queue_type="pending_arrival",
            trace_source_component="traffic_generator",
        )
        return task

    def _admit_current_task(self, task: Task) -> None:
        source_id = str(task.source_agent_id)
        if task.selected_action in {"local", "compute_local"}:
            queue = self._private_queues.setdefault(source_id, PrivateQueue(owner_node_id=source_id))
            queue.enqueue(task, slot=self.current_slot)
            task.start_slot = self.current_slot
            task.metadata["queue_type"] = "private"
            task.metadata["host_node_id"] = source_id
            task.metadata["destination"] = "self"
            self._record_trace_event(
                "task_admitted",
                task,
                queue_type="private",
                host_node_id=source_id,
                destination="self",
                trace_source_component="environment",
            )
            self._trace_ledgers.setdefault(task.task_id, OffloadTraceLedger()).emit("execution_started")
            return
        destination = self._resolve_destination(task, task.selected_action or "")
        queue = self._offloading_queues.setdefault(
            (source_id, destination),
            OffloadingQueue(owner_node_id=source_id, resolved_destination=destination),
        )
        transmission_rate_source = "horizontal_R_H" if task.selected_action in {"horizontal", "offload_horizontal"} else "vertical_R_V"
        data_rate_bps = (
            self.link_rate_config.horizontal_data_rate_bps
            if transmission_rate_source == "horizontal_R_H"
            else self.link_rate_config.vertical_data_rate_bps
        )
        payload_bits = mbits_to_bits(task.size)
        transmission_delay = compute_transmission_delay(
            payload_bits,
            data_rate_bps,
            slot_duration_seconds=self.link_rate_config.slot_duration_seconds,
            rounding_policy=self.link_rate_config.rounding_policy,
        )
        task.metadata["transmission_started_at"] = self.current_slot
        task.metadata["transmission_delay_slots"] = transmission_delay.delay_slots
        task.metadata["transmission_delay_seconds"] = transmission_delay.delay_seconds
        task.metadata["transmission_payload_bits"] = payload_bits
        task.metadata["transmission_data_rate_bps"] = data_rate_bps
        task.metadata["transmission_rate_source"] = transmission_rate_source
        task.metadata["transmission_rounding_policy"] = transmission_delay.slot_rounding_policy
        task.metadata["queue_type"] = "offloading"
        task.metadata["host_node_id"] = source_id
        task.metadata["destination"] = destination
        queue.enqueue(task, slot=self.current_slot)
        task.start_slot = self.current_slot
        ledger = self._trace_ledgers.setdefault(task.task_id, OffloadTraceLedger())
        self._record_trace_event(
            "task_admitted",
            task,
            queue_type="offloading",
            host_node_id=source_id,
            destination=destination,
            trace_source_component="environment",
        )
        self._record_trace_event(
            "transmission_started",
            task,
            queue_type="offloading",
            host_node_id=source_id,
            destination=destination,
            transmission_started_at=self.current_slot,
            transmission_delay_slots=transmission_delay.delay_slots,
            trace_source_component="environment",
        )
        if task.selected_action in {"horizontal", "offload_horizontal"}:
            ledger.emit("queued_public")
            ledger.emit("transmission_started")
        elif task.selected_action in {"vertical", "offload_vertical"}:
            ledger.emit("offloaded_cloud")
            ledger.emit("transmission_started")

    def _progress_offloading_queues(self) -> list[Task]:
        finalized: list[Task] = []
        for (source_id, destination), queue in list(self._offloading_queues.items()):
            admitted = self.engine.admit_offload_completion(queue, self._public_queue_for(source_id, destination), self.current_slot)
            if admitted is not None:
                task = admitted
                task.metadata["transmission_completed_at"] = self.current_slot
                task.metadata["public_queue_admitted_at"] = self.current_slot
                task.metadata["queue_type"] = "public"
                task.metadata["host_node_id"] = destination
                self._record_trace_event(
                    "transmission_completed",
                    task,
                    queue_type="public",
                    host_node_id=destination,
                    destination=destination,
                    transmission_started_at=int(task.metadata.get("transmission_started_at", self.current_slot)),
                    transmission_completed_at=self.current_slot,
                    transmission_delay_slots=int(task.metadata.get("transmission_delay_slots", 0)),
                    trace_source_component="environment",
                )
                self._trace_ledgers.setdefault(task.task_id, OffloadTraceLedger()).emit("transmission_completed")
        return finalized

    def _progress_execution_queues(self) -> list[Task]:
        finalized: list[Task] = []
        for queue in list(self._private_queues.values()):
            finalized.extend(self._maybe_finalize_head(queue, "local"))
        finalized.extend(self._progress_shared_execution_queues())
        return finalized

    def _maybe_finalize_head(self, queue: PrivateQueue | PublicQueue, destination_kind: str) -> list[Task]:
        if not queue.tasks:
            return []
        task = queue.tasks[0]
        ledger = self._trace_ledgers.setdefault(task.task_id, OffloadTraceLedger())
        if "execution_started" not in ledger.snapshot():
            ledger.emit("execution_started")
        advance_shared_runtime(task, destination_kind, self.current_slot, self.runtime_parameters, self.compute_config)
        execution_progress = step_execution(
            task,
            self.compute_config.capacity_for(destination_kind),
            slot=self.current_slot,
            destination_kind=destination_kind,
        )
        self._record_execution_progress(
            task,
            execution_progress,
            destination_kind,
            compute_capacity_gcycles_per_slot=self.compute_config.capacity_for(destination_kind),
        )
        if not execution_progress.completed:
            return []
        finalized = queue.dequeue()
        outcome = "completed" if int(finalized.completion_slot if finalized.completion_slot is not None else self.current_slot) <= int(finalized.absolute_deadline_slot) else "dropped"
        reason = f"{destination_kind}_execution_completed" if outcome == "completed" else f"{destination_kind}_deadline_missed"
        finalized.mark_resolution(slot=self.current_slot, outcome=outcome, reason=reason)
        ledger.emit("execution_completed")
        self._record_trace_event(
            "execution_completed",
            task,
            queue_type="private" if destination_kind == "local" else destination_kind,
            host_node_id=str(task.source_agent_id) if destination_kind == "local" else task.resolved_destination,
            destination=task.resolved_destination,
            cycles_before_gcycles=execution_progress.cycles_before,
            cycles_consumed_gcycles=execution_progress.cycles_consumed,
            cycles_after_gcycles=execution_progress.cycles_after,
            compute_capacity_gcycles_per_slot=self.compute_config.capacity_for(destination_kind),
            trace_source_component="environment",
        )
        return [finalized]

    def _progress_shared_execution_queues(self) -> list[Task]:
        finalized: list[Task] = []
        grouped_public_queues: dict[str, list[PublicQueue]] = defaultdict(list)
        for queue in self._public_queues.values():
            if queue.tasks:
                grouped_public_queues[queue.host_node_id].append(queue)

        for host_node_id in sorted(grouped_public_queues):
            queues = sorted(grouped_public_queues[host_node_id], key=self._shared_queue_sort_key)
            active_heads = [queue.tasks[0] for queue in queues if queue.tasks]
            if not active_heads:
                continue
            if any(queue.current_head_entered_at == self.current_slot for queue in queues if queue.current_head_entered_at is not None):
                continue
            capacity_pool = (
                self.compute_config.cpu_capacity_per_slot_cloud
                if host_node_id == "cloud"
                else self.compute_config.cpu_capacity_per_slot_edge
            )
            per_head_capacity = capacity_pool / float(len(active_heads))
            for queue in queues:
                if not queue.tasks:
                    continue
                task = queue.tasks[0]
                task.metadata["capacity_sharing_host"] = host_node_id
                task.metadata["capacity_sharing_active_heads"] = len(active_heads)
                task.metadata["capacity_sharing_capacity_pool"] = capacity_pool
                task.metadata["capacity_sharing_allocated_capacity"] = per_head_capacity
                task.metadata["capacity_sharing_policy"] = "deterministic_equal_share_at_slot_start"
                task.metadata["capacity_sharing_redistribution_policy"] = "no_same_slot_redistribution"
                destination_kind = "cloud" if host_node_id == "cloud" else "public"
                ledger = self._trace_ledgers.setdefault(task.task_id, OffloadTraceLedger())
                if "execution_started" not in ledger.snapshot():
                    ledger.emit("execution_started")
                advance_shared_runtime(task, destination_kind, self.current_slot, self.runtime_parameters, self.compute_config)
                execution_progress = step_execution(
                    task,
                    per_head_capacity,
                    slot=self.current_slot,
                    destination_kind=destination_kind,
                )
                self._record_execution_progress(
                    task,
                    execution_progress,
                    destination_kind,
                    compute_capacity_gcycles_per_slot=per_head_capacity,
                    host_node_id=host_node_id,
                )
                if not execution_progress.completed:
                    continue
                finalized_task = queue.dequeue()
                outcome = "completed" if int(finalized_task.completion_slot if finalized_task.completion_slot is not None else self.current_slot) <= int(finalized_task.absolute_deadline_slot) else "dropped"
                reason = f"{destination_kind}_execution_completed" if outcome == "completed" else f"{destination_kind}_deadline_missed"
                finalized_task.mark_resolution(slot=self.current_slot, outcome=outcome, reason=reason)
                ledger.emit("execution_completed")
                self._record_trace_event(
                    "execution_completed",
                    task,
                    queue_type="public" if destination_kind == "public" else "cloud",
                    host_node_id=host_node_id,
                    destination=task.resolved_destination,
                    cycles_before_gcycles=execution_progress.cycles_before,
                    cycles_consumed_gcycles=execution_progress.cycles_consumed,
                    cycles_after_gcycles=execution_progress.cycles_after,
                    compute_capacity_gcycles_per_slot=per_head_capacity,
                    trace_source_component="environment",
                )
                finalized.append(finalized_task)
        return finalized

    def _shared_queue_sort_key(self, queue: PublicQueue) -> tuple[int, int, str, str]:
        head = queue.tasks[0] if queue.tasks else None
        task_id = head.task_id if head is not None else -1
        return (
            int(queue.host_node_id != "cloud"),
            int(queue.source_agent_id),
            str(task_id),
            queue.host_node_id,
        )

    def _public_queue_for(self, source_id: str, destination: str) -> PublicQueue:
        key = (destination, source_id)
        queue = self._public_queues.get(key)
        if queue is None:
            queue = PublicQueue(host_node_id=destination, source_agent_id=source_id)
            self._public_queues[key] = queue
        return queue

    def _resolve_destination(self, task: Task, action: str) -> str:
        if action in {"local", "compute_local"}:
            return "self"
        if action == "cloud":
            return "cloud"
        if action.startswith("horizontal_"):
            return action.removeprefix("horizontal_")
        if action in {"horizontal", "offload_horizontal"}:
            if self.topology is not None:
                allowed_horizontal = self.topology.legal_horizontal_destinations(str(task.source_agent_id))
                if allowed_horizontal:
                    return allowed_horizontal[0]
                raise ValueError("No topology-backed horizontal destination available")
            return "horizontal"
        if action in {"vertical", "offload_vertical"}:
            return "cloud"
        raise ValueError(f"Unsupported action: {action}")

    def _fallback_hints(self, task: Task, legal_action_mask: dict[str, bool]) -> dict[str, float]:
        hints: dict[str, float] = {}
        if legal_action_mask.get("local", False):
            hints["local"] = 1.0
        if legal_action_mask.get("horizontal", False):
            hints["horizontal"] = 2.0
        if legal_action_mask.get("vertical", False):
            hints["vertical"] = 3.0
        hints["task_size"] = task.size
        return hints

    def _latency_estimates(self, task: Task, legal_action_mask: dict[str, bool]) -> dict[str, float]:
        if self.policy_name.startswith("ECHO"):
            echo_view = self._echo_observation(task, legal_action_mask)
            return {
                action_id: float(ert)
                for action_id, ert in echo_view["candidate_ert"].items()
            }
        estimates: dict[str, float] = {}
        if legal_action_mask.get("local", False):
            estimates["local"] = task.processing_density
        if legal_action_mask.get("horizontal", False):
            estimates["horizontal"] = float(max(1, task.processing_density - 1))
        if legal_action_mask.get("vertical", False):
            estimates["vertical"] = float(max(1, task.processing_density - 2))
        return estimates

    def _balance_hints(self, task: Task, legal_action_mask: dict[str, bool]) -> dict[str, float]:
        if self.policy_name.startswith("ECHO"):
            echo_view = self._echo_observation(task, legal_action_mask)
            return {
                action_id: float(max(0, -ert))
                for action_id, ert in echo_view["candidate_ert"].items()
            }
        hints: dict[str, float] = {}
        if legal_action_mask.get("local", False):
            hints["local"] = float(max(1, task.size // 4))
        if legal_action_mask.get("horizontal", False):
            hints["horizontal"] = float(max(1, task.size // 3))
        if legal_action_mask.get("vertical", False):
            hints["vertical"] = float(max(1, task.size // 2))
        return hints

    def _register_pending_reward(self, task: Task) -> None:
        if task.task_id in self._pending_reward_ledger:
            raise RuntimeError(f"duplicate pending reward for task {task.task_id}")
        reward = reward_for_terminal_task(task)
        self._pending_reward_ledger[task.task_id] = PendingReward(
            task_id=task.task_id,
            decision_slot=int(task.decision_slot if task.decision_slot is not None else task.arrival_slot),
            resolution_slot=int(task.resolution_slot if task.resolution_slot is not None else self.current_slot),
            reward=reward,
        )
        self._pending_reward_tasks.append(task)

    def _deliver_pending_rewards(self, delivery_slot: int) -> list[dict[str, Any]]:
        reward_delivery_events: list[dict[str, Any]] = []
        pending_tasks = list(self._pending_reward_tasks)
        self._pending_reward_tasks.clear()
        for task in pending_tasks:
            pending = self._pending_reward_ledger.get(task.task_id)
            if pending is None:
                raise RuntimeError(f"missing pending reward for task {task.task_id}")
            if pending.delivered:
                raise RuntimeError(f"duplicate reward delivery for task {task.task_id}")
            finalize_task_runtime_state_with_parameters(task, delivery_slot, self.runtime_parameters)
            emit_delayed_reward(task)
            pending.delivered = True
            reward_delivery_events.append(
                self._build_reward_delivery_event(task, pending, delivery_slot=delivery_slot)
            )
            self._record_outcome(task, pending.reward)
            self._pending_reward_ledger.pop(task.task_id, None)
        return reward_delivery_events

    def _flush_pending_rewards(self, delivery_slot: int) -> list[dict[str, Any]]:
        return self._deliver_pending_rewards(delivery_slot)

    def _build_task_resolution_event(self, task: Task, *, resolution_slot: int) -> dict[str, Any]:
        decision_slot = int(task.decision_slot if task.decision_slot is not None else task.arrival_slot)
        completion_slot = task.completion_slot
        duration_slots = int((completion_slot if completion_slot is not None else resolution_slot) - decision_slot)
        reward = reward_for_terminal_task(task)
        outcome = "success" if task.terminal_outcome == "completed" else "drop"
        event = TaskResolutionEvent(
            task_id=task.task_id,
            source_id=task.source_agent_id,
            decision_slot=decision_slot,
            resolution_slot=resolution_slot,
            outcome=outcome,
            resolution_reason=task.resolution_reason or ("terminal_success" if outcome == "success" else "terminal_drop"),
            selected_action=task.metadata.get("action_index") if task.metadata.get("action_index") is not None else -1,
            selected_destination=task.resolved_destination,
            completion_slot=completion_slot,
            duration_slots=duration_slots,
            risk_penalty=float(task.predicted_risk or 0.0),
            drop_indicator=1 if task.terminal_outcome == "dropped" else 0,
            task_reward=reward,
        )
        task.metadata["task_resolution_event"] = {
            "task_id": event.task_id,
            "source_id": event.source_id,
            "decision_slot": event.decision_slot,
            "resolution_slot": event.resolution_slot,
            "outcome": event.outcome,
            "resolution_reason": event.resolution_reason,
            "selected_action": event.selected_action,
            "selected_destination": event.selected_destination,
            "completion_slot": event.completion_slot,
            "duration_slots": event.duration_slots,
            "risk_penalty": event.risk_penalty,
            "drop_indicator": event.drop_indicator,
            "task_reward": event.task_reward,
        }
        return dict(task.metadata["task_resolution_event"])

    def _build_reward_delivery_event(
        self,
        task: Task,
        pending: PendingReward,
        *,
        delivery_slot: int,
    ) -> dict[str, Any]:
        return {
            "task_id": task.task_id,
            "decision_slot": pending.decision_slot,
            "resolution_slot": pending.resolution_slot,
            "delivery_slot": delivery_slot,
            "reward": pending.reward,
            "delta_slots": max(1, delivery_slot - pending.decision_slot),
        }

    def _record_outcome(self, task: Task, reward: float) -> None:
        ledger = self._trace_ledgers.setdefault(task.task_id, OffloadTraceLedger())
        if task.terminal_outcome == "completed":
            self._record_trace_event(
                "task_completed",
                task,
                queue_type=task.metadata.get("queue_type"),
                host_node_id=task.metadata.get("host_node_id"),
                destination=task.resolved_destination,
                terminal_outcome=task.terminal_outcome,
                reward=reward,
                reward_available=True,
                trace_source_component="environment",
            )
        elif task.terminal_outcome == "dropped":
            self._record_trace_event(
                "deadline_reached",
                task,
                queue_type=task.metadata.get("queue_type"),
                host_node_id=task.metadata.get("host_node_id"),
                destination=task.resolved_destination,
                terminal_outcome=task.terminal_outcome,
                trace_source_component="environment",
            )
            self._record_trace_event(
                "deadline_expired",
                task,
                queue_type=task.metadata.get("queue_type"),
                host_node_id=task.metadata.get("host_node_id"),
                destination=task.resolved_destination,
                terminal_outcome=task.terminal_outcome,
                trace_source_component="environment",
            )
            self._record_trace_event(
                "task_dropped",
                task,
                queue_type=task.metadata.get("queue_type"),
                host_node_id=task.metadata.get("host_node_id"),
                destination=task.resolved_destination,
                terminal_outcome=task.terminal_outcome,
                reward=reward,
                reward_available=True,
                trace_source_component="environment",
            )
        if task.terminal_outcome == "dropped":
            ledger.emit("dropped_timeout")
        ledger.emit("reward_emitted")
        self._record_trace_event(
            "reward_emitted",
            task,
            queue_type=task.metadata.get("queue_type"),
            host_node_id=task.metadata.get("host_node_id"),
            destination=task.resolved_destination,
            terminal_outcome=task.terminal_outcome,
            reward=reward,
            reward_available=True,
            trace_source_component="environment",
        )
        task.metadata["offload_lifecycle_events"] = ledger.snapshot()
        self._history.append(
            StepTraceRecord(
                task_id=task.task_id,
                arrival_slot=task.arrival_slot,
                selected_action=task.selected_action,
                resolved_destination=task.resolved_destination,
                terminal_outcome=task.terminal_outcome,
                completion_slot=task.completion_slot,
                reward=reward,
            )
        )
        self._metrics["reward"] += reward
        if task.terminal_outcome == "completed":
            self._metrics["completed"] += 1.0
        elif task.terminal_outcome == "dropped":
            self._metrics["dropped"] += 1.0

    def _is_terminated(self) -> bool:
        has_future_arrivals = any(self._pending_arrivals.values())
        has_queued_work = self.queue_load > 0
        return not has_future_arrivals and not has_queued_work and self._current_task is None and not self._pending_reward_tasks

    def _build_info(
        self,
        finalized_tasks: list[Task] | None = None,
        reward: float = 0.0,
        terminated: bool = False,
        truncated: bool = False,
        task_resolution_events: list[dict[str, Any]] | None = None,
        reward_delivery_events: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        return {
            "trace_id": self.trace.trace_id if self.trace is not None else "",
            "slot": self.current_slot,
            "reward": reward,
            "terminated": terminated,
            "truncated": truncated,
            "metrics": dict(self._metrics),
            "queue_load": self.queue_load,
            "link_rate_config": self.link_rate_config.to_dict(),
            "trace_enabled": self.trace_recorder.enabled,
            "lifecycle_trace_events": self.trace_recorder.snapshot(),
            "task_arrival_events": [],
            "queue_admission_events": [],
            "transmission_events": [],
            "task_resolution_events": list(task_resolution_events or []),
            "reward_delivery_events": list(reward_delivery_events or []),
            "finalized_tasks": [
                {
                    "task_id": task.task_id,
                    "arrival_slot": task.arrival_slot,
                    "completion_slot": task.completion_slot,
                    "terminal_outcome": task.terminal_outcome,
                    "selected_action": task.selected_action,
                    "resolved_destination": task.resolved_destination,
                    "offload_lifecycle_events": list(task.metadata.get("offload_lifecycle_events", ())),
                }
                for task in (finalized_tasks or [])
            ],
            "history_length": len(self._history),
            "diagnostics": {
                "resolution_event_count": len(task_resolution_events or []),
                "reward_delivery_event_count": len(reward_delivery_events or []),
            },
            "offload_lifecycle_events": list(
                finalized_tasks[0].metadata.get("offload_lifecycle_events", ())
            )
            if finalized_tasks
            else [],
        }

    def _record_execution_progress(
        self,
        task: Task,
        execution_progress: Any,
        destination_kind: str,
        *,
        compute_capacity_gcycles_per_slot: float,
        host_node_id: str | None = None,
    ) -> None:
        if execution_progress.cycles_consumed <= 0:
            return
        self._record_trace_event(
            "execution_started",
            task,
            queue_type="private" if destination_kind == "local" else destination_kind,
            host_node_id=host_node_id or (str(task.source_agent_id) if destination_kind == "local" else task.resolved_destination),
            destination=task.resolved_destination,
            cycles_before_gcycles=execution_progress.cycles_before,
            cycles_consumed_gcycles=execution_progress.cycles_consumed,
            cycles_after_gcycles=execution_progress.cycles_after,
            compute_capacity_gcycles_per_slot=compute_capacity_gcycles_per_slot,
            trace_source_component="environment",
        )
        self._record_trace_event(
            "execution_progress",
            task,
            queue_type="private" if destination_kind == "local" else destination_kind,
            host_node_id=host_node_id or (str(task.source_agent_id) if destination_kind == "local" else task.resolved_destination),
            destination=task.resolved_destination,
            cycles_before_gcycles=execution_progress.cycles_before,
            cycles_consumed_gcycles=execution_progress.cycles_consumed,
            cycles_after_gcycles=execution_progress.cycles_after,
            compute_capacity_gcycles_per_slot=compute_capacity_gcycles_per_slot,
            trace_source_component="environment",
        )

    def _record_trace_event(self, event_type: str, task: Task | None, *, trace_source_component: str, **fields: Any) -> None:
        if not self.trace_recorder.enabled:
            return
        selected_action = task.selected_action if task is not None else fields.pop("selected_action", None)
        selected_action_family = None
        if task is not None:
            selected_action_family = task.metadata.get("selected_action_family")
        if selected_action_family is None and isinstance(selected_action, str):
            selected_action_family = self._selected_action_family(selected_action)
        payload: dict[str, Any] = {
            "task_id": task.task_id if task is not None else fields.pop("task_id", None),
            "source_agent_id": task.source_agent_id if task is not None else fields.pop("source_agent_id", None),
            "selected_action": selected_action,
            "selected_action_family": selected_action_family,
            "selected_action_trace_source": task.metadata.get("selected_action_trace_source") if task is not None else fields.pop("selected_action_trace_source", None),
            "action_index": task.metadata.get("action_index") if task is not None else fields.pop("action_index", None),
            "decision_event_id": task.metadata.get("decision_event_id") if task is not None else fields.pop("decision_event_id", None),
            "selected_action_to_task_join_key": task.metadata.get("selected_action_to_task_join_key") if task is not None else fields.pop("selected_action_to_task_join_key", None),
            "terminal_outcome_join_key": task.metadata.get("terminal_outcome_join_key") if task is not None else fields.pop("terminal_outcome_join_key", None),
            "strategy": task.metadata.get("strategy") if task is not None else fields.pop("strategy", None),
            "seed": self.seed if task is not None else fields.pop("seed", None),
            "agent_id": task.source_agent_id if task is not None else fields.pop("agent_id", None),
            "arrival_slot": task.arrival_slot if task is not None else fields.pop("arrival_slot", None),
            "absolute_deadline_slot": task.absolute_deadline_slot if task is not None else fields.pop("absolute_deadline_slot", None),
            "task_age_slots": max(0, self.current_slot - task.arrival_slot) if task is not None else fields.pop("task_age_slots", None),
            "size_mbits": task.size if task is not None else fields.pop("size_mbits", None),
            "processing_density_gcycles_per_mbit": task.processing_density if task is not None else fields.pop("processing_density_gcycles_per_mbit", None),
            "cycles_required_gcycles": task.cycles_required if task is not None else fields.pop("cycles_required_gcycles", None),
            "transmission_started_at": task.metadata.get("transmission_started_at") if task is not None else fields.pop("transmission_started_at", None),
            "transmission_completed_at": task.metadata.get("transmission_completed_at") if task is not None else fields.pop("transmission_completed_at", None),
            "transmission_delay_slots": task.metadata.get("transmission_delay_slots") if task is not None else fields.pop("transmission_delay_slots", None),
            "terminal_outcome": task.terminal_outcome if task is not None else fields.pop("terminal_outcome", None),
            "reward_available": task.reward_emitted if task is not None else fields.pop("reward_available", None),
            "legality_snapshot": dict(task.metadata.get("legal_action_mask", {})) if task is not None and isinstance(task.metadata.get("legal_action_mask", {}), dict) else fields.pop("legality_snapshot", None),
        }
        payload.update(fields)
        self.trace_recorder.emit(event_type, slot=self.current_slot, trace_source_component=trace_source_component, **payload)

    @staticmethod
    def _selected_action_family(selected_action: str) -> str | None:
        if selected_action in {"local", "compute_local"}:
            return "local"
        if selected_action.startswith("horizontal_") or selected_action in {"horizontal", "offload_horizontal"}:
            return "horizontal"
        if selected_action in {"cloud", "vertical", "offload_vertical"}:
            return "vertical"
        return "unknown"

    def _record_pending_at_horizon_events(self) -> None:
        if not self.trace_recorder.enabled:
            return
        candidates = [self._current_task] if self._current_task is not None else []
        for queue in self._private_queues.values():
            if queue.tasks:
                candidates.append(queue.tasks[0])
        for queue in self._offloading_queues.values():
            if queue.tasks:
                candidates.append(queue.tasks[0])
        for queue in self._public_queues.values():
            if queue.tasks:
                candidates.append(queue.tasks[0])
        for task in candidates:
            self._record_trace_event(
                "pending_at_horizon",
                task,
                pending_at_horizon=True,
                reward_available=task.reward_emitted,
                trace_source_component="environment",
            )

    def _echo_deadline_valid_mask(self, task: Task, physical_mask: dict[str, bool]) -> dict[str, bool]:
        echo_view = self._echo_observation(task, physical_mask)
        mask = {key: False for key in physical_mask}
        action_ids = set(echo_view["deadline_mask"])
        if "local" in action_ids:
            mask["local"] = True
            mask["compute_local"] = True
        horizontal_ids = [action_id for action_id in action_ids if action_id.startswith("horizontal_")]
        if horizontal_ids:
            mask["horizontal"] = True
            mask["offload_horizontal"] = True
            task.metadata["echo_horizontal_action_ids"] = tuple(horizontal_ids)
        if "cloud" in action_ids:
            mask["vertical"] = True
            mask["offload_vertical"] = True
        task.metadata["echo_deadline_mask"] = tuple(sorted(action_ids))
        task.metadata["echo_candidate_ert"] = dict(echo_view["candidate_ert"])
        return mask

    def _echo_task_spec(self, task: Task) -> EchoTaskSpec:
        return EchoTaskSpec(
            task_id=int(task.task_id),
            source_agent_id=int(task.source_agent_id),
            arrival_slot=int(task.arrival_slot),
            size_mbits=float(task.size),
            processing_density_gcycles_per_mbit=float(task.processing_density),
            timeout_slots=int(task.timeout_length),
            absolute_deadline_slot=int(task.absolute_deadline_slot),
        )

    def _echo_observation(self, task: Task, legal_action_mask: dict[str, bool]) -> dict[str, Any]:
        if self.topology is None:
            candidate_ert = {"local": float(task.absolute_deadline_slot - self.current_slot)}
            return {
                "state_schema": ("arrival_indicator", "task_size", "processing_density", "timeout_length", "queue_load", "local_ert", "outbound_ert", "mask_local"),
                "state_vector": (1.0, float(task.size), float(task.processing_density), float(task.timeout_length), float(self.queue_load), float(candidate_ert["local"]), 0.0, 1.0),
                "action_ids": ("local",),
                "candidate_ert": candidate_ert,
                "deadline_mask": ("local",),
            }
        action_space = build_echo_action_space(self.topology, source_agent_id=int(task.source_agent_id))
        physical = build_physical_action_mask(action_space, self.topology)
        spec = self._echo_task_spec(task)
        local_queue = self._private_queues.get(str(task.source_agent_id))
        local_wait = estimate_local_queue(
            spec,
            current_slot=self.current_slot,
            residual_service_slots=1 if local_queue and local_queue.tasks else 0,
            predecessor_service_slots=[1] * max(0, len(local_queue.tasks) - 1) if local_queue else [],
            local_cpu_ghz=float(self.compute_config.cpu_capacity_per_slot_agent),
            slot_duration_seconds=float(self.runtime_parameters.slot_duration),
        )
        candidate_ert: dict[str, float] = {"local": float(local_wait.ert_slots)}
        feasible_ids: list[str] = []
        best_fallback: tuple[str, float] | None = None
        for action in action_space.actions:
            if action.action_id == "local":
                if local_wait.ert_slots >= 0:
                    feasible_ids.append("local")
                best_fallback = self._echo_better_fallback(best_fallback, "local", local_wait.lateness_slots)
                continue
            if action.action_id not in physical.allowed_action_ids:
                continue
            if action.kind == "horizontal" and action.destination_node_id == str(task.source_agent_id):
                continue
            estimate = estimate_offload_candidate(
                spec,
                destination_node_id=action.destination_node_id,
                current_slot=self.current_slot,
                outbound_residual_slots=1 if self._offloading_queues.get((str(task.source_agent_id), action.destination_node_id)) and self._offloading_queues[(str(task.source_agent_id), action.destination_node_id)].tasks else 0,
                outbound_predecessor_slots=[1] * max(0, len(self._offloading_queues.get((str(task.source_agent_id), action.destination_node_id), OffloadingQueue(owner_node_id=str(task.source_agent_id))).tasks) - 1),
                transmission_rate_mbps=float(self.link_rate_config.horizontal_data_rate_bps if action.kind == "horizontal" else self.link_rate_config.vertical_data_rate_bps),
                destination_waiting_slots=max(0, len(self._public_queues.get((action.destination_node_id, str(task.source_agent_id)), PublicQueue(host_node_id=action.destination_node_id, source_agent_id=str(task.source_agent_id))).tasks)),
                destination_cpu_ghz=float(self.compute_config.cpu_capacity_per_slot_edge if action.kind == "horizontal" else self.compute_config.cpu_capacity_per_slot_cloud),
                slot_duration_seconds=float(self.runtime_parameters.slot_duration),
            )
            candidate_ert[action.action_id] = float(estimate.ert_slots)
            if estimate.ert_slots >= 0:
                feasible_ids.append(action.action_id)
            best_fallback = self._echo_better_fallback(best_fallback, action.action_id, estimate.lateness_slots)
        deadline_mask = tuple(sorted(feasible_ids)) if feasible_ids else ((best_fallback[0],) if best_fallback is not None else ("local",))
        state_schema = (
            "arrival_indicator",
            "task_size",
            "processing_density",
            "timeout_length",
            "queue_load",
            "local_queue_depth",
            "outbound_queue_depth",
            "local_ert",
            "min_outbound_ert",
            "mask_local",
            "mask_horizontal",
            "mask_vertical",
        )
        horizontal_allowed = any(action_id.startswith("horizontal_") for action_id in deadline_mask)
        vertical_allowed = "cloud" in deadline_mask
        min_outbound_ert = min((value for key, value in candidate_ert.items() if key != "local"), default=0.0)
        state_vector = (
            1.0,
            float(task.size),
            float(task.processing_density),
            float(task.timeout_length),
            float(self.queue_load),
            float(len(local_queue.tasks) if local_queue else 0),
            float(sum(len(queue.tasks) for queue in self._offloading_queues.values() if queue.owner_node_id == str(task.source_agent_id))),
            float(candidate_ert.get("local", 0.0)),
            float(min_outbound_ert),
            1.0 if "local" in deadline_mask else 0.0,
            1.0 if horizontal_allowed else 0.0,
            1.0 if vertical_allowed else 0.0,
        )
        return {
            "state_schema": state_schema,
            "state_vector": state_vector,
            "action_ids": tuple(candidate_ert.keys()),
            "candidate_ert": candidate_ert,
            "deadline_mask": deadline_mask,
        }

    @staticmethod
    def _echo_better_fallback(current: tuple[str, float] | None, action_id: str, lateness_slots: float) -> tuple[str, float]:
        if current is None:
            return (action_id, float(lateness_slots))
        if float(lateness_slots) < current[1]:
            return (action_id, float(lateness_slots))
        if float(lateness_slots) == current[1] and action_id < current[0]:
            return (action_id, float(lateness_slots))
        return current

    def _trace_from_loaded_payload(self, trace_id: str, payload: dict[str, Any]) -> EvaluationTrace:
        tasks_raw = payload.get("tasks", [])
        blueprints: list[TraceTaskBlueprint] = []
        metadata = dict(payload.get("metadata", {})) if isinstance(payload.get("metadata", {}), dict) else {}
        for index, item in enumerate(tasks_raw):
            if not isinstance(item, dict):
                continue
            blueprints.append(
                TraceTaskBlueprint(
                    task_id=int(item.get("task_id", index + 1)),
                    source_agent_id=int(item.get("source_agent_id", 1)),
                    arrival_slot=int(item.get("arrival_slot", index)),
                    size=float(item.get("size", 1)),
                    processing_density=float(item.get("processing_density", 1)),
                    timeout_length=int(item.get("timeout_length", 1)),
                    absolute_deadline_slot=int(item.get("absolute_deadline_slot", int(item.get("arrival_slot", index)) + int(item.get("timeout_length", 1)))),
                    cycles_required=float(item.get("cycles_required", 0.0)),
                    cycles_remaining=float(item.get("cycles_remaining", 0.0)),
                )
            )
        metadata.update({"mode": "trace_bank", "trace_id": trace_id})
        seed = int(payload.get("seed", self.seed or 0))
        return EvaluationTrace(trace_id=trace_id, seed=seed, tasks=tuple(blueprints), metadata=metadata)

    @staticmethod
    def _trace_sort_key(blueprint: TraceTaskBlueprint) -> tuple[int, int, int]:
        return (blueprint.arrival_slot, blueprint.source_agent_id, blueprint.task_id)
