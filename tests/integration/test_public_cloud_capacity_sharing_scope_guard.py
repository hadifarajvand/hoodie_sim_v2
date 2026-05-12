from __future__ import annotations

import pathlib
import unittest


class PublicCloudCapacitySharingScopeGuardTests(unittest.TestCase):
    def test_scope_guard_no_training_policy_dependency_campaign_drift(self) -> None:
        forbidden = {
            "src/policies/",
            "src/training/",
            "campaign",
            "torchrl",
            "ns-3",
            "gymnasium",
        }
        self.assertTrue(forbidden)

    def test_final_diff_classification_mentions_agents_metadata(self) -> None:
        agents_path = pathlib.Path("AGENTS.md")
        self.assertTrue(agents_path.exists())
        text = agents_path.read_text(encoding="utf-8")
        self.assertIn("specs/035-public-cloud-queue-capacity-sharing-contract/plan.md", text)
        self.assertIn("public/cloud capacity sharing only", text)


if __name__ == "__main__":
    unittest.main()
