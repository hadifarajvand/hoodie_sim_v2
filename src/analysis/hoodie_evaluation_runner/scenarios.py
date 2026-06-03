from __future__ import annotations

from dataclasses import dataclass
from random import Random

from .config import DEADLINE_PRESSURE_LEVELS, EvaluationConfig, WORKLOAD_LEVELS, TOPOLOGY_MODE_PAPER_FIGURE_7, RUNTIME_MODE_PAPER
from .model import ScenarioContext, TaskBlueprint


_WORKLOAD_TASKS = {"low": 2, "medium": 4, "high": 6}
_WORKLOAD_DURATION = {"low": 6, "medium": 8, "high": 10}
_WORKLOAD_DEADLINE_SHIFT = {"relaxed": 2, "moderate": 0, "tight": -1}
_DEADLINE_OFFSET = {"relaxed": 2, "moderate": 0, "tight": -1}


@dataclass(frozen=True, slots=True)
class ScenarioBlueprint:
    name: str
    local_completion_base: int
    horizontal_completion_base: int
    vertical_completion_base: int
    cloud_available: bool
    horizontal_destinations: tuple[str, ...]
    illegal_horizontal_destinations: tuple[str, ...]
    network_condition: str
    local_available: bool = True
    horizontal_available: bool = True
    vertical_available: bool = True


_SCENARIOS: dict[str, ScenarioBlueprint] = {
    "light_load_no_deadline_pressure": ScenarioBlueprint("light_load_no_deadline_pressure", 2, 3, 2, True, ("6",), ("2",), "clear"),
    "tight_deadline_pressure": ScenarioBlueprint("tight_deadline_pressure", 3, 4, 3, True, ("6",), ("2",), "congested"),
    "legal_horizontal_offload": ScenarioBlueprint("legal_horizontal_offload", 3, 2, 2, True, ("6",), ("2",), "horizontal_ready"),
    "illegal_horizontal_destination_attempt": ScenarioBlueprint("illegal_horizontal_destination_attempt", 2, 3, 2, True, ("6",), ("2",), "invalid_horizontal"),
    "cloud_vertical_fallback": ScenarioBlueprint("cloud_vertical_fallback", 3, 4, 2, True, ("6",), ("2",), "cloud_fallback"),
    "timeout_drop_case": ScenarioBlueprint("timeout_drop_case", 5, 5, 5, True, ("6",), ("2",), "deadline_loss"),
    "mixed_local_horizontal_cloud_candidates": ScenarioBlueprint("mixed_local_horizontal_cloud_candidates", 2, 3, 2, True, ("6",), ("2",), "mixed"),
}


def _task_deadline(base_duration: int, deadline_pressure: str, arrival_slot: int, workload: str) -> int:
    pressure_offset = _DEADLINE_OFFSET[deadline_pressure]
    workload_offset = _WORKLOAD_DEADLINE_SHIFT[deadline_pressure]
    return arrival_slot + max(2, base_duration // 2 + pressure_offset + workload_offset)


def _scenario_duration(workload: str) -> int:
    return _WORKLOAD_DURATION[workload]


def _queue_snapshot(index: int, workload: str, family_bias: int) -> tuple[int, ...]:
    base = {"low": 1, "medium": 2, "high": 3}[workload]
    return tuple(max(0, base + family_bias + offset) for offset in (0, 1, 2))


def _task_count(workload: str) -> int:
    return _WORKLOAD_TASKS[workload]


def _completion_time(blueprint: ScenarioBlueprint, action_family: str, workload: str, deadline_pressure: str, index: int) -> int:
    base = {
        "local": blueprint.local_completion_base,
        "horizontal": blueprint.horizontal_completion_base,
        "vertical": blueprint.vertical_completion_base,
    }[action_family]
    workload_adjustment = {"low": 0, "medium": 1, "high": 2}[workload]
    pressure_adjustment = {"relaxed": -1, "moderate": 0, "tight": 1}[deadline_pressure]
    return 1 + index + base + workload_adjustment + pressure_adjustment


def build_scenario_contexts(config: EvaluationConfig) -> tuple[ScenarioContext, ...]:
    contexts: list[ScenarioContext] = []
    for seed in config.seeds:
        rng = Random(seed)
        for workload in config.workloads:
            for deadline_pressure in config.deadline_pressures:
                for scenario_name in config.scenarios:
                    blueprint = _SCENARIOS[scenario_name]
                    task_count = _task_count(workload)
                    duration = _scenario_duration(workload)
                    tasks: list[TaskBlueprint] = []
                    deadlines: list[int] = []
                    for index in range(task_count):
                        arrival = index
                        absolute_deadline = _task_deadline(duration, deadline_pressure, arrival, workload)
                        family_bias = 0 if scenario_name != "timeout_drop_case" else 2
                        queue_snapshot = _queue_snapshot(index, workload, family_bias)
                        local_completion = _completion_time(blueprint, "local", workload, deadline_pressure, index)
                        horizontal_completion = _completion_time(blueprint, "horizontal", workload, deadline_pressure, index)
                        vertical_completion = _completion_time(blueprint, "vertical", workload, deadline_pressure, index)
                        source_agent_id = str((index % 3) + 1)
                        tasks.append(
                            TaskBlueprint(
                                task_id=f"{scenario_name}-{seed}-{index}",
                                arrival_time=arrival,
                                source_agent_id=source_agent_id,
                                local_completion_time=local_completion,
                                horizontal_completion_time=horizontal_completion,
                                vertical_completion_time=vertical_completion,
                                absolute_deadline_time=absolute_deadline,
                                scenario_duration=duration,
                                legal_horizontal_destinations=blueprint.horizontal_destinations,
                                illegal_horizontal_destinations=blueprint.illegal_horizontal_destinations,
                                cloud_available=blueprint.cloud_available,
                                local_available=blueprint.local_available,
                                horizontal_available=blueprint.horizontal_available,
                                vertical_available=blueprint.vertical_available,
                                queue_length_snapshot=queue_snapshot,
                            )
                        )
                        deadlines.append(absolute_deadline)
                    contexts.append(
                        ScenarioContext(
                            scenario_name=scenario_name,
                            workload=workload,
                            deadline_pressure=deadline_pressure,
                            seed=seed,
                            vehicle_count=3,
                            task_type_count=3,
                            task_count=task_count,
                            scenario_duration=duration,
                            local_available=blueprint.local_available,
                            horizontal_destinations=blueprint.horizontal_destinations,
                            illegal_horizontal_destinations=blueprint.illegal_horizontal_destinations,
                            cloud_available=blueprint.cloud_available,
                            deadline_slots=tuple(deadlines),
                            network_condition=blueprint.network_condition,
                            queue_initial_state=(0, 0, 0),
                            tasks=tuple(tasks),
                            topology_mode=TOPOLOGY_MODE_PAPER_FIGURE_7,
                            runtime_mode=RUNTIME_MODE_PAPER,
                        )
                    )
    return tuple(contexts)
