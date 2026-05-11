from __future__ import annotations

import unittest

from src.analysis.link_rate_transmission_delay_contract.report import build_link_rate_contract_report
from src.environment.link_rate_config import LinkRateConfig


class LinkRateScopeGuardTest(unittest.TestCase):
    def test_report_schema_and_unsupported_controls_are_explicit(self) -> None:
        report = build_link_rate_contract_report().to_dict()
        self.assertEqual(report["paper_backed_defaults"]["horizontal_data_rate_mbps"], 30.0)
        self.assertEqual(report["paper_backed_defaults"]["vertical_data_rate_mbps"], 10.0)
        self.assertEqual(report["paper_backed_defaults"]["cloud_data_rate_status"], "unrecoverable")
        self.assertEqual(report["link_rate_controls"]["public_config_entrypoint"], "src/environment/link_rate_config.py")
        unsupported = {item["control_name"]: item for item in report["unsupported_controls"]}
        self.assertIn("per_edge_link_rates", unsupported)
        self.assertIn("cloud_data_rate", unsupported)
        self.assertEqual(unsupported["per_edge_link_rates"]["reason"], "Topology evidence is unrecoverable; non-fabricated per-edge control remains unsupported.")

    def test_config_entrypoint_exposes_only_supported_public_defaults(self) -> None:
        config = LinkRateConfig(horizontal_data_rate_mbps=30.0, vertical_data_rate_mbps=10.0, slot_duration_seconds=1.0)
        self.assertEqual(config.supported_entrypoint(), "src/environment/link_rate_config.py")
        self.assertEqual(config.horizontal_data_rate_bps, 30_000_000.0)
        self.assertEqual(config.vertical_data_rate_bps, 10_000_000.0)


if __name__ == "__main__":
    unittest.main()
