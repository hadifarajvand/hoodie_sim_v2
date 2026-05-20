from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
from typing import Any

from .config import FEATURE_ID

DEFAULT_OUTPUT_DIR = Path("artifacts/analysis/passive-runtime-lifecycle-trace-instrumentation")
JSON_FILENAME = "lifecycle-trace-instrumentation-report.json"
MARKDOWN_FILENAME = "lifecycle-trace-instrumentation-report.md"


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


@dataclass(frozen=True, slots=True)
class PassiveRuntimeLifecycleTraceReport:
    feature_id: str
    prerequisite_tags_verified: list[dict[str, Any]]
    prior_feature_gates_verified: list[dict[str, Any]]
    instrumentation_scope: dict[str, Any]
    trace_event_schema: dict[str, Any]
    trace_sources: list[dict[str, Any]]
    paper_default_runtime_verified: dict[str, Any]
    behavior_equivalence_checks: list[dict[str, Any]]
    trace_coverage_summary: dict[str, Any]
    lifecycle_trace_sample: list[dict[str, Any]]
    completion_diagnosis_readiness: dict[str, Any]
    runtime_contracts_verified: dict[str, Any]
    reward_timing_contract_verified: bool
    pending_at_horizon_contract_verified: bool
    no_training_started: bool
    no_optimizer_step: bool
    no_replay_training: bool
    no_target_update_execution: bool
    no_dependency_drift: bool
    no_policy_drift: bool
    no_reward_timing_change: bool
    no_timeout_contract_drift: bool
    no_capacity_contract_drift: bool
    no_transmission_contract_drift: bool
    no_action_legality_drift: bool
    no_curve_fitting: bool
    no_simulator_output_tuning: bool
    no_paper_reproduction_claim: bool
    final_verdict: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "prerequisite_tags_verified": list(self.prerequisite_tags_verified),
            "prior_feature_gates_verified": list(self.prior_feature_gates_verified),
            "instrumentation_scope": dict(self.instrumentation_scope),
            "trace_event_schema": dict(self.trace_event_schema),
            "trace_sources": list(self.trace_sources),
            "paper_default_runtime_verified": dict(self.paper_default_runtime_verified),
            "behavior_equivalence_checks": list(self.behavior_equivalence_checks),
            "trace_coverage_summary": dict(self.trace_coverage_summary),
            "lifecycle_trace_sample": list(self.lifecycle_trace_sample),
            "completion_diagnosis_readiness": dict(self.completion_diagnosis_readiness),
            "runtime_contracts_verified": dict(self.runtime_contracts_verified),
            "reward_timing_contract_verified": self.reward_timing_contract_verified,
            "pending_at_horizon_contract_verified": self.pending_at_horizon_contract_verified,
            "no_training_started": self.no_training_started,
            "no_optimizer_step": self.no_optimizer_step,
            "no_replay_training": self.no_replay_training,
            "no_target_update_execution": self.no_target_update_execution,
            "no_dependency_drift": self.no_dependency_drift,
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

    def to_markdown(self) -> str:
        payload = self.to_dict()
        lines = [
            "# Passive Runtime Lifecycle Trace Instrumentation Report",
            "",
            f"- feature_id: `{payload['feature_id']}`",
            f"- final_verdict: `{payload['final_verdict']}`",
            "",
            "## Trace Coverage Summary",
            _json_dump(payload["trace_coverage_summary"]).strip(),
            "",
            "## Behavior Equivalence Checks",
            _json_dump(payload["behavior_equivalence_checks"]).strip(),
            "",
            "## Lifecycle Trace Sample",
            _json_dump(payload["lifecycle_trace_sample"]).strip(),
            "",
        ]
        return "\n".join(lines)


def write_passive_runtime_lifecycle_trace_report(report: PassiveRuntimeLifecycleTraceReport, output_dir: Path | str | None = None) -> tuple[Path, Path]:
    target_dir = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    json_path = target_dir / JSON_FILENAME
    markdown_path = target_dir / MARKDOWN_FILENAME
    json_path.write_text(_json_dump(report.to_dict()), encoding="utf-8")
    markdown_path.write_text(report.to_markdown(), encoding="utf-8")
    return json_path, markdown_path

