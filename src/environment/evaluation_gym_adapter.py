from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.evaluation.trace_protocol import EvaluationTrace
from src.policies.action_masking import select_legal_action
from src.policies.policy_interface import PolicyContext

from .environment import apply_policy_action
from .gym_adapter import HoodieGymEnvironment
from .offload_trace_ledger import OffloadTraceLedger


@dataclass(slots=True)
class EvaluationHoodieGymEnvironment(HoodieGymEnvironment):
    """Evaluation environment with exact paired traces and slot-batched decisions.

    All tasks whose blueprint arrival slot equals the current physical slot are
    decided and admitted before computation or transmission advances.  This is
    required by the paper model, in which every EA has an independent arrival
    opportunity at the same synchronized slot boundary.
    """

    supplied_trace: EvaluationTrace | None = None

    def reset(self, seed: int | None = None):
        # Reuse the base reset for queues, runtime objects, metrics, and ledgers,
        # then replace only the generated trace before the first decision.
        super().reset(seed=seed)
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
        """Execute one synchronized physical slot for one shared policy.

        The policy is called once for every task arriving in ``current_slot``.
        All those decisions observe the same slot index and are admitted before
        queue execution progresses exactly once.
        """

        if self.trace is None:
            raise RuntimeError("Environment must be reset before stepping")

        reward = 0.0
        task_resolution_events: list[dict[str, Any]] = []
        reward_delivery_events: list[dict[str, Any]] = []
        selected_action_emitted = False

        reward_delivery_events.extend(self._deliver_pending_rewards(self.current_slot))
        if reward_delivery_events:
            reward += sum(float(event["reward"]) for event in reward_delivery_events)

        # Decision phase: exhaust every blueprint eligible at this slot without
        # changing the physical clock or advancing any queue.
        while self._current_task is not None and self._current_task.arrival_slot <= self.current_slot:
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
            current_task.metadata["selected_action_family"] = self._selected_action_family(selected_action)
            current_task.metadata["action_index"] = self._canonical_action_index(selected_action)
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

            resolved_destination = self._resolve_destination(current_task, selected_action)
            apply_policy_action(
                current_task,
                context,
                selected_action,
                resolved_destination=resolved_destination,
            )
            ledger = OffloadTraceLedger()
            ledger.emit("selected_action")
            self._trace_ledgers[current_task.task_id] = ledger
            self._admit_current_task(current_task)
            selected_action_emitted = True

            self._current_task = None
            self._current_task = self._load_current_task()

        # Service phase: all source and destination resources advance exactly
        # once regardless of the number of decisions made above.
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
            and self._current_task is None
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
            finalized_tasks=finalized_tasks
            or (self._last_finalized_tasks if (terminated or truncated) else []),
            reward=reward,
            terminated=terminated,
            truncated=truncated,
            task_resolution_events=task_resolution_events,
            reward_delivery_events=reward_delivery_events,
        )
        return observation, reward, terminated, truncated, info

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
