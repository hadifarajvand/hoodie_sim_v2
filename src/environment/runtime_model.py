from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .task import Task


def _load_runtime_config() -> dict[str, Any]:
    config_path = Path("configs/runtime_model.yml")
    if not config_path.exists():
        return {}

    values: dict[str, Any] = {}
    current_section: str | None = None
    for raw_line in config_path.read_text().splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if line.startswith(" "):
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if value:
                try:
                    values[key] = int(value)
                except ValueError:
                    values[key] = value
            else:
                current_section = key
                values.setdefault(current_section, {})
    return values


_RUNTIME_CONFIG = _load_runtime_config()


@dataclass(slots=True)
class SharedRuntimeParameters:
    slot_duration: int = int(_RUNTIME_CONFIG.get("slot_duration", 1))
    local_service_capacity: int = int(_RUNTIME_CONFIG.get("local_service_capacity", 1))
    public_service_capacity: int = int(_RUNTIME_CONFIG.get("public_service_capacity", 1))
    cloud_service_capacity: int = int(_RUNTIME_CONFIG.get("cloud_service_capacity", 1))
    timeout_grace_slots: int = int(_RUNTIME_CONFIG.get("timeout_grace_slots", 0))
    runtime_variant: str = str(_RUNTIME_CONFIG.get("runtime_variant", "density_based"))
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class SharedRuntimeProgress:
    waiting_slots: int = 0
    offload_slots: int = 0
    service_slots: int = 0
    terminal_slot: int | None = None
    delayed_reward_ready: bool = False


def compute_service_delay(task: Task, destination_kind: str, parameters: SharedRuntimeParameters) -> int:
    variant = parameters.runtime_variant
    if variant == "constant_service":
        return 1
    if variant == "discrete_slot_service":
        return max(1, math.ceil(task.size / max(1, parameters.slot_duration)))

    base = max(1, task.processing_density) * max(1, parameters.slot_duration)
    if destination_kind == "local":
        capacity = max(1, parameters.local_service_capacity)
    elif destination_kind == "public":
        capacity = max(1, parameters.public_service_capacity)
    elif destination_kind == "cloud":
        capacity = max(1, parameters.cloud_service_capacity)
    else:
        capacity = max(1, parameters.local_service_capacity)

    return max(1, math.ceil(base / capacity))


def resolve_destination_kind(destination_kind: str | None, action: str | None) -> str:
    if destination_kind in {"local", "public", "cloud"}:
        return destination_kind
    if action in {"local", "compute_local"}:
        return "local"
    if action in {"vertical", "offload_vertical"}:
        return "cloud"
    if action in {"horizontal", "offload_horizontal"}:
        return "public"
    return "local"


def runtime_variant_name(parameters: SharedRuntimeParameters) -> str:
    return parameters.runtime_variant or "density_based"


def advance_shared_runtime(
    task: Task,
    destination_kind: str,
    current_slot: int,
    parameters: SharedRuntimeParameters,
) -> SharedRuntimeProgress:
    destination_kind = resolve_destination_kind(destination_kind, task.selected_action)
    waiting_slots = max(0, current_slot - task.arrival_slot)
    if task.metadata.get("queue_entered_at") is not None:
        waiting_slots = max(waiting_slots, max(0, current_slot - int(task.metadata["queue_entered_at"])))
    service_slots = compute_service_delay(task, destination_kind, parameters)
    offload_slots = 1 if destination_kind in {"public", "cloud"} else 0
    terminal_slot = task.arrival_slot + waiting_slots + offload_slots + service_slots
    return SharedRuntimeProgress(
        waiting_slots=waiting_slots,
        offload_slots=offload_slots,
        service_slots=service_slots,
        terminal_slot=terminal_slot,
        delayed_reward_ready=True,
    )


def resolve_runtime_terminal_state(
    task: Task,
    terminal_slot: int,
    current_slot: int,
    parameters: SharedRuntimeParameters | None = None,
) -> None:
    if task.completion_slot is None:
        task.completion_slot = terminal_slot
    effective_deadline = task.absolute_deadline_slot
    if parameters is not None:
        effective_deadline += max(0, parameters.timeout_grace_slots)
    if task.terminal_outcome is None:
        if terminal_slot <= effective_deadline:
            task.terminal_outcome = "completed"
        else:
            task.terminal_outcome = "dropped"
    if task.terminal_outcome in {"completed", "dropped"}:
        task.drop_flag = task.terminal_outcome == "dropped"
        task.reward_emitted = True
