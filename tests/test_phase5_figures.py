from __future__ import annotations

import csv
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / ".venvmac" / "bin" / "python"


def _write_phase4_fixture(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    (path / "phase4_validation_report.json").write_text(
        json.dumps(
            {
                "paper_performance_claims_made": False,
                "invalid_action_ratio": 0.0,
                "predicted_next_load_method_counts": {"persistence_baseline": 2},
            }
        )
    )
    (path / "episode_metrics_summary.csv").write_text(
        "episode_id,total_tasks,completed_tasks,dropped_tasks,pending_tasks,drop_ratio,completion_ratio,average_latency,average_waiting_time,average_service_time,average_queue_length,total_reward,mean_reward\n"
        "0,10,7,2,1,0.2,0.7,1,0.3,0.4,1.2,-1,-0.1\n"
        "1,10,6,3,1,0.3,0.6,1.2,0.4,0.5,1.4,-2,-0.2\n"
    )
    (path / "policy_action_summary.csv").write_text(
        "metric,value\n"
        "action_distribution_by_type,\"{\\\"local\\\": 1, \\\"horizontal_edge\\\": 2, \\\"vertical_cloud\\\": 3}\"\n"
    )
    (path / "state_lstm_summary.json").write_text(
        json.dumps(
            {
                "state_dim_max": 129,
                "state_dim_min": 129,
                "active_load_vector_length": 21,
                "predicted_next_load_method_counts": {"persistence_baseline": 2},
                "paper_lstm_forecast_false_count": 2,
            }
        )
    )
    (path / "readiness_matrix.csv").write_text("criterion,expected,observed,status,evidence,next_action\n")
    (path / "phase4_validation_report.md").write_text("# stub\n")


class Phase5FigureTests(unittest.TestCase):
    def test_figure_generation_succeeds_with_synthetic_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_dir = Path(tmp) / "phase4"
            out_dir = Path(tmp) / "phase5"
            _write_phase4_fixture(input_dir)
            result = subprocess.run(
                [
                    str(PYTHON),
                    "phase5_generate_figures.py",
                    "--input-dir",
                    str(input_dir),
                    "--output-dir",
                    str(out_dir),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            manifest = json.loads((out_dir / "figure_manifest.json").read_text())
            self.assertTrue(manifest["diagnostic_only"])
            self.assertFalse(manifest["paper_performance_claims_made"])
            self.assertTrue((out_dir / "figures" / "figure_8_episode_outcomes.png").exists())
            self.assertTrue((out_dir / "figures" / "figure_9_latency_wait_service.png").exists())
            self.assertTrue((out_dir / "figures" / "figure_10_action_legality.png").exists())
            self.assertTrue((out_dir / "figures" / "figure_11_state_lstm_readiness.png").exists())
            self.assertTrue((out_dir / "data" / "figure_8_episode_outcomes.csv").exists())
            self.assertTrue((out_dir / "data" / "figure_9_latency_wait_service.csv").exists())
            self.assertTrue((out_dir / "data" / "figure_10_action_distribution.csv").exists())
            self.assertTrue((out_dir / "data" / "figure_11_state_lstm_readiness.csv").exists())


if __name__ == "__main__":
    unittest.main()
