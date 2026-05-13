from __future__ import annotations

from dataclasses import dataclass

from src.evaluation.policy_registry import PolicyRegistry

BASELINE_POLICY_NAMES: tuple[str, ...] = ("FLC", "VO", "HO", "RO", "BCO", "MLEO", "ADAPTIVE")
BASELINE_SCENARIO_NAMES: tuple[str, ...] = ("paper_default",)
BASELINE_SEEDS: tuple[int, ...] = (0, 1, 2)


@dataclass(slots=True)
class BaselineRegistryStatus:
    supported_names: tuple[str, ...]
    missing_names: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not self.missing_names

    def to_dict(self) -> dict[str, object]:
        return {
            "supported_names": list(self.supported_names),
            "missing_names": list(self.missing_names),
            "passed": self.passed,
        }


def supported_baseline_policies() -> tuple[str, ...]:
    return PolicyRegistry.supported_names()


def assert_baselines_registered() -> BaselineRegistryStatus:
    supported = supported_baseline_policies()
    missing = tuple(name for name in BASELINE_POLICY_NAMES if name not in supported)
    if missing:
        raise ValueError(f"Missing required baseline policies: {missing}")
    return BaselineRegistryStatus(supported_names=supported, missing_names=())
