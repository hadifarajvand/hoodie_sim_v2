from __future__ import annotations

from dataclasses import dataclass, field
from math import ceil
from typing import Mapping

BITS_PER_MBIT = 1_000_000.0
BPS_PER_MBPS = 1_000_000.0
DEFAULT_SLOT_DURATION_SECONDS = 1.0
DEFAULT_HORIZONTAL_DATA_RATE_MBPS = 30.0
DEFAULT_VERTICAL_DATA_RATE_MBPS = 10.0
DEFAULT_LINK_RATE_ROUNDING_POLICY = "ceil"


def bits_to_mbits(bits: float) -> float:
    return float(bits) / BITS_PER_MBIT


def mbits_to_bits(mbits: float) -> float:
    return float(mbits) * BITS_PER_MBIT


def bps_to_mbps(bps: float) -> float:
    return float(bps) / BPS_PER_MBPS


def mbps_to_bps(mbps: float) -> float:
    return float(mbps) * BPS_PER_MBPS


def seconds_to_slots(seconds: float, slot_duration_seconds: float, *, rounding_policy: str = DEFAULT_LINK_RATE_ROUNDING_POLICY) -> int:
    if slot_duration_seconds <= 0:
        raise ValueError("slot_duration_seconds must be greater than zero")
    if seconds < 0:
        raise ValueError("seconds must be greater than or equal to zero")
    ratio = float(seconds) / float(slot_duration_seconds)
    if rounding_policy == "ceil":
        return int(ceil(ratio))
    if rounding_policy == "floor":
        return int(ratio // 1)
    if rounding_policy == "exact":
        if abs(ratio - round(ratio)) > 1e-12:
            raise ValueError("seconds cannot be represented exactly as slots under exact rounding")
        return int(round(ratio))
    if rounding_policy == "round_half_up":
        return int(ceil(ratio - 0.5))
    raise ValueError(f"Unsupported slot rounding policy: {rounding_policy}")


def slots_to_seconds(slots: int, slot_duration_seconds: float) -> float:
    if slot_duration_seconds <= 0:
        raise ValueError("slot_duration_seconds must be greater than zero")
    if slots < 0:
        raise ValueError("slots must be greater than or equal to zero")
    return float(slots) * float(slot_duration_seconds)


@dataclass(slots=True)
class LinkRateConfig:
    horizontal_data_rate_mbps: float = DEFAULT_HORIZONTAL_DATA_RATE_MBPS
    vertical_data_rate_mbps: float = DEFAULT_VERTICAL_DATA_RATE_MBPS
    slot_duration_seconds: float = DEFAULT_SLOT_DURATION_SECONDS
    per_edge_link_rates: Mapping[str, float] | None = None
    cloud_data_rate_mbps: float | None = None
    per_edge_status: str = "unsupported"
    cloud_status: str = "unrecoverable"
    source_registry_path: str = "artifacts/analysis/structured-paper-topology-linkrate-registry/topology-recovery-report.json"
    rounding_policy: str = DEFAULT_LINK_RATE_ROUNDING_POLICY
    metadata: dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.horizontal_data_rate_mbps = float(self.horizontal_data_rate_mbps)
        self.vertical_data_rate_mbps = float(self.vertical_data_rate_mbps)
        self.slot_duration_seconds = float(self.slot_duration_seconds)
        if self.horizontal_data_rate_mbps <= 0:
            raise ValueError("horizontal_data_rate_mbps must be greater than zero")
        if self.vertical_data_rate_mbps <= 0:
            raise ValueError("vertical_data_rate_mbps must be greater than zero")
        if self.slot_duration_seconds <= 0:
            raise ValueError("slot_duration_seconds must be greater than zero")
        if self.per_edge_link_rates is not None:
            self.per_edge_link_rates = dict(self.per_edge_link_rates)

    @property
    def horizontal_data_rate_bps(self) -> float:
        return mbps_to_bps(self.horizontal_data_rate_mbps)

    @property
    def vertical_data_rate_bps(self) -> float:
        return mbps_to_bps(self.vertical_data_rate_mbps)

    def supported_entrypoint(self) -> str:
        return "src/environment/link_rate_config.py"

    def to_dict(self) -> dict[str, object]:
        return {
            "horizontal_data_rate_mbps": self.horizontal_data_rate_mbps,
            "vertical_data_rate_mbps": self.vertical_data_rate_mbps,
            "slot_duration_seconds": self.slot_duration_seconds,
            "per_edge_link_rates": None if self.per_edge_link_rates is None else dict(self.per_edge_link_rates),
            "cloud_data_rate_mbps": self.cloud_data_rate_mbps,
            "per_edge_status": self.per_edge_status,
            "cloud_status": self.cloud_status,
            "public_config_entrypoint": self.supported_entrypoint(),
            "source_registry_path": self.source_registry_path,
            "rounding_policy": self.rounding_policy,
            "metadata": dict(self.metadata),
        }


@dataclass(slots=True)
class TransmissionDelayResult:
    payload_bits: float
    data_rate_bps: float
    delay_seconds: float
    delay_slots: int
    slot_duration_seconds: float
    slot_rounding_policy: str
    payload_unit: str = "bits"
    rate_unit: str = "bps"
    invalid_rate_policy: str = "fail_loudly"
    zero_payload_policy: str = "explicit_zero_delay"

    def to_dict(self) -> dict[str, object]:
        return {
            "payload_bits": self.payload_bits,
            "data_rate_bps": self.data_rate_bps,
            "delay_seconds": self.delay_seconds,
            "delay_slots": self.delay_slots,
            "slot_duration_seconds": self.slot_duration_seconds,
            "slot_rounding_policy": self.slot_rounding_policy,
            "payload_unit": self.payload_unit,
            "rate_unit": self.rate_unit,
            "invalid_rate_policy": self.invalid_rate_policy,
            "zero_payload_policy": self.zero_payload_policy,
        }


def compute_transmission_delay(
    payload_bits: float,
    data_rate_bps: float,
    *,
    slot_duration_seconds: float,
    rounding_policy: str = DEFAULT_LINK_RATE_ROUNDING_POLICY,
) -> TransmissionDelayResult:
    if payload_bits < 0:
        raise ValueError("payload_bits must be greater than or equal to zero")
    if data_rate_bps <= 0:
        raise ValueError("data_rate_bps must be greater than zero")
    delay_seconds = float(payload_bits) / float(data_rate_bps) if payload_bits else 0.0
    delay_slots = seconds_to_slots(delay_seconds, slot_duration_seconds, rounding_policy=rounding_policy)
    return TransmissionDelayResult(
        payload_bits=float(payload_bits),
        data_rate_bps=float(data_rate_bps),
        delay_seconds=delay_seconds,
        delay_slots=delay_slots,
        slot_duration_seconds=float(slot_duration_seconds),
        slot_rounding_policy=rounding_policy,
    )
