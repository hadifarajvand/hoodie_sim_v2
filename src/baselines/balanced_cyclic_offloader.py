from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class BalancedCyclicOffloader:
    cursor: int = 0
    history: list[str] = field(default_factory=list)

    def select(self, legal_destination_ids: list[str]) -> str:
        if not legal_destination_ids:
            raise ValueError("no legal destinations")
        choice = legal_destination_ids[self.cursor % len(legal_destination_ids)]
        self.cursor += 1
        self.history.append(choice)
        return choice

