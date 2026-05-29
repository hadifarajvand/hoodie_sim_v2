from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class FullLocalComputing:
    def select(self, legal_destination_ids: list[str]) -> str:
        return "local"

