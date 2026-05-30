from __future__ import annotations

import random
from dataclasses import dataclass, field

from .common import horizontal_destinations, legal_actions, source_agent_id
from .policy_interface import PolicyContext, SharedPolicy


@dataclass(slots=True)
class RandomOffloadingPolicy(SharedPolicy):
    seed: int | None = None
    rng: random.Random = field(default_factory=random.Random)

    def __post_init__(self) -> None:
        if self.seed is not None:
            self.rng = random.Random(self.seed)

    def choose_action(self, context: PolicyContext) -> str:
        legal = legal_actions(context)
        if not legal:
            raise ValueError("No legal actions available")
        families = []
        if context.legal_action_mask.get("local", False) or context.legal_action_mask.get("compute_local", False):
            families.append("local")
        if context.legal_action_mask.get("horizontal", False) or context.legal_action_mask.get("offload_horizontal", False) or horizontal_destinations(context):
            families.append("horizontal")
        if context.legal_action_mask.get("vertical", False) or context.legal_action_mask.get("offload_vertical", False) or context.legal_action_mask.get("cloud", False):
            families.append("vertical")
        if not families:
            return self.rng.choice(legal)
        chosen_family = self.rng.choice(families)
        if chosen_family == "horizontal":
            source = source_agent_id(context)
            destinations = tuple(destination for destination in horizontal_destinations(context) if destination != source and context.legal_action_mask.get(destination, False))
            if destinations:
                return self.rng.choice(list(destinations))
        if chosen_family == "local":
            for action in ("local", "compute_local"):
                if context.legal_action_mask.get(action, False):
                    return action
        if chosen_family == "vertical":
            for action in ("cloud", "vertical", "offload_vertical"):
                if context.legal_action_mask.get(action, False):
                    return action
        return self.rng.choice(legal)
