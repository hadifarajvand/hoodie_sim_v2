from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json


@dataclass(frozen=True, slots=True)
class Topology:
    node_ids: tuple[str, ...]
    legal_actions: dict[str, tuple[str, ...]]

    @classmethod
    def load(cls, path: str | Path) -> "Topology":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(
            node_ids=tuple(payload["node_ids"]),
            legal_actions={key: tuple(value) for key, value in payload["legal_actions"].items()},
        )

    def legal_action_map(self) -> dict[str, tuple[str, ...]]:
        return dict(self.legal_actions)
