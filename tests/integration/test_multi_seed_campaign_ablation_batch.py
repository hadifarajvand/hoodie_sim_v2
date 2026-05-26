from __future__ import annotations

import json
import unittest

from src.analysis.multi_seed_campaign_ablation_batch import generate_multi_seed_campaign_ablation_batch_artifacts
from src.analysis.multi_seed_campaign_ablation_batch.config import ABLATION_RESULTS_JSON, MULTI_SEED_AGGREGATION_JSON, MULTI_SEED_GATE_JSON, MULTI_SEED_RESULTS_JSON


class MultiSeedCampaignAblationBatchIntegrationTests(unittest.TestCase):
    def test_artifacts_are_written(self) -> None:
        report, json_path, md_path = generate_multi_seed_campaign_ablation_batch_artifacts()
        self.assertTrue(json_path.exists())
        self.assertTrue(md_path.exists())
        self.assertTrue(MULTI_SEED_GATE_JSON.exists())
        self.assertTrue(MULTI_SEED_RESULTS_JSON.exists())
        self.assertTrue(MULTI_SEED_AGGREGATION_JSON.exists())
        self.assertTrue(ABLATION_RESULTS_JSON.exists())
        self.assertEqual(json.loads(json_path.read_text(encoding="utf-8")), report.to_dict())


if __name__ == "__main__":
    unittest.main()
