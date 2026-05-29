from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class VerticalOffloader:
    def select(self, legal_destination_ids: list[str]) -> str:
        return "cloud" if "cloud" in legal_destination_ids else legal_destination_ids[0]

