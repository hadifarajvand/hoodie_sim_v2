from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .formulas import paper_action_vector


@dataclass(frozen=True, slots=True)
class HybridActionDecision:
    primary_decision: int
    destination_kind: str
    destination_id: str | None = None

    def __post_init__(self) -> None:
        paper_action_vector(self.primary_decision, self.destination_kind)
        if self.destination_kind != "local" and not isinstance(self.destination_id, str):
            raise ValueError("offloading actions require a destination_id")
        if self.destination_kind == "local" and self.destination_id not in {None, "", "self"}:
            raise ValueError("local actions must not target a remote destination")

    @property
    def is_local(self) -> bool:
        return bool(self.primary_decision)

    @property
    def is_offloading(self) -> bool:
        return not self.is_local

    def to_vector(self) -> tuple[int, str]:
        return paper_action_vector(self.primary_decision, self.destination_kind)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["vector"] = list(self.to_vector())
        return payload
