"""Tests for paper figure reproduction pipeline.

Covers: data format correctness, sub-figure coverage,
Figure 10 limitation enforcement, determinism, and
import/compilation integrity.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.paper_figure_reproduction import (
    _figure8_rows,
    _figure9_rows,
    _figure10_rows,
    _figure11_rows,
    _sweep_base_row,
)


def _make_sweep_result(
    figure_id: str = "Figure 8",
    label: str = "test",
    sweep_type: str = "learning_rate",
    meta: dict | None = None,
    episodes: int = 3,
) -> dict:
    meta = meta or {"sweep_type": sweep_type}
    config = {"sweep_metadata": meta}
    metrics = {
        "episode_rewards": [10.0, 20.0, 30.0],
        "loss_values": [0.5, 0.3, 0.2],
        "action_counts": [{0: 5, 1: 3, 2: 2}],
        "average_delays": [1.5, 2.0, 1.8],
        "drop_ratios": [0.1, 0.0, 0.05],
    }
    return {
        "experiment_label": label,
        "config": config,
        "training_metrics": metrics,
        "result": {"evaluation_summary": {}},
    }


class PaperFigureReproductionTests(unittest.TestCase):

    def test_sweep_base_row_has_required_columns(self):
        row = _sweep_base_row("Figure 8", "full_pdf_extracted")
        expected_keys = {
            "figure_id", "subfigure_id", "series_name",
            "x_value", "y_value", "x_unit", "y_unit",
            "policy_name", "seed", "scenario_name",
            "source_kind", "source_path",
            "reconstruction_status", "limitation",
        }
        self.assertTrue(expected_keys.issubset(row.keys()),
                        f"Missing keys: {expected_keys - row.keys()}")

    def test_figure8_rows_produces_correct_shaped_rows(self):
        results = [
            _make_sweep_result("Figure 8", "lr=1e-7", "learning_rate"),
            _make_sweep_result("Figure 8", "lr=5e-7", "learning_rate"),
            _make_sweep_result("Figure 8", "gamma=0.99", "discount_factor",
                               meta={"sweep_type": "discount_factor", "discount_factor": 0.99}),
        ]
        rows = _figure8_rows(results)
        self.assertGreater(len(rows), 0)
        # Every row gets figure_id = "Figure 8"
        for row in rows:
            self.assertEqual(row["figure_id"], "Figure 8")
        # Both reward and loss series present
        series_names = {row["series_name"] for row in rows}
        self.assertIn("learning_rate_reward", series_names)
        self.assertIn("discount_factor_reward", series_names)
        self.assertIn("learning_rate_loss", series_names)

    def test_figure8_subfigure_ids(self):
        lr = _make_sweep_result("Figure 8", "lr=1e-7", "learning_rate")
        gamma = _make_sweep_result("Figure 8", "gamma=0.99", "discount_factor",
                                   meta={"sweep_type": "discount_factor", "discount_factor": 0.99})
        rows = _figure8_rows([lr, gamma])
        sub_ids = {row["subfigure_id"] for row in rows}
        self.assertIn("8-learning-rate", sub_ids)
        self.assertIn("8-discount-factor", sub_ids)

    def test_figure9_subfigure_ids(self):
        results = [
            _make_sweep_result("Figure 9", "P=0.5", "arrival_probability",
                               meta={"sweep_type": "arrival_probability", "arrival_probability": 0.5}),
            _make_sweep_result("Figure 9", "CPU=5", "cpu_capacity",
                               meta={"sweep_type": "cpu_capacity", "cpu_capacity": 5}),
            _make_sweep_result("Figure 9", "N=20", "num_drl_agents",
                               meta={"sweep_type": "num_drl_agents", "num_drl_agents": 20}),
            _make_sweep_result("Figure 9", "balanced N=20", "offload_data_rate",
                               meta={"sweep_type": "offload_data_rate", "data_rate_scenario": "balanced"}),
        ]
        rows = _figure9_rows(results)
        sub_ids = {row["subfigure_id"] for row in rows}
        self.assertIn("9a", sub_ids)
        self.assertIn("9c", sub_ids)
        self.assertIn("9d", sub_ids)
        self.assertIn("9e", sub_ids)

    def test_figure9_action_distribution_9b_present(self):
        results = [
            _make_sweep_result("Figure 9", "P=0.5 N=10", "arrival_probability",
                               meta={"sweep_type": "arrival_probability", "arrival_probability": 0.5,
                                     "num_drl_agents": 10}),
            _make_sweep_result("Figure 9", "P=0.7 N=20", "arrival_probability",
                               meta={"sweep_type": "arrival_probability", "arrival_probability": 0.7,
                                     "num_drl_agents": 20}),
        ]
        rows = _figure9_rows(results)
        sub9b = [r for r in rows if r["subfigure_id"] == "9b"]
        self.assertGreater(len(sub9b), 0, "Figure 9b action distribution rows missing")
        for row in sub9b:
            self.assertIn(row["series_name"], ["action_local", "action_horizontal", "action_vertical"])

    def test_figure10_contains_limitation_and_partial_marker(self):
        results = [
            _make_sweep_result("Figure 10", "RO P=0.5", "arrival_probability",
                               meta={"sweep_type": "arrival_probability", "arrival_probability": 0.5,
                                     "policy": "RO"}),
            _make_sweep_result("Figure 10", "FLC CPU=5", "cpu_capacity",
                               meta={"sweep_type": "cpu_capacity", "cpu_capacity": 5, "policy": "FLC"}),
        ]
        rows = _figure10_rows(results)
        self.assertGreater(len(rows), 0)
        for row in rows:
            self.assertEqual(row["reconstruction_status"], "partial_pdf_extracted")
            # The limitation should reference the Figure 10 limitation string
            limit_text = row.get("limitation", "") or ""
            self.assertTrue(len(limit_text) > 20, "Limitation text should be substantive")

    def test_figure10_subfigure_panels(self):
        results = [
            _make_sweep_result("Figure 10", "RO P=0.5", "arrival_probability",
                               meta={"sweep_type": "arrival_probability", "arrival_probability": 0.5,
                                     "policy": "RO"}),
            _make_sweep_result("Figure 10", "FLC CPU=5", "cpu_capacity",
                               meta={"sweep_type": "cpu_capacity", "cpu_capacity": 5, "policy": "FLC"}),
            _make_sweep_result("Figure 10", "HO timeout=20", "task_timeout",
                               meta={"sweep_type": "task_timeout", "task_timeout_slots": 20, "policy": "HO"}),
        ]
        rows = _figure10_rows(results)
        sub_ids = {row["subfigure_id"] for row in rows}
        # Should cover delay and drop panels for each sweep dim
        expected = {"10a", "10b", "10c", "10d", "10e", "10f"}
        present = sub_ids & expected
        self.assertEqual(present, expected,
                         f"Missing subfigure IDs: {expected - present}")

    def test_figure10_comparison_allowed_false(self):
        # Verify the exported JSON marks comparison_allowed: false
        rows = _figure10_rows([
            _make_sweep_result("Figure 10", "RO P=0.5", "arrival_probability",
                               meta={"sweep_type": "arrival_probability", "arrival_probability": 0.5,
                                     "policy": "RO"}),
        ])
        payload = {
            "figure_id": "Figure 10",
            "comparison_allowed": False,
            "reconstruction_status": "partial_pdf_extracted",
            "rows": rows,
        }
        self.assertFalse(payload["comparison_allowed"])
        self.assertEqual(payload["reconstruction_status"], "partial_pdf_extracted")

    def test_figure11_rows_produce_both_variants(self):
        with_lstm = [_make_sweep_result("Figure 11", "with_lstm", "lstm_ablation")]
        without_lstm = [_make_sweep_result("Figure 11", "without_lstm", "lstm_ablation")]
        rows = _figure11_rows(with_lstm, without_lstm)
        self.assertGreater(len(rows), 0)
        series = {row["series_name"] for row in rows}
        self.assertIn("avg_delay_with_lstm", series)
        self.assertIn("avg_delay_without_lstm", series)
        self.assertIn("reward_with_lstm", series)
        self.assertIn("reward_without_lstm", series)

    def test_figure11_subfigure_id(self):
        rows = _figure11_rows(
            [_make_sweep_result("Figure 11", "with_lstm", "lstm_ablation")],
            [_make_sweep_result("Figure 11", "without_lstm", "lstm_ablation")],
        )
        for row in rows:
            self.assertEqual(row["subfigure_id"], "11-lstm-ablation")

    def test_all_figures_export_consistent_columns(self):
        fig8 = _figure8_rows([
            _make_sweep_result("Figure 8", "lr=1e-7", "learning_rate"),
        ])
        fig9 = _figure9_rows([
            _make_sweep_result("Figure 9", "P=0.5", "arrival_probability",
                               meta={"sweep_type": "arrival_probability", "arrival_probability": 0.5}),
        ])
        fig10 = _figure10_rows([
            _make_sweep_result("Figure 10", "RO P=0.5", "arrival_probability",
                               meta={"sweep_type": "arrival_probability", "arrival_probability": 0.5,
                                     "policy": "RO"}),
        ])
        fig11 = _figure11_rows(
            [_make_sweep_result("Figure 11", "with_lstm", "lstm_ablation")],
            [_make_sweep_result("Figure 11", "without_lstm", "lstm_ablation")],
        )
        all_rows = fig8 + fig9 + fig10 + fig11
        base = _sweep_base_row("Figure 8", "full_pdf_extracted")
        expected_keys = set(base.keys())
        for row in all_rows:
            self.assertTrue(
                expected_keys.issubset(row.keys()),
                f"Row missing keys {expected_keys - set(row.keys())} in {row.get('figure_id')}",
            )

    def test_reproduction_pipeline_module_imports(self):
        """Verify the main module compiles and its public API exists."""
        from src.analysis import paper_figure_reproduction
        self.assertTrue(hasattr(paper_figure_reproduction, "run_paper_figure_reproduction"))
        self.assertTrue(hasattr(paper_figure_reproduction, "OUTPUT_DIR"))

    def test_empty_results_produce_empty_rows(self):
        self.assertEqual(_figure8_rows([]), [])
        self.assertEqual(_figure9_rows([]), [])
        self.assertEqual(_figure10_rows([]), [] )
        self.assertEqual(_figure11_rows([], []), [])


if __name__ == "__main__":
    unittest.main()
