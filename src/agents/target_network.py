from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class TargetNetwork:
    parameters: dict[str, float] = field(default_factory=dict)

    def copy_from(self, source_parameters: dict[str, float]) -> None:
        self.parameters = dict(source_parameters)

    def soft_update(self, source_parameters: dict[str, float], tau: float) -> None:
        if not self.parameters:
            self.copy_from(source_parameters)
            return
        for key, value in source_parameters.items():
            current = self.parameters.get(key, value)
            self.parameters[key] = (1 - tau) * current + tau * value
