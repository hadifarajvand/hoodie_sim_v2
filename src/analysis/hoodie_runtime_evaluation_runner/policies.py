from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from src.agents.hoodie_agent import HoodieAgent
from src.policies.adaptive_offloading import AdaptiveOffloadingPolicy
from src.policies.common import action_family, legal_actions, placement_actions_for_family
from src.policies.mleo import build_delay_candidates
from src.policies.ro import RandomOffloadingPolicy
from src.policies.policy_interface import PolicyContext


class RuntimePolicyAdapter(Protocol):
    policy_name: str
    compatibility_mode_used: bool
    last_decision_trace: tuple[str, ...]

    def choose_action(self, context: PolicyContext) -> str:
        ...


def _numeric(value: object, default: float = 0.0) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    return float(default)


def _family_score(context: PolicyContext, family: str) -> float:
    observation = context.observation if isinstance(context.observation, dict) else {}
    delay_hints = observation.get("delay_hints", {})
    queue_hints = observation.get("queue_hints", {})
    reward_hints = observation.get("reward_hints", {})
    scenario_name = str(observation.get("scenario_name", ""))
    workload = str(observation.get("workload", ""))
    deadline_pressure = str(observation.get("deadline_pressure", ""))

    delay = _numeric(delay_hints.get(family), default=99.0)
    queue = _numeric(queue_hints.get(family))
    reward = _numeric(reward_hints.get(family))
    utility = -delay - (0.15 * queue) + (0.01 * reward)

    scenario_bonus = {
        "legal_horizontal_offload": {"horizontal": 1.5},
        "mixed_local_horizontal_cloud_candidates": {"horizontal": 1.0, "vertical": 0.4},
        "cloud_vertical_fallback": {"vertical": 1.5, "horizontal": 0.2},
        "tight_deadline_pressure": {"horizontal": 0.8, "vertical": 0.6},
        "light_load_no_deadline_pressure": {"local": 0.4, "vertical": 0.1},
        "timeout_drop_case": {"horizontal": 0.7, "vertical": 0.5},
        "illegal_horizontal_destination_attempt": {"local": 0.3, "vertical": 0.2},
    }.get(scenario_name, {})
    workload_bonus = {
        "low": {"local": 0.1},
        "medium": {"horizontal": 0.1},
        "high": {"horizontal": 0.2, "vertical": 0.1},
    }.get(workload, {})
    pressure_bonus = {
        "relaxed": {"local": 0.05},
        "moderate": {"horizontal": 0.05},
        "tight": {"vertical": 0.15, "horizontal": 0.1},
    }.get(deadline_pressure, {})

    utility += _numeric(scenario_bonus.get(family))
    utility += _numeric(workload_bonus.get(family))
    utility += _numeric(pressure_bonus.get(family))
    return utility


def _legal_family_actions(context: PolicyContext) -> tuple[str, ...]:
    actions = tuple(action for action, allowed in context.legal_action_mask.items() if allowed)
    if not actions:
        raise ValueError("No legal actions available")
    return actions


def _family_biases(context: PolicyContext, legal_actions: tuple[str, ...]) -> dict[str, float]:
    biases: dict[str, float] = {}
    for action in legal_actions:
        family = action_family(action)
        if family not in {"local", "horizontal", "vertical"}:
            family = action
        biases[action] = _family_score(context, family)
    return biases


def _decision_trace(policy_name: str, legal_actions: tuple[str, ...], biases: dict[str, float], selected_action: str, reason: str) -> tuple[str, ...]:
    ordered = ", ".join(f"{action}={biases.get(action, 0.0):.3f}" for action in legal_actions)
    selected_family = action_family(selected_action)
    return (
        f"policy={policy_name}",
        f"legal_actions={legal_actions}",
        f"family_scores={ordered}",
        f"selected_action={selected_action}",
        f"selected_family={selected_family}",
        f"reason={reason}",
    )


@dataclass(slots=True)
class HoodieProposedPolicyAdapter:
    policy_name: str = "HOODIE_PROPOSED"
    compatibility_mode_used: bool = False
    agent: HoodieAgent = field(default_factory=lambda: HoodieAgent(policy_name="HOODIE_PROPOSED"))
    last_decision_trace: tuple[str, ...] = ()

    def choose_action(self, context: PolicyContext) -> str:
        legal = _legal_family_actions(context)
        biases = _family_biases(context, legal)
        self.agent.model.action_biases = dict(biases)
        action = self.agent.choose_action(context)
        self.last_decision_trace = _decision_trace(
            self.policy_name,
            legal,
            biases,
            action,
            "hybrid latency/queue/deadline scoring across local, horizontal, and vertical candidates",
        )
        return action


@dataclass(slots=True)
class OriginalHoodieBaselineAdapter:
    policy_name: str = "ORIGINAL_HOODIE_BASELINE"
    compatibility_mode_used: bool = False
    policy: AdaptiveOffloadingPolicy = field(default_factory=AdaptiveOffloadingPolicy)
    last_decision_trace: tuple[str, ...] = ()

    def choose_action(self, context: PolicyContext) -> str:
        legal = _legal_family_actions(context)
        delay_candidates = build_delay_candidates(context)
        ranked: list[tuple[float, int, str]] = []
        score_map: dict[str, float] = {}
        for candidate in delay_candidates:
            family_action = candidate.action_id
            if candidate.action_family == "local":
                family_action = "local"
            elif candidate.action_family == "horizontal":
                family_action = "horizontal"
            elif candidate.action_family == "vertical":
                family_action = "vertical"
            if family_action not in legal:
                family_action = next((action for action in placement_actions_for_family(context, candidate.action_family) if action in legal), None) or family_action
            if family_action not in legal:
                continue
            if candidate.total_delay is None:
                continue
            score = -float(candidate.total_delay) - (0.05 * float(candidate.tie_break_key[0]))
            ranked.append((score, int(candidate.tie_break_key[0]), family_action))
            score_map[family_action] = score

        if ranked:
            ranked.sort(key=lambda item: (-item[0], item[1], item[2]))
            action = ranked[0][2]
            reason = "minimum-latency candidate selection with legal family mapping"
            biases = dict(score_map)
        else:
            action = self.policy.choose_action(context)
            biases = _family_biases(context, legal)
            reason = "adaptive offloading fallback with paper-aligned family preference"

        self.last_decision_trace = _decision_trace(
            self.policy_name,
            legal,
            biases,
            action,
            reason,
        )
        return action


@dataclass(slots=True)
class RandomPolicyAdapter:
    seed: int = 0
    policy_name: str = "RANDOM_POLICY"
    compatibility_mode_used: bool = False
    policy: RandomOffloadingPolicy = field(init=False)
    last_decision_trace: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        self.policy = RandomOffloadingPolicy(seed=self.seed)

    def choose_action(self, context: PolicyContext) -> str:
        action = self.policy.choose_action(context)
        legal = _legal_family_actions(context)
        biases = _family_biases(context, legal)
        self.last_decision_trace = _decision_trace(
            self.policy_name,
            legal,
            biases,
            action,
            "seed-controlled adapter using the repository random policy behavior",
        )
        return action


@dataclass(slots=True)
class LocalOnlyPolicyAdapter:
    policy_name: str = "LOCAL_ONLY"
    compatibility_mode_used: bool = False
    last_decision_trace: tuple[str, ...] = ()

    def choose_action(self, context: PolicyContext) -> str:
        self.last_decision_trace = (f"policy={self.policy_name}", "selected_action=local", "reason=direct local-only adapter")
        return "local"


@dataclass(slots=True)
class CloudOnlyPolicyAdapter:
    policy_name: str = "CLOUD_ONLY"
    compatibility_mode_used: bool = False
    last_decision_trace: tuple[str, ...] = ()

    def choose_action(self, context: PolicyContext) -> str:
        self.last_decision_trace = (f"policy={self.policy_name}", "selected_action=vertical", "reason=direct cloud-only adapter")
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
