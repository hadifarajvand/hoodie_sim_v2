from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from dataclasses import asdict, dataclass, field
from pathlib import Path
from statistics import mean, pstdev
from typing import Any, Iterable

import numpy as np


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True))


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _config_hash(payload: dict[str, Any]) -> str:
    text = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _finite_mean(values: list[float]) -> float | None:
    vals = [float(v) for v in values if v is not None and np.isfinite(v)]
    if not vals:
        return None
    return float(mean(vals))


def _finite_std(values: list[float]) -> float | None:
    vals = [float(v) for v in values if v is not None and np.isfinite(v)]
    if len(vals) < 2:
        return 0.0 if vals else None
    return float(pstdev(vals))


def _ci95(values: list[float]) -> tuple[float | None, float | None]:
    vals = [float(v) for v in values if v is not None and np.isfinite(v)]
    if not vals:
        return None, None
    mu = float(mean(vals))
    if len(vals) == 1:
        return mu, mu
    std = float(pstdev(vals))
    half_width = 1.96 * std / math.sqrt(len(vals))
    return float(mu - half_width), float(mu + half_width)


@dataclass(frozen=True)
class BaselineScenario:
    scenario_id: str
    description: str
    num_edge_nodes: int
    arrival_slots: int
    drain_slots: int
    task_size_range: tuple[int, int]
    deadline_range: tuple[int, int]
    edge_cpu_capacities: tuple[float, ...]
    cloud_cpu_capacity: float
    arrival_rate_schedule: dict[str, Any]
    queue_order: tuple[int, ...] = field(default_factory=tuple)

    @property
    def total_slots(self) -> int:
        return self.arrival_slots + self.drain_slots

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def scenario_catalog() -> dict[str, BaselineScenario]:
    edge_nodes = 2
    return {
        "low": BaselineScenario(
            scenario_id="low",
            description="low load, light contention, deterministic baseline measurement",
            num_edge_nodes=edge_nodes,
            arrival_slots=100,
            drain_slots=10,
            task_size_range=(1, 3),
            deadline_range=(8, 14),
            edge_cpu_capacities=(2.0, 2.0),
            cloud_cpu_capacity=4.0,
            arrival_rate_schedule={"type": "constant", "rate": 0.25},
            queue_order=(0, 1, 2),
        ),
        "medium": BaselineScenario(
            scenario_id="medium",
            description="medium load baseline measurement",
            num_edge_nodes=edge_nodes,
            arrival_slots=100,
            drain_slots=10,
            task_size_range=(2, 5),
            deadline_range=(8, 16),
            edge_cpu_capacities=(2.0, 2.0),
            cloud_cpu_capacity=4.0,
            arrival_rate_schedule={"type": "constant", "rate": 0.6},
            queue_order=(0, 1, 2),
        ),
        "high": BaselineScenario(
            scenario_id="high",
            description="high congestion baseline measurement",
            num_edge_nodes=edge_nodes,
            arrival_slots=100,
            drain_slots=10,
            task_size_range=(3, 6),
            deadline_range=(6, 12),
            edge_cpu_capacities=(1.5, 1.5),
            cloud_cpu_capacity=3.0,
            arrival_rate_schedule={"type": "constant", "rate": 1.0},
            queue_order=(0, 1, 2),
        ),
        "burst": BaselineScenario(
            scenario_id="burst",
            description="burst arrival baseline measurement",
            num_edge_nodes=edge_nodes,
            arrival_slots=100,
            drain_slots=10,
            task_size_range=(2, 6),
            deadline_range=(8, 14),
            edge_cpu_capacities=(2.0, 2.0),
            cloud_cpu_capacity=4.0,
            arrival_rate_schedule={
                "type": "burst",
                "baseline_rate": 0.2,
                "burst_rate": 1.4,
                "burst_start": 35,
                "burst_end": 60,
            },
            queue_order=(0, 1, 2),
        ),
    }


@dataclass
class BaselineTask:
    task_id: int
    source_node: int
    arrival_time: int
    deadline: int
    size: float
    assigned_node: int
    policy_name: str
    selected_action: str
    queue_snapshot: dict[str, Any]
    start_time: int | None = None
    finish_time: int | None = None
    drop_time: int | None = None
    violation_flag: bool = False
    dropped: bool = False
    remaining_work: float = 0.0
    waiting_time: float | None = None
    service_time: float | None = None
    latency: float | None = None
    reward_proxy: float | None = None

    def to_lifecycle_row(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "arrival_time": self.arrival_time,
            "start_time": self.start_time if self.start_time is not None else "",
            "finish_time": self.finish_time if self.finish_time is not None else "",
            "assigned_node": self.assigned_node,
            "offloading_decision": self.selected_action,
            "deadline": self.deadline,
            "violation_flag": bool(self.violation_flag),
            "drop_time": self.drop_time if self.drop_time is not None else "",
            "drop_reason": "deadline_violation" if self.dropped else "",
            "task_size": self.size,
            "source_node": self.source_node,
            "policy_name": self.policy_name,
            "waiting_time": self.waiting_time if self.waiting_time is not None else "",
            "service_time": self.service_time if self.service_time is not None else "",
            "latency": self.latency if self.latency is not None else "",
            "reward_proxy": self.reward_proxy if self.reward_proxy is not None else "",
        }


class FrozenPolicy:
    name: str = "base"

    def choose(self, *, task: BaselineTask, state: dict[str, Any], rng: np.random.Generator, scenario: BaselineScenario) -> int:
        raise NotImplementedError


class FIFOQueueBaselinePolicy(FrozenPolicy):
    name = "FIFO"

    def choose(self, *, task: BaselineTask, state: dict[str, Any], rng: np.random.Generator, scenario: BaselineScenario) -> int:
        queue_order = list(scenario.queue_order) or list(range(scenario.num_edge_nodes + 1))
        return int(queue_order[0])


class RandomOffloadingBaselinePolicy(FrozenPolicy):
    name = "RO"

    def choose(self, *, task: BaselineTask, state: dict[str, Any], rng: np.random.Generator, scenario: BaselineScenario) -> int:
        queue_order = list(scenario.queue_order) or list(range(scenario.num_edge_nodes + 1))
        return int(queue_order[int(rng.integers(0, len(queue_order)))])


class GreedyLatencyBaselinePolicy(FrozenPolicy):
    name = "GreedyLatency"

    def choose(self, *, task: BaselineTask, state: dict[str, Any], rng: np.random.Generator, scenario: BaselineScenario) -> int:
        best_node = 0
        best_latency = None
        for node_id in range(scenario.num_edge_nodes + 1):
            queue_work = float(state["queue_work"].get(node_id, 0.0))
            capacity = float(state["capacities"].get(node_id, 1.0))
            estimated_latency = queue_work / max(capacity, 1e-9) + task.size / max(capacity, 1e-9)
            if best_latency is None or estimated_latency < best_latency or (math.isclose(estimated_latency, best_latency) and node_id < best_node):
                best_latency = estimated_latency
                best_node = node_id
        return int(best_node)


POLICY_REGISTRY: dict[str, type[FrozenPolicy]] = {
    "FIFO": FIFOQueueBaselinePolicy,
    "RO": RandomOffloadingBaselinePolicy,
    "GreedyLatency": GreedyLatencyBaselinePolicy,
}


def _arrival_rate_for_time(scenario: BaselineScenario, time: int) -> float:
    schedule = scenario.arrival_rate_schedule
    if schedule["type"] == "constant":
        return float(schedule["rate"])
    if schedule["type"] == "burst":
        if int(schedule["burst_start"]) <= time < int(schedule["burst_end"]):
            return float(schedule["burst_rate"])
        return float(schedule["baseline_rate"])
    raise ValueError(f"unsupported arrival schedule {schedule['type']!r}")


class BaselineExecutionEngine:
    def __init__(self, scenario: BaselineScenario, policy: FrozenPolicy, seed: int) -> None:
        self.scenario = scenario
        self.policy = policy
        self.seed = int(seed)
        self.rng = np.random.default_rng(seed)
        self.task_counter = 0
        self.queue_work = {node_id: 0.0 for node_id in range(scenario.num_edge_nodes + 1)}
        self.capacities = {node_id: float(cap) for node_id, cap in enumerate(scenario.edge_cpu_capacities)}
        self.capacities[scenario.num_edge_nodes] = float(scenario.cloud_cpu_capacity)
        self.queues: dict[int, list[BaselineTask]] = {node_id: [] for node_id in range(scenario.num_edge_nodes + 1)}
        self.lifecycle_rows: list[dict[str, Any]] = []
        self.action_rows: list[dict[str, Any]] = []
        self.metrics_rows: list[dict[str, Any]] = []
        self.trace_integrity = "PASSED"
        self.integrity_warnings: list[str] = []
        self.total_processed_work = 0.0
        self.total_capacity_work = 0.0

    def _make_task(self, source_node: int, time: int) -> BaselineTask:
        self.task_counter += 1
        size = float(self.rng.integers(self.scenario.task_size_range[0], self.scenario.task_size_range[1] + 1))
        deadline = int(self.rng.integers(self.scenario.deadline_range[0], self.scenario.deadline_range[1] + 1)) + time
        task = BaselineTask(
            task_id=self.task_counter,
            source_node=source_node,
            arrival_time=time,
            deadline=deadline,
            size=size,
            assigned_node=source_node,
            policy_name=self.policy.name,
            selected_action="local",
            queue_snapshot={},
            remaining_work=size,
        )
        return task

    def _legal_actions(self) -> list[int]:
        return list(range(self.scenario.num_edge_nodes + 1))

    def _policy_state(self) -> dict[str, Any]:
        return {
            "queue_work": dict(self.queue_work),
            "capacities": dict(self.capacities),
        }

    def _enqueue_task(self, task: BaselineTask, assigned_node: int) -> None:
        task.assigned_node = int(assigned_node)
        task.selected_action = ["local", *[f"edge_{node}" for node in range(self.scenario.num_edge_nodes)], "cloud"][assigned_node]
        task.queue_snapshot = {
            "queue_work": dict(self.queue_work),
            "queue_lengths": {node_id: len(queue) for node_id, queue in self.queues.items()},
        }
        self.queues[assigned_node].append(task)
        self.queue_work[assigned_node] += task.size
        self.action_rows.append(
            {
                "timestamp": task.arrival_time,
                "task_id": task.task_id,
                "policy_decision": self.policy.name,
                "selected_action": assigned_node,
                "queue_state_snapshot_json": json.dumps(task.queue_snapshot, sort_keys=True),
                "seed": self.seed,
                "scenario_id": self.scenario.scenario_id,
            }
        )
        self.lifecycle_rows.append(
            {
                "task_id": task.task_id,
                "arrival_time": task.arrival_time,
                "start_time": "",
                "finish_time": "",
                "assigned_node": task.assigned_node,
                "offloading_decision": task.selected_action,
                "deadline": task.deadline,
                "violation_flag": False,
                "drop_time": "",
                "drop_reason": "",
                "task_size": task.size,
                "source_node": task.source_node,
                "policy_name": task.policy_name,
                "waiting_time": "",
                "service_time": "",
                "latency": "",
                "reward_proxy": "",
            }
        )

    def _drop_expired_tasks(self, current_time: int) -> None:
        for node_id, queue in self.queues.items():
            while queue and queue[0].deadline < current_time:
                task = queue.pop(0)
                self.queue_work[node_id] -= task.size
                task.dropped = True
                task.violation_flag = True
                task.drop_time = current_time
                task.finish_time = current_time
                task.waiting_time = max(0.0, (task.start_time or current_time) - task.arrival_time) if task.start_time is not None else float(current_time - task.arrival_time)
                task.service_time = 0.0 if task.start_time is None else max(0.0, task.finish_time - task.start_time + 1)
                task.latency = max(0.0, task.finish_time - task.arrival_time + 1)
                task.reward_proxy = -float(task.size)
                self.lifecycle_rows.append(task.to_lifecycle_row())

    def _process_node(self, node_id: int, current_time: int) -> None:
        queue = self.queues[node_id]
        if not queue:
            return
        capacity = float(self.capacities[node_id])
        self.total_capacity_work += capacity
        task = queue[0]
        if task.start_time is None:
            task.start_time = current_time
        processed = min(capacity, task.remaining_work)
        self.total_processed_work += processed
        task.remaining_work -= processed
        if task.remaining_work <= 1e-9:
            task.finish_time = current_time
            task.waiting_time = float(task.start_time - task.arrival_time)
            task.service_time = float(task.finish_time - task.start_time + 1)
            task.latency = float(task.finish_time - task.arrival_time + 1)
            task.reward_proxy = -float(task.latency)
            task.violation_flag = bool(task.finish_time > task.deadline)
            queue.pop(0)
            self.queue_work[node_id] -= task.size
            self.lifecycle_rows.append(task.to_lifecycle_row())

    def run(self) -> dict[str, Any]:
        total_slots = self.scenario.total_slots
        for current_time in range(total_slots):
            arrival_rate = _arrival_rate_for_time(self.scenario, current_time)
            self._drop_expired_tasks(current_time)
            for source_node in range(self.scenario.num_edge_nodes):
                arrivals = int(self.rng.poisson(arrival_rate))
                for _ in range(arrivals):
                    task = self._make_task(source_node, current_time)
                    assigned_node = self.policy.choose(task=task, state=self._policy_state(), rng=self.rng, scenario=self.scenario)
                    self._enqueue_task(task, assigned_node)
            for node_id in range(self.scenario.num_edge_nodes + 1):
                self._process_node(node_id, current_time)

        # drain
        drain_guard = 0
        while any(self.queues.values()) and drain_guard < max(10, self.scenario.total_slots):
            current_time = total_slots + drain_guard
            self._drop_expired_tasks(current_time)
            for node_id in range(self.scenario.num_edge_nodes + 1):
                self._process_node(node_id, current_time)
            drain_guard += 1

        for node_id, queue in self.queues.items():
            for task in queue:
                self.integrity_warnings.append(f"orphan task remained in node {node_id}: task_id={task.task_id}")
                self.trace_integrity = "DEGRADED"
        if any(row.get("finish_time") in ("", None) for row in self.lifecycle_rows if row.get("drop_time") in ("", None)):
            self.trace_integrity = "DEGRADED"

        completed = [row for row in self.lifecycle_rows if str(row.get("drop_reason") or "") == "" and row.get("finish_time") not in ("", None)]
        dropped = [row for row in self.lifecycle_rows if str(row.get("drop_reason") or "") != ""]
        pending = [row for row in self.lifecycle_rows if row.get("finish_time") in ("", None) and row.get("drop_reason") in ("", None)]
        latencies = [_coerce_float(row.get("latency")) for row in completed]
        waiting_times = [_coerce_float(row.get("waiting_time")) for row in completed]
        service_times = [_coerce_float(row.get("service_time")) for row in completed]
        reward_proxy = [_coerce_float(row.get("reward_proxy")) for row in self.lifecycle_rows]
        total_latency = float(sum(v for v in latencies if v is not None)) if latencies else 0.0
        avg_latency = _finite_mean([v for v in latencies if v is not None])
        violation_rate = float(len([row for row in self.lifecycle_rows if row.get("violation_flag")]) / len(self.lifecycle_rows)) if self.lifecycle_rows else 0.0
        drop_rate = float(len(dropped) / len(self.lifecycle_rows)) if self.lifecycle_rows else 0.0
        system_utilization = float(self.total_processed_work / self.total_capacity_work) if self.total_capacity_work > 0 else 0.0
        episode_row = {
            "episode_id": 0,
            "scenario_id": self.scenario.scenario_id,
            "policy_name": self.policy.name,
            "seed": self.seed,
            "total_tasks": len(self.lifecycle_rows),
            "completed_tasks": len(completed),
            "dropped_tasks": len(dropped),
            "pending_tasks": len(pending),
            "total_latency": total_latency,
            "avg_latency": avg_latency if avg_latency is not None else "",
            "deadline_violation_rate": violation_rate,
            "drop_rate": drop_rate,
            "system_utilization": system_utilization,
            "reward_proxy": float(sum(v for v in reward_proxy if v is not None)),
            "mean_queue_length": float(mean([len(row) for row in self.lifecycle_rows])) if self.lifecycle_rows else 0.0,
        }
        self.metrics_rows.append(episode_row)
        return {
            "episode_metrics_row": episode_row,
            "total_tasks": len(self.lifecycle_rows),
            "completed_tasks": len(completed),
            "dropped_tasks": len(dropped),
            "pending_tasks": len(pending),
            "total_latency": total_latency,
            "avg_latency": avg_latency,
            "deadline_violation_rate": violation_rate,
            "drop_rate": drop_rate,
            "system_utilization": system_utilization,
            "reward_proxy": episode_row["reward_proxy"],
            "trace_integrity": self.trace_integrity,
            "integrity_warnings": self.integrity_warnings,
            "lifecycle_rows": self.lifecycle_rows,
            "action_rows": self.action_rows,
            "episode_rows": self.metrics_rows,
        }


def _coerce_float(value: Any) -> float | None:
    if value in (None, "", "None"):
        return None
    try:
        return float(value)
    except Exception:
        return None


def _aggregate_metrics(seed_reports: list[dict[str, Any]]) -> dict[str, Any]:
    metric_keys = [
        "total_latency",
        "avg_latency",
        "deadline_violation_rate",
        "drop_rate",
        "system_utilization",
        "reward_proxy",
    ]
    aggregates: dict[str, Any] = {}
    for key in metric_keys:
        values = [report["computed_metrics"].get(key) for report in seed_reports]
        values = [float(v) for v in values if v is not None]
        ci_low, ci_high = _ci95(values)
        aggregates[key] = {
            "mean": _finite_mean(values),
            "std": _finite_std(values),
            "ci95_low": ci_low,
            "ci95_high": ci_high,
            "count": len(values),
        }
    return aggregates


def _policy_instance(policy_name: str) -> FrozenPolicy:
    if policy_name not in POLICY_REGISTRY:
        raise ValueError(f"unsupported baseline policy {policy_name!r}")
    return POLICY_REGISTRY[policy_name]()


def run_baseline_seed(
    *,
    scenario: BaselineScenario,
    policy_name: str,
    seed: int,
    output_dir: str | Path,
) -> dict[str, Any]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    policy = _policy_instance(policy_name)
    engine = BaselineExecutionEngine(scenario, policy, seed)
    run_result = engine.run()
    lifecycle_path = output_dir / "task_lifecycle.csv"
    action_path = output_dir / "action_trace.csv"
    metrics_path = output_dir / "episode_metrics.csv"
    _write_csv(lifecycle_path, run_result["lifecycle_rows"] or [BaselineTask(0, 0, 0, 0, 0.0, 0, policy.name, "local", {}, 0, 0).to_lifecycle_row()])
    _write_csv(action_path, run_result["action_rows"] or [{
        "timestamp": 0,
        "task_id": 0,
        "policy_decision": policy.name,
        "selected_action": 0,
        "queue_state_snapshot_json": "{}",
        "seed": seed,
        "scenario_id": scenario.scenario_id,
    }])
    _write_csv(metrics_path, run_result["episode_rows"])
    config_payload = {
        "scenario": scenario.to_dict(),
        "policy_name": policy.name,
        "seed": seed,
    }
    config_hash = _config_hash(config_payload)
    report = {
        "model": "Model 15 — Controlled Baseline Evaluation Run Contract",
        "status": "passed" if run_result["trace_integrity"] == "PASSED" else "degraded",
        "trace_integrity": run_result["trace_integrity"],
        "scenario": scenario.to_dict(),
        "policy": {"name": policy.name, "class": policy.__class__.__name__},
        "seed": seed,
        "config_hash": config_hash,
        "computed_metrics": {
            "total_tasks": run_result["total_tasks"],
            "completed_tasks": run_result["completed_tasks"],
            "dropped_tasks": run_result["dropped_tasks"],
            "pending_tasks": run_result["pending_tasks"],
            "total_latency": run_result["total_latency"],
            "avg_latency": run_result["avg_latency"],
            "deadline_violation_rate": run_result["deadline_violation_rate"],
            "drop_rate": run_result["drop_rate"],
            "system_utilization": run_result["system_utilization"],
            "reward_proxy": run_result["reward_proxy"],
        },
        "validation_status": "passed" if run_result["trace_integrity"] == "PASSED" else "degraded",
        "validation_warnings": run_result["integrity_warnings"],
        "output_files": {
            "task_lifecycle.csv": str(lifecycle_path),
            "action_trace.csv": str(action_path),
            "episode_metrics.csv": str(metrics_path),
        },
        "scenario_metadata": scenario.to_dict(),
        "policy_metadata": {"name": policy.name, "class": policy.__class__.__name__},
        "reward_proxy_definition": "negative latency for completed tasks; negative task size for dropped tasks",
        "scientific_role": "evaluation_only",
        "paper_claims_made": False,
        "no_training": True,
        "no_learning_updates": True,
    }
    _write_json(output_dir / "baseline_evaluation_report.json", report)
    return report


def run_baseline_evaluation(
    output_dir: str | Path,
    *,
    scenario_ids: Iterable[str] | None = None,
    policy_names: Iterable[str] | None = None,
    seeds: Iterable[int] | None = None,
) -> dict[str, Any]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    scenarios = scenario_catalog()
    selected_scenarios = [scenarios[name] for name in (scenario_ids or scenarios.keys())]
    selected_policies = list(policy_names or POLICY_REGISTRY.keys())
    selected_seeds = list(seeds or range(10))
    manifests: list[dict[str, Any]] = []
    for scenario in selected_scenarios:
        scenario_dir = output_dir / scenario.scenario_id
        for policy_name in selected_policies:
            policy_dir = scenario_dir / policy_name
            seed_reports: list[dict[str, Any]] = []
            for seed in selected_seeds:
                seed_dir = policy_dir / f"seed_{seed}"
                report = run_baseline_seed(scenario=scenario, policy_name=policy_name, seed=seed, output_dir=seed_dir)
                seed_reports.append(report)
            summary = {
                "model": "Model 15 — Controlled Baseline Evaluation Run Contract",
                "scenario": scenario.to_dict(),
                "policy": {"name": policy_name, "class": _policy_instance(policy_name).__class__.__name__},
                "seed_count": len(seed_reports),
            "seed_reports": [str(policy_dir / f"seed_{seed}" / "baseline_evaluation_report.json") for seed in selected_seeds],
            "aggregated_metrics": _aggregate_metrics(seed_reports),
            "seed_reports_metrics": [report["computed_metrics"] for report in seed_reports],
                "paper_claims_made": False,
                "no_training": True,
                "no_learning_updates": True,
            }
            _write_json(policy_dir / "baseline_evaluation_summary.json", summary)
            manifests.append(summary)
    root_summary = {
        "model": "Model 15 — Controlled Baseline Evaluation Run Contract",
        "status": "passed",
        "scenario_count": len(selected_scenarios),
        "policy_count": len(selected_policies),
        "seed_count": len(selected_seeds),
        "scenarios": [scenario.scenario_id for scenario in selected_scenarios],
        "policies": selected_policies,
        "paper_claims_made": False,
        "no_training": True,
        "no_learning_updates": True,
        "baseline_runs": manifests,
    }
    _write_json(output_dir / "baseline_evaluation_root_summary.json", root_summary)
    return root_summary


def _parse_list_arg(value: str | None) -> list[str] | None:
    if value in (None, "", "all"):
        return None
    return [item.strip() for item in value.split(",") if item.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description="Controlled baseline evaluation runner")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--scenarios", default="low,medium,high,burst")
    parser.add_argument("--policies", default="FIFO,RO,GreedyLatency")
    parser.add_argument("--seed-start", type=int, default=0)
    parser.add_argument("--seed-count", type=int, default=10)
    args = parser.parse_args()
    seeds = list(range(args.seed_start, args.seed_start + args.seed_count))
    run_baseline_evaluation(
        args.output_dir,
        scenario_ids=_parse_list_arg(args.scenarios),
        policy_names=_parse_list_arg(args.policies),
        seeds=seeds,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
