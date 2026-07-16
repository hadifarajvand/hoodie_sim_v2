from __future__ import annotations

from typing import Any, Callable

from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.link_rate_config import compute_transmission_delay, mbits_to_bits

_INSTALLED = False
_ORIGINAL_ADMIT: Callable[..., Any] | None = None


def admit_with_exact_horizontal_runtime(
    self: HoodieGymEnvironment, task
) -> None:
    """Repair generic-environment bookkeeping for ``horizontal_<EA>`` actions.

    The environment historically recognized only the family label ``horizontal``
    while the corrected HOODIE policy emits an exact destination action. Queue
    placement already resolves that destination correctly, but the base admission
    path otherwise records the vertical data rate and omits horizontal lifecycle
    events. This wrapper keeps the exact selected action and repairs those physical
    and provenance fields immediately after admission.
    """

    if _ORIGINAL_ADMIT is None:  # pragma: no cover
        raise RuntimeError("exact horizontal runtime patch is not installed")
    _ORIGINAL_ADMIT(self, task)
    selected = str(task.selected_action or "")
    if not selected.startswith("horizontal_"):
        return

    payload_bits = mbits_to_bits(task.size)
    data_rate_bps = self.link_rate_config.horizontal_data_rate_bps
    transmission = compute_transmission_delay(
        payload_bits,
        data_rate_bps,
        slot_duration_seconds=self.link_rate_config.slot_duration_seconds,
        rounding_policy=self.link_rate_config.rounding_policy,
    )
    task.metadata["transmission_delay_slots"] = transmission.delay_slots
    task.metadata["transmission_delay_seconds"] = transmission.delay_seconds
    task.metadata["transmission_payload_bits"] = payload_bits
    task.metadata["transmission_data_rate_bps"] = data_rate_bps
    task.metadata["transmission_rate_source"] = "horizontal_R_H"
    task.metadata["transmission_rounding_policy"] = (
        transmission.slot_rounding_policy
    )

    ledger = self._trace_ledgers.get(task.task_id)
    if ledger is not None:
        events = ledger.snapshot()
        if "queued_public" not in events:
            ledger.emit("queued_public")
        if "transmission_started" not in events:
            ledger.emit("transmission_started")


def install_exact_horizontal_runtime_patch() -> None:
    global _INSTALLED
    global _ORIGINAL_ADMIT
    if _INSTALLED:
        return
    _ORIGINAL_ADMIT = HoodieGymEnvironment._admit_current_task
    HoodieGymEnvironment._admit_current_task = admit_with_exact_horizontal_runtime
    _INSTALLED = True
