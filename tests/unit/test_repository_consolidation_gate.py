from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


MODULE_PATH = Path(__file__).parents[2] / "scripts" / "audit" / "repository_consolidation_gate.py"
SPEC = importlib.util.spec_from_file_location("repository_consolidation_gate", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
GATE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = GATE
SPEC.loader.exec_module(GATE)


def test_generated_artifacts_are_blocked_except_approved() -> None:
    paths = (
        "artifacts/approved/source-contract.json",
        "artifacts/analysis/old-report.json",
        "artifacts/hoodie/campaigns/run/status.json",
    )
    assert GATE._artifact_issues(paths) == (
        "artifacts/analysis/old-report.json",
        "artifacts/hoodie/campaigns/run/status.json",
    )


def test_patch_and_v2_modules_are_transitional() -> None:
    paths = (
        "src/hoodie/experiments/campaign.py",
        "src/hoodie/experiments/runtime_path_patch.py",
        "src/hoodie/experiments/distributed_v2.py",
    )
    assert GATE._transitional_issues(paths) == (
        "src/hoodie/experiments/distributed_v2.py",
        "src/hoodie/experiments/runtime_path_patch.py",
    )


def test_canonical_pyproject_passes(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        """
[project]
name = "hoodie"
[project.scripts]
hoodie-experiments = "hoodie.experiments.cli:main"
[tool.setuptools]
package-dir = {"" = "src"}
[tool.setuptools.packages.find]
where = ["src"]
include = ["hoodie*"]
[tool.pytest.ini_options]
testpaths = ["tests/unit", "tests/integration", "tests/acceptance"]
""".strip()
        + "\n",
        encoding="utf-8",
    )
    assert GATE._packaging_issues(tmp_path) == ()


def test_legacy_pyproject_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        """
[project]
name = "hoodie"
[project.scripts]
hoodie-experiments = "src.hoodie.experiments.cli:main"
[tool.setuptools]
package-dir = {"" = "."}
[tool.setuptools.packages.find]
where = ["."]
include = ["src*", "hoodie*"]
[tool.pytest.ini_options]
testpaths = ["tests_supported/hoodie", "tests/unit"]
""".strip()
        + "\n",
        encoding="utf-8",
    )
    issues = GATE._packaging_issues(tmp_path)
    assert len(issues) == 5
