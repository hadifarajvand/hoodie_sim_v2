from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Iterable

from .policy_interface import PolicyContext

LOCAL_ACTIONS = ("local", "compute_local")
HORIZONTAL_ACTIONS = ("horizontal", "offload_horizontal")
VERTICAL_ACTIONS = ("vertical", "offload_vertical")
FAMILY_ACTIONS = {
    "local": LOCAL_ACTIONS,
    "horizontal": HORIZONTAL_ACTIONS,
    "vertical": VERTICAL_ACTIONS,
}
FALLBACK_FAMILY_ORDER = ("local", "horizontal", "vertical")
FALLBACK_ACTION_ORDER = LOCAL_ACTIONS + HORIZONTAL_ACTIONS + VERTICAL_ACTIONS

def action_family(action: str) -> str:
    for family, actions in FAMILY_ACTIONS.items():
        if action in actions:
            return family
    if action == "cloud":
        return "vertical"
    if action.isdigit() or action.startswith("horizontal_"):
        return "horizontal"
    return action

def legal_actions(context: PolicyContext) -> tuple[str, ...]:
    return tuple(action for action, allowed in context.legal_action_mask.items() if allowed)

def first_legal_action(context: PolicyContext, preferred: Iterable[str] = FALLBACK_ACTION_ORDER) -> str:
    legal = legal_actions(context)
    legal_set = set(legal)
    for action in preferred:
        if action in legal_set:
            return action
    if not legal:
        raise ValueError("No legal actions available")
    return legal[0]

def first_legal_family_action(context: PolicyContext, family: str) -> str | None:
    return first_legal_from_actions(context, FAMILY_ACTIONS.get(family, (family,)))

def first_legal_from_actions(context: PolicyContext, preferred: Iterable[str]) -> str | None:
    legal_set = set(legal_actions(context))
    for action in preferred:
        if action in legal_set:
            return action
    return None

def fallback_action(context: PolicyContext) -> str:
    return first_legal_action(context, FALLBACK_ACTION_ORDER)

def legal_family_available(context: PolicyContext, family: str) -> bool:
    return first_legal_family_action(context, family) is not None

def observation_mapping(context: PolicyContext) -> Mapping[str, object]:
    if isinstance(context.observation, Mapping):
        return context.observation
    return {}

def placement_actions_for_family(context: PolicyContext, family: str) -> tuple[str, ...]:
    observation = observation_mapping(context)
    legal_set = set(legal_actions(context))
    candidates: list[str] = []
    candidates.extend(_placement_candidates_from_observation(observation, family))
    placement_actions = observation.get("placement_actions")
    if isinstance(placement_actions, Mapping):
        candidates.extend(_placement_candidates_from_value(placement_actions.get(family)))
        if family == "vertical":
            candidates.extend(_placement_candidates_from_value(placement_actions.get("cloud")))
        if family == "local":
            candidates.extend(_placement_candidates_from_value(placement_actions.get("local")))
        if family == "horizontal":
            candidates.extend(_placement_candidates_from_value(placement_actions.get("horizontal")))
    if not candidates:
        candidates.extend(FAMILY_ACTIONS.get(family, (family,)))
    source_agent_id = _string_or_none(observation.get("source_agent_id"))
    unique: list[str] = []
    for candidate in candidates:
        if candidate not in legal_set:
            continue
        if family == "horizontal" and source_agent_id is not None and candidate == source_agent_id:
            continue
        if family == "horizontal" and candidate in {"local", "cloud"}:
            continue
        if candidate not in unique:
            unique.append(candidate)
    if unique:
        return tuple(unique)
    fallback = first_legal_family_action(context, family)
    if fallback is not None:
        return (fallback,)
    return ()

def first_legal_placement_action(context: PolicyContext, family: str) -> str | None:
    candidates = placement_actions_for_family(context, family)
    if candidates:
        return candidates[0]
    return None

def legal_placement_available(context: PolicyContext, family: str) -> bool:
    return first_legal_placement_action(context, family) is not None

def placement_contract_available(context: PolicyContext) -> bool:
    observation = observation_mapping(context)
    return any(key in observation for key in ("local_action", "cloud_action", "horizontal_destinations", "placement_actions"))

def _placement_candidates_from_observation(observation: Mapping[str, object], family: str) -> tuple[str, ...]:
    if family == "local":
        candidates = _placement_candidates_from_value(observation.get("local_action"))
    elif family == "vertical":
        candidates = _placement_candidates_from_value(observation.get("cloud_action"))
    elif family == "horizontal":
        candidates = _placement_candidates_from_value(observation.get("horizontal_destinations"))
        if not candidates:
            candidates = _placement_candidates_from_value(observation.get("edge_agent_ids"))
    else:
        candidates = ()
    return candidates

def _placement_candidates_from_value(value: object) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,)
    if isinstance(value, int):
        return (str(value),)
    if isinstance(value, Mapping):
        for key in ("action_id", "action", "destination_id", "destination", "placement", "name"):
            candidate = value.get(key)
            if isinstance(candidate, str) and candidate:
                return (candidate,)
            if isinstance(candidate, int):
                return (str(candidate),)
        candidates: list[str] = []
        for item in value.values():
            candidates.extend(_placement_candidates_from_value(item))
        return tuple(candidates)
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        candidates: list[str] = []
        for item in value:
            candidates.extend(_placement_candidates_from_value(item))
        return tuple(candidates)
    return ()

def _string_or_none(value: object) -> str | None:
    if isinstance(value, str) and value:
        return value
    if isinstance(value, int):
        return str(value)
    return None
