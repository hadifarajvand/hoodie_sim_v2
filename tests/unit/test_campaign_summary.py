from __future__ import annotations

import unittest

from src.evaluation.campaign_runner import _aggregate_records, _group_records


class CampaignSummaryTests(unittest.TestCase):
    def _records(self) -> list[dict[str, object]]:
        return [
            {
                "policy_name": "ADAPTIVE",
                "scenario_name": "moderate",
                "final_metrics": {
                    "average_delay": 2.0,
                    "drop_ratio": 0.1,
                    "throughput": 5,
                    "completed_tasks": 4,
                    "dropped_tasks": 1,
                    "total_tasks": 5,
                },
            },
            {
                "policy_name": "FLC",
                "scenario_name": "paper_default",
                "final_metrics": {
                    "average_delay": 4.0,
                    "drop_ratio": 0.2,
                    "throughput": 7,
                    "completed_tasks": 6,
                    "dropped_tasks": 1,
                    "total_tasks": 7,
                },
            },
        ]

    def test_aggregate_all_results(self) -> None:
        summary = _aggregate_records(self._records())
        self.assertEqual(summary["result_count"], 2)
        self.assertEqual(summary["total_throughput"], 12)
        self.assertEqual(summary["total_completed_tasks"], 10)
        self.assertEqual(summary["total_dropped_tasks"], 2)
        self.assertEqual(summary["total_tasks"], 12)
        self.assertAlmostEqual(summary["mean_average_delay"], 3.0)
        self.assertAlmostEqual(summary["mean_drop_ratio"], 0.15)

    def test_group_by_policy_is_deterministic(self) -> None:
        grouped = _group_records(self._records(), "policy_name")
        self.assertEqual([item["policy_name"] for item in grouped], ["ADAPTIVE", "FLC"])
        self.assertEqual(grouped[0]["result_count"], 1)
        self.assertEqual(grouped[1]["result_count"], 1)

    def test_group_by_scenario_is_deterministic(self) -> None:
        grouped = _group_records(self._records(), "scenario_name")
        self.assertEqual([item["scenario_name"] for item in grouped], ["moderate", "paper_default"])

    def test_empty_records_return_zero_summary(self) -> None:
        summary = _aggregate_records([])
        self.assertEqual(summary["result_count"], 0)
        self.assertEqual(summary["total_tasks"], 0)


if __name__ == "__main__":
    unittest.main()

