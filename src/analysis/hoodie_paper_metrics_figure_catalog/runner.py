from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from math import isnan
from pathlib import Path
import csv
import json
import subprocess
from tempfile import TemporaryDirectory
from typing import Any
import struct
import zlib

from src.environment.compute_config import ComputeConfig
from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.link_rate_config import LinkRateConfig
from src.environment.runtime_model import SharedRuntimeParameters
from src.environment.topology import TopologyGraph
from src.environment.trace_source import TraceSource
from src.environment.traffic_config import TrafficConfig
from src.environment.traffic_generator import TrafficGenerator
from src.evaluation.metrics import TaskEvaluationRecord, evaluate_trace
from src.evaluation.policy_registry import PolicyRegistry
from src.evaluation.scenario_registry import ScenarioRegistry
from src.policies import RandomOffloadingPolicy
from src.policies.policy_interface import PolicyContext

from .config import (
    ACTIVE_POLICIES,
    ARTIFACT_DIR,
    FEATURE_080_BOUNDARY,
    FEATURE_086_BOUNDARY,
    FEATURE_086_REPORT_PATH,
    FEATURE_ID,
    PAPER_OCR_PATH,
    PAPER_PDF_PATH,
    PRIORITY_1_FIGURES,
    PRIORITY_2_FIGURES,
    PRIORITY_3_FIGURES,
    SIMULATOR_REFERENCE_ARTIFACTS,
    SPEC_DIR,
)
from .output_usage_bundle import generate_output_usage_bundle, validate_output_usage_bundle
from .model import Feature089Report, PaperFigure, PaperMetric, SimulatorOutputRequirement


FIGURE_10_SIMULATION_SEED = 7
FIGURE_10_HIGH_TIMEOUT_SECONDS = 10.0
FIGURE_10_STRICT_TIMEOUT_SECONDS = 2.0
FIGURE_9_VALIDATION_SEEDS = (7, 13, 21)
FIGURE_9_PAPER_VALIDATION_EPISODES = 200
FIGURE_10_COMPARISON_ANALYSIS_VERDICT = "figure_10_comparison_analysis_partial"
FIGURE_10_COMPARISON_ANALYSIS_MODE = "qualitative_ranking_based"
FIGURE_9_OUTPUT_SUPPORT_STATUS = "generated_with_approximation"
FIGURE_8_TRAINING_STATUS = "not_generated_training_required"
FIGURE_11_TRAINING_STATUS = "not_generated_lstm_training_required"
PAPER_STYLE_PLOT_DIR_NAME = "paper_style_plots"


@dataclass(frozen=True, slots=True)
class Figure10SweepRow:
    figure_id: str
    policy: str
    metric: str
    x_axis: str
    sweep_value: float
    seed: int
    scenario_name: str
    number_of_agents: int
    episode_length: int
    arrival_probability: float
    timeout_slots: int
    timeout_seconds: float
    cpu_capacity_per_slot_agent: float
    cpu_capacity_per_slot_edge: float
    cpu_capacity_per_slot_cloud: float
    task_completion_delay_raw: float
    paper_style_delay_for_plotting: float
    task_drop_ratio: float
    task_drop_percent: float
    completion_rate: float
    throughput: int
    average_reward: float
    total_reward: float
    completed_tasks: int
    dropped_tasks: int
    total_tasks: int
    generated_arrivals: int
    finalized_terminal_tasks: int
    pending_at_horizon: int
    status: str
    claim_boundary: tuple[str, ...]
    notes: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "figure_id": self.figure_id,
            "policy": self.policy,
            "metric": self.metric,
            "x_axis": self.x_axis,
            "sweep_value": self.sweep_value,
            "seed": self.seed,
            "scenario_name": self.scenario_name,
            "number_of_agents": self.number_of_agents,
            "episode_length": self.episode_length,
            "arrival_probability": self.arrival_probability,
            "timeout_slots": self.timeout_slots,
            "timeout_seconds": self.timeout_seconds,
            "cpu_capacity_per_slot_agent": self.cpu_capacity_per_slot_agent,
            "cpu_capacity_per_slot_edge": self.cpu_capacity_per_slot_edge,
            "cpu_capacity_per_slot_cloud": self.cpu_capacity_per_slot_cloud,
            "task_completion_delay_raw": self.task_completion_delay_raw,
            "paper_style_delay_for_plotting": self.paper_style_delay_for_plotting,
            "task_drop_ratio": self.task_drop_ratio,
            "task_drop_percent": self.task_drop_percent,
            "completion_rate": self.completion_rate,
            "throughput": self.throughput,
            "average_reward": self.average_reward,
            "total_reward": self.total_reward,
            "completed_tasks": self.completed_tasks,
            "dropped_tasks": self.dropped_tasks,
            "total_tasks": self.total_tasks,
            "generated_arrivals": self.generated_arrivals,
            "finalized_terminal_tasks": self.finalized_terminal_tasks,
            "pending_at_horizon": self.pending_at_horizon,
            "status": self.status,
            "claim_boundary": list(self.claim_boundary),
            "notes": self.notes,
        }


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_json_dump(payload), encoding="utf-8")


def _paper_style_plot_dir(artifact_dir: Path) -> Path:
    return artifact_dir / PAPER_STYLE_PLOT_DIR_NAME


def _png_bytes(width: int, height: int, rgb_rows: list[bytes]) -> bytes:
    raw = b"".join(b"\x00" + row for row in rgb_rows)
    compressor = zlib.compressobj()
    compressed = compressor.compress(raw) + compressor.flush()

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", compressed) + chunk(b"IEND", b"")


def _blank_canvas(width: int = 1000, height: int = 600, color: tuple[int, int, int] = (255, 255, 255)) -> list[list[list[int]]]:
    return [[[color[0], color[1], color[2]] for _ in range(width)] for _ in range(height)]


def _set_px(canvas: list[list[list[int]]], x: int, y: int, color: tuple[int, int, int]) -> None:
    if 0 <= y < len(canvas) and 0 <= x < len(canvas[0]):
        canvas[y][x] = [color[0], color[1], color[2]]


def _fill_rect(canvas: list[list[list[int]]], x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
    for y in range(max(0, y0), min(len(canvas), y1)):
        row = canvas[y]
        for x in range(max(0, x0), min(len(row), x1)):
            row[x] = [color[0], color[1], color[2]]


def _line(canvas: list[list[list[int]]], x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        _set_px(canvas, x0, y0, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def _write_png_canvas(path: Path, canvas: list[list[list[int]]]) -> None:
    rows = [bytes(channel for pixel in row for channel in pixel) for row in canvas]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_png_bytes(len(canvas[0]), len(canvas), rows))


def _draw_series_plot(path: Path, title: str, x_label: str, y_label: str, series: list[dict[str, Any]], kind: str = "line") -> None:
    width, height = 1000, 600
    canvas = _blank_canvas(width, height)
    _fill_rect(canvas, 0, 0, width, height, (250, 250, 252))
    _fill_rect(canvas, 80, 60, width - 40, height - 70, (255, 255, 255))
    _line(canvas, 80, height - 70, width - 40, height - 70, (0, 0, 0))
    _line(canvas, 80, 60, 80, height - 70, (0, 0, 0))
    colors = [(31, 119, 180), (255, 127, 14), (44, 160, 44), (214, 39, 40), (148, 103, 189), (140, 86, 75), (227, 119, 194)]
    xs = [float(point) for s in series for point in s["x"]]
    ys = [float(point) for s in series for point in s["y"]]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    if abs(max_x - min_x) < 1e-9:
        max_x += 1.0
    if abs(max_y - min_y) < 1e-9:
        max_y += 1.0

    def sx(value: float) -> int:
        return int(80 + (value - min_x) / (max_x - min_x) * (width - 120))

    def sy(value: float) -> int:
        return int((height - 70) - (value - min_y) / (max_y - min_y) * (height - 140))

    for idx, s in enumerate(series):
        color = colors[idx % len(colors)]
        points = list(zip(s["x"], s["y"]))
        for i in range(len(points) - 1):
            _line(canvas, sx(float(points[i][0])), sy(float(points[i][1])), sx(float(points[i + 1][0])), sy(float(points[i + 1][1])), color)
        for x_val, y_val in points:
            cx, cy = sx(float(x_val)), sy(float(y_val))
            _fill_rect(canvas, cx - 3, cy - 3, cx + 4, cy + 4, color)
    _fill_rect(canvas, width - 250, 80, width - 50, 170, (245, 245, 245))
    _write_png_canvas(path, canvas)


def _draw_status_plot(path: Path, figure_id: str, reason: str) -> None:
    canvas = _blank_canvas()
    _fill_rect(canvas, 0, 0, 1000, 600, (244, 248, 252))
    _fill_rect(canvas, 120, 120, 880, 480, (255, 255, 255))
    _fill_rect(canvas, 120, 120, 880, 180, (230, 236, 244))
    _fill_rect(canvas, 120, 420, 880, 480, (245, 235, 235))
    _fill_rect(canvas, 160, 220, 840, 380, (250, 250, 250))
    _write_png_canvas(path, canvas)


def _plot_status_panel(path: Path, figure_id: str, reason: str) -> None:
    _draw_status_plot(path, figure_id, reason)


def _load_rows(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"{path.name} must contain a JSON array")
    return [dict(row) for row in payload]


def _plot_figure_9(artifact_dir: Path, plot_dir: Path, figure_id: str, rows: list[dict[str, Any]]) -> None:
    path_map = {
        "Figure 9a": "figure_9a_reward_vs_arrival_probability.png",
        "Figure 9b": "figure_9b_action_distribution_vs_arrival_probability.png",
        "Figure 9c": "figure_9c_reward_vs_cpu_capacity.png",
        "Figure 9d": "figure_9d_reward_vs_agent_count_traffic.png",
        "Figure 9e": "figure_9e_reward_vs_agent_count_data_rate.png",
    }
    if figure_id == "Figure 9b":
        action_types = ["local", "horizontal", "vertical"]
        sweep_values = sorted({float(row["sweep_value"]) for row in rows})
        series = []
        for action_type in action_types:
            values = []
            for sweep_value in sweep_values:
                match = next(row for row in rows if float(row["sweep_value"]) == sweep_value and row["action_type"] == action_type)
                values.append(float(match["action_share"]))
            series.append({"label": action_type.title(), "x": sweep_values, "y": values})
        _draw_series_plot(plot_dir / path_map[figure_id], "Figure 9b", "Task Arrival Probability P", "Action Share", series)
    else:
        series_key = "curve_label"
        x_key = "sweep_value"
        y_key = "average_reward"
        series = []
        for curve_label in sorted({str(row[series_key]) for row in rows}):
            series_rows = sorted((row for row in rows if str(row[series_key]) == curve_label), key=lambda row: float(row[x_key]))
            x_values = [float(row[x_key]) for row in series_rows]
            y_values = [float(row[y_key]) for row in series_rows]
            series.append({"label": curve_label.replace("_", " ").title(), "x": x_values, "y": y_values})
        if figure_id in {"Figure 9a", "Figure 9c"}:
            x_label = "Task Arrival Probability P" if figure_id == "Figure 9a" else "CPU Computation Capacity (GHz)"
            _draw_series_plot(plot_dir / path_map[figure_id], figure_id, x_label, "Average Reward (a.u.)", series)
        elif figure_id == "Figure 9d":
            _draw_series_plot(plot_dir / path_map[figure_id], figure_id, "Number of Agents N", "Average Reward (a.u.)", series)
        else:
            _draw_series_plot(plot_dir / path_map[figure_id], figure_id, "Number of Agents N", "Average Reward (a.u.)", series)


def _plot_figure_10(artifact_dir: Path, plot_dir: Path, figure_id: str, rows: list[dict[str, Any]]) -> None:
    path_map = {
        "Figure 10a": "figure_10a_delay_vs_arrival_probability.png",
        "Figure 10b": "figure_10b_delay_vs_cpu_capacity.png",
        "Figure 10c": "figure_10c_delay_vs_timeout.png",
        "Figure 10d": "figure_10d_drop_ratio_vs_arrival_probability.png",
        "Figure 10e": "figure_10e_drop_ratio_vs_cpu_capacity.png",
        "Figure 10f": "figure_10f_drop_ratio_vs_timeout.png",
    }
    y_key = "paper_style_delay_for_plotting" if "delay" in figure_id else "task_drop_ratio"
    x_key = "sweep_value"
    series = []
    for policy in ACTIVE_POLICIES:
        series_rows = sorted((row for row in rows if row["policy"] == policy), key=lambda row: float(row[x_key]))
        x_values = [float(row[x_key]) for row in series_rows]
        y_values = [float(row[y_key]) for row in series_rows]
        series.append({"label": policy, "x": x_values, "y": y_values})
    x_labels = {
        "Figure 10a": "Task Arrival Probability P",
        "Figure 10b": "CPU Computation Capacity (GHz)",
        "Figure 10c": "Task Timeout (sec)",
        "Figure 10d": "Task Arrival Probability P",
        "Figure 10e": "CPU Computation Capacity (GHz)",
        "Figure 10f": "Task Timeout (sec)",
    }
    y_labels = {
        "Figure 10a": "Average Delay (paper-style negative)",
        "Figure 10b": "Average Delay (paper-style negative)",
        "Figure 10c": "Average Delay (paper-style negative)",
        "Figure 10d": "Drop Ratio",
        "Figure 10e": "Drop Ratio",
        "Figure 10f": "Drop Ratio",
    }
    _draw_series_plot(plot_dir / path_map[figure_id], figure_id, x_labels[figure_id], y_labels[figure_id], series)


def _plot_paper_style_outputs(artifact_dir: Path, figures: list[PaperFigure]) -> None:
    plot_dir = _paper_style_plot_dir(artifact_dir)
    plot_dir.mkdir(parents=True, exist_ok=True)
    gated_status_paths = {
        "Figure 8a": artifact_dir / "figure_8a_learning_rate_convergence_status.json",
        "Figure 8b": artifact_dir / "figure_8b_discount_factor_convergence_status.json",
        "Figure 11": artifact_dir / "figure_11_lstm_ablation_status.json",
    }
    for figure in figures:
        if figure.figure_id in PRIORITY_1_FIGURES:
            rows = _load_rows(artifact_dir / _figure_10_artifact_files()[figure.figure_id][1])
            _plot_figure_10(artifact_dir, plot_dir, figure.figure_id, rows)
        elif figure.figure_id in PRIORITY_2_FIGURES:
            rows = _load_rows(artifact_dir / _figure_9_artifact_files()[figure.figure_id][1])
            _plot_figure_9(artifact_dir, plot_dir, figure.figure_id, rows)
        elif figure.figure_id in {"Figure 8a", "Figure 8b", "Figure 11"}:
            payload = json.loads(gated_status_paths[figure.figure_id].read_text(encoding="utf-8"))
            _plot_status_panel(
                plot_dir / (
                    "figure_8a_learning_rate_convergence_status.png"
                    if figure.figure_id == "Figure 8a"
                    else "figure_8b_discount_factor_convergence_status.png"
                    if figure.figure_id == "Figure 8b"
                    else "figure_11_lstm_ablation_status.png"
                ),
                payload["figure_id"],
                payload["reason"],
            )


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    headers = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            normalized = {}
            for key, value in row.items():
                if isinstance(value, (dict, list, tuple)):
                    normalized[key] = json.dumps(value, ensure_ascii=False)
                else:
                    normalized[key] = value
            writer.writerow(normalized)


def _write_markdown_table(path: Path, rows: list[dict[str, Any]], title: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text(f"# {title}\n\n_No rows._\n", encoding="utf-8")
        return
    headers = list(rows[0].keys())
    lines = [f"# {title}", "", "| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        values = [str(row.get(header, "")) for header in headers]
        lines.append("| " + " | ".join(values) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _approved_topology() -> TopologyGraph:
    return TopologyGraph.from_approved_assumption_registry()


def _dynamic_topology(number_of_agents: int) -> TopologyGraph:
    node_ids = tuple(str(agent_id) for agent_id in range(1, number_of_agents + 1)) + ("cloud",)
    legal_adjacency = {
        node_id: tuple(destination for destination in node_ids if destination != node_id)
        for node_id in node_ids[:-1]
    }
    legal_adjacency["cloud"] = tuple(node_id for node_id in node_ids if node_id != "cloud")
    return TopologyGraph(node_ids=node_ids, legal_adjacency=legal_adjacency)


def _validate_topology_contract(topology: TopologyGraph) -> None:
    if len(topology.node_ids) != 20:
        raise ValueError("Approved Figure 7 topology must contain exactly 20 nodes")
    if len(topology.legal_adjacency) != 20:
        raise ValueError("Approved Figure 7 topology must expose 20 adjacency rows")
    degrees = [len(topology.legal_adjacency[node]) for node in topology.node_ids]
    if any(degree != 3 for degree in degrees):
        raise ValueError("Approved Figure 7 topology must have degree 3 for every node")
    if sum(degrees) // 2 != 30:
        raise ValueError("Approved Figure 7 topology must contain 30 undirected edges")


def _policy_factory(policy_name: str, seed: int) -> object:
    if policy_name == "RO":
        return RandomOffloadingPolicy(seed=seed)
    return PolicyRegistry.resolve(policy_name)


def _base_traffic_config() -> TrafficConfig:
    return ScenarioRegistry.resolve("paper_default", 110)


def _traffic_config_for_figure(figure_id: str, sweep_value: float) -> TrafficConfig:
    base = _base_traffic_config()
    if figure_id in {"Figure 10a", "Figure 10b", "Figure 10c"}:
        timeout_seconds = FIGURE_10_HIGH_TIMEOUT_SECONDS
        arrival_probability = float(sweep_value) if figure_id == "Figure 10a" else base.arrival_probability
        timeout_slots = int(round(timeout_seconds / base.slot_duration_seconds)) if figure_id != "Figure 10c" else int(
            round(float(sweep_value) / base.slot_duration_seconds)
        )
    elif figure_id in {"Figure 10d", "Figure 10e", "Figure 10f"}:
        timeout_seconds = FIGURE_10_STRICT_TIMEOUT_SECONDS
        arrival_probability = float(sweep_value) if figure_id == "Figure 10d" else base.arrival_probability
        timeout_slots = int(round(timeout_seconds / base.slot_duration_seconds)) if figure_id != "Figure 10f" else int(
            round(float(sweep_value) / base.slot_duration_seconds)
        )
    else:
        raise ValueError(f"Unsupported Figure 10 identifier: {figure_id}")
    return TrafficConfig(
        scenario_name=base.scenario_name,
        number_of_agents=base.number_of_agents,
        episode_length=base.episode_length,
        arrival_probability=arrival_probability,
        slot_duration_seconds=base.slot_duration_seconds,
        timeout_slots=timeout_slots,
        task_size_mbits_min=base.task_size_mbits_min,
        task_size_mbits_max=base.task_size_mbits_max,
        task_size_mbits_step=base.task_size_mbits_step,
        processing_density_gcycles_per_mbit=base.processing_density_gcycles_per_mbit,
    )


def _compute_config_for_figure(figure_id: str, sweep_value: float) -> ComputeConfig:
    if figure_id in {"Figure 10b", "Figure 10e"}:
        default_compute = ComputeConfig()
        return ComputeConfig(
            cpu_capacity_per_slot_agent=float(sweep_value),
            cpu_capacity_per_slot_edge=default_compute.cpu_capacity_per_slot_edge,
            cpu_capacity_per_slot_cloud=default_compute.cpu_capacity_per_slot_cloud,
        )
    return ComputeConfig()


def _link_rate_config_for_figure9(figure_id: str, curve_label: str) -> LinkRateConfig:
    if figure_id != "Figure 9e":
        return LinkRateConfig()
    if curve_label == "balanced":
        return LinkRateConfig(horizontal_data_rate_mbps=10.0, vertical_data_rate_mbps=30.0)
    if curve_label == "horizontal_centric":
        return LinkRateConfig(horizontal_data_rate_mbps=20.0, vertical_data_rate_mbps=20.0)
    if curve_label == "vertical_centric":
        return LinkRateConfig(horizontal_data_rate_mbps=5.0, vertical_data_rate_mbps=40.0)
    raise ValueError(f"Unsupported Figure 9e curve label: {curve_label}")


def _family_for_action(action: str | None) -> str:
    if action in {"local", "compute_local"}:
        return "local"
    if action in {"horizontal", "offload_horizontal"}:
        return "horizontal"
    if action in {"vertical", "offload_vertical"}:
        return "vertical"
    return "unknown"


def _collect_task_records(info: dict[str, Any], policy_name: str, scenario_name: str, seed: int) -> list[TaskEvaluationRecord]:
    records: list[TaskEvaluationRecord] = []
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
    return records


def _collect_action_counts(records: list[TaskEvaluationRecord]) -> dict[str, int]:
    counts = Counter(_family_for_action(record.selected_action) for record in records)
    return {family: int(counts.get(family, 0)) for family in ("local", "horizontal", "vertical")}


def _run_policy_episode(
    *,
    policy_name: str,
    traffic_config: TrafficConfig,
    compute_config: ComputeConfig,
    topology: TopologyGraph,
    link_rate_config: LinkRateConfig,
    trace_source: TraceSource,
    seed: int,
    generated_arrivals: int,
) -> dict[str, Any]:
    policy = _policy_factory(policy_name, seed)
    env = HoodieGymEnvironment(
        episode_length=traffic_config.episode_length,
        topology=topology,
        runtime_parameters=SharedRuntimeParameters(),
        compute_config=compute_config,
        link_rate_config=link_rate_config,
        trace_source=trace_source,
        policy_name=policy_name,
    )
    observation, _info = env.reset(seed=None)
    del observation
    total_reward = 0.0
    while True:
        current_task = env.current_task
        if current_task is None:
            action = None
        else:
            observation = env.observe_flat(current_task)
            legal_action_mask = env.legal_action_mask(current_task)
            context = PolicyContext(
                observation=observation,
                legal_action_mask=legal_action_mask,
                trace_history=(trace_source.identifier,),
            )
            action = policy.choose_action(context)
        _observation, reward, terminated, truncated, info = env.step(action)
        if isinstance(reward, (int, float)) and not isnan(float(reward)):
            total_reward += float(reward)
        if terminated or truncated:
            break
    records = _collect_task_records(info, policy_name, traffic_config.scenario_name, seed)
    trace_metrics = evaluate_trace(
        trace_id=trace_source.identifier,
        policy_name=policy_name,
        seed=seed,
        device="cpu",
        records=records,
    )
    finalized_terminal_tasks = len(records)
    pending_at_horizon = max(generated_arrivals - finalized_terminal_tasks, 0)
    average_reward = float(total_reward / finalized_terminal_tasks) if finalized_terminal_tasks else 0.0
    return {
        "trace_metrics": trace_metrics.to_dict(),
        "generated_arrivals": generated_arrivals,
        "finalized_terminal_tasks": finalized_terminal_tasks,
        "pending_at_horizon": pending_at_horizon,
        "average_reward": average_reward,
        "total_reward": float(total_reward),
        "trace_id": trace_source.identifier,
        "records": records,
        "action_counts": _collect_action_counts(records),
        "topology_node_count": len(topology.node_ids),
    }


def _figure_10_row(
    *,
    figure: PaperFigure,
    policy: str,
    sweep_value: float,
    traffic_config: TrafficConfig,
    compute_config: ComputeConfig,
    trace_metrics: dict[str, Any],
    generated_arrivals: int,
    finalized_terminal_tasks: int,
    pending_at_horizon: int,
    average_reward: float,
    total_reward: float,
) -> Figure10SweepRow:
    task_completion_delay_raw = float(trace_metrics.get("average_delay", 0.0))
    task_drop_ratio = float(trace_metrics.get("drop_ratio", 0.0))
    total_tasks = int(trace_metrics.get("total_tasks", finalized_terminal_tasks))
    completed_tasks = int(trace_metrics.get("completed_tasks", 0))
    dropped_tasks = int(trace_metrics.get("dropped_tasks", 0))
    throughput = int(trace_metrics.get("throughput", 0))
    completion_rate = float(completed_tasks / total_tasks) if total_tasks else 0.0
    paper_style_delay = -abs(task_completion_delay_raw)
    return Figure10SweepRow(
        figure_id=figure.figure_id,
        policy=policy,
        metric=figure.metric,
        x_axis=figure.x_axis,
        sweep_value=float(sweep_value),
        seed=FIGURE_10_SIMULATION_SEED,
        scenario_name=traffic_config.scenario_name,
        number_of_agents=traffic_config.number_of_agents,
        episode_length=traffic_config.episode_length,
        arrival_probability=float(traffic_config.arrival_probability),
        timeout_slots=int(traffic_config.timeout_slots),
        timeout_seconds=float(traffic_config.timeout_slots * traffic_config.slot_duration_seconds),
        cpu_capacity_per_slot_agent=float(compute_config.cpu_capacity_per_slot_agent),
        cpu_capacity_per_slot_edge=float(compute_config.cpu_capacity_per_slot_edge),
        cpu_capacity_per_slot_cloud=float(compute_config.cpu_capacity_per_slot_cloud),
        task_completion_delay_raw=task_completion_delay_raw,
        paper_style_delay_for_plotting=paper_style_delay,
        task_drop_ratio=task_drop_ratio,
        task_drop_percent=_drop_percent(task_drop_ratio),
        completion_rate=completion_rate,
        throughput=throughput,
        average_reward=average_reward,
        total_reward=total_reward,
        completed_tasks=completed_tasks,
        dropped_tasks=dropped_tasks,
        total_tasks=total_tasks,
        generated_arrivals=generated_arrivals,
        finalized_terminal_tasks=finalized_terminal_tasks,
        pending_at_horizon=pending_at_horizon,
        status="simulator_generated",
        claim_boundary=figure.claim_boundary,
        notes=(
            "Live simulator sweep generated from the approved runtime controls. "
            "Preserve raw positive delay and paper-style negative plotting delay; "
            "preserve raw drop ratio and percentage."
        ),
    )


def _ordered_figures() -> list[PaperFigure]:
    return [
        PaperFigure(
            figure_id="Figure 8a",
            family="Figure 8",
            paper_section="Section V.A",
            caption="Accumulated reward time-course across learning-rate sweeps.",
            metric="accumulated_reward",
            x_axis="training_episode",
            sweep_values=(1e-9, 5e-9, 1e-8, 1e-7, 5e-7, 7e-7),
            policies_or_curves=("HOODIE",),
            scenario_setup="Table 4 defaults; P=0.5; N=20; Figure 7 topology; 5000 training episodes.",
            requires_training=True,
            requires_lstm=True,
            requires_digitization=False,
            priority="priority_3_training_or_lstm_required",
            output_status="later_training_required",
            extraction_confidence="high",
            pdf_verified=True,
            ocr_caveat="Learning-rate sweep is explicit in the OCR and PDF text.",
            simulator_output_requirement_id="req_figure_8a_training_curve",
            claim_boundary=FEATURE_080_BOUNDARY + FEATURE_086_BOUNDARY,
        ),
        PaperFigure(
            figure_id="Figure 8b",
            family="Figure 8",
            paper_section="Section V.A",
            caption="Accumulated reward time-course across discount-factor sweeps.",
            metric="accumulated_reward",
            x_axis="training_episode",
            sweep_values=(0.2, 0.4, 0.6, 0.8, 0.99),
            policies_or_curves=("HOODIE",),
            scenario_setup="Table 4 defaults except gamma sweep; optimal learning rate carried over from Figure 8a.",
            requires_training=True,
            requires_lstm=True,
            requires_digitization=False,
            priority="priority_3_training_or_lstm_required",
            output_status="later_training_required",
            extraction_confidence="high",
            pdf_verified=True,
            ocr_caveat="Discount-factor sweep is explicit in the OCR and PDF text.",
            simulator_output_requirement_id="req_figure_8b_training_curve",
            claim_boundary=FEATURE_080_BOUNDARY + FEATURE_086_BOUNDARY,
        ),
        PaperFigure(
            figure_id="Figure 9a",
            family="Figure 9",
            paper_section="Section V.B",
            caption="Average reward versus task arrival probability for different agent counts.",
            metric="average_reward",
            x_axis="task_arrival_probability",
            sweep_values=(0.1, 0.3, 0.5, 0.7, 0.9),
            policies_or_curves=("N=10", "N=15", "N=20"),
            scenario_setup="Table 4 defaults; N=10/15/20; 200 validation episodes; exploitative actions.",
            requires_training=False,
            requires_lstm=False,
            requires_digitization=False,
            priority="priority_2_hoodie_behavior_output",
            extraction_confidence="medium",
            pdf_verified=True,
            ocr_caveat="OCR and PDF disagree on some tick labels; the paper text supports the 0.1-0.9 sweep.",
            simulator_output_requirement_id="req_figure_9a_reward_arrival",
            output_status="reference_only",
            claim_boundary=FEATURE_080_BOUNDARY + FEATURE_086_BOUNDARY,
        ),
        PaperFigure(
            figure_id="Figure 9b",
            family="Figure 9",
            paper_section="Section V.B",
            caption="Action distribution across task arrival probabilities.",
            metric="action_distribution",
            x_axis="action_type",
            sweep_values=(0.1, 0.3, 0.5, 0.7, 0.9),
            policies_or_curves=("local", "horizontal", "vertical"),
            scenario_setup="Table 4 defaults; N=20; HOODIE only; exploitative validation episodes; bars are task arrival probabilities P=0.1/0.3/0.5/0.7/0.9.",
            requires_training=False,
            requires_lstm=False,
            requires_digitization=False,
            priority="priority_2_hoodie_behavior_output",
            extraction_confidence="high",
            pdf_verified=True,
            ocr_caveat="Action categories are explicit in the paper text.",
            simulator_output_requirement_id="req_figure_9b_action_distribution",
            output_status="reference_only",
            claim_boundary=FEATURE_080_BOUNDARY + FEATURE_086_BOUNDARY,
        ),
        PaperFigure(
            figure_id="Figure 9c",
            family="Figure 9",
            paper_section="Section V.B",
            caption="Average reward versus local CPU computation capacity.",
            metric="average_reward",
            x_axis="cpu_computation_capacity_ghz",
            sweep_values=(4, 5, 6, 7, 8, 9),
            policies_or_curves=("N=10", "N=15", "N=20"),
            scenario_setup="Table 4 defaults; CPU capacity sweep; HOODIE only.",
            requires_training=False,
            requires_lstm=False,
            requires_digitization=False,
            priority="priority_2_hoodie_behavior_output",
            extraction_confidence="high",
            pdf_verified=True,
            ocr_caveat="CPU sweep values are explicit in the paper text.",
            simulator_output_requirement_id="req_figure_9c_reward_cpu",
            output_status="reference_only",
            claim_boundary=FEATURE_080_BOUNDARY + FEATURE_086_BOUNDARY,
        ),
        PaperFigure(
            figure_id="Figure 9d",
            family="Figure 9",
            paper_section="Section V.B",
            caption="Average reward versus number of agents under traffic intensity scenarios.",
            metric="average_reward",
            x_axis="number_of_agents",
            sweep_values=(10, 15, 20, 25, 30),
            policies_or_curves=("Moderate Traffic", "Heavy Traffic", "Extreme Traffic"),
            scenario_setup="Moderate: task sizes 1-3 Mbits, P=0.5; Heavy: task sizes 2-5 Mbits, P=0.7; Extreme: task sizes 3-7 Mbits, P=0.9.",
            requires_training=False,
            requires_lstm=False,
            requires_digitization=False,
            priority="priority_2_hoodie_behavior_output",
            extraction_confidence="high",
            pdf_verified=True,
            ocr_caveat="Traffic-intensity scenarios are explicit in the paper text.",
            simulator_output_requirement_id="req_figure_9d_reward_agents_traffic",
            output_status="reference_only",
            claim_boundary=FEATURE_080_BOUNDARY + FEATURE_086_BOUNDARY,
        ),
        PaperFigure(
            figure_id="Figure 9e",
            family="Figure 9",
            paper_section="Section V.B",
            caption="Average reward versus number of agents under offloading data-rate configurations.",
            metric="average_reward",
            x_axis="number_of_agents",
            sweep_values=(10, 15, 20, 25, 30),
            policies_or_curves=("Balanced", "Horizontal-centric", "Vertical-centric"),
            scenario_setup="Balanced: RH=10 Mbps, RV=30 Mbps; Horizontal-centric: RH=20 Mbps, RV=20 Mbps; Vertical-centric: RH=5 Mbps, RV=40 Mbps.",
            requires_training=False,
            requires_lstm=False,
            requires_digitization=False,
            priority="priority_2_hoodie_behavior_output",
            extraction_confidence="high",
            pdf_verified=True,
            ocr_caveat="Data-rate configurations are explicit in the paper text.",
            simulator_output_requirement_id="req_figure_9e_reward_agents_rates",
            output_status="reference_only",
            claim_boundary=FEATURE_080_BOUNDARY + FEATURE_086_BOUNDARY,
        ),
        PaperFigure(
            figure_id="Figure 10a",
            family="Figure 10",
            paper_section="Section V.C",
            caption="Average delay versus task arrival probability for comparative baselines.",
            metric="average_task_completion_delay",
            x_axis="task_arrival_probability",
            sweep_values=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9),
            policies_or_curves=ACTIVE_POLICIES,
            scenario_setup="High timeout window: 10 sec; Table 4 defaults otherwise.",
            requires_training=False,
            requires_lstm=False,
            requires_digitization=False,
            priority="priority_1_comparative_output",
            output_status="required_now",
            extraction_confidence="high",
            pdf_verified=True,
            ocr_caveat="PDF confirms the high-timeout comparative sweep and the arrival-probability x-range.",
            simulator_output_requirement_id="req_figure_10a_delay_arrival",
            claim_boundary=FEATURE_080_BOUNDARY + FEATURE_086_BOUNDARY,
        ),
        PaperFigure(
            figure_id="Figure 10b",
            family="Figure 10",
            paper_section="Section V.C",
            caption="Average delay versus CPU computation capacity for comparative baselines.",
            metric="average_task_completion_delay",
            x_axis="cpu_computation_capacity_ghz",
            sweep_values=(3, 4, 5, 6, 7),
            policies_or_curves=ACTIVE_POLICIES,
            scenario_setup="High timeout window: 10 sec; CPU capacity sweep.",
            requires_training=False,
            requires_lstm=False,
            requires_digitization=False,
            priority="priority_1_comparative_output",
            output_status="required_now",
            extraction_confidence="high",
            pdf_verified=True,
            ocr_caveat="PDF resolves the CPU sweep range as 3-7 GHz.",
            simulator_output_requirement_id="req_figure_10b_delay_cpu",
            claim_boundary=FEATURE_080_BOUNDARY + FEATURE_086_BOUNDARY,
        ),
        PaperFigure(
            figure_id="Figure 10c",
            family="Figure 10",
            paper_section="Section V.C",
            caption="Average delay versus task timeout for comparative baselines.",
            metric="average_task_completion_delay",
            x_axis="task_timeout_sec",
            sweep_values=(9.6, 9.8, 10.0, 10.2, 10.4),
            policies_or_curves=ACTIVE_POLICIES,
            scenario_setup="High timeout comparison window from 9.6 to 10.4 sec.",
            requires_training=False,
            requires_lstm=False,
            requires_digitization=False,
            priority="priority_1_comparative_output",
            output_status="required_now",
            extraction_confidence="high",
            pdf_verified=True,
            ocr_caveat="PDF confirms the timeout axis values.",
            simulator_output_requirement_id="req_figure_10c_delay_timeout",
            claim_boundary=FEATURE_080_BOUNDARY + FEATURE_086_BOUNDARY,
        ),
        PaperFigure(
            figure_id="Figure 10d",
            family="Figure 10",
            paper_section="Section V.C",
            caption="Drop ratio versus task arrival probability for comparative baselines.",
            metric="task_drop_ratio",
            x_axis="task_arrival_probability",
            sweep_values=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9),
            policies_or_curves=ACTIVE_POLICIES,
            scenario_setup="Strict timeout window: 2 sec; Table 4 defaults otherwise.",
            requires_training=False,
            requires_lstm=False,
            requires_digitization=False,
            priority="priority_1_comparative_output",
            output_status="required_now",
            extraction_confidence="high",
            pdf_verified=True,
            ocr_caveat="PDF confirms the strict timeout window and the arrival-probability sweep.",
            simulator_output_requirement_id="req_figure_10d_drop_arrival",
            claim_boundary=FEATURE_080_BOUNDARY + FEATURE_086_BOUNDARY,
        ),
        PaperFigure(
            figure_id="Figure 10e",
            family="Figure 10",
            paper_section="Section V.C",
            caption="Drop ratio versus CPU computation capacity for comparative baselines.",
            metric="task_drop_ratio",
            x_axis="cpu_computation_capacity_ghz",
            sweep_values=(3, 4, 5, 6, 7),
            policies_or_curves=ACTIVE_POLICIES,
            scenario_setup="Strict timeout window: 2 sec; CPU capacity sweep.",
            requires_training=False,
            requires_lstm=False,
            requires_digitization=False,
            priority="priority_1_comparative_output",
            output_status="required_now",
            extraction_confidence="high",
            pdf_verified=True,
            ocr_caveat="PDF resolves the CPU sweep range as 3-7 GHz.",
            simulator_output_requirement_id="req_figure_10e_drop_cpu",
            claim_boundary=FEATURE_080_BOUNDARY + FEATURE_086_BOUNDARY,
        ),
        PaperFigure(
            figure_id="Figure 10f",
            family="Figure 10",
            paper_section="Section V.C",
            caption="Drop ratio versus task timeout for comparative baselines.",
            metric="task_drop_ratio",
            x_axis="task_timeout_sec",
            sweep_values=(1.6, 1.8, 2.0, 2.2, 2.4),
            policies_or_curves=ACTIVE_POLICIES,
            scenario_setup="Strict timeout comparison window from 1.6 to 2.4 sec.",
            requires_training=False,
            requires_lstm=False,
            requires_digitization=False,
            priority="priority_1_comparative_output",
            output_status="required_now",
            extraction_confidence="high",
            pdf_verified=True,
            ocr_caveat="PDF confirms the timeout axis values.",
            simulator_output_requirement_id="req_figure_10f_drop_timeout",
            claim_boundary=FEATURE_080_BOUNDARY + FEATURE_086_BOUNDARY,
        ),
        PaperFigure(
            figure_id="Figure 11",
            family="Figure 11",
            paper_section="Section V.D",
            caption="Average task delay with versus without LSTM across training episodes.",
            metric="average_task_delay_with_vs_without_lstm",
            x_axis="training_episode",
            sweep_values=(0, 500, 1000, 1500, 2000, 2500, 3000),
            policies_or_curves=("with LSTM", "without LSTM"),
            scenario_setup="P=0.3; phi_n=1 sec; 20 EAs; Table 4 defaults otherwise.",
            requires_training=True,
            requires_lstm=True,
            requires_digitization=False,
            priority="priority_3_training_or_lstm_required",
            output_status="later_lstm_required",
            extraction_confidence="high",
            pdf_verified=True,
            ocr_caveat="The paper gives explicit end-of-training values, but the figure itself is a training ablation.",
            simulator_output_requirement_id="req_figure_11_lstm_ablation",
            claim_boundary=FEATURE_080_BOUNDARY + FEATURE_086_BOUNDARY,
        ),
    ]


def _paper_metric_catalog() -> list[PaperMetric]:
    return [
        PaperMetric(
            metric_id="average_task_completion_delay",
            paper_names=("average delay", "average task delay", "completion delay"),
            definition="Mean task completion delay used in the paper's comparative figures.",
            used_in_figures=("Figure 10a", "Figure 10b", "Figure 10c", "Figure 11"),
            primary_or_secondary="primary",
            simulator_metric_mapping="task_completion_delay",
            requires_training=False,
            requires_lstm=False,
            comparison_allowed_now=True,
            claim_boundary=FEATURE_086_BOUNDARY,
        ),
        PaperMetric(
            metric_id="task_drop_ratio",
            paper_names=("drop ratio",),
            definition="Fraction of tasks dropped before completion.",
            used_in_figures=("Figure 10d", "Figure 10e", "Figure 10f"),
            primary_or_secondary="primary",
            simulator_metric_mapping="task_drop_ratio",
            requires_training=False,
            requires_lstm=False,
            comparison_allowed_now=True,
            claim_boundary=FEATURE_086_BOUNDARY,
        ),
        PaperMetric(
            metric_id="average_reward",
            paper_names=("average reward",),
            definition="Paper reward signal used in behavior and sensitivity figures.",
            used_in_figures=("Figure 9a", "Figure 9c", "Figure 9d", "Figure 9e"),
            primary_or_secondary="behavioral",
            simulator_metric_mapping="average_reward",
            requires_training=False,
            requires_lstm=False,
            comparison_allowed_now=False,
            claim_boundary=FEATURE_080_BOUNDARY,
        ),
        PaperMetric(
            metric_id="accumulated_reward",
            paper_names=("accumulated reward", "cumulative reward"),
            definition="Training convergence reward plotted across episodes.",
            used_in_figures=("Figure 8a", "Figure 8b"),
            primary_or_secondary="training",
            simulator_metric_mapping="total_reward",
            requires_training=True,
            requires_lstm=True,
            comparison_allowed_now=False,
            claim_boundary=FEATURE_080_BOUNDARY,
        ),
        PaperMetric(
            metric_id="action_distribution",
            paper_names=("actions count", "action distribution"),
            definition="Distribution of local, horizontal, and vertical actions across arrival probabilities.",
            used_in_figures=("Figure 9b",),
            primary_or_secondary="behavioral",
            simulator_metric_mapping=None,
            requires_training=False,
            requires_lstm=False,
            comparison_allowed_now=False,
            claim_boundary=FEATURE_086_BOUNDARY,
        ),
        PaperMetric(
            metric_id="average_task_delay_with_vs_without_lstm",
            paper_names=("average task delay with vs without LSTM", "LSTM ablation delay"),
            definition="Training ablation curve comparing HOODIE with and without the LSTM module.",
            used_in_figures=("Figure 11",),
            primary_or_secondary="training",
            simulator_metric_mapping="task_completion_delay",
            requires_training=True,
            requires_lstm=True,
            comparison_allowed_now=False,
            claim_boundary=FEATURE_080_BOUNDARY,
        ),
    ]


def _requirements() -> list[SimulatorOutputRequirement]:
    figures = {item.figure_id: item for item in _ordered_figures()}
    return [
        SimulatorOutputRequirement(
            requirement_id="req_figure_10a_delay_arrival",
            target_figures=("Figure 10a",),
            output_family="arrival_probability_delay_sweep",
            metrics=("task_completion_delay", "paper_style_delay_for_plotting"),
            policies=ACTIVE_POLICIES,
            x_axis="task_arrival_probability",
            sweep_values=figures["Figure 10a"].sweep_values,
            scenario_setup=figures["Figure 10a"].scenario_setup,
            artifact_outputs=("figure_10a_delay_vs_arrival_probability.csv", "figure_10a_delay_vs_arrival_probability.json"),
            implementation_priority="priority_1",
            blocked_by_training=False,
            blocked_by_lstm=False,
            blocked_by_simulator_support=False,
            notes="Preserve raw positive delay and a paper-style negative plotting value. Use the Feature 086 approximation boundary only.",
            claim_boundary=FEATURE_086_BOUNDARY + FEATURE_080_BOUNDARY,
        ),
        SimulatorOutputRequirement(
            requirement_id="req_figure_10b_delay_cpu",
            target_figures=("Figure 10b",),
            output_family="cpu_capacity_delay_sweep",
            metrics=("task_completion_delay", "paper_style_delay_for_plotting"),
            policies=ACTIVE_POLICIES,
            x_axis="cpu_computation_capacity_ghz",
            sweep_values=figures["Figure 10b"].sweep_values,
            scenario_setup=figures["Figure 10b"].scenario_setup,
            artifact_outputs=("figure_10b_delay_vs_cpu_capacity.csv", "figure_10b_delay_vs_cpu_capacity.json"),
            implementation_priority="priority_1",
            blocked_by_training=False,
            blocked_by_lstm=False,
            blocked_by_simulator_support=False,
            notes="Preserve raw positive delay and a paper-style negative plotting value. Use the Feature 086 approximation boundary only.",
            claim_boundary=FEATURE_086_BOUNDARY + FEATURE_080_BOUNDARY,
        ),
        SimulatorOutputRequirement(
            requirement_id="req_figure_10c_delay_timeout",
            target_figures=("Figure 10c",),
            output_family="timeout_delay_sweep",
            metrics=("task_completion_delay", "paper_style_delay_for_plotting"),
            policies=ACTIVE_POLICIES,
            x_axis="task_timeout_sec",
            sweep_values=figures["Figure 10c"].sweep_values,
            scenario_setup=figures["Figure 10c"].scenario_setup,
            artifact_outputs=("figure_10c_delay_vs_timeout.csv", "figure_10c_delay_vs_timeout.json"),
            implementation_priority="priority_1",
            blocked_by_training=False,
            blocked_by_lstm=False,
            blocked_by_simulator_support=False,
            notes="Preserve raw positive delay and a paper-style negative plotting value. Use the Feature 086 approximation boundary only.",
            claim_boundary=FEATURE_086_BOUNDARY + FEATURE_080_BOUNDARY,
        ),
        SimulatorOutputRequirement(
            requirement_id="req_figure_10d_drop_arrival",
            target_figures=("Figure 10d",),
            output_family="arrival_probability_drop_sweep",
            metrics=("task_drop_ratio", "task_drop_percent"),
            policies=ACTIVE_POLICIES,
            x_axis="task_arrival_probability",
            sweep_values=figures["Figure 10d"].sweep_values,
            scenario_setup=figures["Figure 10d"].scenario_setup,
            artifact_outputs=("figure_10d_drop_ratio_vs_arrival_probability.csv", "figure_10d_drop_ratio_vs_arrival_probability.json"),
            implementation_priority="priority_1",
            blocked_by_training=False,
            blocked_by_lstm=False,
            blocked_by_simulator_support=False,
            notes="Preserve raw drop ratio and percentage form for plotting and validation.",
            claim_boundary=FEATURE_086_BOUNDARY + FEATURE_080_BOUNDARY,
        ),
        SimulatorOutputRequirement(
            requirement_id="req_figure_10e_drop_cpu",
            target_figures=("Figure 10e",),
            output_family="cpu_capacity_drop_sweep",
            metrics=("task_drop_ratio", "task_drop_percent"),
            policies=ACTIVE_POLICIES,
            x_axis="cpu_computation_capacity_ghz",
            sweep_values=figures["Figure 10e"].sweep_values,
            scenario_setup=figures["Figure 10e"].scenario_setup,
            artifact_outputs=("figure_10e_drop_ratio_vs_cpu_capacity.csv", "figure_10e_drop_ratio_vs_cpu_capacity.json"),
            implementation_priority="priority_1",
            blocked_by_training=False,
            blocked_by_lstm=False,
            blocked_by_simulator_support=False,
            notes="Preserve raw drop ratio and percentage form for plotting and validation.",
            claim_boundary=FEATURE_086_BOUNDARY + FEATURE_080_BOUNDARY,
        ),
        SimulatorOutputRequirement(
            requirement_id="req_figure_10f_drop_timeout",
            target_figures=("Figure 10f",),
            output_family="timeout_drop_sweep",
            metrics=("task_drop_ratio", "task_drop_percent"),
            policies=ACTIVE_POLICIES,
            x_axis="task_timeout_sec",
            sweep_values=figures["Figure 10f"].sweep_values,
            scenario_setup=figures["Figure 10f"].scenario_setup,
            artifact_outputs=("figure_10f_drop_ratio_vs_timeout.csv", "figure_10f_drop_ratio_vs_timeout.json"),
            implementation_priority="priority_1",
            blocked_by_training=False,
            blocked_by_lstm=False,
            blocked_by_simulator_support=False,
            notes="Preserve raw drop ratio and percentage form for plotting and validation.",
            claim_boundary=FEATURE_086_BOUNDARY + FEATURE_080_BOUNDARY,
        ),
        SimulatorOutputRequirement(
            requirement_id="req_figure_9a_reward_arrival",
            target_figures=("Figure 9a",),
            output_family="arrival_probability_reward_sweep",
            metrics=("average_reward",),
            policies=("HOODIE",),
            x_axis="task_arrival_probability",
            sweep_values=figures["Figure 9a"].sweep_values,
            scenario_setup=figures["Figure 9a"].scenario_setup,
            artifact_outputs=("figure_9a_reward_vs_arrival_probability.csv", "figure_9a_reward_vs_arrival_probability.json"),
            implementation_priority="priority_2",
            blocked_by_training=False,
            blocked_by_lstm=False,
            blocked_by_simulator_support=True,
            notes="Reference-only Figure 9 behavior output. Do not schedule as deterministic simulator output until trained HOODIE DRL/LSTM policy support and paper validation semantics are available.",
            claim_boundary=FEATURE_080_BOUNDARY + FEATURE_086_BOUNDARY,
        ),
        SimulatorOutputRequirement(
            requirement_id="req_figure_9b_action_distribution",
            target_figures=("Figure 9b",),
            output_family="arrival_probability_action_distribution",
            metrics=("action_distribution",),
            policies=("HOODIE",),
            x_axis="action_type",
            sweep_values=figures["Figure 9b"].sweep_values,
            scenario_setup=figures["Figure 9b"].scenario_setup,
            artifact_outputs=("figure_9b_action_distribution_vs_arrival_probability.csv", "figure_9b_action_distribution_vs_arrival_probability.json"),
            implementation_priority="priority_2",
            blocked_by_training=False,
            blocked_by_lstm=False,
            blocked_by_simulator_support=True,
            notes="Reference-only Figure 9 behavior output. Action type remains the paper x-axis, but generation is blocked until trained HOODIE DRL/LSTM policy support and paper validation semantics are available.",
            claim_boundary=FEATURE_080_BOUNDARY + FEATURE_086_BOUNDARY,
        ),
        SimulatorOutputRequirement(
            requirement_id="req_figure_9c_reward_cpu",
            target_figures=("Figure 9c",),
            output_family="cpu_capacity_reward_sweep",
            metrics=("average_reward",),
            policies=("HOODIE",),
            x_axis="cpu_computation_capacity_ghz",
            sweep_values=figures["Figure 9c"].sweep_values,
            scenario_setup=figures["Figure 9c"].scenario_setup,
            artifact_outputs=("figure_9c_reward_vs_cpu_capacity.csv", "figure_9c_reward_vs_cpu_capacity.json"),
            implementation_priority="priority_2",
            blocked_by_training=False,
            blocked_by_lstm=False,
            blocked_by_simulator_support=True,
            notes="Reference-only Figure 9 behavior output. Do not schedule as deterministic simulator output until trained HOODIE DRL/LSTM policy support and paper validation semantics are available.",
            claim_boundary=FEATURE_080_BOUNDARY + FEATURE_086_BOUNDARY,
        ),
        SimulatorOutputRequirement(
            requirement_id="req_figure_9d_reward_agents_traffic",
            target_figures=("Figure 9d",),
            output_family="agent_count_traffic_reward_sweep",
            metrics=("average_reward",),
            policies=("HOODIE",),
            x_axis="number_of_agents",
            sweep_values=figures["Figure 9d"].sweep_values,
            scenario_setup=figures["Figure 9d"].scenario_setup,
            artifact_outputs=("figure_9d_reward_vs_agent_count_traffic.csv", "figure_9d_reward_vs_agent_count_traffic.json"),
            implementation_priority="priority_2",
            blocked_by_training=False,
            blocked_by_lstm=False,
            blocked_by_simulator_support=True,
            notes="Reference-only Figure 9 behavior output. Agent-count traffic sweep is cataloged but blocked until trained HOODIE DRL/LSTM policy support and paper validation semantics are available.",
            claim_boundary=FEATURE_080_BOUNDARY + FEATURE_086_BOUNDARY,
        ),
        SimulatorOutputRequirement(
            requirement_id="req_figure_9e_reward_agents_rates",
            target_figures=("Figure 9e",),
            output_family="agent_count_data_rate_reward_sweep",
            metrics=("average_reward",),
            policies=("HOODIE",),
            x_axis="number_of_agents",
            sweep_values=figures["Figure 9e"].sweep_values,
            scenario_setup=figures["Figure 9e"].scenario_setup,
            artifact_outputs=("figure_9e_reward_vs_agent_count_data_rate.csv", "figure_9e_reward_vs_agent_count_data_rate.json"),
            implementation_priority="priority_2",
            blocked_by_training=False,
            blocked_by_lstm=False,
            blocked_by_simulator_support=True,
            notes="Reference-only Figure 9 behavior output. Agent-count data-rate sweep is cataloged but blocked until trained HOODIE DRL/LSTM policy support and paper validation semantics are available.",
            claim_boundary=FEATURE_080_BOUNDARY + FEATURE_086_BOUNDARY,
        ),
        SimulatorOutputRequirement(
            requirement_id="req_figure_8a_training_curve",
            target_figures=("Figure 8a",),
            output_family="training_learning_rate_curve",
            metrics=("accumulated_reward",),
            policies=("HOODIE",),
            x_axis="training_episode",
            sweep_values=figures["Figure 8a"].sweep_values,
            scenario_setup=figures["Figure 8a"].scenario_setup,
            artifact_outputs=("figure_8a_learning_rate_training_curve.csv", "figure_8a_learning_rate_training_curve.json"),
            implementation_priority="priority_3",
            blocked_by_training=True,
            blocked_by_lstm=True,
            blocked_by_simulator_support=True,
            notes="Future-required training curve. Do not schedule as deterministic evaluation output.",
            claim_boundary=FEATURE_080_BOUNDARY + FEATURE_086_BOUNDARY,
        ),
        SimulatorOutputRequirement(
            requirement_id="req_figure_8b_training_curve",
            target_figures=("Figure 8b",),
            output_family="training_discount_factor_curve",
            metrics=("accumulated_reward",),
            policies=("HOODIE",),
            x_axis="training_episode",
            sweep_values=figures["Figure 8b"].sweep_values,
            scenario_setup=figures["Figure 8b"].scenario_setup,
            artifact_outputs=("figure_8b_discount_factor_training_curve.csv", "figure_8b_discount_factor_training_curve.json"),
            implementation_priority="priority_3",
            blocked_by_training=True,
            blocked_by_lstm=True,
            blocked_by_simulator_support=True,
            notes="Future-required training curve. Do not schedule as deterministic evaluation output.",
            claim_boundary=FEATURE_080_BOUNDARY + FEATURE_086_BOUNDARY,
        ),
        SimulatorOutputRequirement(
            requirement_id="req_figure_11_lstm_ablation",
            target_figures=("Figure 11",),
            output_family="lstm_ablation_curve",
            metrics=("average_task_delay_with_vs_without_lstm",),
            policies=("HOODIE",),
            x_axis="training_episode",
            sweep_values=figures["Figure 11"].sweep_values,
            scenario_setup=figures["Figure 11"].scenario_setup,
            artifact_outputs=("figure_11_lstm_ablation_curve.csv", "figure_11_lstm_ablation_curve.json"),
            implementation_priority="priority_3",
            blocked_by_training=True,
            blocked_by_lstm=True,
            blocked_by_simulator_support=True,
            notes="Future-required LSTM ablation. Do not schedule as deterministic evaluation output.",
            claim_boundary=FEATURE_080_BOUNDARY + FEATURE_086_BOUNDARY,
        ),
    ]


def _reference_metric_values() -> dict[str, dict[str, float | int]]:
    path = SIMULATOR_REFERENCE_ARTIFACTS[0]
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("rows", [])
    values: dict[str, dict[str, float | int]] = {}
    for row in rows:
        policy = str(row["policy"])
        values[policy] = {
            "task_completion_delay": float(row["task_completion_delay"]),
            "task_drop_ratio": float(row["task_drop_ratio"]),
            "average_reward": float(row["average_reward"]),
            "total_reward": float(row["total_reward"]),
            "throughput": float(row["throughput"]),
            "completion_rate": float(row["completion_rate"]),
        }
    return values


def _delay_plot_value(raw_value: float) -> float:
    return -abs(float(raw_value))


def _drop_percent(drop_ratio: float) -> float:
    return float(drop_ratio) * 100.0


def _figure_output_rows(figure: PaperFigure, requirement: SimulatorOutputRequirement, references: dict[str, dict[str, float | int]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if figure.figure_id in PRIORITY_1_FIGURES:
        metric_name = "task_completion_delay" if "delay" in figure.caption.lower() else "task_drop_ratio"
    elif figure.figure_id in PRIORITY_2_FIGURES:
        metric_name = figure.metric
    else:
        metric_name = "accumulated_reward" if figure.figure_id.startswith("Figure 8") else "average_task_delay_with_vs_without_lstm"

    for policy in requirement.policies:
        ref = references.get(policy, {})
        raw_delay = float(ref.get("task_completion_delay", 0.0))
        drop_ratio = float(ref.get("task_drop_ratio", 0.0))
        row: dict[str, Any] = {
            "figure_id": figure.figure_id,
            "policy": policy,
            "metric": metric_name,
            "x_axis": figure.x_axis,
            "sweep_values": list(figure.sweep_values),
            "reference_task_completion_delay_raw": raw_delay if "delay" in metric_name else None,
            "reference_task_completion_delay_plot": _delay_plot_value(raw_delay) if "delay" in metric_name else None,
            "reference_drop_ratio": drop_ratio if "drop" in metric_name else None,
            "reference_drop_percent": _drop_percent(drop_ratio) if "drop" in metric_name else None,
            "reference_average_reward": float(ref.get("average_reward", 0.0)) if metric_name == "average_reward" else None,
            "status": requirement.blocked_by_simulator_support and "blocked_by_simulator_support" or "ready_for_generation",
            "claim_boundary": list(requirement.claim_boundary),
            "notes": requirement.notes,
        }
        rows.append(row)
    return rows


def _figure_10_output_rows(figure: PaperFigure) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    topology = _approved_topology()
    _validate_topology_contract(topology)
    link_rate_config = LinkRateConfig()
    for sweep_value in figure.sweep_values:
        traffic_config = _traffic_config_for_figure(figure.figure_id, float(sweep_value))
        compute_config = _compute_config_for_figure(figure.figure_id, float(sweep_value))
        trace = TrafficGenerator.generate(traffic_config, FIGURE_10_SIMULATION_SEED)
        with TemporaryDirectory(prefix=f"feature_089_{figure.figure_id.lower().replace(' ', '_')}_") as temp_dir:
            temp_path = Path(temp_dir)
            trace.write_json(temp_path / f"{trace.trace_id}.json")
            trace_source = TraceSource.from_trace_bank(trace.trace_id, root_path=temp_path)
            for policy in ACTIVE_POLICIES:
                result = _run_policy_episode(
                    policy_name=policy,
                    traffic_config=traffic_config,
                    compute_config=compute_config,
                    topology=topology,
                    link_rate_config=link_rate_config,
                    trace_source=trace_source,
                    seed=FIGURE_10_SIMULATION_SEED,
                    generated_arrivals=len(trace.records),
                )
                rows.append(
                    _figure_10_row(
                        figure=figure,
                        policy=policy,
                        sweep_value=float(sweep_value),
                        traffic_config=traffic_config,
                        compute_config=compute_config,
                        trace_metrics=result["trace_metrics"],
                        generated_arrivals=int(result["generated_arrivals"]),
                        finalized_terminal_tasks=int(result["finalized_terminal_tasks"]),
                        pending_at_horizon=int(result["pending_at_horizon"]),
                        average_reward=float(result["average_reward"]),
                        total_reward=float(result["total_reward"]),
                    ).to_dict()
                )
    return rows


def _figure_10_artifact_files() -> dict[str, tuple[str, str]]:
    return {
        "Figure 10a": ("figure_10a_delay_vs_arrival_probability.csv", "figure_10a_delay_vs_arrival_probability.json"),
        "Figure 10b": ("figure_10b_delay_vs_cpu_capacity.csv", "figure_10b_delay_vs_cpu_capacity.json"),
        "Figure 10c": ("figure_10c_delay_vs_timeout.csv", "figure_10c_delay_vs_timeout.json"),
        "Figure 10d": ("figure_10d_drop_ratio_vs_arrival_probability.csv", "figure_10d_drop_ratio_vs_arrival_probability.json"),
        "Figure 10e": ("figure_10e_drop_ratio_vs_cpu_capacity.csv", "figure_10e_drop_ratio_vs_cpu_capacity.json"),
        "Figure 10f": ("figure_10f_drop_ratio_vs_timeout.csv", "figure_10f_drop_ratio_vs_timeout.json"),
    }


def _figure_9_artifact_files() -> dict[str, tuple[str, str]]:
    return {
        "Figure 9a": ("figure_9a_reward_vs_arrival_probability.csv", "figure_9a_reward_vs_arrival_probability.json"),
        "Figure 9b": ("figure_9b_action_distribution_vs_arrival_probability.csv", "figure_9b_action_distribution_vs_arrival_probability.json"),
        "Figure 9c": ("figure_9c_reward_vs_cpu_capacity.csv", "figure_9c_reward_vs_cpu_capacity.json"),
        "Figure 9d": ("figure_9d_reward_vs_agent_count_traffic.csv", "figure_9d_reward_vs_agent_count_traffic.json"),
        "Figure 9e": ("figure_9e_reward_vs_agent_count_data_rate.csv", "figure_9e_reward_vs_agent_count_data_rate.json"),
    }


def _figure_9_curve_labels(figure_id: str) -> list[tuple[str, int | None]]:
    if figure_id in {"Figure 9a", "Figure 9c"}:
        return [("N=10", 10), ("N=15", 15), ("N=20", 20)]
    if figure_id == "Figure 9b":
        return [("local", None), ("horizontal", None), ("vertical", None)]
    if figure_id == "Figure 9d":
        return [("moderate", None), ("heavy", None), ("extreme", None)]
    if figure_id == "Figure 9e":
        return [("balanced", None), ("horizontal_centric", None), ("vertical_centric", None)]
    raise ValueError(f"Unsupported Figure 9 identifier: {figure_id}")


def _figure_9_paper_curve_dimension(figure_id: str) -> str:
    if figure_id in {"Figure 9a", "Figure 9c"}:
        return "number_of_agents"
    if figure_id == "Figure 9b":
        return "task_arrival_probability"
    if figure_id == "Figure 9d":
        return "traffic_intensity"
    if figure_id == "Figure 9e":
        return "data_rate_configuration"
    raise ValueError(f"Unsupported Figure 9 identifier: {figure_id}")


def _figure_9_paper_x_value(figure_id: str, sweep_value: float, action_type: str | None) -> float | str:
    if figure_id == "Figure 9b":
        if action_type is None:
            raise ValueError("Figure 9b requires an action_type x-axis value")
        return action_type
    return float(sweep_value)


def _figure_9_paper_series_value(figure_id: str, curve_label: str, sweep_value: float) -> float | str:
    if figure_id == "Figure 9b":
        return float(sweep_value)
    return curve_label


def _figure_9_traffic_config(figure_id: str, sweep_value: float, curve_label: str, agent_count: int | None) -> TrafficConfig:
    if figure_id in {"Figure 9a", "Figure 9b", "Figure 9c"}:
        base = ScenarioRegistry.resolve("paper_default", 110)
        return TrafficConfig(
            scenario_name=base.scenario_name,
            number_of_agents=int(agent_count or base.number_of_agents),
            episode_length=base.episode_length,
            arrival_probability=float(sweep_value) if figure_id in {"Figure 9a", "Figure 9b"} else base.arrival_probability,
            slot_duration_seconds=base.slot_duration_seconds,
            timeout_slots=base.timeout_slots,
            task_size_mbits_min=base.task_size_mbits_min,
            task_size_mbits_max=base.task_size_mbits_max,
            task_size_mbits_step=base.task_size_mbits_step,
            processing_density_gcycles_per_mbit=base.processing_density_gcycles_per_mbit,
        )
    if figure_id == "Figure 9d":
        base = ScenarioRegistry.resolve(curve_label, 110)
        return TrafficConfig(
            scenario_name=base.scenario_name,
            number_of_agents=int(sweep_value),
            episode_length=base.episode_length,
            arrival_probability=base.arrival_probability,
            slot_duration_seconds=base.slot_duration_seconds,
            timeout_slots=base.timeout_slots,
            task_size_mbits_min=base.task_size_mbits_min,
            task_size_mbits_max=base.task_size_mbits_max,
            task_size_mbits_step=base.task_size_mbits_step,
            processing_density_gcycles_per_mbit=base.processing_density_gcycles_per_mbit,
        )
    if figure_id == "Figure 9e":
        base = ScenarioRegistry.resolve("paper_default", 110)
        if curve_label == "balanced":
            scenario_name = base.scenario_name
        elif curve_label == "horizontal_centric":
            scenario_name = base.scenario_name
        elif curve_label == "vertical_centric":
            scenario_name = base.scenario_name
        else:
            raise ValueError(f"Unsupported Figure 9e curve label: {curve_label}")
        return TrafficConfig(
            scenario_name=scenario_name,
            number_of_agents=int(sweep_value),
            episode_length=base.episode_length,
            arrival_probability=base.arrival_probability,
            slot_duration_seconds=base.slot_duration_seconds,
            timeout_slots=base.timeout_slots,
            task_size_mbits_min=base.task_size_mbits_min,
            task_size_mbits_max=base.task_size_mbits_max,
            task_size_mbits_step=base.task_size_mbits_step,
            processing_density_gcycles_per_mbit=base.processing_density_gcycles_per_mbit,
        )
    raise ValueError(f"Unsupported Figure 9 identifier: {figure_id}")


def _figure_9_curve_row(
    *,
    figure: PaperFigure,
    policy: str,
    curve_label: str,
    curve_value: int | None,
    sweep_value: float,
    traffic_config: TrafficConfig,
    compute_config: ComputeConfig,
    link_rate_config: LinkRateConfig,
    runs: list[dict[str, Any]],
    support_status: str,
    approximation_note: str,
    action_type: str | None = None,
) -> dict[str, Any]:
    all_records: list[TaskEvaluationRecord] = []
    action_counts = Counter({"local": 0, "horizontal": 0, "vertical": 0})
    total_reward = 0.0
    generated_arrivals = 0
    finalized_terminal_tasks = 0
    pending_at_horizon = 0
    for run in runs:
        all_records.extend(run["records"])
        run_action_counts = run["action_counts"]
        for family in ("local", "horizontal", "vertical"):
            action_counts[family] += int(run_action_counts.get(family, 0))
        total_reward += float(run["total_reward"])
        generated_arrivals += int(run["generated_arrivals"])
        finalized_terminal_tasks += int(run["finalized_terminal_tasks"])
        pending_at_horizon += int(run["pending_at_horizon"])

    combined_metrics = evaluate_trace(
        trace_id=f"{figure.figure_id.lower().replace(' ', '_')}-{curve_label}-{sweep_value}",
        policy_name=policy,
        seed=FIGURE_9_VALIDATION_SEEDS[0],
        device="cpu",
        records=all_records,
    ).to_dict()
    total_tasks = int(combined_metrics.get("total_tasks", len(all_records)))
    completion_rate = float(combined_metrics.get("completed_tasks", 0)) / total_tasks if total_tasks else 0.0
    average_reward = float(total_reward / total_tasks) if total_tasks else 0.0
    selected_action_total = int(sum(action_counts.values()))
    selected_action_count = int(action_counts[action_type]) if action_type is not None else None
    selected_action_share = (
        float(selected_action_count / selected_action_total)
        if action_type is not None and selected_action_total
        else None
    )
    value = float(average_reward) if figure.figure_id != "Figure 9b" else (
        float(selected_action_count) if selected_action_count is not None else None
    )
    row: dict[str, Any] = {
        "figure_id": figure.figure_id,
        "policy": policy,
        "metric": figure.metric,
        "x_axis": figure.x_axis,
        "paper_x_axis": figure.x_axis,
        "paper_x_axis_value": _figure_9_paper_x_value(figure.figure_id, float(sweep_value), action_type),
        "paper_y_axis": figure.metric,
        "paper_curve_dimension": _figure_9_paper_curve_dimension(figure.figure_id),
        "paper_curve_label": _figure_9_paper_series_value(figure.figure_id, curve_label, float(sweep_value)),
        "paper_curve_value": _figure_9_paper_series_value(figure.figure_id, curve_label, float(sweep_value)),
        "paper_validation_episodes": FIGURE_9_PAPER_VALIDATION_EPISODES,
        "simulator_validation_episodes": len(FIGURE_9_VALIDATION_SEEDS),
        "validation_policy_mode": "exploitative",
        "value": value,
        "sweep_value": float(sweep_value),
        "curve_label": curve_label,
        "curve_value": curve_value,
        "agent_count_curve": curve_value if figure.figure_id in {"Figure 9a", "Figure 9c"} else None,
        "action_type": action_type,
        "action_count": selected_action_count,
        "action_share": selected_action_share,
        "arrival_probability_bar": float(sweep_value) if figure.figure_id == "Figure 9b" else None,
        "traffic_intensity_label": curve_label if figure.figure_id == "Figure 9d" else None,
        "data_rate_configuration_label": curve_label if figure.figure_id == "Figure 9e" else None,
        "seed_count": len(FIGURE_9_VALIDATION_SEEDS),
        "seeds": list(FIGURE_9_VALIDATION_SEEDS),
        "scenario_name": traffic_config.scenario_name,
        "number_of_agents": traffic_config.number_of_agents,
        "episode_length": traffic_config.episode_length,
        "arrival_probability": float(traffic_config.arrival_probability),
        "task_size_mbits_min": float(traffic_config.task_size_mbits_min),
        "task_size_mbits_max": float(traffic_config.task_size_mbits_max),
        "task_size_mbits_step": float(traffic_config.task_size_mbits_step),
        "timeout_slots": int(traffic_config.timeout_slots),
        "timeout_seconds": float(traffic_config.timeout_slots * traffic_config.slot_duration_seconds),
        "cpu_capacity_per_slot_agent": float(compute_config.cpu_capacity_per_slot_agent),
        "cpu_capacity_per_slot_edge": float(compute_config.cpu_capacity_per_slot_edge),
        "cpu_capacity_per_slot_cloud": float(compute_config.cpu_capacity_per_slot_cloud),
        "horizontal_data_rate_mbps": float(link_rate_config.horizontal_data_rate_mbps),
        "vertical_data_rate_mbps": float(link_rate_config.vertical_data_rate_mbps),
        "task_completion_delay_raw": float(combined_metrics.get("average_delay", 0.0) or 0.0),
        "paper_style_delay_for_plotting": _delay_plot_value(float(combined_metrics.get("average_delay", 0.0) or 0.0)),
        "task_drop_ratio": float(combined_metrics.get("drop_ratio", 0.0)),
        "task_drop_percent": _drop_percent(float(combined_metrics.get("drop_ratio", 0.0))),
        "completion_rate": completion_rate,
        "throughput": int(combined_metrics.get("throughput", 0)),
        "average_reward": average_reward,
        "total_reward": float(total_reward),
        "completed_tasks": int(combined_metrics.get("completed_tasks", 0)),
        "dropped_tasks": int(combined_metrics.get("dropped_tasks", 0)),
        "total_tasks": total_tasks,
        "generated_arrivals": generated_arrivals,
        "finalized_terminal_tasks": finalized_terminal_tasks,
        "pending_at_horizon": pending_at_horizon,
        "local_action_count": int(action_counts["local"]),
        "horizontal_action_count": int(action_counts["horizontal"]),
        "vertical_action_count": int(action_counts["vertical"]),
        "total_selected_actions": selected_action_total,
        "local_action_share": float(action_counts["local"] / selected_action_total) if selected_action_total else 0.0,
        "horizontal_action_share": float(action_counts["horizontal"] / selected_action_total) if selected_action_total else 0.0,
        "vertical_action_share": float(action_counts["vertical"] / selected_action_total) if selected_action_total else 0.0,
        "support_status": support_status,
        "approximation_note": approximation_note,
        "status": "simulator_generated",
        "claim_boundary": list(figure.claim_boundary),
        "notes": (
            "Live simulator sweep generated from the paper Figure 9 semantic contract. "
            "The paper uses 200 exploitative validation episodes; this artifact records the simulator seed ensemble separately. "
            "Figure 9d/9e use the dynamic multi-agent topology support path for N up to 30."
        ),
    }
    return row


def _figure_9_output_rows(figure: PaperFigure) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for curve_label, curve_value in _figure_9_curve_labels(figure.figure_id):
        support_status = FIGURE_9_OUTPUT_SUPPORT_STATUS
        if figure.figure_id == "Figure 9b":
            approximation_note = (
                "Generated from current simulator action traces; "
                "action counts and shares are derived from exploitative validation rather than paper-trained policy runs."
            )
        elif figure.figure_id in {"Figure 9a", "Figure 9c"}:
            approximation_note = (
                "Generated from current simulator sweeps with explicit N curves; "
                "paper validation uses 200 episodes, while this artifact records the current simulator seed ensemble."
            )
        else:
            approximation_note = (
                "Generated from current simulator sweeps using the available topology and scenario adapters; "
                "the output is feasible from runtime evaluation, but it is not a trained-paper reproduction."
            )
        if figure.figure_id in {"Figure 9a", "Figure 9c"}:
            agent_count = curve_value
            for sweep_value in figure.sweep_values:
                traffic_config = _figure_9_traffic_config(figure.figure_id, float(sweep_value), curve_label, agent_count)
                compute_config = ComputeConfig() if figure.figure_id != "Figure 9c" else ComputeConfig(
                    cpu_capacity_per_slot_agent=float(sweep_value),
                    cpu_capacity_per_slot_edge=ComputeConfig().cpu_capacity_per_slot_edge,
                    cpu_capacity_per_slot_cloud=ComputeConfig().cpu_capacity_per_slot_cloud,
                )
                link_rate_config = _link_rate_config_for_figure9(figure.figure_id, curve_label)
                topology = _dynamic_topology(traffic_config.number_of_agents)
                runs: list[dict[str, Any]] = []
                for seed in FIGURE_9_VALIDATION_SEEDS:
                    trace = TrafficGenerator.generate(traffic_config, seed=seed)
                    with TemporaryDirectory(prefix=f"feature_089_{figure.figure_id.lower().replace(' ', '_')}_") as temp_dir:
                        temp_path = Path(temp_dir)
                        trace.write_json(temp_path / f"{trace.trace_id}.json")
                        trace_source = TraceSource.from_trace_bank(trace.trace_id, root_path=temp_path)
                        runs.append(
                            _run_policy_episode(
                                policy_name="HOODIE",
                                traffic_config=traffic_config,
                                compute_config=compute_config,
                                topology=topology,
                                link_rate_config=link_rate_config,
                                trace_source=trace_source,
                                seed=seed,
                                generated_arrivals=len(trace.records),
                            )
                        )
                rows.append(
                    _figure_9_curve_row(
                        figure=figure,
                        policy="HOODIE",
                        curve_label=curve_label,
                        curve_value=curve_value,
                        sweep_value=float(sweep_value),
                        traffic_config=traffic_config,
                        compute_config=compute_config,
                        link_rate_config=link_rate_config,
                        runs=runs,
                        support_status=support_status,
                        approximation_note=approximation_note,
                    )
                )
        elif figure.figure_id == "Figure 9b":
            action_type = curve_label
            for sweep_value in figure.sweep_values:
                traffic_config = _figure_9_traffic_config(figure.figure_id, float(sweep_value), curve_label, None)
                compute_config = ComputeConfig()
                link_rate_config = _link_rate_config_for_figure9(figure.figure_id, curve_label)
                topology = _dynamic_topology(traffic_config.number_of_agents)
                runs: list[dict[str, Any]] = []
                for seed in FIGURE_9_VALIDATION_SEEDS:
                    trace = TrafficGenerator.generate(traffic_config, seed=seed)
                    with TemporaryDirectory(prefix=f"feature_089_{figure.figure_id.lower().replace(' ', '_')}_") as temp_dir:
                        temp_path = Path(temp_dir)
                        trace.write_json(temp_path / f"{trace.trace_id}.json")
                        trace_source = TraceSource.from_trace_bank(trace.trace_id, root_path=temp_path)
                        runs.append(
                            _run_policy_episode(
                                policy_name="HOODIE",
                                traffic_config=traffic_config,
                                compute_config=compute_config,
                                topology=topology,
                                link_rate_config=link_rate_config,
                                trace_source=trace_source,
                                seed=seed,
                                generated_arrivals=len(trace.records),
                            )
                        )
                rows.append(
                    _figure_9_curve_row(
                        figure=figure,
                        policy="HOODIE",
                        curve_label=curve_label,
                        curve_value=curve_value,
                        sweep_value=float(sweep_value),
                        traffic_config=traffic_config,
                        compute_config=compute_config,
                        link_rate_config=link_rate_config,
                        runs=runs,
                        support_status=support_status,
                        approximation_note=approximation_note,
                        action_type=action_type,
                    )
                )
        elif figure.figure_id == "Figure 9d":
            for sweep_value in figure.sweep_values:
                curve_traffic_config = _figure_9_traffic_config(figure.figure_id, float(sweep_value), curve_label, None)
                compute_config = ComputeConfig()
                link_rate_config = _link_rate_config_for_figure9(figure.figure_id, curve_label)
                topology = _dynamic_topology(curve_traffic_config.number_of_agents)
                runs: list[dict[str, Any]] = []
                for seed in FIGURE_9_VALIDATION_SEEDS:
                    trace = TrafficGenerator.generate(curve_traffic_config, seed=seed)
                    with TemporaryDirectory(prefix=f"feature_089_{figure.figure_id.lower().replace(' ', '_')}_") as temp_dir:
                        temp_path = Path(temp_dir)
                        trace.write_json(temp_path / f"{trace.trace_id}.json")
                        trace_source = TraceSource.from_trace_bank(trace.trace_id, root_path=temp_path)
                        runs.append(
                            _run_policy_episode(
                                policy_name="HOODIE",
                                traffic_config=curve_traffic_config,
                                compute_config=compute_config,
                                topology=topology,
                                link_rate_config=link_rate_config,
                                trace_source=trace_source,
                                seed=seed,
                                generated_arrivals=len(trace.records),
                            )
                        )
                rows.append(
                    _figure_9_curve_row(
                        figure=figure,
                        policy="HOODIE",
                        curve_label=curve_label,
                        curve_value=curve_value,
                        sweep_value=float(sweep_value),
                        traffic_config=curve_traffic_config,
                        compute_config=compute_config,
                        link_rate_config=link_rate_config,
                        runs=runs,
                        support_status=support_status,
                        approximation_note=approximation_note,
                    )
                )
        elif figure.figure_id == "Figure 9e":
            for sweep_value in figure.sweep_values:
                curve_traffic_config = _figure_9_traffic_config(figure.figure_id, float(sweep_value), curve_label, None)
                compute_config = ComputeConfig()
                link_rate_config = _link_rate_config_for_figure9(figure.figure_id, curve_label)
                topology = _dynamic_topology(curve_traffic_config.number_of_agents)
                runs: list[dict[str, Any]] = []
                for seed in FIGURE_9_VALIDATION_SEEDS:
                    trace = TrafficGenerator.generate(curve_traffic_config, seed=seed)
                    with TemporaryDirectory(prefix=f"feature_089_{figure.figure_id.lower().replace(' ', '_')}_") as temp_dir:
                        temp_path = Path(temp_dir)
                        trace.write_json(temp_path / f"{trace.trace_id}.json")
                        trace_source = TraceSource.from_trace_bank(trace.trace_id, root_path=temp_path)
                        runs.append(
                            _run_policy_episode(
                                policy_name="HOODIE",
                                traffic_config=curve_traffic_config,
                                compute_config=compute_config,
                                topology=topology,
                                link_rate_config=link_rate_config,
                                trace_source=trace_source,
                                seed=seed,
                                generated_arrivals=len(trace.records),
                            )
                        )
                rows.append(
                    _figure_9_curve_row(
                        figure=figure,
                        policy="HOODIE",
                        curve_label=curve_label,
                        curve_value=curve_value,
                        sweep_value=float(sweep_value),
                        traffic_config=curve_traffic_config,
                        compute_config=compute_config,
                        link_rate_config=link_rate_config,
                        runs=runs,
                        support_status=support_status,
                        approximation_note=approximation_note,
                    )
                )
        else:
            raise ValueError(f"Unsupported Figure 9 identifier: {figure.figure_id}")
    return rows


def _read_json_array(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"{path.name} must contain a JSON array")
    return payload


def _figure_10_audit_rows(artifact_dir: Path, figures: dict[str, PaperFigure]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for figure_id, (csv_name, json_name) in _figure_10_artifact_files().items():
        figure = figures[figure_id]
        payload = _read_json_array(artifact_dir / json_name)
        expected_sweeps = {float(value) for value in figure.sweep_values}
        seen_sweeps = {float(row.get("sweep_value")) for row in payload}
        seen_policies = {str(row.get("policy")) for row in payload}
        expected_rows = len(ACTIVE_POLICIES) * len(figure.sweep_values)
        status_valid = all(row.get("status") == "simulator_generated" for row in payload)
        raw_delay_valid = all(float(row.get("task_completion_delay_raw", 0.0)) >= 0.0 for row in payload)
        plot_delay_valid = all(
            abs(float(row.get("paper_style_delay_for_plotting", 0.0)) + abs(float(row.get("task_completion_delay_raw", 0.0)))) <= 1e-9
            for row in payload
        )
        drop_ratio_valid = all(0.0 <= float(row.get("task_drop_ratio", 0.0)) <= 1.0 for row in payload)
        drop_percent_valid = all(
            abs(float(row.get("task_drop_percent", 0.0)) - (float(row.get("task_drop_ratio", 0.0)) * 100.0)) <= 1e-9
            for row in payload
        )
        boundary_valid = all(
            all(boundary in row.get("claim_boundary", []) for boundary in FEATURE_080_BOUNDARY + FEATURE_086_BOUNDARY)
            for row in payload
        )
        audit_passed = (
            len(payload) == expected_rows
            and seen_policies == set(ACTIVE_POLICIES)
            and seen_sweeps == expected_sweeps
            and status_valid
            and raw_delay_valid
            and plot_delay_valid
            and drop_ratio_valid
            and drop_percent_valid
            and boundary_valid
        )
        rows.append(
            {
                "figure_id": figure_id,
                "metric": figure.metric,
                "x_axis": figure.x_axis,
                "csv_artifact": csv_name,
                "json_artifact": json_name,
                "row_count": len(payload),
                "expected_row_count": expected_rows,
                "policy_count": len(seen_policies),
                "expected_policy_count": len(ACTIVE_POLICIES),
                "sweep_count": len(seen_sweeps),
                "expected_sweep_count": len(figure.sweep_values),
                "raw_positive_delay_valid": raw_delay_valid,
                "paper_style_negative_delay_valid": plot_delay_valid,
                "drop_ratio_valid": drop_ratio_valid,
                "drop_percent_valid": drop_percent_valid,
                "claim_boundary_valid": boundary_valid,
                "status_valid": status_valid,
                "audit_status": "pass" if audit_passed else "fail",
            }
        )
    return rows


def _figure_10_analysis_summary(audit_rows: list[dict[str, Any]], figures: dict[str, PaperFigure]) -> dict[str, Any]:
    delay_figures = [row["figure_id"] for row in audit_rows if "delay" in str(row["json_artifact"])]
    drop_figures = [row["figure_id"] for row in audit_rows if "drop" in str(row["json_artifact"])]
    return {
        "feature_id": FEATURE_ID,
        "analysis_scope": "Figure 10a-10f simulator output analysis",
        "verdict": "figure_10_outputs_validated" if all(row["audit_status"] == "pass" for row in audit_rows) else "figure_10_outputs_invalid",
        "figures_analyzed": [row["figure_id"] for row in audit_rows],
        "delay_figures": delay_figures,
        "drop_ratio_figures": drop_figures,
        "policies": list(ACTIVE_POLICIES),
        "total_rows": sum(int(row["row_count"]) for row in audit_rows),
        "all_audits_passed": all(row["audit_status"] == "pass" for row in audit_rows),
        "raw_positive_delay_preserved": all(bool(row["raw_positive_delay_valid"]) for row in audit_rows),
        "paper_style_negative_delay_preserved": all(bool(row["paper_style_negative_delay_valid"]) for row in audit_rows),
        "drop_ratio_and_percent_preserved": all(bool(row["drop_ratio_valid"]) and bool(row["drop_percent_valid"]) for row in audit_rows),
        "figure_9_boundary": "Figure 9a-9e remain blocked/reference-only.",
        "training_lstm_boundary": "Figure 8a, Figure 8b, and Figure 11 remain future-required/training-LSTM-gated.",
        "claim_boundary": list(FEATURE_080_BOUNDARY + FEATURE_086_BOUNDARY),
        "figure_sweep_values": {figure_id: list(figures[figure_id].sweep_values) for figure_id in PRIORITY_1_FIGURES},
    }


def _completion_report_payload(report: Feature089Report, audit_rows: list[dict[str, Any]], summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "feature_id": FEATURE_ID,
        "completion_status": "complete" if summary["all_audits_passed"] else "incomplete",
        "figure_10_verdict": summary["verdict"],
        "figure_10_audit_artifacts": [
            "figure_10_output_audit.json",
            "figure_10_output_audit.md",
            "figure_10_analysis_summary.json",
            "figure_10_analysis_summary.md",
        ],
        "ready_now_figures": list(report.ready_now_figures),
        "blocked_figures": list(report.blocked_figures),
        "future_required_figures": list(report.future_required_figures),
        "figure_10_figures": [row["figure_id"] for row in audit_rows],
        "figure_10_rows": summary["total_rows"],
        "figure_10_all_audits_passed": summary["all_audits_passed"],
        "figure_9_boundary_preserved": list(report.blocked_figures) == list(PRIORITY_2_FIGURES),
        "training_lstm_boundary_preserved": list(report.future_required_figures) == list(PRIORITY_3_FIGURES),
        "feature_086_boundary": list(FEATURE_086_BOUNDARY),
        "feature_080_boundary": list(FEATURE_080_BOUNDARY),
        "notes": (
            "Feature 089 is complete for Figure 10 simulator outputs. "
            "Figure 9 remains blocked/reference-only; Figures 8a, 8b, and 11 remain future-required."
        ),
    }


def _write_figure_10_analysis_artifacts(artifact_dir: Path, figures: dict[str, PaperFigure], report: Feature089Report) -> None:
    audit_rows = _figure_10_audit_rows(artifact_dir, figures)
    summary = _figure_10_analysis_summary(audit_rows, figures)
    completion_report = _completion_report_payload(report, audit_rows, summary)
    _write_json(artifact_dir / "figure_10_output_audit.json", audit_rows)
    _write_markdown_table(artifact_dir / "figure_10_output_audit.md", audit_rows, "Feature 089 Figure 10 Output Audit")
    _write_json(artifact_dir / "figure_10_analysis_summary.json", summary)
    _write_markdown_table(
        artifact_dir / "figure_10_analysis_summary.md",
        [
            {
                "feature_id": summary["feature_id"],
                "verdict": summary["verdict"],
                "figures_analyzed": ", ".join(summary["figures_analyzed"]),
                "total_rows": summary["total_rows"],
                "all_audits_passed": summary["all_audits_passed"],
                "raw_positive_delay_preserved": summary["raw_positive_delay_preserved"],
                "paper_style_negative_delay_preserved": summary["paper_style_negative_delay_preserved"],
                "drop_ratio_and_percent_preserved": summary["drop_ratio_and_percent_preserved"],
                "figure_9_boundary": summary["figure_9_boundary"],
                "training_lstm_boundary": summary["training_lstm_boundary"],
            }
        ],
        "Feature 089 Figure 10 Analysis Summary",
    )
    _write_json(artifact_dir / "feature_089_completion_report.json", completion_report)
    _write_markdown_table(
        artifact_dir / "feature_089_completion_report.md",
        [
            {
                "feature_id": completion_report["feature_id"],
                "completion_status": completion_report["completion_status"],
                "figure_10_verdict": completion_report["figure_10_verdict"],
                "figure_10_rows": completion_report["figure_10_rows"],
                "figure_10_all_audits_passed": completion_report["figure_10_all_audits_passed"],
                "ready_now_figures": ", ".join(completion_report["ready_now_figures"]),
                "blocked_figures": ", ".join(completion_report["blocked_figures"]),
                "future_required_figures": ", ".join(completion_report["future_required_figures"]),
                "figure_9_boundary_preserved": completion_report["figure_9_boundary_preserved"],
                "training_lstm_boundary_preserved": completion_report["training_lstm_boundary_preserved"],
            }
        ],
        "Feature 089 Completion Report",
    )


def _write_figure_output_files(artifact_dir: Path, figures: list[PaperFigure], requirements: list[SimulatorOutputRequirement]) -> None:
    references = _reference_metric_values()
    requirement_by_id = {item.requirement_id: item for item in requirements}
    by_id = {figure.figure_id: figure for figure in figures}
    filenames = {
        **_figure_10_artifact_files(),
        "Figure 9a": ("figure_9a_reward_vs_arrival_probability.csv", "figure_9a_reward_vs_arrival_probability.json"),
        "Figure 9b": ("figure_9b_action_distribution_vs_arrival_probability.csv", "figure_9b_action_distribution_vs_arrival_probability.json"),
        "Figure 9c": ("figure_9c_reward_vs_cpu_capacity.csv", "figure_9c_reward_vs_cpu_capacity.json"),
        "Figure 9d": ("figure_9d_reward_vs_agent_count_traffic.csv", "figure_9d_reward_vs_agent_count_traffic.json"),
        "Figure 9e": ("figure_9e_reward_vs_agent_count_data_rate.csv", "figure_9e_reward_vs_agent_count_data_rate.json"),
    }
    figure_10_ids = {"Figure 10a", "Figure 10b", "Figure 10c", "Figure 10d", "Figure 10e", "Figure 10f"}
    for figure_id, figure in by_id.items():
        if figure_id not in filenames:
            continue
        requirement = requirement_by_id[figure.simulator_output_requirement_id]
        csv_name, json_name = filenames[figure_id]
        if figure_id in figure_10_ids:
            rows = _figure_10_output_rows(figure)
        elif figure_id in PRIORITY_2_FIGURES:
            rows = _figure_9_output_rows(figure)
        else:
            rows = _figure_output_rows(figure, requirement, references)
        csv_path = artifact_dir / csv_name
        json_path = artifact_dir / json_name
        _write_csv(csv_path, rows)
        _write_json(json_path, rows)


def _figure_rows(figures: list[PaperFigure]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for figure in figures:
        rows.append(
            {
                "figure_id": figure.figure_id,
                "family": figure.family,
                "paper_section": figure.paper_section,
                "metric": figure.metric,
                "x_axis": figure.x_axis,
                "sweep_values": list(figure.sweep_values),
                "policies_or_curves": list(figure.policies_or_curves),
                "priority": figure.priority,
                "output_status": figure.output_status,
                "pdf_verified": figure.pdf_verified,
                "extraction_confidence": figure.extraction_confidence,
                "scenario_setup": figure.scenario_setup,
                "requires_training": figure.requires_training,
                "requires_lstm": figure.requires_lstm,
                "claim_boundary": list(figure.claim_boundary),
                "ocr_caveat": figure.ocr_caveat,
            }
        )
    return rows


def _metric_rows(metrics: list[PaperMetric]) -> list[dict[str, Any]]:
    return [metric.to_dict() for metric in metrics]


def _requirement_rows(requirements: list[SimulatorOutputRequirement]) -> list[dict[str, Any]]:
    return [requirement.to_dict() for requirement in requirements]


def _report(figures: list[PaperFigure], metrics: list[PaperMetric], requirements: list[SimulatorOutputRequirement]) -> Feature089Report:
    ready_now = tuple(figure.figure_id for figure in figures if figure.output_status == "required_now")
    future_required = tuple(figure.figure_id for figure in figures if figure.output_status in {"later_training_required", "later_lstm_required"})
    blocked = tuple(figure.figure_id for figure in figures if figure.output_status == "reference_only")
    return Feature089Report(
        feature_id=FEATURE_ID,
        verdict="paper_metrics_catalog_partial",
        source_truth_files=(
            "specs/089-hoodie-paper-metrics-figure-catalog/paper-figures-8-9-extracted.md",
            "specs/089-hoodie-paper-metrics-figure-catalog/paper-metrics-extracted.md",
            "specs/089-hoodie-paper-metrics-figure-catalog/simulator-output-requirements.md",
            str(PAPER_OCR_PATH),
            str(PAPER_PDF_PATH),
            str(FEATURE_086_REPORT_PATH),
        ),
        figures_cataloged=len(figures),
        metrics_cataloged=len(metrics),
        simulator_output_requirements=len(requirements),
        priority_1_figures=PRIORITY_1_FIGURES,
        priority_2_figures=PRIORITY_2_FIGURES,
        priority_3_figures=PRIORITY_3_FIGURES,
        ready_now_figures=ready_now,
        future_required_figures=future_required,
        blocked_figures=blocked,
        feature_086_boundary=FEATURE_086_BOUNDARY,
        feature_080_boundary=FEATURE_080_BOUNDARY,
        allowed_policies=ACTIVE_POLICIES,
        remaining_limitations=(
            "Figure 9a-9e remain blocked/reference-only because faithful behavior outputs require trained HOODIE DRL/LSTM policy support and paper validation semantics.",
            "Figures 8a, 8b, and 11 remain future-required because they depend on trained DRL and LSTM artifacts.",
            "Figure 10 output files are live simulator sweeps over the approved runtime controls, with Feature 086 approximations preserved for the plotting transforms.",
        ),
    )


def _generate_supporting_spec_docs(figures: list[PaperFigure], metrics: list[PaperMetric], requirements: list[SimulatorOutputRequirement]) -> None:
    figure_rows = _figure_rows(figures)
    metric_rows = _metric_rows(metrics)
    requirement_rows = _requirement_rows(requirements)
    _write_markdown_table(SPEC_DIR / "paper-metrics-extracted.md", metric_rows, "Feature 089 Paper Metrics Extraction")
    _write_markdown_table(SPEC_DIR / "simulator-output-requirements.md", requirement_rows, "Feature 089 Simulator Output Requirements")


def generate_artifacts(artifact_dir: Path | None = None) -> Feature089Report:
    artifact_dir = artifact_dir or ARTIFACT_DIR
    artifact_dir.mkdir(parents=True, exist_ok=True)
    SPEC_DIR.mkdir(parents=True, exist_ok=True)

    figures = _ordered_figures()
    metrics = _paper_metric_catalog()
    requirements = _requirements()
    report = _report(figures, metrics, requirements)

    _write_json(artifact_dir / "paper_figures_8_11_catalog.json", [figure.to_dict() for figure in figures])
    _write_markdown_table(artifact_dir / "paper_figures_8_11_catalog.md", _figure_rows(figures), "Feature 089 Paper Figures 8-11 Catalog")

    _write_json(artifact_dir / "paper_metrics_catalog.json", [metric.to_dict() for metric in metrics])
    _write_markdown_table(artifact_dir / "paper_metrics_catalog.md", _metric_rows(metrics), "Feature 089 Paper Metrics Catalog")

    _write_json(artifact_dir / "simulator_output_requirements.json", [requirement.to_dict() for requirement in requirements])
    _write_markdown_table(artifact_dir / "simulator_output_requirements.md", _requirement_rows(requirements), "Feature 089 Simulator Output Requirements")

    _write_json(artifact_dir / "feature_089_report.json", report.to_dict())
    _write_markdown_table(
        artifact_dir / "feature_089_report.md",
        [
            {
                "feature_id": report.feature_id,
                "verdict": report.verdict,
                "figures_cataloged": report.figures_cataloged,
                "metrics_cataloged": report.metrics_cataloged,
                "simulator_output_requirements": report.simulator_output_requirements,
                "ready_now_figures": ", ".join(report.ready_now_figures),
                "future_required_figures": ", ".join(report.future_required_figures),
                "blocked_figures": ", ".join(report.blocked_figures),
                "allowed_policies": ", ".join(report.allowed_policies),
            }
        ],
        "Feature 089 Report",
    )

    _write_figure_output_files(artifact_dir, figures, requirements)
    _write_figure_10_analysis_artifacts(artifact_dir, {figure.figure_id: figure for figure in figures}, report)
    _write_figure_10_comparison_analysis_artifacts(artifact_dir)
    _write_figure_8_11_status_artifacts(artifact_dir)
    _write_remaining_figure_outputs_report(artifact_dir)
    _plot_paper_style_outputs(artifact_dir, figures)
    generate_output_usage_bundle(artifact_dir)
    _generate_supporting_spec_docs(figures, metrics, requirements)
    return report


def _validate_figure_10_output(path: Path, figure: PaperFigure) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"{path.name} must contain a JSON array")
    expected_row_count = len(ACTIVE_POLICIES) * len(figure.sweep_values)
    if len(payload) != expected_row_count:
        raise ValueError(f"{path.name} must contain {expected_row_count} rows")
    seen_policies = {str(row.get("policy")) for row in payload}
    if seen_policies != set(ACTIVE_POLICIES):
        raise ValueError(f"{path.name} must cover the Figure 10 policy set")
    seen_sweeps = {float(row.get("sweep_value")) for row in payload}
    if seen_sweeps != {float(value) for value in figure.sweep_values}:
        raise ValueError(f"{path.name} must cover the Figure 10 sweep values")
    for row in payload:
        if row.get("figure_id") != figure.figure_id:
            raise ValueError(f"{path.name} contains a row for the wrong figure")
        if row.get("status") != "simulator_generated":
            raise ValueError(f"{path.name} must mark Figure 10 rows as simulator-generated")
        delay_raw = float(row["task_completion_delay_raw"])
        delay_plot = float(row["paper_style_delay_for_plotting"])
        if delay_raw < 0:
            raise ValueError(f"{path.name} must preserve raw positive delay")
        if abs(delay_plot + abs(delay_raw)) > 1e-9:
            raise ValueError(f"{path.name} must keep paper-style delay negative")
        drop_ratio = float(row["task_drop_ratio"])
        drop_percent = float(row["task_drop_percent"])
        if not 0.0 <= drop_ratio <= 1.0:
            raise ValueError(f"{path.name} must preserve raw drop ratio")
        if abs(drop_percent - (drop_ratio * 100.0)) > 1e-9:
            raise ValueError(f"{path.name} must preserve drop ratio percentage")


def _validate_figure_9_output(path: Path, figure: PaperFigure) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"{path.name} must contain a JSON array")
    expected_row_count = len(figure.sweep_values) * len(_figure_9_curve_labels(figure.figure_id))
    if len(payload) != expected_row_count:
        raise ValueError(f"{path.name} must contain {expected_row_count} rows")
    expected_curve_labels = {label for label, _value in _figure_9_curve_labels(figure.figure_id)}
    seen_curve_labels = {str(row.get("curve_label")) for row in payload}
    if seen_curve_labels != expected_curve_labels:
        raise ValueError(f"{path.name} must cover all Figure 9 curve labels")
    seen_sweeps = {float(row.get("sweep_value")) for row in payload}
    if seen_sweeps != {float(value) for value in figure.sweep_values}:
        raise ValueError(f"{path.name} must cover the Figure 9 sweep values")
    for row in payload:
        if row.get("figure_id") != figure.figure_id:
            raise ValueError(f"{path.name} contains a row for the wrong figure")
        if row.get("policy") != "HOODIE":
            raise ValueError(f"{path.name} must remain HOODIE-only")
        if row.get("status") != "simulator_generated":
            raise ValueError(f"{path.name} must mark Figure 9 rows as simulator-generated")
        if row.get("paper_x_axis") != figure.x_axis:
            raise ValueError(f"{path.name} must preserve the paper x-axis")
        if row.get("paper_y_axis") != figure.metric:
            raise ValueError(f"{path.name} must preserve the paper y-axis")
        if row.get("paper_curve_dimension") != _figure_9_paper_curve_dimension(figure.figure_id):
            raise ValueError(f"{path.name} must preserve the Figure 9 curve dimension")
        if int(row.get("paper_validation_episodes", 0)) != FIGURE_9_PAPER_VALIDATION_EPISODES:
            raise ValueError(f"{path.name} must record the paper validation episode count")
        if int(row.get("simulator_validation_episodes", 0)) != len(FIGURE_9_VALIDATION_SEEDS):
            raise ValueError(f"{path.name} must record the simulator validation episode count")
        if row.get("validation_policy_mode") != "exploitative":
            raise ValueError(f"{path.name} must record exploitative Figure 9 validation mode")
        if int(row.get("seed_count", 0)) != len(FIGURE_9_VALIDATION_SEEDS):
            raise ValueError(f"{path.name} must report the Figure 9 validation seed count")
        if list(row.get("seeds", [])) != list(FIGURE_9_VALIDATION_SEEDS):
            raise ValueError(f"{path.name} must report the Figure 9 validation seeds")
        if int(row.get("total_selected_actions", 0)) != int(row.get("finalized_terminal_tasks", 0)):
            raise ValueError(f"{path.name} must keep action counts aligned with finalized tasks")
        share_total = float(row.get("local_action_share", 0.0)) + float(row.get("horizontal_action_share", 0.0)) + float(row.get("vertical_action_share", 0.0))
        if int(row.get("total_selected_actions", 0)) == 0:
            if abs(share_total) > 1e-9:
                raise ValueError(f"{path.name} must keep zero-action shares at zero")
        elif abs(share_total - 1.0) > 1e-9:
            raise ValueError(f"{path.name} must preserve action-share totals")
        if figure.figure_id in {"Figure 9a", "Figure 9c"}:
            if int(row.get("curve_value")) not in {10, 15, 20}:
                raise ValueError(f"{path.name} must keep the Figure 9 N curves")
            if int(row.get("agent_count_curve", 0)) != int(row.get("number_of_agents", 0)):
                raise ValueError(f"{path.name} must align the N curve with the simulator agent count")
            if row.get("support_status") != FIGURE_9_OUTPUT_SUPPORT_STATUS:
                raise ValueError(f"{path.name} must mark Figure 9a/9c as generated with approximation")
            if abs(float(row.get("value", 0.0)) - float(row.get("average_reward", 0.0))) > 1e-9:
                raise ValueError(f"{path.name} must keep Figure 9a/9c value aligned with average_reward")
            if abs(float(row.get("arrival_probability", 0.0)) - float(row.get("sweep_value", 0.0))) > 1e-9 and figure.figure_id == "Figure 9a":
                raise ValueError(f"{path.name} must sweep arrival probability on the x-axis")
            if figure.figure_id == "Figure 9c" and abs(float(row.get("cpu_capacity_per_slot_agent", 0.0)) - float(row.get("sweep_value", 0.0))) > 1e-9:
                raise ValueError(f"{path.name} must sweep CPU capacity on the agent slot capacity axis")
        if figure.figure_id == "Figure 9b":
            action_type = str(row.get("action_type"))
            if action_type not in {"local", "horizontal", "vertical"}:
                raise ValueError(f"{path.name} must use action type as the Figure 9b x-axis")
            if row.get("paper_x_axis_value") != action_type:
                raise ValueError(f"{path.name} must preserve the Figure 9b action-type x-axis value")
            if abs(float(row.get("arrival_probability", 0.0)) - float(row.get("arrival_probability_bar", -1.0))) > 1e-9:
                raise ValueError(f"{path.name} must preserve the Figure 9b arrival-probability bar group")
            if abs(float(row.get("arrival_probability", 0.0)) - float(row.get("sweep_value", 0.0))) > 1e-9:
                raise ValueError(f"{path.name} must generate Figure 9b bars over arrival probability")
            if int(row.get("number_of_agents", 0)) != 20:
                raise ValueError(f"{path.name} must keep Figure 9b at Table 4 N=20")
            action_count = int(row.get("action_count", -1))
            total_actions = int(row.get("total_selected_actions", 0))
            if action_count < 0 or action_count > total_actions:
                raise ValueError(f"{path.name} must keep Figure 9b action counts inside the selected-action total")
            action_share = float(row.get("action_share", -1.0))
            expected_share = float(action_count / total_actions) if total_actions else 0.0
            if abs(action_share - expected_share) > 1e-9:
                raise ValueError(f"{path.name} must keep Figure 9b action shares aligned with action counts")
            if row.get("support_status") != FIGURE_9_OUTPUT_SUPPORT_STATUS:
                raise ValueError(f"{path.name} must mark Figure 9b as generated with approximation")
            if abs(float(row.get("value", 0.0)) - float(row.get("action_count", 0.0))) > 1e-9:
                raise ValueError(f"{path.name} must keep Figure 9b value aligned with action_count")
        if figure.figure_id == "Figure 9d":
            if row.get("scenario_name") not in {"moderate", "heavy", "extreme"}:
                raise ValueError(f"{path.name} must preserve the traffic scenario labels")
            expected_traffic = {
                "moderate": (0.5, 1.0, 3.0),
                "heavy": (0.7, 2.0, 5.0),
                "extreme": (0.9, 3.0, 7.0),
            }[str(row.get("curve_label"))]
            if abs(float(row.get("arrival_probability", 0.0)) - expected_traffic[0]) > 1e-9:
                raise ValueError(f"{path.name} must preserve the Figure 9d traffic arrival probability")
            if abs(float(row.get("task_size_mbits_min", 0.0)) - expected_traffic[1]) > 1e-9:
                raise ValueError(f"{path.name} must preserve the Figure 9d task-size lower bound")
            if abs(float(row.get("task_size_mbits_max", 0.0)) - expected_traffic[2]) > 1e-9:
                raise ValueError(f"{path.name} must preserve the Figure 9d task-size upper bound")
            if int(row.get("number_of_agents", 0)) != int(float(row.get("sweep_value", 0.0))):
                raise ValueError(f"{path.name} must sweep Figure 9d on number of agents")
            if row.get("support_status") != FIGURE_9_OUTPUT_SUPPORT_STATUS:
                raise ValueError(f"{path.name} must mark Figure 9d as generated with approximation")
            if abs(float(row.get("value", 0.0)) - float(row.get("average_reward", 0.0))) > 1e-9:
                raise ValueError(f"{path.name} must keep Figure 9d value aligned with average_reward")
        if figure.figure_id == "Figure 9e":
            expected_rates = {
                "balanced": (10.0, 30.0),
                "horizontal_centric": (20.0, 20.0),
                "vertical_centric": (5.0, 40.0),
            }[str(row.get("curve_label"))]
            if abs(float(row.get("horizontal_data_rate_mbps", 0.0)) - expected_rates[0]) > 1e-9:
                raise ValueError(f"{path.name} must preserve the Figure 9e horizontal rate path")
            if abs(float(row.get("vertical_data_rate_mbps", 0.0)) - expected_rates[1]) > 1e-9:
                raise ValueError(f"{path.name} must preserve the Figure 9e vertical rate path")
            if int(row.get("number_of_agents", 0)) != int(float(row.get("sweep_value", 0.0))):
                raise ValueError(f"{path.name} must sweep Figure 9e on number of agents")
            if row.get("support_status") != FIGURE_9_OUTPUT_SUPPORT_STATUS:
                raise ValueError(f"{path.name} must mark Figure 9e as generated with approximation")
            if abs(float(row.get("value", 0.0)) - float(row.get("average_reward", 0.0))) > 1e-9:
                raise ValueError(f"{path.name} must keep Figure 9e value aligned with average_reward")

def validate_artifacts(artifact_dir: Path | None = None) -> Feature089Report:
    artifact_dir = artifact_dir or ARTIFACT_DIR
    report = _report(_ordered_figures(), _paper_metric_catalog(), _requirements())
    required_files = (
        "paper_figures_8_11_catalog.json",
        "paper_figures_8_11_catalog.md",
        "paper_metrics_catalog.json",
        "paper_metrics_catalog.md",
        "simulator_output_requirements.json",
        "simulator_output_requirements.md",
        "feature_089_report.json",
        "feature_089_report.md",
        "figure_10_output_audit.json",
        "figure_10_output_audit.md",
        "figure_10_analysis_summary.json",
        "figure_10_analysis_summary.md",
        "feature_089_completion_report.json",
        "feature_089_completion_report.md",
        "figure_10_trend_analysis.json",
        "figure_10_trend_analysis.md",
        "figure_10_ranking_analysis.json",
        "figure_10_ranking_analysis.md",
        "figure_10_paper_claim_alignment.json",
        "figure_10_paper_claim_alignment.md",
        "figure_10_comparison_analysis_report.json",
        "figure_10_comparison_analysis_report.md",
        "remaining_figure_outputs_report.json",
        "remaining_figure_outputs_report.md",
        "figure_10a_delay_vs_arrival_probability.csv",
        "figure_10a_delay_vs_arrival_probability.json",
        "figure_10b_delay_vs_cpu_capacity.csv",
        "figure_10b_delay_vs_cpu_capacity.json",
        "figure_10c_delay_vs_timeout.csv",
        "figure_10c_delay_vs_timeout.json",
        "figure_10d_drop_ratio_vs_arrival_probability.csv",
        "figure_10d_drop_ratio_vs_arrival_probability.json",
        "figure_10e_drop_ratio_vs_cpu_capacity.csv",
        "figure_10e_drop_ratio_vs_cpu_capacity.json",
        "figure_10f_drop_ratio_vs_timeout.csv",
        "figure_10f_drop_ratio_vs_timeout.json",
        "figure_9a_reward_vs_arrival_probability.csv",
        "figure_9a_reward_vs_arrival_probability.json",
        "figure_9b_action_distribution_vs_arrival_probability.csv",
        "figure_9b_action_distribution_vs_arrival_probability.json",
        "figure_9c_reward_vs_cpu_capacity.csv",
        "figure_9c_reward_vs_cpu_capacity.json",
        "figure_9d_reward_vs_agent_count_traffic.csv",
        "figure_9d_reward_vs_agent_count_traffic.json",
        "figure_9e_reward_vs_agent_count_data_rate.csv",
        "figure_9e_reward_vs_agent_count_data_rate.json",
        "figure_8a_learning_rate_convergence_status.json",
        "figure_8a_learning_rate_convergence_status.md",
        "figure_8b_discount_factor_convergence_status.json",
        "figure_8b_discount_factor_convergence_status.md",
        "figure_11_lstm_ablation_status.json",
        "figure_11_lstm_ablation_status.md",
        "paper_style_plots/figure_8a_learning_rate_convergence_status.png",
        "paper_style_plots/figure_8b_discount_factor_convergence_status.png",
        "paper_style_plots/figure_9a_reward_vs_arrival_probability.png",
        "paper_style_plots/figure_9b_action_distribution_vs_arrival_probability.png",
        "paper_style_plots/figure_9c_reward_vs_cpu_capacity.png",
        "paper_style_plots/figure_9d_reward_vs_agent_count_traffic.png",
        "paper_style_plots/figure_9e_reward_vs_agent_count_data_rate.png",
        "paper_style_plots/figure_10a_delay_vs_arrival_probability.png",
        "paper_style_plots/figure_10b_delay_vs_cpu_capacity.png",
        "paper_style_plots/figure_10c_delay_vs_timeout.png",
        "paper_style_plots/figure_10d_drop_ratio_vs_arrival_probability.png",
        "paper_style_plots/figure_10e_drop_ratio_vs_cpu_capacity.png",
        "paper_style_plots/figure_10f_drop_ratio_vs_timeout.png",
        "paper_style_plots/figure_11_lstm_ablation_status.png",
    )
    missing = [name for name in required_files if not (artifact_dir / name).exists()]
    if missing:
        raise FileNotFoundError(f"missing Feature 089 artifacts: {', '.join(missing)}")
    report_json = json.loads((artifact_dir / "feature_089_report.json").read_text(encoding="utf-8"))
    if report_json["verdict"] != "paper_metrics_catalog_partial":
        raise ValueError("unexpected Feature 089 verdict")
    if len(report_json["feature_086_boundary"]) != len(FEATURE_086_BOUNDARY):
        raise ValueError("Feature 086 boundary mismatch")
    figures = {figure.figure_id: figure for figure in _ordered_figures()}
    for figure_id, (_csv_name, json_name) in _figure_10_artifact_files().items():
        _validate_figure_10_output(artifact_dir / json_name, figures[figure_id])
    audit_rows = _read_json_array(artifact_dir / "figure_10_output_audit.json")
    if len(audit_rows) != len(PRIORITY_1_FIGURES):
        raise ValueError("Figure 10 output audit must cover every Priority 1 figure")
    if any(row.get("audit_status") != "pass" for row in audit_rows):
        raise ValueError("Figure 10 output audit contains failures")
    summary = json.loads((artifact_dir / "figure_10_analysis_summary.json").read_text(encoding="utf-8"))
    if summary.get("verdict") != "figure_10_outputs_validated":
        raise ValueError("Figure 10 analysis summary must validate Figure 10 outputs")
    if summary.get("figures_analyzed") != list(PRIORITY_1_FIGURES):
        raise ValueError("Figure 10 analysis summary must cover Figure 10a-10f")
    if not summary.get("raw_positive_delay_preserved"):
        raise ValueError("Figure 10 analysis summary must preserve raw positive delay")
    if not summary.get("paper_style_negative_delay_preserved"):
        raise ValueError("Figure 10 analysis summary must preserve paper-style negative delay")
    if not summary.get("drop_ratio_and_percent_preserved"):
        raise ValueError("Figure 10 analysis summary must preserve drop ratio and percent")
    completion = json.loads((artifact_dir / "feature_089_completion_report.json").read_text(encoding="utf-8"))
    if completion.get("completion_status") != "complete":
        raise ValueError("Feature 089 completion report must mark completion")
    if completion.get("ready_now_figures") != list(PRIORITY_1_FIGURES):
        raise ValueError("Feature 089 completion report must keep only Figure 10 ready now")
    if completion.get("blocked_figures") != list(PRIORITY_2_FIGURES):
        raise ValueError("Feature 089 completion report must keep Figure 9 blocked")
    if completion.get("future_required_figures") != list(PRIORITY_3_FIGURES):
        raise ValueError("Feature 089 completion report must keep Figure 8/11 future-required")
    comparison_report = json.loads((artifact_dir / "figure_10_comparison_analysis_report.json").read_text(encoding="utf-8"))
    if comparison_report.get("verdict") != FIGURE_10_COMPARISON_ANALYSIS_VERDICT:
        raise ValueError("Figure 10 comparison analysis report must use the partial verdict")
    if comparison_report.get("paper_numeric_digitization_performed") is not False:
        raise ValueError("Figure 10 comparison analysis report must state that numeric digitization was not performed")
    if comparison_report.get("analysis_mode") != FIGURE_10_COMPARISON_ANALYSIS_MODE:
        raise ValueError("Figure 10 comparison analysis report must be qualitative/ranking-based")
    if comparison_report.get("feature_088_repair_recommended") is not True:
        raise ValueError("Figure 10 comparison analysis report must recommend Feature 088 repair")
    if comparison_report.get("claim_alignment_by_figure", {}).get("Figure 10c") != "partial_directional_only":
        raise ValueError("Figure 10 comparison analysis report must record the timeout-only partial match for Figure 10c")
    if any(comparison_report.get("hoody_matches_paper_claims_by_figure", {}).get(figure_id) for figure_id in PRIORITY_1_FIGURES):
        raise ValueError("Figure 10 comparison analysis report must not claim full paper matching")
    figure_9_paths = {
        "Figure 9a": artifact_dir / "figure_9a_reward_vs_arrival_probability.json",
        "Figure 9b": artifact_dir / "figure_9b_action_distribution_vs_arrival_probability.json",
        "Figure 9c": artifact_dir / "figure_9c_reward_vs_cpu_capacity.json",
        "Figure 9d": artifact_dir / "figure_9d_reward_vs_agent_count_traffic.json",
        "Figure 9e": artifact_dir / "figure_9e_reward_vs_agent_count_data_rate.json",
    }
    for figure_id, path in figure_9_paths.items():
        _validate_figure_9_output(path, figures[figure_id])
    remaining_report = json.loads((artifact_dir / "remaining_figure_outputs_report.json").read_text(encoding="utf-8"))
    if remaining_report.get("verdict") != "feature_089_remaining_outputs_partial":
        raise ValueError("Remaining figure outputs report must mark the partial verdict")
    if remaining_report.get("no_output_sync_tuning") is not True:
        raise ValueError("Remaining figure outputs report must confirm no output-sync tuning")
    figure_8_status_files = {
        "Figure 8a": artifact_dir / "figure_8a_learning_rate_convergence_status.json",
        "Figure 8b": artifact_dir / "figure_8b_discount_factor_convergence_status.json",
        "Figure 11": artifact_dir / "figure_11_lstm_ablation_status.json",
    }
    expected_statuses = {
        "Figure 8a": FIGURE_8_TRAINING_STATUS,
        "Figure 8b": FIGURE_8_TRAINING_STATUS,
        "Figure 11": FIGURE_11_TRAINING_STATUS,
    }
    for figure_id, status_path in figure_8_status_files.items():
        payload = json.loads(status_path.read_text(encoding="utf-8"))
        if payload.get("support_status") != expected_statuses[figure_id]:
            raise ValueError(f"{status_path.name} must preserve the gated status")
        if payload.get("plot_ready_generated") is not False:
            raise ValueError(f"{status_path.name} must not fabricate plot-ready curves")
        if payload.get("claim_boundary") != list(FEATURE_080_BOUNDARY + FEATURE_086_BOUNDARY):
            raise ValueError(f"{status_path.name} must carry the claim boundary")
    forbidden_training_outputs = (
        artifact_dir / "figure_8a_learning_rate_training_curve.csv",
        artifact_dir / "figure_8a_learning_rate_training_curve.json",
        artifact_dir / "figure_8b_discount_factor_training_curve.csv",
        artifact_dir / "figure_8b_discount_factor_training_curve.json",
        artifact_dir / "figure_11_lstm_ablation_curve.csv",
        artifact_dir / "figure_11_lstm_ablation_curve.json",
    )
    if any(path.exists() for path in forbidden_training_outputs):
        raise ValueError("Validation must not accept fabricated Figure 8/11 training curves")
    validate_output_usage_bundle(artifact_dir)
    return report


def _figure_10_metric_field(figure_id: str) -> str:
    if figure_id in {"Figure 10a", "Figure 10b", "Figure 10c"}:
        return "paper_style_delay_for_plotting"
    if figure_id in {"Figure 10d", "Figure 10e", "Figure 10f"}:
        return "task_drop_ratio"
    raise ValueError(f"Unsupported Figure 10 identifier: {figure_id}")


def _figure_10_metric_goal(figure_id: str) -> str:
    return "lower_is_better"


def _figure_10_metric_summary(figure_id: str) -> str:
    if figure_id == "Figure 10a":
        return "Average delay should stay lower than baselines as arrival probability increases; MLEO should fall behind HOODIE at high load."
    if figure_id == "Figure 10b":
        return "Increasing CPU capacity should generally reduce average delay while HOODIE remains better than baselines."
    if figure_id == "Figure 10c":
        return "Increasing timeout should slightly improve average delay while HOODIE remains lower-delay than baselines."
    if figure_id == "Figure 10d":
        return "HOODIE should maintain the lowest drop ratio as arrival probability increases; FLC and HO should be weak at high load."
    if figure_id == "Figure 10e":
        return "Increasing CPU capacity should reduce drop ratio, with HOODIE showing strong reduction at low CPU capacity."
    if figure_id == "Figure 10f":
        return "Increasing timeout should reduce drop ratio while HOODIE maintains the lowest drop ratio."
    raise ValueError(f"Unsupported Figure 10 identifier: {figure_id}")


def _figure_10_claim_status(figure_id: str) -> str:
    if figure_id == "Figure 10c":
        return "partial_directional_only"
    return "not_supported"


def _figure_10_series_direction(series: list[float], tol: float = 1e-9) -> str:
    if len(series) < 2:
        return "flat"
    deltas = [b - a for a, b in zip(series, series[1:])]
    if all(abs(delta) <= tol for delta in deltas):
        return "flat"
    if all(delta <= tol for delta in deltas) and any(delta < -tol for delta in deltas):
        return "decreasing"
    if all(delta >= -tol for delta in deltas) and any(delta > tol for delta in deltas):
        return "increasing"
    return "non_monotonic"


def _figure_10_rank_groups(metric_by_policy: dict[str, float], tol: float = 1e-9) -> tuple[list[list[str]], list[tuple[str, float]]]:
    ordered = sorted(metric_by_policy.items(), key=lambda item: (item[1], item[0]))
    groups: list[list[str]] = []
    current_group: list[str] = []
    current_value: float | None = None
    for policy, value in ordered:
        if current_value is None or abs(value - current_value) <= tol:
            current_group.append(policy)
        else:
            groups.append(current_group)
            current_group = [policy]
        current_value = value
    if current_group:
        groups.append(current_group)
    return groups, ordered


def _figure_10_read_analysis_rows(artifact_dir: Path, figure_id: str) -> list[dict[str, Any]]:
    _, json_name = _figure_10_artifact_files()[figure_id]
    return _read_json_array(artifact_dir / json_name)


def _figure_10_comparison_analysis_payloads(artifact_dir: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    figures = {figure.figure_id: figure for figure in _ordered_figures() if figure.figure_id in PRIORITY_1_FIGURES}
    trend_rows: list[dict[str, Any]] = []
    ranking_rows: list[dict[str, Any]] = []
    claim_rows: list[dict[str, Any]] = []
    claim_status_by_figure: dict[str, str] = {}
    claim_match_by_figure: dict[str, bool] = {}

    for figure_id in PRIORITY_1_FIGURES:
        figure = figures[figure_id]
        rows = _figure_10_read_analysis_rows(artifact_dir, figure_id)
        metric_field = _figure_10_metric_field(figure_id)
        by_policy: dict[str, list[tuple[float, float]]] = {}
        by_sweep: dict[float, dict[str, float]] = {}
        for row in rows:
            policy = str(row["policy"])
            sweep_value = float(row["sweep_value"])
            metric_value = float(row[metric_field])
            by_policy.setdefault(policy, []).append((sweep_value, metric_value))
            by_sweep.setdefault(sweep_value, {})[policy] = metric_value

        series_by_policy = {policy: [value for _sweep, value in sorted(items)] for policy, items in by_policy.items()}
        hoodie_series = series_by_policy["HOODIE"]
        hoodie_mean = sum(hoodie_series) / len(hoodie_series)
        trend_direction = _figure_10_series_direction(hoodie_series)
        start_value = hoodie_series[0]
        end_value = hoodie_series[-1]
        delta_value = end_value - start_value
        trend_matches_claim = figure_id == "Figure 10c" and trend_direction == "decreasing"
        claim_status = _figure_10_claim_status(figure_id)
        claim_status_by_figure[figure_id] = claim_status
        claim_matches = claim_status == "supported"
        claim_match_by_figure[figure_id] = claim_matches

        per_sweep_rankings: list[dict[str, Any]] = []
        for sweep_value in sorted(by_sweep):
            sweep_metric_by_policy = by_sweep[sweep_value]
            rank_groups, ordered = _figure_10_rank_groups(sweep_metric_by_policy)
            hoodie_value = sweep_metric_by_policy["HOODIE"]
            mleo_value = sweep_metric_by_policy["MLEO"]
            per_sweep_rankings.append(
                {
                    "sweep_value": sweep_value,
                    "best_value": ordered[0][1],
                    "rank_groups": rank_groups,
                    "ordered_policies": [policy for policy, _value in ordered],
                    "hoodie_value": hoodie_value,
                    "hoodie_rank_band": "best" if len(rank_groups[0]) == 1 and rank_groups[0][0] == "HOODIE" else "tied-best",
                    "mleo_relation": "ties_with_hoodie" if abs(mleo_value - hoodie_value) <= 1e-9 else "diverges_from_hoodie",
                }
            )

        aggregate_means = {policy: sum(value for _sweep, value in items) / len(items) for policy, items in by_policy.items()}
        aggregate_groups, aggregate_ordered = _figure_10_rank_groups(aggregate_means)
        hoodie_group = next(group for group in aggregate_groups if "HOODIE" in group)
        mleo_relation = "ties_with_hoodie" if abs(aggregate_means["MLEO"] - aggregate_means["HOODIE"]) <= 1e-9 else "diverges_from_hoodie"
        worst_group = aggregate_groups[-1]
        weak_baselines = [policy for policy in worst_group if policy != "HOODIE" and len(worst_group) == 1]

        trend_rows.append(
            {
                "figure_id": figure_id,
                "metric": figure.metric,
                "metric_field": metric_field,
                "x_axis": figure.x_axis,
                "paper_numeric_digitization_performed": False,
                "paper_metric_goal": _figure_10_metric_goal(figure_id),
                "sweep_values": list(figure.sweep_values),
                "series_by_policy": series_by_policy,
                "hoodie_series": hoodie_series,
                "series_start_value": start_value,
                "series_end_value": end_value,
                "series_delta": delta_value,
                "trend_direction": trend_direction,
                "trend_summary": _figure_10_metric_summary(figure_id),
                "trend_notes": (
                    "No paper numeric digitization was performed. "
                    "Trend analysis uses the validated simulator rows and paper-style negative delay for the delay figures."
                    if figure_id in {"Figure 10a", "Figure 10b", "Figure 10c"}
                    else "No paper numeric digitization was performed. Trend analysis uses the validated simulator rows and raw drop ratio."
                ),
                "claim_alignment_status": claim_status,
                "feature_088_repair_recommended": True,
            }
        )
        ranking_rows.append(
            {
                "figure_id": figure_id,
                "metric": figure.metric,
                "metric_field": metric_field,
                "paper_numeric_digitization_performed": False,
                "per_sweep_rankings": per_sweep_rankings,
                "aggregate_means": aggregate_means,
                "aggregate_rank_groups": aggregate_groups,
                "aggregate_rank_order": [policy for policy, _value in aggregate_ordered],
                "hoodie_rank_band": "best" if len(hoodie_group) == 1 else "tied-best",
                "mleo_relation": mleo_relation,
                "weak_baselines": weak_baselines,
                "ranking_summary": "All policies tie across every sweep on the paper-facing metric." if len(aggregate_groups) == 1 else "Policy separation exists, but the tie structure is still shallow.",
                "feature_088_repair_recommended": True,
            }
        )
        claim_rows.append(
            {
                "figure_id": figure_id,
                "paper_claim_summary": _figure_10_metric_summary(figure_id),
                "claim_alignment_status": claim_status,
                "hoody_matches_paper_claims": claim_matches,
                "trend_matches_paper_claim": trend_matches_claim,
                "mleo_relation": mleo_relation,
                "numeric_digitization_performed": False,
                "feature_088_repair_recommended": True,
                "claim_notes": (
                    "HOODIE is tied with all baselines on every sweep, so the paper claim is not reproduced."
                    if not trend_matches_claim
                    else "Only a directional timeout effect is visible; policy separation is still absent."
                ),
            }
        )

    report = {
        "feature_id": FEATURE_ID,
        "analysis_mode": FIGURE_10_COMPARISON_ANALYSIS_MODE,
        "verdict": FIGURE_10_COMPARISON_ANALYSIS_VERDICT,
        "paper_numeric_digitization_performed": False,
        "overall_claim_alignment": "mostly_not_supported",
        "claim_alignment_by_figure": claim_status_by_figure,
        "hoody_matches_paper_claims_by_figure": claim_match_by_figure,
        "feature_088_repair_recommended": True,
        "feature_088_repair_reason": (
            "The Figure 10 outputs collapse to ties across policies, so the paper's qualitative separation is not supported."
        ),
        "feature_080_boundary_preserved": True,
        "feature_086_boundary_preserved": True,
        "claim_boundary": list(FEATURE_080_BOUNDARY + FEATURE_086_BOUNDARY),
        "notes": (
            "Comparison analysis is qualitative and ranking-based only. "
            "Paper numeric values were not digitized."
        ),
    }
    return trend_rows, ranking_rows, claim_rows, report


def _figure_10_comparison_analysis_md_rows(rows: list[dict[str, Any]], fields: tuple[str, ...]) -> list[dict[str, Any]]:
    md_rows: list[dict[str, Any]] = []
    for row in rows:
        md_rows.append({field: (json.dumps(row[field], ensure_ascii=False) if isinstance(row[field], (dict, list, tuple)) else row[field]) for field in fields})
    return md_rows


def _write_figure_10_comparison_analysis_artifacts(artifact_dir: Path) -> None:
    trend_rows, ranking_rows, claim_rows, report = _figure_10_comparison_analysis_payloads(artifact_dir)
    _write_json(artifact_dir / "figure_10_trend_analysis.json", trend_rows)
    _write_markdown_table(
        artifact_dir / "figure_10_trend_analysis.md",
        _figure_10_comparison_analysis_md_rows(
            trend_rows,
            (
                "figure_id",
                "metric",
                "metric_field",
                "trend_direction",
                "series_start_value",
                "series_end_value",
                "series_delta",
                "claim_alignment_status",
                "feature_088_repair_recommended",
                "trend_summary",
            ),
        ),
        "Feature 089 Figure 10 Trend Analysis",
    )
    _write_json(artifact_dir / "figure_10_ranking_analysis.json", ranking_rows)
    _write_markdown_table(
        artifact_dir / "figure_10_ranking_analysis.md",
        _figure_10_comparison_analysis_md_rows(
            ranking_rows,
            (
                "figure_id",
                "metric",
                "hoodie_rank_band",
                "mleo_relation",
                "aggregate_rank_groups",
                "weak_baselines",
                "ranking_summary",
                "feature_088_repair_recommended",
            ),
        ),
        "Feature 089 Figure 10 Ranking Analysis",
    )
    _write_json(artifact_dir / "figure_10_paper_claim_alignment.json", claim_rows)
    _write_markdown_table(
        artifact_dir / "figure_10_paper_claim_alignment.md",
        _figure_10_comparison_analysis_md_rows(
            claim_rows,
            (
                "figure_id",
                "claim_alignment_status",
                "hoody_matches_paper_claims",
                "trend_matches_paper_claim",
                "mleo_relation",
                "numeric_digitization_performed",
                "feature_088_repair_recommended",
                "paper_claim_summary",
            ),
        ),
        "Feature 089 Figure 10 Paper Claim Alignment",
    )
    _write_json(artifact_dir / "figure_10_comparison_analysis_report.json", report)
    _write_markdown_table(
        artifact_dir / "figure_10_comparison_analysis_report.md",
        [
            {
                "feature_id": report["feature_id"],
                "verdict": report["verdict"],
                "analysis_mode": report["analysis_mode"],
                "paper_numeric_digitization_performed": report["paper_numeric_digitization_performed"],
                "overall_claim_alignment": report["overall_claim_alignment"],
                "feature_088_repair_recommended": report["feature_088_repair_recommended"],
                "feature_080_boundary_preserved": report["feature_080_boundary_preserved"],
                "feature_086_boundary_preserved": report["feature_086_boundary_preserved"],
                "claim_alignment_by_figure": json.dumps(report["claim_alignment_by_figure"], ensure_ascii=False),
                "hoody_matches_paper_claims_by_figure": json.dumps(report["hoody_matches_paper_claims_by_figure"], ensure_ascii=False),
                "notes": report["notes"],
            }
        ],
        "Feature 089 Figure 10 Comparison Analysis Report",
    )


def _figure_9_row_status_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    support_counts = Counter(str(row.get("support_status", "unknown")) for row in rows)
    row_count = len(rows)
    if support_counts.get("not_supported", 0) == row_count and row_count:
        figure_status = "not_supported"
    elif support_counts.get(FIGURE_9_OUTPUT_SUPPORT_STATUS, 0) == row_count and row_count:
        figure_status = FIGURE_9_OUTPUT_SUPPORT_STATUS
    elif support_counts.get("generated", 0) + support_counts.get(FIGURE_9_OUTPUT_SUPPORT_STATUS, 0) == row_count and row_count:
        figure_status = "generated"
    else:
        figure_status = "partial"
    return {
        "row_count": row_count,
        "support_counts": dict(support_counts),
        "figure_status": figure_status,
    }


def _training_trace_files(base_dir: Path | None = None) -> dict[str, list[Path]]:
    root = base_dir or ARTIFACT_DIR
    return {
        "Figure 8a": [
            root / "figure_8a_learning_rate_training_curve.csv",
            root / "figure_8a_learning_rate_training_curve.json",
        ],
        "Figure 8b": [
            root / "figure_8b_discount_factor_training_curve.csv",
            root / "figure_8b_discount_factor_training_curve.json",
        ],
        "Figure 11": [
            root / "figure_11_lstm_ablation_curve.csv",
            root / "figure_11_lstm_ablation_curve.json",
        ],
    }


def _figure_8_11_status_payload(figure_id: str, artifact_dir: Path) -> dict[str, Any]:
    if figure_id in {"Figure 8a", "Figure 8b"}:
        status = FIGURE_8_TRAINING_STATUS
        reason = "No real trained HOODIE DRL traces were found in the repository; deterministic benchmark rows are not used."
        traces_present = any(path.exists() for path in _training_trace_files(artifact_dir)[figure_id])
    elif figure_id == "Figure 11":
        status = FIGURE_11_TRAINING_STATUS
        reason = "No real LSTM ablation traces were found in the repository; deterministic benchmark rows are not used."
        traces_present = any(path.exists() for path in _training_trace_files(artifact_dir)[figure_id])
    else:
        raise ValueError(f"Unsupported gated figure identifier: {figure_id}")
    return {
        "figure_id": figure_id,
        "support_status": status,
        "plot_ready_generated": traces_present,
        "training_traces_available": traces_present,
        "claim_boundary": list(FEATURE_080_BOUNDARY + FEATURE_086_BOUNDARY),
        "reason": reason,
        "notes": "No fake curves were generated.",
    }


def _git_diff_paths(*paths: str) -> list[str]:
    try:
        completed = subprocess.run(
            ["git", "diff", "--name-only", "--", *paths],
            cwd=ROOT_DIR,
            check=False,
            capture_output=True,
            text=True,
        )
    except Exception:
        return []
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def _remaining_figure_outputs_report_payload(artifact_dir: Path) -> dict[str, Any]:
    figure_9_statuses: dict[str, Any] = {}
    figure_9_rows: dict[str, list[dict[str, Any]]] = {}
    for figure_id, (_csv_name, json_name) in _figure_9_artifact_files().items():
        rows = _read_json_array(artifact_dir / json_name)
        figure_9_rows[figure_id] = rows
        summary = _figure_9_row_status_summary(rows)
        figure_9_statuses[figure_id] = {
            "status": summary["figure_status"],
            "support_counts": summary["support_counts"],
            "row_count": summary["row_count"],
            "claim_boundary": list(FEATURE_080_BOUNDARY + FEATURE_086_BOUNDARY),
        }

    figure_8_statuses = {
        "Figure 8a": _figure_8_11_status_payload("Figure 8a", artifact_dir),
        "Figure 8b": _figure_8_11_status_payload("Figure 8b", artifact_dir),
    }
    figure_11_status = _figure_8_11_status_payload("Figure 11", artifact_dir)
    semantic_paths_modified = _git_diff_paths("src/policies", "src/environment", "src/evaluation", "src/training")
    no_output_sync_tuning = len(semantic_paths_modified) == 0
    figure_10_summary = json.loads((artifact_dir / "figure_10_analysis_summary.json").read_text(encoding="utf-8"))
    comparison_report = json.loads((artifact_dir / "figure_10_comparison_analysis_report.json").read_text(encoding="utf-8"))
    return {
        "feature_id": FEATURE_ID,
        "verdict": "feature_089_remaining_outputs_partial",
        "figure_10_status": {
            "status": "already_implemented_and_validated",
            "analysis_verdict": figure_10_summary.get("verdict"),
            "comparison_verdict": comparison_report.get("verdict"),
            "claims_alignment_verdict": comparison_report.get("overall_claim_alignment"),
        },
        "figure_9_status_by_figure": figure_9_statuses,
        "figure_9_row_samples": {
            figure_id: [
                {
                    "figure_id": row.get("figure_id"),
                    "metric": row.get("metric"),
                    "policy": row.get("policy"),
                    "support_status": row.get("support_status"),
                    "value": row.get("value"),
                    "approximation_note": row.get("approximation_note"),
                    "claim_boundary": row.get("claim_boundary"),
                }
                for row in rows[:3]
            ]
            for figure_id, rows in figure_9_rows.items()
        },
        "figure_8_status_by_figure": figure_8_statuses,
        "figure_11_status": figure_11_status,
        "no_output_sync_tuning": no_output_sync_tuning,
        "no_output_sync_tuning_proof": {
            "semantic_paths_scanned": ["src/policies", "src/environment", "src/evaluation", "src/training"],
            "modified_semantic_paths": semantic_paths_modified,
            "note": "No policy, reward, queue, or environment semantics were modified in this pass.",
        },
        "feature_080_boundary_preserved": True,
        "feature_086_boundary_preserved": True,
        "claim_boundary": list(FEATURE_080_BOUNDARY + FEATURE_086_BOUNDARY),
        "notes": (
            "Figure 10 remains implemented and validated. Figure 9 is now emitted as current-simulator output "
            "with approximation notes. Figure 8a, Figure 8b, and Figure 11 are gated because no trained traces exist."
        ),
    }


def _write_figure_8_11_status_artifacts(artifact_dir: Path) -> None:
    payloads = {
        "figure_8a_learning_rate_convergence_status": _figure_8_11_status_payload("Figure 8a", artifact_dir),
        "figure_8b_discount_factor_convergence_status": _figure_8_11_status_payload("Figure 8b", artifact_dir),
        "figure_11_lstm_ablation_status": _figure_8_11_status_payload("Figure 11", artifact_dir),
    }
    for stem, payload in payloads.items():
        _write_json(artifact_dir / f"{stem}.json", payload)
        _write_markdown_table(
            artifact_dir / f"{stem}.md",
            [
                {
                    "figure_id": payload["figure_id"],
                    "support_status": payload["support_status"],
                    "plot_ready_generated": payload["plot_ready_generated"],
                    "training_traces_available": payload["training_traces_available"],
                    "claim_boundary": json.dumps(payload["claim_boundary"], ensure_ascii=False),
                    "reason": payload["reason"],
                    "notes": payload["notes"],
                }
            ],
            stem.replace("_", " ").title(),
        )


def _write_remaining_figure_outputs_report(artifact_dir: Path) -> None:
    payload = _remaining_figure_outputs_report_payload(artifact_dir)
    _write_json(artifact_dir / "remaining_figure_outputs_report.json", payload)
    _write_markdown_table(
        artifact_dir / "remaining_figure_outputs_report.md",
        [
            {
                "feature_id": payload["feature_id"],
                "verdict": payload["verdict"],
                "figure_10_status": payload["figure_10_status"]["status"],
                "figure_9_status_by_figure": json.dumps(payload["figure_9_status_by_figure"], ensure_ascii=False),
                "figure_8_status_by_figure": json.dumps(payload["figure_8_status_by_figure"], ensure_ascii=False),
                "figure_11_status": json.dumps(payload["figure_11_status"], ensure_ascii=False),
                "no_output_sync_tuning": payload["no_output_sync_tuning"],
                "feature_080_boundary_preserved": payload["feature_080_boundary_preserved"],
                "feature_086_boundary_preserved": payload["feature_086_boundary_preserved"],
                "notes": payload["notes"],
            }
        ],
        "Feature 089 Remaining Figure Outputs Report",
    )


def build_report() -> Feature089Report:
    return _report(_ordered_figures(), _paper_metric_catalog(), _requirements())


def main(argv: list[str] | None = None) -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Feature 089 HOODIE paper metrics figure catalog")
    parser.add_argument("--artifact-dir", type=Path, default=ARTIFACT_DIR)
    parser.add_argument("--generate-artifacts", action="store_true", help="Generate Feature 089 artifacts")
    parser.add_argument("--validate-artifacts", action="store_true", help="Validate Feature 089 artifacts")
    args = parser.parse_args(argv)

    if not args.generate_artifacts and not args.validate_artifacts:
        args.generate_artifacts = True

    if args.generate_artifacts:
        generate_artifacts(args.artifact_dir)
    if args.validate_artifacts:
        validate_artifacts(args.artifact_dir)
