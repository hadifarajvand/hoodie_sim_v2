from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PolicyBinding:
    agent_id: int
    policy: Any


@dataclass
class PolicyBindingRegistry:
    bindings: dict[int, PolicyBinding] = field(default_factory=dict)

    def bind(self, agent_id: int, policy: Any) -> None:
        self.bindings[int(agent_id)] = PolicyBinding(agent_id=int(agent_id), policy=policy)

    def bind_many(self, mapping: dict[int, Any]) -> None:
        for agent_id, policy in mapping.items():
            self.bind(agent_id, policy)

    def get(self, agent_id: int) -> Any | None:
        binding = self.bindings.get(int(agent_id))
        return None if binding is None else binding.policy

    def items(self):
        for agent_id in sorted(self.bindings):
            yield agent_id, self.bindings[agent_id].policy

    def policies(self) -> dict[int, Any]:
        return {agent_id: binding.policy for agent_id, binding in sorted(self.bindings.items())}
