from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Sequence
import math
import random

from src.agents.dueling_dqn import DuelingDQN
from src.agents.replay_buffer import Transition
from src.policies.adaptive_context import AdaptiveDecisionContext, build_adaptive_context
from src.policies.common import action_family, legal_actions as context_legal_actions
from src.policies.policy_interface import PolicyContext, SharedPolicy


@dataclass(frozen=True, slots=True)
class DQNDecisionTrace:
    state_vector: tuple[float, ...]
    legal_actions: tuple[str, ...]
    q_values: dict[str, float]
    chosen_action: str
    source: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "state_vector": list(self.state_vector),
            "legal_actions": list(self.legal_actions),
            "q_values": dict(self.q_values),
            "chosen_action": self.chosen_action,
            "source": self.source,
        }


@dataclass(slots=True)
class DoubleDQNTargetTrace:
    online_q_values: dict[str, float]
    target_q_values: dict[str, float]
    legal_actions: tuple[str, ...]
    chosen_action: str
    target_value: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "online_q_values": dict(self.online_q_values),
            "target_q_values": dict(self.target_q_values),
            "legal_actions": list(self.legal_actions),
            "chosen_action": self.chosen_action,
            "target_value": self.target_value,
        }


@dataclass(slots=True)
class DQNInterface:
    action_names: tuple[str, ...] = ("local", "horizontal", "vertical")
    trainable: bool = False
    default_q_value: float = 0.0
    state_feature_order: tuple[str, ...] = ("state_value",)
    q_table: dict[tuple[float, ...], dict[str, float]] = field(default_factory=dict)
    decision_trace: list[DQNDecisionTrace] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.action_names:
            raise ValueError("action_names must be non-empty")
        if len(set(self.action_names)) != len(self.action_names):
            raise ValueError("action_names must be unique")
        if len(set(self.state_feature_order)) != len(self.state_feature_order):
            raise ValueError("state_feature_order must be unique")

    def state_vector(self, state_features: Mapping[str, float] | Sequence[float]) -> tuple[float, ...]:
        if isinstance(state_features, Mapping):
            ordered_keys = list(self.state_feature_order)
            ordered_keys.extend(key for key in sorted(state_features) if key not in self.state_feature_order)
            return tuple(float(state_features.get(key, 0.0)) for key in ordered_keys)
        return tuple(float(value) for value in state_features)

    def set_q_value(self, state_features: Mapping[str, float] | Sequence[float], action: str, value: float) -> None:
        state = self.state_vector(state_features)
        q_values = dict(self.q_table.get(state, {}))
        q_values[action] = float(value)
        self.q_table[state] = q_values

    def set_q_values(self, state_features: Mapping[str, float] | Sequence[float], q_values: Mapping[str, float]) -> None:
        state = self.state_vector(state_features)
        self.q_table[state] = {str(action): float(value) for action, value in q_values.items()}

    def _stored_q_values(self, state: tuple[float, ...]) -> dict[str, float]:
        return dict(self.q_table.get(state, {}))

    def _fallback_q_value(self, state: tuple[float, ...], action: str) -> float:
        state_sum = sum(state)
        action_bias = 0.0
        if action in self.action_names:
            action_bias = float(len(self.action_names) - self.action_names.index(action)) * 0.001
        return self.default_q_value + (state_sum * 0.01) + action_bias

    def q_values(self, state_features: Mapping[str, float] | Sequence[float], legal_actions: Sequence[str]) -> dict[str, float]:
        if not legal_actions:
            raise ValueError("legal_actions must be non-empty")
        state = self.state_vector(state_features)
        stored = self._stored_q_values(state)
        return {
            action: float(stored.get(action, self._fallback_q_value(state, action)))
            for action in tuple(legal_actions)
        }

    def choose_action(self, q_values: Mapping[str, float], legal_actions: Sequence[str] | None = None) -> str:
        candidate_actions = tuple(legal_actions) if legal_actions is not None else tuple(q_values.keys())
        if not candidate_actions:
            raise ValueError("legal_actions must be non-empty")
        best_action = candidate_actions[0]
        best_value = float(q_values.get(best_action, self.default_q_value))
        best_index = 0
        for index, action in enumerate(candidate_actions[1:], start=1):
            value = float(q_values.get(action, self.default_q_value))
            if value > best_value or (value == best_value and index < best_index):
                best_action = action
                best_value = value
                best_index = index
        return best_action

    def select_action(
        self,
        state_features: Mapping[str, float] | Sequence[float],
        legal_actions: Sequence[str],
        *,
        source: str = "q_table",
    ) -> str:
        q_values = self.q_values(state_features, legal_actions)
        chosen = self.choose_action(q_values, legal_actions)
        self.decision_trace.append(
            DQNDecisionTrace(
                state_vector=self.state_vector(state_features),
                legal_actions=tuple(legal_actions),
                q_values=dict(q_values),
                chosen_action=chosen,
                source=source,
            )
        )
        return chosen

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_names": list(self.action_names),
            "trainable": self.trainable,
            "default_q_value": self.default_q_value,
            "state_feature_order": list(self.state_feature_order),
            "q_table": [
                {
                    "state_vector": list(state_vector),
                    "q_values": dict(self.q_table[state_vector]),
                }
                for state_vector in sorted(self.q_table)
            ],
            "decision_trace": [trace.to_dict() for trace in self.decision_trace],
        }


@dataclass(frozen=True, slots=True)
class DoubleDQNTargetRule:
    default_target_value: float = 0.0
    decision_trace: list[DoubleDQNTargetTrace] = field(default_factory=list)

    def select_action(self, online_q_values: Mapping[str, float], legal_actions: Sequence[str]) -> str:
        candidates = tuple(dict.fromkeys(legal_actions))
        if not candidates:
            raise ValueError("legal_actions must be non-empty")
        best_action = candidates[0]
        best_value = float(online_q_values.get(best_action, float("-inf")))
        for action in candidates[1:]:
            value = float(online_q_values.get(action, float("-inf")))
            if value > best_value:
                best_action = action
                best_value = value
        return best_action

    def target_value(
        self,
        online_q_values: Mapping[str, float],
        target_q_values: Mapping[str, float],
        legal_actions: Sequence[str],
    ) -> float:
        chosen_action = self.select_action(online_q_values, legal_actions)
        target_value = float(target_q_values.get(chosen_action, self.default_target_value))
        self.decision_trace.append(
            DoubleDQNTargetTrace(
                online_q_values=dict(online_q_values),
                target_q_values=dict(target_q_values),
                legal_actions=tuple(dict.fromkeys(legal_actions)),
                chosen_action=chosen_action,
                target_value=target_value,
            )
        )
        return target_value

    def to_dict(self) -> dict[str, Any]:
        return {
            "default_target_value": self.default_target_value,
            "decision_trace": [trace.to_dict() for trace in self.decision_trace],
        }


@dataclass(frozen=True, slots=True)
class DuelingDQNInterface:
    value_weight: float = 1.0
    advantage_weights: dict[str, float] = field(default_factory=dict)

    def q_values(self, state_features: Mapping[str, float], legal_actions: Sequence[str]) -> dict[str, float]:
        model = DuelingDQN(value_weight=self.value_weight, advantage_weights=dict(self.advantage_weights))
        return model.q_values(dict(state_features), tuple(legal_actions))

    def choose_action(self, state_features: Mapping[str, float], legal_actions: Sequence[str]) -> str:
        q_values = self.q_values(state_features, legal_actions)
        if not q_values:
            raise ValueError("legal_actions must be non-empty")
        return max(q_values, key=lambda key: (q_values[key], key))

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
class EpsilonGreedyDecisionTrace:
    episode_index: int
    epsilon: float
    mode: str
    selected_action: str
    legal_actions: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "episode_index": self.episode_index,
            "epsilon": self.epsilon,
            "mode": self.mode,
            "selected_action": self.selected_action,
            "legal_actions": list(self.legal_actions),
        }


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

    def sample_batch(
        self,
        batch_size: int,
        *,
        deterministic: bool = True,
        seed: int | None = None,
    ) -> tuple[Transition, ...]:
        if batch_size <= 0:
            return ()
        if not self._items:
            return ()
        if batch_size >= len(self._items):
            return tuple(self._items)
        if deterministic:
            rng = random.Random(self.seed + len(self._items) if seed is None else seed)
        else:
            rng = random.Random(seed) if seed is not None else random.Random()
        indices = sorted(rng.sample(range(len(self._items)), batch_size))
        return tuple(self._items[index] for index in indices)

    def __len__(self) -> int:
        return len(self._items)

    def is_empty(self) -> bool:
        return not self._items

    def sample(self, batch_size: int, *, deterministic: bool = True, seed: int | None = None) -> tuple[Transition, ...]:
        return self.sample_batch(batch_size, deterministic=deterministic, seed=seed)

    def latest(self) -> Transition | None:
        if not self._items:
            return None
        return self._items[-1]

    def clear(self) -> None:
        self._items.clear()

    def to_dict(self) -> dict[str, Any]:
        return {"capacity": self.capacity, "size": len(self._items), "seed": self.seed}


@dataclass(slots=True)
class EpsilonGreedyTrainingSchedule:
    epsilon_start: float = 1.0
    epsilon_end: float = 0.0
    total_episodes: int = 100
    decay_episodes: int | None = None
    exploration_seed: int = 13
    decision_trace: list[EpsilonGreedyDecisionTrace] = field(default_factory=list)

    def __post_init__(self) -> None:
        effective_total_episodes = self.total_episodes if self.decay_episodes is None else self.decay_episodes
        if effective_total_episodes <= 0:
            raise ValueError("total_episodes must be positive")
        if self.epsilon_start < self.epsilon_end:
            raise ValueError("epsilon_start must be greater than or equal to epsilon_end")
        self.total_episodes = int(effective_total_episodes)
        if self.decay_episodes is None:
            self.decay_episodes = int(effective_total_episodes)

    def epsilon(self, episode_index: int) -> float:
        if episode_index < 0:
            raise ValueError("episode_index must be non-negative")
        if episode_index == 0:
            return self.epsilon_start
        half_point = max(1, self.total_episodes // 2)
        if episode_index >= half_point:
            return self.epsilon_end
        progress = episode_index / half_point
        return self.epsilon_start + (self.epsilon_end - self.epsilon_start) * progress

    def epsilon_for_inference(self) -> float:
        return 0.0

    def _exploration_action(self, legal_actions: Sequence[str], *, episode_index: int, seed: int | None = None, deterministic: bool = True) -> str:
        if not legal_actions:
            raise ValueError("legal_actions must be non-empty")
        ordered_actions = tuple(sorted(dict.fromkeys(legal_actions)))
        if deterministic:
            index = (self.exploration_seed + episode_index + (seed or 0)) % len(ordered_actions)
            return ordered_actions[index]
        rng = random.Random(seed if seed is not None else self.exploration_seed + episode_index + len(ordered_actions))
        return rng.choice(ordered_actions)

    def select_action(
        self,
        dqn_interface: DQNInterface,
        state_features: Mapping[str, float] | Sequence[float],
        legal_actions: Sequence[str],
        *,
        episode_index: int,
        use_inference: bool = False,
        force_mode: str | None = None,
        deterministic_exploration: bool = True,
        exploration_seed: int | None = None,
    ) -> str:
        if not legal_actions:
            raise ValueError("legal_actions must be non-empty")
        if episode_index < 0:
            raise ValueError("episode_index must be non-negative")

        epsilon = self.epsilon_for_inference() if use_inference else self.epsilon(episode_index)
        mode: str
        if use_inference:
            mode = "inference"
        elif force_mode == "explore":
            mode = "explore"
        elif force_mode == "exploit":
            mode = "exploit"
        else:
            rng = random.Random((exploration_seed if exploration_seed is not None else self.exploration_seed) + episode_index + len(legal_actions))
            mode = "explore" if rng.random() < epsilon else "exploit"

        if mode in {"exploit", "inference"}:
            selected_action = dqn_interface.select_action(state_features, legal_actions, source=f"epsilon_greedy:{mode}")
        else:
            selected_action = self._exploration_action(
                legal_actions,
                episode_index=episode_index,
                seed=exploration_seed,
                deterministic=deterministic_exploration,
            )

        self.decision_trace.append(
            EpsilonGreedyDecisionTrace(
                episode_index=episode_index,
                epsilon=epsilon,
                mode=mode,
                selected_action=selected_action,
                legal_actions=tuple(legal_actions),
            )
        )
        return selected_action

    def to_dict(self) -> dict[str, Any]:
        return {
            "epsilon_start": self.epsilon_start,
            "epsilon_end": self.epsilon_end,
            "total_episodes": self.total_episodes,
            "decay_episodes": self.decay_episodes,
            "exploration_seed": self.exploration_seed,
            "decision_trace": [trace.to_dict() for trace in self.decision_trace],
        }


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
    exploration_seed: int = 23
    family_biases: dict[str, float] = field(default_factory=dict)
    decision_history: list[dict[str, Any]] = field(default_factory=list)

    def _coerce_float(self, value: object) -> float | None:
        if isinstance(value, (int, float)):
            return float(value)
        return None

    def _decision_pressure(self, adaptive_context: AdaptiveDecisionContext) -> float:
        queue_load = self._coerce_float(adaptive_context.queue_load)
        load_hint = self._coerce_float(adaptive_context.observation.get("load_hint"))
        observed_arrival = self._coerce_float(adaptive_context.observed_arrival_probability)
        cycles_remaining = self._coerce_float(adaptive_context.cycles_remaining)
        deadline_slack: float | None = None
        if adaptive_context.absolute_deadline_slot is not None and adaptive_context.current_slot is not None:
            deadline_slack = float(max(1, adaptive_context.absolute_deadline_slot - adaptive_context.current_slot))

        pressure_terms: list[float] = []
        for value in (queue_load, load_hint, observed_arrival):
            if value is not None:
                pressure_terms.append(value)
        if cycles_remaining is not None:
            if deadline_slack is not None:
                pressure_terms.append(cycles_remaining / deadline_slack)
            else:
                pressure_terms.append(cycles_remaining)
        return max(pressure_terms) if pressure_terms else 0.0

    def _base_features(self, adaptive_context: AdaptiveDecisionContext, legal_actions: Sequence[str]) -> dict[str, float]:
        topology = adaptive_context.topology
        topology_size = 0.0
        if isinstance(topology, (tuple, list, set)):
            topology_size = float(len(topology))
        elif hasattr(topology, "__len__"):
            try:
                topology_size = float(len(topology))  # type: ignore[arg-type]
            except TypeError:
                topology_size = 0.0

        queue_load = self._coerce_float(adaptive_context.queue_load) or 0.0
        load_hint = self._coerce_float(adaptive_context.observation.get("load_hint")) or 0.0
        cycles_remaining = self._coerce_float(adaptive_context.cycles_remaining) or 0.0
        deadline_slack = 0.0
        if adaptive_context.absolute_deadline_slot is not None and adaptive_context.current_slot is not None:
            deadline_slack = float(max(0, adaptive_context.absolute_deadline_slot - adaptive_context.current_slot))

        return {
            "state_value": float(len(adaptive_context.observation) + len(adaptive_context.legal_action_mask) + len(tuple(legal_actions))),
            "queue_load": queue_load,
            "load_hint": load_hint,
            "cycles_remaining": cycles_remaining,
            "deadline_slack": deadline_slack,
            "topology_size": topology_size,
            "fallback_hint_total": float(
                sum(
                    float(value)
                    for value in (
                        adaptive_context.observation.get("fallback_hints", {}) or {}
                    ).values()
                    if isinstance(value, (int, float))
                )
            ),
        }

    def _family_score(self, adaptive_context: AdaptiveDecisionContext, family: str) -> float:
        pressure = self._decision_pressure(adaptive_context)
        if pressure <= 0.5:
            score_map = {"local": 3.2, "horizontal": 1.4, "vertical": 0.8}
        elif pressure <= 1.5:
            score_map = {"local": 1.9, "horizontal": 3.1, "vertical": 2.2}
        else:
            score_map = {"local": 0.7, "horizontal": 2.2, "vertical": 3.3}
        score = score_map.get(family, 0.0)
        fallback_hints = adaptive_context.observation.get("fallback_hints")
        if isinstance(fallback_hints, dict):
            hint = fallback_hints.get(family)
            if isinstance(hint, (int, float)):
                score += float(hint) * 0.1
        score += float(self.family_biases.get(family, 0.0))
        if adaptive_context.topology is not None and family == "horizontal":
            score += 0.2
        if adaptive_context.absolute_deadline_slot is not None and adaptive_context.current_slot is not None:
            deadline_slack = adaptive_context.absolute_deadline_slot - adaptive_context.current_slot
            if deadline_slack <= 1 and family == "vertical":
                score += 0.3
            if deadline_slack > 2 and family == "local":
                score += 0.1
        return score

    def score_actions(self, adaptive_context: AdaptiveDecisionContext, legal_actions: Sequence[str]) -> dict[str, float]:
        normalized_legal = tuple(dict.fromkeys(legal_actions))
        if not normalized_legal:
            return {}
        features = self._base_features(adaptive_context, normalized_legal)
        q_values = self.dueling_interface.q_values(features, normalized_legal)
        dqn_values = self.dqn_interface.q_values(features, normalized_legal)
        scores: dict[str, float] = {}
        fallback_hints = adaptive_context.observation.get("fallback_hints")
        hint_map = fallback_hints if isinstance(fallback_hints, dict) else {}
        latency_estimates = adaptive_context.observation.get("latency_estimates")
        latency_map = latency_estimates if isinstance(latency_estimates, dict) else {}
        balance_hint = adaptive_context.observation.get("balance_hint")
        balance_map = balance_hint if isinstance(balance_hint, dict) else {}

        for action in normalized_legal:
            family = action_family(action)
            score = q_values.get(action, 0.0) + dqn_values.get(action, 0.0) + self._family_score(adaptive_context, family)
            for candidate in (action, family):
                hint = hint_map.get(candidate)
                if isinstance(hint, (int, float)):
                    score += float(hint) * 0.05
                latency = latency_map.get(candidate)
                if isinstance(latency, (int, float)):
                    score -= float(latency) * 0.05
                balance = balance_map.get(candidate)
                if isinstance(balance, (int, float)):
                    score += float(balance) * 0.05
            if action in {"local", "compute_local"} and family == "local":
                score += 0.05
            elif action in {"horizontal", "offload_horizontal"} and family == "horizontal":
                score += 0.05
            elif action in {"vertical", "offload_vertical"} and family == "vertical":
                score += 0.05
            scores[action] = score
        return scores

    def _choose_greedy(self, scores: Mapping[str, float]) -> str:
        if not scores:
            raise ValueError("scores must be non-empty")
        return max(scores, key=lambda key: (scores[key], key))

    def _choose_exploratory(self, legal_actions: Sequence[str], *, episode_index: int, trace_history: Sequence[object]) -> str:
        rng = random.Random(self.exploration_seed + episode_index + len(legal_actions) + len(trace_history))
        return rng.choice(tuple(sorted(legal_actions)))

    def choose_from_context(self, context: PolicyContext, *, episode_index: int = 0, use_inference: bool = False) -> str:
        legal = context_legal_actions(context)
        if not legal:
            raise ValueError("legal_actions must be non-empty")
        adaptive_context = build_adaptive_context(context)
        scores = self.score_actions(adaptive_context, legal)
        epsilon = 0.0 if use_inference else self.schedule.epsilon(episode_index)
        if self.inference.epsilon == 0.0 or use_inference:
            chosen = self._choose_greedy(scores)
        elif epsilon <= 0.0:
            chosen = self._choose_greedy(scores)
        else:
            exploratory_rng = random.Random(self.exploration_seed + episode_index + len(legal) + len(context.trace_history))
            if exploratory_rng.random() < epsilon:
                chosen = self._choose_exploratory(legal, episode_index=episode_index, trace_history=context.trace_history)
            else:
                chosen = self._choose_greedy(scores)
        self.decision_history.append(
            {
                "agent_id": self.agent_id,
                "episode_index": episode_index,
                "use_inference": use_inference,
                "epsilon": epsilon,
                "legal_actions": tuple(legal),
                "scores": dict(scores),
                "chosen_action": chosen,
                "chosen_family": action_family(chosen),
            }
        )
        return chosen

    def choose_action(
        self,
        state_or_context: Mapping[str, float] | PolicyContext,
        legal_actions: Sequence[str] | None = None,
        *,
        episode_index: int = 0,
        use_inference: bool = False,
    ) -> str:
        if isinstance(state_or_context, PolicyContext):
            return self.choose_from_context(state_or_context, episode_index=episode_index, use_inference=use_inference)
        if legal_actions is None:
            raise TypeError("legal_actions must be provided when choosing from raw state features")
        normalized_legal = tuple(dict.fromkeys(legal_actions))
        if not normalized_legal:
            raise ValueError("legal_actions must be non-empty")
        q_values = self.dueling_interface.q_values(state_or_context, normalized_legal)
        if use_inference or self.inference.epsilon == 0.0:
            return self.inference.choose_action(q_values)
        epsilon = self.schedule.epsilon(episode_index)
        if epsilon <= 0.0:
            return self.inference.choose_action(q_values)
        rng = random.Random(self.exploration_seed + episode_index + len(normalized_legal))
        if rng.random() < epsilon:
            return rng.choice(tuple(sorted(normalized_legal)))
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
            "family_biases": dict(self.family_biases),
            "decision_history_size": len(self.decision_history),
        }
