from __future__ import annotations

import unittest

from src.analysis.reward_equation_terminal_reward_contract.report import build_reward_contract_report


class RewardEquationTerminalRewardContractAggregationTest(unittest.TestCase):
    def test_aggregation_classification_is_honest(self) -> None:
        report = build_reward_contract_report()
        aggregation = report.aggregation_contract
        self.assertEqual(aggregation["per_agent"], "paper_backed")
        self.assertEqual(aggregation["reported_cumulative_reward"], "artifact_backed")
        self.assertEqual(aggregation["average_across_distributed_agents"], "artifact_backed")
        self.assertEqual(aggregation["exact_reduction_order"], "assumption_backed")


if __name__ == "__main__":
    unittest.main()
