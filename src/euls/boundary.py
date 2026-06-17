from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class EULSBoundaryContract:
    owns: tuple[str, ...] = field(
        default_factory=lambda: (
            "task arrival",
            "queue admission",
            "queue mutation",
            "queue service",
            "transmission lifecycle",
            "public queue handoff",
            "deadline/drop handling",
            "completion lifecycle",
            "reward availability event",
            "replay/determinism evidence",
        )
    )
    does_not_own: tuple[str, ...] = field(
        default_factory=lambda: (
            "policy optimization",
            "DRL training",
            "baseline comparison logic",
            "figure plotting",
            "paper result claims",
            "DAL mutation",
        )
    )
    phase_name: str = "Phase 1 - explicit EULS boundary"
    notes: tuple[str, ...] = field(
        default_factory=lambda: (
            "Wrapper-only boundary over existing hoodie runtime.",
            "No queue timing or deadline semantics are changed.",
            "DAL remains out of scope for this phase.",
        )
    )
