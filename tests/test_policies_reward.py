from __future__ import annotations

from src.environment.task import Task
from src.policies.bco import BalancedCooperationOffloadingPolicy
from src.policies.flc import FullLocalComputingPolicy
from src.policies.ho import HorizontalOffloadingPolicy
from src.policies.interface import PolicyContext
from src.policies.mleo import MinimumLatencyEstimateOffloadingPolicy
from src.policies.ro import RandomOffloadingPolicy
from src.policies.vo import VerticalOffloadingPolicy
from src.training.reward_model import RewardContract, reward_for_task


def ctx(mask):
    return PolicyContext(observation={"task_size": 1.0}, legal_action_mask=mask)


def test_reward_signs():
    task = Task(task_id=1, source_agent_id=1, arrival_slot=0, size=1.0, processing_density=1.0, timeout_length=1, absolute_deadline_slot=10)
    task.terminal_outcome = "completed"
    task.completion_slot = 3
    assert reward_for_task(task, RewardContract(completion_reward=10.0), "local") == 7.0
    task.terminal_outcome = "dropped"
    assert reward_for_task(task, RewardContract(drop_penalty=5.0), "local") == -5.0


def test_policy_contracts():
    policies = [
        FullLocalComputingPolicy(),
        RandomOffloadingPolicy(seed=1),
        HorizontalOffloadingPolicy(),
        VerticalOffloadingPolicy(),
        BalancedCooperationOffloadingPolicy(),
        MinimumLatencyEstimateOffloadingPolicy(),
    ]
    for policy in policies:
        action = policy.choose_action(ctx({"local": True, "horizontal": True, "vertical": True}))
        assert action in {"local", "horizontal", "vertical"}
