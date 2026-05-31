from __future__ import annotations

import unittest

from src.analysis.end_to_end_hoodie_golden_trace_validation.config import validate_scope


class EndToEndHoodieGoldenTraceValidationScopeGuardTests(unittest.TestCase):
    def test_validate_scope_accepts_only_allowed_feature_paths(self) -> None:
        allowed = [
            "specs/072-end-to-end-hoodie-golden-trace-validation/spec.md",
            "src/analysis/end_to_end_hoodie_golden_trace_validation/report.py",
            "tests/unit/test_end_to_end_hoodie_golden_trace_validation_model.py",
            "tests/integration/test_end_to_end_hoodie_golden_trace_validation_report.py",
        ]
        self.assertEqual(validate_scope(allowed), allowed)

    def test_validate_scope_rejects_forbidden_paths(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "outside approved Feature 072 scope"):
            validate_scope(
                [
                    "specs/072-end-to-end-hoodie-golden-trace-validation/tasks.md",
                    "src/agents/rogue.py",
                    "artifacts/generated/output.json",
                    "poetry.lock",
                    "specs/073-next-step/spec.md",
                    "src/analysis/feature073/rogue.py",
                ]
            )


if __name__ == "__main__":
    unittest.main()
