from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
from typing import Any, Iterable


FEATURE_NAME = "010-paper-result-reporting-and-reproducibility-artifacts"
LIFECYCLE_GUARDRAIL_NOTE = "HoodieGymEnvironment remains lifecycle owner; artifact packaging is reporting-only."


@dataclass(slots=True)
class ReproducibilityBundleConfig:
    matrix_output_dir: Path
    bundle_output_dir: Path
    policy_names: tuple[str, ...]
    scenario_names: tuple[str, ...]
    seeds: tuple[int, ...]
    created_at_override: str | None
    dependency_change_note: str = "No dependency files changed."

    def __post_init__(self) -> None:
        self.matrix_output_dir = Path(self.matrix_output_dir)
        self.bundle_output_dir = Path(self.bundle_output_dir)
        self.policy_names = tuple(self.policy_names)
        self.scenario_names = tuple(self.scenario_names)
        self.seeds = tuple(self.seeds)
        if not self.policy_names:
            raise ValueError("policy_names must not be empty")
        if not self.scenario_names:
            raise ValueError("scenario_names must not be empty")
        if not self.seeds:
            raise ValueError("seeds must not be empty")
        for seed in self.seeds:
            if not isinstance(seed, int):
                raise TypeError("seeds must contain integers")
        if self.matrix_output_dir == self.bundle_output_dir:
            raise ValueError("matrix_output_dir and bundle_output_dir must differ")


@dataclass(slots=True)
class ArtifactRecord:
    relative_path: str
    kind: str
    sha256: str
    size_bytes: int

    def to_dict(self) -> dict[str, object]:
        return {
            "relative_path": self.relative_path,
            "kind": self.kind,
            "sha256": self.sha256,
            "size_bytes": self.size_bytes,
        }


@dataclass(slots=True)
class ValidationSummary:
    expected_runs: int
    discovered_run_json_files: int
    matrix_summary_exists: bool
    missing_artifacts: list[str]
    passed: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "expected_runs": self.expected_runs,
            "discovered_run_json_files": self.discovered_run_json_files,
            "matrix_summary_exists": self.matrix_summary_exists,
            "missing_artifacts": list(self.missing_artifacts),
            "passed": self.passed,
        }


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


class ReproducibilityBundleBuilder:
    def __init__(self, config: ReproducibilityBundleConfig):
        self.config = config

    def _timestamp(self) -> str:
        if self.config.created_at_override is not None:
            return self.config.created_at_override
        return datetime.now(timezone.utc).isoformat()

    def _expected_run_files(self) -> list[str]:
        return [
            f"{policy}-{scenario}-{seed}.json"
            for policy in self.config.policy_names
            for scenario in self.config.scenario_names
            for seed in self.config.seeds
        ]

    def _source_run_json_paths(self) -> list[Path]:
        return sorted(path for path in self.config.matrix_output_dir.glob("*.json") if path.is_file())

    def _trace_paths(self) -> list[Path]:
        trace_dir = self.config.matrix_output_dir / "traces"
        if not trace_dir.exists():
            return []
        return sorted(path for path in trace_dir.rglob("*") if path.is_file())

    def _matrix_summary_path(self) -> Path:
        return self.config.matrix_output_dir / "matrix-summary.csv"

    def _artifact_records(self) -> list[ArtifactRecord]:
        records: list[ArtifactRecord] = []
        for path in self._source_run_json_paths():
            records.append(
                ArtifactRecord(
                    relative_path=path.relative_to(self.config.matrix_output_dir).as_posix(),
                    kind="run_json",
                    sha256=_file_sha256(path),
                    size_bytes=path.stat().st_size,
                )
            )
        summary_path = self._matrix_summary_path()
        if summary_path.exists():
            records.append(
                ArtifactRecord(
                    relative_path=summary_path.relative_to(self.config.matrix_output_dir).as_posix(),
                    kind="summary_csv",
                    sha256=_file_sha256(summary_path),
                    size_bytes=summary_path.stat().st_size,
                )
            )
        for path in self._trace_paths():
            records.append(
                ArtifactRecord(
                    relative_path=path.relative_to(self.config.matrix_output_dir).as_posix(),
                    kind="trace",
                    sha256=_file_sha256(path),
                    size_bytes=path.stat().st_size,
                )
            )
        return sorted(records, key=lambda record: record.relative_path)

    def _missing_artifacts(self) -> list[str]:
        missing = [
            expected
            for expected in self._expected_run_files()
            if not (self.config.matrix_output_dir / expected).exists()
        ]
        if not self._matrix_summary_path().exists():
            missing.append("matrix-summary.csv")
        return sorted(missing)

    def _validation_summary(self, artifacts: Iterable[ArtifactRecord]) -> ValidationSummary:
        discovered_run_json_files = sum(1 for artifact in artifacts if artifact.kind == "run_json")
        missing_artifacts = self._missing_artifacts()
        passed = not missing_artifacts and discovered_run_json_files == len(self._expected_run_files())
        return ValidationSummary(
            expected_runs=len(self._expected_run_files()),
            discovered_run_json_files=discovered_run_json_files,
            matrix_summary_exists=self._matrix_summary_path().exists(),
            missing_artifacts=missing_artifacts,
            passed=passed,
        )

    def _run_config_snapshot(self) -> dict[str, object]:
        return {
            "feature_name": FEATURE_NAME,
            "matrix_output_dir": str(self.config.matrix_output_dir),
            "policy_names": list(self.config.policy_names),
            "scenario_names": list(self.config.scenario_names),
            "seeds": list(self.config.seeds),
            "created_at_override": self.config.created_at_override,
            "dependency_change_note": self.config.dependency_change_note,
            "lifecycle_guardrail_note": LIFECYCLE_GUARDRAIL_NOTE,
        }

    def _manifest(self, artifacts: list[ArtifactRecord], validation_summary: ValidationSummary) -> dict[str, object]:
        return {
            "feature_name": FEATURE_NAME,
            "created_at": self._timestamp(),
            "policy_names": list(self.config.policy_names),
            "scenario_names": list(self.config.scenario_names),
            "seeds": list(self.config.seeds),
            "artifact_files": [artifact.to_dict() for artifact in artifacts],
            "dependency_change_note": self.config.dependency_change_note,
            "lifecycle_guardrail_note": LIFECYCLE_GUARDRAIL_NOTE,
            "validation_summary": validation_summary.to_dict(),
        }

    def _artifact_index(self, artifacts: list[ArtifactRecord]) -> dict[str, object]:
        return {
            "matrix_output_dir": str(self.config.matrix_output_dir),
            "run_json_files": [artifact.relative_path for artifact in artifacts if artifact.kind == "run_json"],
            "matrix_summary_csv": [artifact.relative_path for artifact in artifacts if artifact.kind == "summary_csv"],
            "trace_files": [artifact.relative_path for artifact in artifacts if artifact.kind == "trace"],
            "all_artifacts": [artifact.relative_path for artifact in artifacts],
        }

    def _readme(self, validation_summary: ValidationSummary) -> str:
        status = "PASS" if validation_summary.passed else "FAIL"
        return "\n".join(
            [
                "# Reproducibility Bundle",
                "",
                "This bundle packages outputs from the evaluation matrix for audit and reproduction.",
                "",
                "## Policies",
                "",
                ", ".join(self.config.policy_names),
                "",
                "## Scenarios",
                "",
                ", ".join(self.config.scenario_names),
                "",
                "## Seeds",
                "",
                ", ".join(str(seed) for seed in self.config.seeds),
                "",
                "## Bundle Contents",
                "",
                "- `manifest.json`",
                "- `run-config.json`",
                "- `artifact-index.json`",
                "- `validation-summary.json`",
                "- `README.md`",
                "",
                "## Validation",
                "",
                f"Status: {status}",
                f"Expected runs: {validation_summary.expected_runs}",
                f"Discovered run JSON files: {validation_summary.discovered_run_json_files}",
                f"Matrix summary exists: {validation_summary.matrix_summary_exists}",
                "",
                "## Constraints",
                "",
                self.config.dependency_change_note,
                LIFECYCLE_GUARDRAIL_NOTE,
                "",
                "No training, plotting, or policy behavior changes are introduced by this bundle.",
                "",
            ]
        )

    def build(self) -> dict[str, Path]:
        self.config.bundle_output_dir.mkdir(parents=True, exist_ok=True)
        artifacts = self._artifact_records()
        validation_summary = self._validation_summary(artifacts)
        outputs = {
            "manifest.json": self.config.bundle_output_dir / "manifest.json",
            "run-config.json": self.config.bundle_output_dir / "run-config.json",
            "artifact-index.json": self.config.bundle_output_dir / "artifact-index.json",
            "validation-summary.json": self.config.bundle_output_dir / "validation-summary.json",
            "README.md": self.config.bundle_output_dir / "README.md",
        }
        outputs["manifest.json"].write_text(_json_dump(self._manifest(artifacts, validation_summary)), encoding="utf-8")
        outputs["run-config.json"].write_text(_json_dump(self._run_config_snapshot()), encoding="utf-8")
        outputs["artifact-index.json"].write_text(_json_dump(self._artifact_index(artifacts)), encoding="utf-8")
        outputs["validation-summary.json"].write_text(_json_dump(validation_summary.to_dict()), encoding="utf-8")
        outputs["README.md"].write_text(self._readme(validation_summary), encoding="utf-8")
        return outputs

    def package(self) -> dict[str, object]:
        outputs = self.build()
        return {"bundle_output_dir": str(self.config.bundle_output_dir), "outputs": {name: str(path) for name, path in outputs.items()}}
