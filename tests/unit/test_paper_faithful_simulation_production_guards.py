"""Unit tests: budget guards and claim-safety for the production pipeline."""

from __future__ import annotations

from src.analysis.paper_faithful_simulation_production import profiles
from src.analysis.paper_faithful_simulation_production.runner import _full_campaign_config_only


def test_no_5000_in_executed_budgets():
    p = profiles.ProductionProfile()
    assert 5000 not in p.training_budgets
    assert p.max_training_budget <= 300


def test_full_campaign_config_only_not_executed():
    cfg = _full_campaign_config_only(profiles.ProductionProfile())
    assert cfg["executed"] is False
    assert cfg["number_of_training_episodes_N_E"] == 5000
    assert cfg["requires_explicit_user_approval"] is True


def test_paper_exact_parameters_recorded():
    pe = profiles.PAPER_EXACT
    assert pe["number_of_agents_N_EA"] == 20
    assert pe["task_timeout_slots"] == 20
    assert pe["drop_penalty_C"] == 40
    assert pe["number_of_time_slots_T"] == 110
