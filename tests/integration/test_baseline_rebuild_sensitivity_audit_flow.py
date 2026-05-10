from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.analysis.baseline_rebuild_sensitivity_audit.runner import BaselineRebuildSensitivityAuditRunner
from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.runtime_model import SharedRuntimeParameters
from src.evaluation.matrix_config import EvaluationMatrixConfig
from src.evaluation.matrix_runner import EvaluationMatrixRunner
from src.evaluation.trace_protocol import EvaluationTrace, TraceTaskBlueprint
from src.policies.policy_interface import PolicyContext


class LearnedPolicyPlaceholderStub:
    def choose_action(self, context: PolicyContext) -> str:
        self.seen_context = context
        return "local"


class BaselineRebuildSensitivityAuditFlowIntegrationTest(unittest.TestCase):
    def _stub_environment(self) -> HoodieGymEnvironment:
        return HoodieGymEnvironment(
            episode_length=4,
            runtime_parameters=SharedRuntimeParameters(runtime_variant="constant_service"),
            policy_name="LEARNED_STUB",
        )

    def test_tiny_audit_is_deterministic_and_writes_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "audit"
            runner = BaselineRebuildSensitivityAuditRunner(output_dir=output_dir)
            first = runner.run()
            first_snapshot = {path.name: path.read_text(encoding="utf-8") for path in sorted(output_dir.iterdir()) if path.is_file()}
            second = BaselineRebuildSensitivityAuditRunner(output_dir=output_dir).run()
            second_snapshot = {path.name: path.read_text(encoding="utf-8") for path in sorted(output_dir.iterdir()) if path.is_file()}

            self.assertEqual(first.to_dict(), second.to_dict())
            self.assertEqual(first_snapshot, second_snapshot)
            self.assertTrue((output_dir / "baseline-rebuild-sensitivity-audit.json").exists())
            self.assertTrue((output_dir / "baseline-rebuild-sensitivity-audit.md").exists())
            self.assertTrue((output_dir / "baseline-rebuild-sensitivity-audit.csv").exists())
            self.assertEqual(first.metadata["feature_id"], "022-baseline-rebuild-sensitivity-audit")
            self.assertEqual(first.source_gate_status["passed"], True)
            self.assertEqual(first.included_baselines, ["FLC", "VO", "HO", "RO", "BCO", "MLEO", "ADAPTIVE"])
            self.assertEqual(first.sensitivity_dimensions["seeds"], [7, 11, 13])
            self.assertEqual(first.sensitivity_dimensions["scenarios"], ["paper_default", "moderate", "heavy"])
            self.assertEqual(first.sensitivity_dimensions["episode_lengths"], [4, 6])
            self.assertIn(first.overall_status, {"robust_collapse_reduced", "fragile_collapse_reduced", "collapse_unchanged", "collapse_worsened", "inconclusive"})

    def test_learned_policy_placeholder_stub_runs_through_shared_environment_interface(self) -> None:
        env = self._stub_environment()
        policy = LearnedPolicyPlaceholderStub()
        observation, _info = env.reset(seed=7)
        env.trace = EvaluationTrace(
            trace_id="learned-stub",
            seed=7,
            tasks=(
                TraceTaskBlueprint(
                    task_id=1,
                    source_agent_id=1,
                    arrival_slot=0,
                    size=8.0,
                    processing_density=1.0,
                    timeout_length=5,
                    absolute_deadline_slot=5,
                ),
            ),
            metadata={"mode": "stub", "trace_id": "learned-stub", "seed": "7"},
        )
        self.assertIn("1", observation)
        final_info = {}
        while True:
            current_task = env.current_task
            if current_task is None:
                action = None
            else:
                action = policy.choose_action(
                    PolicyContext(
                        observation=env.observe_flat(current_task),
                        legal_action_mask=env.legal_action_mask(current_task),
                        trace_history=("learned-stub",),
                    )
                )
            _obs, _reward, terminated, truncated, info = env.step(action)
            final_info = info
            if terminated or truncated:
                break
        self.assertIn("finalized_tasks", final_info)
        self.assertIsNotNone(getattr(policy, "seen_context", None))

    def test_existing_baseline_policy_path_runs_through_shared_environment_interface(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            matrix_output = Path(tmpdir) / "matrix"
            config = EvaluationMatrixConfig(
                policy_names=("FLC",),
                scenario_names=("paper_default",),
                seeds=(7,),
                output_dir=matrix_output,
                episode_length=4,
            )
            result = EvaluationMatrixRunner(config).run()
            self.assertEqual(result["count"], 1)
            self.assertTrue((matrix_output / "matrix-summary.csv").exists())
            self.assertTrue(any(path.name.endswith(".json") for path in matrix_output.iterdir() if path.is_file()))


if __name__ == "__main__":
    unittest.main()
