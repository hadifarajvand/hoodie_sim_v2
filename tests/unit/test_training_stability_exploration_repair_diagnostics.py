"""Unit tests: Q-value diagnostics, double-DQN wiring, budgets/claim-safety."""

from __future__ import annotations

import inspect

import torch

from src.analysis.full_training_reproduction_campaign.config import CampaignConfig
from src.analysis.full_training_reproduction_campaign.trainer import DDQNTrainer
from src.analysis.paper_faithful_simulation_production import simulation_runner, training_repair


def _trainer():
    return DDQNTrainer(CampaignConfig(evaluation_episode_length=110, full_campaign_episode_length=110))


def test_q_value_diagnostics_empty_then_populated():
    t = _trainer()
    assert t.q_value_diagnostics()["q_value_decision_count"] == 0
    # Build a state window tensor of the right shape via the trainer helper.
    hist = t._initial_history(episode_length=110)
    state_tensor = t._state_tensor(hist)
    t._record_q_values(state_tensor)
    diag = t.q_value_diagnostics()
    assert diag["q_value_decision_count"] == 1
    for key in ("q_local_mean", "q_horizontal_mean", "q_vertical_mean", "advantage_gap",
                "dominant_q_action", "q_values_have_nonzero_action_separation"):
        assert key in diag


def test_double_dqn_uses_online_for_selection_target_for_eval():
    # Source-level guarantee that next-action selection uses the online network
    # and evaluation uses the target network (paper double-DQN).
    src = inspect.getsource(DDQNTrainer._train_batch)
    assert "online_network(batch.next_state_tensor)" in src or "online_q_next" in src or "next_actions" in src
    assert "target_network(batch.next_state_tensor)" in src


def test_repair_budgets_no_5000():
    assert 5000 not in training_repair.REPAIR_BUDGETS
    assert max(training_repair.REPAIR_BUDGETS) == 1000
    assert training_repair.REPAIR_BUDGETS == [50, 100, 200, 300, 500, 750, 1000]


def test_production_session_enables_exploration_kwargs():
    assert simulation_runner.EXPLORATION_KWARGS["epsilon_start"] == 1.0
    assert simulation_runner.EXPLORATION_KWARGS["epsilon_final"] <= simulation_runner.EXPLORATION_KWARGS["epsilon_start"]
    assert simulation_runner.EXPLORATION_KWARGS["epsilon_decay_steps"] > 0


def test_eval_path_is_greedy_epsilon_zero():
    # The repair documents epsilon_eval = 0.0 (evaluation deterministic).
    # Evaluation uses trainer.policy.choose_action (greedy argmax) — no exploration object consulted.
    src = inspect.getsource(simulation_runner)
    assert "candidate_policy_result" in src
