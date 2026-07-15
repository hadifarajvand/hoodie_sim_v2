from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ReplayTransition:
    state: tuple[float, ...]
    action: str
    reward: float
    next_state: tuple[float, ...]
    done: bool


@dataclass(slots=True)
class ReplayBuffer:
    capacity: int = 4096
    items: list[ReplayTransition] = field(default_factory=list)

    def add(self, transition: ReplayTransition) -> None:
        self.items.append(transition)
        if len(self.items) > self.capacity:
            del self.items[: len(self.items) - self.capacity]

    def sample(self, batch_size: int) -> tuple[ReplayTransition, ...]:
        if batch_size <= 0:
            return ()
        return tuple(self.items[: min(batch_size, len(self.items))])


@dataclass(slots=True)
class DuelingQNetwork:
    value_bias: float = 0.0
    advantage_biases: dict[str, float] = field(default_factory=dict)

    def q_values(self, features: tuple[float, ...], legal_actions: tuple[str, ...]) -> dict[str, float]:
        if not legal_actions:
            return {}
        state_value = self.value_bias + (sum(features) / len(features) if features else 0.0)
        advantages = {action: self.advantage_biases.get(action, 0.0) for action in legal_actions}
        mean_advantage = sum(advantages.values()) / len(advantages)
        return {action: state_value + advantage - mean_advantage for action, advantage in advantages.items()}


@dataclass(slots=True)
class DoubleDQNAgent:
    online: DuelingQNetwork = field(default_factory=DuelingQNetwork)
    target: DuelingQNetwork = field(default_factory=DuelingQNetwork)
    replay: ReplayBuffer = field(default_factory=ReplayBuffer)
    gamma: float = 0.99
    learning_rate: float = 0.01
    batch_size: int = 8
    update_interval: int = 4
    steps: int = 0

    def select(self, features: tuple[float, ...], legal_actions: tuple[str, ...]) -> str:
        q_values = self.online.q_values(features, legal_actions)
        return max(legal_actions, key=lambda action: q_values.get(action, float("-inf")))

    def masked_epsilon_greedy(self, features: tuple[float, ...], legal_actions: tuple[str, ...], epsilon: float) -> str:
        if not legal_actions:
            raise ValueError("No legal actions")
        return legal_actions[0] if epsilon <= 0.0 else self.select(features, legal_actions)

    def update(self) -> int:
        batch = self.replay.sample(self.batch_size)
        if not batch:
            return 0
        for transition in batch:
            q_values = self.online.q_values(transition.state, (transition.action,))
            target_next = self.target.q_values(transition.next_state, (transition.action,))
            target = transition.reward + (0.0 if transition.done else self.gamma * target_next.get(transition.action, 0.0))
            current = q_values.get(transition.action, 0.0)
            self.online.advantage_biases[transition.action] = current + self.learning_rate * (target - current)
        self.steps += 1
        if self.steps % self.update_interval == 0:
            self.target.value_bias = self.online.value_bias
            self.target.advantage_biases = dict(self.online.advantage_biases)
        return len(batch)
