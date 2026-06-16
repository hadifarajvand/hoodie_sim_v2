from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FairnessCheckResult:
    passed: bool
    diagnostics: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {"passed": self.passed, "diagnostics": self.diagnostics}


class FairnessValidationFailure(RuntimeError):
    pass


def _group_by(experiments: list[dict[str, Any]], key_fields: tuple[str, ...]) -> dict[tuple[Any, ...], list[dict[str, Any]]]:
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for row in experiments:
        key = tuple(row.get(field) for field in key_fields)
        grouped.setdefault(key, []).append(row)
    return grouped


def validate_equal_workload(experiments: list[dict[str, Any]], fail_fast: bool = False) -> FairnessCheckResult:
    diagnostics: dict[str, Any] = {"check": "equal_workload", "failures": []}
    grouped = _group_by(experiments, ("scenario", "seed"))
    for (scenario, seed), rows in grouped.items():
        signatures = {row.get("workload_signature") for row in rows}
        if len(signatures) > 1:
            diagnostics["failures"].append(
                {"scenario": scenario, "seed": seed, "reason": "workload_signature mismatch", "values": sorted(str(v) for v in signatures)}
            )
            if fail_fast:
                return FairnessCheckResult(False, diagnostics)
    return FairnessCheckResult(not diagnostics["failures"], diagnostics)


def validate_seed_alignment(experiments: list[dict[str, Any]], fail_fast: bool = False) -> FairnessCheckResult:
    diagnostics: dict[str, Any] = {"check": "seed_alignment", "failures": []}
    grouped = _group_by(experiments, ("scenario", "seed"))
    for (scenario, seed), rows in grouped.items():
        hashes = {row.get("workload_signature") for row in rows}
        if len(hashes) != 1:
            diagnostics["failures"].append({"scenario": scenario, "seed": seed, "reason": "seed/workload mismatch"})
            if fail_fast:
                return FairnessCheckResult(False, diagnostics)
    return FairnessCheckResult(not diagnostics["failures"], diagnostics)


def validate_resource_parity(experiments: list[dict[str, Any]], fail_fast: bool = False) -> FairnessCheckResult:
    diagnostics: dict[str, Any] = {"check": "resource_parity", "failures": []}
    grouped = _group_by(experiments, ("scenario",))
    for scenario, rows in grouped.items():
        signatures = {row.get("resource_signature") for row in rows}
        if len(signatures) > 1:
            diagnostics["failures"].append(
                {"scenario": scenario, "reason": "resource_signature mismatch", "values": sorted(str(v) for v in signatures)}
            )
            if fail_fast:
                return FairnessCheckResult(False, diagnostics)
    return FairnessCheckResult(not diagnostics["failures"], diagnostics)


def run_fairness_validation(experiments: list[dict[str, Any]], fail_fast: bool = True) -> dict[str, Any]:
    checks = [
        validate_equal_workload(experiments, fail_fast=fail_fast),
        validate_seed_alignment(experiments, fail_fast=fail_fast),
        validate_resource_parity(experiments, fail_fast=fail_fast),
    ]
    return {
        "passed": all(check.passed for check in checks),
        "checks": [check.to_dict() for check in checks],
    }


def inject_asymmetric_workload_and_validate(
    experiments: list[dict[str, Any]],
    fail_fast: bool = True,
) -> dict[str, Any]:
    if not experiments:
        raise FairnessValidationFailure("cannot inject adversarial workload into empty experiment set")
    synthetic = [dict(row) for row in experiments]
    if len(synthetic) == 1:
        synthetic.append(dict(synthetic[0]))
    synthetic[0]["workload_signature"] = "adversarial-workload-a"
    synthetic[1]["workload_signature"] = "adversarial-workload-b"
    report = run_fairness_validation(synthetic, fail_fast=fail_fast)
    if report["passed"]:
        raise FairnessValidationFailure("fairness validator did not flag injected workload imbalance")
    return {"passed": False, "report": report, "injected": True}


def fairness_report_from_json(experiments: list[dict[str, Any]]) -> str:
    return json.dumps(run_fairness_validation(experiments), indent=2, sort_keys=True)
