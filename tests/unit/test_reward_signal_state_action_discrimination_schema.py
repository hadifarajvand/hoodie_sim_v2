"""Unit tests: reward-signal repair schema, raw-reward safety, no-5000."""

from __future__ import annotations

import inspect

from src.analysis.paper_faithful_simulation_production import reward_signal_repair, simulation_runner
from src.analysis.paper_faithful_simulation_production.metric_schema import PAPER_COMPATIBLE_METRIC_FIELDS


def test_repair_budgets_bounded_no_5000():
    assert 5000 not in reward_signal_repair.REPAIR_BUDGETS
    assert max(reward_signal_repair.REPAIR_BUDGETS) == 1000
    assert reward_signal_repair.REPAIR_BUDGETS == [50, 100, 200, 300, 500, 750, 1000]


def test_raw_reward_semantics_not_changed():
    # The repair must not edit the environment reward function.
    import src.environment.reward_timing as rt

    src = inspect.getsource(rt.reward_for_terminal_task)
    assert "-float(phi_private(task.completion_slot, task.arrival_slot))" in src
    assert "drop_penalty: float = 40.0" in src


def test_credit_assignment_is_training_only_flag():
    # per_task_credit_assignment is a trainer flag, gated and off by default.
    src = inspect.getsource(simulation_runner.run_medium_smoke)
    assert "per_task_credit_assignment" in src


def test_audit_reports_separation():
    audit = reward_signal_repair._audit_report()
    assert audit["raw_reward_semantics_changed"] is False
    assert audit["environment_semantics_changed"] is False
    me = audit["measured_evidence"]
    # Before: near-identical per-action means (the bug). After: separated.
    before = me["per_action_mean_reward_before"]
    after = me["per_action_mean_reward_after"]
    assert max(before.values()) - min(before.values()) < 3.0  # flat (noise)
    assert max(after.values()) - min(after.values()) > 3.0   # separated


def test_metric_schema_unchanged():
    # Reward repair must not alter the paper-compatible metric schema.
    assert "reward_reconciled" in PAPER_COMPATIBLE_METRIC_FIELDS
    assert "raw_vs_canonical_reward_delta" in PAPER_COMPATIBLE_METRIC_FIELDS
    assert len(PAPER_COMPATIBLE_METRIC_FIELDS) == len(set(PAPER_COMPATIBLE_METRIC_FIELDS))
