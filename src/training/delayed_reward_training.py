from __future__ import annotations

from dataclasses import dataclass, field

from src.agents.replay_buffer import Transition
from src.environment.task import Task


@dataclass(slots=True)
class DelayedRewardTraining:
    drop_penalty: float = 40.0
    pending_transitions: dict[int, Transition] = field(default_factory=dict)

    def stage_transition(
        self,
        *,
        task: Task,
        state: dict[str, object],
        action: str,
        next_state: dict[str, object],
        done: bool,
    ) -> None:
        self.pending_transitions[task.task_id] = Transition(
            state=state,
            action=action,
            reward=0.0,
            next_state=next_state,
            done=done,
        )

    def reward_for_task(self, task: Task) -> float:
        if task.terminal_outcome == "completed" and task.completion_slot is not None:
            return -float(task.completion_slot - task.arrival_slot)
        if task.terminal_outcome == "dropped":
            return -float(self.drop_penalty)
        raise ValueError("Reward is only available after a terminal outcome is emitted")

    def release_ready_transition(self, task: Task) -> Transition | None:
        transition = self.pending_transitions.get(task.task_id)
        if transition is None or not task.reward_emitted:
            return None
        return Transition(
            state=transition.state,
            action=transition.action,
            reward=self.reward_for_task(task),
            next_state=transition.next_state,
            done=transition.done,
        )

    def consume_ready_transition(self, task: Task) -> Transition | None:
        transition = self.release_ready_transition(task)
        if transition is None:
            return None
        self.pending_transitions.pop(task.task_id, None)
        return transition
