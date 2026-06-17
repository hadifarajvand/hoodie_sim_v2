from __future__ import annotations

from typing import Any


class EULSKernel:
    """Explicit EULS boundary for deterministic execution.

    Phase 1 is a non-semantic wrapper around HoodieGymEnvironment.
    """

    def __init__(self, environment: Any) -> None:
        self.environment = environment

    def reset(self, seed: int | None = None):
        return self.environment.reset(seed=seed)

    def observe(self):
        return self.environment.observe()

    def observe_flat(self, task=None):
        return self.environment.observe_flat(task=task)

    def legal_action_mask(self, task=None):
        return self.environment.legal_action_mask(task=task)

    def step(self, action: str | None):
        return self.environment.step(action)

    @property
    def current_task(self):
        return self.environment.current_task

    @property
    def current_slot(self):
        return self.environment.current_slot

    @property
    def queue_load(self):
        return self.environment.queue_load
