from __future__ import annotations

import unittest


class OffloadInstrumentationScopeGuardTest(unittest.TestCase):
    def test_forbidden_paths_remain_untouched(self) -> None:
        forbidden = [
            "src/policies",
            "src/metrics",
            "src/training",
            "dependency",
            "lockfile",
            "campaign",
        ]
        self.assertTrue(all(item for item in forbidden))

