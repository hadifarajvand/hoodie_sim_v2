"""Unit tests: epsilon-greedy exploration schedule and trainer wiring."""

from __future__ import annotations

import pytest

from src.analysis.full_training_reproduction_campaign.trainer import EpsilonGreedyExploration


def test_epsilon_decays_linearly():
    sched = EpsilonGreedyExploration(epsilon_start=1.0, epsilon_final=0.1, epsilon_decay_steps=100, decay_type="linear")
    assert sched.epsilon_for_step(0) == pytest.approx(1.0)
    assert sched.epsilon_for_step(50) == pytest.approx(0.55)
    assert sched.epsilon_for_step(100) == pytest.approx(0.1)
    assert sched.epsilon_for_step(1000) == pytest.approx(0.1)  # clamped


def test_epsilon_exponential_decay_monotonic():
    sched = EpsilonGreedyExploration(epsilon_start=1.0, epsilon_final=0.05, epsilon_decay_steps=100, decay_type="exponential")
    vals = [sched.epsilon_for_step(s) for s in range(0, 120, 10)]
    assert all(vals[i] >= vals[i + 1] - 1e-9 for i in range(len(vals) - 1))


def test_select_respects_legal_mask_and_counts():
    sched = EpsilonGreedyExploration(epsilon_start=1.0, epsilon_final=1.0, epsilon_decay_steps=10, seed=1)
    # epsilon=1 => always random, but only among legal indices.
    for _ in range(50):
        idx, was_random, eps = sched.select_action_index(0, greedy_index=0, legal_mask=(False, True, False))
        assert idx == 1 and was_random is True and eps == 1.0
    assert sched.random_action_count == 50
    assert sched.greedy_action_count == 0


def test_select_greedy_when_epsilon_zero():
    sched = EpsilonGreedyExploration(epsilon_start=0.0, epsilon_final=0.0, epsilon_decay_steps=10)
    idx, was_random, eps = sched.select_action_index(0, greedy_index=2, legal_mask=(True, True, True))
    assert idx == 2 and was_random is False and eps == 0.0
    assert sched.greedy_action_count == 1


def test_invalid_schedule_rejected():
    with pytest.raises(ValueError):
        EpsilonGreedyExploration(epsilon_start=0.1, epsilon_final=0.5)  # final > start
    with pytest.raises(ValueError):
        EpsilonGreedyExploration(decay_type="cosine")
    with pytest.raises(ValueError):
        EpsilonGreedyExploration(epsilon_decay_steps=0)


def test_default_trainer_has_no_exploration():
    # Default behavior must be preserved (None) so existing campaign features are unaffected.
    from src.analysis.full_training_reproduction_campaign.config import CampaignConfig
    from src.analysis.full_training_reproduction_campaign.trainer import DDQNTrainer

    trainer = DDQNTrainer(CampaignConfig(evaluation_episode_length=110, full_campaign_episode_length=110))
    assert trainer.exploration is None
