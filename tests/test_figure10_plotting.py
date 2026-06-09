from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.plot_figure10_from_validation import generate_plots


ROOT = Path(__file__).resolve().parents[1]


def _write_validation_fixture(input_dir: Path, *, figure10_data_ready: bool = False, baseline_validation_ready: bool = True) -> None:
    input_dir.mkdir(parents=True, exist_ok=True)
    summary_rows = []
    policies = ["RO", "FLC", "VO", "HO", "BCO", "MLEO"]
    for regime_id, metric_key in (("delay", "mean_average_computation_delay"), ("drop_ratio", "mean_drop_ratio")):
        for idx, policy in enumerate(policies, start=1):
            row = {
                "regime_id": regime_id,
                "policy_name": policy,
                "episodes_requested": 200,
                "episodes_completed": 200,
                "total_tasks": 1000,
                "completed_tasks": 800,
                "dropped_tasks": 150,
                "pending_tasks": 50,
                "mean_average_computation_delay": float(idx) + (0.5 if regime_id == "delay" else 1.5),
                "mean_drop_ratio": round(0.01 * idx, 4),
                "std_average_computation_delay": 0.1,
                "std_drop_ratio": 0.01,
                "policy_readiness_status": "ready",
                "warnings": [],
            }
            summary_rows.append(row)
    summary = {
        "summary_rows": summary_rows,
        "runtime_parameter_diagnostics": [
            {"parameter": "timeout_slots", "paper_value": 20, "runtime_value": 10, "severity": "high"}
        ],
    }
    readiness = {
        "baseline_validation_ready": baseline_validation_ready,
        "figure10_data_ready": figure10_data_ready,
        "baseline_blocking_reasons": [] if baseline_validation_ready else ["mleo_contract_status_ready=false"],
        "figure10_blocking_reasons": ["hoodie_checkpoint_status=unavailable_not_trained"],
        "blocking_reasons": ["hoodie_checkpoint_status=unavailable_not_trained"],
    }
    manifest = {
        "diagnostic_only": True,
        "paper_performance_claims_made": False,
    }
    run_config = {
        "runtime_parameter_diagnostics": summary["runtime_parameter_diagnostics"],
        "figure10_data_ready": figure10_data_ready,
        "baseline_validation_ready": baseline_validation_ready,
    }
    (input_dir / "figure10_policy_metrics_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True))
    (input_dir / "figure10_policy_readiness.json").write_text(json.dumps(readiness, indent=2, sort_keys=True))
    (input_dir / "figure10_validation_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True))
    (input_dir / "figure10_run_config_snapshot.json").write_text(json.dumps(run_config, indent=2, sort_keys=True))


class Figure10PlottingTests(unittest.TestCase):
    def test_plotting_script_writes_expected_files_from_validation_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_dir = Path(tmp) / "input"
            output_dir = Path(tmp) / "output"
            _write_validation_fixture(input_dir)
            metadata = generate_plots(input_dir, output_dir, "baseline-validation-only")
            self.assertTrue((output_dir / "figure10_baseline_delay.png").exists())
            self.assertTrue((output_dir / "figure10_baseline_drop_ratio.png").exists())
            self.assertTrue((output_dir / "figure10_baseline_combined.png").exists())
            self.assertTrue((output_dir / "figure10_baseline_plot_metadata.json").exists())
            self.assertEqual(metadata["plot_scope"], "baseline_validation_only")
            self.assertEqual(metadata["figure_claim"], "not_full_official_figure10")
            self.assertFalse(metadata["hoodie_included"])
            self.assertFalse(metadata["simulation_rerun"])
            self.assertFalse(metadata["figure10_data_ready"])
            self.assertTrue(metadata["baseline_validation_ready"])
            self.assertIn("RO", metadata["policies_plotted"])
            self.assertNotIn("HOODIE", metadata["policies_plotted"])
            self.assertEqual(metadata["runtime_parameter_diagnostics"][0]["parameter"], "timeout_slots")

    def test_plotting_requires_expected_baseline_policies_and_regimes(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_dir = Path(tmp) / "input"
            output_dir = Path(tmp) / "output"
            _write_validation_fixture(input_dir)
            summary_path = input_dir / "figure10_policy_metrics_summary.json"
            summary = json.loads(summary_path.read_text())
            summary["summary_rows"] = summary["summary_rows"][:-1]
            summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True))
            with self.assertRaisesRegex(ValueError, "missing baseline policies"):
                generate_plots(input_dir, output_dir, "baseline-validation-only")

    def test_plotting_requires_both_baseline_regimes(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_dir = Path(tmp) / "input"
            output_dir = Path(tmp) / "output"
            _write_validation_fixture(input_dir)
            summary_path = input_dir / "figure10_policy_metrics_summary.json"
            summary = json.loads(summary_path.read_text())
            summary["summary_rows"] = [row for row in summary["summary_rows"] if row["regime_id"] != "drop_ratio"]
            summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True))
            with self.assertRaisesRegex(ValueError, "missing required regimes"):
                generate_plots(input_dir, output_dir, "baseline-validation-only")

    def test_plotting_requires_summary_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_dir = Path(tmp) / "input"
            output_dir = Path(tmp) / "output"
            _write_validation_fixture(input_dir)
            summary_path = input_dir / "figure10_policy_metrics_summary.json"
            summary = json.loads(summary_path.read_text())
            summary["summary_rows"] = []
            summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True))
            with self.assertRaisesRegex(ValueError, "summary_rows"):
                generate_plots(input_dir, output_dir, "baseline-validation-only")

    def test_plotting_metadata_preserves_readiness_flags(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_dir = Path(tmp) / "input"
            output_dir = Path(tmp) / "output"
            _write_validation_fixture(input_dir, figure10_data_ready=False, baseline_validation_ready=False)
            metadata = generate_plots(input_dir, output_dir, "baseline-validation-only")
            self.assertFalse(metadata["figure10_data_ready"])
            self.assertFalse(metadata["baseline_validation_ready"])
            self.assertIn("Runtime parameter diagnostics exist", metadata["warning"])
            self.assertEqual(metadata["hoodie_reason"], "trained HOODIE checkpoint unavailable")

    def test_plotting_never_includes_hoodie(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_dir = Path(tmp) / "input"
            output_dir = Path(tmp) / "output"
            _write_validation_fixture(input_dir)
            metadata = generate_plots(input_dir, output_dir, "baseline-validation-only")
            self.assertFalse(metadata["hoodie_included"])
            self.assertNotIn("HOODIE", metadata["policies_plotted"])

    def test_plotting_script_does_not_reference_simulator_entry_points(self):
        source = (ROOT / "scripts" / "plot_figure10_from_validation.py").read_text()
        self.assertNotIn("main.py", source)
        self.assertNotIn("run_figure10_validation", source)
        self.assertNotIn("training.train_phase3", source)


if __name__ == "__main__":
    unittest.main()
