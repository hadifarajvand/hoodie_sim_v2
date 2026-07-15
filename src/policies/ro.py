from __future__ import annotations

import random
from dataclasses import dataclass, field

from .common import placement_actions_for_family
from .policy_interface import PolicyContext, SharedPolicy


@dataclass(slots=True)
class RandomOffloadingPolicy(SharedPolicy):
    seed: int | None = None
    rng: random.Random = field(default_factory=random.Random)

    def __post_init__(self) -> None:
        if self.seed is not None:
            self.rng = random.Random(self.seed)

    def choose_action(self, context: PolicyContext) -> str:
        available_families = [family for family in ("local", "horizontal", "vertical") if placement_actions_for_family(context, family)]
        if not available_families:
            raise ValueError("No legal actions available")
        chosen_family = self.rng.choice(tuple(available_families))
        actions = placement_actions_for_family(context, chosen_family)
        return self.rng.choice(tuple(actions))
