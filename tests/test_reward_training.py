from __future__ import annotations

from src.agents.hoodie_agent import HoodieAgent
from src.policies.interface import PolicyContext
from src.training.delayed_reward_training import DelayedRewardTraining
from src.environment.task import Task


def test_delayed_reward_exactly_once():
    trainer = DelayedRewardTraining()
    task = Task(task_id=1, source_agent_id=1, arrival_slot=0, size=1.0, processing_density=1.0, timeout_length=1, absolute_deadline_slot=10)
    trainer.stage_transition(task=task, state={"task_size": 1.0}, action="local", next_state={"task_size": 2.0}, done=True)
    task.terminal_outcome = "completed"
    task.completion_slot = 2
    task.reward_emitted = True
    assert trainer.consume_ready_transition(task) is not None
    assert trainer.consume_ready_transition(task) is None


def test_hoodie_checkpoint_round_trip():
    agent = HoodieAgent()
    agent.causal_history.append({"task_size": 1.0})
    restored = HoodieAgent.from_state(agent.export_state())
    assert restored.export_state()["causal_history"] == [{"task_size": 1.0}]
