from __future__ import annotations

import ast
from pathlib import Path
import tempfile
import unittest

from src.audits.differential_environment import DifferentialEnvironmentAudit, build_default_toy_cases


FORBIDDEN_NAMES = (
    "src/environment",
    "src.policies",
    "src/training",
    "src.metrics",
    "artifacts/campaigns",
    "campaign runner",
)

FORBIDDEN_IMPORT_PREFIXES = (
    "environment",
    "src.environment",
    "policies",
    "src.policies",
    "training",
    "src.training",
    "metrics",
    "src.metrics",
    "campaign",
)


def _is_forbidden_module(module_name: str) -> bool:
    if module_name == "src.environment.gym_adapter":
        return False
    return any(
        module_name == forbidden or module_name.startswith(f"{forbidden}.")
        for forbidden in FORBIDDEN_IMPORT_PREFIXES
    )


class DifferentialEnvironmentAuditFlowTest(unittest.TestCase):
    def test_public_interface_only_import_guard(self) -> None:
        source_dir = Path("src/audits/differential_environment")
        source_files = sorted(source_dir.glob("*.py"))
        self.assertTrue(source_files, "audit source files must exist")
        for path in source_files:
            text = path.read_text(encoding="utf-8")
            sanitized_text = text.replace("from src.environment.gym_adapter import HoodieGymEnvironment\n", "")
            sanitized_text = sanitized_text.replace("src/environment/gym_adapter.py", "")
            for forbidden in FORBIDDEN_NAMES:
                self.assertNotIn(forbidden, sanitized_text, f"forbidden reference found in {path}: {forbidden}")
            tree = ast.parse(text, filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.assertFalse(_is_forbidden_module(alias.name), f"forbidden import in {path}: {alias.name}")
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    self.assertFalse(_is_forbidden_module(module), f"forbidden from-import in {path}: {module}")

    def test_end_to_end_audit_runs_and_writes_deterministic_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            audit = DifferentialEnvironmentAudit(output_dir=Path(tmpdir) / "artifacts")
            report_one = audit.run(build_default_toy_cases())
            report_two = audit.run(build_default_toy_cases())
            self.assertEqual(report_one.to_dict(), report_two.to_dict())
            json_path = Path(tmpdir) / "artifacts" / "differential-audit.json"
            md_path = Path(tmpdir) / "artifacts" / "differential-audit.md"
            self.assertTrue(json_path.exists())
            self.assertTrue(md_path.exists())
            payload = report_one.to_dict()
            self.assertEqual(payload["metadata"]["feature_id"], "018")
            self.assertTrue(payload["metadata"]["deterministic"])
            self.assertIn("no fixes were applied", payload["no_fix_disclaimer"].lower())
            self.assertEqual(
                [case["case_id"] for case in payload["toy_cases"]],
                [case.case_id for case in build_default_toy_cases()],
            )
            self.assertEqual(len(payload["comparison_results"]), 6)
            timeout_case = next(result for result in payload["comparison_results"] if result["case_id"] == "case-timeout-drop")
            self.assertEqual(timeout_case["classification"], "divergence")
            self.assertEqual(timeout_case["finding_cause"], "likely_environment_bug")

    def test_artifact_output_is_feature_namespaced(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            audit = DifferentialEnvironmentAudit(output_dir=Path(tmpdir) / "artifacts")
            report = audit.run(build_default_toy_cases())
            json_path = Path(tmpdir) / "artifacts" / "differential-audit.json"
            md_path = Path(tmpdir) / "artifacts" / "differential-audit.md"
            self.assertEqual(json_path.name, "differential-audit.json")
            self.assertEqual(md_path.name, "differential-audit.md")
            self.assertIn("artifact", report.reproducibility["output_root"])


if __name__ == "__main__":
    unittest.main()
