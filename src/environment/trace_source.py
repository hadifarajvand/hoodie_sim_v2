from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json


@dataclass(slots=True)
class TraceSource:
    mode: str
    identifier: str
    root_path: Path | None = None

    def metadata(self) -> dict[str, str]:
        return {"mode": self.mode, "identifier": self.identifier}

    @classmethod
    def from_trace_bank(cls, identifier: str, root_path: Path | None = None) -> "TraceSource":
        return cls(mode="trace_bank", identifier=identifier, root_path=root_path)

    @classmethod
    def from_seed(cls, identifier: str, root_path: Path | None = None) -> "TraceSource":
        return cls(mode="deterministic_seed", identifier=identifier, root_path=root_path)

    def load(self) -> dict:
        if self.root_path is None:
            return {"mode": self.mode, "identifier": self.identifier}
        path = self.root_path / f"{self.identifier}.json"
        return json.loads(path.read_text(encoding="utf-8"))

