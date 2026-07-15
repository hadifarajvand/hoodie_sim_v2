from __future__ import annotations

from dataclasses import dataclass

from src.environment.task import Task


@dataclass(frozen=True, slots=True)
class RewardContract:
    completion_reward: float = 1.0
    drop_penalty: float = 40.0
    action_cost_local: float = 0.0
    action_cost_horizontal: float = 0.0
    action_cost_vertical: float = 0.0
    normalize: bool = False
    clip_min: float | None = None
    clip_max: float | None = None


@dataclass(frozen=True, slots=True)
class RewardEvent:
    task_id: int
    agent_id: str
    decision_slot: int
    resolution_slot: int
    reward: float
    terminal: bool
    ownership: str


@dataclass(frozen=True, slots=True)
class RewardResult:
    reward: float
    resolved_slot: int
    terminal: bool
    ownership: str


def reward_for_task(task: Task, contract: RewardContract, action_family: str) -> float:
    if task.terminal_outcome == "completed" and task.completion_slot is not None:
        reward = contract.completion_reward - float(task.completion_slot - task.arrival_slot)
    elif task.terminal_outcome == "dropped":
        reward = -float(contract.drop_penalty)
    else:
        reward = 0.0
    cost = {
        "local": contract.action_cost_local,
        "horizontal": contract.action_cost_horizontal,
        "vertical": contract.action_cost_vertical,
    }.get(action_family, 0.0)
    reward -= float(cost)
    if contract.clip_min is not None:
        reward = max(contract.clip_min, reward)
    if contract.clip_max is not None:
        reward = min(contract.clip_max, reward)
    return reward
