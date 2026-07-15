from __future__ import annotations

from collections import Counter
from pathlib import Path
import json
import subprocess
from typing import Any

from .config import DEFAULT_ARRIVAL_PROBABILITY, DEFAULT_NODE_COUNT, DEFAULT_SEEDS, DEFAULT_STRATEGIES, DEFAULT_TIMEOUT_SLOTS, DEFAULT_EPISODE_LENGTH, ExposureMatrixConfig, FEATURE_ID
from .model import ExposureDecisionRecord, ExposureMatrixMetrics, ExposureMatrixReport, IllegalActionSummary, build_illegal_action_summary
from .report import write_exposure_matrix_report

FEATURE_044_REPORT = Path("artifacts/analysis/passive-runtime-lifecycle-trace-instrumentation/lifecycle-trace-instrumentation-report.json")
FEATURE_045_REPORT = Path("artifacts/analysis/completion-root-cause-diagnosis/completion-root-cause-report.json")
FEATURE_046_REPORT = Path("artifacts/analysis/load-admission-action-exposure-review/load-admission-action-exposure-report.json")

FULL_RECONSTRUCTION_POPULATION = "feature_045_full_reconstruction_summary"
UNAVAILABLE_POPULATION = "unavailable_in_committed_artifacts"
REPRESENTATIVE_POPULATION = "representative_trace_sample"

APPROVED_DIRTY_PATH_PREFIXES = (
    "specs/047-exposure-matrix-review/",
    "src/analysis/exposure_matrix_review/",
    "tests/unit/test_exposure_matrix_schema.py",
    "tests/unit/test_exposure_matrix_metrics.py",
    "tests/integration/test_exposure_matrix_review.py",
    "tests/integration/test_exposure_matrix_report.py",
    "tests/integration/test_exposure_matrix_scope_guard.py",
    "artifacts/analysis/exposure-matrix-review/",
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _git_output(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()


def _is_allowed_dirty_path(path: str) -> bool:
    return path == ".specify/feature.json" or any(path.startswith(prefix) for prefix in APPROVED_DIRTY_PATH_PREFIXES)


def _tracked_dirty_paths() -> list[str]:
    result = subprocess.run(["git", "status", "--short"], check=True, capture_output=True, text=True)
    paths: list[str] = []
    for line in result.stdout.splitlines():
        if len(line) < 4:
            continue
        path = line[3:].strip()
        if path:
            paths.append(path)
    return paths


def _validate_no_unrelated_dirty_files() -> tuple[bool, list[str]]:
    dirty_paths = _tracked_dirty_paths()
    if any(path == "AGENTS.md" or path.endswith("/AGENTS.md") for path in dirty_paths):
        raise RuntimeError("AGENTS.md must be clean before exposure-matrix report generation.")
    unrelated = [path for path in dirty_paths if not _is_allowed_dirty_path(path)]
    if unrelated:
        raise RuntimeError("Dirty paths outside approved Feature 047 paths block report generation: " + ", ".join(unrelated))
    return True, dirty_paths


def _validate_prerequisites() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    _validate_no_unrelated_dirty_files()
    feature_044 = _load_json(FEATURE_044_REPORT)
    feature_045 = _load_json(FEATURE_045_REPORT)
    feature_046 = _load_json(FEATURE_046_REPORT)
    if feature_044.get("feature_id") != "044-passive-runtime-lifecycle-trace-instrumentation":
        raise ValueError("Feature 044 report required.")
    if feature_045.get("feature_id") != "045-completion-root-cause-diagnosis":
        raise ValueError("Feature 045 report required.")
    if feature_046.get("feature_id") != "046-load-admission-action-exposure-review":
        raise ValueError("Feature 046 report required.")
    if feature_045.get("final_verdict") != "root_cause_identified_configuration_or_load_explanation":
        raise ValueError("Feature 045 verdict prerequisite failed.")
    if feature_045.get("recommended_next_feature") != "load/admission/action-exposure review":
        raise ValueError("Feature 045 next-feature prerequisite failed.")
    if feature_046.get("final_verdict") not in {"diagnosis_inconclusive_requires_deeper_exposure_matrix", "exposure_matrix_incomplete_requires_legality_evidence"}:
        raise ValueError("Feature 046 verdict prerequisite failed.")
    return feature_044, feature_045, feature_046


def _paper_default_runtime_verified(feature_044: dict[str, Any], feature_045: dict[str, Any], config: ExposureMatrixConfig) -> dict[str, Any]:
    payload = dict(feature_044.get("paper_default_runtime_verified", {}))
    payload.update(
        {
            "feature_045_report_path": str(FEATURE_045_REPORT),
            "feature_046_report_path": str(FEATURE_046_REPORT),
            "paper_default_probe": True,
            "seeds": list(config.seeds),
            "strategies": list(config.strategies),
            "episode_length": config.episode_length,
            "timeout_slots": config.timeout_slots,
            "node_count": config.node_count,
            "arrival_probability": config.arrival_probability,
        }
    )
    return payload


def _feature_gate_entries() -> list[dict[str, Any]]:
    entries = [
        ("037", "baseline revalidation", "artifacts/analysis/baseline-revalidation-after-runtime-repair/baseline-revalidation-report.json"),
        ("038", "training foundation", "artifacts/analysis/training-foundation-contract/training-foundation-contract-report.json"),
        ("039", "paper HOODIE network", "artifacts/analysis/paper-hoodie-network-implementation/network-implementation-report.json"),
        ("040", "smoke training", "artifacts/analysis/smoke-training/smoke-training-report.json"),
        ("041", "full-training campaign gate", "artifacts/analysis/full-training-reproduction-campaign/training-campaign-report.json"),
        ("042", "paper default terminal exposure", "artifacts/analysis/paper-default-terminal-exposure-probe/terminal-exposure-report.json"),
        ("043", "task completion lifecycle audit", "artifacts/analysis/task-completion-lifecycle-formula-audit/completion-lifecycle-audit-report.json"),
        ("044", "passive runtime lifecycle trace instrumentation", str(FEATURE_044_REPORT)),
        ("045", "completion root-cause diagnosis", str(FEATURE_045_REPORT)),
        ("046", "load/admission/action exposure review", str(FEATURE_046_REPORT)),
    ]
    return [{"feature": feature, "name": name, "verified": Path(path).exists(), "details": f"{path} exists"} for feature, name, path in entries]


def _prerequisite_tags() -> list[dict[str, Any]]:
    dirty_ok, dirty_paths = _validate_no_unrelated_dirty_files()
    return [
        {"name": "branch", "verified": _git_output("branch", "--show-current") == "047-exposure-matrix-review", "details": "git branch --show-current == 047-exposure-matrix-review"},
        {"name": "not_main", "verified": _git_output("branch", "--show-current") != "main", "details": "current branch != main"},
        {"name": "main_equals_origin_main", "verified": _git_output("rev-parse", resolve_git_base_ref()) == _git_output("rev-parse", "origin/main"), "details": "main == origin/main"},
        {"name": "main_equals_feature_046", "verified": _git_output("rev-parse", resolve_git_base_ref()) == _git_output("rev-parse", "046-load-admission-action-exposure-review-complete^{}"), "details": "main == 046-load-admission-action-exposure-review-complete^{}"},
        {"name": "prerequisite_diff_empty", "verified": _git_output("diff", "--name-only", "046-load-admission-action-exposure-review-complete^{}", "main") == "", "details": "diff between 046-load-admission-action-exposure-review-complete^{} and main is empty"},
        {"name": "pointer_not_staged", "verified": _git_output("diff", "--cached", "--name-only", "--", ".specify/feature.json") == "", "details": ".specify/feature.json must not be staged"},
        {"name": "pointer_not_in_main_head", "verified": ".specify/feature.json" not in _git_output("diff", "--name-only", "git_triple_dot_range()").splitlines(), "details": ".specify/feature.json must not appear in git diff --name-only git_triple_dot_range()"},
        {"name": "agents_clean_before_report", "verified": not any(path == "AGENTS.md" or path.endswith("/AGENTS.md") for path in dirty_paths), "details": "AGENTS.md clean before report generation"},
        {"name": "no_unrelated_dirty_files", "verified": dirty_ok, "details": "working tree clean except optional pointer and approved feature artifacts"},
    ]


def _load_feature_045_summary(feature_045: dict[str, Any]) -> dict[str, Any]:
    summary = dict(feature_045.get("task_lifecycle_reconstruction_summary", {}))
    action_counts = summary.get("action_counts", {})
    queue_counts = summary.get("queue_counts", {})
    terminal_counts = summary.get("terminal_counts", {})
    total_tasks = int(summary.get("total_tasks", 0))
    completed = int(summary.get("completed_count", 0))
    dropped = int(summary.get("dropped_count", 0))
    pending = int(summary.get("pending_at_horizon_count", 0))
    return {
        "generated_task_count": total_tasks,
        "admitted_task_count": total_tasks,
        "selected_action_count": total_tasks,
        "terminal_task_count": completed + dropped,
        "completed_task_count": completed,
        "dropped_task_count": dropped,
        "pending_at_horizon_count": pending,
        "selected_local_count": int(action_counts.get("local", 0)),
        "selected_horizontal_count": int(action_counts.get("horizontal", 0)) if "horizontal" in action_counts else None,
        "selected_vertical_count": int(action_counts.get("vertical", 0)) if "vertical" in action_counts else None,
        "private_queue_admission_count": int(queue_counts.get("private", 0)) if "private" in queue_counts else None,
        "public_queue_admission_count": int(queue_counts.get("public", 0)) if "public" in queue_counts else None,
        "cloud_queue_admission_count": int(queue_counts.get("cloud", 0)) if "cloud" in queue_counts else None,
        "terminal_counts": dict(terminal_counts),
    }


def _null_metrics(population: str) -> dict[str, Any]:
    return {
        "evidence_population": population,
        "decision_opportunity_count": None,
        "generated_task_count": None,
        "admitted_task_count": None,
        "selected_action_count": None,
        "terminal_task_count": None,
        "completed_task_count": None,
        "dropped_task_count": None,
        "pending_at_horizon_count": None,
        "legal_local_count": None,
        "legal_horizontal_count": None,
        "legal_vertical_count": None,
        "selected_local_count": None,
        "selected_horizontal_count": None,
        "selected_vertical_count": None,
        "selected_illegal_local_count": None,
        "selected_illegal_horizontal_count": None,
        "selected_illegal_vertical_count": None,
        "legal_but_unselected_local_count": None,
        "legal_but_unselected_horizontal_count": None,
        "legal_but_unselected_vertical_count": None,
        "selected_illegal_action_count": None,
        "selected_illegal_action_examples": [],
        "selected_illegal_action_rate": None,
        "action_entropy": None,
        "per_action_completion_rate": {"local": None, "horizontal": None, "vertical": None},
        "per_action_drop_rate": {"local": None, "horizontal": None, "vertical": None},
        "per_action_pending_rate": {"local": None, "horizontal": None, "vertical": None},
        "per_action_mean_wait_slots": {"local": None, "horizontal": None, "vertical": None},
        "per_action_mean_execution_progress_slots": {"local": None, "horizontal": None, "vertical": None},
        "per_action_mean_task_age_at_terminal": {"local": None, "horizontal": None, "vertical": None},
        "private_queue_admission_count": None,
        "public_queue_admission_count": None,
        "cloud_queue_admission_count": None,
        "offloaded_transmission_started_count": None,
        "offloaded_transmission_completed_count": None,
        "offloaded_completed_count": None,
        "offloaded_dropped_count": None,
        "offloaded_pending_count": None,
    }


def _illegal_action_summary() -> IllegalActionSummary:
    return IllegalActionSummary(
        selected_illegal_action_count=None,
        selected_illegal_local_count=None,
        selected_illegal_horizontal_count=None,
        selected_illegal_vertical_count=None,
        selected_illegal_action_examples=[],
        selected_illegal_action_rate=None,
        evidence_status="unavailable",
    )


def _exposure_bias_summary(load_summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "load_dominant": True,
        "action_exposure_measurable": False,
        "offload_underexposure_measurable": False,
        "load_pressure_reference": {
            "generated_task_count": load_summary["generated_task_count"],
            "completed_task_count": load_summary["completed_task_count"],
            "dropped_task_count": load_summary["dropped_task_count"],
        },
        "legal_action_evidence_status": "unavailable_in_committed_artifacts",
    }


def _load_vs_exposure_summary(load_summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "load_pressure_explains_completion_weakness": True,
        "action_exposure_evidence_status": "unavailable_in_committed_artifacts",
        "queue_pressure_evidence_status": "unavailable_in_committed_artifacts",
        "offload_path_pressure_evidence_status": "unavailable_in_committed_artifacts",
        "selected_illegal_action_count": None,
        "load_pressure_summary": {
            "generated_task_count": load_summary["generated_task_count"],
            "completed_task_count": load_summary["completed_task_count"],
            "dropped_task_count": load_summary["dropped_task_count"],
            "pending_at_horizon_count": load_summary["pending_at_horizon_count"],
            "evidence_population": FULL_RECONSTRUCTION_POPULATION,
        },
    }


def _matrix_completeness_summary() -> dict[str, Any]:
    return {
        "status": "incomplete",
        "reason": "legal action evidence unavailable in committed artifacts",
        "evidence_coverage_ratio": 0.0,
        "sample_usage_policy": "representative examples only; no aggregate derivation from lifecycle_trace_sample",
    }


def _dominant_exposure_findings(load_summary: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "source": "load_pressure",
            "rank": 1,
            "confidence": "high",
            "evidence_population": FULL_RECONSTRUCTION_POPULATION,
            "details": {
                "generated_task_count": load_summary["generated_task_count"],
                "completed_task_count": load_summary["completed_task_count"],
                "dropped_task_count": load_summary["dropped_task_count"],
            },
        },
        {
            "source": "admission_serialization",
            "rank": 2,
            "confidence": "high",
            "evidence_population": UNAVAILABLE_POPULATION,
            "details": "aggregate admission serialization evidence unavailable in committed artifacts",
        },
        {
            "source": "action_exposure_unavailable",
            "rank": 3,
            "confidence": "unknown",
            "evidence_population": UNAVAILABLE_POPULATION,
            "details": "legal-vs-selected exposure evidence unavailable in committed artifacts",
        },
        {
            "source": "queue_pressure_unavailable",
            "rank": 4,
            "confidence": "unknown",
            "evidence_population": UNAVAILABLE_POPULATION,
            "details": "queue pressure aggregate evidence unavailable in committed artifacts",
        },
        {
            "source": "offload_path_pressure_unavailable",
            "rank": 5,
            "confidence": "unknown",
            "evidence_population": UNAVAILABLE_POPULATION,
            "details": "offload path aggregate evidence unavailable in committed artifacts",
        },
    ]


def _build_per_strategy_seed_matrix(config: ExposureMatrixConfig) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for strategy in config.strategies:
        for seed in config.seeds:
            rows.append(
                {
                    "strategy": strategy,
                    "seed": seed,
                    "evidence_population": UNAVAILABLE_POPULATION,
                    "decision_opportunity_count": None,
                    "selected_action_count": None,
                    "selected_illegal_action_count": None,
                    "selected_illegal_action_examples": [],
                    "selected_illegal_action_rate": None,
                    "matrix_completeness": "incomplete",
                }
            )
    return rows


def _build_report() -> ExposureMatrixReport:
    config = ExposureMatrixConfig()
    feature_044, feature_045, feature_046 = _validate_prerequisites()
    load_summary = _load_feature_045_summary(feature_045)
    illegal_summary = _illegal_action_summary()
    aggregate_exposure_matrix = {
        "evidence_population": FULL_RECONSTRUCTION_POPULATION,
        "decision_opportunity_count": load_summary["generated_task_count"],
        "generated_task_count": load_summary["generated_task_count"],
        "admitted_task_count": load_summary["admitted_task_count"],
        "selected_action_count": load_summary["selected_action_count"],
        "terminal_task_count": load_summary["terminal_task_count"],
        "completed_task_count": load_summary["completed_task_count"],
        "dropped_task_count": load_summary["dropped_task_count"],
        "pending_at_horizon_count": load_summary["pending_at_horizon_count"],
        "selected_local_count": load_summary["selected_local_count"],
        "selected_horizontal_count": load_summary["selected_horizontal_count"],
        "selected_vertical_count": load_summary["selected_vertical_count"],
        "selected_illegal_action_count": None,
        "selected_illegal_local_count": None,
        "selected_illegal_horizontal_count": None,
        "selected_illegal_vertical_count": None,
        "selected_illegal_action_examples": [],
        "selected_illegal_action_rate": None,
        "legal_local_count": None,
        "legal_horizontal_count": None,
        "legal_vertical_count": None,
        "legal_but_unselected_local_count": None,
        "legal_but_unselected_horizontal_count": None,
        "legal_but_unselected_vertical_count": None,
        "action_entropy": None,
    }
    per_action_outcome_matrix = {
        "evidence_population": UNAVAILABLE_POPULATION,
        "local": {
            "selected_count": None,
            "selected_illegal_action_count": None,
            "completion_rate": None,
            "drop_rate": None,
            "pending_rate": None,
            "mean_wait_slots": None,
            "mean_execution_progress_slots": None,
            "mean_task_age_at_terminal": None,
        },
        "horizontal": {
            "selected_count": None,
            "selected_illegal_action_count": None,
            "completion_rate": None,
            "drop_rate": None,
            "pending_rate": None,
            "mean_wait_slots": None,
            "mean_execution_progress_slots": None,
            "mean_task_age_at_terminal": None,
        },
        "vertical": {
            "selected_count": None,
            "selected_illegal_action_count": None,
            "completion_rate": None,
            "drop_rate": None,
            "pending_rate": None,
            "mean_wait_slots": None,
            "mean_execution_progress_slots": None,
            "mean_task_age_at_terminal": None,
        },
    }
    per_queue_matrix = {
        "evidence_population": UNAVAILABLE_POPULATION,
        "private": {"admission_count": None, "terminal_count": None, "completion_rate": None, "drop_rate": None},
        "public": {"admission_count": None, "terminal_count": None, "completion_rate": None, "drop_rate": None},
        "cloud": {"admission_count": None, "terminal_count": None, "completion_rate": None, "drop_rate": None},
    }
    offload_exposure_matrix = {
        "evidence_population": UNAVAILABLE_POPULATION,
        "transmission_started_count": None,
        "transmission_completed_count": None,
        "offloaded_completed_count": None,
        "offloaded_dropped_count": None,
        "offloaded_pending_count": None,
    }
    report = ExposureMatrixReport(
        feature_id=FEATURE_ID,
        prerequisite_tags_verified=_prerequisite_tags(),
        prior_feature_gates_verified=_feature_gate_entries(),
        paper_default_runtime_verified=_paper_default_runtime_verified(feature_044, feature_045, config),
        exposure_matrix_input_sources=[
            {"feature": "044", "path": str(FEATURE_044_REPORT), "role": "trace-legality-snapshot-source", "available": True},
            {"feature": "045", "path": str(FEATURE_045_REPORT), "role": "full-population-load-summary-source", "available": True},
            {"feature": "046", "path": str(FEATURE_046_REPORT), "role": "prior-exposure-gap-report", "available": True},
        ],
        exposure_matrix_population="feature_045_full_reconstruction_summary_for_load_metrics_only",
        legal_action_evidence_source="unavailable_in_committed_artifacts",
        legal_action_evidence_coverage_ratio=0.0,
        per_strategy_seed_matrix=_build_per_strategy_seed_matrix(config),
        aggregate_exposure_matrix=aggregate_exposure_matrix,
        per_action_outcome_matrix=per_action_outcome_matrix,
        per_queue_matrix=per_queue_matrix,
        offload_exposure_matrix=offload_exposure_matrix,
        illegal_action_summary=illegal_summary,
        exposure_bias_summary=_exposure_bias_summary(load_summary),
        load_vs_exposure_summary=_load_vs_exposure_summary(load_summary),
        matrix_completeness_summary=_matrix_completeness_summary(),
        dominant_exposure_findings=_dominant_exposure_findings(load_summary),
        diagnosis={
            "summary": "Committed Feature 045 aggregate evidence supports a load/admission explanation, but legal-vs-selected exposure evidence is unavailable in the committed artifacts.",
            "dominant_pressure_sources": ["load_pressure", "admission_serialization", "action_exposure_unavailable"],
            "load_pressure_summary_reference": {
                "generated_task_count": load_summary["generated_task_count"],
                "completed_task_count": load_summary["completed_task_count"],
                "dropped_task_count": load_summary["dropped_task_count"],
                "pending_at_horizon_count": load_summary["pending_at_horizon_count"],
            },
            "legal_action_evidence_status": "unavailable",
        },
        recommended_next_feature="legality evidence expansion before Feature 048",
        final_verdict="exposure_matrix_incomplete_requires_legality_evidence",
    )
    return report


def run_exposure_matrix_review(output_dir: Path | str | None = None) -> ExposureMatrixReport:
    report = _build_report()
    write_exposure_matrix_report(report, output_dir=output_dir)
    return report


def build_exposure_matrix_report() -> ExposureMatrixReport:
    return _build_report()


def main(argv: list[str] | None = None) -> int:
    run_exposure_matrix_review()
    return 0
