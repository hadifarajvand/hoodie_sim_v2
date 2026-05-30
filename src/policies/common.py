from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Iterable, Any

from .policy_interface import PolicyContext


def legal_actions(context: PolicyContext) -> tuple[str, ...]:
    return tuple(action for action, allowed in context.legal_action_mask.items() if allowed)


def first_legal_action(context: PolicyContext, preferred: Iterable[str]) -> str:
    legal = legal_actions(context)
    legal_set = set(legal)
    for action in preferred:
        if action in legal_set:
            return action
    if not legal:
        raise ValueError("No legal actions available")
    return legal[0]


def _observation_mapping(context: PolicyContext) -> Mapping[str, Any]:
    observation = context.observation
    return observation if isinstance(observation, Mapping) else {}


def _as_action_sequence(value: object) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,)
    if isinstance(value, Sequence):
        return tuple(str(item) for item in value if item is not None)
    return ()


def _canonical_placement_action(action: str) -> str:
    canonical = {
        "compute_local": "local",
        "offload_vertical": "cloud",
        "vertical": "cloud",
        "offload_horizontal": "horizontal",
    }
    return canonical.get(action, action)


def source_agent_id(context: PolicyContext) -> str | None:
    observation = _observation_mapping(context)
    source = observation.get("source_agent_id")
    if source is None:
        return None
    return str(source)


def placement_action(context: PolicyContext, family: str) -> str | None:
    observation = _observation_mapping(context)
    key_map = {
        "local": ("local_action", "local_action_id"),
        "vertical": ("cloud_action", "vertical_action"),
    }
    for key in key_map.get(family, ()):
        action = observation.get(key)
        if isinstance(action, str) and action:
            return action
    return None


def horizontal_destinations(context: PolicyContext) -> tuple[str, ...]:
    observation = _observation_mapping(context)
    return _as_action_sequence(observation.get("horizontal_destinations"))


def placement_candidates(context: PolicyContext) -> dict[str, tuple[str, ...]]:
    observation = _observation_mapping(context)
    candidates: dict[str, tuple[str, ...]] = {
        "local": (),
        "vertical": (),
        "horizontal": (),
    }

    local_action = observation.get("local_action")
    if isinstance(local_action, str) and local_action:
        candidates["local"] = (local_action,)

    cloud_action = observation.get("cloud_action")
    if isinstance(cloud_action, str) and cloud_action:
        candidates["vertical"] = (cloud_action,)

    placement_actions = observation.get("placement_actions")
    if isinstance(placement_actions, Mapping):
        for family in candidates:
            family_actions = placement_actions.get(family)
            candidates[family] = _as_action_sequence(family_actions)
    elif isinstance(placement_actions, Sequence):
        normalized = tuple(str(action) for action in placement_actions if action is not None)
        for action in normalized:
            family = _family_for_action(action)
            candidates[family] = candidates[family] + (action,)

    horizontal = observation.get("horizontal_destinations")
    if isinstance(horizontal, Sequence) and not isinstance(horizontal, str):
        candidates["horizontal"] = tuple(str(destination) for destination in horizontal if destination is not None)
    elif isinstance(horizontal, Mapping):
        candidates["horizontal"] = tuple(str(key) for key, allowed in horizontal.items() if allowed)

    return candidates


def _family_for_action(action: str) -> str:
    action = _canonical_placement_action(action)
    if action == "local":
        return "local"
    if action == "cloud":
        return "vertical"
    return "horizontal"


def fallback_reason(context: PolicyContext, family: str, *, detail: str) -> str:
    observation = _observation_mapping(context)
    fallback_hints = observation.get("fallback_hints")
    hint = None
    if isinstance(fallback_hints, Mapping):
        hint = fallback_hints.get(family)
    if hint is None:
        return detail
    return f"{detail}; hint={hint}"


def ordered_available_candidates(candidates: Sequence[str], legal_mask: Mapping[str, bool]) -> tuple[str, ...]:
    return tuple(action for action in candidates if legal_mask.get(action, False))


def deterministic_choice(candidates: Sequence[str], seed: int | None = None) -> str:
    if not candidates:
        raise ValueError("No candidates available")
    if seed is None:
        return candidates[0]
    import random

    rng = random.Random(seed)
    return rng.choice(list(candidates))
