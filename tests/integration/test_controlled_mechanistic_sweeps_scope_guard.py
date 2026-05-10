from __future__ import annotations

import ast
import unittest
from pathlib import Path


FORBIDDEN_IMPORT_PREFIXES = (
    "src.policies",
    "src.training",
    "src.metrics",
    "src.evaluation.campaign_runner",
    "src.analysis.plot_builder",
    "src.analysis.baseline_sensitivity",
)

FORBIDDEN_TEXT_SNIPPETS = (
    "campaign runner",
    "plot_builder",
    "plot outputs",
)


class ControlledMechanisticSweepsScopeGuardTests(unittest.TestCase):
    def test_analysis_package_does_not_import_forbidden_modules_or_text(self) -> None:
        package_dir = Path("src/analysis/controlled_mechanistic_sweeps")
        for path in sorted(package_dir.glob("*.py")):
            text = path.read_text(encoding="utf-8")
            tree = ast.parse(text, filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.assertFalse(
                            alias.name.startswith(FORBIDDEN_IMPORT_PREFIXES),
                            msg=f"{path} imports forbidden module {alias.name}",
                        )
                if isinstance(node, ast.ImportFrom) and node.module is not None:
                    self.assertFalse(
                        node.module.startswith(FORBIDDEN_IMPORT_PREFIXES),
                        msg=f"{path} imports forbidden module {node.module}",
                    )
            for snippet in FORBIDDEN_TEXT_SNIPPETS:
                self.assertNotIn(snippet, text)

    def test_git_diff_does_not_touch_forbidden_paths(self) -> None:
        import subprocess

        diff = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
        untracked = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()

        changed_paths = [Path(item) for item in diff + untracked]
        forbidden_prefixes = (
            Path("src/environment"),
            Path("src/policies"),
            Path("src/training"),
            Path("src/metrics"),
            Path("campaign"),
            Path("dependencies"),
            Path("lockfiles"),
        )
        for path in changed_paths:
            self.assertFalse(
                any(path.as_posix().startswith(prefix.as_posix()) for prefix in forbidden_prefixes),
                msg=f"Forbidden path touched: {path}",
            )


if __name__ == "__main__":
    unittest.main()
