from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator
import json
import tempfile

from src.environment.compute_config import ComputeConfig
from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.link_rate_config import LinkRateConfig
from src.environment.runtime_model import SharedRuntimeParameters
from src.environment.topology import TopologyGraph
from src.environment.trace_source import TraceSource
from src.environment.traffic_config import TrafficConfig
from src.environment.traffic_generator import TrafficGenerator

from src.analysis.full_training_reproduction_campaign import trainer as campaign_trainer
from src.analysis.terminal_lifecycle_accounting_50_100_comparison import repaired_terminal_evaluator as terminal_evaluator

from .config import (
    CALIBRATION_ARRIVAL_PROBABILITY,
    CALIBRATION_CPU_CLOUD_GCYCLES_PER_SLOT,
    CALIBRATION_CPU_PRIVATE_GCYCLES_PER_SLOT,
    CALIBRATION_CPU_PUBLIC_GCYCLES_PER_SLOT,
    CALIBRATION_DEADLINE_SLACK_MULTIPLIER,
    CALIBRATION_HORIZONTAL_LINK_RATE_MBPS,
    CALIBRATION_NUMBER_OF_AGENTS,
    CALIBRATION_PROCESSING_DENSITY_GCYCLES_PER_MBIT,
    CALIBRATION_PROFILE_NAME,
    CALIBRATION_SLOT_DURATION_SECONDS,
    CALIBRATION_TASK_SIZE_MBITS_MAX,
    CALIBRATION_TASK_SIZE_MBITS_MIN,
    CALIBRATION_TASK_SIZE_MBITS_STEP,
    CALIBRATION_TIMEOUT_SLOTS,
    CALIBRATION_TRACE_ROOT_NAME,
    CALIBRATION_VERTICAL_LINK_RATE_MBPS,
)


@dataclass(frozen=True, slots=True)
class CalibrationProfile:
    profile_name: str
    traffic_config: TrafficConfig
    trace_root: Path

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile_name": self.profile_name,
            "trace_root": str(self.trace_root),
            "traffic_config": {
                "scenario_name": self.traffic_config.scenario_name,
                "number_of_agents": self.traffic_config.number_of_agents,
                "episode_length": self.traffic_config.episode_length,
                "arrival_probability": self.traffic_config.arrival_probability,
                "slot_duration_seconds": self.traffic_config.slot_duration_seconds,
                "timeout_slots": self.traffic_config.timeout_slots,
                "task_size_mbits_min": self.traffic_config.task_size_mbits_min,
                "task_size_mbits_max": self.traffic_config.task_size_mbits_max,
                "task_size_mbits_step": self.traffic_config.task_size_mbits_step,
                "processing_density_gcycles_per_mbit": self.traffic_config.processing_density_gcycles_per_mbit,
            },
        }


def build_calibration_profile(trace_root: Path) -> CalibrationProfile:
    traffic_config = TrafficConfig(
        scenario_name="paper_default",
        number_of_agents=CALIBRATION_NUMBER_OF_AGENTS,
        episode_length=110,
        arrival_probability=CALIBRATION_ARRIVAL_PROBABILITY,
        slot_duration_seconds=CALIBRATION_SLOT_DURATION_SECONDS,
        timeout_slots=CALIBRATION_TIMEOUT_SLOTS,
        task_size_mbits_min=CALIBRATION_TASK_SIZE_MBITS_MIN,
        task_size_mbits_max=CALIBRATION_TASK_SIZE_MBITS_MAX,
        task_size_mbits_step=CALIBRATION_TASK_SIZE_MBITS_STEP,
        processing_density_gcycles_per_mbit=CALIBRATION_PROCESSING_DENSITY_GCYCLES_PER_MBIT,
    )
    return CalibrationProfile(profile_name=CALIBRATION_PROFILE_NAME, traffic_config=traffic_config, trace_root=trace_root)


def build_calibration_change_log() -> list[dict[str, Any]]:
    return [
        {
            "field_name": "trace_generation_model",
            "before_value": "build_deterministic_trace",
            "after_value": CALIBRATION_PROFILE_NAME,
            "reason": "The deterministic synthetic trace used by Feature 068 was infeasible for every action path.",
            "paper_alignment_note": "Paper-aligned traces should expose both feasible and infeasible decisions.",
        },
        {
            "field_name": "timeout_length",
            "before_value": {"min": 2, "max": 5},
            "after_value": {"min": CALIBRATION_TIMEOUT_SLOTS, "max": CALIBRATION_TIMEOUT_SLOTS},
            "reason": "The deadline envelope was too short for any completion path to win before the timeout.",
            "paper_alignment_note": "A longer timeout restores a nontrivial offloading decision problem.",
        },
        {
            "field_name": "task_size_mbits",
            "before_value": {"min": 10.0, "max": 100.0},
            "after_value": {"min": CALIBRATION_TASK_SIZE_MBITS_MIN, "max": CALIBRATION_TASK_SIZE_MBITS_MAX},
            "reason": "Task sizes were too large relative to CPU and link capacity.",
            "paper_alignment_note": "The calibrated sizes are smaller and span both feasible and infeasible cases.",
        },
        {
            "field_name": "processing_density_gcycles_per_mbit",
            "before_value": {"min": 1.0, "max": 5.0},
            "after_value": CALIBRATION_PROCESSING_DENSITY_GCYCLES_PER_MBIT,
            "reason": "The workload density was too heavy for the existing compute capacities.",
            "paper_alignment_note": "A lighter density restores feasible local and offload paths.",
        },
        {
            "field_name": "arrival_probability",
            "before_value": 1.0,
            "after_value": CALIBRATION_ARRIVAL_PROBABILITY,
            "reason": "The calibrated profile reduces load while keeping the workload nontrivial.",
            "paper_alignment_note": "Lower arrival pressure makes feasible tasks observable without trivializing the episode.",
        },
        {
            "field_name": "number_of_agents",
            "before_value": 1,
            "after_value": CALIBRATION_NUMBER_OF_AGENTS,
            "reason": "The calibrated profile keeps the per-episode decision volume close to the earlier comparison window.",
            "paper_alignment_note": "Maintains a comparable decision horizon without forcing every slot to be occupied.",
        },
        {
            "field_name": "deadline_slack_multiplier",
            "before_value": 1.0,
            "after_value": CALIBRATION_DEADLINE_SLACK_MULTIPLIER,
            "reason": "No hidden slack multiplier is introduced; the calibration is explicit in the trace profile.",
            "paper_alignment_note": "The deadline repair remains transparent and documented.",
        },
    ]


class CalibratedHoodieGymEnvironment(HoodieGymEnvironment):
    def reset(self, seed: int | None = None):  # type: ignore[override]
        if self.trace_source is not None and self.trace_source.mode == "trace_bank":
            return super().reset(seed=None)
        return super().reset(seed=seed)


def _trace_payload(trace) -> dict[str, Any]:
    return {
        "trace_id": trace.trace_id,
        "seed": trace.seed,
        "metadata": dict(trace.metadata),
        "tasks": [
            {
                "task_id": blueprint.task_id,
                "source_agent_id": blueprint.source_agent_id,
                "arrival_slot": blueprint.arrival_slot,
                "size": blueprint.size,
                "processing_density": blueprint.processing_density,
                "timeout_length": blueprint.timeout_length,
                "absolute_deadline_slot": blueprint.absolute_deadline_slot,
                "cycles_required": blueprint.cycles_required,
                "cycles_remaining": blueprint.cycles_remaining,
            }
            for blueprint in trace.tasks
        ],
    }


def ensure_calibrated_trace_bank(profile: CalibrationProfile, seed: int) -> Path:
    profile.trace_root.mkdir(parents=True, exist_ok=True)
    trace = TrafficGenerator.generate(profile.traffic_config, seed)
    trace_path = profile.trace_root / f"{profile.profile_name}-{seed}.json"
    if not trace_path.exists():
        trace.write_json(trace_path)
    return trace_path


@contextmanager
def patched_calibrated_environment(profile: CalibrationProfile) -> Iterator[None]:
    original_trainer_builder = campaign_trainer._build_environment
    original_evaluator_builder = terminal_evaluator._build_environment

    def _build_environment(config, *, episode_length: int, seed: int):
        trace_seed = int(seed)
        ensure_calibrated_trace_bank(profile, trace_seed)
        return CalibratedHoodieGymEnvironment(
            episode_length=episode_length,
            topology=TopologyGraph.from_approved_assumption_registry(),
            runtime_parameters=SharedRuntimeParameters(),
            compute_config=ComputeConfig(
                cpu_capacity_per_slot_agent=CALIBRATION_CPU_PRIVATE_GCYCLES_PER_SLOT,
                cpu_capacity_per_slot_edge=CALIBRATION_CPU_PUBLIC_GCYCLES_PER_SLOT,
                cpu_capacity_per_slot_cloud=CALIBRATION_CPU_CLOUD_GCYCLES_PER_SLOT,
            ),
            trace_source=TraceSource.from_trace_bank(f"{profile.profile_name}-{trace_seed}", root_path=profile.trace_root),
            link_rate_config=LinkRateConfig(
                horizontal_data_rate_mbps=CALIBRATION_HORIZONTAL_LINK_RATE_MBPS,
                vertical_data_rate_mbps=CALIBRATION_VERTICAL_LINK_RATE_MBPS,
                slot_duration_seconds=CALIBRATION_SLOT_DURATION_SECONDS,
            ),
            policy_name="HOODIE",
        )

    campaign_trainer._build_environment = _build_environment
    terminal_evaluator._build_environment = _build_environment
    try:
        yield
    finally:
        campaign_trainer._build_environment = original_trainer_builder
        terminal_evaluator._build_environment = original_evaluator_builder

