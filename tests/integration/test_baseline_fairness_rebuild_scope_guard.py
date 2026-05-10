from __future__ import annotations

import unittest

from src.analysis.baseline_fairness_rebuild.runner import BaselineFairnessRebuildRunner


class BaselineFairnessRebuildScopeGuardIntegrationTest(unittest.TestCase):
    def test_runner_source_refs_are_limited_to_allowed_paths(self) -> None:
        report = BaselineFairnessRebuildRunner().run()
        source_refs = report.metadata["source_refs"]

        self.assertTrue(any(path.endswith("matrix_runner.py") for path in source_refs))
        self.assertFalse(any("src/policies/" in path for path in source_refs))
        self.assertFalse(any("src/training/" in path for path in source_refs))
        self.assertFalse(any("src/metrics/" in path for path in source_refs))
        self.assertFalse(any("campaign" in path for path in source_refs))


if __name__ == "__main__":
    unittest.main()
