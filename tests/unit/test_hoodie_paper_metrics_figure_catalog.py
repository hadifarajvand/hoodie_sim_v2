from __future__ import annotations

import json
import shutil
from pathlib import Path
import unittest

from src.analysis.hoodie_paper_metrics_figure_catalog.config import ACTIVE_POLICIES
from src.analysis.hoodie_paper_metrics_figure_catalog.runner import (
    build_report,
    generate_artifacts,
    _delay_plot_value,
    _drop_percent,
    _ordered_figures,
    _paper_metric_catalog,
    _requirements,
)


class HoodiePaperMetricsFigureCatalogTests(unittest.TestCase):
    def test_all_required_figures_exist(self) -> None:
        figure_ids = [figure.figure_id for figure in _ordered_figures()]
        self.assertEqual(
            figure_ids,
            [
                "Figure 8a",
                "Figure 8b",
                "Figure 9a",
                "Figure 9b",
                "Figure 9c",
                "Figure 9d",
                "Figure 9e",
                "Figure 10a",
                "Figure 10b",
                "Figure 10c",
                "Figure 10d",
                "Figure 10e",
                "Figure 10f",
                "Figure 11",
            ],
        )

    def test_figure_10_priority_one_policy_sets_and_sweeps(self) -> None:
        figures = {figure.figure_id: figure for figure in _ordered_figures()}
        for figure_id in ("Figure 10a", "Figure 10b", "Figure 10c", "Figure 10d", "Figure 10e", "Figure 10f"):
            figure = figures[figure_id]
            self.assertEqual(figure.priority, "priority_1_comparative_output")
            self.assertEqual(tuple(figure.policies_or_curves), ACTIVE_POLICIES)
            self.assertTrue(figure.pdf_verified)

        self.assertEqual(figures["Figure 10a"].sweep_values, (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9))
        self.assertEqual(figures["Figure 10b"].sweep_values, (3, 4, 5, 6, 7))
        self.assertEqual(figures["Figure 10c"].sweep_values, (9.6, 9.8, 10.0, 10.2, 10.4))
        self.assertEqual(figures["Figure 10d"].sweep_values, (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9))
        self.assertEqual(figures["Figure 10e"].sweep_values, (3, 4, 5, 6, 7))
        self.assertEqual(figures["Figure 10f"].sweep_values, (1.6, 1.8, 2.0, 2.2, 2.4))

    def test_figure_9_catalog_preserves_paper_curve_semantics(self) -> None:
        figures = {figure.figure_id: figure for figure in _ordered_figures()}
        self.assertEqual(figures["Figure 9a"].policies_or_curves, ("N=10", "N=15", "N=20"))
        self.assertEqual(figures["Figure 9b"].x_axis, "action_type")
        self.assertEqual(figures["Figure 9b"].policies_or_curves, ("local", "horizontal", "vertical"))
        self.assertIn("N=20", figures["Figure 9b"].scenario_setup)
        self.assertEqual(figures["Figure 9d"].policies_or_curves, ("Moderate Traffic", "Heavy Traffic", "Extreme Traffic"))
        self.assertEqual(figures["Figure 9e"].policies_or_curves, ("Balanced", "Horizontal-centric", "Vertical-centric"))

    def test_delay_and_drop_transforms(self) -> None:
        self.assertEqual(_delay_plot_value(3.5), -3.5)
        self.assertEqual(_delay_plot_value(-3.5), -3.5)
        self.assertEqual(_drop_percent(0.125), 12.5)

    def test_metric_catalog_contains_expected_entries(self) -> None:
        metric_ids = [metric.metric_id for metric in _paper_metric_catalog()]
        self.assertEqual(
            metric_ids,
            [
                "average_task_completion_delay",
                "task_drop_ratio",
                "average_reward",
                "accumulated_reward",
                "action_distribution",
                "average_task_delay_with_vs_without_lstm",
            ],
        )

    def test_output_requirements_cover_blocked_and_ready_figures(self) -> None:
        requirements = {item.requirement_id: item for item in _requirements()}
        self.assertFalse(requirements["req_figure_10a_delay_arrival"].blocked_by_simulator_support)
        self.assertTrue(requirements["req_figure_9a_reward_arrival"].blocked_by_simulator_support)
        self.assertTrue(requirements["req_figure_9b_action_distribution"].blocked_by_simulator_support)
        self.assertTrue(requirements["req_figure_9c_reward_cpu"].blocked_by_simulator_support)
        self.assertTrue(requirements["req_figure_9d_reward_agents_traffic"].blocked_by_simulator_support)
        self.assertTrue(requirements["req_figure_9e_reward_agents_rates"].blocked_by_simulator_support)
        self.assertTrue(requirements["req_figure_8a_training_curve"].blocked_by_training)
        self.assertTrue(requirements["req_figure_11_lstm_ablation"].blocked_by_lstm)

    def test_report_counts(self) -> None:
        report = build_report()
        self.assertEqual(report.figures_cataloged, 14)
        self.assertEqual(report.metrics_cataloged, 6)
        self.assertEqual(report.simulator_output_requirements, 14)
        self.assertIn("Figure 10a", report.ready_now_figures)
        self.assertNotIn("Figure 9a", report.ready_now_figures)
        self.assertIn("Figure 9a", report.blocked_figures)
        self.assertIn("Figure 9b", report.blocked_figures)
        self.assertIn("Figure 9c", report.blocked_figures)
        self.assertIn("Figure 9d", report.blocked_figures)
        self.assertIn("Figure 9e", report.blocked_figures)
        self.assertIn("Figure 8a", report.future_required_figures)
        self.assertIn("Figure 8b", report.future_required_figures)
        self.assertIn("Figure 11", report.future_required_figures)

    def test_generate_artifacts_writes_files(self) -> None:
        artifact_dir = Path("/tmp/feature_089_test_artifacts")
        if artifact_dir.exists():
            for path in sorted(artifact_dir.glob("*")):
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
        report = generate_artifacts(artifact_dir)
        self.assertEqual(report.verdict, "paper_metrics_catalog_partial")
        self.assertTrue((artifact_dir / "feature_089_report.json").exists())
        self.assertTrue((artifact_dir / "figure_10_output_audit.json").exists())
        self.assertTrue((artifact_dir / "figure_10_analysis_summary.json").exists())
        self.assertTrue((artifact_dir / "feature_089_completion_report.json").exists())
        self.assertTrue((artifact_dir / "figure_10_trend_analysis.json").exists())
        self.assertTrue((artifact_dir / "figure_10_ranking_analysis.json").exists())
        self.assertTrue((artifact_dir / "figure_10_paper_claim_alignment.json").exists())
        self.assertTrue((artifact_dir / "figure_10_comparison_analysis_report.json").exists())
        self.assertTrue((artifact_dir / "remaining_figure_outputs_report.json").exists())
        self.assertTrue((artifact_dir / "remaining_figure_outputs_report.md").exists())
        self.assertTrue((artifact_dir / "figure_8a_learning_rate_convergence_status.json").exists())
        self.assertTrue((artifact_dir / "figure_8b_discount_factor_convergence_status.json").exists())
        self.assertTrue((artifact_dir / "figure_11_lstm_ablation_status.json").exists())
        delay_payload = json.loads((artifact_dir / "figure_10a_delay_vs_arrival_probability.json").read_text(encoding="utf-8"))
        self.assertEqual(len(delay_payload), len(ACTIVE_POLICIES) * 9)
        self.assertEqual(
            {row["policy"] for row in delay_payload},
            set(ACTIVE_POLICIES),
        )
        self.assertEqual(
            {row["sweep_value"] for row in delay_payload},
            {0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9},
        )
        self.assertTrue(all(row["status"] == "simulator_generated" for row in delay_payload))
        self.assertTrue(all(row["task_completion_delay_raw"] >= 0 for row in delay_payload))
        self.assertTrue(all(row["paper_style_delay_for_plotting"] <= 0 for row in delay_payload))
        self.assertTrue(all(abs(row["paper_style_delay_for_plotting"] + row["task_completion_delay_raw"]) < 1e-9 for row in delay_payload))

        reward_payload = json.loads((artifact_dir / "figure_9a_reward_vs_arrival_probability.json").read_text(encoding="utf-8"))
        self.assertEqual(len(reward_payload), 15)
        self.assertTrue(all(row["policy"] == "HOODIE" for row in reward_payload))
        self.assertTrue(all(row["support_status"] == "generated_with_approximation" for row in reward_payload))
        self.assertTrue(all(row["status"] == "simulator_generated" for row in reward_payload))
        self.assertTrue(all(row["claim_boundary"] for row in reward_payload))
        self.assertTrue(all("approximation_note" in row for row in reward_payload))
        self.assertTrue(all(row["value"] == row["average_reward"] for row in reward_payload))

        action_payload = json.loads((artifact_dir / "figure_9b_action_distribution_vs_arrival_probability.json").read_text(encoding="utf-8"))
        self.assertEqual(len(action_payload), 15)
        self.assertTrue(all(row["support_status"] == "generated_with_approximation" for row in action_payload))
        self.assertTrue(all(row["metric"] == "action_distribution" for row in action_payload))
        self.assertTrue(all(row["x_axis"] == "action_type" for row in action_payload))
        self.assertTrue(all(row["value"] == row["action_count"] for row in action_payload))

        cpu_payload = json.loads((artifact_dir / "figure_9c_reward_vs_cpu_capacity.json").read_text(encoding="utf-8"))
        self.assertEqual(len(cpu_payload), 18)
        self.assertTrue(all(row["support_status"] == "generated_with_approximation" for row in cpu_payload))
        self.assertTrue(all(row["value"] == row["average_reward"] for row in cpu_payload))

        traffic_payload = json.loads((artifact_dir / "figure_9d_reward_vs_agent_count_traffic.json").read_text(encoding="utf-8"))
        self.assertEqual(len(traffic_payload), 15)
        self.assertTrue(all(row["support_status"] == "generated_with_approximation" for row in traffic_payload))
        self.assertTrue(all(row["value"] == row["average_reward"] for row in traffic_payload))

        rate_payload = json.loads((artifact_dir / "figure_9e_reward_vs_agent_count_data_rate.json").read_text(encoding="utf-8"))
        self.assertEqual(len(rate_payload), 15)
        self.assertTrue(all(row["support_status"] == "generated_with_approximation" for row in rate_payload))
        self.assertTrue(all(row["value"] == row["average_reward"] for row in rate_payload))

        drop_payload = json.loads((artifact_dir / "figure_10f_drop_ratio_vs_timeout.json").read_text(encoding="utf-8"))
        self.assertEqual(len(drop_payload), len(ACTIVE_POLICIES) * 5)
        self.assertTrue(all(0.0 <= row["task_drop_ratio"] <= 1.0 for row in drop_payload))
        self.assertTrue(all(abs(row["task_drop_percent"] - (row["task_drop_ratio"] * 100.0)) < 1e-9 for row in drop_payload))

        audit_payload = json.loads((artifact_dir / "figure_10_output_audit.json").read_text(encoding="utf-8"))
        self.assertEqual(
            [row["figure_id"] for row in audit_payload],
            ["Figure 10a", "Figure 10b", "Figure 10c", "Figure 10d", "Figure 10e", "Figure 10f"],
        )
        self.assertTrue(all(row["audit_status"] == "pass" for row in audit_payload))
        self.assertTrue(all(row["policy_count"] == len(ACTIVE_POLICIES) for row in audit_payload))
        self.assertTrue(all(row["raw_positive_delay_valid"] for row in audit_payload))
        self.assertTrue(all(row["paper_style_negative_delay_valid"] for row in audit_payload))
        self.assertTrue(all(row["drop_ratio_valid"] for row in audit_payload))
        self.assertTrue(all(row["drop_percent_valid"] for row in audit_payload))

        summary_payload = json.loads((artifact_dir / "figure_10_analysis_summary.json").read_text(encoding="utf-8"))
        self.assertEqual(summary_payload["verdict"], "figure_10_outputs_validated")
        self.assertEqual(summary_payload["figures_analyzed"], ["Figure 10a", "Figure 10b", "Figure 10c", "Figure 10d", "Figure 10e", "Figure 10f"])
        self.assertEqual(summary_payload["policies"], list(ACTIVE_POLICIES))
        self.assertTrue(summary_payload["all_audits_passed"])
        self.assertTrue(summary_payload["raw_positive_delay_preserved"])
        self.assertTrue(summary_payload["paper_style_negative_delay_preserved"])
        self.assertTrue(summary_payload["drop_ratio_and_percent_preserved"])
        self.assertEqual(summary_payload["figure_9_boundary"], "Figure 9a-9e remain blocked/reference-only.")

        completion_payload = json.loads((artifact_dir / "feature_089_completion_report.json").read_text(encoding="utf-8"))
        self.assertEqual(completion_payload["completion_status"], "complete")
        self.assertEqual(completion_payload["ready_now_figures"], ["Figure 10a", "Figure 10b", "Figure 10c", "Figure 10d", "Figure 10e", "Figure 10f"])
        self.assertEqual(completion_payload["blocked_figures"], ["Figure 9a", "Figure 9b", "Figure 9c", "Figure 9d", "Figure 9e"])
        self.assertEqual(completion_payload["future_required_figures"], ["Figure 8a", "Figure 8b", "Figure 11"])
        self.assertTrue(completion_payload["figure_9_boundary_preserved"])
        self.assertTrue(completion_payload["training_lstm_boundary_preserved"])

        remaining_payload = json.loads((artifact_dir / "remaining_figure_outputs_report.json").read_text(encoding="utf-8"))
        self.assertEqual(remaining_payload["verdict"], "feature_089_remaining_outputs_partial")
        self.assertTrue(remaining_payload["no_output_sync_tuning"])
        self.assertEqual(remaining_payload["figure_9_status_by_figure"]["Figure 9a"]["status"], "generated_with_approximation")
        self.assertEqual(remaining_payload["figure_9_status_by_figure"]["Figure 9b"]["status"], "generated_with_approximation")
        self.assertEqual(remaining_payload["figure_9_status_by_figure"]["Figure 9c"]["status"], "generated_with_approximation")
        self.assertEqual(remaining_payload["figure_8_status_by_figure"]["Figure 8a"]["support_status"], "not_generated_training_required")
        self.assertEqual(remaining_payload["figure_8_status_by_figure"]["Figure 8b"]["support_status"], "not_generated_training_required")
        self.assertEqual(remaining_payload["figure_11_status"]["support_status"], "not_generated_lstm_training_required")

        trend_payload = json.loads((artifact_dir / "figure_10_trend_analysis.json").read_text(encoding="utf-8"))
        self.assertEqual([row["figure_id"] for row in trend_payload], ["Figure 10a", "Figure 10b", "Figure 10c", "Figure 10d", "Figure 10e", "Figure 10f"])
        self.assertEqual(trend_payload[0]["trend_direction"], "non_monotonic")
        self.assertEqual(trend_payload[2]["trend_direction"], "decreasing")
        self.assertTrue(all(row["paper_numeric_digitization_performed"] is False for row in trend_payload))
        self.assertTrue(all(row["feature_088_repair_recommended"] for row in trend_payload))

        ranking_payload = json.loads((artifact_dir / "figure_10_ranking_analysis.json").read_text(encoding="utf-8"))
        self.assertTrue(all(row["hoodie_rank_band"] == "tied-best" for row in ranking_payload))
        self.assertTrue(all(row["mleo_relation"] == "ties_with_hoodie" for row in ranking_payload))
        self.assertTrue(all(row["feature_088_repair_recommended"] for row in ranking_payload))

        claim_payload = json.loads((artifact_dir / "figure_10_paper_claim_alignment.json").read_text(encoding="utf-8"))
        self.assertEqual(claim_payload[0]["claim_alignment_status"], "not_supported")
        self.assertEqual(claim_payload[2]["claim_alignment_status"], "partial_directional_only")
        self.assertTrue(all(row["numeric_digitization_performed"] is False for row in claim_payload))
        self.assertTrue(all(row["feature_088_repair_recommended"] for row in claim_payload))

        comparison_payload = json.loads((artifact_dir / "figure_10_comparison_analysis_report.json").read_text(encoding="utf-8"))
        self.assertEqual(comparison_payload["verdict"], "figure_10_comparison_analysis_partial")
        self.assertFalse(comparison_payload["paper_numeric_digitization_performed"])
        self.assertEqual(comparison_payload["analysis_mode"], "qualitative_ranking_based")
        self.assertTrue(comparison_payload["feature_088_repair_recommended"])
        self.assertEqual(comparison_payload["claim_alignment_by_figure"]["Figure 10c"], "partial_directional_only")
        self.assertFalse(any(comparison_payload["hoody_matches_paper_claims_by_figure"].values()))

        figure_9a_payload = json.loads((artifact_dir / "figure_9a_reward_vs_arrival_probability.json").read_text(encoding="utf-8"))
        self.assertEqual(len(figure_9a_payload), 15)
        self.assertTrue(all(row["policy"] == "HOODIE" for row in figure_9a_payload))
        self.assertTrue(all(row["support_status"] == "generated_with_approximation" for row in figure_9a_payload))
        self.assertTrue(all(isinstance(row["claim_boundary"], list) and row["claim_boundary"] for row in figure_9a_payload))
        self.assertTrue(all(row["approximation_note"] for row in figure_9a_payload))
        self.assertTrue(all(row["value"] == row["average_reward"] for row in figure_9a_payload))

        figure_9b_payload = json.loads((artifact_dir / "figure_9b_action_distribution_vs_arrival_probability.json").read_text(encoding="utf-8"))
        self.assertEqual(len(figure_9b_payload), 15)
        self.assertTrue(all(row["support_status"] == "generated_with_approximation" for row in figure_9b_payload))
        self.assertTrue(all(row["value"] == row["action_count"] for row in figure_9b_payload))
        self.assertTrue(all("approximation_note" in row for row in figure_9b_payload))

        figure_9d_payload = json.loads((artifact_dir / "figure_9d_reward_vs_agent_count_traffic.json").read_text(encoding="utf-8"))
        self.assertEqual(len(figure_9d_payload), 15)
        self.assertTrue(all(row["support_status"] == "generated_with_approximation" for row in figure_9d_payload))
        self.assertTrue(all(row["value"] == row["average_reward"] for row in figure_9d_payload))

        figure_9e_payload = json.loads((artifact_dir / "figure_9e_reward_vs_agent_count_data_rate.json").read_text(encoding="utf-8"))
        self.assertEqual(len(figure_9e_payload), 15)
        self.assertTrue(all(row["support_status"] == "generated_with_approximation" for row in figure_9e_payload))
        self.assertTrue(all(row["value"] == row["average_reward"] for row in figure_9e_payload))

        figure_8a_status = json.loads((artifact_dir / "figure_8a_learning_rate_convergence_status.json").read_text(encoding="utf-8"))
        self.assertEqual(figure_8a_status["support_status"], "not_generated_training_required")
        self.assertFalse(figure_8a_status["plot_ready_generated"])
        self.assertFalse(figure_8a_status["training_traces_available"])
        self.assertFalse((artifact_dir / "figure_8a_learning_rate_training_curve.csv").exists())
        self.assertFalse((artifact_dir / "figure_8a_learning_rate_training_curve.json").exists())

        figure_8b_status = json.loads((artifact_dir / "figure_8b_discount_factor_convergence_status.json").read_text(encoding="utf-8"))
        self.assertEqual(figure_8b_status["support_status"], "not_generated_training_required")
        self.assertFalse(figure_8b_status["plot_ready_generated"])
        self.assertFalse(figure_8b_status["training_traces_available"])
        self.assertFalse((artifact_dir / "figure_8b_discount_factor_training_curve.csv").exists())
        self.assertFalse((artifact_dir / "figure_8b_discount_factor_training_curve.json").exists())

        figure_11_status = json.loads((artifact_dir / "figure_11_lstm_ablation_status.json").read_text(encoding="utf-8"))
        self.assertEqual(figure_11_status["support_status"], "not_generated_lstm_training_required")
        self.assertFalse(figure_11_status["plot_ready_generated"])
        self.assertFalse(figure_11_status["training_traces_available"])
        self.assertFalse((artifact_dir / "figure_11_lstm_ablation_curve.csv").exists())
        self.assertFalse((artifact_dir / "figure_11_lstm_ablation_curve.json").exists())
