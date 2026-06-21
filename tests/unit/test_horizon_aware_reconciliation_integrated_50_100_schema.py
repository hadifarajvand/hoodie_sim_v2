"""Unit tests: paper-compatible metric schema for Feature 081."""

from __future__ import annotations

import pytest

from src.analysis.paper_faithful_simulation_production_pipeline.schema import (
    PAPER_COMPATIBLE_METRIC_FIELDS,
    build_paper_compatible_metric,
    validate_metric_schema,
)


def test_schema_includes_horizon_recovery_fields():
    for required in (
        "recovered_horizon_reward_event_count",
        "raw_plus_recovered_reward_event_count",
        "horizon_finalized_terminal_count",
        "reward_reconciled",
        "terminal_reconciled",
        "raw_vs_canonical_reward_delta",
    ):
        assert required in PAPER_COMPATIBLE_METRIC_FIELDS


def test_build_row_validates():
    row = build_paper_compatible_metric(
        run_id="x", policy_name="fixed_local_policy",
        recovered_horizon_reward_event_count=3,
        horizon_finalized_terminal_count=3,
    )
    assert validate_metric_schema(row)
    assert row["recovered_horizon_reward_event_count"] == 3


def test_unknown_field_rejected():
    with pytest.raises(KeyError):
        build_paper_compatible_metric(bogus=1)
