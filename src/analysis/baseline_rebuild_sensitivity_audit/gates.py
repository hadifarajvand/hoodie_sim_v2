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
        return {
            "passed": self.passed,
            "checks": [check.to_dict() for check in self.checks],
        }


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_differential_audit(payload: dict[str, Any]) -> list[str]:
    details: list[str] = []
    if payload.get("overall_status") != "diagnostic":
        details.append("overall_status mismatch")
    comparison_results = payload.get("comparison_results")
    if not isinstance(comparison_results, list) or not comparison_results:
        details.append("comparison_results missing")
    return details


def _validate_repair_summary(payload: dict[str, Any]) -> list[str]:
    details: list[str] = []
    if payload.get("feature_id") != "019":
        details.append("feature_id mismatch")
    if payload.get("repaired_case_id") != "case-timeout-drop":
        details.append("repaired_case_id mismatch")
    if payload.get("repaired_classification") != "assumption_gap":
        details.append("repaired_classification mismatch")
    if payload.get("changed_environment_files") != ["src/environment/deadline_rules.py", "src/environment/environment.py"]:
        details.append("changed_environment_files mismatch")
    if payload.get("environment_wrapper_edited") is not False:
        details.append("environment_wrapper_edited should be false")
    if payload.get("slot_engine_edited") is not False:
        details.append("slot_engine_edited should be false")
    return details


def _validate_controlled_sweeps(payload: dict[str, Any]) -> list[str]:
    details: list[str] = []
    if payload.get("metadata", {}).get("feature_id") != "020-controlled-mechanistic-sweeps":
        details.append("feature_id mismatch")
    overall_status = payload.get("overall_status")
    if overall_status not in {"pass", "warn", "inconclusive", "instrumentation_gap"}:
        details.append("overall_status mismatch")
    monotonic_checks = payload.get("monotonic_checks")
    if not isinstance(monotonic_checks, list) or not monotonic_checks:
        details.append("monotonic_checks missing")
    return details


def _validate_fairness_rebuild(payload: dict[str, Any]) -> list[str]:
    details: list[str] = []
    if payload.get("metadata", {}).get("feature_id") != "021-baseline-fairness-rebuild":
        details.append("feature_id mismatch")
    if payload.get("overall_status") not in {"collapse_reduced", "collapse_unchanged", "collapse_worsened", "inconclusive"}:
        details.append("overall_status mismatch")
    anti = payload.get("anti_collapse_assessment", {})
    if anti.get("status") != "collapse_reduced":
        details.append("anti_collapse_assessment.status mismatch")
    if not payload.get("baseline_policies_included"):
        details.append("missing baseline_policies_included")
    return details


def validate_feature_gates(
    differential_audit_path: Path,
    repair_summary_path: Path,
    controlled_sweeps_path: Path,
    fairness_rebuild_path: Path,
) -> GateValidationResult:
    checks: list[GateCheck] = []

    validators = (
        ("differential_audit", differential_audit_path, _validate_differential_audit),
        ("repair_summary", repair_summary_path, _validate_repair_summary),
        ("controlled_sweeps", controlled_sweeps_path, _validate_controlled_sweeps),
        ("fairness_rebuild", fairness_rebuild_path, _validate_fairness_rebuild),
    )
    for artifact, path, validator in validators:
        if not path.exists():
            checks.append(GateCheck(artifact, False, False, [f"missing file: {path}"]))
            continue
        try:
            payload = _read_json(path)
        except json.JSONDecodeError as exc:
            checks.append(GateCheck(artifact, True, False, [f"invalid JSON: {exc.msg}"]))
            continue
        details = validator(payload)
        checks.append(GateCheck(artifact, True, not details, details or ["valid"]))

    return GateValidationResult(passed=all(check.valid for check in checks), checks=checks)
