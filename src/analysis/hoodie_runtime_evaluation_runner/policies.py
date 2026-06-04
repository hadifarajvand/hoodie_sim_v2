from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Protocol

from src.agents.hoodie_agent import HoodieAgent
from src.policies.bco import BalancedCooperationOffloadingPolicy
from src.policies.common import action_family, placement_actions_for_family
from src.policies.flc import FullLocalComputingPolicy
from src.policies.ho import HorizontalOffloadingPolicy
from src.policies.mleo import MinimumLatencyEstimateOffloadingPolicy
from src.policies.policy_interface import PolicyContext
from src.policies.ro import RandomOffloadingPolicy
from src.policies.vo import VerticalOffloadingPolicy


class RuntimePolicyAdapter(Protocol):
    policy_name: str
    compatibility_mode_used: bool
    last_decision_trace: tuple[str, ...]

    def choose_action(self, context: PolicyContext) -> str:
        ...


def _legal_action_tuple(context: PolicyContext) -> tuple[str, ...]:
    actions = tuple(action for action, allowed in context.legal_action_mask.items() if allowed)
    if not actions:
        raise ValueError("No legal actions available")
    return actions


def _decision_trace(policy_name: str, *, legal_actions: tuple[str, ...], selected_action: str, reason: str, details: dict[str, object]) -> tuple[str, ...]:
    lines = [f"policy={policy_name}", f"legal_actions={legal_actions}", f"selected_action={selected_action}", f"selected_family={action_family(selected_action)}", f"reason={reason}"]
    for key in sorted(details):
        lines.append(f"{key}={details[key]}")
    return tuple(lines)


def _trace_summary(trace: tuple[str, ...]) -> str:
    return " | ".join(trace)


def _queue_hint_for_action(context: PolicyContext, action: str) -> float:
    observation = context.observation if isinstance(context.observation, dict) else {}
    queue_hints = observation.get("queue_hints", {})
    if isinstance(queue_hints, dict):
        value = queue_hints.get(action)
        if isinstance(value, (int, float)):
            return float(value)
        family = action_family(action)
        value = queue_hints.get(family)
        if isinstance(value, (int, float)):
            return float(value)
    queue_history = observation.get("queue_history")
    if isinstance(queue_history, tuple) and queue_history:
        if action_family(action) == "local":
            index = 0
        elif action_family(action) == "horizontal":
            index = 1 if len(queue_history) > 1 else 0
        else:
            index = 2 if len(queue_history) > 2 else len(queue_history) - 1
        return float(queue_history[max(0, index)])
    queue_load = observation.get("queue_load")
    if isinstance(queue_load, (int, float)):
        return float(queue_load)
    return 0.0


def _family_queue_snapshot(context: PolicyContext, legal: tuple[str, ...]) -> dict[str, float]:
    snapshot: dict[str, float] = {}
    for action in legal:
        family = action_family(action)
        if family not in snapshot:
            snapshot[family] = _queue_hint_for_action(context, action)
    return snapshot


@dataclass(slots=True)
class HoodiePolicyAdapter:
    policy_name: str = "HOODIE"
    compatibility_mode_used: bool = False
    agent: HoodieAgent = field(default_factory=lambda: HoodieAgent(policy_name="HOODIE"))
    last_decision_trace: tuple[str, ...] = ()

    def choose_action(self, context: PolicyContext) -> str:
        legal = _legal_action_tuple(context)
        history = self.agent.history_builder.build(context)
        features = {
            "state_value": float(len(history.observations) + len(history.trace_history)),
        }
        base_q_values = self.agent.model.dueling_dqn.q_values(features, legal)
        adjusted_q_values = self.agent.model.forward(history, legal)
        selected_action = self.agent.selector.select_action(adjusted_q_values, legal)
        self.agent.history_builder.record(context)
        state_value = self.agent.model.dueling_dqn.value_weight * features["state_value"]
        raw_advantages = {action: self.agent.model.dueling_dqn.advantage_weights.get(action, 0.0) for action in legal}
        mean_advantage = sum(raw_advantages.values()) / len(raw_advantages) if raw_advantages else 0.0
        self.last_decision_trace = _decision_trace(
            self.policy_name,
            legal_actions=legal,
            selected_action=selected_action,
            reason="Feature 080 proposed-method runtime path using value/advantage aggregation and learned bias adjustments",
            details={
                "state_value": state_value,
                "raw_advantages": raw_advantages,
                "mean_advantage": mean_advantage,
                "base_q_values": base_q_values,
                "adjusted_q_values": adjusted_q_values,
            },
        )
        return selected_action


@dataclass(slots=True)
class RandomOffloaderAdapter:
    seed: int = 0
    policy_name: str = "RO"
    compatibility_mode_used: bool = False
    policy: RandomOffloadingPolicy = field(init=False)
    last_decision_trace: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        self.policy = RandomOffloadingPolicy(seed=self.seed)

    def choose_action(self, context: PolicyContext) -> str:
        legal = _legal_action_tuple(context)
        action = self.policy.choose_action(context)
        family_snapshot = _family_queue_snapshot(context, legal)
        self.last_decision_trace = _decision_trace(
            self.policy_name,
            legal_actions=legal,
            selected_action=action,
            reason="seed-controlled random offloader choosing a legal family and destination uniformly",
            details={"seed": self.seed, "queue_snapshot": family_snapshot},
        )
        return action


@dataclass(slots=True)
class FullLocalComputingAdapter:
    policy_name: str = "FLC"
    compatibility_mode_used: bool = False
    policy: FullLocalComputingPolicy = field(default_factory=FullLocalComputingPolicy)
    last_decision_trace: tuple[str, ...] = ()

    def choose_action(self, context: PolicyContext) -> str:
        legal = _legal_action_tuple(context)
        action = self.policy.choose_action(context)
        self.last_decision_trace = _decision_trace(
            self.policy_name,
            legal_actions=legal,
            selected_action=action,
            reason="full local computing always chooses the local family when legal",
            details={"local_available": "local" in legal or "compute_local" in legal},
        )
        return action


@dataclass(slots=True)
class VerticalOffloadingAdapter:
    policy_name: str = "VO"
    compatibility_mode_used: bool = False
    policy: VerticalOffloadingPolicy = field(default_factory=VerticalOffloadingPolicy)
    last_decision_trace: tuple[str, ...] = ()

    def choose_action(self, context: PolicyContext) -> str:
        legal = _legal_action_tuple(context)
        action = self.policy.choose_action(context)
        self.last_decision_trace = _decision_trace(
            self.policy_name,
            legal_actions=legal,
            selected_action=action,
            reason="vertical offloading always chooses the cloud family when legal",
            details={"cloud_available": "vertical" in legal or "offload_vertical" in legal},
        )
        return action


@dataclass(slots=True)
class HorizontalOffloadingAdapter:
    policy_name: str = "HO"
    compatibility_mode_used: bool = False
    policy: HorizontalOffloadingPolicy = field(default_factory=HorizontalOffloadingPolicy)
    last_decision_trace: tuple[str, ...] = ()

    def choose_action(self, context: PolicyContext) -> str:
        legal = _legal_action_tuple(context)
        action = self.policy.choose_action(context)
        self.last_decision_trace = _decision_trace(
            self.policy_name,
            legal_actions=legal,
            selected_action=action,
            reason="horizontal offloading always chooses a legal horizontal destination when one exists",
            details={"horizontal_destinations": tuple(placement_actions_for_family(context, "horizontal"))},
        )
        return action


@dataclass(slots=True)
class BalancedCyclicOffloaderAdapter:
    policy_name: str = "BCO"
    compatibility_mode_used: bool = False
    policy: BalancedCooperationOffloadingPolicy = field(default_factory=BalancedCooperationOffloadingPolicy)
    last_decision_trace: tuple[str, ...] = ()

    def choose_action(self, context: PolicyContext) -> str:
        legal = _legal_action_tuple(context)
        action = self.policy.choose_action(context)
        self.last_decision_trace = _decision_trace(
            self.policy_name,
            legal_actions=legal,
            selected_action=action,
            reason="balanced cyclic offloader rotates through local, vertical, and horizontal actions",
            details={"next_family_index": self.policy._next_family_index, "next_placement_index": self.policy._next_placement_index},
        )
        return action


@dataclass(slots=True)
class MinimumLatencyEstimateOffloaderAdapter:
    policy_name: str = "MLEO"
    compatibility_mode_used: bool = False
    policy: MinimumLatencyEstimateOffloadingPolicy = field(default_factory=MinimumLatencyEstimateOffloadingPolicy)
    last_decision_trace: tuple[str, ...] = ()

    def choose_action(self, context: PolicyContext) -> str:
        legal = _legal_action_tuple(context)
        selected_action = self.policy.choose_action(context)
        self.last_decision_trace = _decision_trace(
            self.policy_name,
            legal_actions=legal,
            selected_action=selected_action,
            reason="minimum latency estimate offloader chooses the legal candidate with the smallest estimated total delay",
            details={
                "candidate_count": len(self.policy.last_candidates),
                "candidates": tuple(asdict(candidate) for candidate in self.policy.last_candidates),
                "fallback_reason": self.policy.last_fallback_reason,
            },
        )
        return selected_action


def build_policy_adapter(policy_name: str, seed: int = 0) -> RuntimePolicyAdapter:
    normalized = policy_name.strip().upper()
    if normalized in {"HOODIE", "HOODIE_PROPOSED"}:
        return HoodiePolicyAdapter()
    if normalized == "RO" or normalized == "RANDOM_POLICY":
        return RandomOffloaderAdapter(seed=seed)
    if normalized == "FLC" or normalized == "LOCAL_ONLY":
        return FullLocalComputingAdapter()
    if normalized == "VO" or normalized == "CLOUD_ONLY":
        return VerticalOffloadingAdapter()
    if normalized == "HO":
        return HorizontalOffloadingAdapter()
    if normalized == "BCO":
        return BalancedCyclicOffloaderAdapter()
    if normalized == "MLEO":
        return MinimumLatencyEstimateOffloaderAdapter()
    if normalized == "ORIGINAL_HOODIE_BASELINE":
        raise ValueError("ORIGINAL_HOODIE_BASELINE is not an active Feature 085 policy")
    raise ValueError(f"Unsupported runtime evaluation policy: {policy_name!r}")
