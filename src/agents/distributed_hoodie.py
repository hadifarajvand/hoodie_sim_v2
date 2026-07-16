from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.policies.policy_interface import PolicyContext

from .hoodie_agent import HoodieAgent


@dataclass(slots=True)
class DistributedHoodiePolicy:
    """One independently trained HOODIE learner per Edge Agent.

    The simulator presents tasks sequentially at a synchronized slot boundary. This
    dispatcher uses ``source_agent_id`` to route every decision and delayed reward to
    the learner that owns that source EA, while retaining one shared physical environment.
    """

    agents: dict[str, HoodieAgent]
    policy_name: str = "HOODIE"
    _last_agent_id: str | None = field(default=None, init=False)

    @classmethod
    def configured(
        cls,
        *,
        agent_count: int,
        seed: int,
        use_lstm: bool,
        learning_rate: float,
        discount_factor: float,
        batch_size: int,
        replay_capacity: int,
        target_update_interval: int,
        device_name: str | None = None,
    ) -> "DistributedHoodiePolicy":
        if agent_count <= 0:
            raise ValueError("agent_count must be positive")
        return cls(
            agents={
                str(index): HoodieAgent.configured(
                    seed=seed + index - 1,
                    use_lstm=use_lstm,
                    learning_rate=learning_rate,
                    discount_factor=discount_factor,
                    batch_size=batch_size,
                    replay_capacity=replay_capacity,
                    target_update_interval=target_update_interval,
                    device_name=device_name,
                )
                for index in range(1, agent_count + 1)
            }
        )

    @property
    def use_lstm(self) -> bool:
        return all(agent.use_lstm for agent in self.agents.values())

    @use_lstm.setter
    def use_lstm(self, enabled: bool) -> None:
        for agent in self.agents.values():
            agent.use_lstm = bool(enabled)

    @property
    def exploration_epsilon(self) -> float:
        if not self.agents:
            return 0.0
        return next(iter(self.agents.values())).exploration_epsilon

    @exploration_epsilon.setter
    def exploration_epsilon(self, epsilon: float) -> None:
        for agent in self.agents.values():
            agent.exploration_epsilon = float(epsilon)

    def _agent_id(self, observation: dict[str, object]) -> str:
        raw = observation.get("source_agent_id")
        if raw is None:
            if self._last_agent_id is None:
                raise ValueError("source_agent_id is required for distributed HOODIE")
            return self._last_agent_id
        agent_id = str(raw)
        if agent_id not in self.agents:
            raise ValueError(f"no HOODIE learner configured for source agent {agent_id}")
        self._last_agent_id = agent_id
        return agent_id

    def choose_action(self, context: PolicyContext) -> str:
        return self.agents[self._agent_id(context.observation)].choose_action(context)

    def learner_for(self, agent_id: str | int) -> HoodieAgent:
        key = str(agent_id)
        if key not in self.agents:
            raise ValueError(f"unknown source agent {key}")
        return self.agents[key]

    def record_transition(
        self,
        *,
        agent_id: str | int,
        state: dict[str, object],
        action: str,
        reward: float,
        next_state: dict[str, object],
        done: bool,
    ) -> None:
        self.learner_for(agent_id).record_transition(
            state=state,
            action=action,
            reward=reward,
            next_state=next_state,
            done=done,
        )

    def learn_from_replay(
        self,
        *,
        agent_id: str | int,
        batch_size: int,
        learning_rate: float,
    ) -> float | None:
        return self.learner_for(agent_id).learn_from_replay(
            batch_size=batch_size, learning_rate=learning_rate
        )

    def replay_size(self) -> int:
        return sum(len(agent.learner.replay) for agent in self.agents.values())

    def optimizer_step_count(self) -> int:
        return sum(agent.learner.learner.training_steps for agent in self.agents.values())

    def target_copy_count(self) -> int:
        return sum(agent.learner.learner.target_update_steps for agent in self.agents.values())

    def device_string(self) -> str:
        devices = {str(agent.learner.learner.device) for agent in self.agents.values()}
        if len(devices) != 1:
            raise ValueError(f"mixed learner devices are unsupported: {sorted(devices)}")
        return next(iter(devices))

    def export_state(self) -> dict[str, Any]:
        device_string = self.device_string()
        return {
            "schema_version": 1,
            "policy_name": self.policy_name,
            "policy_kind": "distributed_hoodie",
            "agent_count": len(self.agents),
            "agents": {key: agent.export_state() for key, agent in sorted(self.agents.items())},
            "backend_type": device_string.split(":", 1)[0],
            "device_string": device_string,
        }

    @classmethod
    def from_state(cls, state: dict[str, Any]) -> "DistributedHoodiePolicy":
        policy_state = state.get("policy_state") if isinstance(state.get("policy_state"), dict) else state
        agents_payload = policy_state.get("agents") if isinstance(policy_state, dict) else None
        if not isinstance(agents_payload, dict) or not agents_payload:
            # Backward compatibility: a legacy single learner becomes EA 1 only. The
            # readiness gate prevents using this conversion for a different topology.
            return cls(agents={"1": HoodieAgent.from_state(policy_state)})
        return cls(
            agents={
                str(agent_id): HoodieAgent.from_state(agent_state)
                for agent_id, agent_state in agents_payload.items()
            },
            policy_name=str(policy_state.get("policy_name", "HOODIE")),
        )
