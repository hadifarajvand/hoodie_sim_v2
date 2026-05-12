from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.compute_config import ComputeConfig
from src.environment.runtime_model import SharedRuntimeParameters
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
    runtime_parameters: SharedRuntimeParameters | None = None

    def _trace_for_episode(self, episode_index: int) -> EvaluationTrace:
        trace_id = f"{self.config.trace_id}-{episode_index}"
        return build_deterministic_trace(trace_id, self.config.seed + episode_index, self.config.episode_length)

    def _evaluate_episode(self, trace: EvaluationTrace) -> TraceMetrics:
        env = HoodieGymEnvironment(
            episode_length=self.config.episode_length,
            topology=self.topology,
            runtime_parameters=self.runtime_parameters or SharedRuntimeParameters(),
            compute_config=ComputeConfig(
                cpu_capacity_per_slot_agent=0.5,
                cpu_capacity_per_slot_edge=0.5,
                cpu_capacity_per_slot_cloud=3.0,
            ),
            policy_name=self.config.policy_name,
        )
        observation, _info = env.reset(seed=trace.seed)
        records: list[TaskEvaluationRecord] = []
        while True:
            current_task = env.current_task
            if current_task is None:
                action = None
            else:
                observation = env.observe_flat(current_task)
                legal_action_mask = observation.get("legal_action_mask", {})
                context = PolicyContext(
                    observation=observation,
                    legal_action_mask=legal_action_mask,
                    trace_history=(trace.trace_id,),
                )
                action = self.policy.choose_action(context)
            observation, reward, terminated, truncated, info = env.step(action)
            if env.current_task is not None:
                observation = env.observe_flat()
            for finalized in info.get("finalized_tasks", []):
                records.append(
                    TaskEvaluationRecord(
                        task_id=int(finalized["task_id"]),
                        arrival_slot=int(finalized["arrival_slot"]),
                        completion_slot=int(finalized["completion_slot"]) if finalized.get("completion_slot") is not None else None,
                        terminal_outcome=finalized.get("terminal_outcome"),
                        selected_action=finalized.get("selected_action"),
                        resolved_destination=finalized.get("resolved_destination"),
                        delay=(
                            int(finalized["completion_slot"]) - int(finalized["arrival_slot"])
                            if finalized.get("terminal_outcome") == "completed" and finalized.get("completion_slot") is not None
                            else None
                        ),
                    )
                )
            if terminated or truncated:
                break
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
        fallback_hints: dict[str, float] = {}
        if legal_action_mask.get("local", False):
            fallback_hints["local"] = 1.0
        if legal_action_mask.get("horizontal", False):
            fallback_hints["horizontal"] = 2.0
        if legal_action_mask.get("vertical", False):
            fallback_hints["vertical"] = 3.0
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
            source_id = str(task.source_agent_id)
            allowed_horizontal = self.topology.legal_horizontal_destinations(source_id)
            legal["horizontal"] = bool(allowed_horizontal)
            legal["offload_horizontal"] = legal["horizontal"]
            legal["vertical"] = True
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
            source_id = str(task.source_agent_id)
            if action in {"horizontal", "offload_horizontal"}:
                allowed_horizontal = self.topology.legal_horizontal_destinations(source_id)
                if allowed_horizontal:
                    return allowed_horizontal[0]
                raise ValueError("No topology-backed horizontal destination available")
            if action in {"vertical", "offload_vertical"}:
                return "cloud"
        if action in {"horizontal", "offload_horizontal", "vertical", "offload_vertical"}:
            raise ValueError("Topology-backed destination required for offload actions")
        raise ValueError(f"Unsupported action for destination resolution: {action}")

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
