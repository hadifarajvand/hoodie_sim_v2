from __future__ import annotations

import unittest
from dataclasses import dataclass

from src.echo_queue_ordering import construct_ert_order


@dataclass(frozen=True)
class Item:
    item_id: int
    arrival: int
    deadline: int
    service: int
    downstream: int = 0


class ConstructiveERTOrderingTests(unittest.TestCase):
    def test_selects_smallest_nonnegative_ert_at_each_position(self) -> None:
        items = [
            Item(1, arrival=0, deadline=10, service=2),
            Item(2, arrival=1, deadline=5, service=2),
            Item(3, arrival=2, deadline=8, service=1),
        ]
        result = construct_ert_order(
            items,
            current_slot=3,
            residual_source_slots=0,
            service_slots=lambda item: item.service,
            downstream_slots=lambda item: item.downstream,
            deadline_slot=lambda item: item.deadline,
            arrival_slot=lambda item: item.arrival,
            stable_id=lambda item: item.item_id,
        )

        self.assertEqual([item.item_id for item in result.ordered_items], [2, 3, 1])
        self.assertEqual(result.candidate_evaluations, 6)
        self.assertTrue(all(estimate.ert_slots >= 0 for estimate in result.estimates))

    def test_all_late_case_uses_minimum_lateness_not_most_negative_ert(self) -> None:
        items = [
            Item(1, arrival=0, deadline=3, service=5),
            Item(2, arrival=1, deadline=4, service=2),
        ]
        result = construct_ert_order(
            items,
            current_slot=5,
            residual_source_slots=0,
            service_slots=lambda item: item.service,
            downstream_slots=lambda item: 0,
            deadline_slot=lambda item: item.deadline,
            arrival_slot=lambda item: item.arrival,
            stable_id=lambda item: item.item_id,
        )

        self.assertEqual(result.ordered_items[0].item_id, 2)
        self.assertEqual(result.estimates[0].lateness_slots, 2)

    def test_active_residual_is_included_without_reordering_active_work(self) -> None:
        items = [
            Item(1, arrival=1, deadline=7, service=1, downstream=2),
            Item(2, arrival=2, deadline=12, service=2, downstream=1),
        ]
        result = construct_ert_order(
            items,
            current_slot=4,
            residual_source_slots=3,
            service_slots=lambda item: item.service,
            downstream_slots=lambda item: item.downstream,
            deadline_slot=lambda item: item.deadline,
            arrival_slot=lambda item: item.arrival,
            stable_id=lambda item: item.item_id,
        )

        first = result.estimates[0]
        self.assertEqual(first.completion_slot, 9)
        self.assertEqual(first.item.item_id, 1)


if __name__ == "__main__":
    unittest.main()
