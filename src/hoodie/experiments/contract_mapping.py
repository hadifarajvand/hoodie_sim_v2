from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.config.training_config import TrainingConfig
from src.evaluation.config import EvaluationConfig
from src.environment.runtime_model import SharedRuntimeParameters
from src.training.seed_management import SeedManagement

from .job_matrix import ProductionJobRow
from .panel_registry import PANEL_REGISTRY

@dataclass(frozen=True, slots=True)
class ContractAuditResult:
    job_id: str
    panel_id: str
    independent_variable: str
    independent_value: Any
    required_training_episodes: int | None
    required_validation_episodes: int | None
    required_slots_per_episode: int | None
    generated_executor_configuration: dict[str, Any]
    mismatches: list[str]
    valid: bool


def _panel_contract(row: ProductionJobRow) -> dict[str, Any]:
    return PANEL_REGISTRY[row.panel_id].source_contract


def _slot_duration(panel_contract: dict[str, Any]) -> float:
    return float(panel_contract.get("slot_duration", 0.1))


def _override_contract(matrix_row: ProductionJobRow, source_contract: dict[str, Any], kind: str) -> dict[str, Any]:
    contract = dict(source_contract)
    override = getattr(matrix_row, f"{kind}_contract", None) or {}
    if isinstance(override, dict) and override:
        contract.update(override)
    return contract


def build_environment_config(row: ProductionJobRow, source_contract: dict[str, Any]) -> SharedRuntimeParameters:
    panel_contract = _override_contract(row, source_contract, "workload") if getattr(row, "training_contract", None) or getattr(row, "evaluation_contract", None) else source_contract
    slot_duration = _slot_duration(panel_contract)
    arrival_probability = float(panel_contract.get("task_arrival_probability", 0.5) or 0.5)
    timeout_seconds = float(panel_contract.get("task_timeout_seconds", 2.0) or 2.0)
    agent_count = int((panel_contract.get("agent_counts") or [20])[0])
    cpu_capacity = panel_contract.get("cpu_computation_capacity_ghz")
    metadata: dict[str, object] = {
        "panel_id": row.panel_id,
        "independent_variable": row.independent_variable,
        "independent_value": row.independent_value,
        "topology_hash": row.topology_contract,
    }
    if row.independent_variable == "task_arrival_probability":
        arrival_probability = float(row.independent_value)
    elif row.independent_variable == "cpu_computation_capacity_ghz":
        cpu_capacity = float(row.independent_value)
        metadata["cpu_computation_capacity_ghz"] = cpu_capacity
    elif row.independent_variable in {"number_of_agents", "agent_count"}:
        agent_count = int(row.independent_value)
    elif row.independent_variable == "task_timeout_seconds":
        timeout_seconds = float(row.independent_value)
    elif row.independent_variable in {"traffic_scenario", "communication_rate_scenario"}:
        metadata[row.independent_variable] = row.independent_value
    timeout_slots = max(1, int(round(timeout_seconds / slot_duration)))
    if cpu_capacity is not None:
        metadata["cpu_computation_capacity_ghz"] = float(cpu_capacity)
    return SharedRuntimeParameters(
        arrival_probability=arrival_probability,
        agent_count=agent_count,
        timeout_slots=timeout_slots,
        local_service_capacity=float(cpu_capacity if cpu_capacity is not None else panel_contract.get("local_service_capacity", 0.5) or 0.5),
        public_service_capacity=float(panel_contract.get("public_service_capacity", 0.5) or 0.5),
        cloud_service_capacity=float(panel_contract.get("cloud_service_capacity", 3.0) or 3.0),
        metadata=metadata,
    )


def build_training_config(matrix_row: ProductionJobRow, source_contract: dict[str, Any], *, trace_hash: str, output_dir) -> TrainingConfig:
    panel_contract = _override_contract(matrix_row, source_contract, "training")
    training_episodes = int(panel_contract.get("training_episodes", matrix_row.topology_contract.get("training_episodes", 0)))
    episode_length = int(panel_contract.get("slots_per_episode", 110 if matrix_row.panel_id.startswith("figure_8") else panel_contract.get("validation_episodes", 200)))
    learning_rate = float(panel_contract.get("learning_rate", 7e-7))
    discount_factor = float(panel_contract.get("discount_factor", 0.99))
    batch_size = int(panel_contract.get("batch_size", 64))
    replay_capacity = int(panel_contract.get("replay_capacity", 10000))
    target_copy_frequency = int(panel_contract.get("target_copy_frequency", 2000))
    drain_slots = int(panel_contract.get("drain_slots", 10))
    return TrainingConfig(
        learning_rate=learning_rate,
        batch_size=batch_size,
        replay_buffer_capacity=replay_capacity,
        target_network_update_frequency=target_copy_frequency,
        episode_count=training_episodes,
        episode_length=episode_length,
        discount_factor=discount_factor,
        drain_slots=drain_slots,
        seed_management=SeedManagement(training_seed=int(matrix_row.seed or 0), evaluation_seed=int(matrix_row.seed or 0)),
        policy_name=matrix_row.policy,
        trace_id=trace_hash,
        output_dir=output_dir,
    )


def build_evaluation_config(matrix_row: ProductionJobRow, source_contract: dict[str, Any], *, trace_id: str, output_dir) -> EvaluationConfig:
    panel_contract = _override_contract(matrix_row, source_contract, "evaluation")
    validation_episodes = int(panel_contract.get("validation_episodes", 200))
    episode_length = int(panel_contract.get("slots_per_episode", 110 if matrix_row.panel_id.startswith("figure_8") else validation_episodes))
    drain_slots = int(panel_contract.get("drain_slots", 10))
    return EvaluationConfig(
        policy_name=matrix_row.policy,
        seed=int(matrix_row.seed or 0),
        trace_id=trace_id,
        episode_count=validation_episodes,
        episode_length=episode_length,
        drain_slots=drain_slots,
        output_dir=output_dir,
        trace_mode="deterministic_seed",
        device="cpu",
    )


def apply_panel_sweep(base_config: dict[str, Any], panel_contract: dict[str, Any], matrix_row: ProductionJobRow) -> dict[str, Any]:
    sweep_key = matrix_row.independent_variable
    result = dict(base_config)
    allowed: set[str]
    if matrix_row.panel_id == "figure_8a":
        allowed = {"training_episode", "learning_rate"}
    elif matrix_row.panel_id == "figure_8b":
        allowed = {"training_episode", "discount_factor"}
    elif matrix_row.panel_id == "figure_9a":
        allowed = {"task_arrival_probability"}
    elif matrix_row.panel_id == "figure_9b":
        allowed = {"action_category", "metric"}
    elif matrix_row.panel_id == "figure_9c":
        allowed = {"cpu_computation_capacity_ghz"}
    elif matrix_row.panel_id == "figure_9d":
        allowed = {"agent_count"}
    elif matrix_row.panel_id == "figure_9e":
        allowed = {"communication_rate_scenario"}
    elif matrix_row.panel_id in {"figure_10a", "figure_10d"}:
        allowed = {"task_arrival_probability"}
    elif matrix_row.panel_id in {"figure_10b", "figure_10e"}:
        allowed = {"cpu_computation_capacity_ghz"}
    elif matrix_row.panel_id in {"figure_10c", "figure_10f"}:
        allowed = {"task_timeout_seconds"}
    elif matrix_row.panel_id == "figure_11":
        allowed = {"training_episode", "variant"}
    else:
        raise ValueError(f"unknown panel {matrix_row.panel_id!r}")
    if sweep_key not in allowed:
        raise ValueError(f"unexpected sweep key {sweep_key!r} for panel {matrix_row.panel_id!r}")
    result["panel_id"] = matrix_row.panel_id
    result["independent_variable"] = sweep_key
    result["independent_value"] = matrix_row.independent_value
    result["policy"] = matrix_row.policy
    result["variant"] = matrix_row.variant
    return result


def validate_contract_mapping(row: ProductionJobRow, source_contract: dict[str, Any]) -> list[str]:
    mismatches: list[str] = []
    if row.job_type == "training":
        config = build_training_config(row, source_contract, trace_hash="trace", output_dir=None)
        if config.episode_count != int(source_contract.get("training_episodes", config.episode_count)):
            mismatches.append("episode_count")
        if row.panel_id == "figure_8a" and config.episode_count != 5000:
            mismatches.append("figure_8a_training_episodes")
        if row.panel_id == "figure_11" and config.episode_count != int(source_contract.get("training_episodes", config.episode_count)):
            mismatches.append("figure_11_training_episodes")
    else:
        config = build_evaluation_config(row, source_contract, trace_id="trace", output_dir=None)
        if config.episode_count != int(source_contract.get("validation_episodes", config.episode_count)):
            mismatches.append("validation_episodes")
    return mismatches
