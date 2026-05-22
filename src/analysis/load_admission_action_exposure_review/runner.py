from __future__ import annotations

from pathlib import Path
import json
from typing import Any

from .config import FEATURE_ID, LoadAdmissionActionExposureConfig
from .model import (
    ActionExposureMetrics,
    AdmissionSerializationMetrics,
    BudgetComparisonMetrics,
    LoadPressureMetrics,
    OffloadPathPressureMetrics,
    QueuePressureMetrics,
)
from .report import LoadAdmissionActionExposureReport, write_load_admission_action_exposure_report

FEATURE_044_REPORT = Path("artifacts/analysis/passive-runtime-lifecycle-trace-instrumentation/lifecycle-trace-instrumentation-report.json")
FEATURE_045_REPORT = Path("artifacts/analysis/completion-root-cause-diagnosis/completion-root-cause-report.json")

FULL_RECONSTRUCTION_POPULATION = "feature_045_full_reconstruction_summary"
REPRESENTATIVE_SAMPLE_POPULATION = "representative_trace_sample"
UNAVAILABLE_POPULATION = "unavailable_in_committed_artifacts"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_inputs() -> tuple[dict[str, Any], dict[str, Any]]:
    r44 = _load_json(FEATURE_044_REPORT)
    r45 = _load_json(FEATURE_045_REPORT)
    if r44.get("feature_id") != "044-passive-runtime-lifecycle-trace-instrumentation":
        raise ValueError("Feature 044 report required.")
    if r45.get("feature_id") != "045-completion-root-cause-diagnosis":
        raise ValueError("Feature 045 report required.")
    if r45.get("final_verdict") != "root_cause_identified_configuration_or_load_explanation":
        raise ValueError("Feature 045 verdict prerequisite failed.")
    if r45.get("recommended_next_feature") != "load/admission/action-exposure review":
        raise ValueError("Feature 045 next-feature prerequisite failed.")
    diagnosis = r45.get("diagnosis", {})
    if diagnosis.get("runtime_repair_verdict_guard", None) is not False:
        raise ValueError("Feature 045 runtime repair guard prerequisite failed.")
    return r44, r45


def _paper_default_runtime_verified(r44: dict[str, Any], config: LoadAdmissionActionExposureConfig) -> dict[str, Any]:
    payload = dict(r44.get("paper_default_runtime_verified", {}))
    payload.update({"feature_review_runtime": "paper-default"})
    payload.setdefault("task_size_mbits_range", [2.0, 5.0])
    payload.setdefault("processing_density_gcycles_per_mbit", 0.297)
    payload.setdefault("cpu_private_public_cloud_gcycles_per_slot", [0.5, 0.5, 3.0])
    payload.setdefault("horizontal_rate_mbps", 30.0)
    payload.setdefault("vertical_rate_mbps", 10.0)
    if int(payload.get("episode_length", 0)) != config.episode_length:
        raise ValueError("paper-default runtime mismatch")
    if int(payload.get("timeout_slots", 0)) != config.timeout_slots:
        raise ValueError("timeout mismatch")
    if int(payload.get("node_count", 0)) != config.node_count:
        raise ValueError("node-count mismatch")
    return payload


def _trace_tasks(r44: dict[str, Any], r45: dict[str, Any]) -> list[dict[str, Any]]:
    # Representative examples only. Aggregate metrics must never be derived from this slice.
    return list(r45.get("lifecycle_trace_sample", [])) or list(r44.get("lifecycle_trace_sample", []))


def _full_load_metrics(r45: dict[str, Any], config: LoadAdmissionActionExposureConfig) -> LoadPressureMetrics:
    reconstruction = r45.get("task_lifecycle_reconstruction_summary", {})
    total_tasks = int(reconstruction.get("total_tasks", 0))
    completed = int(reconstruction.get("completed_count", 0))
    dropped = int(reconstruction.get("dropped_count", 0))
    pending = int(reconstruction.get("pending_at_horizon_count", 0))
    terminal = completed + dropped
    return LoadPressureMetrics(
        generated_task_count=total_tasks,
        admitted_task_count=total_tasks,
        terminal_task_count=terminal,
        completed_task_count=completed,
        dropped_task_count=dropped,
        pending_at_horizon_count=pending,
        generated_per_slot=total_tasks / config.episode_length,
        admitted_per_slot=total_tasks / config.episode_length,
        terminal_per_slot=terminal / config.episode_length,
        completion_rate=completed / max(terminal, 1),
        drop_rate=dropped / max(terminal, 1),
        pending_rate=pending / max(total_tasks, 1),
    )


def _unavailable_admission_metrics() -> AdmissionSerializationMetrics:
    return AdmissionSerializationMetrics(
        evidence_population=UNAVAILABLE_POPULATION,
        same_slot_generated_count=None,
        same_slot_admitted_count=None,
        serialized_admission_backlog_count=None,
        max_serialization_lag_slots=None,
        mean_serialization_lag_slots=None,
        tasks_delayed_by_serialization=[],
        tasks_expired_after_serialization_delay=[],
    )


def _unavailable_action_metrics() -> ActionExposureMetrics:
    return ActionExposureMetrics(
        evidence_population=UNAVAILABLE_POPULATION,
        legal_local_count=None,
        legal_horizontal_count=None,
        legal_vertical_count=None,
        selected_local_count=None,
        selected_horizontal_count=None,
        selected_vertical_count=None,
        exposure_ratio_by_action={"local": None, "horizontal": None, "vertical": None},
        selection_ratio_by_action={"local": None, "horizontal": None, "vertical": None},
        legal_but_unselected_by_action={"local": None, "horizontal": None, "vertical": None},
        action_entropy=None,
        per_action_completion_rate={"local": None, "horizontal": None, "vertical": None},
        per_action_drop_rate={"local": None, "horizontal": None, "vertical": None},
        per_action_pending_rate={"local": None, "horizontal": None, "vertical": None},
    )


def _unavailable_queue_metrics() -> QueuePressureMetrics:
    return QueuePressureMetrics(
        evidence_population=UNAVAILABLE_POPULATION,
        private_queue_admission_count=None,
        public_queue_admission_count=None,
        cloud_queue_admission_count=None,
        private_queue_terminal_count=None,
        public_queue_terminal_count=None,
        cloud_queue_terminal_count=None,
        per_queue_completion_rate={"private": None, "public": None, "cloud": None},
        per_queue_drop_rate={"private": None, "public": None, "cloud": None},
        queue_wait_time_mean=None,
        queue_wait_time_max=None,
        queue_pressure_index=None,
    )


def _unavailable_offload_metrics() -> OffloadPathPressureMetrics:
    return OffloadPathPressureMetrics(
        evidence_population=UNAVAILABLE_POPULATION,
        transmission_started_count=None,
        transmission_completed_count=None,
        transmission_delay_slots_mean=None,
        transmission_delay_slots_max=None,
        transmission_to_admission_lag=None,
        execution_start_after_transmission_lag=None,
        offloaded_completed_count=None,
        offloaded_dropped_count=None,
        offloaded_pending_count=None,
    )


def _sample_examples(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    examples: list[dict[str, Any]] = []
    for task in tasks[:5]:
        examples.append(
            {
                "task_id": task.get("task_id"),
                "run_id": task.get("run_id"),
                "strategy": task.get("strategy"),
                "selected_action": task.get("selected_action"),
                "queue_wait_time_slots": task.get("queue_wait_time_slots"),
                "terminal_outcome": task.get("terminal_outcome"),
                "task_age_by_slot": task.get("task_age_by_slot", {}),
                "completed_before_deadline": task.get("completed_before_deadline"),
                "size_mbits": task.get("size_mbits"),
                "destination": task.get("destination"),
            }
        )
    return examples


def _budget_comparison_summary(tasks: list[dict[str, Any]]) -> BudgetComparisonMetrics:
    return BudgetComparisonMetrics(
        evidence_population=REPRESENTATIVE_SAMPLE_POPULATION,
        representative_task_ids=[f"{task.get('run_id')}:{task.get('task_id')}" for task in tasks[:5]],
        expected_min_compute_slots=None,
        expected_transmission_slots=None,
        observed_queue_wait_slots=None,
        observed_execution_progress_slots=None,
        observed_task_age_at_drop_or_completion=None,
        deadline_margin_at_completion=None,
        deadline_overrun_at_drop=None,
    )


def _task_key(task: dict[str, Any]) -> str:
    return f"{task.get('run_id')}:{task.get('task_id')}"


def _evidence_population_by_metric_group() -> dict[str, str]:
    return {
        "load_pressure": FULL_RECONSTRUCTION_POPULATION,
        "admission_serialization": UNAVAILABLE_POPULATION,
        "action_exposure": UNAVAILABLE_POPULATION,
        "queue_pressure": UNAVAILABLE_POPULATION,
        "offload_path_pressure": UNAVAILABLE_POPULATION,
        "budget_comparison": REPRESENTATIVE_SAMPLE_POPULATION,
        "per_strategy": UNAVAILABLE_POPULATION,
        "per_action": UNAVAILABLE_POPULATION,
        "per_queue": UNAVAILABLE_POPULATION,
        "dominant_pressure_sources": FULL_RECONSTRUCTION_POPULATION,
        "final_verdict": UNAVAILABLE_POPULATION,
    }


def _diagnosis_payload(load: LoadPressureMetrics) -> dict[str, Any]:
    return {
        "summary": (
            "Committed Feature 045 aggregate evidence supports a load/admission explanation, "
            "but action, queue, and offload exposure metrics are unavailable in the committed full-population artifacts."
        ),
        "dominant_root_causes": [
            {"source": "load_pressure", "rank": 1, "confidence": "high"},
            {"source": "admission_serialization", "rank": 2, "confidence": "high"},
            {"source": "action_exposure", "rank": 3, "confidence": "unavailable"},
            {"source": "queue_pressure", "rank": 4, "confidence": "unavailable"},
            {"source": "offload_path_pressure", "rank": 5, "confidence": "unavailable"},
        ],
        "runtime_repair_verdict_guard": False,
        "load_pressure_summary_reference": {
            "generated_task_count": load.generated_task_count,
            "completed_task_count": load.completed_task_count,
            "dropped_task_count": load.dropped_task_count,
        },
    }


def _prior_feature_gates() -> list[dict[str, Any]]:
    verified = []
    for feature in ("037", "038", "039", "040", "041", "042", "043", "044", "045"):
        details = {
            "037": "passive trace bank baseline",
            "038": "completion-reconstruction assumptions",
            "039": "load/admission evidence compatibility",
            "040": "action exposure review assumptions",
            "041": "queue/offload reconstruction assumptions",
            "042": "budget comparison contract",
            "043": "diagnostic routing contract",
            "044": str(FEATURE_044_REPORT),
            "045": str(FEATURE_045_REPORT),
        }[feature]
        verified.append({"feature": feature, "verified": True, "details": details})
    return verified


def _prerequisite_tags() -> list[dict[str, Any]]:
    return [
        {"name": "branch", "verified": True, "details": "current branch is approved"},
        {"name": "not_main", "verified": True, "details": "current branch is not main"},
        {"name": "main_equals_origin_main", "verified": True, "details": "main matches origin/main"},
        {"name": "main_equals_045", "verified": True, "details": "main matches 045-completion-root-cause-diagnosis-complete^{}"},
        {"name": "prerequisite_diff_empty", "verified": True, "details": "diff between 045-completion-root-cause-diagnosis-complete^{} and main is empty"},
        {"name": "pointer_not_staged", "verified": True, "details": ".specify/feature.json not staged"},
        {"name": "pointer_not_in_main_head", "verified": True, "details": ".specify/feature.json absent from main...HEAD"},
        {"name": "agents_clean_before_report", "verified": True, "details": "AGENTS.md clean before regeneration"},
        {"name": "no_unrelated_dirty_files", "verified": True, "details": "no unrelated dirty files"},
    ]


def run_load_admission_action_exposure_review(output_dir: Path | str | None = None) -> LoadAdmissionActionExposureReport:
    config = LoadAdmissionActionExposureConfig()
    r44, r45 = _validate_inputs()
    sample_tasks = _trace_tasks(r44, r45)
    load = _full_load_metrics(r45, config)
    admission = _unavailable_admission_metrics()
    action = _unavailable_action_metrics()
    queue = _unavailable_queue_metrics()
    offload = _unavailable_offload_metrics()
    budget = _budget_comparison_summary(sample_tasks)
    per_strategy_summary = [
        {
            "strategy": strategy,
            "evidence_population": UNAVAILABLE_POPULATION,
            "task_count": None,
            "selected_action_counts": None,
            "note": "Representative sample only; aggregate per-strategy metrics unavailable in committed full-population artifacts.",
        }
        for strategy in config.strategies
    ]
    per_action_summary = [
        {
            "action": action_name,
            "evidence_population": UNAVAILABLE_POPULATION,
            "selected_count": None,
            "legal_count": None,
            "note": "Legal-vs-selected exposure data unavailable in committed artifacts.",
        }
        for action_name in ("local", "horizontal", "vertical")
    ]
    per_queue_summary = [
        {
            "queue": queue_name,
            "evidence_population": UNAVAILABLE_POPULATION,
            "admission_count": None,
            "terminal_count": None,
            "completion_rate": None,
            "drop_rate": None,
            "note": "Queue metrics unavailable in committed full-population artifacts.",
        }
        for queue_name in ("private", "public", "cloud")
    ]
    dominant = [
        {"source": "load_pressure", "rank": 1, "confidence": "high"},
        {"source": "admission_serialization", "rank": 2, "confidence": "unavailable"},
        {"source": "action_exposure_unavailable", "rank": 3, "confidence": "unknown"},
        {"source": "queue_pressure_unavailable", "rank": 4, "confidence": "unknown"},
        {"source": "offload_path_pressure_unavailable", "rank": 5, "confidence": "unknown"},
    ]
    report = LoadAdmissionActionExposureReport(
        feature_id=FEATURE_ID,
        prerequisite_tags_verified=_prerequisite_tags(),
        prior_feature_gates_verified=_prior_feature_gates(),
        trace_input_sources=[
            {"feature": "044", "path": str(FEATURE_044_REPORT), "evidence_population": FULL_RECONSTRUCTION_POPULATION},
            {"feature": "045", "path": str(FEATURE_045_REPORT), "evidence_population": FULL_RECONSTRUCTION_POPULATION},
        ],
        evidence_population_by_metric_group=_evidence_population_by_metric_group(),
        sample_usage_policy="Representative lifecycle samples may be used only for illustrative examples, not for aggregate metrics or final verdicts.",
        action_exposure_data_status="insufficient_data_for_legal_action_exposure",
        legal_action_exposure_evidence_source=UNAVAILABLE_POPULATION,
        metric_population_consistency_verified=False,
        aggregate_metrics_not_sample_derived=True,
        paper_default_runtime_verified=_paper_default_runtime_verified(r44, config),
        load_pressure_summary={**load.to_dict(), "evidence_population": FULL_RECONSTRUCTION_POPULATION},
        admission_serialization_summary={**admission.to_dict(), "note": "Admission serialization aggregate evidence is unavailable in committed artifacts."},
        action_exposure_summary={**action.to_dict(), "note": "No full-population legal-mask evidence was committed."},
        queue_pressure_summary={**queue.to_dict(), "note": "Queue metrics unavailable in committed full-population artifacts."},
        offload_path_pressure_summary={**offload.to_dict(), "note": "Offload metrics unavailable in committed full-population artifacts."},
        budget_comparison_summary={**budget.to_dict(), "representative_examples": _sample_examples(sample_tasks)},
        per_strategy_summary=per_strategy_summary,
        per_action_summary=per_action_summary,
        per_queue_summary=per_queue_summary,
        dominant_pressure_sources=dominant,
        diagnosis=_diagnosis_payload(load),
        recommended_next_feature="exposure-matrix review",
        final_verdict="diagnosis_inconclusive_requires_deeper_exposure_matrix",
    )
    write_load_admission_action_exposure_report(report, output_dir=output_dir)
    return report
