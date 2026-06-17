from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import subprocess
from typing import Any

from .config import FEATURE_ID
from .model import RootCauseEvaluation

RUNTIME_FAULT_CLASSES: tuple[str, ...] = (
    "completion_emitted_but_reward_or_counter_path_wrong",
    "deadline_drop_ordering_issue",
    "formula_unit_mismatch",
)

DEFAULT_OUTPUT_DIR = Path("artifacts/analysis/completion-root-cause-diagnosis")
JSON_FILENAME = "completion-root-cause-report.json"
MARKDOWN_FILENAME = "completion-root-cause-report.md"

APPROVED_DIRTY_PATH_PREFIXES: tuple[str, ...] = (
    "specs/045-completion-root-cause-diagnosis/",
    "src/analysis/completion_root_cause_diagnosis/",
    "tests/unit/test_completion_root_cause_schema.py",
    "tests/unit/test_completion_root_cause_classifiers.py",
    "tests/integration/test_completion_root_cause_diagnosis.py",
    "tests/integration/test_completion_root_cause_report.py",
    "tests/integration/test_completion_root_cause_scope_guard.py",
    "artifacts/analysis/passive-runtime-lifecycle-trace-instrumentation/",
    "artifacts/analysis/task-completion-lifecycle-formula-audit/",
    "artifacts/analysis/completion-root-cause-diagnosis/",
)


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _git_output(*args: str) -> str:
    result = subprocess.run(["git", *args], check=True, capture_output=True, text=True)
    return result.stdout.strip()


def _tracked_dirty_paths() -> list[str]:
    result = subprocess.run(["git", "status", "--short", "--untracked-files=no"], check=True, capture_output=True, text=True)
    paths: list[str] = []
    for line in result.stdout.splitlines():
        if len(line) < 4:
            continue
        path = line[3:].strip()
        if path:
            paths.append(path)
    return paths


def _is_allowed_dirty_path(path: str) -> bool:
    if path == ".specify/feature.json":
        return True
    return any(path.startswith(prefix) for prefix in APPROVED_DIRTY_PATH_PREFIXES)


def _validate_no_unrelated_dirty_files() -> tuple[bool, list[str]]:
    dirty_paths = _tracked_dirty_paths()
    unrelated = [path for path in dirty_paths if not _is_allowed_dirty_path(path)]
    if any(path == "AGENTS.md" or path.endswith("/AGENTS.md") for path in dirty_paths):
        raise RuntimeError("AGENTS.md must be clean before completion-root-cause report generation.")
    if unrelated:
        raise RuntimeError("Dirty paths outside approved Feature 045 paths block report generation: " + ", ".join(unrelated))
    return True, dirty_paths


def build_prerequisite_tags_verified() -> list[dict[str, Any]]:
    no_unrelated_dirty_files, dirty_paths = _validate_no_unrelated_dirty_files()
    return [
        {"name": "branch", "verified": _git_output("branch", "--show-current") == "045-completion-root-cause-diagnosis", "details": "git branch --show-current == 045-completion-root-cause-diagnosis"},
        {"name": "not_main", "verified": _git_output("branch", "--show-current") != "main", "details": "current branch != main"},
        {"name": "main_equals_origin_main", "verified": _git_output("rev-parse", "main") == _git_output("rev-parse", "origin/main"), "details": "main == origin/main"},
        {"name": "main_equals_feature_044", "verified": _git_output("rev-parse", "main") == _git_output("rev-parse", "044-passive-runtime-lifecycle-trace-instrumentation-complete^{}"), "details": "main == 044-passive-runtime-lifecycle-trace-instrumentation-complete^{}"},
        {"name": "prerequisite_diff_empty", "verified": _git_output("diff", "--name-only", "044-passive-runtime-lifecycle-trace-instrumentation-complete^{}", "main") == "", "details": "diff between 044-passive-runtime-lifecycle-trace-instrumentation-complete^{} and main is empty"},
        {"name": "pointer_not_staged", "verified": _git_output("diff", "--cached", "--name-only", "--", ".specify/feature.json") == "", "details": ".specify/feature.json must not be staged"},
        {"name": "pointer_not_in_main_head", "verified": ".specify/feature.json" not in _git_output("diff", "--name-only", "main...HEAD").splitlines(), "details": ".specify/feature.json must not appear in git diff --name-only main...HEAD"},
        {"name": "no_unrelated_dirty_files", "verified": no_unrelated_dirty_files, "details": "working tree clean except optional pointer" if no_unrelated_dirty_files else f"dirty_paths={', '.join(dirty_paths)}"},
    ]


def collect_prior_feature_gates_verified() -> list[dict[str, Any]]:
    features = [
        ("037", "baseline revalidation", "artifacts/analysis/baseline-revalidation-after-runtime-repair/baseline-revalidation-report.json"),
        ("038", "training foundation", "artifacts/analysis/training-foundation-contract/training-foundation-contract-report.json"),
        ("039", "paper HOODIE network", "artifacts/analysis/paper-hoodie-network-implementation/network-implementation-report.json"),
        ("040", "smoke training", "artifacts/analysis/smoke-training/smoke-training-report.json"),
        ("041", "full-training campaign gate", "artifacts/analysis/full-training-reproduction-campaign/training-campaign-report.json"),
        ("042", "paper default terminal exposure", "artifacts/analysis/paper-default-terminal-exposure-probe/terminal-exposure-report.json"),
        ("043", "task completion lifecycle audit", "artifacts/analysis/task-completion-lifecycle-formula-audit/completion-lifecycle-audit-report.json"),
        ("044", "passive runtime lifecycle trace instrumentation", "artifacts/analysis/passive-runtime-lifecycle-trace-instrumentation/lifecycle-trace-instrumentation-report.json"),
    ]
    return [{"feature": feature, "name": name, "verified": Path(path).exists(), "details": f"{path} exists"} for feature, name, path in features]


@dataclass(frozen=True, slots=True)
class CompletionRootCauseReport:
    feature_id: str
    prerequisite_tags_verified: list[dict[str, Any]]
    prior_feature_gates_verified: list[dict[str, Any]]
    trace_input_sources: list[dict[str, Any]]
    paper_default_runtime_verified: dict[str, Any]
    task_lifecycle_reconstruction_summary: dict[str, Any]
    root_cause_evaluations: list[dict[str, Any]]
    dominant_root_causes: list[dict[str, Any]]
    per_action_root_cause_summary: list[dict[str, Any]]
    per_queue_root_cause_summary: list[dict[str, Any]]
    formula_consistency_summary: dict[str, Any]
    deadline_ordering_summary: dict[str, Any]
    reward_counter_path_summary: dict[str, Any]
    diagnosis: dict[str, Any]
    recommended_next_feature: str
    lifecycle_trace_sample: list[dict[str, Any]]
    trace_coverage_summary: dict[str, Any]
    no_runtime_repair_performed: bool
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
    no_action_legality_drift: bool
    no_curve_fitting: bool
    no_simulator_output_tuning: bool
    no_paper_reproduction_claim: bool
    final_verdict: str

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("CompletionRootCauseReport.feature_id must match the feature id.")
        if not all(entry.get("verified") is True for entry in self.prerequisite_tags_verified):
            raise ValueError("All prerequisite tags must be verified.")
        if not all(entry.get("verified") is True for entry in self.prior_feature_gates_verified):
            raise ValueError("All prior feature gates must be verified.")
        if self.final_verdict not in {
            "root_cause_identified_runtime_repair_required",
            "root_cause_identified_configuration_or_load_explanation",
            "root_cause_identified_policy_or_action_exposure_issue",
            "root_cause_identified_formula_unit_mismatch",
            "no_completion_problem_detected",
            "inconclusive_requires_additional_trace_depth",
            "prerequisite_blocked",
        }:
            raise ValueError("CompletionRootCauseReport.final_verdict is invalid.")
        for flag in (
            "no_runtime_repair_performed",
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
            "no_action_legality_drift",
            "no_curve_fitting",
            "no_simulator_output_tuning",
            "no_paper_reproduction_claim",
        ):
            if getattr(self, flag) is not True:
                raise ValueError(f"CompletionRootCauseReport.{flag} must be true.")
        self._validate_verdict_consistency()

    def _root_cause_evaluation_map(self) -> dict[str, dict[str, Any]]:
        return {
            str(entry.get("root_cause_class")): dict(entry)
            for entry in self.root_cause_evaluations
            if entry.get("root_cause_class")
        }

    def _runtime_fault_guard_satisfied(self) -> bool:
        evaluations = self._root_cause_evaluation_map()
        for root_cause_class in RUNTIME_FAULT_CLASSES:
            entry = evaluations.get(root_cause_class)
            if not entry:
                continue
            if entry.get("detected") is True and int(entry.get("evidence_count", 0)) > 0 and entry.get("confidence") in {"medium", "high"}:
                return True
        return False

    def _validate_verdict_consistency(self) -> None:
        verdict = self.final_verdict
        recommendation = self.recommended_next_feature
        load_follow_up = "load/admission/action-exposure review"
        action_follow_up = "observation/exploration/loss sequence"
        runtime_follow_up = "Feature 046 - Runtime Repair for Completion Lifecycle"
        if verdict == "root_cause_identified_runtime_repair_required":
            if not self._runtime_fault_guard_satisfied():
                raise ValueError("Runtime-repair verdict requires detected runtime-fault evidence with non-zero evidence and medium/high confidence.")
            if recommendation != runtime_follow_up:
                raise ValueError("Runtime-repair verdict must recommend Feature 046.")
        elif verdict == "root_cause_identified_configuration_or_load_explanation":
            if recommendation != load_follow_up:
                raise ValueError("Configuration/load verdict must recommend load/admission/action-exposure review.")
        elif verdict == "root_cause_identified_policy_or_action_exposure_issue":
            if recommendation != action_follow_up:
                raise ValueError("Policy/action-exposure verdict must recommend observation/exploration/loss sequence.")
        elif verdict == "root_cause_identified_formula_unit_mismatch":
            if recommendation != load_follow_up:
                raise ValueError("Formula mismatch verdict must recommend load/admission/action-exposure review.")
        elif verdict == "no_completion_problem_detected":
            if recommendation == runtime_follow_up:
                raise ValueError("No-completion verdict must not recommend runtime repair.")
        if verdict != "root_cause_identified_runtime_repair_required" and recommendation == runtime_follow_up:
            raise ValueError("Runtime repair may only be recommended when the verdict is runtime-repair-required.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "prerequisite_tags_verified": list(self.prerequisite_tags_verified),
            "prior_feature_gates_verified": list(self.prior_feature_gates_verified),
            "trace_input_sources": list(self.trace_input_sources),
            "paper_default_runtime_verified": dict(self.paper_default_runtime_verified),
            "task_lifecycle_reconstruction_summary": dict(self.task_lifecycle_reconstruction_summary),
            "root_cause_evaluations": list(self.root_cause_evaluations),
            "dominant_root_causes": list(self.dominant_root_causes),
            "per_action_root_cause_summary": list(self.per_action_root_cause_summary),
            "per_queue_root_cause_summary": list(self.per_queue_root_cause_summary),
            "formula_consistency_summary": dict(self.formula_consistency_summary),
            "deadline_ordering_summary": dict(self.deadline_ordering_summary),
            "reward_counter_path_summary": dict(self.reward_counter_path_summary),
            "diagnosis": dict(self.diagnosis),
            "recommended_next_feature": self.recommended_next_feature,
            "lifecycle_trace_sample": list(self.lifecycle_trace_sample),
            "trace_coverage_summary": dict(self.trace_coverage_summary),
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

    def to_markdown(self) -> str:
        payload = self.to_dict()
        lines = [
            "# Completion Root-Cause Diagnosis Report",
            "",
            f"- feature_id: `{payload['feature_id']}`",
            f"- final_verdict: `{payload['final_verdict']}`",
            f"- recommended_next_feature: `{payload['recommended_next_feature']}`",
            "",
            "## Diagnosis",
            _json_dump(payload["diagnosis"]).strip(),
            "",
            "## Dominant Root Causes",
            _json_dump(payload["dominant_root_causes"]).strip(),
            "",
            "## Root Cause Evaluations",
            _json_dump(payload["root_cause_evaluations"]).strip(),
            "",
            "## Task Lifecycle Reconstruction Summary",
            _json_dump(payload["task_lifecycle_reconstruction_summary"]).strip(),
            "",
            "## Trace Input Sources",
            _json_dump(payload["trace_input_sources"]).strip(),
            "",
        ]
        return "\n".join(lines)


def write_completion_root_cause_report(report: CompletionRootCauseReport, output_dir: Path | str | None = None) -> tuple[Path, Path]:
    target_dir = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    json_path = target_dir / JSON_FILENAME
    markdown_path = target_dir / MARKDOWN_FILENAME
    json_path.write_text(_json_dump(report.to_dict()), encoding="utf-8")
    markdown_path.write_text(report.to_markdown(), encoding="utf-8")
    return json_path, markdown_path
