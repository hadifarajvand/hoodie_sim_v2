from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
from typing import Any

from .config import FEATURE_ID

DEFAULT_OUTPUT_DIR = Path("artifacts/analysis/load-admission-action-exposure-review")
JSON_FILENAME = "load-admission-action-exposure-report.json"
MARKDOWN_FILENAME = "load-admission-action-exposure-report.md"


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


@dataclass(frozen=True, slots=True)
class LoadAdmissionActionExposureReport:
    feature_id: str
    prerequisite_tags_verified: list[dict[str, Any]]
    prior_feature_gates_verified: list[dict[str, Any]]
    trace_input_sources: list[dict[str, Any]]
    paper_default_runtime_verified: dict[str, Any]
    load_pressure_summary: dict[str, Any]
    admission_serialization_summary: dict[str, Any]
    action_exposure_summary: dict[str, Any]
    queue_pressure_summary: dict[str, Any]
    offload_path_pressure_summary: dict[str, Any]
    budget_comparison_summary: dict[str, Any]
    per_strategy_summary: list[dict[str, Any]]
    per_action_summary: list[dict[str, Any]]
    per_queue_summary: list[dict[str, Any]]
    dominant_pressure_sources: list[dict[str, Any]]
    diagnosis: dict[str, Any]
    recommended_next_feature: str
    no_runtime_repair_performed: bool = True
    no_training_started: bool = True
    no_optimizer_step: bool = True
    no_replay_training: bool = True
    no_target_update_execution: bool = True
    no_dependency_drift: bool = True
    no_environment_contract_drift: bool = True
    no_policy_drift: bool = True
    no_reward_timing_change: bool = True
    no_timeout_contract_drift: bool = True
    no_capacity_contract_drift: bool = True
    no_transmission_contract_drift: bool = True
    no_action_legality_drift: bool = True
    no_curve_fitting: bool = True
    no_simulator_output_tuning: bool = True
    no_paper_reproduction_claim: bool = True
    final_verdict: str = "prerequisite_blocked"

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id mismatch")

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "feature_id": self.feature_id,
            "prerequisite_tags_verified": list(self.prerequisite_tags_verified),
            "prior_feature_gates_verified": list(self.prior_feature_gates_verified),
            "trace_input_sources": list(self.trace_input_sources),
            "paper_default_runtime_verified": dict(self.paper_default_runtime_verified),
            "load_pressure_summary": dict(self.load_pressure_summary),
            "admission_serialization_summary": dict(self.admission_serialization_summary),
            "action_exposure_summary": dict(self.action_exposure_summary),
            "queue_pressure_summary": dict(self.queue_pressure_summary),
            "offload_path_pressure_summary": dict(self.offload_path_pressure_summary),
            "budget_comparison_summary": dict(self.budget_comparison_summary),
            "per_strategy_summary": list(self.per_strategy_summary),
            "per_action_summary": list(self.per_action_summary),
            "per_queue_summary": list(self.per_queue_summary),
            "dominant_pressure_sources": list(self.dominant_pressure_sources),
            "diagnosis": dict(self.diagnosis),
            "recommended_next_feature": self.recommended_next_feature,
            "no_runtime_repair_performed": self.no_runtime_repair_performed,
            "no_training_started": self.no_training_started,
            "no_optimizer_step": self.no_optimizer_step,
            "no_replay_training": self.no_replay_training,
            "no_target_update_execution": self.no_target_update_execution,
            "no_dependency_drift": self.no_dependency_drift,
            "no_environment_contract_drift": self.no_environment_contract_drift,
            "no_policy_drift": self.no_policy_drift,
            "no_reward_timing_change": self.no_reward_timing_change,
            "no_timeout_contract_drift": self.no_timeout_contract_drift,
            "no_capacity_contract_drift": self.no_capacity_contract_drift,
            "no_transmission_contract_drift": self.no_transmission_contract_drift,
            "no_action_legality_drift": self.no_action_legality_drift,
            "no_curve_fitting": self.no_curve_fitting,
            "no_simulator_output_tuning": self.no_simulator_output_tuning,
            "no_paper_reproduction_claim": self.no_paper_reproduction_claim,
            "final_verdict": self.final_verdict,
        }
        return payload

    def to_markdown(self) -> str:
        payload = self.to_dict()
        return "\n".join([
            "# Load Admission Action Exposure Review",
            "",
            f"- feature_id: `{payload['feature_id']}`",
            f"- final_verdict: `{payload['final_verdict']}`",
            f"- recommended_next_feature: `{payload['recommended_next_feature']}`",
            "",
            "## Diagnosis",
            _json_dump(payload["diagnosis"]).strip(),
            "",
            "## Load Pressure",
            _json_dump(payload["load_pressure_summary"]).strip(),
            "",
            "## Admission Serialization",
            _json_dump(payload["admission_serialization_summary"]).strip(),
            "",
            "## Action Exposure",
            _json_dump(payload["action_exposure_summary"]).strip(),
            "",
            "## Queue Pressure",
            _json_dump(payload["queue_pressure_summary"]).strip(),
            "",
            "## Offload Path Pressure",
            _json_dump(payload["offload_path_pressure_summary"]).strip(),
            "",
            "## Budget Comparison",
            _json_dump(payload["budget_comparison_summary"]).strip(),
        ])


def write_load_admission_action_exposure_report(report: LoadAdmissionActionExposureReport, output_dir: Path | str | None = None) -> tuple[Path, Path]:
    target_dir = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    json_path = target_dir / JSON_FILENAME
    md_path = target_dir / MARKDOWN_FILENAME
    json_path.write_text(_json_dump(report.to_dict()), encoding="utf-8")
    md_path.write_text(report.to_markdown(), encoding="utf-8")
    return json_path, md_path
