from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
import json
from typing import Any

from src.environment.compute_config import ComputeConfig
from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.runtime_model import SharedRuntimeParameters
from src.environment.topology import TopologyGraph
from src.environment.trace_source import TraceSource
from src.environment.traffic_config import TrafficConfig
from src.environment.traffic_generator import TrafficGenerator
from src.environment.traffic_observer import TrafficObserver
from src.evaluation.trace_protocol import EvaluationTrace, TraceTaskBlueprint

from .classify import classify_monotonic
from .report import DEFAULT_OUTPUT_DIR, write_controlled_mechanistic_sweep_report
from .sweeps import (
    ControlledMechanisticSweepReport,
    FixedInput,
    MonotonicCheck,
    SweepDefinition,
    SweepObservation,
    build_controlled_mechanistic_sweep_definitions,
)


def _trace_payload(trace: EvaluationTrace) -> dict[str, object]:
    return {
        "trace_id": trace.trace_id,
        "seed": trace.seed,
        "metadata": dict(trace.metadata),
        "tasks": [
            {
                "task_id": blueprint.task_id,
                "source_agent_id": blueprint.source_agent_id,
                "arrival_slot": blueprint.arrival_slot,
                "size": blueprint.size,
                "processing_density": blueprint.processing_density,
                "timeout_length": blueprint.timeout_length,
                "absolute_deadline_slot": blueprint.absolute_deadline_slot,
                "cycles_required": blueprint.cycles_required,
                "cycles_remaining": blueprint.cycles_remaining,
            }
            for blueprint in trace.tasks
        ],
    }


def _one_task_trace(trace_id: str, *, seed: int, timeout_slots: int, size: float = 4.0, processing_density: float = 1.0) -> EvaluationTrace:
    task = TraceTaskBlueprint(
        task_id=1,
        source_agent_id=1,
        arrival_slot=0,
        size=size,
        processing_density=processing_density,
        timeout_length=timeout_slots,
        absolute_deadline_slot=timeout_slots,
    )
    return EvaluationTrace(trace_id=trace_id, seed=seed, tasks=(task,), metadata={"mode": "analysis", "trace_id": trace_id, "seed": str(seed)})


def _traffic_config(*, arrival_probability: float, timeout_slots: int, episode_length: int = 6) -> TrafficConfig:
    return TrafficConfig(
        scenario_name="paper_default",
        number_of_agents=1,
        episode_length=episode_length,
        arrival_probability=arrival_probability,
        slot_duration_seconds=0.1,
        timeout_slots=timeout_slots,
        task_size_mbits_min=4.0,
        task_size_mbits_max=4.0,
        task_size_mbits_step=0.1,
        processing_density_gcycles_per_mbit=1.0,
    )


def _topology_for_density(value: str) -> TopologyGraph:
    if value == "sparse":
        return TopologyGraph(node_ids=("1",), legal_adjacency={"1": ()})
    if value == "default":
        return TopologyGraph(node_ids=("1", "2"), legal_adjacency={"1": ("2",)})
    if value == "dense":
        return TopologyGraph(node_ids=("1", "2", "cloud"), legal_adjacency={"1": ("2", "cloud")})
    raise ValueError(f"Unsupported topology density label: {value}")


@dataclass(slots=True)
class _FamilyResult:
    fixed_inputs: list[FixedInput]
    observations: list[SweepObservation]
    monotonic_check: MonotonicCheck
    warnings: list[str]
    instrumentation_gaps: list[str]


class ControlledMechanisticSweepRunner:
    def __init__(self, output_dir: Path | str | None = None):
        self.output_dir = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR

    def run(self) -> ControlledMechanisticSweepReport:
        definitions = build_controlled_mechanistic_sweep_definitions()
        fixed_inputs: list[FixedInput] = []
        observations: list[SweepObservation] = []
        monotonic_checks: list[MonotonicCheck] = []
        warnings: list[str] = []
        instrumentation_gaps: list[str] = []

        for definition in definitions:
            result = self._run_definition(definition)
            fixed_inputs.extend(result.fixed_inputs)
            observations.extend(result.observations)
            monotonic_checks.append(result.monotonic_check)
            warnings.extend(result.warnings)
            instrumentation_gaps.extend(result.instrumentation_gaps)

        report = ControlledMechanisticSweepReport(
            metadata={
                "feature_id": "020-controlled-mechanistic-sweeps",
                "generated_by": "controlled_mechanistic_sweeps",
                "deterministic": True,
                "source_refs": [
                    "specs/020-controlled-mechanistic-sweeps/spec.md",
                    "specs/020-controlled-mechanistic-sweeps/plan.md",
                    "specs/020-controlled-mechanistic-sweeps/research.md",
                    "src/environment/traffic_config.py",
                    "src/environment/traffic_generator.py",
                    "src/environment/traffic_observer.py",
                    "src/environment/gym_adapter.py",
                ],
            },
            sweep_definitions=list(definitions),
            fixed_inputs=fixed_inputs,
            observations=observations,
            monotonic_checks=monotonic_checks,
            warnings=warnings,
            instrumentation_gaps=instrumentation_gaps,
            limitations=[
                "This feature is diagnostic only and does not prove paper-level completeness.",
                "Unsupported or unobservable dimensions remain classified instead of being patched.",
            ],
            no_campaign_rerun_disclaimer="No baseline campaigns were rerun to generate this report.",
            no_paper_validity_disclaimer="This report is not a paper-validity or reproduction-completeness claim.",
            reproducibility={
                "approved_interpreter": "/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python",
                "fixed_seeds": [7],
                "deterministic_ordering": "definitions -> fixed inputs -> observations -> checks",
                "run_count_per_value": 1,
            },
            overall_status=self._overall_status(monotonic_checks),
        )
        write_controlled_mechanistic_sweep_report(report, self.output_dir)
        return report

    def _overall_status(self, checks: list[MonotonicCheck]) -> str:
        statuses = [check.status for check in checks]
        if "instrumentation_gap" in statuses:
            return "instrumentation_gap"
        if "inconclusive" in statuses:
            return "inconclusive"
        if "warn" in statuses:
            return "warn"
        return "pass"

    def _run_definition(self, definition: SweepDefinition) -> _FamilyResult:
        if definition.name == "arrival_probability":
            return self._run_arrival_probability(definition)
        if definition.name == "timeout":
            return self._run_timeout(definition)
        if definition.name == "cpu_capacity":
            return self._run_cpu_capacity(definition)
        if definition.name == "link_rate":
            return self._run_link_rate(definition)
        if definition.name == "topology_density":
            return self._run_topology_density(definition)
        raise ValueError(f"Unsupported sweep definition: {definition.name}")

    def _run_arrival_probability(self, definition: SweepDefinition) -> _FamilyResult:
        fixed_inputs: list[FixedInput] = []
        observations: list[SweepObservation] = []
        seed = definition.fixed_seeds[0]
        for value in definition.values:
            config = _traffic_config(arrival_probability=float(value), timeout_slots=2, episode_length=6)
            trace = TrafficGenerator.generate(config, seed)
            summary = TrafficObserver.summarize(trace.evaluation_trace, config, seed)
            fixed_inputs.append(
                FixedInput(
                    sweep_name=definition.name,
                    seed=seed,
                    parameter_value=value,
                    trace_identifier=trace.trace_id,
                    control_notes=definition.control_notes,
                )
            )
            observations.append(
                SweepObservation(
                    sweep_name=definition.name,
                    seed=seed,
                    parameter_value=value,
                    observed_pressure_indicator=float(summary.observed_arrival_probability),
                    observed_outcome_summary=f"arrivals={summary.total_arrivals}, observed_probability={summary.observed_arrival_probability}",
                    evidence_available=True,
                )
            )
        check = classify_monotonic(definition, observations)
        warnings = [f"{definition.name} remains qualitative and does not claim paper-validity."]
        return _FamilyResult(fixed_inputs, observations, check, warnings if check.status == "warn" else [], [])

    def _run_timeout(self, definition: SweepDefinition) -> _FamilyResult:
        return self._run_environment_family(
            definition=definition,
            values=definition.values,
            seed=definition.fixed_seeds[0],
            timeout_slots=definition.values,
            compute_config=ComputeConfig(cpu_capacity_per_slot_agent=2.0, cpu_capacity_per_slot_edge=2.0, cpu_capacity_per_slot_cloud=2.0),
            summarize=lambda info: float(info["metrics"]["dropped"]),
            summary_name="dropped",
            action_selector=lambda _env, _task: "local",
            episode_length=5,
        )

    def _run_cpu_capacity(self, definition: SweepDefinition) -> _FamilyResult:
        return self._run_environment_family(
            definition=definition,
            values=definition.values,
            seed=definition.fixed_seeds[0],
            timeout_slots=[3, 3, 3],
            compute_config_factory=lambda value: ComputeConfig(cpu_capacity_per_slot_agent=float(value), cpu_capacity_per_slot_edge=float(value), cpu_capacity_per_slot_cloud=float(value)),
            summarize=lambda info: float(info["metrics"]["completed"]),
            summary_name="completed",
            action_selector=lambda _env, _task: "local",
            episode_length=5,
        )

    def _run_link_rate(self, definition: SweepDefinition) -> _FamilyResult:
        seed = definition.fixed_seeds[0]
        fixed_inputs: list[FixedInput] = []
        observations: list[SweepObservation] = []
        for value in definition.values:
            fixed_inputs.append(
                FixedInput(
                    sweep_name=definition.name,
                    seed=seed,
                    parameter_value=value,
                    trace_identifier=f"unsupported-{definition.name}-{value}",
                    control_notes=definition.control_notes,
                )
            )
            observations.append(
                SweepObservation(
                    sweep_name=definition.name,
                    seed=seed,
                    parameter_value=value,
                    observed_pressure_indicator=None,
                    observed_outcome_summary="no direct public control for link rate; instrumentation gap recorded",
                    evidence_available=False,
                )
            )
        check = classify_monotonic(definition, observations)
        return _FamilyResult(
            fixed_inputs,
            observations,
            check,
            [],
            [f"{definition.name.replace('_', ' ')}: {definition.control_notes}"],
        )

    def _run_topology_density(self, definition: SweepDefinition) -> _FamilyResult:
        fixed_inputs: list[FixedInput] = []
        observations: list[SweepObservation] = []
        seed = definition.fixed_seeds[0]
        config = _traffic_config(arrival_probability=1.0, timeout_slots=3, episode_length=1)
        trace = self._single_task_trace(seed=seed, timeout_slots=3)
        for value in definition.values:
            topology = _topology_for_density(str(value))
            mask_count = self._topology_offload_opportunities(trace, topology)
            fixed_inputs.append(
                FixedInput(
                    sweep_name=definition.name,
                    seed=seed,
                    parameter_value=value,
                    trace_identifier=trace.trace_id,
                    control_notes=definition.control_notes,
                )
            )
            observations.append(
                SweepObservation(
                    sweep_name=definition.name,
                    seed=seed,
                    parameter_value=value,
                    observed_pressure_indicator=float(mask_count),
                    observed_outcome_summary=f"offload_opportunities={mask_count}",
                    evidence_available=True,
                )
            )
        check = classify_monotonic(definition, observations)
        return _FamilyResult(fixed_inputs, observations, check, [], [])

    def _single_task_trace(self, *, seed: int, timeout_slots: int) -> EvaluationTrace:
        trace_id = f"controlled-mechanistic-sweeps-{seed}"
        return _one_task_trace(trace_id, seed=seed, timeout_slots=timeout_slots)

    def _topology_offload_opportunities(self, trace: EvaluationTrace, topology: TopologyGraph) -> int:
        with TemporaryDirectory() as tmpdir:
            trace_root = Path(tmpdir)
            payload_path = trace_root / f"{trace.trace_id}.json"
            payload_path.write_text(json.dumps(_trace_payload(trace), indent=2), encoding="utf-8")
            env = HoodieGymEnvironment(
                episode_length=5,
                topology=topology,
                runtime_parameters=SharedRuntimeParameters(runtime_variant="density_based"),
                compute_config=ComputeConfig(cpu_capacity_per_slot_agent=2.0, cpu_capacity_per_slot_edge=2.0, cpu_capacity_per_slot_cloud=2.0),
                trace_source=TraceSource.from_trace_bank(trace.trace_id, root_path=trace_root),
                policy_name="FLC",
            )
            env.reset(seed=None)
            current_task = env.current_task
            if current_task is None:
                return 0
            mask = env.legal_action_mask(current_task)
            return int(bool(mask.get("horizontal"))) + int(bool(mask.get("vertical")))

    def _run_environment_family(
        self,
        *,
        definition: SweepDefinition,
        values: tuple[object, ...],
        seed: int,
        timeout_slots: int | list[int] | tuple[int, ...],
        compute_config: ComputeConfig | None = None,
        compute_config_factory: Callable[[object], ComputeConfig] | None = None,
        summarize: Callable[[dict[str, Any]], float],
        summary_name: str,
        action_selector: Callable[[HoodieGymEnvironment, object], str],
        episode_length: int,
    ) -> _FamilyResult:
        fixed_inputs: list[FixedInput] = []
        observations: list[SweepObservation] = []
        for index, value in enumerate(values):
            timeout_value = timeout_slots[index] if isinstance(timeout_slots, (list, tuple)) else timeout_slots
            trace = self._single_task_trace(seed=seed, timeout_slots=int(timeout_value))
            local_compute = compute_config_factory(value) if compute_config_factory is not None else compute_config
            assert local_compute is not None
            observation, info = self._run_single_task_episode(
                trace=trace,
                topology=None,
                compute_config=local_compute,
                action_selector=action_selector,
                episode_length=episode_length,
            )
            fixed_inputs.append(
                FixedInput(
                    sweep_name=definition.name,
                    seed=seed,
                    parameter_value=value,
                    trace_identifier=trace.trace_id,
                    control_notes=definition.control_notes,
                )
            )
            observations.append(
                SweepObservation(
                    sweep_name=definition.name,
                    seed=seed,
                    parameter_value=value,
                    observed_pressure_indicator=summarize(info),
                    observed_outcome_summary=f"{summary_name}={summarize(info)} final_outcomes={[task['terminal_outcome'] for task in info['finalized_tasks']]}",
                    evidence_available=True,
                )
            )
        check = classify_monotonic(definition, observations)
        warnings: list[str] = []
        if check.status == "warn":
            warnings.append(f"{definition.name} remained flat across the tiny sweep.")
        return _FamilyResult(fixed_inputs, observations, check, warnings, [])

    def _run_single_task_episode(
        self,
        *,
        trace: EvaluationTrace,
        topology: TopologyGraph | None,
        compute_config: ComputeConfig,
        action_selector: Callable[[HoodieGymEnvironment, object], str],
        episode_length: int,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        with TemporaryDirectory() as tmpdir:
            trace_root = Path(tmpdir)
            payload_path = trace_root / f"{trace.trace_id}.json"
            payload_path.write_text(json.dumps(_trace_payload(trace), indent=2), encoding="utf-8")
            env = HoodieGymEnvironment(
                episode_length=episode_length,
                topology=topology,
                runtime_parameters=SharedRuntimeParameters(runtime_variant="density_based"),
                compute_config=compute_config,
                trace_source=TraceSource.from_trace_bank(trace.trace_id, root_path=trace_root),
                policy_name="FLC",
            )
            env.reset(seed=None)
            last_info: dict[str, Any] = {}
            last_observation: dict[str, Any] = {}
            for _ in range(episode_length + 3):
                current_task = env.current_task
                action = action_selector(env, current_task) if current_task is not None else None
                last_observation, _reward, terminated, truncated, last_info = env.step(action)
                if terminated or truncated:
                    break
            return last_observation, last_info


def run_controlled_mechanistic_sweeps(output_dir: Path | str | None = None) -> ControlledMechanisticSweepReport:
    return ControlledMechanisticSweepRunner(output_dir=output_dir).run()
