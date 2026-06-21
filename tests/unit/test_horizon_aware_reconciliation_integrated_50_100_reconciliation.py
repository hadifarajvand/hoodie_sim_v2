"""Unit tests: recovered-strategy horizon-aware reconciliation (Feature 081)."""

from __future__ import annotations

from src.analysis.paper_faithful_simulation_production_pipeline.reconciliation import (
    horizon_aware_recovered_reconciliation,
)


def _task(outcome, canonical_reward, raw_count, raw_total, source="env_step_finalized_tasks"):
    return {
        "terminal_outcome": outcome,
        "canonical_reward": canonical_reward,
        "raw_reward_event_count": raw_count,
        "raw_reward_total": raw_total,
        "terminal_event_source": source,
    }


def test_recovered_total_equals_canonical_total():
    records = {
        "t:0:1": _task("completed", -5.0, 1, -5.0),
        "t:0:2": _task("dropped", -40.0, 1, -40.0),
        "t:0:3": _task("dropped", -40.0, 0, 0.0),  # horizon-only, no reward event
        "t:0:4": _task("completed", -3.0, 0, 0.0),  # horizon-only, no reward event
        "t:0:5": _task("pending_at_horizon", 0.0, 0, 0.0),
    }
    r = horizon_aware_recovered_reconciliation(records)
    assert r["recovery_strategy"] == "horizon_aware_recovered_reward_event"
    assert r["recovered_horizon_reward_event_count"] == 2
    assert r["raw_plus_recovered_reward_total"] == r["canonical_reward_total"]
    assert r["raw_vs_canonical_reward_delta"] == 0.0
    assert r["reward_reconciled"] is True


def test_terminal_coverage_is_one_after_recovery():
    records = {
        "t:0:1": _task("completed", -5.0, 1, -5.0),
        "t:0:3": _task("dropped", -40.0, 0, 0.0),
    }
    r = horizon_aware_recovered_reconciliation(records)
    assert r["raw_plus_horizon_terminal_count"] == r["canonical_terminal_task_count"]
    assert r["terminal_event_coverage_ratio"] == 1.0
    assert r["terminal_reconciled"] is True


def test_pending_tasks_excluded_from_reward_universe():
    records = {"t:0:5": _task("pending_at_horizon", 0.0, 0, 0.0)}
    r = horizon_aware_recovered_reconciliation(records)
    assert r["canonical_reward_task_count"] == 0
    assert r["pending_at_horizon_count"] == 1
    assert r["reward_reconciled"] is True


def test_required_reconciliation_fields_present():
    r = horizon_aware_recovered_reconciliation({"t:0:1": _task("completed", -5.0, 1, -5.0)})
    for field in (
        "raw_reward_event_count", "recovered_horizon_reward_event_count",
        "raw_plus_recovered_reward_event_count", "canonical_reward_task_count",
        "raw_reward_total", "recovered_horizon_reward_total", "raw_plus_recovered_reward_total",
        "canonical_reward_total", "raw_vs_canonical_reward_delta", "reward_reconciled",
        "raw_terminal_event_count", "horizon_finalized_terminal_count",
        "raw_plus_horizon_terminal_count", "canonical_terminal_task_count",
        "terminal_event_coverage_ratio", "terminal_reconciled",
    ):
        assert field in r, field
