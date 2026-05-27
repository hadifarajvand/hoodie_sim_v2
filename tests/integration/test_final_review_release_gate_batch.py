from __future__ import annotations

import json
import unittest

from src.analysis.final_review_release_gate_batch import generate_final_review_release_gate_batch_artifacts
from src.analysis.final_review_release_gate_batch.config import (
    ARTIFACT_COMPLETENESS_JSON,
    CLAIM_BOUNDARY_JSON,
    HANDOFF_MD,
    REPOSITORY_STATE_AUDIT_JSON,
    RELEASE_TAG_READINESS_MD,
)


class FinalReviewReleaseGateBatchIntegrationTests(unittest.TestCase):
    def test_artifacts_are_written(self) -> None:
        report, json_path, md_path = generate_final_review_release_gate_batch_artifacts()
        self.assertTrue(json_path.exists())
        self.assertTrue(md_path.exists())
        for path in [REPOSITORY_STATE_AUDIT_JSON, ARTIFACT_COMPLETENESS_JSON, CLAIM_BOUNDARY_JSON, RELEASE_TAG_READINESS_MD, HANDOFF_MD]:
            self.assertTrue(path.exists())
        self.assertEqual(json.loads(json_path.read_text(encoding="utf-8")), report.to_dict())


if __name__ == "__main__":
    unittest.main()
