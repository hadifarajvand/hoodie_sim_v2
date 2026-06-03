from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from src.agents.hoodie_agent import HoodieAgent
from src.policies import MinimumLatencyEstimateOffloadingPolicy, RandomOffloadingPolicy
from src.policies.policy_interface import PolicyContext


class RuntimePolicyAdapter(Protocol):
    policy_name: str
    compatibility_mode_used: bool

    def choose_action(self, context: PolicyContext) -> str:
        ...


@dataclass(slots=True)
class HoodieProposedPolicyAdapter:
    policy_name: str = "HOODIE_PROPOSED"
    compatibility_mode_used: bool = True
    agent: HoodieAgent = field(default_factory=lambda: HoodieAgent(policy_name="HOODIE_PROPOSED"))

    def choose_action(self, context: PolicyContext) -> str:
        return self.agent.choose_action(context)


@dataclass(slots=True)
class OriginalHoodieBaselineAdapter:
    policy_name: str = "ORIGINAL_HOODIE_BASELINE"
    compatibility_mode_used: bool = True
    policy: MinimumLatencyEstimateOffloadingPolicy = field(default_factory=MinimumLatencyEstimateOffloadingPolicy)

    def choose_action(self, context: PolicyContext) -> str:
        return self.policy.choose_action(context)


@dataclass(slots=True)
class RandomPolicyAdapter:
    seed: int = 0
    policy_name: str = "RANDOM_POLICY"
    compatibility_mode_used: bool = False
    policy: RandomOffloadingPolicy = field(init=False)

    def __post_init__(self) -> None:
        self.policy = RandomOffloadingPolicy(seed=self.seed)

    def choose_action(self, context: PolicyContext) -> str:
        return self.policy.choose_action(context)


@dataclass(slots=True)
class LocalOnlyPolicyAdapter:
    policy_name: str = "LOCAL_ONLY"
    compatibility_mode_used: bool = False

    def choose_action(self, context: PolicyContext) -> str:
        return "local"


@dataclass(slots=True)
class CloudOnlyPolicyAdapter:
    policy_name: str = "CLOUD_ONLY"
    compatibility_mode_used: bool = False

    def choose_action(self, context: PolicyContext) -> str:
        return "vertical"


def build_policy_adapter(policy_name: str, seed: int = 0) -> RuntimePolicyAdapter:
    normalized = policy_name.strip().upper()
    if normalized == "HOODIE_PROPOSED":
        return HoodieProposedPolicyAdapter()
    if normalized == "ORIGINAL_HOODIE_BASELINE":
        return OriginalHoodieBaselineAdapter()
    if normalized == "RANDOM_POLICY":
        return RandomPolicyAdapter(seed=seed)
    if normalized == "LOCAL_ONLY":
        return LocalOnlyPolicyAdapter()
    if normalized == "CLOUD_ONLY":
        return CloudOnlyPolicyAdapter()
    raise ValueError(f"Unsupported runtime evaluation policy: {policy_name!r}")

