from __future__ import annotations

from src.agents.ddqn import DoubleDQNAgent, ReplayTransition
from src.agents.hoodie_agent import HoodieAgent
from src.policies.policy_interface import PolicyContext


def test_masked_selection_uses_legal_actions():
    agent = DoubleDQNAgent()
    agent.online.advantage_biases = {"a": 1.0, "b": 2.0}
    assert agent.select((1.0, 2.0), ("a", "b")) == "b"


def test_replay_and_update_round_trip():
    agent = DoubleDQNAgent()
    agent.replay.add(ReplayTransition((1.0,), "a", 1.0, (2.0,), False))
    assert agent.update() == 1


def test_hoodie_agent_checkpoint_round_trip():
    hoodie = HoodieAgent()
    hoodie.causal_history.append({"task_size": 1.0})
    state = hoodie.export_state()
    restored = HoodieAgent.from_state(state)
    assert restored.export_state()["causal_history"] == [{"task_size": 1.0}]


def test_choose_action_respects_mask():
    hoodie = HoodieAgent()
    hoodie.learner.online.advantage_biases = {"local": 0.0, "remote": 2.0}
    ctx = PolicyContext(observation={"task_size": 1.0}, legal_action_mask={"local": True, "remote": True})
    assert hoodie.choose_action(ctx) == "remote"
