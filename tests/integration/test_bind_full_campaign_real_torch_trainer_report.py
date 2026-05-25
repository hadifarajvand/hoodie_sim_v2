from __future__ import annotations

import json
import unittest

from src.analysis.bind_full_campaign_real_torch_trainer import generate_bind_full_campaign_real_torch_trainer_artifacts
from src.analysis.bind_full_campaign_real_torch_trainer.config import REPORT_JSON, REPORT_MD


class BindFullCampaignRealTorchTrainerReportTests(unittest.TestCase):
    def test_report_artifacts_are_written(self) -> None:
        report, json_path, md_path = generate_bind_full_campaign_real_torch_trainer_artifacts()
        self.assertEqual(json_path, REPORT_JSON)
        self.assertEqual(md_path, REPORT_MD)
        self.assertTrue(json_path.exists())
        self.assertTrue(md_path.exists())
        self.assertEqual(json.loads(json_path.read_text(encoding="utf-8")), report.to_dict())

    def test_markdown_report_records_real_binding(self) -> None:
        generate_bind_full_campaign_real_torch_trainer_artifacts()
        text = REPORT_MD.read_text(encoding="utf-8")
        self.assertIn("real_torch_trainer_binding_repair_passed", text)
        self.assertIn("DDQNTrainer", text)


if __name__ == "__main__":
    unittest.main()
