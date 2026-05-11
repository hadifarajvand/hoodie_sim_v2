from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
from typing import Any

from src.environment.link_rate_config import (
    BITS_PER_MBIT,
    BPS_PER_MBPS,
    DEFAULT_HORIZONTAL_DATA_RATE_MBPS,
    DEFAULT_LINK_RATE_ROUNDING_POLICY,
    DEFAULT_SLOT_DURATION_SECONDS,
    DEFAULT_VERTICAL_DATA_RATE_MBPS,
    LinkRateConfig,
    compute_transmission_delay,
    mbits_to_bits,
    mbps_to_bps,
    seconds_to_slots,
    slots_to_seconds,
)


DEFAULT_OUTPUT_DIR = Path("artifacts/analysis/link-rate-transmission-delay-contract")
JSON_FILENAME = "link-rate-contract-report.json"
MARKDOWN_FILENAME = "link-rate-contract-report.md"


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


@dataclass(frozen=True, slots=True)
class LinkRateContractReport:
    schema_version: str
    feature_id: str
    source_gates: dict[str, object]
    paper_backed_defaults: dict[str, object]
    link_rate_controls: dict[str, object]
    transmission_delay_contract: dict[str, object]
    unit_conversions: dict[str, object]
    monotonicity_checks: dict[str, object]
    unsupported_controls: list[dict[str, object]]
    remaining_blockers: list[dict[str, object]]
    topology_boundaries: dict[str, object]
    no_curve_fitting: bool
    no_topology_fabrication: bool
    no_policy_or_metric_redesign: bool
    no_training_or_dependency_drift: bool
    generated_artifacts: list[str]
    validation_summary: str

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "feature_id": self.feature_id,
            "source_gates": dict(self.source_gates),
            "paper_backed_defaults": dict(self.paper_backed_defaults),
            "link_rate_controls": dict(self.link_rate_controls),
            "transmission_delay_contract": dict(self.transmission_delay_contract),
            "unit_conversions": dict(self.unit_conversions),
            "monotonicity_checks": dict(self.monotonicity_checks),
            "unsupported_controls": [dict(item) for item in self.unsupported_controls],
            "remaining_blockers": [dict(item) for item in self.remaining_blockers],
            "topology_boundaries": dict(self.topology_boundaries),
            "no_curve_fitting": self.no_curve_fitting,
            "no_topology_fabrication": self.no_topology_fabrication,
            "no_policy_or_metric_redesign": self.no_policy_or_metric_redesign,
            "no_training_or_dependency_drift": self.no_training_or_dependency_drift,
            "generated_artifacts": list(self.generated_artifacts),
            "validation_summary": self.validation_summary,
        }

    def to_json(self) -> str:
        return _json_dump(self.to_dict())

    def to_markdown(self) -> str:
        lines = [
            "# Link-Rate Contract Report",
            "",
            f"- schema_version: `{self.schema_version}`",
            f"- feature_id: `{self.feature_id}`",
            "",
            "## Paper-Backed Defaults",
            f"- horizontal_data_rate_mbps: `{self.paper_backed_defaults['horizontal_data_rate_mbps']}`",
            f"- vertical_data_rate_mbps: `{self.paper_backed_defaults['vertical_data_rate_mbps']}`",
            f"- cloud_data_rate_status: `{self.paper_backed_defaults['cloud_data_rate_status']}`",
            f"- source_registry_path: `{self.paper_backed_defaults['source_registry_path']}`",
            "",
            "## Link-Rate Controls",
            f"- horizontal_control_status: `{self.link_rate_controls['horizontal_control_status']}`",
            f"- vertical_control_status: `{self.link_rate_controls['vertical_control_status']}`",
            f"- per_edge_control_status: `{self.link_rate_controls['per_edge_control_status']}`",
            f"- cloud_control_status: `{self.link_rate_controls['cloud_control_status']}`",
            f"- public_config_entrypoint: `{self.link_rate_controls['public_config_entrypoint']}`",
            "",
            "## Transmission Delay Contract",
            f"- formula: `{self.transmission_delay_contract['formula']}`",
            f"- output_seconds: `{self.transmission_delay_contract['output_seconds']}`",
            f"- output_slots: `{self.transmission_delay_contract['output_slots']}`",
            f"- slot_rounding_policy: `{self.transmission_delay_contract['slot_rounding_policy']}`",
            "",
            "## Unit Conversions",
            f"- bits_per_mbit: `{self.unit_conversions['bits_per_mbit']}`",
            f"- bps_per_mbps: `{self.unit_conversions['bps_per_mbps']}`",
            f"- seconds_to_slots_policy: `{self.unit_conversions['seconds_to_slots_policy']}`",
            f"- slots_to_seconds_policy: `{self.unit_conversions['slots_to_seconds_policy']}`",
            "",
            "## Monotonicity Checks",
        ]
        for key, value in self.monotonicity_checks.items():
            lines.append(f"- {key}: {value}")
        lines.extend([
            "",
            "## Unsupported Controls",
        ])
        for item in self.unsupported_controls:
            lines.append(f"- {item['control_name']}: {item['reason']} ({item['evidence_source']})")
        lines.extend([
            "",
            "## Remaining Blockers",
        ])
        for item in self.remaining_blockers:
            lines.append(f"- {item['blocker_id']} [{item['blocker_type']}]: {item['reason']}")
        lines.extend([
            "",
            "## Topology Boundaries",
            f"- figure_7_adjacency_status: `{self.topology_boundaries['figure_7_adjacency_status']}`",
            f"- legal_horizontal_destinations_status: `{self.topology_boundaries['legal_horizontal_destinations_status']}`",
            f"- paper_topology_injected: `{self.topology_boundaries['paper_topology_injected']}`",
            "",
            "## Validation Summary",
            self.validation_summary,
            "",
        ])
        return "\n".join(lines)

    def write(self, output_dir: Path | str | None = None) -> tuple[Path, Path]:
        target_dir = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR
        target_dir.mkdir(parents=True, exist_ok=True)
        json_path = target_dir / JSON_FILENAME
        markdown_path = target_dir / MARKDOWN_FILENAME
        json_path.write_text(self.to_json(), encoding="utf-8")
        markdown_path.write_text(self.to_markdown(), encoding="utf-8")
        return json_path, markdown_path


def build_link_rate_contract_report() -> LinkRateContractReport:
    config = LinkRateConfig()
    horizontal = compute_transmission_delay(8_000_000.0, config.horizontal_data_rate_bps, slot_duration_seconds=config.slot_duration_seconds)
    vertical = compute_transmission_delay(8_000_000.0, config.vertical_data_rate_bps, slot_duration_seconds=config.slot_duration_seconds)
    wider_horizontal = compute_transmission_delay(8_000_000.0, mbps_to_bps(60.0), slot_duration_seconds=config.slot_duration_seconds)
    wider_vertical = compute_transmission_delay(8_000_000.0, mbps_to_bps(20.0), slot_duration_seconds=config.slot_duration_seconds)

    return LinkRateContractReport(
        schema_version="1.0",
        feature_id="027-link-rate-control-transmission-delay-contract",
        source_gates={
            "feature_020": {"artifact": "artifacts/analysis/controlled-mechanistic-sweeps/controlled-mechanistic-sweeps.json", "status": "instrumentation_gap"},
            "feature_025": {"artifact": "artifacts/analysis/structured-paper-topology-linkrate-registry/topology-recovery-report.json", "status": "recovered_defaults"},
            "feature_026": {"artifact": "artifacts/analysis/offload-lifecycle-instrumentation/instrumentation-summary.json", "status": "present"},
        },
        paper_backed_defaults={
            "horizontal_data_rate_mbps": DEFAULT_HORIZONTAL_DATA_RATE_MBPS,
            "vertical_data_rate_mbps": DEFAULT_VERTICAL_DATA_RATE_MBPS,
            "cloud_data_rate_status": "unrecoverable",
            "source_registry_path": config.source_registry_path,
        },
        link_rate_controls={
            "horizontal_control_status": "public_configured",
            "vertical_control_status": "public_configured",
            "per_edge_control_status": "unsupported_without_non_fabricated_evidence",
            "cloud_control_status": "unrecoverable",
            "public_config_entrypoint": config.supported_entrypoint(),
        },
        transmission_delay_contract={
            "formula": "delay_seconds = payload_bits / data_rate_bps",
            "payload_unit": "bits",
            "rate_unit": "bps",
            "output_seconds": {
                "horizontal_default": horizontal.delay_seconds,
                "vertical_default": vertical.delay_seconds,
            },
            "output_slots": {
                "horizontal_default": horizontal.delay_slots,
                "vertical_default": vertical.delay_slots,
            },
            "slot_duration_seconds": config.slot_duration_seconds,
            "slot_rounding_policy": config.rounding_policy,
            "invalid_rate_policy": "fail_loudly",
            "zero_payload_policy": "explicit_zero_delay",
        },
        unit_conversions={
            "bits_per_mbit": BITS_PER_MBIT,
            "bps_per_mbps": BPS_PER_MBPS,
            "seconds_to_slots_policy": config.rounding_policy,
            "slots_to_seconds_policy": "exact_multiplication_by_slot_duration_seconds",
        },
        monotonicity_checks={
            "horizontal": wider_horizontal.delay_seconds <= horizontal.delay_seconds,
            "vertical": wider_vertical.delay_seconds <= vertical.delay_seconds,
            "per_edge_if_supported": "unsupported",
        },
        unsupported_controls=[
            {
                "control_name": "per_edge_link_rates",
                "reason": "Topology evidence is unrecoverable; non-fabricated per-edge control remains unsupported.",
                "evidence_source": config.source_registry_path,
            },
            {
                "control_name": "cloud_data_rate",
                "reason": "Paper evidence does not recover a distinct cloud data-rate constant.",
                "evidence_source": config.source_registry_path,
            },
        ],
        remaining_blockers=[
            {
                "blocker_id": "topology-figure-7",
                "blocker_type": "paper_recovery_gap",
                "reason": "Figure 7 adjacency remains unrecoverable without fabrication.",
            }
        ],
        topology_boundaries={
            "figure_7_adjacency_status": "unrecoverable",
            "legal_horizontal_destinations_status": "non-paper-backed",
            "paper_topology_injected": False,
        },
        no_curve_fitting=True,
        no_topology_fabrication=True,
        no_policy_or_metric_redesign=True,
        no_training_or_dependency_drift=True,
        generated_artifacts=[
            "artifacts/analysis/link-rate-transmission-delay-contract/link-rate-contract-report.json",
            "artifacts/analysis/link-rate-transmission-delay-contract/link-rate-contract-report.md",
        ],
        validation_summary=(
            "Recovered defaults are public and deterministic; unsupported per-edge/cloud controls remain blocked; "
            "monotonic delay checks pass for supported horizontal and vertical defaults; no paper-topology fabrication is claimed."
        ),
    )


def render_markdown(report: LinkRateContractReport) -> str:
    return report.to_markdown()


def write_link_rate_contract_report(report: LinkRateContractReport | None = None, output_dir: Path | str | None = None) -> tuple[Path, Path]:
    contract_report = report or build_link_rate_contract_report()
    return contract_report.write(output_dir)

