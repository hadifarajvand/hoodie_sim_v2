from __future__ import annotations

from pathlib import Path
import csv
import json
from typing import Any

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
        writer = csv.DictWriter(handle, fieldnames=headers)
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
            policies_or_curves=("HOODIE",),
            scenario_setup="Table 4 defaults; N=10/15/20; 200 validation episodes; exploitative actions.",
            requires_training=False,
            requires_lstm=False,
            requires_digitization=False,
            priority="priority_2_hoodie_behavior_output",
            output_status="reference_only",
            extraction_confidence="medium",
            pdf_verified=True,
            ocr_caveat="OCR and PDF disagree on some tick labels; the paper text supports the 0.1-0.9 sweep.",
            simulator_output_requirement_id="req_figure_9a_reward_arrival",
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
            scenario_setup="Table 4 defaults; HOODIE only; exploitative validation episodes.",
            requires_training=False,
            requires_lstm=False,
            requires_digitization=False,
            priority="priority_2_hoodie_behavior_output",
            output_status="reference_only",
            extraction_confidence="high",
            pdf_verified=True,
            ocr_caveat="Action categories are explicit in the paper text.",
            simulator_output_requirement_id="req_figure_9b_action_distribution",
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
            output_status="reference_only",
            extraction_confidence="high",
            pdf_verified=True,
            ocr_caveat="CPU sweep values are explicit in the paper text.",
            simulator_output_requirement_id="req_figure_9c_reward_cpu",
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
            output_status="reference_only",
            extraction_confidence="high",
            pdf_verified=True,
            ocr_caveat="Traffic-intensity scenarios are explicit in the paper text.",
            simulator_output_requirement_id="req_figure_9d_reward_agents_traffic",
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
            output_status="reference_only",
            extraction_confidence="high",
            pdf_verified=True,
            ocr_caveat="Data-rate configurations are explicit in the paper text.",
            simulator_output_requirement_id="req_figure_9e_reward_agents_rates",
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
            notes="Figure 9 behavior output is cataloged but remains blocked until the simulator can sweep the arrival probability grid without inventing training claims.",
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
            notes="Figure 9 behavior output is cataloged but remains blocked until the simulator can produce action counts directly from the policy traces.",
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
            notes="Figure 9 behavior output is cataloged but remains blocked until the simulator can sweep CPU capacity directly.",
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
            notes="Figure 9 behavior output is cataloged but remains blocked until the simulator can vary agent count and workload intensity directly.",
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
            notes="Figure 9 behavior output is cataloged but remains blocked until the simulator can vary agent count and link-rate configurations directly.",
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
        metric_name = "average_reward"
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


def _write_figure_output_files(artifact_dir: Path, figures: list[PaperFigure], requirements: list[SimulatorOutputRequirement]) -> None:
    references = _reference_metric_values()
    requirement_by_id = {item.requirement_id: item for item in requirements}
    by_id = {figure.figure_id: figure for figure in figures}
    filenames = {
        "Figure 10a": ("figure_10a_delay_vs_arrival_probability.csv", "figure_10a_delay_vs_arrival_probability.json"),
        "Figure 10b": ("figure_10b_delay_vs_cpu_capacity.csv", "figure_10b_delay_vs_cpu_capacity.json"),
        "Figure 10c": ("figure_10c_delay_vs_timeout.csv", "figure_10c_delay_vs_timeout.json"),
        "Figure 10d": ("figure_10d_drop_ratio_vs_arrival_probability.csv", "figure_10d_drop_ratio_vs_arrival_probability.json"),
        "Figure 10e": ("figure_10e_drop_ratio_vs_cpu_capacity.csv", "figure_10e_drop_ratio_vs_cpu_capacity.json"),
        "Figure 10f": ("figure_10f_drop_ratio_vs_timeout.csv", "figure_10f_drop_ratio_vs_timeout.json"),
        "Figure 9a": ("figure_9a_reward_vs_arrival_probability.csv", "figure_9a_reward_vs_arrival_probability.json"),
        "Figure 9b": ("figure_9b_action_distribution_vs_arrival_probability.csv", "figure_9b_action_distribution_vs_arrival_probability.json"),
        "Figure 9c": ("figure_9c_reward_vs_cpu_capacity.csv", "figure_9c_reward_vs_cpu_capacity.json"),
        "Figure 9d": ("figure_9d_reward_vs_agent_count_traffic.csv", "figure_9d_reward_vs_agent_count_traffic.json"),
        "Figure 9e": ("figure_9e_reward_vs_agent_count_data_rate.csv", "figure_9e_reward_vs_agent_count_data_rate.json"),
    }
    for figure_id, figure in by_id.items():
        if figure_id not in filenames:
            continue
        requirement = requirement_by_id[figure.simulator_output_requirement_id]
        rows = _figure_output_rows(figure, requirement, references)
        csv_name, json_name = filenames[figure_id]
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
            "Figure 9 outputs are cataloged as blocked because the current simulator does not expose the exact sweep outputs without adding new sweep plumbing.",
            "Figures 8a, 8b, and 11 remain future-required because they depend on trained DRL and LSTM artifacts.",
            "Figure 10 output files are extension scaffolds that preserve the required raw versus paper-style transformations, but they do not claim fresh simulator-run measurements yet.",
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
    _generate_supporting_spec_docs(figures, metrics, requirements)
    return report


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
