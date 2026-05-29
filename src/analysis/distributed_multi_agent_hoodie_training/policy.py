from __future__ import annotations

from dataclasses import dataclass

from .schedule import EpsilonScheduleState


@dataclass(slots=True)
class DistributedEpsilonGreedyPolicy:
    epsilon_start: float = 1.0
    epsilon_end: float = 0.05
    decay_steps: int = 1000

    def choose(self, *, legal_action_mask: list[bool], step: int, rng_seed: int, epsilon_state: EpsilonScheduleState) -> int:
        legal = [index for index, allowed in enumerate(legal_action_mask) if allowed]
        if not legal:
            raise ValueError("no legal actions available")
        epsilon = epsilon_state.epsilon(step, self.epsilon_start, self.epsilon_end, self.decay_steps)
        if (rng_seed + step) % 1000 / 1000.0 < epsilon:
            return legal[(rng_seed + step) % len(legal)]
        return legal[0]

