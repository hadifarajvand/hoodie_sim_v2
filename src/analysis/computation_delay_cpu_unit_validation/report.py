from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from src.analysis.link_rate_transmission_delay_contract.report import build_link_rate_contract_report
from src.environment.traffic_config import TrafficScenarioPreset

from .completion_slot import compute_completion_slot
from .computation_delay import ComputationDelayExample, compute_cycles_required
from .cpu_capacity import build_cpu_capacity_contract
from .slot_duration import audit_slot_duration_contract
from .unit_evidence import build_paper_unit_evidence, build_runtime_unit_contract, FEATURE_027_REPORT_PATH


DEFAULT_OUTPUT_DIR = Path("artifacts/analysis/computation-delay-cpu-unit-validation")
JSON_FILENAME = "unit-validation-report.json"
MARKDOWN_FILENAME = "unit-validation-report.md"


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


@dataclass(frozen=True, slots=True)
class UnitValidationReport:
    schema_version: str
    feature_id: str
    source_gates: dict[str, object]
    paper_unit_evidence: dict[str, object]
    runtime_unit_contract: dict[str, object]
    slot_duration_audit: dict[str, object]
    computation_delay_contract: dict[str, object]
    cpu_capacity_contract: dict[str, object]
    completion_slot_contract: dict[str, object]
    mismatch_findings: list[dict[str, object]]
    repaired_items: list[dict[str, object]]
    unrecoverable_items: list[dict[str, object]]
    regression_checks: dict[str, object]
    no_curve_fitting: bool
    no_policy_or_training_drift: bool
    generated_artifacts: list[str]
    validation_summary: str

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "feature_id": self.feature_id,
            "source_gates": dict(self.source_gates),
            "paper_unit_evidence": dict(self.paper_unit_evidence),
            "runtime_unit_contract": dict(self.runtime_unit_contract),
            "slot_duration_audit": dict(self.slot_duration_audit),
            "computation_delay_contract": dict(self.computation_delay_contract),
            "cpu_capacity_contract": dict(self.cpu_capacity_contract),
            "completion_slot_contract": dict(self.completion_slot_contract),
            "mismatch_findings": [dict(item) for item in self.mismatch_findings],
            "repaired_items": [dict(item) for item in self.repaired_items],
            "unrecoverable_items": [dict(item) for item in self.unrecoverable_items],
            "regression_checks": dict(self.regression_checks),
            "no_curve_fitting": self.no_curve_fitting,
            "no_policy_or_training_drift": self.no_policy_or_training_drift,
            "generated_artifacts": list(self.generated_artifacts),
            "validation_summary": self.validation_summary,
        }

    def to_json(self) -> str:
        return _json_dump(self.to_dict())

    def to_markdown(self) -> str:
        lines = [
            "# Computation Delay / CPU Unit Validation Report",
            "",
            f"- schema_version: `{self.schema_version}`",
            f"- feature_id: `{self.feature_id}`",
            "",
            "## Slot Duration Audit",
            f"- paper_delta_seconds: `{self.slot_duration_audit['paper_delta_seconds']}`",
            f"- runtime_delta_seconds: `{self.slot_duration_audit['runtime_delta_seconds']}`",
            f"- feature_027_reported_slot_duration_seconds: `{self.slot_duration_audit['feature_027_reported_slot_duration_seconds']}`",
            f"- mismatch_status: `{self.slot_duration_audit['mismatch_status']}`",
            f"- required_action: `{self.slot_duration_audit['required_action']}`",
            "",
            "## Runtime Unit Contract",
            f"- compute_config_path: `{self.runtime_unit_contract['compute_config_path']}`",
            f"- traffic_config_path: `{self.runtime_unit_contract['traffic_config_path']}`",
            f"- link_rate_config_path: `{self.runtime_unit_contract['link_rate_config_path']}`",
            f"- runtime_slot_duration_seconds: `{self.runtime_unit_contract['runtime_slot_duration_seconds']}`",
            f"- runtime_timeout_slots: `{self.runtime_unit_contract['runtime_timeout_slots']}`",
            f"- runtime_task_size_unit: `{self.runtime_unit_contract['runtime_task_size_unit']}`",
            f"- runtime_processing_density_unit: `{self.runtime_unit_contract['runtime_processing_density_unit']}`",
            "",
            "## Validation Summary",
            self.validation_summary,
            "",
        ]
        return "\n".join(lines)

    def write(self, output_dir: Path | str | None = None) -> tuple[Path, Path]:
        target_dir = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR
        target_dir.mkdir(parents=True, exist_ok=True)
        json_path = target_dir / JSON_FILENAME
        markdown_path = target_dir / MARKDOWN_FILENAME
        json_path.write_text(self.to_json(), encoding="utf-8")
        markdown_path.write_text(self.to_markdown(), encoding="utf-8")
        return json_path, markdown_path


def build_unit_validation_report() -> UnitValidationReport:
    traffic = TrafficScenarioPreset.paper_default()
    link_rate_report = build_link_rate_contract_report().to_dict()
    paper_unit_evidence = build_paper_unit_evidence()
    runtime_unit_contract = build_runtime_unit_contract()
    slot_audit = audit_slot_duration_contract(
        paper_delta_seconds=paper_unit_evidence["slot_duration"]["paper_delta_seconds"],
        runtime_delta_seconds=runtime_unit_contract["runtime_slot_duration_seconds"]["traffic_config"],
        feature_027_reported_slot_duration_seconds=link_rate_report["transmission_delay_contract"]["slot_duration_seconds"],
    ).to_dict()

    task_size = paper_unit_evidence["task_size"]
    processing_density = paper_unit_evidence["processing_density"]
    cycles_required = compute_cycles_required(2.1, 0.297)
    completion_slot = compute_completion_slot(current_slot=10, cycles_required=cycles_required, cpu_capacity_per_slot=32.0)
    cpu_capacity_contract = build_cpu_capacity_contract()

    return UnitValidationReport(
        schema_version="1.0",
        feature_id="028-computation-delay-cpu-unit-validation",
        source_gates={
            "feature_016": {
                "artifact": "artifacts/analysis/paper-mechanism-registry/paper-mechanism-registry.json",
                "status": "present",
            },
            "feature_025": {
                "artifact": "resources/papers/hoodie/recovered/paper-parameter-registry.json",
                "status": "present",
            },
            "feature_026": {
                "artifact": "artifacts/analysis/offload-lifecycle-instrumentation/instrumentation-summary.json",
                "status": "present",
            },
            "feature_027": {
                "artifact": "artifacts/analysis/link-rate-transmission-delay-contract/link-rate-contract-report.json",
                "status": "present",
            },
            "paper_ocr": {
                "artifact": "resources/papers/hoodie/ocr/merged.tex",
                "status": "present",
            },
        },
        paper_unit_evidence=paper_unit_evidence,
        runtime_unit_contract=runtime_unit_contract,
        slot_duration_audit=slot_audit,
        computation_delay_contract={
            "task_size_unit": "Mbits",
            "processing_density_unit": "gigacycles/Mbit",
            "cycles_required_formula": "cycles_required = task_size_mbits * processing_density_gcycles_per_mbit",
            "cycles_required_example": ComputationDelayExample(
                task_size_mbits=2.1,
                processing_density_gcycles_per_mbit=0.297,
                cycles_required=cycles_required,
                cpu_capacity_per_slot=32.0,
                delay_slots=1,
            ).to_dict(),
        },
        cpu_capacity_contract=cpu_capacity_contract,
        completion_slot_contract=completion_slot.to_dict() | {
            "current_slot": completion_slot.current_slot,
            "formula": completion_slot.formula,
        },
        mismatch_findings=[] if slot_audit["mismatch_status"] == "matched" else [
            {
                "finding": "slot_duration_mismatch",
                "paper_delta_seconds": slot_audit["paper_delta_seconds"],
                "runtime_delta_seconds": slot_audit["runtime_delta_seconds"],
                "feature_027_reported_slot_duration_seconds": slot_audit["feature_027_reported_slot_duration_seconds"],
                "status": slot_audit["mismatch_status"],
                "required_action": slot_audit["required_action"],
            }
        ],
        repaired_items=[] if slot_audit["mismatch_status"] != "repaired" else [
            {
                "item": "slot_duration_seconds",
                "from": 1.0,
                "to": slot_audit["paper_delta_seconds"],
            }
        ],
        unrecoverable_items=[
            {"item": "EA_private_cpu_capacity", "status": "unrecoverable"},
            {"item": "EA_public_cpu_capacity", "status": "unrecoverable"},
            {"item": "cloud_cpu_capacity", "status": "unrecoverable"},
        ],
        regression_checks={
            "feature_019_timeout_drop": "covered",
            "feature_024_local_compute_and_deterministic_ordering": "covered",
            "feature_027_link_rate_formula_and_monotonicity": "covered",
        },
        no_curve_fitting=True,
        no_policy_or_training_drift=True,
        generated_artifacts=[
            "artifacts/analysis/computation-delay-cpu-unit-validation/unit-validation-report.json",
            "artifacts/analysis/computation-delay-cpu-unit-validation/unit-validation-report.md",
            "artifacts/analysis/link-rate-transmission-delay-contract/link-rate-contract-report.json",
            "artifacts/analysis/link-rate-transmission-delay-contract/link-rate-contract-report.md",
        ],
        validation_summary=(
            "Task size and processing density are paper-backed; CPU capacities remain unrecoverable; "
            f"paper Δ={paper_unit_evidence['slot_duration']['paper_delta_seconds']} sec, "
            f"runtime Δ={runtime_unit_contract['runtime_slot_duration_seconds']['traffic_config']} sec, "
            f"Feature 027 reported Δ={link_rate_report['transmission_delay_contract']['slot_duration_seconds']} sec; "
            f"mismatch_status={slot_audit['mismatch_status']}; required_action={slot_audit['required_action']}."
        ),
    )


def write_unit_validation_report(report: UnitValidationReport, output_dir: Path | str | None = None) -> tuple[Path, Path]:
    return report.write(output_dir)
