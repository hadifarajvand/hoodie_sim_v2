from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import json
from typing import Any

from src.analysis.reproducibility_bundle import ReproducibilityBundleBuilder, ReproducibilityBundleConfig

from .campaign_config import CampaignConfig
from .matrix_config import EvaluationMatrixConfig
from .matrix_runner import EvaluationMatrixRunner
from .policy_registry import PolicyRegistry
from .scenario_registry import ScenarioRegistry


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _aggregate_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    if not records:
        return {
            "result_count": 0,
            "mean_average_delay": 0.0,
            "mean_drop_ratio": 0.0,
            "total_throughput": 0,
            "total_completed_tasks": 0,
            "total_dropped_tasks": 0,
            "total_tasks": 0,
        }
    count = len(records)
    average_delay = sum(float(record["final_metrics"].get("average_delay", 0.0)) for record in records) / count
    drop_ratio = sum(float(record["final_metrics"].get("drop_ratio", 0.0)) for record in records) / count
    throughput = sum(int(record["final_metrics"].get("throughput", 0)) for record in records)
    completed_tasks = sum(int(record["final_metrics"].get("completed_tasks", 0)) for record in records)
    dropped_tasks = sum(int(record["final_metrics"].get("dropped_tasks", 0)) for record in records)
    total_tasks = sum(int(record["final_metrics"].get("total_tasks", 0)) for record in records)
    return {
        "result_count": count,
        "mean_average_delay": average_delay,
        "mean_drop_ratio": drop_ratio,
        "total_throughput": throughput,
        "total_completed_tasks": completed_tasks,
        "total_dropped_tasks": dropped_tasks,
        "total_tasks": total_tasks,
    }


def _group_records(records: list[dict[str, Any]], field_name: str) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        grouped.setdefault(str(record[field_name]), []).append(record)
    return [
        {
            field_name: key,
            **_aggregate_records(grouped[key]),
        }
        for key in sorted(grouped)
    ]


def _campaign_readme(config: CampaignConfig) -> str:
    return "\n".join(
        [
            "# Baseline Reproduction Campaign",
            "",
            "This campaign orchestrates the evaluation matrix and bundle packaging only.",
            "",
            "## Outputs",
            "",
            "- `campaign-manifest.json`",
            "- `campaign-summary.json`",
            "- `policy-summary.json`",
            "- `scenario-summary.json`",
            "- `determinism-check.json`",
            "- `README.md`",
            "",
            "## Constraints",
            "",
            config.dependency_change_note,
            "No training, plotting, or policy behavior changes are introduced by this campaign.",
            "HoodieGymEnvironment remains lifecycle owner; CampaignRunner is orchestration-only.",
            "",
        ]
    )


@dataclass(slots=True)
class CampaignRunResult:
    campaign_name: str
    matrix_result_count: int
    bundle_output_dir: str
    campaign_output_dir: str
    campaign_artifacts: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "campaign_name": self.campaign_name,
            "matrix_result_count": self.matrix_result_count,
            "bundle_output_dir": self.bundle_output_dir,
            "campaign_output_dir": self.campaign_output_dir,
            "campaign_artifacts": dict(self.campaign_artifacts),
        }


class CampaignRunner:
    def __init__(self, config: CampaignConfig):
        self.config = config

    def _matrix_config(self, matrix_dir: Path) -> EvaluationMatrixConfig:
        return EvaluationMatrixConfig(
            policy_names=self.config.policy_names,
            scenario_names=self.config.scenario_names,
            seeds=self.config.seeds,
            output_dir=matrix_dir,
            episode_length=self.config.episode_length,
            dependency_change_note=self.config.dependency_change_note,
        )

    def _bundle_config(self, matrix_dir: Path, bundle_dir: Path) -> ReproducibilityBundleConfig:
        return ReproducibilityBundleConfig(
            matrix_output_dir=matrix_dir,
            bundle_output_dir=bundle_dir,
            policy_names=self.config.policy_names,
            scenario_names=self.config.scenario_names,
            seeds=self.config.seeds,
            created_at_override=self.config.created_at_override,
            dependency_change_note=self.config.dependency_change_note,
        )

    def _campaign_manifest(
        self,
        matrix_dir: Path,
        bundle_dir: Path,
        campaign_dir: Path,
        matrix_results: list[dict[str, Any]],
        bundle_outputs: dict[str, Path],
        campaign_artifacts: dict[str, Path],
    ) -> dict[str, Any]:
        return {
            "campaign_name": self.config.campaign_name,
            "created_at": self.config.created_at_override,
            "policy_names": list(self.config.policy_names),
            "scenario_names": list(self.config.scenario_names),
            "seeds": list(self.config.seeds),
            "output_dir": str(self.config.output_dir),
            "matrix_output_dir": str(matrix_dir),
            "bundle_output_dir": str(bundle_dir),
            "campaign_output_dir": str(campaign_dir),
            "matrix_result_count": len(matrix_results),
            "expected_run_count": len(self.config.policy_names) * len(self.config.scenario_names) * len(self.config.seeds),
            "bundle_outputs": {name: str(path) for name, path in bundle_outputs.items()},
            "campaign_artifacts": {name: str(path) for name, path in campaign_artifacts.items()},
            "dependency_change_note": self.config.dependency_change_note,
        }

    def _write_campaign_artifacts(
        self,
        campaign_dir: Path,
        matrix_dir: Path,
        bundle_dir: Path,
        matrix_results: list[dict[str, Any]],
        bundle_outputs: dict[str, Path],
    ) -> dict[str, Path]:
        campaign_dir.mkdir(parents=True, exist_ok=True)
        artifacts: dict[str, Path] = {}
        summary = _aggregate_records(matrix_results)
        policy_summary = _group_records(matrix_results, "policy_name")
        scenario_summary = _group_records(matrix_results, "scenario_name")
        artifact_names = sorted(bundle_outputs.keys())
        campaign_manifest_path = campaign_dir / "campaign-manifest.json"
        campaign_summary_path = campaign_dir / "campaign-summary.json"
        policy_summary_path = campaign_dir / "policy-summary.json"
        scenario_summary_path = campaign_dir / "scenario-summary.json"
        determinism_check_path = campaign_dir / "determinism-check.json"
        readme_path = campaign_dir / "README.md"
        artifacts["campaign-manifest.json"] = campaign_manifest_path
        artifacts["campaign-summary.json"] = campaign_summary_path
        artifacts["policy-summary.json"] = policy_summary_path
        artifacts["scenario-summary.json"] = scenario_summary_path
        artifacts["determinism-check.json"] = determinism_check_path
        artifacts["README.md"] = readme_path
        campaign_manifest = self._campaign_manifest(matrix_dir, bundle_dir, campaign_dir, matrix_results, bundle_outputs, artifacts)
        campaign_manifest_path.write_text(_json_dump(campaign_manifest), encoding="utf-8")
        campaign_summary_path.write_text(_json_dump(summary), encoding="utf-8")
        policy_summary_path.write_text(_json_dump(policy_summary), encoding="utf-8")
        scenario_summary_path.write_text(_json_dump(scenario_summary), encoding="utf-8")
        readme_path.write_text(_campaign_readme(self.config), encoding="utf-8")
        determinism_check = {
            "campaign_name": self.config.campaign_name,
            "expected_runs": len(self.config.policy_names) * len(self.config.scenario_names) * len(self.config.seeds),
            "discovered_runs": len(matrix_results),
            "artifact_names": sorted(artifacts.keys()),
            "deterministic_timestamp_used": self.config.created_at_override is not None,
            "passed": len(matrix_results)
            == len(self.config.policy_names) * len(self.config.scenario_names) * len(self.config.seeds)
            and all(path.exists() for name, path in artifacts.items() if name != "determinism-check.json"),
        }
        determinism_check_path.write_text(_json_dump(determinism_check), encoding="utf-8")
        return artifacts

    def run(self) -> dict[str, object]:
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        matrix_dir = self.config.output_dir / "matrix"
        bundle_dir = self.config.output_dir / "bundle"
        campaign_dir = self.config.output_dir / "campaign"

        matrix_config = self._matrix_config(matrix_dir)
        matrix_result = EvaluationMatrixRunner(matrix_config).run()
        matrix_results = list(matrix_result["results"])
        bundle_config = self._bundle_config(matrix_dir, bundle_dir)
        bundle_outputs = ReproducibilityBundleBuilder(bundle_config).build()
        campaign_artifacts = self._write_campaign_artifacts(campaign_dir, matrix_dir, bundle_dir, matrix_results, bundle_outputs)
        result = CampaignRunResult(
            campaign_name=self.config.campaign_name,
            matrix_result_count=int(matrix_result["count"]),
            bundle_output_dir=str(bundle_dir),
            campaign_output_dir=str(campaign_dir),
            campaign_artifacts={name: str(path) for name, path in campaign_artifacts.items()},
        )
        return result.to_dict()
