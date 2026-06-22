"""Unit tests: full paper campaign config-only (must never execute 5000)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.analysis.full_paper_campaign_config import build_full_campaign_config
from src.analysis.full_paper_campaign_config import config as cfgmod
from src.analysis.full_paper_campaign_config.runbook import build_runbook, write_campaign_config_artifacts


def test_config_is_paper_faithful_and_config_only():
    c = build_full_campaign_config()
    assert c.number_of_training_episodes == 5000
    assert c.episode_length == 110
    assert c.epsilon_start == 1.0 and c.epsilon_final == 0.0
    assert c.epsilon_decay_episodes == 2500          # N_E/2
    assert c.epsilon_schedule_unit == "episode"
    assert c.target_update_frequency == 2000
    assert c.target_update_unit == "episode"
    assert c.learning_rate == 7e-7 and c.gamma == 0.99
    assert c.batch_size == 64 and c.replay_memory_capacity == 10_000
    assert c.credit_assignment == "per_task_delayed_reward"
    assert c.reconciliation_profile == "horizon_aware_recovered_reward_event"
    assert c.execute is False


def test_execute_flag_cannot_be_true():
    with pytest.raises(ValueError):
        cfgmod.FullPaperCampaignConfig(execute=True)


def test_epsilon_schedule_matches_paper():
    c = build_full_campaign_config()
    assert c.epsilon_at(0) == 1.0
    assert abs(c.epsilon_at(1250) - 0.5) < 1e-9      # halfway through decay
    assert c.epsilon_at(2500) == 0.0                  # fully decayed at N_E/2
    assert c.epsilon_at(5000) == 0.0                  # stays 0 in second half


def test_estimates_are_grounded_and_bounded():
    c = build_full_campaign_config()
    # measured ~1.73 s/episode -> training a few hours, not minutes, not days.
    assert 2.0 <= c.estimated_total_hours() <= 6.0


def test_runbook_has_all_required_sections():
    rb = build_runbook()
    for key in (
        "config", "compute_time_estimates", "checkpoint_resume_strategy",
        "monitoring", "abort_conditions", "expected_artifacts",
        "multi_agent_approximation", "claim_safety",
    ):
        assert key in rb, key
    assert rb["execute"] is False
    assert rb["claim_safety"]["training_5000_run"] is False
    ma = rb["multi_agent_approximation"]
    assert ma["status"] == "known_approximation_not_repaired"
    assert "per-EA" in ma["paper_design"] or "per_EA" in ma["paper_design"] or "each" in ma["paper_design"]


def test_no_execution_imports_in_modules():
    # The config-only package must not IMPORT the trainer/session/campaign runners
    # (doc prose may mention them, but there must be no executable wiring).
    import src.analysis.full_paper_campaign_config.runbook as rbmod

    for mod in (cfgmod, rbmod):
        names = set(vars(mod))
        assert "DDQNTrainer" not in names
        assert "StateRepresentationTrainingSession" not in names
        assert "run_medium_smoke" not in names


def test_artifacts_written(tmp_path, monkeypatch):
    rb = write_campaign_config_artifacts(emit_json=False)
    root = Path("artifacts/production/full-paper-campaign-config-only")
    for name in (
        "full-campaign-config.json", "compute-time-storage-estimates.json",
        "checkpoint-resume-strategy.json", "monitoring-and-abort.json",
        "expected-artifacts.json", "multi-agent-approximation.json",
        "claim-safety.json", "runbook.json", "runbook.md",
    ):
        assert (root / name).exists(), name
    assert (root / "figures" / "figure_01_paper_epsilon_schedule.png").exists()
    cfg = json.loads((root / "full-campaign-config.json").read_text())
    assert cfg["number_of_training_episodes_N_E"] == 5000
    assert cfg["execute"] is False
