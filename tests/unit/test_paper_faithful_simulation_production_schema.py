"""Unit tests: production metric schema, profiles, paper source audit, mechanism map."""

from __future__ import annotations

import pytest

from src.analysis.paper_faithful_simulation_production.mechanism_map import build_mechanism_map
from src.analysis.paper_faithful_simulation_production.metric_schema import (
    PAPER_COMPATIBLE_METRIC_FIELDS,
    build_metric,
    validate_metric_schema,
)
from src.analysis.paper_faithful_simulation_production.paper_source_audit import build_paper_source_audit
from src.analysis.paper_faithful_simulation_production.profiles import (
    FORBIDDEN_BUDGETS,
    ProductionProfile,
)


def test_schema_has_production_fields():
    for f in (
        "simulation_profile", "calibration_profile", "state_representation_profile",
        "reconciliation_profile", "recovered_horizon_reward_event_count",
        "horizon_finalized_terminal_count", "energy_total", "cost_total",
        "deadline_violation_ratio", "reward_reconciled", "terminal_reconciled",
    ):
        assert f in PAPER_COMPATIBLE_METRIC_FIELDS


def test_build_and_validate_metric_row():
    row = build_metric(run_id="x", policy_name="fixed_local_policy")
    assert validate_metric_schema(row)


def test_unknown_field_rejected():
    with pytest.raises(KeyError):
        build_metric(bogus=1)


def test_profile_rejects_forbidden_budget():
    assert 5000 in FORBIDDEN_BUDGETS
    with pytest.raises(ValueError):
        ProductionProfile(training_budgets=[50, 5000])


def test_profile_defaults_bounded():
    p = ProductionProfile()
    assert p.training_budgets == [50, 100, 200, 300]
    assert p.max_training_budget == 300
    assert p.episode_length == 110
    assert 5000 not in p.training_budgets


def test_paper_source_audit_finds_pdf_and_params():
    audit = build_paper_source_audit()
    assert audit["paper_pdf_present"] is True
    assert audit["paper_text_extracted"] is True
    # Key Table 4 params must be extracted.
    assert "number_of_agents_N_EA" in audit["parameters_extracted"]
    assert "drop_penalty_C" in audit["parameters_extracted"]


def test_mechanism_map_complete_schema():
    mech = build_mechanism_map()
    assert mech["paper_mechanism_map_completed"] is True
    assert mech["mechanism_count"] >= 20
    for row in mech["rows"]:
        for field in ("mechanism", "paper_expected", "repo_current", "implementation_status",
                      "gap", "source", "confidence", "required_action"):
            assert field in row
        assert row["implementation_status"] in {
            "matched", "matched_with_documented_approximation", "implemented_but_unverified",
            "missing", "broken", "not_applicable",
        }
