from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import re
from typing import Any


REQUIRED_SOURCE_ARTIFACTS: tuple[tuple[str, Path], ...] = (
    ("paper_ocr", Path("resources/papers/hoodie/ocr/merged.tex")),
    ("mechanism_registry", Path("artifacts/analysis/paper-mechanism-registry/paper-mechanism-registry.json")),
    ("differential_audit", Path("artifacts/analysis/differential-environment-audit/differential-audit.json")),
    ("mechanism_repair_summary", Path("artifacts/analysis/mechanism-repair/repair-summary.json")),
    ("controlled_sweeps", Path("artifacts/analysis/controlled-mechanistic-sweeps/controlled-mechanistic-sweeps.json")),
    ("baseline_fairness_rebuild", Path("artifacts/analysis/baseline-fairness-rebuild/baseline-fairness-rebuild.json")),
    ("baseline_rebuild_sensitivity_audit", Path("artifacts/analysis/baseline-rebuild-sensitivity-audit/baseline-rebuild-sensitivity-audit.json")),
)

_REQUIRED_OCR_PHRASES: tuple[str, ...] = (
    "distributed deep reinforcement learning",
    "distributed drl agents",
    "state input",
    "task features",
    "lstm",
    "double",
    "dueling",
    "double q-learning",
    "singlestep offloading",
    "task latency",
    "drop rate",
    "training",
    "validation",
)


@dataclass(slots=True)
class GateCheck:
    artifact: str
    path: str
    present: bool
    valid: bool
    details: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "artifact": self.artifact,
            "path": self.path,
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


def _artifact_contains_phrases(path: Path, phrases: tuple[str, ...]) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="ignore").lower()
    details: list[str] = []
    for phrase in phrases:
        if phrase.lower() not in text:
            details.append(f"missing evidence phrase: {phrase}")
    return details


def _validate_paper_ocr(path: Path) -> list[str]:
    if not path.exists():
        return [f"missing file: {path}"]
    text = path.read_text(encoding="utf-8", errors="ignore")
    details = _artifact_contains_phrases(path, _REQUIRED_OCR_PHRASES)
    if re.search(r"double[- ]?dqn", text, re.IGNORECASE) is None and "double q-learning" not in text.lower():
        details.append("missing evidence phrase: Double-DQN")
    if re.search(r"dueling", text, re.IGNORECASE) is None:
        details.append("missing evidence phrase: Dueling DQN")
    return details


def _validate_json_artifact(path: Path, *, required_keys: tuple[str, ...]) -> list[str]:
    if not path.exists():
        return [f"missing file: {path}"]
    try:
        payload = _read_json(path)
    except json.JSONDecodeError as exc:
        return [f"invalid JSON: {exc.msg}"]
    details: list[str] = []
    if not isinstance(payload, dict):
        return ["payload is not a JSON object"]
    for key in required_keys:
        if key not in payload:
            details.append(f"missing key: {key}")
    return details


def validate_feature_gates(*paths: Path) -> GateValidationResult:
    if paths and len(paths) != len(REQUIRED_SOURCE_ARTIFACTS):
        raise ValueError("validate_feature_gates expects the required source artifact set in order")

    checks: list[GateCheck] = []
    source_paths = paths or tuple(path for _artifact, path in REQUIRED_SOURCE_ARTIFACTS)
    validators = (
        ("paper_ocr", REQUIRED_SOURCE_ARTIFACTS[0][1], _validate_paper_ocr),
        ("mechanism_registry", REQUIRED_SOURCE_ARTIFACTS[1][1], lambda p: _validate_json_artifact(p, required_keys=("passed", "mechanism_entries", "blocking_gaps"))),
        ("differential_audit", REQUIRED_SOURCE_ARTIFACTS[2][1], lambda p: _validate_json_artifact(p, required_keys=("overall_status", "comparison_results", "findings"))),
        ("mechanism_repair_summary", REQUIRED_SOURCE_ARTIFACTS[3][1], lambda p: _validate_json_artifact(p, required_keys=("feature_id", "repaired_case_id", "repaired_classification", "changed_environment_files"))),
        ("controlled_sweeps", REQUIRED_SOURCE_ARTIFACTS[4][1], lambda p: _validate_json_artifact(p, required_keys=("metadata", "monotonic_checks", "overall_status"))),
        ("baseline_fairness_rebuild", REQUIRED_SOURCE_ARTIFACTS[5][1], lambda p: _validate_json_artifact(p, required_keys=("metadata", "overall_status", "anti_collapse_assessment", "baseline_policies_included"))),
        ("baseline_rebuild_sensitivity_audit", REQUIRED_SOURCE_ARTIFACTS[6][1], lambda p: _validate_json_artifact(p, required_keys=("metadata", "overall_status", "sensitivity_classification", "included_baselines"))),
    )
    for (artifact, expected_path, validator), actual_path in zip(validators, source_paths, strict=True):
        path = actual_path if actual_path is not None else expected_path
        if not path.exists():
            checks.append(GateCheck(artifact, str(path), False, False, [f"missing file: {path}"]))
            continue
        details = validator(path)
        checks.append(GateCheck(artifact, str(path), True, not details, details or ["valid"]))
    return GateValidationResult(passed=all(check.valid for check in checks), checks=checks)
