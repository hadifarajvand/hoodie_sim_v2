from __future__ import annotations

import unittest

from src.environment.paper_link_delay import build_link_delay_contract


class PaperLinkDelayTests(unittest.TestCase):
    def test_per_link_override_supported(self) -> None:
        horizontal = build_link_delay_contract(
            source_node_id="1",
            destination_node_id="2",
            link_type="horizontal",
            task_size_mbits=3.0,
            data_rate_mbps=30.0,
            link_delay_source="override",
        )
        vertical = build_link_delay_contract(
            source_node_id="1",
            destination_node_id="cloud",
            link_type="vertical",
            task_size_mbits=3.0,
            data_rate_mbps=10.0,
            link_delay_source="override",
        )
        self.assertGreaterEqual(vertical.transmission_delay_slots, horizontal.transmission_delay_slots)
        self.assertEqual(horizontal.link_delay_source, "override")


if __name__ == "__main__":
    unittest.main()

