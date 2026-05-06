from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tempfile
import csv
import json
from typing import Any

from src.environment.compute_config import ComputeConfig
from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.runtime_model import SharedRuntimeParameters
from src.environment.topology import TopologyGraph
from src.environment.trace_source import TraceSource
from src.environment.traffic_generator import TrafficGenerator
from src.policies.adaptive_offloading import AdaptiveOffloadingPolicy
from src.policies.policy_interface import PolicyContext

from .metrics import TaskEvaluationRecord, evaluate_trace
from .matrix_config import EvaluationMatrixConfig
from .policy_registry import PolicyRegistry
from .run_metadata import RunMetadata
from .scenario_registry import ScenarioRegistry


@dataclass(slots=True)
class MatrixRunResult:
    policy_name: str
    scenario_name: str
    seed: int
    trace_id: str
    config_snapshot: dict[str, object]
    final_metrics: dict[str, object]
    runtime_metadata: dict[str, object]
    finalized_tasks: list[dict[str, object]]

    def to_dict(self) -> dict[str, object]:
        return {
            "policy_name": self.policy_name,
            "scenario_name": self.scenario_name,
            "seed": self.seed,
            "trace_id": self.trace_id,
            "config_snapshot": dict(self.config_snapshot),
            "final_metrics": dict(self.final_metrics),
            "runtime_metadata": dict(self.runtime_metadata),
            "finalized_tasks": list(self.finalized_tasks),
        }


class EvaluationMatrixRunner:
    def __init__(self, config: EvaluationMatrixConfig):
        self.config = config

    def _policy_order(self) -> tuple[str, ...]:
        return self.config.policy_names

    def _scenario_order(self) -> tuple[str, ...]:
        return self.config.scenario_names

    def _seed_order(self) -> tuple[int, ...]:
        return self.config.seeds

    def _default_topology(self, traffic_config) -> TopologyGraph:
        node_ids = tuple(str(agent_id) for agent_id in range(1, traffic_config.number_of_agents + 1)) + ("cloud",)
        legal_adjacency = {
            node_id: tuple(destination for destination in node_ids if destination != node_id)
            for node_id in node_ids[:-1]
        }
        legal_adjacency["cloud"] = tuple(node_id for node_id in node_ids if node_id != "cloud")
        return TopologyGraph(node_ids=node_ids, legal_adjacency=legal_adjacency)

    def _trace_directory(self) -> Path | None:
        if self.config.output_dir is None:
            return None
        trace_dir = self.config.output_dir / "traces"
        trace_dir.mkdir(parents=True, exist_ok=True)
        return trace_dir

    def _results_directory(self) -> Path | None:
        if self.config.output_dir is None:
            return None
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        return self.config.output_dir

    def _make_policy(self, policy_name: str) -> object:
        return PolicyRegistry.resolve(policy_name)

    def _make_scenario(self, scenario_name: str):
        return ScenarioRegistry.resolve(scenario_name, self.config.episode_length)

    def _evaluate_single(self, policy_name: str, scenario_name: str, seed: int) -> MatrixRunResult:
        traffic_config = self._make_scenario(scenario_name)
        traffic_trace = TrafficGenerator.generate(traffic_config, seed=seed)
        trace_dir = self._trace_directory()
        cleanup_dir: tempfile.TemporaryDirectory[str] | None = None
        if trace_dir is None:
            cleanup_dir = tempfile.TemporaryDirectory()
            trace_dir = Path(cleanup_dir.name)
        traffic_trace.write_json(trace_dir / f"{traffic_trace.trace_id}.json")
        trace_source = TraceSource.from_trace_bank(traffic_trace.trace_id, root_path=trace_dir)

        try:
            compute_config = self.config.compute_config or ComputeConfig()
            runtime_parameters = self.config.runtime_parameters or SharedRuntimeParameters()
            env = HoodieGymEnvironment(
                episode_length=self.config.episode_length or traffic_config.episode_length,
                topology=self._default_topology(traffic_config),
                runtime_parameters=runtime_parameters,
                compute_config=compute_config,
                trace_source=trace_source,
                policy_name=policy_name,
            )
            policy = self._make_policy(policy_name)
            observation, _info = env.reset(seed=None)
            finalized_tasks: list[dict[str, object]] = []
            while True:
                current_task = env.current_task
                if current_task is None:
                    action = None
                else:
                    observation = env.observe_flat(current_task)
                    context = PolicyContext(
                        observation=observation,
                        legal_action_mask=env.legal_action_mask(current_task),
                        trace_history=(traffic_trace.trace_id,),
                    )
                    action = policy.choose_action(context)
                observation, reward, terminated, truncated, info = env.step(action)
                finalized_tasks.extend(info.get("finalized_tasks", []))
                if terminated or truncated:
                    break
        finally:
            if cleanup_dir is not None:
                cleanup_dir.cleanup()

        records = [
            TaskEvaluationRecord(
                task_id=int(task["task_id"]),
                arrival_slot=int(task["arrival_slot"]),
                completion_slot=int(task["completion_slot"]) if task.get("completion_slot") is not None else None,
                terminal_outcome=task.get("terminal_outcome"),
                selected_action=task.get("selected_action"),
                resolved_destination=task.get("resolved_destination"),
                delay=(
                    int(task["completion_slot"]) - int(task["arrival_slot"])
                    if task.get("terminal_outcome") == "completed" and task.get("completion_slot") is not None
                    else None
                ),
            )
            for task in finalized_tasks
        ]
        final_metrics = evaluate_trace(
            trace_id=traffic_trace.trace_id,
            policy_name=policy_name,
            seed=seed,
            device="cpu",
            records=records,
        ).to_dict()
        runtime_metadata = RunMetadata(
            policy_name=policy_name,
            trace_id=traffic_trace.trace_id,
            seed=seed,
            device="cpu",
            trace_mode="matrix",
        ).to_dict()
        runtime_metadata["scenario_name"] = scenario_name
        runtime_metadata["dependency_change_note"] = self.config.dependency_change_note
        return MatrixRunResult(
            policy_name=policy_name,
            scenario_name=scenario_name,
            seed=seed,
            trace_id=traffic_trace.trace_id,
            config_snapshot={
                "policy_names": self.config.policy_names,
                "scenario_names": self.config.scenario_names,
                "seeds": self.config.seeds,
                "episode_length": self.config.episode_length,
                "output_dir": str(self.config.output_dir) if self.config.output_dir is not None else None,
                "dependency_change_note": self.config.dependency_change_note,
            },
            final_metrics=final_metrics,
            runtime_metadata=runtime_metadata,
            finalized_tasks=finalized_tasks,
        )

    def _write_artifacts(self, results: list[MatrixRunResult]) -> None:
        output_dir = self._results_directory()
        if output_dir is None:
            return
        for result in results:
            path = output_dir / f"{result.policy_name}-{result.scenario_name}-{result.seed}.json"
            path.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")
        summary_path = output_dir / "matrix-summary.csv"
        with summary_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "policy_name",
                    "scenario_name",
                    "seed",
                    "trace_id",
                    "average_delay",
                    "drop_ratio",
                    "throughput",
                    "completed_tasks",
                    "dropped_tasks",
                    "total_tasks",
                ],
            )
            writer.writeheader()
            for result in results:
                metrics = result.final_metrics
                writer.writerow(
                    {
                        "policy_name": result.policy_name,
                        "scenario_name": result.scenario_name,
                        "seed": result.seed,
                        "trace_id": result.trace_id,
                        "average_delay": metrics.get("average_delay", 0.0),
                        "drop_ratio": metrics.get("drop_ratio", 0.0),
                        "throughput": metrics.get("throughput", 0),
                        "completed_tasks": metrics.get("completed_tasks", 0),
                        "dropped_tasks": metrics.get("dropped_tasks", 0),
                        "total_tasks": metrics.get("total_tasks", 0),
                    }
                )

    def run(self) -> dict[str, object]:
        results: list[MatrixRunResult] = []
        for policy_name in self._policy_order():
            if policy_name not in PolicyRegistry.supported_names():
                raise ValueError(f"Unsupported policy name: {policy_name}")
            for scenario_name in self._scenario_order():
                if scenario_name not in ScenarioRegistry.supported_names():
                    raise ValueError(f"Unsupported scenario name: {scenario_name}")
                for seed in self._seed_order():
                    results.append(self._evaluate_single(policy_name, scenario_name, seed))
        self._write_artifacts(results)
        return {
            "results": [result.to_dict() for result in results],
            "count": len(results),
        }
