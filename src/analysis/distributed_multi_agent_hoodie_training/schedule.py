from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class EpsilonScheduleState:
    epsilon_start: float = 1.0
    epsilon_end: float = 0.05
    decay_steps: int = 1000

    def epsilon(self, step: int, epsilon_start: float | None = None, epsilon_end: float | None = None, decay_steps: int | None = None) -> float:
        start = self.epsilon_start if epsilon_start is None else epsilon_start
        end = self.epsilon_end if epsilon_end is None else epsilon_end
        decay = self.decay_steps if decay_steps is None else decay_steps
        if step >= decay:
            return end
        return start + (end - start) * (step / max(decay, 1))

