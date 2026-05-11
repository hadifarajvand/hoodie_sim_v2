from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from src.environment.compute_config import ComputeConfig
from src.environment.link_rate_config import LinkRateConfig
from src.environment.traffic_config import TrafficScenarioPreset


PAPER_PARAMETER_REGISTRY_PATH = Path("resources/papers/hoodie/recovered/paper-parameter-registry.json")
PAPER_OCR_PATH = Path("resources/papers/hoodie/ocr/merged.tex")
FEATURE_027_REPORT_PATH = Path("artifacts/analysis/link-rate-transmission-delay-contract/link-rate-contract-report.json")
COMPUTE_CONFIG_PATH = Path("src/environment/compute_config.py")
TRAFFIC_CONFIG_PATH = Path("src/environment/traffic_config.py")
LINK_RATE_CONFIG_PATH = Path("src/environment/link_rate_config.py")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


@dataclass(frozen=True, slots=True)
class UnitEvidence:
    name: str
    value: str | float | None
    unit: str | None
    status: str
    source_path: str
    notes: str

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "status": self.status,
            "source_path": self.source_path,
            "notes": self.notes,
        }


def build_paper_unit_evidence() -> dict[str, object]:
    registry = _load_json(PAPER_PARAMETER_REGISTRY_PATH)
    task_size = registry["task_size_parameters"]
    processing_density = registry["processing_density"]
    cpu_capacities = registry["cpu_capacities"]

    return {
        "task_size": UnitEvidence(
            name="task_size",
            value=task_size["value"],
            unit="Mbits",
            status=task_size["recovery_status"],
            source_path=PAPER_PARAMETER_REGISTRY_PATH.as_posix(),
            notes="Recovered from Table 4 and the paper OCR registry.",
        ).to_dict(),
        "processing_density": UnitEvidence(
            name="processing_density",
            value=processing_density["value"],
            unit="gigacycles/Mbit",
            status=processing_density["recovery_status"],
            source_path=PAPER_PARAMETER_REGISTRY_PATH.as_posix(),
            notes="Recovered from Table 4 and the paper OCR registry.",
        ).to_dict(),
        "cpu_capacities": {
            "EA_private": UnitEvidence(
                name="EA_private",
                value=cpu_capacities["EA_private"]["value"],
                unit="unrecoverable",
                status=cpu_capacities["EA_private"]["recovery_status"],
                source_path=PAPER_PARAMETER_REGISTRY_PATH.as_posix(),
                notes="No recoverable paper evidence for EA private CPU capacity.",
            ).to_dict(),
            "EA_public": UnitEvidence(
                name="EA_public",
                value=cpu_capacities["EA_public"]["value"],
                unit="unrecoverable",
                status=cpu_capacities["EA_public"]["recovery_status"],
                source_path=PAPER_PARAMETER_REGISTRY_PATH.as_posix(),
                notes="No recoverable paper evidence for EA public CPU capacity.",
            ).to_dict(),
            "cloud": UnitEvidence(
                name="cloud",
                value=cpu_capacities["cloud"]["value"],
                unit="unrecoverable",
                status=cpu_capacities["cloud"]["recovery_status"],
                source_path=PAPER_PARAMETER_REGISTRY_PATH.as_posix(),
                notes="No recoverable paper evidence for cloud CPU capacity.",
            ).to_dict(),
        },
        "slot_duration": {
            "paper_delta_seconds": TrafficScenarioPreset.paper_default().slot_duration_seconds,
            "source_path": PAPER_OCR_PATH.as_posix(),
            "status": "recovered",
            "notes": "Recovered from the paper-backed traffic preset and OCR evidence.",
        },
    }


def build_runtime_unit_contract() -> dict[str, object]:
    traffic = TrafficScenarioPreset.paper_default()
    link_rate = LinkRateConfig()
    compute = ComputeConfig()

    return {
        "compute_config_path": COMPUTE_CONFIG_PATH.as_posix(),
        "traffic_config_path": TRAFFIC_CONFIG_PATH.as_posix(),
        "link_rate_config_path": LINK_RATE_CONFIG_PATH.as_posix(),
        "runtime_slot_duration_seconds": {
            "traffic_config": traffic.slot_duration_seconds,
            "link_rate_config": link_rate.slot_duration_seconds,
        },
        "runtime_slot_duration_source": {
            "traffic_config": "paper-backed",
            "link_rate_config": "paper-backed" if link_rate.slot_duration_seconds == traffic.slot_duration_seconds else "assumption-backed",
        },
        "runtime_timeout_slots": traffic.timeout_slots,
        "runtime_timeout_source": "paper-backed",
        "runtime_task_size_unit": "Mbits",
        "runtime_processing_density_unit": "gigacycles/Mbit",
        "runtime_cpu_capacity_fields": {
            "cpu_capacity_per_slot_agent": {
                "value": compute.cpu_capacity_per_slot_agent,
                "source": "assumption-backed",
            },
            "cpu_capacity_per_slot_edge": {
                "value": compute.cpu_capacity_per_slot_edge,
                "source": "assumption-backed",
            },
            "cpu_capacity_per_slot_cloud": {
                "value": compute.cpu_capacity_per_slot_cloud,
                "source": "assumption-backed",
            },
        },
        "runtime_contract_classification": (
            "paper-backed-runtime-with-assumption-backed-cpu-capacity-fields"
            if link_rate.slot_duration_seconds == traffic.slot_duration_seconds
            else "runtime-paper-mismatch"
        ),
    }
