from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import numpy as np


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


@dataclass(frozen=True)
class PipelineConfig:
    run_id: str
    seed: int
    mode: str = "paper_faithful"
    phase: int = 5
    num_edge_nodes: int = 3
    horizon: int = 110
    arrival_probability: float = 0.5
    task_count: int = 120
    task_size_range: tuple[int, int] = (1, 4)
    processing_density_range: tuple[float, float] = (1.0, 2.0)
    edge_capacity: float = 1.0
    cloud_capacity: float = 2.0
    queue_threshold: int = 2
    topography: list[list[int]] = field(default_factory=list)
    smoke_only: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Task:
    task_id: int
    source_node: int
    arrival_time: int
    size: int
    density: float
    deadline: int | None = None
    decision_reason: str = "local"
    assigned_node: int | None = None
    enqueue_time: int | None = None
    start_time: int | None = None
    finish_time: int | None = None
    waiting_time: float | None = None
    service_time: float | None = None
    latency: float | None = None
    dropped: bool = False


@dataclass(frozen=True)
class Event:
    timestamp: int
    sequence_id: int
    task_id: int
    node_id: int
    event_type: str
    queue_snapshot: dict[str, Any]
    cpu_state_snapshot: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Node:
    node_id: int
    cpu_capacity: float
    queue: list[Task] = field(default_factory=list)
    active: Task | None = None
    remaining_work: float = 0.0
    busy_time: int = 0
    completed: int = 0

    def snapshot(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "queue_length": len(self.queue),
            "active_task_id": None if self.active is None else self.active.task_id,
            "busy": self.active is not None,
        }


class DeterministicSimulator:
    def __init__(self, config: PipelineConfig) -> None:
        self.config = config
        self.rng = np.random.default_rng(int(config.seed))
        self.nodes = [Node(i, float(config.edge_capacity)) for i in range(config.num_edge_nodes)]
        self.cloud = Node(config.num_edge_nodes, float(config.cloud_capacity))
        self.events: list[Event] = []
        self._seq = 0
        self.tasks: dict[int, Task] = {}
        self.trace: list[dict[str, Any]] = []
        self.metrics: dict[str, Any] = {}
        self.topology = self._build_topology(config.num_edge_nodes, config.topography)

    def _build_topology(self, n: int, topo: list[list[int]]) -> dict[int, list[int]]:
        if topo:
            return {i: [j for j, v in enumerate(row) if v and j != i] for i, row in enumerate(topo[:n])}
        return {i: [((i - 1) % n), ((i + 1) % n)] if n > 1 else [] for i in range(n)}

    def _next_seq(self) -> int:
        self._seq += 1
        return self._seq

    def _queue_snapshot(self, node: Node) -> dict[str, Any]:
        return {"node_id": node.node_id, "queue_length": len(node.queue), "active_task_id": None if node.active is None else node.active.task_id}

    def _cpu_snapshot(self) -> dict[str, Any]:
        return {
            node.node_id: {"busy": int(node.active is not None), "capacity": node.cpu_capacity}
            for node in self.nodes + [self.cloud]
        }

    def _log(self, time: int, task: Task, node: Node, event_type: str, metadata: dict[str, Any] | None = None) -> None:
        self.events.append(
            Event(
                timestamp=time,
                sequence_id=self._next_seq(),
                task_id=task.task_id,
                node_id=node.node_id,
                event_type=event_type,
                queue_snapshot=self._queue_snapshot(node),
                cpu_state_snapshot=self._cpu_snapshot(),
                metadata=metadata or {},
            )
        )

    def _sample_task(self, time: int, source_node: int) -> Task:
        size = int(self.rng.integers(self.config.task_size_range[0], self.config.task_size_range[1] + 1))
        density = float(self.rng.uniform(self.config.processing_density_range[0], self.config.processing_density_range[1]))
        return Task(task_id=len(self.tasks) + 1, source_node=source_node, arrival_time=time, size=size, density=density)

    def _choose_destination(self, task: Task) -> tuple[int, str]:
        if self.config.phase <= 0:
            return task.source_node, "local_only"
        if self.config.phase == 1:
            if self.rng.random() < 0.5:
                return task.source_node, "random_local"
            return self._neighbors(task.source_node)[0], "random_neighbor"
        local = self.nodes[task.source_node]
        neighbor_ids = self._neighbors(task.source_node)
        neighbor_lengths = [(nid, len(self.nodes[nid].queue) + (1 if self.nodes[nid].active else 0)) for nid in neighbor_ids]
        cloud_length = len(self.cloud.queue) + (1 if self.cloud.active else 0)
        if len(local.queue) > self.config.queue_threshold:
            return self.cloud.node_id, "offload_cloud"
        if neighbor_lengths:
            best_neighbor, best_len = min(neighbor_lengths, key=lambda item: (item[1], item[0]))
            if best_len < len(local.queue):
                return best_neighbor, "horizontal_offload"
        return task.source_node, "local_execute"

    def _neighbors(self, node_id: int) -> list[int]:
        return list(self.topology.get(int(node_id), []))

    def _service_time(self, task: Task, capacity: float) -> float:
        return float(math.ceil(task.size * task.density / max(capacity, 1e-9)))

    def _enqueue(self, node: Node, task: Task, time: int) -> None:
        task.assigned_node = node.node_id
        task.enqueue_time = time
        node.queue.append(task)

    def _maybe_start(self, node: Node, time: int) -> None:
        if node.active is not None or not node.queue:
            return
        task = node.queue.pop(0)
        task.start_time = time
        task.waiting_time = float(time - task.arrival_time)
        node.active = task
        node.remaining_work = self._service_time(task, node.cpu_capacity)
        self._log(time, task, node, "TASK_START")

    def _step_node(self, node: Node, time: int) -> list[Task]:
        finished: list[Task] = []
        self._maybe_start(node, time)
        if node.active is None:
            return finished
        node.busy_time += 1
        node.remaining_work -= node.cpu_capacity
        if node.remaining_work <= 0:
            task = node.active
            task.finish_time = time
            task.service_time = float(task.finish_time - task.start_time + 1)
            task.latency = float(task.finish_time - task.arrival_time + 1)
            finished.append(task)
            node.completed += 1
            self._log(time, task, node, "TASK_FINISH")
            node.active = None
            node.remaining_work = 0.0
        return finished

    def run(self) -> dict[str, Any]:
        for time in range(self.config.horizon):
            arrivals = 0
            if self.config.mode == "paper_faithful":
                arrivals = int(self.rng.random() < self.config.arrival_probability) * self.config.num_edge_nodes
            else:
                arrivals = int(round(self.config.arrival_probability * self.config.num_edge_nodes))
            for source in range(self.config.num_edge_nodes):
                if self.config.mode == "paper_faithful" and self.rng.random() >= self.config.arrival_probability:
                    continue
                if self.config.phase == 0 and time >= self.config.task_count:
                    continue
                task = self._sample_task(time, source)
                self.tasks[task.task_id] = task
                self._log(time, task, self.nodes[source], "TASK_ARRIVAL")
                dest_id, reason = self._choose_destination(task)
                task.decision_reason = reason
                dest_node = self.cloud if dest_id == self.cloud.node_id else self.nodes[dest_id]
                self._log(time, task, dest_node, "TASK_ENQUEUE", {"reason": reason, "destination": dest_id})
                self._enqueue(dest_node, task, time)
            for node in self.nodes + [self.cloud]:
                self._step_node(node, time)
            self.trace.append(
                {
                    "time": time,
                    "queue_lengths": {node.node_id: len(node.queue) + (1 if node.active else 0) for node in self.nodes + [self.cloud]},
                    "utilization": {node.node_id: float(node.busy_time / max(1, time + 1)) for node in self.nodes + [self.cloud]},
                }
            )
        # drain
        drain_time = self.config.horizon
        while any(node.queue or node.active for node in self.nodes + [self.cloud]):
            for node in self.nodes + [self.cloud]:
                self._step_node(node, drain_time)
            drain_time += 1

        self.metrics = self._build_metrics()
        return {
            "config": self.config.to_dict(),
            "event_hash": self.event_hash(),
            "events": [e.to_dict() for e in self.events],
            "metrics": self.metrics,
            "trace": self.trace,
        }

    def _build_metrics(self) -> dict[str, Any]:
        latencies = [t.latency for t in self.tasks.values() if t.latency is not None]
        waiting = [t.waiting_time for t in self.tasks.values() if t.waiting_time is not None]
        service = [t.service_time for t in self.tasks.values() if t.service_time is not None]
        offload_counts = {"local": 0, "neighbor": 0, "cloud": 0}
        for task in self.tasks.values():
            if task.decision_reason == "horizontal_offload":
                offload_counts["neighbor"] += 1
            elif task.decision_reason == "offload_cloud":
                offload_counts["cloud"] += 1
            else:
                offload_counts["local"] += 1
        return {
            "average_latency": float(np.mean(latencies)) if latencies else None,
            "average_waiting_time": float(np.mean(waiting)) if waiting else None,
            "average_service_time": float(np.mean(service)) if service else None,
            "queue_length_over_time": self.trace,
            "utilization": {
                node.node_id: float(node.busy_time / max(1, self.config.horizon))
                for node in self.nodes + [self.cloud]
            },
            "offloading_breakdown": offload_counts,
        }

    def event_hash(self) -> str:
        payload = json.dumps([e.to_dict() for e in self.events], sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ExperimentScenario:
    name: str
    arrival_probability: float
    seed_start: int
    seed_count: int
    config_overrides: dict[str, Any] = field(default_factory=dict)


def _mean(values: list[float]) -> float | None:
    return float(statistics.mean(values)) if values else None


def _variance(values: list[float]) -> float | None:
    return float(statistics.pvariance(values)) if values else None


def _stddev(values: list[float]) -> float | None:
    return float(statistics.pstdev(values)) if values else None


def _confidence_interval_95(values: list[float]) -> tuple[float | None, float | None]:
    if not values:
        return None, None
    mu = float(statistics.mean(values))
    if len(values) == 1:
        return mu, mu
    sd = float(statistics.stdev(values))
    half = 1.96 * sd / math.sqrt(len(values))
    return float(mu - half), float(mu + half)


def _copy_config(base: PipelineConfig, **overrides: Any) -> PipelineConfig:
    payload = base.to_dict()
    payload.update(overrides)
    return PipelineConfig(**payload)


def _baseline_config(base: PipelineConfig, policy: str) -> PipelineConfig:
    mode = "paper_faithful"
    cfg = _copy_config(base, mode=mode)
    return cfg


def _policy_transform(result: dict[str, Any], policy: str) -> dict[str, Any]:
    transformed = json.loads(json.dumps(result))
    if policy == "fifo_only":
        for task in transformed.get("events", []):
            if task["event_type"] == "TASK_ENQUEUE":
                task["metadata"]["reason"] = "fifo_only_local"
    return transformed


def run_single_experiment(config: PipelineConfig, policy: str) -> dict[str, Any]:
    simulator = DeterministicSimulator(config)
    result = simulator.run()
    workload_signature = hashlib.sha256(
        json.dumps(
            {
                "seed": config.seed,
                "arrival_probability": config.arrival_probability,
                "task_size_range": config.task_size_range,
                "processing_density_range": config.processing_density_range,
                "num_edge_nodes": config.num_edge_nodes,
                "horizon": config.horizon,
            },
            sort_keys=True,
            default=str,
        ).encode("utf-8")
    ).hexdigest()
    resource_signature = hashlib.sha256(
        json.dumps(
            {
                "num_edge_nodes": config.num_edge_nodes,
                "edge_capacity": config.edge_capacity,
                "cloud_capacity": config.cloud_capacity,
                "queue_threshold": config.queue_threshold,
                "topography": config.topography,
            },
            sort_keys=True,
            default=str,
        ).encode("utf-8")
    ).hexdigest()
    result["policy"] = policy
    result["seed"] = config.seed
    result["scenario"] = config.run_id
    result["config_hash"] = hashlib.sha256(json.dumps(config.to_dict(), sort_keys=True, default=str).encode("utf-8")).hexdigest()
    result["workload_signature"] = workload_signature
    result["resource_signature"] = resource_signature
    return _policy_transform(result, policy)


def build_scenarios(base: PipelineConfig, seed_count: int = 20) -> list[ExperimentScenario]:
    return [
        ExperimentScenario("low", 0.2, base.seed, seed_count, {"phase": 5}),
        ExperimentScenario("medium", 0.5, base.seed + 1000, seed_count, {"phase": 5}),
        ExperimentScenario("high", 0.8, base.seed + 2000, seed_count, {"phase": 5}),
    ]


def summarize_numeric(values: list[float]) -> dict[str, float | None]:
    return {
        "mean": _mean(values),
        "variance": _variance(values),
        "stddev": _stddev(values),
    }


def aggregate_results(rows: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        key = (row["scenario"], row["policy"])
        grouped.setdefault(key, []).append(row)

    summary_rows: list[dict[str, Any]] = []
    for (scenario, policy), values in sorted(grouped.items()):
        latencies = [float(v["metrics"]["average_latency"]) for v in values if v["metrics"]["average_latency"] is not None]
        waits = [float(v["metrics"]["average_waiting_time"]) for v in values if v["metrics"]["average_waiting_time"] is not None]
        services = [float(v["metrics"]["average_service_time"]) for v in values if v["metrics"]["average_service_time"] is not None]
        local_ratio = [float(v["metrics"]["offloading_breakdown"]["local"]) / max(1, sum(v["metrics"]["offloading_breakdown"].values())) for v in values]
        neighbor_ratio = [float(v["metrics"]["offloading_breakdown"]["neighbor"]) / max(1, sum(v["metrics"]["offloading_breakdown"].values())) for v in values]
        cloud_ratio = [float(v["metrics"]["offloading_breakdown"]["cloud"]) / max(1, sum(v["metrics"]["offloading_breakdown"].values())) for v in values]
        util_means = [sum(v["metrics"]["utilization"].values()) / len(v["metrics"]["utilization"]) for v in values]
        summary_rows.append(
            {
                "scenario": scenario,
                "policy": policy,
                "runs": len(values),
                "latency_mean": _mean(latencies),
                "latency_variance": _variance(latencies),
                "latency_stddev": _stddev(latencies),
                "latency_ci95_low": _confidence_interval_95(latencies)[0],
                "latency_ci95_high": _confidence_interval_95(latencies)[1],
                "waiting_mean": _mean(waits),
                "waiting_variance": _variance(waits),
                "service_mean": _mean(services),
                "service_variance": _variance(services),
                "offloading_local_mean": _mean(local_ratio),
                "offloading_neighbor_mean": _mean(neighbor_ratio),
                "offloading_cloud_mean": _mean(cloud_ratio),
                "utilization_mean": _mean(util_means),
                "utilization_variance": _variance(util_means),
                "utilization_stddev": _stddev(util_means),
            }
        )
    return {
        "rows": summary_rows,
        "config_count": len({row["scenario"] for row in rows}),
        "run_count": len(rows),
    }


def generate_paper_tables(summary_rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    latency_rows = []
    offloading_rows = []
    utilization_rows = []
    for row in summary_rows:
        latency_rows.append(
            {
                "scenario": row["scenario"],
                "policy": row["policy"],
                "latency_mean": row["latency_mean"],
                "latency_stddev": row["latency_stddev"],
                "latency_ci95_low": row["latency_ci95_low"],
                "latency_ci95_high": row["latency_ci95_high"],
            }
        )
        offloading_rows.append(
            {
                "scenario": row["scenario"],
                "policy": row["policy"],
                "local_offloading": row["offloading_local_mean"],
                "neighbor_offloading": row["offloading_neighbor_mean"],
                "cloud_offloading": row["offloading_cloud_mean"],
            }
        )
        utilization_rows.append(
            {
                "scenario": row["scenario"],
                "policy": row["policy"],
                "utilization_mean": row["utilization_mean"],
                "utilization_stddev": row["utilization_stddev"],
            }
        )
    return {"latency": latency_rows, "offloading": offloading_rows, "utilization": utilization_rows}


def run_experiment_suite(base_config: PipelineConfig, output_dir: str | Path, runs_per_config: int = 20) -> dict[str, Any]:
    if runs_per_config < 20:
        raise ValueError("runs_per_config must be at least 20")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    scenarios = build_scenarios(base_config, seed_count=runs_per_config)
    policies = ["fifo_only", "random_routing", "heuristic_routing"]
    rows: list[dict[str, Any]] = []
    for scenario in scenarios:
        for policy in policies:
            for run_idx in range(runs_per_config):
                seed = scenario.seed_start + run_idx
                cfg = _copy_config(
                    base_config,
                    run_id=f"{scenario.name}_{policy}_{run_idx}",
                    seed=seed,
                    arrival_probability=scenario.arrival_probability,
                    **scenario.config_overrides,
                )
                if policy == "fifo_only":
                    cfg = _copy_config(cfg, phase=0)
                elif policy == "random_routing":
                    cfg = _copy_config(cfg, phase=1)
                else:
                    cfg = _copy_config(cfg, phase=2)
                result = run_single_experiment(cfg, policy)
                rows.append(
                    {
                        "scenario": scenario.name,
                        "policy": policy,
                        "run_index": run_idx,
                        "seed": seed,
                        "config_hash": result["config_hash"],
                        "workload_signature": result["workload_signature"],
                        "resource_signature": result["resource_signature"],
                        "event_hash": result["event_hash"],
                        "policy_label": policy,
                        "metrics": result["metrics"],
                    }
                )
    summary = aggregate_results(rows)
    tables = generate_paper_tables(summary["rows"])
    exp_dir = output_dir / "experiment_suite"
    exp_dir.mkdir(parents=True, exist_ok=True)
    (exp_dir / "raw_results.json").write_text(json.dumps(rows, indent=2, sort_keys=True))
    (exp_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True))
    for name, table_rows in tables.items():
        _write_csv(exp_dir / f"{name}_comparison_table.csv", table_rows)
        (exp_dir / f"{name}_comparison_table.json").write_text(json.dumps(table_rows, indent=2, sort_keys=True))
    try:
        from evaluation.evaluation_pipeline import run_evaluation_pipeline

        evaluation_report = run_evaluation_pipeline(exp_dir, exp_dir / "evaluation")
    except Exception as exc:
        evaluation_report = {"status": "failed", "error": str(exc)}
    (exp_dir / "final_experiment_report.json").write_text(json.dumps({"summary": summary, "evaluation": evaluation_report}, indent=2, sort_keys=True))
    return {"raw_results": rows, "summary": summary, "tables": tables, "evaluation": evaluation_report, "output_dir": str(exp_dir)}


def write_artifacts(output_dir: str | Path, result: dict[str, Any]) -> dict[str, str]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    trace_path = output_dir / "trace.json"
    metrics_path = output_dir / "metrics.json"
    state_path = output_dir / "state.json"
    config_path = output_dir / "config.json"
    trace_path.write_text(json.dumps({"event_hash": result["event_hash"], "events": result["events"]}, indent=2, sort_keys=True))
    metrics_path.write_text(json.dumps(result["metrics"], indent=2, sort_keys=True))
    state_path.write_text(json.dumps(result["trace"], indent=2, sort_keys=True))
    config_path.write_text(json.dumps(result["config"], indent=2, sort_keys=True))
    return {"trace": str(trace_path), "metrics": str(metrics_path), "state": str(state_path), "config": str(config_path)}


def write_plots(output_dir: str | Path, result: dict[str, Any]) -> dict[str, str]:
    output_dir = Path(output_dir)
    plot_dir = output_dir / "plots"
    plot_dir.mkdir(parents=True, exist_ok=True)
    trace = result["trace"]
    x = [row["time"] for row in trace]
    q = [sum(row["queue_lengths"].values()) for row in trace]
    u = [sum(row["utilization"].values()) / len(row["utilization"]) for row in trace]
    fig1 = plot_dir / "queue_evolution.svg"
    fig2 = plot_dir / "utilization.svg"
    fig3 = plot_dir / "offloading.svg"
    _write_svg_line(fig1, "Queue Evolution", x, q)
    _write_svg_line(fig2, "Utilization", x, u)
    labels = ["local", "neighbor", "cloud"]
    values = [result["metrics"]["offloading_breakdown"][k] for k in labels]
    _write_svg_bars(fig3, "Offloading Distribution", labels, values)
    return {"queue_evolution": str(fig1), "utilization": str(fig2), "offloading": str(fig3)}


def _write_svg_line(path: Path, title: str, xs: list[int], ys: list[float]) -> None:
    width, height, pad = 800, 400, 40
    min_y = min(ys) if ys else 0.0
    max_y = max(ys) if ys else 1.0
    if math.isclose(min_y, max_y):
        max_y = min_y + 1.0
    points = []
    for idx, (_, y) in enumerate(zip(xs, ys, strict=False)):
        px = pad + (width - 2 * pad) * (idx / max(1, len(xs) - 1))
        py = height - pad - (height - 2 * pad) * ((y - min_y) / (max_y - min_y))
        points.append(f"{px:.1f},{py:.1f}")
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{pad}" y="24" font-size="18" font-family="sans-serif">{title}</text>',
        f'<polyline fill="none" stroke="#1f77b4" stroke-width="2" points="{" ".join(points)}"/>',
        "</svg>",
    ]
    path.write_text("\n".join(svg))


def _write_svg_bars(path: Path, title: str, labels: list[str], values: list[float]) -> None:
    width, height, pad = 800, 400, 40
    max_v = max(values) if values else 1.0
    if math.isclose(max_v, 0.0):
        max_v = 1.0
    bar_w = (width - 2 * pad) / max(1, len(values))
    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{pad}" y="24" font-size="18" font-family="sans-serif">{title}</text>',
    ]
    for idx, (label, value) in enumerate(zip(labels, values, strict=False)):
        bar_h = (height - 2 * pad) * (value / max_v)
        x = pad + idx * bar_w + 10
        y = height - pad - bar_h
        elements.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w - 20:.1f}" height="{bar_h:.1f}" fill="#1f77b4"/>')
        elements.append(f'<text x="{x:.1f}" y="{height - 10}" font-size="14" font-family="sans-serif">{label}</text>')
    elements.append("</svg>")
    path.write_text("\n".join(elements))
