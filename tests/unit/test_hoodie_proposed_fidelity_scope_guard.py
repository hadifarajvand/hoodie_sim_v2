from __future__ import annotations

import unittest

from src.analysis.hoodie_proposed_fidelity.config import validate_scope


class HoodieProposedFidelityScopeGuardTests(unittest.TestCase):
    def test_validate_scope_allows_only_feature_081_paths(self) -> None:
        allowed = validate_scope(
            [
                "src/analysis/hoodie_proposed_fidelity/report.py",
                "tests/unit/test_hoodie_proposed_fidelity_report.py",
                "tests/integration/test_hoodie_proposed_fidelity_report.py",
            ]
        )
        self.assertEqual(
            allowed,
            [
                "src/analysis/hoodie_proposed_fidelity/report.py",
                "tests/unit/test_hoodie_proposed_fidelity_report.py",
                "tests/integration/test_hoodie_proposed_fidelity_report.py",
            ],
        )

    def test_validate_scope_rejects_forbidden_paths(self) -> None:
        with self.assertRaises(ValueError):
            validate_scope(
                [
                    "src/environment/paper_timeout.py",
                    "src/training/runner.py",
                    "src/analysis/campaign_execution_engine/report.py",
                    "resources/papers/hoodie/original/HOODIE_paper.pdf",
                ]
            )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
