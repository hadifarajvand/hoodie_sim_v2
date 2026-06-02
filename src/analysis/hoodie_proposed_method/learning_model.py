from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Sequence
import math
import random

from src.agents.double_dqn import DoubleDQNSelector
from src.agents.dueling_dqn import DuelingDQN
from src.agents.replay_buffer import Transition


@dataclass(frozen=True, slots=True)
class DQNInterface:
    action_names: tuple[str, ...] = ("local", "horizontal", "vertical")
    trainable: bool = False

    def q_values(self, state_features: Mapping[str, float], legal_actions: Sequence[str]) -> dict[str, float]:
        if not legal_actions:
            return {}
        state_value = float(state_features.get("state_value", 0.0))
        return {action: state_value for action in legal_actions}

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class DoubleDQNTargetRule:
    selector: DoubleDQNSelector = field(default_factory=DoubleDQNSelector)

    def target_value(self, online_q_values: dict[str, float], target_q_values: dict[str, float], legal_actions: tuple[str, ...]) -> float:
        return self.selector.target_value(online_q_values, target_q_values, legal_actions)

    def to_dict(self) -> dict[str, Any]:
        return {"selector": self.selector.__class__.__name__}


@dataclass(frozen=True, slots=True)
class DuelingDQNInterface:
    value_weight: float = 1.0
    advantage_weights: dict[str, float] = field(default_factory=dict)

    def q_values(self, state_features: Mapping[str, float], legal_actions: Sequence[str]) -> dict[str, float]:
        model = DuelingDQN(value_weight=self.value_weight, advantage_weights=dict(self.advantage_weights))
        return model.q_values(dict(state_features), tuple(legal_actions))

    def to_dict(self) -> dict[str, Any]:
        return {
            "value_weight": self.value_weight,
            "advantage_weights": dict(self.advantage_weights),
        }


@dataclass(frozen=True, slots=True)
class LSTMForecastRecoveryInterface:
    lookback_window: int = 10

    def forecast(self, history: Sequence[float]) -> float:
        if not history:
            return 0.0
        window = list(history)[-self.lookback_window :]
        return sum(window) / len(window)

    def recover(self, delayed_history: Sequence[float]) -> float:
        if not delayed_history:
            return 0.0
        return float(delayed_history[-1])

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ReplayMemoryInterface:
    capacity: int = 10_000
    seed: int = 7
    _items: list[Transition] = field(default_factory=list)

    def add(self, transition: Transition) -> None:
        self._items.append(transition)
        if len(self._items) > self.capacity:
            self._items.pop(0)

    def extend(self, transitions: Sequence[Transition]) -> None:
        for transition in transitions:
            self.add(transition)

    def sample_batch(self, batch_size: int) -> tuple[Transition, ...]:
        if batch_size <= 0:
            return ()
        if not self._items:
            return ()
        if batch_size >= len(self._items):
            return tuple(self._items)
        rng = random.Random(self.seed + len(self._items))
        indices = sorted(rng.sample(range(len(self._items)), batch_size))
        return tuple(self._items[index] for index in indices)

    def to_dict(self) -> dict[str, Any]:
        return {"capacity": self.capacity, "size": len(self._items), "seed": self.seed}


@dataclass(frozen=True, slots=True)
class EpsilonGreedyTrainingSchedule:
    epsilon_start: float = 1.0
    epsilon_end: float = 0.0
    decay_episodes: int = 100

    def epsilon(self, episode_index: int) -> float:
        if episode_index <= 0:
            return self.epsilon_start
        half_point = max(1, self.decay_episodes // 2)
        if episode_index >= half_point:
            return self.epsilon_end
        progress = episode_index / half_point
        return self.epsilon_start + (self.epsilon_end - self.epsilon_start) * progress

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class InferenceMode:
    epsilon: float = 0.0

    def choose_action(self, q_values: Mapping[str, float]) -> str:
        if not q_values:
            raise ValueError("q_values must be non-empty")
        return max(q_values, key=lambda key: (q_values[key], key))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class DistributedEdgeAgentDecisionModel:
    agent_id: str
    dqn_interface: DQNInterface = field(default_factory=DQNInterface)
    dueling_interface: DuelingDQNInterface = field(default_factory=DuelingDQNInterface)
    replay_memory: ReplayMemoryInterface = field(default_factory=ReplayMemoryInterface)
    schedule: EpsilonGreedyTrainingSchedule = field(default_factory=EpsilonGreedyTrainingSchedule)
    inference: InferenceMode = field(default_factory=InferenceMode)
    target_rule: DoubleDQNTargetRule = field(default_factory=DoubleDQNTargetRule)
    lstm_interface: LSTMForecastRecoveryInterface = field(default_factory=LSTMForecastRecoveryInterface)

    def choose_action(self, state_features: Mapping[str, float], legal_actions: Sequence[str], *, episode_index: int, use_inference: bool = False) -> str:
        if not legal_actions:
            raise ValueError("legal_actions must be non-empty")
        q_values = self.dueling_interface.q_values(state_features, legal_actions)
        if use_inference or self.inference.epsilon == 0.0:
            return self.inference.choose_action(q_values)
        epsilon = self.schedule.epsilon(episode_index)
        if epsilon <= 0.0:
            return self.inference.choose_action(q_values)
        rng = random.Random(episode_index + len(legal_actions))
        if rng.random() < epsilon:
            return sorted(legal_actions)[0]
        return self.inference.choose_action(q_values)

    def record_transition(self, state: dict[str, object], action: str, reward: float, next_state: dict[str, object], done: bool) -> None:
        self.replay_memory.add(Transition(state=state, action=action, reward=reward, next_state=next_state, done=done))

    def sample_replay_batch(self, batch_size: int) -> tuple[Transition, ...]:
        return self.replay_memory.sample_batch(batch_size)

    def target_value(self, online_q_values: dict[str, float], target_q_values: dict[str, float], legal_actions: tuple[str, ...]) -> float:
        return self.target_rule.target_value(online_q_values, target_q_values, legal_actions)

    def forecast_next_load(self, history: Sequence[float]) -> float:
        return self.lstm_interface.forecast(history)

    def recover_delayed_load(self, delayed_history: Sequence[float]) -> float:
        return self.lstm_interface.recover(delayed_history)

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "dqn_interface": self.dqn_interface.to_dict(),
            "dueling_interface": self.dueling_interface.to_dict(),
            "replay_memory": self.replay_memory.to_dict(),
            "schedule": self.schedule.to_dict(),
            "inference": self.inference.to_dict(),
            "lstm_interface": self.lstm_interface.to_dict(),
        }
