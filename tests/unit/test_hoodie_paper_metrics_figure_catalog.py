from __future__ import annotations

import json
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
                path.unlink()
        report = generate_artifacts(artifact_dir)
        self.assertEqual(report.verdict, "paper_metrics_catalog_partial")
        self.assertTrue((artifact_dir / "feature_089_report.json").exists())
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
        self.assertEqual(len(reward_payload), 1)
        self.assertEqual(reward_payload[0]["policy"], "HOODIE")
        self.assertEqual(reward_payload[0]["status"], "blocked_by_simulator_support")
        self.assertEqual(reward_payload[0]["sweep_values"], [0.1, 0.3, 0.5, 0.7, 0.9])
        self.assertIn("Reference-only Figure 9 behavior output", reward_payload[0]["notes"])

        action_payload = json.loads((artifact_dir / "figure_9b_action_distribution_vs_arrival_probability.json").read_text(encoding="utf-8"))
        self.assertEqual(len(action_payload), 1)
        self.assertEqual(action_payload[0]["status"], "blocked_by_simulator_support")
        self.assertEqual(action_payload[0]["metric"], "action_distribution")
        self.assertEqual(action_payload[0]["x_axis"], "action_type")
        self.assertIn("trained HOODIE DRL/LSTM", action_payload[0]["notes"])

        traffic_payload = json.loads((artifact_dir / "figure_9d_reward_vs_agent_count_traffic.json").read_text(encoding="utf-8"))
        self.assertEqual(len(traffic_payload), 1)
        self.assertEqual(traffic_payload[0]["status"], "blocked_by_simulator_support")
        self.assertEqual(traffic_payload[0]["sweep_values"], [10, 15, 20, 25, 30])

        rate_payload = json.loads((artifact_dir / "figure_9e_reward_vs_agent_count_data_rate.json").read_text(encoding="utf-8"))
        self.assertEqual(len(rate_payload), 1)
        self.assertEqual(rate_payload[0]["status"], "blocked_by_simulator_support")
        self.assertEqual(rate_payload[0]["sweep_values"], [10, 15, 20, 25, 30])

        drop_payload = json.loads((artifact_dir / "figure_10f_drop_ratio_vs_timeout.json").read_text(encoding="utf-8"))
        self.assertEqual(len(drop_payload), len(ACTIVE_POLICIES) * 5)
        self.assertTrue(all(0.0 <= row["task_drop_ratio"] <= 1.0 for row in drop_payload))
        self.assertTrue(all(abs(row["task_drop_percent"] - (row["task_drop_ratio"] * 100.0)) < 1e-9 for row in drop_payload))
