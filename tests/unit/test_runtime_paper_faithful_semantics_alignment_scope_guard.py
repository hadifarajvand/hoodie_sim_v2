from __future__ import annotations

import unittest

from src.analysis.runtime_paper_faithful_semantics_alignment.config import validate_scope


class RuntimePaperFaithfulSemanticsAlignmentScopeGuardTests(unittest.TestCase):
    def test_validate_scope_accepts_only_allowed_feature_paths(self) -> None:
        allowed = [
            "specs/071-runtime-paper-faithful-semantics-alignment/spec.md",
            "src/analysis/runtime_paper_faithful_semantics_alignment/report.py",
            "src/environment/paper_timeout.py",
            "tests/unit/test_topology_timeout_reward_fidelity_models.py",
            "tests/unit/test_runtime_paper_faithful_semantics_alignment_report.py",
        ]
        self.assertEqual(validate_scope(allowed), allowed)

    def test_validate_scope_rejects_forbidden_paths(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "outside approved Feature 071 scope"):
            validate_scope(
                [
                    "specs/071-runtime-paper-faithful-semantics-alignment/tasks.md",
                    "src/agents/rogue.py",
                    "artifacts/generated/output.json",
                    "poetry.lock",
                    "specs/072-runtime-golden-trace/spec.md",
                ]
            )


if __name__ == "__main__":
    unittest.main()
