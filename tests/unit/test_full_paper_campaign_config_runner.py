"""Unit tests: full paper campaign runner + guards (must never execute 5000)."""

from __future__ import annotations

import json
from pathlib import Path

from src.analysis.full_paper_campaign_config import build_full_campaign_config
from src.analysis.full_paper_campaign_config import guards as g
from src.analysis.full_paper_campaign_config import runner as r


def test_no_flag_refuses_and_prints_message(capsys):
    rc = r.run(dry_run=False, execute_full_campaign=False, emit_json=False)
    assert rc == 0
    out = capsys.readouterr().out
    assert out.strip() == g.EXECUTION_DISABLED_MESSAGE


def test_execute_flag_does_not_run_5000(capsys):
    # Flag acknowledged but env confirmation absent -> pre-flight only, nothing runs.
    rc = r.run(dry_run=False, execute_full_campaign=True, emit_json=False)
    assert rc == 0
    out = capsys.readouterr().out
    assert "NOT authorized" in out
    assert "nothing was run" in out


def test_execution_authorized_requires_flag_and_env():
    assert g.execution_authorized(False, {}) is False
    assert g.execution_authorized(True, {}) is False
    assert g.execution_authorized(True, {g.EXECUTION_ENV_CONFIRMATION: "0"}) is False
    assert g.execution_authorized(True, {g.EXECUTION_ENV_CONFIRMATION: "1"}) is True


def test_all_guards_pass():
    cfg = build_full_campaign_config()
    checks = g.validate_config(cfg)
    assert all(checks.values()), checks
    assert checks["N_E_is_5000"]
    assert checks["epsilon_schedule_paper_aligned"]
    assert checks["target_sync_2000_episodes"]
    assert checks["per_task_delayed_reward_credit_enabled"]
    assert checks["horizon_aware_reconciliation_enabled"]


def test_claim_safety_fields_false():
    cs = g.claim_safety()
    assert cs["training_5000_run"] is False
    assert cs["paper_reproduction_claim_made"] is False
    assert cs["performance_superiority_claim_made"] is False
    assert cs["baseline_superiority_claim_made"] is False
    assert cs["reward_function_modified"] is False
    assert cs["environment_semantics_modified"] is False
    assert cs["claim_safety_passed"] is True


def test_dry_run_emits_all_spec_artifacts():
    rc = r.run(dry_run=True, execute_full_campaign=False, emit_json=False)
    assert rc == 0
    root = Path("artifacts/production/full-paper-campaign-config-only")
    for name in (
        "full-paper-campaign-config.json", "execution-runbook.md", "checkpoint-resume-plan.md",
        "monitoring-plan.md", "abort-conditions.md", "compute-time-storage-estimates.json",
        "paper-parameter-summary.json", "remaining-approximations.md", "expected-artifact-manifest.json",
        "claim-safety.json", "config-only-final-report.json", "config-only-final-report.md",
    ):
        assert (root / name).exists(), name
    assert (root / "figures" / "figure_01_full_campaign_epsilon_schedule.png").exists()
    report = json.loads((root / "config-only-final-report.json").read_text())
    assert report["executed_5000"] is False
    assert report["verdict"] == "full_paper_campaign_config_ready_for_user_approval"


def test_estimates_grounded_range():
    from src.analysis.full_paper_campaign_config.estimates import build_estimates

    est = build_estimates(build_full_campaign_config())
    tw = est["total_wall_hours"]
    assert tw["low"] <= tw["expected"] <= tw["high"]
    assert 2.0 <= tw["expected"] <= 6.0
    assert est["checkpoint_count"] == 20
