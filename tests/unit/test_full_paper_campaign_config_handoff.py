"""Unit tests: full paper campaign user-execution handoff (never executes 5000)."""

from __future__ import annotations

import json
from pathlib import Path

from src.analysis.full_paper_campaign_config import guards as g
from src.analysis.full_paper_campaign_config import handoff


def test_handoff_ready_and_guard_correct():
    report = handoff.run(emit_json=False)
    assert report["executed_5000"] is False
    assert report["execution_path_wired"] is True
    assert report["execution_guard_validation"]["guard_correct"] is True
    assert report["verdict"] == "full_campaign_user_execution_handoff_ready"
    assert report["recommended_next_step"] == "user_runs_full_campaign_command"


def test_execution_requires_both_flag_and_env():
    assert g.execution_authorized(True, {}) is False
    assert g.execution_authorized(False, {g.EXECUTION_ENV_CONFIRMATION: "1"}) is False
    assert g.execution_authorized(True, {g.EXECUTION_ENV_CONFIRMATION: "1"}) is True


def test_handoff_artifacts_written():
    handoff.run(emit_json=False)
    root = Path("artifacts/production/full-paper-campaign-user-execution-handoff")
    for name in (
        "user-execution-command.md", "dry-run-validation.json", "execution-guard-validation.json",
        "full-campaign-command.txt", "post-run-instructions.md", "handoff-final-report.json",
        "handoff-final-report.md", "claim-safety.json",
    ):
        assert (root / name).exists(), name
    cmd = (root / "full-campaign-command.txt").read_text()
    assert "HOODIE_EXECUTE_FULL_CAMPAIGN=1" in cmd
    assert "--execute-full-campaign" in cmd


def test_claim_safety_all_false():
    cs = json.loads(Path(
        "artifacts/production/full-paper-campaign-user-execution-handoff/claim-safety.json"
    ).read_text()) if Path(
        "artifacts/production/full-paper-campaign-user-execution-handoff/claim-safety.json"
    ).exists() else g.claim_safety()
    assert cs["training_5000_run"] is False
    assert cs["paper_reproduction_claim_made"] is False
    assert cs["performance_superiority_claim_made"] is False
    assert cs["baseline_superiority_claim_made"] is False
