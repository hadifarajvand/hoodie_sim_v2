from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from src.environment.environment import apply_policy_action, finalize_task_runtime_state_with_parameters
from src.environment.slot_engine import SlotEngine
from src.environment.task import Task
from src.environment.topology import TopologyGraph
from src.policies.policy_interface import PolicyContext

from .config import EvaluationConfig
from .fairness_checks import assert_fair_evaluation
from .metric_storage import persist_metrics
from .metrics import TaskEvaluationRecord, TraceMetrics, evaluate_run, evaluate_trace
from .run_metadata import RunMetadata
from .trace_protocol import EvaluationTrace, build_deterministic_trace


@runtime_checkable
class PolicyProtocol(Protocol):
    def choose_action(self, context: PolicyContext) -> str:
        ...


@dataclass(slots=True)
class EvaluationRunner:
    policy: PolicyProtocol
    config: EvaluationConfig
    topology: TopologyGraph | None = None

    def _trace_for_episode(self, episode_index: int) -> EvaluationTrace:
        trace_id = f"{self.config.trace_id}-{episode_index}"
        return build_deterministic_trace(trace_id, self.config.seed + episode_index, self.config.episode_length)

    def _evaluate_episode(self, trace: EvaluationTrace) -> TraceMetrics:
        engine = SlotEngine(current_slot=0, trace_metadata=trace.metadata)
        records: list[TaskEvaluationRecord] = []
        for blueprint in trace.tasks:
            task = blueprint.build()
            legal_action_mask = self._legal_action_mask(task)
            observation = self._build_observation(task, legal_action_mask)
            context = PolicyContext(
                observation=observation,
                legal_action_mask=legal_action_mask,
                trace_history=(trace.trace_id,),
            )
            action = self.policy.choose_action(context)
            apply_policy_action(task, context, action, resolved_destination=self._resolved_destination(task, action))
            self._advance_task_through_slot_path(engine, task)
            finalize_task_runtime_state_with_parameters(task, task.completion_slot or task.arrival_slot, engine.runtime_parameters)
            records.append(
                TaskEvaluationRecord(
                    task_id=task.task_id,
                    arrival_slot=task.arrival_slot,
                    completion_slot=task.completion_slot,
                    terminal_outcome=task.terminal_outcome,
                    selected_action=task.selected_action,
                    resolved_destination=task.resolved_destination,
                    delay=(
                        task.completion_slot - task.arrival_slot
                        if task.terminal_outcome == "completed" and task.completion_slot is not None
                        else None
                    ),
                )
            )
        return evaluate_trace(
            trace_id=trace.trace_id,
            policy_name=self.config.policy_name,
            seed=trace.seed,
            device=self.config.device,
            records=records,
        )

    def _build_observation(self, task: Task, legal_action_mask: dict[str, bool]) -> dict[str, object]:
        observation: dict[str, object] = {
            "task_id": task.task_id,
            "arrival_slot": task.arrival_slot,
        }
        if self.topology is not None:
            observation["topology"] = self.topology.legal_adjacency.get(str(task.source_agent_id), ())
        fallback_hints: dict[str, int] = {}
        if legal_action_mask.get("local", False):
            fallback_hints["local"] = 1
        if legal_action_mask.get("horizontal", False):
            fallback_hints["horizontal"] = 2
        if legal_action_mask.get("vertical", False):
            fallback_hints["vertical"] = 3
        observation["fallback_hints"] = fallback_hints
        return observation

    def _legal_action_mask(self, task: Task) -> dict[str, bool]:
        legal = {
            "local": True,
            "compute_local": True,
            "horizontal": False,
            "offload_horizontal": False,
            "vertical": False,
            "offload_vertical": False,
        }
        if self.topology is not None:
            allowed = self.topology.legal_adjacency.get(str(task.source_agent_id), ())
            legal["horizontal"] = any(destination != "cloud" for destination in allowed)
            legal["offload_horizontal"] = legal["horizontal"]
            legal["vertical"] = "cloud" in allowed
            legal["offload_vertical"] = legal["vertical"]
        else:
            legal["horizontal"] = True
            legal["offload_horizontal"] = True
            legal["vertical"] = True
            legal["offload_vertical"] = True
        return legal

    def _resolved_destination(self, task: Task, action: str) -> str:
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
        raise ValueError(f"Unsupported action for destination resolution: {action}")

    def _advance_task_through_slot_path(self, engine: SlotEngine, task: Task) -> None:
        engine.run_slot([task])

    def run(self) -> dict[str, object]:
        trace_metrics = []
        for episode_index in range(self.config.episode_count):
            trace = self._trace_for_episode(episode_index)
            trace_metrics.append(self._evaluate_episode(trace))
            if self.config.output_dir is not None:
                persist_metrics(self.config.output_dir, trace_metrics[-1])
        run_metrics = evaluate_run(trace_metrics)
        metadata = RunMetadata(
            policy_name=self.config.policy_name,
            trace_id=self.config.trace_id,
            seed=self.config.seed,
            device=self.config.device,
            trace_mode=self.config.trace_mode,
        )
        return {
            "metadata": metadata.to_dict(),
            "per_trace": [metric.to_dict() for metric in trace_metrics],
            "aggregate": run_metrics,
        }
