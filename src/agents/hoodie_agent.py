from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from src.policies.interface import PolicyContext, ReplayTrainablePolicy

from .ddqn import DoubleDQNAgent, ReplayTransition
from .destination_recurrent_ddqn import DestinationRecurrentDoubleDQNAgent
from .history_builder import HistoryBuilder
from .observation_schema import ObservationSchema
from .recurrent_ddqn import RecurrentDoubleDQNAgent


Learner = (
    DoubleDQNAgent
    | RecurrentDoubleDQNAgent
    | DestinationRecurrentDoubleDQNAgent
)


@dataclass(slots=True)
class HoodieAgent(ReplayTrainablePolicy):
    policy_name: str = "HOODIE"
    observation_schema: ObservationSchema = field(default_factory=ObservationSchema)
    history_builder: HistoryBuilder = field(default_factory=HistoryBuilder)
    learner: Learner = field(default_factory=DoubleDQNAgent)
    use_lstm: bool = True
    exploration_epsilon: float = 0.0
    causal_history: list[tuple[float, ...]] = field(default_factory=list)
    decision_windows: dict[str, list[list[float]]] = field(default_factory=dict)
    active_trace_id: str | None = None

    @classmethod
    def configured(
        cls,
        *,
        seed: int,
        use_lstm: bool,
        learning_rate: float,
        discount_factor: float,
        batch_size: int,
        replay_capacity: int,
        target_update_interval: int,
        device_name: str | None = None,
        hidden_dims: tuple[int, ...] = (1024, 1024, 1024),
        lookback: int = 10,
        lstm_hidden: int = 20,
        action_order: tuple[str, ...] = ("local", "horizontal", "cloud"),
    ) -> "HoodieAgent":
        schema = ObservationSchema()
        learner = DestinationRecurrentDoubleDQNAgent(
            state_dim=len(schema.feature_names),
            action_order=action_order,
            lookback=lookback,
            seed=seed,
            hidden_dims=hidden_dims,
            lstm_hidden=lstm_hidden,
            use_lstm=use_lstm,
            learning_rate=learning_rate,
            gamma=discount_factor,
            batch_size=batch_size,
            capacity=replay_capacity,
            warmup_size=batch_size,
            target_update_interval=target_update_interval,
            device_name=device_name,
        )
        return cls(
            observation_schema=schema,
            history_builder=HistoryBuilder(window_size=lookback),
            learner=learner,
            use_lstm=use_lstm,
        )

    @property
    def action_order(self) -> tuple[str, ...]:
        if isinstance(self.learner, DestinationRecurrentDoubleDQNAgent):
            return self.learner.action_order
        if isinstance(self.learner, RecurrentDoubleDQNAgent):
            return tuple(self.learner.ACTION_ORDER)
        return ("local", "horizontal", "vertical")

    def _history_limit(self) -> int:
        return (
            self.learner.lookback
            if isinstance(self.learner, RecurrentDoubleDQNAgent)
            else 1
        )

    def _trim_history(self) -> None:
        limit = self._history_limit()
        if len(self.causal_history) > limit:
            del self.causal_history[:-limit]

    def reset_episode_history(self, trace_id: str | None = None) -> None:
        """Reset causal state at an episode boundary without touching replay memory."""

        self.causal_history.clear()
        self.decision_windows.clear()
        self.history_builder.observation_history.clear()
        self.history_builder.legal_action_history.clear()
        self.active_trace_id = trace_id

    def _prepare_trace(self, context: PolicyContext) -> None:
        trace_id = (
            str(context.trace_history[-1]) if context.trace_history else None
        )
        if trace_id != self.active_trace_id:
            self.reset_episode_history(trace_id)

    def _feature_vector(
        self, context: PolicyContext | dict[str, object]
    ) -> tuple[float, ...]:
        observation = dict(
            context.observation if isinstance(context, PolicyContext) else context
        )
        if "task_size" not in observation and "size" in observation:
            observation["task_size"] = observation["size"]
        if "private_wait_time" not in observation:
            observation["private_wait_time"] = observation.get(
                "private_queue_wait", observation.get("queue_load", 0.0)
            )
        if "offload_wait_time" not in observation:
            observation["offload_wait_time"] = observation.get(
                "offloading_queue_wait", observation.get("queue_load", 0.0)
            )
        observation["causal_history_length"] = (
            float(len(self.causal_history)) if self.use_lstm else 0.0
        )
        return self.observation_schema.encode(observation)

    def _window(self, current: tuple[float, ...]) -> np.ndarray:
        if isinstance(self.learner, RecurrentDoubleDQNAgent):
            rows = list(self.causal_history[-(self.learner.lookback - 1) :]) + [
                current
            ]
            padding = [
                tuple(0.0 for _ in range(self.learner.state_dim))
                for _ in range(self.learner.lookback - len(rows))
            ]
            return np.asarray(padding + rows, dtype=np.float32)
        return np.asarray(current, dtype=np.float32)

    @staticmethod
    def _topology_destinations(observation: dict[str, object]) -> set[str]:
        raw = observation.get("topology", ())
        if isinstance(raw, (list, tuple, set)):
            return {str(value) for value in raw}
        return set()

    def _legal_actions(
        self,
        mask: dict[str, bool],
        observation: dict[str, object],
    ) -> tuple[str, ...]:
        local_allowed = bool(mask.get("local") or mask.get("compute_local"))
        horizontal_family_allowed = bool(
            mask.get("horizontal")
            or mask.get("offload_horizontal")
        )
        exact_horizontal_keys = {
            key
            for key in mask
            if key.startswith("horizontal_")
            and key not in {"horizontal", "offload_horizontal"}
        }
        horizontal_allowed = horizontal_family_allowed or any(
            bool(mask[key]) for key in exact_horizontal_keys
        )
        cloud_allowed = bool(
            mask.get("vertical")
            or mask.get("offload_vertical")
            or mask.get("cloud")
        )
        destinations = self._topology_destinations(observation)
        legal: list[str] = []
        for action in self.action_order:
            if action == "local" and local_allowed:
                legal.append(action)
            elif action == "horizontal" and horizontal_allowed:
                legal.append(action)
            elif action.startswith("horizontal_"):
                destination = action.removeprefix("horizontal_")
                allowed = (
                    bool(mask.get(action, False))
                    if exact_horizontal_keys
                    else horizontal_family_allowed and destination in destinations
                )
                if allowed:
                    legal.append(action)
            elif action in {"cloud", "vertical"} and cloud_allowed:
                legal.append(action)
        if not legal:
            raise ValueError("no destination-specific legal actions are available")
        return tuple(legal)

    def _normalize_action(self, action: str) -> str:
        value = str(action)
        if value in {"local", "compute_local"}:
            candidate = "local"
        elif value in {"cloud", "vertical", "offload_vertical"}:
            candidate = "cloud" if "cloud" in self.action_order else "vertical"
        elif value in {"horizontal", "offload_horizontal"}:
            candidate = "horizontal"
        else:
            candidate = value
        if candidate not in self.action_order:
            raise ValueError(
                f"action {action!r} is absent from learner vocabulary {self.action_order}"
            )
        return candidate

    def choose_action(self, context: PolicyContext) -> str:
        self._prepare_trace(context)
        task_id_value = context.observation.get("task_id")
        if task_id_value is None:
            raise ValueError("task_id is required for replay-safe HOODIE decisions")
        task_id = str(task_id_value)
        if task_id in self.decision_windows:
            raise RuntimeError(
                f"duplicate unresolved HOODIE decision for task {task_id}"
            )

        legal_actions = self._legal_actions(
            context.legal_action_mask, context.observation
        )
        features = self._feature_vector(context)
        state = self._window(features)
        action = self.learner.select(
            state, legal_actions, epsilon=self.exploration_epsilon
        )
        q_summary = getattr(self.learner, "q_value_summary", None)
        context.observation["hoodie_action_order"] = self.action_order
        context.observation["hoodie_legal_actions"] = legal_actions
        context.observation["hoodie_exploration_epsilon"] = float(
            self.exploration_epsilon
        )
        if callable(q_summary):
            context.observation["hoodie_q_value_summary"] = q_summary()
        self.decision_windows[task_id] = state.tolist()
        self.history_builder.record(context)
        self.causal_history.append(features)
        self._trim_history()
        return action

    def record_transition(
        self,
        state: dict[str, object],
        action: str,
        reward: float,
        next_state: dict[str, object],
        done: bool,
        *,
        delta_slots: int = 1,
    ) -> None:
        del delta_slots
        task_id_value = state.get("task_id")
        if task_id_value is None:
            raise ValueError(
                "task_id is required to join a delayed reward to its decision"
            )
        task_id = str(task_id_value)
        normalized_action = self._normalize_action(action)
        action_index = self.action_order.index(normalized_action)
        current_vector = self._feature_vector(state)

        if isinstance(self.learner, RecurrentDoubleDQNAgent):
            remembered = self.decision_windows.pop(task_id, None)
            if remembered is None:
                raise RuntimeError(
                    f"missing decision window for delayed reward of task {task_id}"
                )
            state_value = np.asarray(remembered, dtype=np.float32)
            next_task_id = next_state.get("task_id")
            next_remembered = (
                self.decision_windows.get(str(next_task_id))
                if next_task_id is not None
                else None
            )
            next_value = (
                np.asarray(next_remembered, dtype=np.float32)
                if next_remembered is not None
                else self._window(self._feature_vector(next_state))
            )
        else:
            state_value = np.asarray(current_vector, dtype=np.float32)
            next_value = np.asarray(
                self._feature_vector(next_state), dtype=np.float32
            )

        raw_mask = next_state.get("legal_action_mask", {})
        mask = (
            {str(key): bool(value) for key, value in raw_mask.items()}
            if isinstance(raw_mask, dict)
            else {}
        )
        try:
            legal = set(self._legal_actions(mask, next_state))
        except ValueError:
            # A terminal observation may be empty. The mask is irrelevant when
            # done=True, but a correctly shaped replay value is still required.
            if not done:
                raise
            legal = set(self.action_order)
        legal_mask = np.asarray(
            [name in legal for name in self.action_order], dtype=bool
        )

        if isinstance(self.learner, RecurrentDoubleDQNAgent):
            self.learner.learner.record_transition(
                state_value,
                action_index,
                float(reward),
                next_value,
                bool(done),
                legal_mask,
            )
        else:
            self.learner.replay.add(
                ReplayTransition(
                    state_value,
                    action_index,
                    float(reward),
                    next_value,
                    bool(done),
                    legal_mask,
                )
            )

    def learn_from_replay(
        self, batch_size: int, learning_rate: float
    ) -> float | None:
        self.learner.configure(
            learning_rate=learning_rate, batch_size=batch_size
        )
        return self.learner.update(batch_size=batch_size)

    def sync_target_network(self) -> None:
        self.learner.sync_target_network()

    def attach_learner(self, learner: object, enabled: bool = True) -> None:
        if enabled and isinstance(
            learner,
            (
                DoubleDQNAgent,
                RecurrentDoubleDQNAgent,
                DestinationRecurrentDoubleDQNAgent,
            ),
        ):
            self.learner = learner
            self._trim_history()

    def export_state(self) -> dict[str, Any]:
        self._trim_history()
        return {
            "schema_version": 6,
            "policy_name": self.policy_name,
            "use_lstm": self.use_lstm,
            "exploration_epsilon": self.exploration_epsilon,
            "causal_history": [list(row) for row in self.causal_history],
            "learner": self.learner.export_state(),
        }

    @classmethod
    def from_state(cls, state: dict[str, Any]) -> "HoodieAgent":
        wrapped = (
            state.get("learner")
            if isinstance(state.get("learner"), dict)
            else None
        )
        learner_state = wrapped or (
            state
            if "online_state_dict" in state and "target_state_dict" in state
            else {}
        )
        use_lstm = bool(
            state.get("use_lstm", learner_state.get("use_lstm", True))
        )
        agent = cls(use_lstm=use_lstm)
        agent.exploration_epsilon = float(
            state.get("exploration_epsilon", 0.0)
        )
        agent.causal_history = [
            tuple(float(value) for value in row)
            for row in state.get("causal_history", [])
        ]
        if learner_state:
            learner_kind = learner_state.get("learner_kind")
            if learner_kind == "destination_recurrent_ddqn":
                agent.learner = DestinationRecurrentDoubleDQNAgent.from_state(
                    learner_state
                )
                agent.learner.use_lstm = use_lstm
            elif learner_kind == "recurrent_ddqn":
                agent.learner = RecurrentDoubleDQNAgent.from_state(learner_state)
                agent.learner.use_lstm = use_lstm
            else:
                agent.learner = DoubleDQNAgent.from_state(learner_state)
        agent.history_builder.window_size = agent._history_limit()
        agent._trim_history()
        return agent
