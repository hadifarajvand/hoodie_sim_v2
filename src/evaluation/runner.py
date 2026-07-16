from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from src.environment.evaluation_gym_adapter import EvaluationHoodieGymEnvironment
from src.environment.link_rate_config import LinkRateConfig
from src.environment.runtime_model import SharedRuntimeParameters
from src.environment.topology import TopologyGraph

from .config import EvaluationConfig
from .metric_storage import persist_metrics
from .metrics import TaskEvaluationRecord, TraceMetrics, evaluate_run, evaluate_trace
from .run_metadata import RunMetadata
from .trace_protocol import EvaluationTrace, build_deterministic_trace


@runtime_checkable
class PolicyProtocol(Protocol):
    def choose_action(self, context):
        ...


@dataclass(slots=True)
class EvaluationRunner:
    """Run one policy on deterministic, paired cloud-edge task traces."""

    policy: PolicyProtocol
    config: EvaluationConfig
    topology: TopologyGraph | None = None
    runtime_parameters: SharedRuntimeParameters | None = None
    link_rate_config: LinkRateConfig | None = None
    task_sizes: tuple[float, ...] | None = None
    processing_density: float = 0.297

    def _trace_for_episode(self, episode_index: int) -> EvaluationTrace:
        trace_id = f"{self.config.trace_id}-{episode_index}"
        agent_count = (
            self.topology.node_count()
            if self.topology is not None
            else int(
                getattr(self.runtime_parameters, "agent_count", 20) or 20
            )
        )
        arrival_probability = float(
            getattr(self.runtime_parameters, "arrival_probability", 1.0)
            or 1.0
        )
        timeout_slots = int(
            getattr(self.runtime_parameters, "timeout_slots", 20) or 20
        )
        return build_deterministic_trace(
            trace_id,
            self.config.seed + episode_index,
            self.config.episode_length,
            agent_count=agent_count,
            arrival_probability=arrival_probability,
            timeout_length=timeout_slots,
            drain_slots=self.config.drain_slots,
            task_sizes=self.task_sizes,
            processing_density=self.processing_density,
        )

    def _validate_policy_topology(self) -> None:
        validator = getattr(self.policy, "validate_topology", None)
        if callable(validator):
            if self.topology is None:
                raise ValueError(
                    "a destination-aware policy requires an explicit topology"
                )
            validator(self.topology)

    def _evaluate_episode(self, trace: EvaluationTrace) -> TraceMetrics:
        self._validate_policy_topology()
        runtime_parameters = (
            self.runtime_parameters or SharedRuntimeParameters()
        )
        env = EvaluationHoodieGymEnvironment(
            episode_length=self.config.episode_length,
            topology=self.topology,
            runtime_parameters=runtime_parameters,
            compute_config=runtime_parameters.to_compute_config(),
            link_rate_config=self.link_rate_config
            or LinkRateConfig(
                slot_duration_seconds=runtime_parameters.slot_duration
            ),
            policy_name=self.config.policy_name,
            supplied_trace=trace,
        )
        env.reset(seed=trace.seed)
        records_by_task: dict[int, TaskEvaluationRecord] = {}
        decision_by_task: dict[int, dict[str, object]] = {}

        while True:
            _observation, _reward, terminated, truncated, info = env.step_slot(
                self.policy
            )
            for decision in info.get("decision_events", []):
                decision_by_task[int(decision["task_id"])] = dict(decision)
            for finalized in info.get("finalized_tasks", []):
                task_id = int(finalized["task_id"])
                terminal_outcome = finalized.get("terminal_outcome")
                completion_slot = (
                    int(finalized["completion_slot"])
                    if finalized.get("completion_slot") is not None
                    else None
                )
                decision = decision_by_task.get(task_id, {})
                state = decision.get("state", {})
                decision_observation = (
                    {str(key): value for key, value in state.items()}
                    if isinstance(state, dict)
                    else {}
                )
                raw_mask = decision.get("legal_action_mask", {})
                legal_action_mask = (
                    {
                        str(key): bool(value)
                        for key, value in raw_mask.items()
                    }
                    if isinstance(raw_mask, dict)
                    else {}
                )
                records_by_task[task_id] = TaskEvaluationRecord(
                    task_id=task_id,
                    arrival_slot=int(finalized["arrival_slot"]),
                    completion_slot=completion_slot,
                    terminal_outcome=terminal_outcome,
                    selected_action=finalized.get("selected_action"),
                    resolved_destination=finalized.get(
                        "resolved_destination"
                    ),
                    delay=(
                        completion_slot
                        - int(finalized["arrival_slot"])
                        + 1
                        if terminal_outcome == "completed"
                        and completion_slot is not None
                        else None
                    ),
                    source_agent_id=(
                        int(decision["source_agent_id"])
                        if decision.get("source_agent_id") is not None
                        else None
                    ),
                    decision_slot=(
                        int(decision["decision_slot"])
                        if decision.get("decision_slot") is not None
                        else None
                    ),
                    legal_action_mask=legal_action_mask,
                    decision_observation=decision_observation,
                )
            if terminated or truncated:
                break

        records = [records_by_task[key] for key in sorted(records_by_task)]
        return evaluate_trace(
            trace_id=trace.trace_id,
            policy_name=self.config.policy_name,
            seed=trace.seed,
            device=self.config.device,
            records=records,
        )

    def run(self) -> dict[str, object]:
        trace_metrics: list[TraceMetrics] = []
        for episode_index in range(self.config.episode_count):
            trace = self._trace_for_episode(episode_index)
            metrics = self._evaluate_episode(trace)
            trace_metrics.append(metrics)
            if self.config.output_dir is not None:
                persist_metrics(self.config.output_dir, metrics)

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
            "aggregate": evaluate_run(trace_metrics),
        }
