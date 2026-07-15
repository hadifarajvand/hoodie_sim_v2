from __future__ import annotations

from src.agents.hoodie_agent import HoodieAgent
from src.policies.interface import PolicyContext


def test_two_learners_distinct_owned_transitions():
    left = HoodieAgent()
    right = HoodieAgent()
    ctx_left = PolicyContext(observation={"task_size": 1.0}, legal_action_mask={"local": True, "horizontal": False, "vertical": False})
    ctx_right = PolicyContext(observation={"task_size": 2.0}, legal_action_mask={"local": False, "horizontal": True, "vertical": False})
    assert left.choose_action(ctx_left) == "local"
    assert right.choose_action(ctx_right) == "horizontal"
    left.record_transition({"task_size": 1.0}, "local", 1.0, {"task_size": 1.1}, True)
    right.record_transition({"task_size": 2.0}, "horizontal", 2.0, {"task_size": 2.1}, True)
    assert len(left.learner.replay.items) == 1
    assert len(right.learner.replay.items) == 1
