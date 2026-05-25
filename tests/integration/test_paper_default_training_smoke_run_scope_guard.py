from __future__ import annotations

import unittest
from unittest import mock

from src.analysis.paper_default_training_smoke_run import build_paper_default_training_smoke_report


class PaperDefaultTrainingSmokeRunScopeGuardTests(unittest.TestCase):
    def test_no_full_campaign_baseline_or_reproduction_claims(self) -> None:
        payload = build_paper_default_training_smoke_report().to_dict()
        for key in (
            "no_full_campaign",
            "no_baseline_comparison",
            "no_paper_reproduction_claim",
            "no_policy_drift",
            "no_dependency_drift",
            "no_environment_contract_drift",
        ):
            self.assertTrue(payload["behavior_safety_summary"][key])

    def test_report_generation_does_not_use_git_status_for_prerequisite_validation(self) -> None:
        import src.analysis.paper_default_training_smoke_run.runner as runner

        real_run = runner.subprocess.run

        def guarded_run(args, *pargs, **kwargs):
            if isinstance(args, (list, tuple)) and len(args) >= 2 and args[0] == "git" and args[1] == "status":
                raise AssertionError("git status must not be used for prerequisite validation")
            return real_run(args, *pargs, **kwargs)

        with mock.patch.object(runner.subprocess, "run", side_effect=guarded_run):
            payload = build_paper_default_training_smoke_report().to_dict()
        self.assertTrue(payload["feature_054_readiness_verified"])
        self.assertEqual(payload["final_verdict"], "paper_default_training_smoke_passed")


if __name__ == "__main__":
    unittest.main()
