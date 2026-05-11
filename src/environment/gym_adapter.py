from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from src.evaluation.trace_protocol import EvaluationTrace, TraceTaskBlueprint, build_deterministic_trace
from src.policies.action_masking import select_legal_action
from src.policies.policy_interface import PolicyContext

from .environment import apply_policy_action, finalize_task_runtime_state_with_parameters
from .compute_config import ComputeConfig
from .execution_helper import step_execution
from .offload_trace_ledger import OffloadTraceLedger
from .offloading_queue import OffloadingQueue
from .offload_trace_schema import OFFLOAD_LIFECYCLE_EVENTS
from .private_queue import PrivateQueue
from .public_queue import PublicQueue
from .reward_timing import emit_delayed_reward, reward_for_terminal_task
from .runtime_model import SharedRuntimeParameters, advance_shared_runtime
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


@dataclass(slots=True)
class HoodieGymEnvironment:
    """Owns all episode and slot lifecycle orchestration for the Gym-style boundary."""

    episode_length: int
    topology: TopologyGraph | None = None
    runtime_parameters: SharedRuntimeParameters = field(default_factory=SharedRuntimeParameters)
    compute_config: ComputeConfig = field(default_factory=ComputeConfig)
    trace_source: TraceSource | None = None
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
        self._metrics = {"completed": 0.0, "dropped": 0.0, "reward": 0.0}
        self._drain_mode = False
        self.engine.current_slot = 0

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
            return observation
        observation.update(self._agent_observation(current_task))
        return observation

    def _agent_observation(self, task: Task) -> dict[str, Any]:
        legal_action_mask = self.legal_action_mask(task)
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
        }

    def legal_action_mask(self, task: Task | None = None) -> dict[str, bool]:
        if task is None and self._current_task is None:
            return {}
        source_id = str((task or self._current_task).source_agent_id)
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
        allowed = self.topology.legal_adjacency.get(source_id, ())
        legal["horizontal"] = any(destination != "cloud" for destination in allowed)
        legal["offload_horizontal"] = legal["horizontal"]
        legal["vertical"] = "cloud" in allowed
        legal["offload_vertical"] = legal["vertical"]
        return legal

    def step(self, action: str | None) -> tuple[dict[str, Any], float, bool, bool, dict[str, Any]]:
        if self.trace is None:
            raise RuntimeError("Environment must be reset before stepping")
        reward = 0.0
        finalized_tasks: list[Task] = []
        current_task = self._current_task
        if current_task is not None:
            if action is None:
                raise ValueError("An action is required while a task is pending")
            legal_action_mask = self.legal_action_mask(current_task)
            context = PolicyContext(
                observation=self.observe_flat(current_task),
                legal_action_mask=legal_action_mask,
                trace_history=(self.trace.trace_id,),
            )
            selected_action = select_legal_action(context, action)
            resolved_destination = self._resolve_destination(current_task, selected_action)
            apply_policy_action(current_task, context, selected_action, resolved_destination=resolved_destination)
            ledger = OffloadTraceLedger()
            ledger.emit("selected_action")
            self._trace_ledgers[current_task.task_id] = ledger
            self._admit_current_task(current_task)
            self._current_task = None

        finalized_tasks.extend(self._progress_offloading_queues())
        finalized_tasks.extend(self._progress_execution_queues())
        for task in finalized_tasks:
            finalize_task_runtime_state_with_parameters(task, self.current_slot, self.runtime_parameters)
            emit_delayed_reward(task)
            task_reward = reward_for_terminal_task(task)
            reward += task_reward
            self._record_outcome(task, task_reward)

        self.engine.current_slot = self.current_slot
        self.current_slot += 1
        self._current_task = self._load_current_task()
        truncated = self.current_slot >= self.episode_length
        terminated = self._is_terminated() and not truncated
        observation = self.observe()
        info = self._build_info(finalized_tasks=finalized_tasks, reward=reward, terminated=terminated, truncated=truncated)
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
        return task

    def _admit_current_task(self, task: Task) -> None:
        source_id = str(task.source_agent_id)
        if task.selected_action in {"local", "compute_local"}:
            queue = self._private_queues.setdefault(source_id, PrivateQueue(owner_node_id=source_id))
            queue.enqueue(task, slot=self.current_slot)
            task.start_slot = self.current_slot
            self._trace_ledgers.setdefault(task.task_id, OffloadTraceLedger()).emit("execution_started")
            return
        destination = self._resolve_destination(task, task.selected_action or "")
        queue = self._offloading_queues.setdefault(
            (source_id, destination),
            OffloadingQueue(owner_node_id=source_id, resolved_destination=destination),
        )
        queue.enqueue(task, slot=self.current_slot)
        task.start_slot = self.current_slot
        ledger = self._trace_ledgers.setdefault(task.task_id, OffloadTraceLedger())
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
            if admitted:
                task = self._public_queue_for(source_id, destination).tasks[-1]
                task.metadata["public_queue_admitted_at"] = self.current_slot
                self._trace_ledgers.setdefault(task.task_id, OffloadTraceLedger()).emit("transmission_completed")
        return finalized

    def _progress_execution_queues(self) -> list[Task]:
        finalized: list[Task] = []
        for queue in list(self._private_queues.values()):
            finalized.extend(self._maybe_finalize_head(queue, "local"))
        for queue in list(self._public_queues.values()):
            destination_kind = "cloud" if queue.host_node_id == "cloud" else "public"
            finalized.extend(self._maybe_finalize_head(queue, destination_kind))
        return finalized

    def _maybe_finalize_head(self, queue: PrivateQueue | PublicQueue, destination_kind: str) -> list[Task]:
        if not queue.tasks:
            return []
        task = queue.tasks[0]
        ledger = self._trace_ledgers.setdefault(task.task_id, OffloadTraceLedger())
        if "execution_started" not in ledger.snapshot():
            ledger.emit("execution_started")
        advance_shared_runtime(task, destination_kind, self.current_slot, self.runtime_parameters)
        execution_progress = step_execution(
            task,
            self.compute_config.capacity_for(destination_kind),
            slot=self.current_slot,
            destination_kind=destination_kind,
        )
        if not execution_progress.completed:
            return []
        finalized = queue.dequeue()
        ledger.emit("execution_completed")
        return [finalized]

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
        if self.topology is not None:
            allowed = self.topology.legal_adjacency.get(str(task.source_agent_id), ())
            if action in {"horizontal", "offload_horizontal"}:
                for destination in allowed:
                    if destination != "cloud":
                        return destination
                raise ValueError("No topology-backed horizontal destination available")
            if action in {"vertical", "offload_vertical"}:
                if "cloud" in allowed:
                    return "cloud"
                raise ValueError("No topology-backed vertical destination available")
        if action in {"horizontal", "offload_horizontal", "vertical", "offload_vertical"}:
            raise ValueError("Topology-backed destination required for offload actions")
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
        estimates: dict[str, float] = {}
        if legal_action_mask.get("local", False):
            estimates["local"] = task.processing_density
        if legal_action_mask.get("horizontal", False):
            estimates["horizontal"] = float(max(1, task.processing_density - 1))
        if legal_action_mask.get("vertical", False):
            estimates["vertical"] = float(max(1, task.processing_density - 2))
        return estimates

    def _balance_hints(self, task: Task, legal_action_mask: dict[str, bool]) -> dict[str, float]:
        hints: dict[str, float] = {}
        if legal_action_mask.get("local", False):
            hints["local"] = float(max(1, task.size // 4))
        if legal_action_mask.get("horizontal", False):
            hints["horizontal"] = float(max(1, task.size // 3))
        if legal_action_mask.get("vertical", False):
            hints["vertical"] = float(max(1, task.size // 2))
        return hints

    def _record_outcome(self, task: Task, reward: float) -> None:
        ledger = self._trace_ledgers.setdefault(task.task_id, OffloadTraceLedger())
        if task.terminal_outcome == "dropped":
            ledger.emit("dropped_timeout")
        ledger.emit("reward_emitted")
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
        return not has_future_arrivals and not has_queued_work and self._current_task is None

    def _build_info(
        self,
        finalized_tasks: list[Task] | None = None,
        reward: float = 0.0,
        terminated: bool = False,
        truncated: bool = False,
    ) -> dict[str, Any]:
        return {
            "trace_id": self.trace.trace_id if self.trace is not None else "",
            "slot": self.current_slot,
            "reward": reward,
            "terminated": terminated,
            "truncated": truncated,
            "metrics": dict(self._metrics),
            "queue_load": self.queue_load,
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
            "offload_lifecycle_events": list(
                finalized_tasks[0].metadata.get("offload_lifecycle_events", ())
            )
            if finalized_tasks
            else [],
        }

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
