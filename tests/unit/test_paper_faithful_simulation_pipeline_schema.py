"""Unit tests for Feature 080 paper-compatible metric schema and claim safety."""

from __future__ import annotations

import pytest

from src.analysis.paper_faithful_simulation_production_pipeline.schema import (
    PAPER_COMPATIBLE_METRIC_FIELDS,
    build_paper_compatible_metric,
    validate_metric_schema,
)


def test_schema_has_required_core_fields():
    for required in (
        "run_id", "policy_name", "completion_ratio", "drop_ratio",
        "deadline_violation_ratio", "reward_reconciled", "terminal_reconciled",
        "raw_vs_canonical_reward_delta", "action_local_count",
    ):
        assert required in PAPER_COMPATIBLE_METRIC_FIELDS


def test_build_fills_missing_with_none_and_keeps_all_fields():
    row = build_paper_compatible_metric(run_id="x", policy_name="fixed_local_policy")
    assert validate_metric_schema(row)
    assert row["run_id"] == "x"
    assert row["completion_ratio"] is None


def test_build_rejects_unknown_fields():
    with pytest.raises(KeyError):
        build_paper_compatible_metric(nonexistent_field=1)


def test_no_5000_training_budget_in_policy():
    from src.analysis.paper_faithful_simulation_production_pipeline.runner import build_implementation_plan

    plan = build_implementation_plan()
    forbidden = plan["budget_policy"]["forbidden"]
    assert 5000 in forbidden
    assert plan["budget_policy"]["max_training_budget"] == 100
