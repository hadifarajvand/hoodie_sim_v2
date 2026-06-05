from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from math import isnan
from pathlib import Path
import csv
import json
from tempfile import TemporaryDirectory
from typing import Any

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
from .model import Feature089Report, PaperFigure, PaperMetric, SimulatorOutputRequirement


FIGURE_10_SIMULATION_SEED = 7
FIGURE_10_HIGH_TIMEOUT_SECONDS = 10.0
FIGURE_10_STRICT_TIMEOUT_SECONDS = 2.0
FIGURE_9_VALIDATION_SEEDS = (7, 13, 21)
FIGURE_9_PAPER_VALIDATION_EPISODES = 200


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
        elif figure_id in PRIORITY_2_FIGURES and not requirement.blocked_by_simulator_support:
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
        if figure.figure_id == "Figure 9c":
            if abs(float(row.get("cpu_capacity_per_slot_agent", 0.0)) - float(row.get("sweep_value", 0.0))) > 1e-9:
                raise ValueError(f"{path.name} must sweep CPU capacity on the agent slot capacity axis")
        if figure.figure_id == "Figure 9a":
            if abs(float(row.get("arrival_probability", 0.0)) - float(row.get("sweep_value", 0.0))) > 1e-9:
                raise ValueError(f"{path.name} must sweep arrival probability on the x-axis")
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


def _validate_blocked_figure_9_output(path: Path, figure: PaperFigure) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"{path.name} must contain a JSON array")
    if len(payload) != 1:
        raise ValueError(f"{path.name} must contain one reference-only row while Figure 9 is blocked")
    row = payload[0]
    if row.get("figure_id") != figure.figure_id:
        raise ValueError(f"{path.name} contains a row for the wrong figure")
    if row.get("policy") != "HOODIE":
        raise ValueError(f"{path.name} must keep blocked Figure 9 outputs HOODIE-only")
    if row.get("status") != "blocked_by_simulator_support":
        raise ValueError(f"{path.name} must mark Figure 9 as blocked by simulator support")
    if row.get("metric") != figure.metric:
        raise ValueError(f"{path.name} must preserve the Figure 9 paper metric while blocked")
    if row.get("x_axis") != figure.x_axis:
        raise ValueError(f"{path.name} must preserve the paper x-axis while blocked")
    if list(row.get("sweep_values", [])) != list(figure.sweep_values):
        raise ValueError(f"{path.name} must preserve the Figure 9 sweep values while blocked")
    notes = str(row.get("notes", ""))
    if "Reference-only Figure 9 behavior output" not in notes:
        raise ValueError(f"{path.name} must explain the Figure 9 reference-only boundary")
    if "trained HOODIE DRL/LSTM" not in notes:
        raise ValueError(f"{path.name} must document the trained-policy blocker")


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
    figure_9_paths = {
        "Figure 9a": artifact_dir / "figure_9a_reward_vs_arrival_probability.json",
        "Figure 9b": artifact_dir / "figure_9b_action_distribution_vs_arrival_probability.json",
        "Figure 9c": artifact_dir / "figure_9c_reward_vs_cpu_capacity.json",
        "Figure 9d": artifact_dir / "figure_9d_reward_vs_agent_count_traffic.json",
        "Figure 9e": artifact_dir / "figure_9e_reward_vs_agent_count_data_rate.json",
    }
    for figure_id, path in figure_9_paths.items():
        _validate_blocked_figure_9_output(path, figures[figure_id])
    return report


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
