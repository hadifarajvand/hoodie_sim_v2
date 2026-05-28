from __future__ import annotations

import json
import unittest

from src.analysis.paper_faithful_state_action_space_batch import generate_paper_faithful_state_action_space_batch_artifacts
from src.analysis.paper_faithful_state_action_space_batch.config import (
    MIGRATION_READINESS_JSON,
    PAPER_ACTION_SPACE_CONTRACT_JSON,
    PAPER_LEGAL_MASK_CONTRACT_JSON,
    PAPER_LOAD_HISTORY_CONTRACT_JSON,
    PAPER_STATE_CONTRACT_JSON,
)


class PaperFaithfulStateActionSpaceBatchIntegrationTests(unittest.TestCase):
    def test_artifacts_are_written(self) -> None:
        report, json_path, md_path = generate_paper_faithful_state_action_space_batch_artifacts()
        self.assertTrue(json_path.exists())
        self.assertTrue(md_path.exists())
        for path in [PAPER_STATE_CONTRACT_JSON, PAPER_ACTION_SPACE_CONTRACT_JSON, PAPER_LEGAL_MASK_CONTRACT_JSON, PAPER_LOAD_HISTORY_CONTRACT_JSON, MIGRATION_READINESS_JSON]:
            self.assertTrue(path.exists())
        self.assertEqual(json.loads(json_path.read_text(encoding="utf-8")), report.to_dict())


if __name__ == "__main__":
    unittest.main()
