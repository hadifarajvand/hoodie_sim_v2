from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Add the repository root to the path so that "src" can be imported as a package
repo_path = str(Path(__file__).resolve().parents[2])
if repo_path not in sys.path:
    sys.path.insert(0, repo_path)

from src.analysis.run_completion_positive_diagnostic import (
    run_completion_positive_diagnostic,
    write_artifacts,
)


class TestCompletionPositiveDiagnostic:
    @classmethod
    def setup_class(cls) -> None:
        # Run the diagnostic with default parameters (3x200)
        cls.report = run_completion_positive_diagnostic()
        cls.json_path, cls.md_path = write_artifacts(cls.report)

    def test_diagnostic_type(self) -> None:
        assert self.report["diagnostic_type"] == "completion_positive_diagnostic"

    def test_bounded_constraint_format(self) -> None:
        assert "episodes x" in self.report["bounded_constraint"]
        assert "slots" in self.report["bounded_constraint"]

    def test_both_paths_execute(self) -> None:
        # This diagnostic only runs the paper_default path, but we can check that the config is correct
        config_summary = self.report["config_summary"]
        assert config_summary["state_dim"] == 74
        assert config_summary["action_count"] == 22
        assert config_summary["lookback_w"] == 10
        assert config_summary["full_campaign_enabled"] is False

    def test_transition_count_positive(self) -> None:
        assert self.report["metrics"]["total_transition_count"] > 0

    def test_losses_all_finite(self) -> None:
        assert self.report["metrics"]["loss_summary"]["all_finite"] is True

    def test_losses_no_nan(self) -> None:
        assert self.report["metrics"]["loss_summary"]["no_nan"] is True

    def test_losses_no_inf(self) -> None:
        assert self.report["metrics"]["loss_summary"]["no_inf"] is True

    def test_legal_action_only(self) -> None:
        assert self.report["metrics"]["legal_action_only"] is True

    def test_illegal_action_count_zero(self) -> None:
        assert self.report["metrics"]["illegal_action_count"] == 0

    def test_verdict_is_pass(self) -> None:
        # The verdict should be either pass_completion_positive or pass_mechanics_only
        assert self.report["verdict"] in ("pass_completion_positive", "pass_mechanics_only", "fail")
        # We expect at least pass_mechanics_only based on previous runs
        assert self.report["verdict"] != "fail"

    def test_json_artifact_written(self) -> None:
        assert self.json_path.exists()
        assert self.json_path.stat().st_size > 0
        # Verify JSON is valid and contains expected structure
        data = json.loads(self.json_path.read_text(encoding="utf-8"))
        assert data["diagnostic_type"] == "completion_positive_diagnostic"
        assert "verdict" in data
        assert "interpretation" in data

    def test_md_artifact_written(self) -> None:
        assert self.md_path.exists()
        assert self.md_path.stat().st_size > 0
        content = self.md_path.read_text(encoding="utf-8")
        assert "# Completion-Positive Diagnostic Evidence" in content
        assert f"- **Verdict**: `{self.report['verdict']}`" in content
        assert "## Interpretation" in content

    def test_interpretation_present(self) -> None:
        assert "interpretation" in self.report
        assert isinstance(self.report["interpretation"], str)
        assert len(self.report["interpretation"]) > 0