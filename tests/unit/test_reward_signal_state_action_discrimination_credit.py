"""Unit tests: per-task delayed-reward credit assignment in the trainer."""

from __future__ import annotations

from collections import defaultdict

from src.analysis.full_training_reproduction_campaign.config import CampaignConfig
from src.analysis.full_training_reproduction_campaign.replay import ACTION_INDEX_TO_SEMANTICS
from src.analysis.full_training_reproduction_campaign.trainer import DDQNTrainer, EpsilonGreedyExploration


def _trainer():
    return DDQNTrainer(CampaignConfig(evaluation_episode_length=110, full_campaign_episode_length=110))


def test_default_off_preserves_legacy():
    t = _trainer()
    assert t.per_task_credit_assignment is False


def test_per_task_credit_produces_clean_bounded_rewards():
    # With credit assignment, replay rewards must be in [-40, 0] (per-task), never
    # the multi-task step aggregates (e.g. -160) that broke learning.
    t = _trainer()
    t.exploration = EpsilonGreedyExploration(epsilon_start=1.0, epsilon_final=0.05, epsilon_decay_steps=20000)
    t.per_task_credit_assignment = True
    t._episode_rollout(episode_id=0, seed=t.config.seed_bundle.training_trace_generation_seed
                       if hasattr(t.config.seed_bundle, "training_trace_generation_seed") else 7,
                       episode_length=110, training=True)
    rewards = [tr.reward for tr in t.replay_buffer.as_list()]
    assert rewards, "expected transitions"
    assert min(rewards) >= -40.0 - 1e-9, f"reward below -40 indicates aggregate mis-attribution: {min(rewards)}"
    assert max(rewards) <= 0.0 + 1e-9
    assert t.per_task_credit_emitted > 0


def test_per_action_reward_separation_with_credit():
    # The whole point: action should correlate with reward (not flat noise).
    t = _trainer()
    t.exploration = EpsilonGreedyExploration(epsilon_start=1.0, epsilon_final=0.05, epsilon_decay_steps=20000)
    t.per_task_credit_assignment = True
    for ep in range(6):
        t._episode_rollout(episode_id=ep, seed=100 + ep, episode_length=110, training=True)
    by_action = defaultdict(list)
    for tr in t.replay_buffer.as_list():
        by_action[ACTION_INDEX_TO_SEMANTICS.get(tr.action, "?")].append(tr.reward)
    means = {a: sum(v) / len(v) for a, v in by_action.items() if v}
    # At least two actions present and their mean rewards differ (separation).
    assert len(means) >= 2
    assert max(means.values()) - min(means.values()) > 0.5, f"no per-action separation: {means}"
