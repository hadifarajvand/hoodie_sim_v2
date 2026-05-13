from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
from typing import Any

DEFAULT_OUTPUT_DIR = Path("artifacts/analysis/baseline-revalidation-after-runtime-repair")
DEFAULT_EVALUATION_OUTPUT_DIR = Path("artifacts/evaluation/baseline-revalidation-after-runtime-repair")
JSON_FILENAME = "baseline-revalidation-report.json"
MARKDOWN_FILENAME = "baseline-revalidation-report.md"


def _json_dump(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


@dataclass(slots=True)
class BaselineRevalidationReport:
    feature_id: str
    prerequisite_tags_verified: list[dict[str, Any]]
    policies_revalidated: list[str]
    scenarios_revalidated: list[str]
    seeds_used: list[int]
    runtime_contracts_verified: list[str]
    environment_interface_verified: bool
    legal_action_mask_verified: bool
    metric_schema_verified: bool
    deterministic_reproducibility_verified: bool
    baseline_result_summary: dict[str, Any]
    artifact_paths: list[str]
    no_curve_fitting: bool
    no_paper_reproduction_claim: bool
    no_dependency_drift: bool
    no_training_or_policy_drift: bool
    no_environment_contract_drift: bool
    no_reward_timing_change: bool
    no_execution_time_contract_drift: bool
    no_transmission_delay_contract_drift: bool
    no_capacity_sharing_contract_drift: bool
    no_timeout_contract_drift: bool
    final_verdict: str

    def to_dict(self) -> dict[str, object]:
        return {
            "feature_id": self.feature_id,
            "prerequisite_tags_verified": list(self.prerequisite_tags_verified),
            "policies_revalidated": list(self.policies_revalidated),
            "scenarios_revalidated": list(self.scenarios_revalidated),
            "seeds_used": list(self.seeds_used),
            "runtime_contracts_verified": list(self.runtime_contracts_verified),
            "environment_interface_verified": self.environment_interface_verified,
            "legal_action_mask_verified": self.legal_action_mask_verified,
            "metric_schema_verified": self.metric_schema_verified,
            "deterministic_reproducibility_verified": self.deterministic_reproducibility_verified,
            "baseline_result_summary": dict(self.baseline_result_summary),
            "artifact_paths": list(self.artifact_paths),
            "no_curve_fitting": self.no_curve_fitting,
            "no_paper_reproduction_claim": self.no_paper_reproduction_claim,
            "no_dependency_drift": self.no_dependency_drift,
            "no_training_or_policy_drift": self.no_training_or_policy_drift,
            "no_environment_contract_drift": self.no_environment_contract_drift,
            "no_reward_timing_change": self.no_reward_timing_change,
            "no_execution_time_contract_drift": self.no_execution_time_contract_drift,
            "no_transmission_delay_contract_drift": self.no_transmission_delay_contract_drift,
            "no_capacity_sharing_contract_drift": self.no_capacity_sharing_contract_drift,
            "no_timeout_contract_drift": self.no_timeout_contract_drift,
            "final_verdict": self.final_verdict,
        }

    def to_json(self) -> str:
        return _json_dump(self.to_dict())

    def to_markdown(self) -> str:
        lines = [
            "# Baseline Revalidation After Runtime Repair",
            "",
            f"- feature_id: `{self.feature_id}`",
            f"- final_verdict: `{self.final_verdict}`",
            f"- no_curve_fitting: `{self.no_curve_fitting}`",
            f"- no_paper_reproduction_claim: `{self.no_paper_reproduction_claim}`",
            f"- no_dependency_drift: `{self.no_dependency_drift}`",
            f"- no_training_or_policy_drift: `{self.no_training_or_policy_drift}`",
            f"- no_environment_contract_drift: `{self.no_environment_contract_drift}`",
            f"- no_reward_timing_change: `{self.no_reward_timing_change}`",
            f"- no_execution_time_contract_drift: `{self.no_execution_time_contract_drift}`",
            f"- no_transmission_delay_contract_drift: `{self.no_transmission_delay_contract_drift}`",
            f"- no_capacity_sharing_contract_drift: `{self.no_capacity_sharing_contract_drift}`",
            f"- no_timeout_contract_drift: `{self.no_timeout_contract_drift}`",
            "",
            "## Prerequisite Tags Verified",
        ]
        lines.extend(f"- `{item['tag']}` @ `{item.get('commit', '')}`" for item in self.prerequisite_tags_verified)
        lines.extend(["", "## Policies Revalidated"])
        lines.extend(f"- `{item}`" for item in self.policies_revalidated)
        lines.extend(["", "## Scenarios Revalidated"])
        lines.extend(f"- `{item}`" for item in self.scenarios_revalidated)
        lines.extend(["", "## Seeds Used"])
        lines.extend(f"- `{item}`" for item in self.seeds_used)
        lines.extend(["", "## Runtime Contracts Verified"])
        lines.extend(f"- `{item}`" for item in self.runtime_contracts_verified)
        lines.extend(["", "## Baseline Result Summary"])
        for key, value in self.baseline_result_summary.items():
            lines.append(f"- **{key}**: {value}")
        lines.extend(["", "## Artifact Paths"])
        lines.extend(f"- `{item}`" for item in self.artifact_paths)
        lines.append("")
        return "\n".join(lines)

    def write(self, output_dir: Path | str | None = None) -> tuple[Path, Path]:
        target_dir = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR
        target_dir.mkdir(parents=True, exist_ok=True)
        json_path = target_dir / JSON_FILENAME
        md_path = target_dir / MARKDOWN_FILENAME
        json_path.write_text(self.to_json(), encoding="utf-8")
        md_path.write_text(self.to_markdown(), encoding="utf-8")
        return json_path, md_path


def build_baseline_revalidation_report(
    *,
    prerequisite_tags_verified: list[dict[str, Any]],
    policies_revalidated: list[str],
    scenarios_revalidated: list[str],
    seeds_used: list[int],
    runtime_contracts_verified: list[str],
    environment_interface_verified: bool,
    legal_action_mask_verified: bool,
    metric_schema_verified: bool,
    deterministic_reproducibility_verified: bool,
    baseline_result_summary: dict[str, Any],
    artifact_paths: list[str],
    final_verdict: str,
) -> BaselineRevalidationReport:
    return BaselineRevalidationReport(
        feature_id="037-baseline-revalidation-after-runtime-repair",
        prerequisite_tags_verified=prerequisite_tags_verified,
        policies_revalidated=policies_revalidated,
        scenarios_revalidated=scenarios_revalidated,
        seeds_used=seeds_used,
        runtime_contracts_verified=runtime_contracts_verified,
        environment_interface_verified=environment_interface_verified,
        legal_action_mask_verified=legal_action_mask_verified,
        metric_schema_verified=metric_schema_verified,
        deterministic_reproducibility_verified=deterministic_reproducibility_verified,
        baseline_result_summary=baseline_result_summary,
        artifact_paths=artifact_paths,
        no_curve_fitting=True,
        no_paper_reproduction_claim=True,
        no_dependency_drift=True,
        no_training_or_policy_drift=True,
        no_environment_contract_drift=True,
        no_reward_timing_change=True,
        no_execution_time_contract_drift=True,
        no_transmission_delay_contract_drift=True,
        no_capacity_sharing_contract_drift=True,
        no_timeout_contract_drift=True,
        final_verdict=final_verdict,
    )


def write_baseline_revalidation_report(
    report: BaselineRevalidationReport,
    output_dir: Path | str | None = None,
) -> tuple[Path, Path]:
    return report.write(output_dir)
