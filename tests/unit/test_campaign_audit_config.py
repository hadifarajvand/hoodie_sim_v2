from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.analysis.campaign_audit import CampaignAudit


class CampaignAuditConfigTests(unittest.TestCase):
    def test_missing_artifact_handling_and_deterministic_ordering(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            campaign_dir = Path(tmpdir) / "campaign"
            matrix_dir = campaign_dir / "matrix"
            bundle_dir = campaign_dir / "bundle"
            traces_dir = matrix_dir / "traces"
            traces_dir.mkdir(parents=True, exist_ok=True)
            (matrix_dir / "b.json").write_text("{}", encoding="utf-8")
            (matrix_dir / "a.json").write_text("{}", encoding="utf-8")
            audit = CampaignAudit(campaign_dir)

            inventory = audit._inventory()

            self.assertEqual(inventory.found_files, sorted(inventory.found_files))
            self.assertIn("matrix/a.json", inventory.found_files)
            self.assertIn("matrix/b.json", inventory.found_files)
            self.assertIn("matrix/matrix-summary.csv", inventory.missing_files)
            self.assertEqual(inventory.bundle_dir, bundle_dir.as_posix())

    def test_read_only_artifact_discovery_does_not_mutate_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            campaign_dir = Path(tmpdir) / "campaign"
            matrix_dir = campaign_dir / "matrix"
            matrix_dir.mkdir(parents=True, exist_ok=True)
            path = matrix_dir / "sample.json"
            path.write_text("{\"hello\": \"world\"}", encoding="utf-8")
            before = path.read_text(encoding="utf-8")

            audit = CampaignAudit(campaign_dir)
            _ = audit._found_files()
            after = path.read_text(encoding="utf-8")

            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()

