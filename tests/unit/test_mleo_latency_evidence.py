from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.hoodie_runtime_evaluation_runner.report import build_feature_085_report
from src.analysis.hoodie_runtime_evaluation_runner.runner import generate_hoodie_runtime_evaluation_artifacts
from src.policies.policy_interface import PolicyContext
from src.evaluation.policy_registry import PolicyRegistry


class MinimumLatencyEstimateEvidenceTests(unittest.TestCase):
    def test_mleo_selects_minimum_total_delay_not_minimum_queue_length(self) -> None:
        policy = PolicyRegistry.resolve("MLEO")
        context = PolicyContext(
            observation={
                "mleo_delay_candidates": {
                    "local": {
                        "queue_delay": 1.0,
                        "transmission_delay": 0.0,
                        "compute_delay": 7.0,
                        "total_delay": 8.0,
                    },
                    "horizontal": {
                        "queue_delay": 4.0,
                        "transmission_delay": 0.2,
                        "compute_delay": 0.8,
                        "total_delay": 1.0,
                    },
                    "vertical": {
                        "queue_delay": 3.0,
                        "transmission_delay": 0.3,
                        "compute_delay": 2.7,
                        "total_delay": 3.0,
                    },
                }
            },
            legal_action_mask={"local": True, "horizontal": True, "vertical": True},
            trace_history=("mleo-evidence",),
        )

        action = policy.choose_action(context)
        self.assertEqual(action, "horizontal")
        self.assertIsNone(policy.last_fallback_reason)

        candidates = {candidate.action_family: candidate for candidate in policy.last_candidates}
        self.assertEqual(candidates["local"].queue_delay, 1.0)
        self.assertEqual(candidates["horizontal"].queue_delay, 4.0)
        self.assertEqual(candidates["vertical"].queue_delay, 3.0)
        self.assertEqual(candidates["local"].total_delay, 8.0)
        self.assertEqual(candidates["horizontal"].total_delay, 1.0)
        self.assertEqual(candidates["vertical"].total_delay, 3.0)
        self.assertEqual(min(candidates.values(), key=lambda candidate: candidate.queue_delay).action_family, "local")
        self.assertEqual(min(candidates.values(), key=lambda candidate: candidate.total_delay).action_family, "horizontal")

    def test_hoodie_mleo_tie_is_documented_with_scenario_level_action_counts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "artifacts/feature_085_full_audit"
            report, paths, manifest = generate_hoodie_runtime_evaluation_artifacts(output_dir)

            raw_payload = json.loads(paths["raw_rows.json"].read_text(encoding="utf-8"))
            rows = raw_payload["rows"]
            by_policy: dict[str, list[dict[str, object]]] = {}
            for row in rows:
                by_policy.setdefault(str(row["policy"]), []).append(row)

            hoodie_rows = by_policy["HOODIE"]
            mleo_rows = by_policy["MLEO"]
            same = 0
            different = 0
            per_scenario: dict[str, dict[str, object]] = {}
            for left, right in zip(hoodie_rows, mleo_rows):
                scenario_name = str(left["scenario_name"])
                scenario_counts = per_scenario.setdefault(scenario_name, {"same": 0, "different": 0, "pairs": {}})
                if left["selected_action"] == right["selected_action"]:
                    same += 1
                    scenario_counts["same"] = int(scenario_counts["same"]) + 1
                else:
                    different += 1
                    scenario_counts["different"] = int(scenario_counts["different"]) + 1
                    pairs = scenario_counts["pairs"]
                    pair_key = f"{left['selected_action']}->{right['selected_action']}"
                    pairs[pair_key] = int(pairs.get(pair_key, 0)) + 1

            self.assertEqual(same, 1080)
            self.assertEqual(different, 432)
            self.assertEqual(
                {name for name, counts in per_scenario.items() if int(counts["different"]) == 0},
                {
                    "cloud_vertical_fallback",
                    "illegal_horizontal_destination_attempt",
                    "legal_horizontal_offload",
                    "light_load_no_deadline_pressure",
                    "mixed_local_horizontal_cloud_candidates",
                },
            )
            self.assertEqual(
                {name for name, counts in per_scenario.items() if int(counts["different"]) > 0},
                {"tight_deadline_pressure", "timeout_drop_case"},
            )
            for scenario_name in ("tight_deadline_pressure", "timeout_drop_case"):
                counts = per_scenario[scenario_name]
                self.assertEqual(int(counts["same"]), 0)
                self.assertEqual(int(counts["different"]), 216)
                self.assertEqual(counts["pairs"], {"vertical->local": 216})

            evidence_lines = report.policy_action_evidence
            self.assertTrue(evidence_lines)
            joined = "\n".join(evidence_lines)
            self.assertIn("HOODIE and MLEO match in 1080 of 1512 raw rows and differ in 432 rows.", joined)
            self.assertIn("tight_deadline_pressure", joined)
            self.assertIn("timeout_drop_case", joined)
            self.assertIn("vertical->local x216", joined)

            report_payload = json.loads(paths["feature_085_audit_report.json"].read_text(encoding="utf-8"))
            manifest_payload = json.loads(paths["execution_manifest.json"].read_text(encoding="utf-8"))
            self.assertEqual(report_payload["policy_action_evidence"], list(evidence_lines))
            self.assertEqual(manifest_payload["policy_action_evidence"], list(evidence_lines))
            self.assertEqual(manifest["policy_action_evidence"], list(evidence_lines))
            self.assertIn("HOODIE/MLEO Tie Evidence", paths["feature_085_audit_report.md"].read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
