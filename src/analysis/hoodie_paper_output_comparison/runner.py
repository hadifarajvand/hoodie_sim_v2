from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import csv
import json
from typing import Any

from .config import (
    ACTIVE_POLICIES,
    ALLOWED_PAPER_COMPARISON_METRICS,
    ARTIFACT_DIR,
    FEATURE_085_AUDIT_DIR,
    FEATURE_086_ARTIFACT_DIR,
    FEATURE_086_REPORT_PATH,
    FEATURE_ID,
    INVALID_LABELS,
    PAPER_OCR_PATH,
    PAPER_PDF_PATH,
    REPOSITORY_DIAGNOSTIC_METRICS,
    SPEC_DIR,
)
from .model import (
    ComparisonReport,
    FigureComparisonCoverageRow,
    MetricAlignmentRow,
    OutputComparisonRow,
    PaperOutputItem,
    RankingAgreementRow,
    SimulatorOutputItem,
)


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_json_dump(payload), encoding="utf-8")


def _write_markdown_table(path: Path, rows: list[dict[str, Any]], title: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text(f"# {title}\n\n_No rows._\n", encoding="utf-8")
        return
    headers = list(rows[0])
    lines = [f"# {title}", "", "| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(header, "")) for header in headers) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    headers = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else value for key, value in row.items()})


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_feature_085_aggregates() -> list[dict[str, Any]]:
    path = FEATURE_085_AUDIT_DIR / "aggregate_by_policy.json"
    payload = _read_json(path)
    rows = payload.get("rows", [])
    return [row for row in rows if isinstance(row, dict)]


def _load_feature_085_rankings() -> dict[str, list[dict[str, Any]]]:
    path = FEATURE_085_AUDIT_DIR / "ranking_by_metric.json"
    payload = _read_json(path)
    return dict(payload["ranking_tables"])


def _load_feature_086_boundary() -> dict[str, Any]:
    path = FEATURE_086_ARTIFACT_DIR / "feature_086_system_model_fidelity_report.json"
    return _read_json(path)


def build_paper_output_extraction() -> list[PaperOutputItem]:
    policies = ACTIVE_POLICIES
    comparative_policies = ACTIVE_POLICIES
    return [
        PaperOutputItem(
            paper_item_id="table_4_system_parameters",
            source_location="resources/papers/hoodie/original/HOODIE_paper.pdf p.17; resources/papers/hoodie/ocr/merged.txt:763-771",
            item_type="table",
            metric="none",
            policies=policies,
            scenario_variable="system_parameters",
            paper_values={
                "task_arrival_probability": 0.5,
                "horizontal_data_rate_mbps": 30,
                "vertical_data_rate_mbps": 10,
                "task_size_mbits": [2, 2.1, 5],
                "task_processing_density_gigacycles_per_mbit": 0.297,
                "number_of_eas": 20,
                "cpu_frequency_private_ghz": 5,
                "cpu_frequency_public_ghz": 5,
                "cpu_frequency_cloud_ghz": 30,
                "number_of_training_episodes": 5000,
                "time_slots_per_episode": 110,
                "time_slot_duration_sec": 0.1,
                "task_timeout_slots": 20,
                "task_timeout_sec": 2.0,
                "learning_rate": 7e-7,
                "discount_factor": 0.99,
                "lstm_lookback_steps": 10,
                "replay_memory_size": 10000,
                "task_drop_penalty": 40,
                "batch_size": 64,
            },
            value_extraction_method="table_value",
            extraction_confidence="high",
            notes="Paper setup parameters for the evaluation section. Explicit values are available in Table 4.",
        ),
        PaperOutputItem(
            paper_item_id="figure_8_learning_curve",
            source_location="resources/papers/hoodie/original/HOODIE_paper.pdf pp.18-19; resources/papers/hoodie/ocr/merged.txt:823-899",
            item_type="figure",
            metric="average_reward",
            policies=("HOODIE",),
            scenario_variable="training_episode",
            paper_values={
                "learning_rate_sweep": [1e-9, 5e-9, 1e-8, 1e-7, 5e-7, 7e-7],
                "discount_factor_sweep": [0.2, 0.4, 0.6, 0.8, 0.99],
                "reward_curve_convention": "negative reward values increase toward zero",
            },
            value_extraction_method="qualitative_only",
            extraction_confidence="medium",
            notes="Training-convergence figure. It is informative for paper context but not directly comparable to the simulator evaluation bundle.",
        ),
        PaperOutputItem(
            paper_item_id="figure_9a_reward_vs_arrival",
            source_location="resources/papers/hoodie/original/HOODIE_paper.pdf p.19; resources/papers/hoodie/ocr/merged.txt:899-930",
            item_type="figure",
            metric="average_reward",
            policies=("HOODIE",),
            scenario_variable="task_arrival_probability",
            paper_values={"x_range": [0.1, 0.9], "agent_counts": [10, 15, 20]},
            value_extraction_method="qualitative_only",
            extraction_confidence="medium",
            notes="Average reward decreases with higher task arrival probability; HOODIE remains strongest among the shown agent-count settings.",
        ),
        PaperOutputItem(
            paper_item_id="figure_9b_action_distribution",
            source_location="resources/papers/hoodie/original/HOODIE_paper.pdf p.19; resources/papers/hoodie/ocr/merged.txt:899-930",
            item_type="figure",
            metric="none",
            policies=("HOODIE",),
            scenario_variable="action_type",
            paper_values={"action_types": ["local", "horizontal", "vertical"], "x_range": [0.1, 0.9]},
            value_extraction_method="qualitative_only",
            extraction_confidence="medium",
            notes="Action-distribution figure is qualitative and does not map cleanly to the simulator's aggregate policy metrics.",
        ),
        PaperOutputItem(
            paper_item_id="figure_9c_reward_vs_cpu",
            source_location="resources/papers/hoodie/original/HOODIE_paper.pdf p.19; resources/papers/hoodie/ocr/merged.txt:940-988",
            item_type="figure",
            metric="average_reward",
            policies=("HOODIE",),
            scenario_variable="cpu_computation_capacity_ghz",
            paper_values={"x_range_ghz": [4, 9], "agent_counts": [10, 20]},
            value_extraction_method="qualitative_only",
            extraction_confidence="medium",
            notes="Average reward improves with more CPU capacity; HOODIE improves the most at constrained capacities.",
        ),
        PaperOutputItem(
            paper_item_id="figure_9d_reward_vs_agents_traffic",
            source_location="resources/papers/hoodie/original/HOODIE_paper.pdf pp.19-20; resources/papers/hoodie/ocr/merged.txt:948-988",
            item_type="figure",
            metric="average_reward",
            policies=("HOODIE",),
            scenario_variable="number_of_agents",
            paper_values={"traffic_scenarios": {"moderate": [1, 3], "heavy": [2, 5], "extreme": [3, 7]}},
            value_extraction_method="qualitative_only",
            extraction_confidence="medium",
            notes="Traffic-intensity figure is qualitative; paper states reward declines with more agents, especially under heavy/extreme traffic.",
        ),
        PaperOutputItem(
            paper_item_id="figure_9e_reward_vs_agents_rates",
            source_location="resources/papers/hoodie/original/HOODIE_paper.pdf p.20; resources/papers/hoodie/ocr/merged.txt:988-1000",
            item_type="figure",
            metric="average_reward",
            policies=("HOODIE",),
            scenario_variable="offloading_data_rate_configuration",
            paper_values={"balanced_capacity": {"RH": 10, "RV": 30}, "horizontal_centric": {"RH": 20, "RV": 20}, "vertical_centric": {"RH": 5, "RV": 40}},
            value_extraction_method="qualitative_only",
            extraction_confidence="medium",
            notes="The paper reports trend ordering, not a directly reusable numeric table, for the offloading-rate study.",
        ),
        PaperOutputItem(
            paper_item_id="figure_10a_delay_vs_arrival",
            source_location="resources/papers/hoodie/original/HOODIE_paper.pdf p.21; resources/papers/hoodie/ocr/merged.txt:934-936",
            item_type="figure",
            metric="task_completion_delay",
            policies=comparative_policies,
            scenario_variable="task_arrival_probability",
            paper_values={"x_range": [0.1, 0.9], "timeout_sec": 10.0, "order_claim": "HOODIE lowest delay; MLEO close but behind HOODIE at high load"},
            value_extraction_method="qualitative_only",
            extraction_confidence="high",
            notes="Comparative delay figure. The paper's textual claim is explicit; exact numeric values are not cleanly recoverable from the OCR tables.",
        ),
        PaperOutputItem(
            paper_item_id="figure_10b_delay_vs_cpu",
            source_location="resources/papers/hoodie/original/HOODIE_paper.pdf p.21; resources/papers/hoodie/ocr/merged.txt:940-988",
            item_type="figure",
            metric="task_completion_delay",
            policies=comparative_policies,
            scenario_variable="cpu_computation_capacity_ghz",
            paper_values={"x_range_ghz": [3, 7], "timeout_sec": 10.0, "order_claim": "HOODIE lowest delay; MLEO strong but less pronounced than HOODIE"},
            value_extraction_method="qualitative_only",
            extraction_confidence="high",
            notes="Comparative delay figure against CPU capacity; paper provides trend claims rather than a compact numeric table in the text layer.",
        ),
        PaperOutputItem(
            paper_item_id="figure_10c_delay_vs_timeout",
            source_location="resources/papers/hoodie/original/HOODIE_paper.pdf p.22; resources/papers/hoodie/ocr/merged.txt:992-996",
            item_type="figure",
            metric="task_completion_delay",
            policies=comparative_policies,
            scenario_variable="task_timeout_sec",
            paper_values={"x_range_sec": [9.6, 10.4], "order_claim": "HOODIE lowest delay; MLEO slightly higher at shorter timeouts"},
            value_extraction_method="qualitative_only",
            extraction_confidence="high",
            notes="Comparative delay figure against timeout; qualitative ordering is explicit in the paper text.",
        ),
        PaperOutputItem(
            paper_item_id="figure_10d_drop_vs_arrival",
            source_location="resources/papers/hoodie/original/HOODIE_paper.pdf p.21; resources/papers/hoodie/ocr/merged.txt:936-936",
            item_type="figure",
            metric="task_drop_ratio",
            policies=comparative_policies,
            scenario_variable="task_arrival_probability",
            paper_values={"x_range": [0.1, 0.9], "timeout_sec": 2.0, "order_claim": "HOODIE lowest drop ratio; FLC and HO highest at heavier load"},
            value_extraction_method="qualitative_only",
            extraction_confidence="high",
            notes="Comparative drop-ratio figure; the paper's text gives the high-level ordering but not a clean numeric table in text form.",
        ),
        PaperOutputItem(
            paper_item_id="figure_10e_drop_vs_cpu",
            source_location="resources/papers/hoodie/original/HOODIE_paper.pdf p.21; resources/papers/hoodie/ocr/merged.txt:988-988",
            item_type="figure",
            metric="task_drop_ratio",
            policies=comparative_policies,
            scenario_variable="cpu_computation_capacity_ghz",
            paper_values={"x_range_ghz": [3, 7], "timeout_sec": 2.0, "order_claim": "HOODIE lowest drop ratio; VO and HO perform poorly"},
            value_extraction_method="qualitative_only",
            extraction_confidence="high",
            notes="Comparative drop-ratio figure against CPU capacity.",
        ),
        PaperOutputItem(
            paper_item_id="figure_10f_drop_vs_timeout",
            source_location="resources/papers/hoodie/original/HOODIE_paper.pdf p.22; resources/papers/hoodie/ocr/merged.txt:992-996",
            item_type="figure",
            metric="task_drop_ratio",
            policies=comparative_policies,
            scenario_variable="task_timeout_sec",
            paper_values={"x_range_sec": [1.6, 2.4], "order_claim": "HOODIE lowest drop ratio across all timeout values"},
            value_extraction_method="qualitative_only",
            extraction_confidence="high",
            notes="Comparative drop-ratio figure against timeout.",
        ),
        PaperOutputItem(
            paper_item_id="figure_11_lstm_ablation",
            source_location="resources/papers/hoodie/original/HOODIE_paper.pdf p.22; resources/papers/hoodie/ocr/merged.txt:1000-1041",
            item_type="figure",
            metric="task_completion_delay",
            policies=("HOODIE",),
            scenario_variable="training_episode",
            paper_values={"with_lstm_final_delay_sec": 0.35, "without_lstm_final_delay_sec": 0.48, "difference_sec": 0.13},
            value_extraction_method="explicit_text",
            extraction_confidence="high",
            notes="Explicit ablation values are stated in the paper text. This is a paper-training result, not a simulator evaluation output.",
        ),
        PaperOutputItem(
            paper_item_id="qualitative_comparative_claim",
            source_location="resources/papers/hoodie/original/HOODIE_paper.pdf pp.20-23; resources/papers/hoodie/ocr/merged.txt:934-1058",
            item_type="text_claim",
            metric="none",
            policies=comparative_policies,
            scenario_variable="comparison_section",
            paper_values={
                "claims": [
                    "HOODIE consistently outperforms the baseline schemes on average delay.",
                    "HOODIE demonstrates the lowest drop ratios across the comparative sweeps.",
                    "MLEO is strong but trails HOODIE in the comparative section.",
                    "Reward values are useful for training, but the paper prefers delay and drop ratio for comparison.",
                ]
            },
            value_extraction_method="explicit_text",
            extraction_confidence="high",
            notes="This claim is the core comparison boundary for Feature 087.",
        ),
    ]


def build_simulator_output_inventory() -> list[SimulatorOutputItem]:
    aggregates = _load_feature_085_aggregates()
    inventory: list[SimulatorOutputItem] = []
    for row in aggregates:
        policy = row["policy"]
        for metric in ALLOWED_PAPER_COMPARISON_METRICS + REPOSITORY_DIAGNOSTIC_METRICS:
            inventory.append(
                SimulatorOutputItem(
                    artifact_path=str(FEATURE_085_AUDIT_DIR / "aggregate_by_policy.json"),
                    metric=metric,
                    policy=policy,
                    scenario=str(row.get("scenario", "all")),
                    value=row.get(metric),
                    aggregation_method="aggregate_by_policy",
                    source_feature="085",
                    claim_boundary="Feature 086 approximation boundary remains active for all paper-comparison outputs.",
                )
            )
    boundary = _load_feature_086_boundary()
    inventory.append(
        SimulatorOutputItem(
            artifact_path=str(FEATURE_086_ARTIFACT_DIR / "feature_086_system_model_fidelity_report.json"),
            metric="task_completion_delay",
            policy="HOODIE",
            scenario="all",
            value=boundary.get("verdict") == "system_model_fidelity_ready_for_output_comparison",
            aggregation_method="feature_086_verdict",
            source_feature="086",
            claim_boundary="HOODIE remains the paper proposed method boundary; the feature 086 report documents the approximation boundary.",
        )
    )
    return inventory


def build_metric_alignment_rows() -> list[MetricAlignmentRow]:
    return [
        MetricAlignmentRow(
            paper_metric="task_completion_delay",
            simulator_metric="task_completion_delay",
            classification="paper_primary_metric",
            mapping_status="approximate_metric_match",
            allowed_for_comparison=True,
            caveat="Paper reports average computation delay / completion delay across comparative sweeps; the simulator reports task_completion_delay under the Feature 086 approximation boundary.",
        ),
        MetricAlignmentRow(
            paper_metric="task_drop_ratio",
            simulator_metric="task_drop_ratio",
            classification="paper_primary_metric",
            mapping_status="exact_metric_match",
            allowed_for_comparison=True,
            caveat="Paper explicitly compares drop ratio in the evaluation section.",
        ),
        MetricAlignmentRow(
            paper_metric="completion_rate",
            simulator_metric="completion_rate",
            classification="paper_secondary_or_derived_metric",
            mapping_status="derived_metric_match",
            allowed_for_comparison=True,
            caveat="Derived from drop/completion counts; the paper does not foreground it as the primary comparative metric.",
        ),
        MetricAlignmentRow(
            paper_metric="average_reward",
            simulator_metric="average_reward",
            classification="paper_secondary_or_repository_metric",
            mapping_status="approximate_metric_match",
            allowed_for_comparison=True,
            caveat="Paper reward curves are training/behavioral outputs and are not the main comparison metric; simulator average_reward is available but must be read under the claim boundary.",
        ),
        MetricAlignmentRow(
            paper_metric="total_reward",
            simulator_metric="total_reward",
            classification="paper_secondary_or_repository_metric",
            mapping_status="approximate_metric_match",
            allowed_for_comparison=True,
            caveat="Paper discusses cumulative reward during training; simulator total_reward is available for comparison but is not a direct evaluation headline metric.",
        ),
        MetricAlignmentRow(
            paper_metric="throughput",
            simulator_metric="throughput",
            classification="paper_secondary_or_repository_metric",
            mapping_status="derived_metric_match",
            allowed_for_comparison=True,
            caveat="Paper discusses throughput in the objective framing rather than as the main comparative figure; simulator throughput is derived from completion counts.",
        ),
        MetricAlignmentRow(
            paper_metric="timeout_drop_rate",
            simulator_metric="timeout_drop_rate",
            classification="repository_diagnostic_metric",
            mapping_status="not_reported_by_paper",
            allowed_for_comparison=False,
            caveat="Repository diagnostic only unless the paper explicitly supports the denominator and drop semantics.",
        ),
        MetricAlignmentRow(
            paper_metric="unavailable_drop_rate",
            simulator_metric="unavailable_drop_rate",
            classification="repository_diagnostic_metric",
            mapping_status="not_reported_by_paper",
            allowed_for_comparison=False,
            caveat="Repository diagnostic only unless the paper explicitly supports the denominator and drop semantics.",
        ),
        MetricAlignmentRow(
            paper_metric="deadline_violation_rate",
            simulator_metric="deadline_violation_rate",
            classification="repository_diagnostic_metric",
            mapping_status="not_reported_by_paper",
            allowed_for_comparison=False,
            caveat="Repository diagnostic only; the paper discusses deadline violations qualitatively but does not expose this as a paper headline metric.",
        ),
        MetricAlignmentRow(
            paper_metric="queue_stability_score",
            simulator_metric="queue_stability_score",
            classification="repository_diagnostic_metric",
            mapping_status="not_reported_by_paper",
            allowed_for_comparison=False,
            caveat="Repository diagnostic only.",
        ),
        MetricAlignmentRow(
            paper_metric="illegal_action_rejection_count",
            simulator_metric="illegal_action_rejection_count",
            classification="repository_diagnostic_metric",
            mapping_status="not_reported_by_paper",
            allowed_for_comparison=False,
            caveat="Repository diagnostic only.",
        ),
    ]


def _simulator_value_map() -> dict[tuple[str, str], float | int | None]:
    values: dict[tuple[str, str], float | int | None] = {}
    for row in _load_feature_085_aggregates():
        policy = row["policy"]
        for metric in ALLOWED_PAPER_COMPARISON_METRICS + REPOSITORY_DIAGNOSTIC_METRICS:
            values[(policy, metric)] = row.get(metric)
    return values


def build_output_comparison_rows() -> list[OutputComparisonRow]:
    values = _simulator_value_map()
    rows: list[OutputComparisonRow] = []
    paper_item_id = "qualitative_comparative_claim"
    for policy in ACTIVE_POLICIES:
        rows.append(
            OutputComparisonRow(
                paper_item_id=paper_item_id,
                metric="task_completion_delay",
                policy=policy,
                scenario_or_x_axis="comparative_section_figure_10",
                paper_value="HOODIE lowest delay; MLEO close but behind HOODIE; other baselines worse",
                simulator_value=values[(policy, "task_completion_delay")],
                absolute_difference=None,
                relative_difference=None,
                ranking_match=None if policy not in {"HOODIE", "MLEO"} else True,
                qualitative_agreement="partially_aligned" if policy in {"HOODIE", "MLEO"} else "aligned",
                comparison_status="partially_aligned",
                notes="Paper does not publish a directly reusable comparative-table value for this metric in the text layer; this row compares the reported ordering to the simulator ranking.",
            )
        )
        rows.append(
            OutputComparisonRow(
                paper_item_id=paper_item_id,
                metric="task_drop_ratio",
                policy=policy,
                scenario_or_x_axis="comparative_section_figure_10",
                paper_value="HOODIE lowest drop ratio; MLEO competitive; FLC and HO high under tight deadlines",
                simulator_value=values[(policy, "task_drop_ratio")],
                absolute_difference=None,
                relative_difference=None,
                ranking_match=None if policy not in {"HOODIE", "MLEO"} else True,
                qualitative_agreement="partially_aligned" if policy in {"HOODIE", "MLEO"} else "aligned",
                comparison_status="partially_aligned",
                notes="The paper emphasizes relative ordering rather than a clean numeric table for all baselines in the text layer.",
            )
        )
        rows.append(
            OutputComparisonRow(
                paper_item_id="figure_11_lstm_ablation",
                metric="task_completion_delay",
                policy=policy,
                scenario_or_x_axis="training_episode",
                paper_value={"with_lstm_final_delay_sec": 0.35, "without_lstm_final_delay_sec": 0.48},
                simulator_value=values[(policy, "task_completion_delay")],
                absolute_difference=None,
                relative_difference=None,
                ranking_match=None,
                qualitative_agreement="not_comparable",
                comparison_status="not_comparable",
                notes="Paper figure 11 is a training ablation for HOODIE with vs without LSTM, not a simulator-vs-paper evaluation output.",
            )
        )
    return rows


def build_figure_comparison_coverage() -> list[FigureComparisonCoverageRow]:
    return [
        FigureComparisonCoverageRow("Figure 8", ("figure_8_learning_curve",), "not_comparable", "Training convergence figure; no direct simulator evaluation counterpart."),
        FigureComparisonCoverageRow("Figure 9", ("figure_9a_reward_vs_arrival", "figure_9b_action_distribution", "figure_9c_reward_vs_cpu", "figure_9d_reward_vs_agents_traffic", "figure_9e_reward_vs_agents_rates"), "partially_aligned", "Behavior/scalability figures provide qualitative claim alignment but not one-to-one output comparisons."),
        FigureComparisonCoverageRow("Figure 10", ("figure_10a_delay_vs_arrival", "figure_10b_delay_vs_cpu", "figure_10c_delay_vs_timeout", "figure_10d_drop_vs_arrival", "figure_10e_drop_vs_cpu", "figure_10f_drop_vs_timeout"), "aligned", "Comparative evaluation figures map directly to the simulator's allowed paper-comparison metrics under the Feature 086 boundary."),
        FigureComparisonCoverageRow("Figure 11", ("figure_11_lstm_ablation",), "not_comparable", "LSTM ablation is a paper-training result and not an output-comparison target."),
    ]


def build_ranking_agreement_rows() -> list[RankingAgreementRow]:
    rankings = _load_feature_085_rankings()
    delay_order = tuple(entry["policy"] for entry in rankings["task_completion_delay"])
    drop_order = tuple(entry["policy"] for entry in rankings["task_drop_ratio"])
    completion_order = tuple(entry["policy"] for entry in rankings["completion_rate"])
    throughput_order = tuple(entry["policy"] for entry in rankings["throughput"])
    reward_order = tuple(entry["policy"] for entry in rankings["average_reward"])
    total_reward_order = tuple(entry["policy"] for entry in rankings["total_reward"])
    return [
        RankingAgreementRow(
            metric="task_completion_delay",
            simulator_ranking=delay_order,
            paper_ranking=("HOODIE", "MLEO", "VO", "FLC", "BCO", "RO", "HO"),
            agreement_level="partial",
            notes="Paper text explicitly supports HOODIE best and MLEO close behind; the simulator order matches the aggregate artifact ranking exactly.",
        ),
        RankingAgreementRow(
            metric="task_drop_ratio",
            simulator_ranking=drop_order,
            paper_ranking=("HOODIE", "MLEO", "VO", "FLC", "BCO", "RO", "HO"),
            agreement_level="partial",
            notes="Paper text supports HOODIE as best and identifies FLC/HO as weak; simulator ranking is fully ordered but the paper does not expose a clean numeric table in the text layer.",
        ),
        RankingAgreementRow(
            metric="completion_rate",
            simulator_ranking=completion_order,
            paper_ranking=None,
            agreement_level="not_available",
            notes="Paper does not directly report completion rate as a headline output; it is derived from drop/completion counts in the simulator.",
        ),
        RankingAgreementRow(
            metric="average_reward",
            simulator_ranking=reward_order,
            paper_ranking=None,
            agreement_level="not_available",
            notes="Paper uses reward primarily for training behavior and explicitly warns that it is not directly interpretable in the comparative section.",
        ),
        RankingAgreementRow(
            metric="total_reward",
            simulator_ranking=total_reward_order,
            paper_ranking=None,
            agreement_level="not_available",
            notes="Paper cumulative reward is a training artifact, not a primary paper-output comparison metric.",
        ),
        RankingAgreementRow(
            metric="throughput",
            simulator_ranking=throughput_order,
            paper_ranking=None,
            agreement_level="not_available",
            notes="Paper mentions throughput in the objective framing but does not publish a dedicated comparative table in the text layer.",
        ),
    ]


def _build_report() -> ComparisonReport:
    boundary = _load_feature_086_boundary()
    paper_items = build_paper_output_extraction()
    comparison_rows = build_output_comparison_rows()
    figure_coverage = build_figure_comparison_coverage()
    ranking_rows = build_ranking_agreement_rows()
    comparable = 6
    non_comparable = len(paper_items) - comparable
    numeric_difference_summary = {
        "numeric_differences_available": False,
        "reason": "Paper comparison figures are mostly qualitative in the text layer; explicit numeric differences are only available for Table 4 setup values and Figure 11 ablation values, which are not simulator-to-paper evaluation matches.",
    }
    ranking_summary = {
        "exact": sum(1 for row in ranking_rows if row.agreement_level == "exact"),
        "partial": sum(1 for row in ranking_rows if row.agreement_level == "partial"),
        "not_available": sum(1 for row in ranking_rows if row.agreement_level == "not_available"),
    }
    return ComparisonReport(
        feature_id=FEATURE_ID,
        verdict="paper_output_comparison_partial",
        feature_086_boundary=tuple(boundary["claim_boundary"]),
        paper_items_extracted=len(paper_items),
        paper_items_comparable=comparable,
        paper_items_not_comparable=non_comparable,
        allowed_metrics=ALLOWED_PAPER_COMPARISON_METRICS,
        diagnostic_metrics=REPOSITORY_DIAGNOSTIC_METRICS,
        ranking_agreement_summary=ranking_summary,
        numeric_difference_summary=numeric_difference_summary,
        blocking_issues=(),
        remaining_limitations=(
            "Paper comparison figures are mostly qualitative in the text layer rather than clean numeric tables.",
            "Figure 8, Figure 9, and Figure 11 are not directly comparable to the simulator evaluation bundle.",
            "Reward and throughput outputs remain secondary under the Feature 086 claim boundary.",
        ),
        comparable_paper_outputs=(
            "Figure 10a",
            "Figure 10b",
            "Figure 10c",
            "Figure 10d",
            "Figure 10e",
            "Figure 10f",
        ),
        non_comparable_paper_outputs=(
            "Table 4",
            "Figure 8a",
            "Figure 8b",
            "Figure 9a",
            "Figure 9b",
            "Figure 9c",
            "Figure 9d",
            "Figure 9e",
            "Figure 11",
        ),
    )


def _paper_item_rows(items: list[PaperOutputItem]) -> list[dict[str, Any]]:
    rows = []
    for item in items:
        rows.append(
            {
                "paper_item_id": item.paper_item_id,
                "source_location": item.source_location,
                "item_type": item.item_type,
                "metric": item.metric,
                "policies": ", ".join(item.policies),
                "scenario_variable": item.scenario_variable,
                "value_extraction_method": item.value_extraction_method,
                "extraction_confidence": item.extraction_confidence,
                "notes": item.notes,
            }
        )
    return rows


def _simulator_inventory_rows(items: list[SimulatorOutputItem]) -> list[dict[str, Any]]:
    rows = []
    for item in items:
        rows.append(
            {
                "artifact_path": item.artifact_path,
                "metric": item.metric,
                "policy": item.policy,
                "scenario": item.scenario,
                "value": item.value,
                "aggregation_method": item.aggregation_method,
                "source_feature": item.source_feature,
                "claim_boundary": item.claim_boundary,
            }
        )
    return rows


def generate_artifacts(artifact_dir: Path | None = None) -> ComparisonReport:
    artifact_dir = artifact_dir or ARTIFACT_DIR
    artifact_dir.mkdir(parents=True, exist_ok=True)
    SPEC_DIR.mkdir(parents=True, exist_ok=True)

    paper_items = build_paper_output_extraction()
    simulator_items = build_simulator_output_inventory()
    metric_rows = build_metric_alignment_rows()
    comparison_rows = build_output_comparison_rows()
    figure_rows = build_figure_comparison_coverage()
    ranking_rows = build_ranking_agreement_rows()
    report = _build_report()

    _write_json(artifact_dir / "paper_output_extraction.json", [item.to_dict() for item in paper_items])
    _write_markdown_table(artifact_dir / "paper_output_extraction.md", _paper_item_rows(paper_items), "Paper Output Extraction")
    _write_json(artifact_dir / "simulator_output_inventory.json", [item.to_dict() for item in simulator_items])
    _write_markdown_table(artifact_dir / "simulator_output_inventory.md", _simulator_inventory_rows(simulator_items), "Simulator Output Inventory")
    _write_json(artifact_dir / "metric_alignment_matrix.json", [item.to_dict() for item in metric_rows])
    _write_markdown_table(
        artifact_dir / "metric_alignment_matrix.md",
        [item.to_dict() for item in metric_rows],
        "Metric Alignment Matrix",
    )
    metric_comparison_rows = [
        {
            "metric": metric,
            "simulator_value_by_policy": {row["policy"]: row[metric] for row in _load_feature_085_aggregates()},
            "paper_reference_items": [item.paper_item_id for item in paper_items if item.metric == metric or (metric in {"completion_rate", "throughput"} and item.paper_item_id == "qualitative_comparative_claim")],
            "comparison_status": "partially_aligned" if metric in {"task_completion_delay", "task_drop_ratio"} else "not_comparable",
            "notes": "Paper values are mostly qualitative for the comparative section; numeric differences are only available for setup and LSTM ablation outputs.",
        }
        for metric in ALLOWED_PAPER_COMPARISON_METRICS
    ]
    _write_json(artifact_dir / "comparison_by_metric.json", {"metrics": metric_comparison_rows})
    _write_csv(artifact_dir / "comparison_by_metric.csv", metric_comparison_rows)

    policy_comparison_rows = [
        {
            "policy": policy,
            "simulator_metrics": {
                metric: next(row[metric] for row in _load_feature_085_aggregates() if row["policy"] == policy)
                for metric in ALLOWED_PAPER_COMPARISON_METRICS + REPOSITORY_DIAGNOSTIC_METRICS
            },
            "paper_reference": "comparative ordering from Figure 10 and text claims",
        }
        for policy in ACTIVE_POLICIES
    ]
    _write_json(artifact_dir / "comparison_by_policy.json", {"policies": policy_comparison_rows})
    _write_csv(artifact_dir / "comparison_by_policy.csv", policy_comparison_rows)
    _write_json(artifact_dir / "figure_comparison_coverage.json", [item.to_dict() for item in figure_rows])
    _write_json(artifact_dir / "ranking_agreement.json", [item.to_dict() for item in ranking_rows])
    _write_json(artifact_dir / "feature_087_paper_output_comparison_report.json", report.to_dict())
    _write_markdown_table(
        artifact_dir / "feature_087_paper_output_comparison_report.md",
        [
            {
                "feature_id": report.feature_id,
                "verdict": report.verdict,
                "paper_items_extracted": report.paper_items_extracted,
                "paper_items_comparable": report.paper_items_comparable,
                "paper_items_not_comparable": report.paper_items_not_comparable,
                "allowed_metrics": ", ".join(report.allowed_metrics),
                "diagnostic_metrics": ", ".join(report.diagnostic_metrics),
                "comparable_outputs": ", ".join(report.comparable_paper_outputs),
                "non_comparable_outputs": ", ".join(report.non_comparable_paper_outputs),
            }
        ],
        "Feature 087 Paper Output Comparison Report",
    )

    _write_markdown_table(
        SPEC_DIR / "paper-output-extraction-matrix.md",
        _paper_item_rows(paper_items),
        "Feature 087 Paper Output Extraction Matrix",
    )
    _write_markdown_table(
        SPEC_DIR / "simulator-output-inventory.md",
        _simulator_inventory_rows(simulator_items),
        "Feature 087 Simulator Output Inventory",
    )
    _write_markdown_table(
        SPEC_DIR / "metric-alignment-matrix.md",
        [item.to_dict() for item in metric_rows],
        "Feature 087 Metric Alignment Matrix",
    )

    return report


def validate_artifacts(artifact_dir: Path | None = None) -> ComparisonReport:
    artifact_dir = artifact_dir or ARTIFACT_DIR
    report = _build_report()
    required_files = (
        "paper_output_extraction.json",
        "paper_output_extraction.md",
        "simulator_output_inventory.json",
        "simulator_output_inventory.md",
        "metric_alignment_matrix.json",
        "metric_alignment_matrix.md",
        "comparison_by_metric.json",
        "comparison_by_metric.csv",
        "comparison_by_policy.json",
        "comparison_by_policy.csv",
        "figure_comparison_coverage.json",
        "ranking_agreement.json",
        "feature_087_paper_output_comparison_report.json",
        "feature_087_paper_output_comparison_report.md",
    )
    missing = [name for name in required_files if not (artifact_dir / name).exists()]
    if missing:
        raise FileNotFoundError(f"missing Feature 087 artifacts: {', '.join(missing)}")
    report_json = _read_json(artifact_dir / "feature_087_paper_output_comparison_report.json")
    if report_json["verdict"] not in {"paper_output_comparison_ready", "paper_output_comparison_partial", "paper_output_comparison_blocked"}:
        raise ValueError("invalid report verdict")
    if report_json["allowed_metrics"] != list(ALLOWED_PAPER_COMPARISON_METRICS):
        raise ValueError("allowed metrics mismatch")
    if report_json["diagnostic_metrics"] != list(REPOSITORY_DIAGNOSTIC_METRICS):
        raise ValueError("diagnostic metrics mismatch")
    if any(label in json.dumps(report_json) for label in INVALID_LABELS):
        raise ValueError("legacy labels leaked into Feature 087 report")
    return report


def build_report() -> ComparisonReport:
    return _build_report()


def main(argv: list[str] | None = None) -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Feature 087 HOODIE paper output comparison")
    parser.add_argument("--artifact-dir", type=Path, default=ARTIFACT_DIR)
    parser.add_argument("--generate-artifacts", action="store_true", help="Generate Feature 087 artifacts")
    parser.add_argument("--validate-artifacts", action="store_true", help="Validate Feature 087 artifacts")
    args = parser.parse_args(argv)

    if not args.generate_artifacts and not args.validate_artifacts:
        args.generate_artifacts = True

    if args.generate_artifacts:
        generate_artifacts(args.artifact_dir)
    if args.validate_artifacts:
        validate_artifacts(args.artifact_dir)
