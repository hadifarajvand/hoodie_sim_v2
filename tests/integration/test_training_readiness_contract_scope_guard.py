from __future__ import annotations

import unittest
from unittest import mock

from src.analysis.training_readiness_contract import build_training_readiness_contract_report


class TrainingReadinessContractScopeGuardTests(unittest.TestCase):
    def test_no_training_optimizer_replay_target_checkpoint_or_campaign(self) -> None:
        payload = build_training_readiness_contract_report().to_dict()
        for key in [
            "no_training_started",
            "no_optimizer_step",
            "no_replay_training",
            "no_target_update_execution",
            "no_checkpoint_written",
            "no_campaign_run",
            "no_policy_drift",
            "no_runtime_semantic_changes",
            "no_dependency_drift",
            "no_prior_artifact_rewrite",
            "no_paper_reproduction_claim",
        ]:
            self.assertTrue(payload[key])

    def test_report_generation_does_not_use_git_status_for_prior_feature_validation(self) -> None:
        import src.analysis.training_readiness_contract.runner as runner

        real_run = runner.subprocess.run

        def guarded_run(args, *pargs, **kwargs):
            if isinstance(args, (list, tuple)) and len(args) >= 2 and args[0] == "git" and args[1] == "status":
                raise AssertionError("git status must not be used for prior-feature validation")
            return real_run(args, *pargs, **kwargs)

        with mock.patch.object(runner.subprocess, "run", side_effect=guarded_run):
            payload = build_training_readiness_contract_report().to_dict()
        self.assertTrue(payload["feature_053_readiness_verified"])
        self.assertTrue(payload["evidence_chain_ready_for_training_contract"])


if __name__ == "__main__":
    unittest.main()
