from __future__ import annotations

import json
from pathlib import Path
import unittest

from paper_contract import build_paper_table4_contract, validate_hyperparameters_against_contract


ROOT = Path(__file__).resolve().parents[1]


class PaperContractTests(unittest.TestCase):
    def test_contract_matches_ocr_and_conversions(self) -> None:
        contract = build_paper_table4_contract()
        self.assertEqual(contract.source, "resources/papers/hoodie/ocr/merged.tex")
        self.assertEqual(contract.delta_sec, 0.1)
        self.assertEqual(contract.action_slots, 100)
        self.assertEqual(contract.drain_slots, 10)
        self.assertEqual(contract.validation_episodes, 200)
        self.assertEqual(contract.task_arrival_probability, 0.5)
        self.assertEqual(contract.number_of_eas, 20)
        self.assertEqual(contract.timeout_slots, 20)
        self.assertEqual(contract.timeout_sec, 2.0)
        self.assertEqual(contract.private_cpu_ghz, 5.0)
        self.assertEqual(contract.public_cpu_ghz, 5.0)
        self.assertEqual(contract.cloud_cpu_ghz, 30.0)
        self.assertEqual(contract.horizontal_rate_mbps, 30.0)
        self.assertEqual(contract.vertical_rate_mbps, 10.0)
        self.assertEqual(contract.task_sizes_mbits[0], 2.0)
        self.assertEqual(contract.task_sizes_mbits[-1], 5.0)
        self.assertEqual(contract.processing_density_gcycles_per_mbit, 0.297)
        self.assertEqual(contract.converted_runtime_units["private_cpu_cycles_per_slot"], 500000000.0)
        self.assertEqual(contract.converted_runtime_units["cloud_cpu_cycles_per_slot"], 3000000000.0)
        self.assertEqual(contract.converted_runtime_units["horizontal_mbits_per_slot"], 3.0)
        self.assertEqual(contract.converted_runtime_units["vertical_mbits_per_slot"], 1.0)

    def test_hyperparameter_validation_reports_real_mismatches(self) -> None:
        diagnostics = validate_hyperparameters_against_contract()
        names = {item["parameter"] for item in diagnostics}
        self.assertIn("timeout_slots", names)
        self.assertIn("drop_penalty", names)
        self.assertIn("cloud_cpu_ghz", names)
        self.assertTrue(all(item["severity"] in {"medium", "high"} for item in diagnostics))

    def test_contract_json_exists(self) -> None:
        contract_path = ROOT / "config" / "paper_table4_contract.json"
        payload = json.loads(contract_path.read_text())
        self.assertEqual(payload["delta_sec"], 0.1)
        self.assertEqual(payload["validation_episodes"], 200)
        self.assertEqual(payload["converted_runtime_units"]["vertical_mbits_per_slot"], 1.0)


if __name__ == "__main__":
    unittest.main()
