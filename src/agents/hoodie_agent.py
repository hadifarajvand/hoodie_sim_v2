from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.policies.policy_interface import PolicyContext, SharedPolicy

from .double_dqn import DoubleDQNSelector
from .history_builder import HistoryBuilder
from .hoodie_model import HoodieModel
from .torchrl_hoodie_learner import TorchRLHoodieLearner
from .torchrl_tensor_adapter import TorchRLTensorAdapter
from .replay_buffer import ReplayBuffer, Transition
from .target_network import TargetNetwork


@dataclass(slots=True)
class HoodieAgent(SharedPolicy):
    policy_name: str = "HOODIE"
    history_builder: HistoryBuilder = field(default_factory=HistoryBuilder)
    replay_buffer: ReplayBuffer = field(default_factory=ReplayBuffer)
    target_network: TargetNetwork = field(default_factory=TargetNetwork)
    model: HoodieModel = field(default_factory=HoodieModel)
    selector: DoubleDQNSelector = field(default_factory=DoubleDQNSelector)
    learner: TorchRLHoodieLearner | None = None
    learner_enabled: bool = False
    tensor_adapter: TorchRLTensorAdapter = field(default_factory=TorchRLTensorAdapter)

    def choose_action(self, context: PolicyContext) -> str:
        history = self.history_builder.build(context)
        legal_actions = tuple(action for action, allowed in context.legal_action_mask.items() if allowed)
        if self.learner_enabled and self.learner is not None:
            adapted_state = self.tensor_adapter.adapt(history, context.legal_action_mask)
            learner_output = self.learner.score(adapted_state)
            q_values = dict(learner_output.get("action_scores", {}))
            legal_actions = tuple(learner_output.get("legal_actions", legal_actions))
        else:
            q_values = self.model.forward(history, legal_actions)
        action = self.selector.select_action(q_values, legal_actions)
        self.history_builder.record(context)
        return action

    def attach_learner(self, learner: TorchRLHoodieLearner, enabled: bool = False) -> None:
        self.learner = learner
        self.learner_enabled = bool(enabled)

    def enable_learner(self) -> None:
        if self.learner is None:
            raise RuntimeError("Cannot enable learner mode without an attached learner")
        self.learner_enabled = True

    def disable_learner(self) -> None:
        self.learner_enabled = False

    def record_transition(self, state: dict[str, object], action: str, reward: float, next_state: dict[str, object], done: bool) -> None:
        self.replay_buffer.add(Transition(state=state, action=action, reward=reward, next_state=next_state, done=done))

    def learn_from_replay(self, batch_size: int, learning_rate: float) -> int:
        if batch_size <= 0:
            return 0
        if self.learner_enabled and self.learner is not None:
            batch = self.replay_buffer.sample(batch_size)
            if not batch:
                return 0
            return self.learner.update(batch, learning_rate)
        learnable = getattr(self.model, "learn_from_transitions", None)
        if learnable is None:
            return 0
        batch = self.replay_buffer.sample(batch_size)
        if not batch:
            return 0
        return learnable(batch, learning_rate)

    def sync_target_network(self) -> None:
        learned_preferences = getattr(self.model, "learned_action_preferences", {})
        self.target_network.copy_from(
            {
                "value_weight": self.model.dueling_dqn.value_weight,
                **{f"learned:{action}": preference for action, preference in learned_preferences.items()},
                **self.model.action_biases,
            }
        )

    def export_state(self) -> dict[str, Any]:
        state = {
            "schema_version": 1,
            "policy_name": self.policy_name,
            "model": self.model.to_state(),
            "target_network": {
                "parameters": {
                    key: self.target_network.parameters[key]
                    for key in sorted(self.target_network.parameters)
                },
            },
        }
        if self.learner is not None:
            learner_state = self.learner.state_dict()
            if not isinstance(learner_state, dict):
                raise TypeError("TorchRLHoodieLearner.state_dict() must return a mapping")
            learner_schema_version = int(learner_state.get("schema_version", 1))
            if learner_schema_version != 1:
                raise ValueError(f"Unsupported TorchRLHoodieLearner state schema version: {learner_schema_version}")
            learned_preferences = learner_state.get("learned_action_preferences", {})
            if not isinstance(learned_preferences, dict):
                raise TypeError("TorchRLHoodieLearner state learned_action_preferences must be a mapping")
            state["learner_state"] = {
                "schema_version": learner_schema_version,
                "learned_action_preferences": {
                    action: float(learned_preferences[action])
                    for action in sorted(learned_preferences)
                },
            }
            state["learner_enabled"] = self.learner_enabled
        return state

    @classmethod
    def from_state(cls, state: dict[str, Any]) -> "HoodieAgent":
        schema_version = int(state.get("schema_version", 1))
        if schema_version != 1:
            raise ValueError(f"Unsupported HoodieAgent state schema version: {schema_version}")
        model_state = state.get("model", {})
        if not isinstance(model_state, dict):
            raise ValueError("HoodieAgent state model must be a mapping")
        target_state = state.get("target_network", {})
        if not isinstance(target_state, dict):
            raise ValueError("HoodieAgent state target_network must be a mapping")

        agent = cls()
        agent.model = HoodieModel.from_state(model_state)
        parameters = target_state.get("parameters", {})
        if not isinstance(parameters, dict):
            raise ValueError("HoodieAgent state target_network.parameters must be a mapping")
        agent.target_network.parameters = {str(key): float(value) for key, value in parameters.items()}
        learner_state = state.get("learner_state")
        if learner_state is not None:
            if not isinstance(learner_state, dict):
                raise ValueError("HoodieAgent state learner_state must be a mapping")
            learner_schema_version = int(learner_state.get("schema_version", 1))
            if learner_schema_version != 1:
                raise ValueError(f"Unsupported HoodieAgent state learner_state schema version: {learner_schema_version}")
            learner = TorchRLHoodieLearner()
            learner.load_state_dict(learner_state)
            agent.learner = learner
            agent.learner_enabled = bool(state.get("learner_enabled", False))
        return agent
