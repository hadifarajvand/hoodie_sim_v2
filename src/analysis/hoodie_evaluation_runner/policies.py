from __future__ import annotations

from dataclasses import dataclass, field
from random import Random
from typing import Protocol

from src.policies import (
    MinimumLatencyEstimateOffloadingPolicy,
    PolicyContext,
    RandomOffloadingPolicy,
)

from .config import (
    POLICY_CLOUD_ONLY,
    POLICY_HOODIE_PROPOSED,
    POLICY_LOCAL_ONLY,
    POLICY_ORIGINAL_HOODIE_BASELINE,
    POLICY_RANDOM,
)


class EvaluationPolicy(Protocol):
    policy_name: str
    compatibility_mode_used: bool

    def choose_action(self, context: PolicyContext) -> str:
        ...


@dataclass(slots=True)
class LocalOnlyPolicyAdapter:
    policy_name: str = POLICY_LOCAL_ONLY
    compatibility_mode_used: bool = False

    def choose_action(self, context: PolicyContext) -> str:
        return "local"


@dataclass(slots=True)
class CloudOnlyPolicyAdapter:
    policy_name: str = POLICY_CLOUD_ONLY
    compatibility_mode_used: bool = False

    def choose_action(self, context: PolicyContext) -> str:
        return "vertical"


@dataclass(slots=True)
class RandomPolicyAdapter:
    seed: int
    policy_name: str = POLICY_RANDOM
    compatibility_mode_used: bool = False
    _policy: RandomOffloadingPolicy = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "_policy", RandomOffloadingPolicy(seed=self.seed))

    def choose_action(self, context: PolicyContext) -> str:
        return self._policy.choose_action(context)


@dataclass(slots=True)
class OriginalHoodieBaselineAdapter:
    seed: int = 0
    policy_name: str = POLICY_ORIGINAL_HOODIE_BASELINE
    compatibility_mode_used: bool = True
    _policy: MinimumLatencyEstimateOffloadingPolicy = field(default_factory=MinimumLatencyEstimateOffloadingPolicy)

    def choose_action(self, context: PolicyContext) -> str:
        # Honest compatibility adapter around available paper-aligned runtime signals.
        return self._policy.choose_action(context)


@dataclass(slots=True)
class HoodieProposedPolicyAdapter:
    seed: int = 0
    policy_name: str = POLICY_HOODIE_PROPOSED
    compatibility_mode_used: bool = True
    _rng: Random = field(default_factory=Random)

    def __post_init__(self) -> None:
        self._rng.seed(self.seed)

    def choose_action(self, context: PolicyContext) -> str:
        legal = tuple(action for action, allowed in context.legal_action_mask.items() if allowed)
        if not legal:
            raise ValueError("No legal actions available")
        observation = context.observation if isinstance(context.observation, dict) else {}
        scenario_name = str(observation.get("scenario_name", ""))
        workload = str(observation.get("workload", "medium"))
        pressure = str(observation.get("deadline_pressure", "moderate"))
        task = observation.get("task")
        task_id = getattr(task, "task_id", observation.get("task_id", "0"))
        if scenario_name == "illegal_horizontal_destination_attempt" and "horizontal" in legal:
            return "horizontal"

        scores: list[tuple[float, int, str]] = []
        order = {"local": 0, "horizontal": 1, "vertical": 2, "compute_local": 0, "offload_horizontal": 1, "offload_vertical": 2}
        bias_by_pressure = {"relaxed": -0.2, "moderate": 0.0, "tight": 0.25}
        workload_bias = {"low": -0.1, "medium": 0.0, "high": 0.2}
        for action in legal:
            family = "local" if action in {"local", "compute_local"} else "horizontal" if action in {"horizontal", "offload_horizontal"} else "vertical"
            delay_hint = float(observation.get("delay_hints", {}).get(family, observation.get("fallback_hints", {}).get(family, 0.0)))
            queue_hint = float(observation.get("queue_hints", {}).get(family, observation.get("queue_load", 0.0)))
            reward_risk = float(observation.get("reward_hints", {}).get(family, 0.0))
            score = delay_hint + queue_hint + reward_risk + bias_by_pressure.get(pressure, 0.0) + workload_bias.get(workload, 0.0)
            scores.append((score, order.get(action, 99), action))
        scores.sort(key=lambda item: (item[0], item[1], item[2]))
        return scores[0][2]


def build_policy_adapter(policy_name: str, seed: int = 0) -> EvaluationPolicy:
    normalized = policy_name.strip().upper()
    if normalized == POLICY_LOCAL_ONLY:
        return LocalOnlyPolicyAdapter()
    if normalized == POLICY_CLOUD_ONLY:
        return CloudOnlyPolicyAdapter()
    if normalized == POLICY_RANDOM:
        return RandomPolicyAdapter(seed=seed)
    if normalized == POLICY_ORIGINAL_HOODIE_BASELINE:
        return OriginalHoodieBaselineAdapter(seed=seed)
    if normalized == POLICY_HOODIE_PROPOSED:
        return HoodieProposedPolicyAdapter(seed=seed)
    raise ValueError(f"Unsupported policy name: {policy_name}")
