from __future__ import annotations

import math

from src.echo_types import EchoCandidateEstimate, EchoQueueEstimate, EchoTaskSpec


def compute_absolute_deadline(arrival_slot: int, timeout_slots: int) -> int:
    return int(arrival_slot) + int(timeout_slots) - 1


def compute_local_service_slots(task: EchoTaskSpec, local_cpu_ghz: float, slot_duration_seconds: float) -> int:
    if local_cpu_ghz <= 0 or slot_duration_seconds <= 0:
        raise ValueError("capacities and slot duration must be positive")
    cycles_per_slot = float(local_cpu_ghz) * float(slot_duration_seconds)
    return max(1, int(math.ceil(task.cycles_required_gcycles / cycles_per_slot)))


def compute_transmission_slots(size_mbits: float, rate_mbps: float, slot_duration_seconds: float) -> int:
    if rate_mbps <= 0 or slot_duration_seconds <= 0:
        raise ValueError("rate and slot duration must be positive")
    seconds = float(size_mbits) / float(rate_mbps)
    return int(math.ceil(seconds / float(slot_duration_seconds)))


def estimate_local_queue(
    task: EchoTaskSpec,
    *,
    current_slot: int,
    residual_service_slots: int,
    predecessor_service_slots: list[int],
    local_cpu_ghz: float,
    slot_duration_seconds: float,
) -> EchoQueueEstimate:
    service_slots = compute_local_service_slots(task, local_cpu_ghz, slot_duration_seconds)
    waiting_slots = int(residual_service_slots) + sum(int(value) for value in predecessor_service_slots)
    completion_slot = int(current_slot) + waiting_slots + service_slots - 1
    ert_slots = int(task.absolute_deadline_slot) - completion_slot
    lateness_slots = max(0, completion_slot - int(task.absolute_deadline_slot))
    return EchoQueueEstimate(
        waiting_slots=waiting_slots,
        completion_slot=completion_slot,
        ert_slots=ert_slots,
        lateness_slots=lateness_slots,
    )


def estimate_offload_candidate(
    task: EchoTaskSpec,
    *,
    destination_node_id: str,
    current_slot: int,
    outbound_residual_slots: int,
    outbound_predecessor_slots: list[int],
    transmission_rate_mbps: float,
    destination_waiting_slots: int,
    destination_cpu_ghz: float,
    slot_duration_seconds: float,
) -> EchoCandidateEstimate:
    transmission_slots = compute_transmission_slots(task.size_mbits, transmission_rate_mbps, slot_duration_seconds)
    destination_service_slots = compute_local_service_slots(task, destination_cpu_ghz, slot_duration_seconds)
    outbound_waiting_slots = int(outbound_residual_slots) + sum(int(value) for value in outbound_predecessor_slots)
    completion_slot = (
        int(current_slot)
        + outbound_waiting_slots
        + transmission_slots
        + int(destination_waiting_slots)
        + destination_service_slots
        - 1
    )
    ert_slots = int(task.absolute_deadline_slot) - completion_slot
    lateness_slots = max(0, completion_slot - int(task.absolute_deadline_slot))
    return EchoCandidateEstimate(
        action_id="",
        destination_node_id=destination_node_id,
        transmission_slots=transmission_slots,
        destination_waiting_slots=int(destination_waiting_slots),
        destination_service_slots=destination_service_slots,
        completion_slot=completion_slot,
        ert_slots=ert_slots,
        lateness_slots=lateness_slots,
        deadline_feasible=ert_slots >= 0,
    )
