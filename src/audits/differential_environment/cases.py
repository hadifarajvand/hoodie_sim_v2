from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ToyCaseScenario(str, Enum):
    LOCAL_COMPUTE = "local_compute"
    HORIZONTAL_OFFLOAD = "horizontal_offload"
    VERTICAL_OFFLOAD = "vertical_offload"
    TIMEOUT_DROP = "timeout_drop"
    DELAYED_REWARD = "delayed_reward"
    DETERMINISTIC_ORDERING = "deterministic_ordering"


@dataclass(frozen=True, slots=True)
class ToyCase:
    case_id: str
    scenario_type: ToyCaseScenario
    task_id: str
    source_agent_id: str
    destination_target: str
    action: str
    timeout_slot: int
    seed: int
    expected_comparison_context: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "case_id": self.case_id,
            "scenario_type": self.scenario_type.value,
            "task_id": self.task_id,
            "source_agent_id": self.source_agent_id,
            "destination_target": self.destination_target,
            "action": self.action,
            "timeout_slot": self.timeout_slot,
            "seed": self.seed,
            "expected_comparison_context": self.expected_comparison_context,
        }


def build_default_toy_cases() -> tuple[ToyCase, ...]:
    return (
        ToyCase("case-local-compute", ToyCaseScenario.LOCAL_COMPUTE, "task-1", "ea-1", "ea-1", "local", 5, 101),
        ToyCase("case-horizontal-offload", ToyCaseScenario.HORIZONTAL_OFFLOAD, "task-2", "ea-1", "ea-2", "horizontal", 5, 102),
        ToyCase("case-vertical-offload", ToyCaseScenario.VERTICAL_OFFLOAD, "task-3", "ea-1", "cloud", "vertical", 5, 103),
        ToyCase("case-timeout-drop", ToyCaseScenario.TIMEOUT_DROP, "task-4", "ea-1", "ea-1", "local", 1, 104),
        ToyCase("case-delayed-reward", ToyCaseScenario.DELAYED_REWARD, "task-5", "ea-1", "ea-1", "local", 5, 105),
        ToyCase("case-deterministic-ordering", ToyCaseScenario.DETERMINISTIC_ORDERING, "task-6", "ea-1", "ea-1", "local", 5, 106),
    )
