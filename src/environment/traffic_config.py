from __future__ import annotations

from dataclasses import dataclass


_SCENARIOS = {"paper_default", "moderate", "heavy", "extreme"}


def _build_size_values(size_min: float, size_max: float, size_step: float) -> tuple[float, ...]:
    values: list[float] = []
    current = size_min
    while current <= size_max + (size_step / 10.0):
        values.append(round(current, 10))
        current = round(current + size_step, 10)
    return tuple(values)


@dataclass(slots=True)
class TrafficConfig:
    scenario_name: str
    number_of_agents: int
    episode_length: int
    arrival_probability: float
    slot_duration_seconds: float
    timeout_slots: int
    task_size_mbits_min: float
    task_size_mbits_max: float
    task_size_mbits_step: float
    processing_density_gcycles_per_mbit: float

    def __post_init__(self) -> None:
        if self.scenario_name not in _SCENARIOS:
            raise ValueError(f"Unsupported traffic scenario: {self.scenario_name}")
        if self.number_of_agents <= 0:
            raise ValueError("number_of_agents must be greater than zero")
        if self.episode_length <= 0:
            raise ValueError("episode_length must be greater than zero")
        if not 0.0 <= self.arrival_probability <= 1.0:
            raise ValueError("arrival_probability must be between 0 and 1")
        if self.slot_duration_seconds <= 0:
            raise ValueError("slot_duration_seconds must be greater than zero")
        if self.timeout_slots < 0:
            raise ValueError("timeout_slots must be greater than or equal to zero")
        if self.task_size_mbits_max < self.task_size_mbits_min:
            raise ValueError("task_size_mbits_max must be greater than or equal to task_size_mbits_min")
        if self.task_size_mbits_step <= 0:
            raise ValueError("task_size_mbits_step must be greater than zero")
        if self.processing_density_gcycles_per_mbit <= 0:
            raise ValueError("processing_density_gcycles_per_mbit must be greater than zero")

    @property
    def task_size_values(self) -> tuple[float, ...]:
        return _build_size_values(self.task_size_mbits_min, self.task_size_mbits_max, self.task_size_mbits_step)


@dataclass(slots=True)
class TrafficScenarioPreset:
    """Static factories for the paper-backed traffic scenarios."""

    @staticmethod
    def paper_default() -> TrafficConfig:
        return TrafficConfig(
            scenario_name="paper_default",
            number_of_agents=20,
            episode_length=110,
            arrival_probability=0.5,
            slot_duration_seconds=0.1,
            timeout_slots=20,
            task_size_mbits_min=2.0,
            task_size_mbits_max=5.0,
            task_size_mbits_step=0.1,
            processing_density_gcycles_per_mbit=0.297,
        )

    @staticmethod
    def moderate() -> TrafficConfig:
        return TrafficConfig(
            scenario_name="moderate",
            number_of_agents=20,
            episode_length=110,
            arrival_probability=0.5,
            slot_duration_seconds=0.1,
            timeout_slots=20,
            task_size_mbits_min=1.0,
            task_size_mbits_max=3.0,
            task_size_mbits_step=0.1,
            processing_density_gcycles_per_mbit=0.297,
        )

    @staticmethod
    def heavy() -> TrafficConfig:
        return TrafficConfig(
            scenario_name="heavy",
            number_of_agents=20,
            episode_length=110,
            arrival_probability=0.7,
            slot_duration_seconds=0.1,
            timeout_slots=20,
            task_size_mbits_min=2.0,
            task_size_mbits_max=5.0,
            task_size_mbits_step=0.1,
            processing_density_gcycles_per_mbit=0.297,
        )

    @staticmethod
    def extreme() -> TrafficConfig:
        return TrafficConfig(
            scenario_name="extreme",
            number_of_agents=20,
            episode_length=110,
            arrival_probability=0.9,
            slot_duration_seconds=0.1,
            timeout_slots=20,
            task_size_mbits_min=3.0,
            task_size_mbits_max=7.0,
            task_size_mbits_step=0.1,
            processing_density_gcycles_per_mbit=0.297,
        )
