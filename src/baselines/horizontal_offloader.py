from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class HorizontalOffloader:
    def select(self, legal_destination_ids: list[str]) -> str:
        for destination in legal_destination_ids:
            if destination not in {"local", "cloud"}:
                return destination
        return "local"

