"""Unit tests for Feature 080 horizon-aware reconciliation (Repair A)."""

from __future__ import annotations

from src.analysis.paper_faithful_simulation_production_pipeline.reconciliation import (
    horizon_aware_reconciliation,
    reward_bearing_task,
)


def _task(outcome, canonical_reward, raw_count, raw_total):
    return {
        "terminal_outcome": outcome,
        "canonical_reward": canonical_reward,
        "raw_reward_event_count": raw_count,
        "raw_reward_total": raw_total,
    }


def test_reward_bearing_requires_reward_event():
    assert reward_bearing_task(_task("completed", -5.0, 1, -5.0)) is True
    assert reward_bearing_task(_task("dropped", -40.0, 0, 0.0)) is False


def test_horizon_truncated_tasks_excluded_so_delta_zero():
    # Two reward-bearing tasks + one horizon-only dropped task (no reward event).
    records = {
        "t:0:1": _task("completed", -5.0, 1, -5.0),
        "t:0:2": _task("dropped", -40.0, 1, -40.0),
        "t:0:3": _task("dropped", -40.0, 0, 0.0),  # horizon-only, no reward event
    }
    result = horizon_aware_reconciliation(records)
    assert result["raw_event_reward_total"] == -45.0
    assert result["canonical_task_reward_total"] == -45.0
    assert result["raw_vs_canonical_reward_delta"] == 0.0
    assert result["reward_reconciled"] is True
    assert result["terminal_reconciled"] is True
    assert result["reward_pending_at_horizon_count"] == 1


def test_reproduces_legacy_positive_delta_without_fix():
    # Demonstrate the legacy failure mode: counting the horizon-only task's
    # canonical reward against a raw stream that never emitted it.
    records = {"t:0:3": _task("dropped", -40.0, 0, 0.0)}
    legacy_canonical = sum(r["canonical_reward"] for r in records.values())  # -40
    legacy_raw = sum(r["raw_reward_total"] for r in records.values())  # 0
    legacy_delta = legacy_raw - legacy_canonical
    assert legacy_delta == 40.0  # positive delta == the observed F072 failure sign
    fixed = horizon_aware_reconciliation(records)
    assert fixed["raw_vs_canonical_reward_delta"] == 0.0


def test_explicit_raw_totals_override():
    records = {"t:0:1": _task("completed", -3.0, 1, -3.0)}
    result = horizon_aware_reconciliation(records, raw_event_reward_total=-3.0, raw_reward_event_count=1)
    assert result["reward_reconciled"] is True
