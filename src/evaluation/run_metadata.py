from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass(slots=True)
class RunMetadata:
    policy_name: str
    trace_id: str
    seed: int
    device: str
    trace_mode: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
