from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
from typing import Any


@dataclass(slots=True)
class GateCheck:
    artifact: str
    present: bool
    valid: bool
    details: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "artifact": self.artifact,
            "present": self.present,
            "valid": self.valid,
            "details": list(self.details),
        }


@dataclass(slots=True)
class GateValidationResult:
    passed: bool
    checks: list[GateCheck]

    def to_dict(self) -> dict[str, object]:
        return {"passed": self.passed, "checks": [check.to_dict() for check in self.checks]}


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_differential_audit(payload: dict[str, Any]) -> list[str]:
    details: list[str] = []
    if payload.get("comparison_results") is None:
        details.append("missing comparison_results")
    else:
        case_ids = {item.get("case_id") for item in payload.get("comparison_results", [])}
        if "case-timeout-drop" not in case_ids:
            details.append("case-timeout-drop missing")
    return details


def _validate_repair_summary(payload: dict[str, Any]) -> list[str]:
    details: list[str] = []
    if payload.get("repaired_case_id") != "case-timeout-drop":
        details.append("repaired_case_id mismatch")
    if "src/environment/deadline_rules.py" not in payload.get("changed_environment_files", []):
        details.append("deadline_rules.py missing from changed_environment_files")
    if "src/environment/environment.py" not in payload.get("changed_environment_files", []):
        details.append("environment.py missing from changed_environment_files")
    if payload.get("environment_wrapper_edited") is not False:
        details.append("environment_wrapper_edited should be false")
    if payload.get("slot_engine_edited") is not False:
        details.append("slot_engine_edited should be false")
    return details


def _validate_controlled_sweeps(payload: dict[str, Any]) -> list[str]:
    details: list[str] = []
    if payload.get("metadata", {}).get("feature_id") != "020-controlled-mechanistic-sweeps":
        details.append("feature_id mismatch")
    statuses = {item.get("status") for item in payload.get("monotonic_checks", [])}
    if not statuses:
        details.append("missing monotonic_checks")
    if payload.get("overall_status") not in {"pass", "warn", "inconclusive", "instrumentation_gap"}:
        details.append("invalid overall_status")
    return details


def validate_feature_gates(
    differential_audit_path: Path,
    repair_summary_path: Path,
    controlled_sweeps_path: Path,
) -> GateValidationResult:
    checks: list[GateCheck] = []

    for label, path, validator in (
        ("differential_audit", differential_audit_path, _validate_differential_audit),
        ("repair_summary", repair_summary_path, _validate_repair_summary),
        ("controlled_sweeps", controlled_sweeps_path, _validate_controlled_sweeps),
    ):
        present = path.exists()
        if not present:
            checks.append(GateCheck(label, False, False, [f"missing file: {path}"]))
            continue
        try:
            payload = _read_json(path)
        except json.JSONDecodeError as exc:
            checks.append(GateCheck(label, True, False, [f"invalid JSON: {exc.msg}"]))
            continue
        details = validator(payload)
        checks.append(GateCheck(label, True, not details, details or ["valid"]))

    return GateValidationResult(passed=all(check.valid for check in checks), checks=checks)
