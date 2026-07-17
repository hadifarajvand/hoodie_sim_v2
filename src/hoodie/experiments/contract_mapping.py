from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from src.config.training_config import TrainingConfig
from src.evaluation.config import EvaluationConfig
from src.environment.link_rate_config import LinkRateConfig
from src.environment.runtime_model import SharedRuntimeParameters
from src.training.seed_management import SeedManagement

from .job_matrix import ProductionJobRow
from .panel_registry import PANEL_REGISTRY

_TABLE4_PATH = Path("resources/papers/hoodie/contracts/table_4.json")


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


def _table4_values() -> dict[str, Any]:
    payload = json.loads(_TABLE4_PATH.read_text(encoding="utf-8"))
    return {str(field["name"]): field.get("value") for field in payload["fields"]}


def _panel_contract(row: ProductionJobRow) -> dict[str, Any]:
    return PANEL_REGISTRY[row.panel_id].source_contract


def _merged_contract(row: ProductionJobRow, source_contract: dict[str, Any]) -> dict[str, Any]:
    table = _table4_values()
    contract: dict[str, Any] = {
        "slot_duration_seconds": table["slot_duration_seconds"],
        "slots_per_episode": table["slots_per_episode"],
        "decision_slots": table["decision_slots"],
        "drain_slots": table["drain_slots"],
        "task_arrival_probability": table["task_arrival_probability"],
        "task_timeout_seconds": table["default_timeout_seconds"],
        "default_timeout_slots": table["default_timeout_slots"],
        "learning_rate": table["default_learning_rate"],
        "discount_factor": table["default_discount_factor"],
        "batch_size": table["batch_size"],
        "replay_capacity": table["replay_capacity"],
        "target_copy_frequency": table["target_copy_frequency_iterations"],
        # These source values are CPU rates in Gcycles/sec (GHz). They are
        # converted to Gcycles/slot only in build_environment_config.
        "local_cpu_ghz": table["private_edge_cpu_ghz"],
        "public_cpu_ghz": table["public_edge_cpu_ghz"],
        "cloud_cpu_ghz": table["cloud_cpu_ghz"],
        "horizontal_data_rate_mbps": table["horizontal_data_rate_mbps"],
        "vertical_data_rate_mbps": table["vertical_data_rate_mbps"],
        "agent_counts": [table["number_of_edge_agents"]],
        "q_network_hidden_layers": tuple(
            table.get("q_network_hidden_layers", (1024, 1024, 1024))
        ),
        "lstm_lookback": int(table.get("lstm_lookback_steps", 10)),
        "lstm_hidden": int(table.get("lstm_hidden_cells", 20)),
    }
    contract.update(source_contract)
    contract.update(row.topology_contract)
    contract.update(row.physical_contract)
    contract.update(row.workload_contract)
    if row.job_type == "training":
        contract.update(row.training_contract)
    else:
        contract.update(row.evaluation_contract)

    key = row.independent_variable
    value = row.independent_value
    if key in {
        "learning_rate",
        "discount_factor",
        "task_arrival_probability",
        "task_timeout_seconds",
    }:
        contract[key] = value
    elif key in {"number_of_agents", "agent_count"}:
        contract["agent_counts"] = [int(value)]
    elif key == "cpu_computation_capacity_ghz":
        contract["local_cpu_ghz"] = float(value)
        contract["public_cpu_ghz"] = float(value)
        contract["cpu_computation_capacity_ghz"] = float(value)
    elif key == "traffic_scenario":
        if not isinstance(value, str):
            raise ValueError("traffic_scenario independent value must be a scenario name")
        scenario = row.workload_contract.get("traffic_scenario")
        if not isinstance(scenario, dict):
            raise ValueError("traffic scenario row is missing its resolved workload contract")
        contract.update(scenario)
    elif key == "communication_rate_scenario":
        scenario = row.physical_contract.get("communication_rate_scenario")
        if not isinstance(scenario, dict):
            raise ValueError("communication-rate row is missing its resolved physical contract")
        contract.update(scenario)
    elif key in {"training_episode", "action_category", "metric", "variant"}:
        pass
    else:
        raise ValueError(f"unsupported matrix independent variable: {key!r}")
    return contract


def _slot_duration(contract: dict[str, Any]) -> float:
    duration = float(
        contract.get("slot_duration_seconds", contract.get("slot_duration", 0.1))
    )
    if duration <= 0:
        raise ValueError("slot duration must be positive")
    return duration


def _agent_count(contract: dict[str, Any]) -> int:
    values = contract.get("agent_counts", [20])
    if isinstance(values, (list, tuple)):
        if len(values) != 1:
            raise ValueError("one matrix row must resolve to exactly one agent count")
        count = int(values[0])
    else:
        count = int(values)
    if count <= 0:
        raise ValueError("agent count must be positive")
    return count


def _cpu_rate_ghz(
    contract: dict[str, Any], modern_key: str, legacy_key: str, default: float
) -> float:
    value = float(contract.get(modern_key, contract.get(legacy_key, default)))
    if value <= 0:
        raise ValueError(f"{modern_key} must be positive")
    return value


def build_environment_config(
    row: ProductionJobRow, source_contract: dict[str, Any]
) -> SharedRuntimeParameters:
    contract = _merged_contract(row, source_contract)
    slot_duration = _slot_duration(contract)
    timeout_seconds = float(contract.get("task_timeout_seconds", 2.0))
    timeout_slots = max(1, int(round(timeout_seconds / slot_duration)))
    local_ghz = _cpu_rate_ghz(contract, "local_cpu_ghz", "local_service_capacity", 5.0)
    public_ghz = _cpu_rate_ghz(contract, "public_cpu_ghz", "public_service_capacity", 5.0)
    cloud_ghz = _cpu_rate_ghz(contract, "cloud_cpu_ghz", "cloud_service_capacity", 30.0)
    metadata: dict[str, object] = {
        "panel_id": row.panel_id,
        "independent_variable": row.independent_variable,
        "independent_value": row.independent_value,
        "topology_contract": row.topology_contract,
        "physical_contract": row.physical_contract,
        "workload_contract": row.workload_contract,
        "slot_duration_seconds": slot_duration,
        "cpu_rate_units": "Gcycles/second",
        "runtime_capacity_units": "Gcycles/slot",
        "local_cpu_ghz": local_ghz,
        "public_cpu_ghz": public_ghz,
        "cloud_cpu_ghz": cloud_ghz,
    }
    return SharedRuntimeParameters(
        arrival_probability=float(contract.get("task_arrival_probability", 0.5)),
        agent_count=_agent_count(contract),
        timeout_slots=timeout_slots,
        local_service_capacity=round(local_ghz * slot_duration, 12),
        public_service_capacity=round(public_ghz * slot_duration, 12),
        cloud_service_capacity=round(cloud_ghz * slot_duration, 12),
        slot_duration=slot_duration,
        metadata=metadata,
    )


def build_link_rate_config(
    row: ProductionJobRow, source_contract: dict[str, Any]
) -> LinkRateConfig:
    contract = _merged_contract(row, source_contract)
    return LinkRateConfig(
        horizontal_data_rate_mbps=float(
            contract.get(
                "R_H_mbps", contract.get("horizontal_data_rate_mbps", 30.0)
            )
        ),
        vertical_data_rate_mbps=float(
            contract.get(
                "R_V_mbps", contract.get("vertical_data_rate_mbps", 10.0)
            )
        ),
        slot_duration_seconds=_slot_duration(contract),
        metadata={
            "panel_id": row.panel_id,
            "independent_variable": row.independent_variable,
            "independent_value": row.independent_value,
        },
    )


def build_training_config(
    matrix_row: ProductionJobRow,
    source_contract: dict[str, Any],
    *,
    trace_hash: str,
    output_dir: Path | None,
) -> TrainingConfig:
    contract = _merged_contract(matrix_row, source_contract)
    episodes = int(contract.get("training_episodes", 0))
    if episodes <= 0:
        raise ValueError(
            f"training row {matrix_row.job_id} has no positive training_episodes"
        )
    slots = int(contract.get("slots_per_episode", 110))
    drain = int(contract.get("drain_slots", 10))
    if slots <= 0 or not 0 <= drain < slots:
        raise ValueError("invalid slots_per_episode/drain_slots contract")
    backend = str(matrix_row.physical_contract.get("backend", "cpu"))
    seed = int(matrix_row.seed or 0)
    return TrainingConfig(
        learning_rate=float(contract.get("learning_rate", 7e-7)),
        batch_size=int(contract.get("batch_size", 64)),
        replay_buffer_capacity=int(contract.get("replay_capacity", 10_000)),
        target_network_update_frequency=int(
            contract.get("target_copy_frequency", 2_000)
        ),
        episode_count=episodes,
        episode_length=slots,
        discount_factor=float(contract.get("discount_factor", 0.99)),
        drain_slots=drain,
        seed_management=SeedManagement(
            training_seed=seed, evaluation_seed=seed
        ),
        policy_name=matrix_row.policy,
        trace_id=trace_hash,
        output_dir=output_dir,
        device=backend,
        learner_type="distributed_recurrent_ddqn",
        replay_seed=seed,
        torch_seed=seed,
    )


def training_architecture(
    matrix_row: ProductionJobRow, source_contract: dict[str, Any]
) -> dict[str, Any]:
    contract = _merged_contract(matrix_row, source_contract)
    hidden = contract.get("q_network_hidden_layers", (1024, 1024, 1024))
    return {
        "hidden_dims": tuple(int(value) for value in hidden),
        "lookback": int(contract.get("lstm_lookback", 10)),
        "lstm_hidden": int(contract.get("lstm_hidden", 20)),
    }


def build_evaluation_config(
    matrix_row: ProductionJobRow,
    source_contract: dict[str, Any],
    *,
    trace_id: str,
    output_dir: Path | None,
) -> EvaluationConfig:
    contract = _merged_contract(matrix_row, source_contract)
    episodes = int(contract.get("validation_episodes", 200))
    slots = int(contract.get("slots_per_episode", 110))
    drain = int(contract.get("drain_slots", 10))
    if episodes <= 0:
        raise ValueError("validation_episodes must be positive")
    if slots <= 0 or not 0 <= drain < slots:
        raise ValueError("invalid slots_per_episode/drain_slots contract")
    return EvaluationConfig(
        policy_name=matrix_row.policy,
        seed=int(matrix_row.seed or 0),
        trace_id=trace_id,
        episode_count=episodes,
        episode_length=slots,
        drain_slots=drain,
        output_dir=output_dir,
        trace_mode="deterministic_seed",
        device=str(matrix_row.physical_contract.get("backend", "cpu")),
    )


def apply_panel_sweep(
    base_config: dict[str, Any],
    panel_contract: dict[str, Any],
    matrix_row: ProductionJobRow,
) -> dict[str, Any]:
    del panel_contract
    result = dict(base_config)
    result.update(
        {
            "panel_id": matrix_row.panel_id,
            "independent_variable": matrix_row.independent_variable,
            "independent_value": matrix_row.independent_value,
            "policy": matrix_row.policy,
            "variant": matrix_row.variant,
            "series_name": matrix_row.series_name,
        }
    )
    return result


def validate_contract_mapping(
    row: ProductionJobRow, source_contract: dict[str, Any]
) -> list[str]:
    mismatches: list[str] = []
    try:
        contract = _merged_contract(row, source_contract)
        if row.job_type == "training":
            config = build_training_config(
                row, source_contract, trace_hash="trace", output_dir=None
            )
            if config.episode_count != int(contract["training_episodes"]):
                mismatches.append("episode_count")
            if config.learning_rate != float(contract["learning_rate"]):
                mismatches.append("learning_rate")
            if config.discount_factor != float(contract["discount_factor"]):
                mismatches.append("discount_factor")
            if config.batch_size != int(contract["batch_size"]):
                mismatches.append("batch_size")
            architecture = training_architecture(row, source_contract)
            if architecture["hidden_dims"] != (1024, 1024, 1024):
                mismatches.append("q_network_hidden_layers")
            if architecture["lookback"] != 10:
                mismatches.append("lstm_lookback_steps")
            if architecture["lstm_hidden"] != 20:
                mismatches.append("lstm_hidden_cells")
        else:
            config = build_evaluation_config(
                row, source_contract, trace_id="trace", output_dir=None
            )
            if config.episode_count != int(
                contract.get("validation_episodes", 200)
            ):
                mismatches.append("validation_episodes")
        environment = build_environment_config(row, source_contract)
        if environment.agent_count != _agent_count(contract):
            mismatches.append("agent_count")
        if (
            row.independent_variable == "task_arrival_probability"
            and environment.arrival_probability != float(row.independent_value)
        ):
            mismatches.append("task_arrival_probability")
        if row.independent_variable == "task_timeout_seconds":
            expected = max(
                1,
                int(
                    round(
                        float(row.independent_value) / _slot_duration(contract)
                    )
                ),
            )
            if environment.timeout_slots != expected:
                mismatches.append("task_timeout_seconds")
        if row.independent_variable == "cpu_computation_capacity_ghz":
            expected_capacity = float(row.independent_value) * _slot_duration(contract)
            if abs(environment.local_service_capacity - expected_capacity) > 1e-12:
                mismatches.append("cpu_computation_capacity_ghz")
        build_link_rate_config(row, source_contract)
    except (KeyError, TypeError, ValueError) as exc:
        mismatches.append(f"configuration_error:{exc}")
    return mismatches
