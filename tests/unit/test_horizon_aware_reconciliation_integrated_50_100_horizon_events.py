"""Unit tests: explicit horizon-finalized task accounting (Feature 081)."""

from __future__ import annotations

from src.analysis.paper_faithful_simulation_production_pipeline.reconciliation import (
    horizon_aware_recovered_reconciliation,
)


def _task(outcome, canonical_reward, raw_count):
    return {
        "terminal_outcome": outcome,
        "canonical_reward": canonical_reward,
        "raw_reward_event_count": raw_count,
        "raw_reward_total": (canonical_reward if raw_count else 0.0),
        "terminal_event_source": "env_step_finalized_tasks",
    }


def test_horizon_finalized_tasks_counted_explicitly():
    records = {
        "a": _task("completed", -5.0, 1),
        "b": _task("dropped", -40.0, 0),   # horizon-only
        "c": _task("completed", -7.0, 0),  # horizon-only
    }
    r = horizon_aware_recovered_reconciliation(records)
    assert r["horizon_finalized_terminal_count"] == 2
    assert r["raw_terminal_event_count"] == 1
    assert r["raw_plus_horizon_terminal_count"] == 3
    assert r["canonical_terminal_task_count"] == 3
    assert len(r["recovered_reward_ledger"]) == 2


def test_recovered_event_marked_with_strategy():
    records = {"b": _task("dropped", -40.0, 0)}
    r = horizon_aware_recovered_reconciliation(records)
    entry = r["recovered_reward_ledger"][0]
    assert entry["recovery_strategy"] == "horizon_aware_recovered_reward_event"
    assert entry["recovered_reward"] == -40.0
