from __future__ import annotations

import unittest

from src.analysis.campaign_execution_engine.config import validate_scope


class CampaignExecutionEngineScopeGuardTests(unittest.TestCase):
    def test_allowed_package_path_passes(self) -> None:
        self.assertEqual(validate_scope(["src/analysis/campaign_execution_engine/model.py"]), ["src/analysis/campaign_execution_engine/model.py"])

    def test_allowed_test_path_passes(self) -> None:
        self.assertEqual(validate_scope(["tests/unit/test_campaign_execution_engine_model.py"]), ["tests/unit/test_campaign_execution_engine_model.py"])

    def test_forbidden_environment_path_fails(self) -> None:
        with self.assertRaises(ValueError):
            validate_scope(["src/environment/paper_timeout.py"])

    def test_forbidden_policies_path_fails(self) -> None:
        with self.assertRaises(ValueError):
            validate_scope(["src/policies/common.py"])

    def test_forbidden_dependency_file_fails(self) -> None:
        with self.assertRaises(ValueError):
            validate_scope(["pyproject.toml"])

    def test_forbidden_future_feature_path_fails(self) -> None:
        with self.assertRaises(ValueError):
            validate_scope(["src/analysis/campaign_summary/report.py"])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
