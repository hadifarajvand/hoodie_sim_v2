from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Keep one canonical PolicyContext/protocol identity across the environment,
# policy registry, and trainable agents.  Historically this module duplicated
# the dataclass defined in policy_interface.py, causing isinstance checks and
# runtime dispatch to fail even though the two objects had identical fields.
from .policy_interface import PolicyContext, ReplayTrainablePolicy, SharedPolicy


@dataclass(frozen=True, slots=True)
class PolicyDecision:
    action: str
    policy_name: str
    metadata: dict[str, Any] = field(default_factory=dict)


__all__ = [
    "PolicyContext",
    "PolicyDecision",
    "ReplayTrainablePolicy",
    "SharedPolicy",
]
