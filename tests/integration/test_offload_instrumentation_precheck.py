from __future__ import annotations

import json
from pathlib import Path
import unittest


class OffloadInstrumentationPrecheckTest(unittest.TestCase):
    def test_current_audit_still_shows_selected_action_only_failure_before_generation(self) -> None:
        payload = json.loads(Path("artifacts/analysis/differential-environment-audit/differential-audit.json").read_text())
        horizontal = next(item for item in payload["comparison_results"] if item["case_id"] == "case-horizontal-offload")
        vertical = next(item for item in payload["comparison_results"] if item["case_id"] == "case-vertical-offload")
        self.assertTrue(horizontal["environment_summary"]["event_sequence"][0].startswith("selected_action"))
        self.assertTrue(vertical["environment_summary"]["event_sequence"][0].startswith("selected_action"))
