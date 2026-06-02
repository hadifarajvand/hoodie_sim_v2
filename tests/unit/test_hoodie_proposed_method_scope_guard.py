from __future__ import annotations

import unittest

from src.analysis.hoodie_proposed_method.config import validate_scope


class HoodieProposedMethodScopeGuardTests(unittest.TestCase):
    def test_scope_guard_rejects_ranking_and_baseline_paths(self) -> None:
        with self.assertRaises(ValueError):
            validate_scope(
                [
                    "src/analysis/evaluation_ranking/report.py",
                    "tests/unit/test_hoodie_proposed_method_scope_guard.py",
                ]
            )

        with self.assertRaises(ValueError):
            validate_scope(
                [
                    "src/analysis/hoodie_proposed_fidelity/report.py",
                    "tests/unit/test_hoodie_proposed_method_scope_guard.py",
                ]
            )

    def test_scope_guard_accepts_only_feature_080_paths(self) -> None:
        checked = validate_scope(
            [
                "specs/080-evaluation-ranking/plan.md",
                "src/analysis/hoodie_proposed_method/report.py",
                "tests/unit/test_hoodie_proposed_method_scope_guard.py",
            ]
        )
        self.assertEqual(len(checked), 3)
        self.assertTrue(all(path.startswith(("specs/080-evaluation-ranking/", "src/analysis/hoodie_proposed_method/", "tests/unit/test_hoodie_proposed_method_")) for path in checked))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
