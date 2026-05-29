from __future__ import annotations

import unittest

from src.environment.paper_traffic import build_bernoulli_arrivals


class PaperBernoulliArrivalsTests(unittest.TestCase):
    def test_same_seed_is_reproducible(self) -> None:
        first = build_bernoulli_arrivals(seed=11, arrival_probability_p=0.5)
        second = build_bernoulli_arrivals(seed=11, arrival_probability_p=0.5)
        self.assertEqual(first.arrivals_by_slot_agent, second.arrivals_by_slot_agent)

    def test_different_seed_can_differ(self) -> None:
        first = build_bernoulli_arrivals(seed=11, arrival_probability_p=0.5)
        second = build_bernoulli_arrivals(seed=12, arrival_probability_p=0.5)
        self.assertNotEqual(first.arrivals_by_slot_agent, second.arrivals_by_slot_agent)

    def test_probability_zero_and_one_edges(self) -> None:
        zero = build_bernoulli_arrivals(seed=1, arrival_probability_p=0.0, slot_count=2, edge_agent_count=3)
        one = build_bernoulli_arrivals(seed=1, arrival_probability_p=1.0, slot_count=2, edge_agent_count=3)
        self.assertEqual(zero.generated_task_count, 0)
        self.assertEqual(one.generated_task_count, 6)


if __name__ == "__main__":
    unittest.main()

