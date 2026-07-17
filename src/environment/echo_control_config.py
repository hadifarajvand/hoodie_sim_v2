from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class EchoControlConfig:
    """Explicit switches for the six manuscript-approved ECHO changes.

    A method label is deliberately not a control switch.  This makes the
    HOODIE/ECHO-disabled differential meaningful and prevents diagnostics from
    silently changing runtime behaviour.
    """

    private_queue_ert: bool = False
    outbound_queue_ert: bool = False
    route_filtering: bool = False
    minimum_lateness_fallback: bool = False
    consistent_action_mask: bool = False
    realized_drop_penalty: bool = False
    fixed_drop_penalty: float = 40.0

    def __post_init__(self) -> None:
        if self.fixed_drop_penalty <= 0:
            raise ValueError("fixed_drop_penalty must be positive")
        if self.minimum_lateness_fallback and not self.route_filtering:
            raise ValueError(
                "minimum-lateness fallback requires route filtering"
            )
        if self.route_filtering and not self.consistent_action_mask:
            raise ValueError(
                "route filtering requires one consistent effective action mask"
            )

    @classmethod
    def disabled(cls) -> "EchoControlConfig":
        return cls()

    @classmethod
    def enabled(cls, *, fixed_drop_penalty: float = 40.0) -> "EchoControlConfig":
        return cls(
            private_queue_ert=True,
            outbound_queue_ert=True,
            route_filtering=True,
            minimum_lateness_fallback=True,
            consistent_action_mask=True,
            realized_drop_penalty=True,
            fixed_drop_penalty=fixed_drop_penalty,
        )

    @property
    def any_enabled(self) -> bool:
        return any(
            (
                self.private_queue_ert,
                self.outbound_queue_ert,
                self.route_filtering,
                self.minimum_lateness_fallback,
                self.consistent_action_mask,
                self.realized_drop_penalty,
            )
        )

    @property
    def fully_enabled(self) -> bool:
        return all(
            (
                self.private_queue_ert,
                self.outbound_queue_ert,
                self.route_filtering,
                self.minimum_lateness_fallback,
                self.consistent_action_mask,
                self.realized_drop_penalty,
            )
        )

    def to_dict(self) -> dict[str, bool | float]:
        return asdict(self)
