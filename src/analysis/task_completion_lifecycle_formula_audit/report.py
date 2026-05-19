from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import subprocess
from typing import Any

DEFAULT_OUTPUT_DIR = Path("artifacts/analysis/task-completion-lifecycle-formula-audit")
JSON_FILENAME = "completion-lifecycle-audit-report.json"
MARKDOWN_FILENAME = "completion-lifecycle-audit-report.md"


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _git_output(*args: str) -> str:
    result = subprocess.run(["git", *args], check=True, capture_output=True, text=True)
    return result.stdout.strip()


def _git_status_short() -> list[str]:
    result = subprocess.run(["git", "status", "--short"], check=True, capture_output=True, text=True)
    return [line.rstrip() for line in result.stdout.splitlines() if line.strip()]


def _tracked_dirty_paths() -> list[str]:
    paths: list[str] = []
    for entry in _git_status_short():
        if len(entry) < 4:
            continue
        path = entry[3:].strip()
        if path:
            paths.append(path)
    return paths


@dataclass(frozen=True, slots=True)
class CompletionLifecycleAuditReport:
    feature_id: str
    prerequisite_tags_verified: list[dict[str, Any]]
    prior_feature_gates_verified: list[dict[str, Any]]
    paper_default_runtime_verified: dict[str, Any]
    formula_audit_summary: dict[str, Any]
    hand_calculation_examples: list[dict[str, Any]]
    per_action_lifecycle_results: list[dict[str, Any]]
    lifecycle_breakpoint_summary: dict[str, Any]
    completion_absence_diagnosis: str
    suspected_root_causes: list[str]
    recommended_next_feature: str | None
    runtime_contracts_verified: dict[str, Any]
    reward_timing_contract_verified: bool
    pending_at_horizon_contract_verified: bool
    no_training_started: bool
    no_optimizer_step: bool
    no_replay_training: bool
    no_target_update_execution: bool
    no_dependency_drift: bool
    no_environment_contract_drift: bool
    no_policy_drift: bool
    no_reward_timing_change: bool
    no_timeout_contract_drift: bool
    no_capacity_contract_drift: bool
    no_transmission_contract_drift: bool
    no_curve_fitting: bool
    no_simulator_output_tuning: bool
    no_paper_reproduction_claim: bool
    final_verdict: str

    def __post_init__(self) -> None:
        for name in (
            "no_training_started",
            "no_optimizer_step",
            "no_replay_training",
            "no_target_update_execution",
            "no_dependency_drift",
            "no_environment_contract_drift",
            "no_policy_drift",
            "no_reward_timing_change",
            "no_timeout_contract_drift",
            "no_capacity_contract_drift",
            "no_transmission_contract_drift",
            "no_curve_fitting",
            "no_simulator_output_tuning",
            "no_paper_reproduction_claim",
        ):
            if getattr(self, name) is not True:
                raise ValueError(f"CompletionLifecycleAuditReport.{name} must be true.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "prerequisite_tags_verified": list(self.prerequisite_tags_verified),
            "prior_feature_gates_verified": list(self.prior_feature_gates_verified),
            "paper_default_runtime_verified": dict(self.paper_default_runtime_verified),
            "formula_audit_summary": dict(self.formula_audit_summary),
            "hand_calculation_examples": list(self.hand_calculation_examples),
            "per_action_lifecycle_results": list(self.per_action_lifecycle_results),
            "lifecycle_breakpoint_summary": dict(self.lifecycle_breakpoint_summary),
            "completion_absence_diagnosis": self.completion_absence_diagnosis,
            "suspected_root_causes": list(self.suspected_root_causes),
            "recommended_next_feature": self.recommended_next_feature,
            "runtime_contracts_verified": dict(self.runtime_contracts_verified),
            "reward_timing_contract_verified": self.reward_timing_contract_verified,
            "pending_at_horizon_contract_verified": self.pending_at_horizon_contract_verified,
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
            "no_curve_fitting": self.no_curve_fitting,
            "no_simulator_output_tuning": self.no_simulator_output_tuning,
            "no_paper_reproduction_claim": self.no_paper_reproduction_claim,
            "final_verdict": self.final_verdict,
        }

    def to_markdown(self) -> str:
        payload = self.to_dict()
        lines = [
            "# Completion Lifecycle Audit Report",
            "",
            f"- feature_id: `{payload['feature_id']}`",
            f"- final_verdict: `{payload['final_verdict']}`",
            f"- completion_absence_diagnosis: `{payload['completion_absence_diagnosis']}`",
            f"- recommended_next_feature: `{payload['recommended_next_feature']}`",
            "",
            "## Audit Flags",
        ]
        for key in (
            "no_training_started",
            "no_optimizer_step",
            "no_replay_training",
            "no_target_update_execution",
            "no_dependency_drift",
            "no_environment_contract_drift",
            "no_policy_drift",
            "no_reward_timing_change",
            "no_timeout_contract_drift",
            "no_capacity_contract_drift",
            "no_transmission_contract_drift",
            "no_curve_fitting",
            "no_simulator_output_tuning",
            "no_paper_reproduction_claim",
        ):
            lines.append(f"- **{key}**: `{payload[key]}`")
        lines.extend([
            "",
            "## Formula Audit Summary",
            _json_dump(payload["formula_audit_summary"]).strip(),
            "",
            "## Hand Calculation Examples",
            _json_dump(payload["hand_calculation_examples"]).strip(),
            "",
            "## Per-Action Lifecycle Results",
            _json_dump(payload["per_action_lifecycle_results"]).strip(),
            "",
            "## Lifecycle Breakpoint Summary",
            _json_dump(payload["lifecycle_breakpoint_summary"]).strip(),
            "",
            "## Suspected Root Causes",
        ])
        lines.extend(f"- `{item}`" for item in payload["suspected_root_causes"])
        return "\n".join(lines)


def write_completion_lifecycle_audit_report(report: CompletionLifecycleAuditReport, output_dir: Path | str | None = None) -> tuple[Path, Path]:
    target_dir = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    json_path = target_dir / JSON_FILENAME
    markdown_path = target_dir / MARKDOWN_FILENAME
    json_path.write_text(_json_dump(report.to_dict()), encoding="utf-8")
    markdown_path.write_text(report.to_markdown(), encoding="utf-8")
    return json_path, markdown_path


def build_prerequisite_tags_verified() -> list[dict[str, Any]]:
    dirty_paths = _tracked_dirty_paths()
    pointer_dirty = [path for path in dirty_paths if path == ".specify/feature.json"]
    unrelated_dirty = [path for path in dirty_paths if path != ".specify/feature.json"]
    no_unrelated_dirty_files = len(unrelated_dirty) == 0 and (not dirty_paths or dirty_paths == pointer_dirty)
    dirty_details = "working tree clean except optional pointer" if no_unrelated_dirty_files else "dirty_paths=" + ", ".join(dirty_paths)
    return [
        {"name": "branch", "verified": _git_output("branch", "--show-current") == "043-task-completion-lifecycle-formula-audit", "details": "git branch --show-current == 043-task-completion-lifecycle-formula-audit"},
        {"name": "not_main", "verified": _git_output("branch", "--show-current") != "main", "details": "current branch != main"},
        {"name": "main_equals_origin_main", "verified": _git_output("rev-parse", "main") == _git_output("rev-parse", "origin/main"), "details": "main == origin/main"},
        {"name": "main_equals_feature_042", "verified": _git_output("rev-parse", "main") == _git_output("rev-parse", "042-paper-default-terminal-exposure-probe-complete^{}"), "details": "main == 042-paper-default-terminal-exposure-probe-complete^{}"},
        {"name": "prerequisite_diff_empty", "verified": _git_output("diff", "--name-only", "042-paper-default-terminal-exposure-probe-complete^{}", "main") == "", "details": "diff between 042-paper-default-terminal-exposure-probe-complete^{} and main is empty"},
        {"name": "pointer_not_staged", "verified": _git_output("diff", "--cached", "--name-only", "--", ".specify/feature.json") == "", "details": ".specify/feature.json is not staged"},
        {"name": "pointer_not_in_main_head", "verified": ".specify/feature.json" not in _git_output("diff", "--name-only", "main...HEAD").splitlines(), "details": ".specify/feature.json does not appear in git diff --name-only main...HEAD"},
        {"name": "no_unrelated_dirty_files", "verified": no_unrelated_dirty_files, "details": dirty_details},
    ]


def collect_prior_feature_gates_verified() -> list[dict[str, Any]]:
    features = [
        ("037", "baseline revalidation", "artifacts/analysis/baseline-revalidation-after-runtime-repair/baseline-revalidation-report.json"),
        ("038", "training foundation", "artifacts/analysis/training-foundation-contract/training-foundation-contract-report.json"),
        ("039", "paper HOODIE network", "artifacts/analysis/paper-hoodie-network-implementation/network-implementation-report.json"),
        ("040", "smoke training", "artifacts/analysis/smoke-training/smoke-training-report.json"),
        ("041", "full-training campaign gate", "artifacts/analysis/full-training-reproduction-campaign/training-campaign-report.json"),
        ("042", "paper default terminal exposure", "artifacts/analysis/paper-default-terminal-exposure-probe/terminal-exposure-report.json"),
    ]
    return [{"feature": feature, "name": name, "verified": Path(path).exists(), "details": f"{path} exists"} for feature, name, path in features]


def validate_prerequisite_evidence(prerequisite_tags_verified: list[dict[str, Any]], prior_feature_gates_verified: list[dict[str, Any]]) -> None:
    failed_tags = [entry for entry in prerequisite_tags_verified if not entry["verified"]]
    failed_gates = [entry for entry in prior_feature_gates_verified if not entry["verified"]]
    if failed_tags:
        raise ValueError("Prerequisite tags not verified: " + ", ".join(entry["name"] for entry in failed_tags))
    if failed_gates:
        raise ValueError("Prior feature gates not verified: " + ", ".join(entry["feature"] for entry in failed_gates))
