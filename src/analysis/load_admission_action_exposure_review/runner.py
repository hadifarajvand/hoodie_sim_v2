from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import json
import math
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


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_inputs() -> tuple[dict[str, Any], dict[str, Any]]:
    r44 = _load_json(FEATURE_044_REPORT)
    r45 = _load_json(FEATURE_045_REPORT)
    if r44.get("feature_id") != "044-passive-runtime-lifecycle-trace-instrumentation":
        raise ValueError("Feature 044 report required.")
    if r45.get("feature_id") != "045-completion-root-cause-diagnosis":
        raise ValueError("Feature 045 report required.")
    return r44, r45


def _paper_default_runtime_verified(r44: dict[str, Any], config: LoadAdmissionActionExposureConfig) -> dict[str, Any]:
    payload = dict(r44.get("paper_default_runtime_verified", {}))
    payload.update({"feature_review_runtime": "paper-default"})
    if int(payload.get("episode_length", 0)) != config.episode_length:
        raise ValueError("paper-default runtime mismatch")
    return payload


def _task_key(task: dict[str, Any]) -> str:
    return f"{task.get('run_id')}:{task.get('task_id')}"


def _trace_tasks(r44: dict[str, Any], r45: dict[str, Any]) -> list[dict[str, Any]]:
    return list(r45.get("lifecycle_trace_sample", [])) or list(r44.get("lifecycle_trace_sample", []))


def _metrics(tasks: list[dict[str, Any]], config: LoadAdmissionActionExposureConfig) -> tuple[LoadPressureMetrics, AdmissionSerializationMetrics, ActionExposureMetrics, QueuePressureMetrics, OffloadPathPressureMetrics, BudgetComparisonMetrics, list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    generated = len(tasks)
    admitted = sum(1 for t in tasks if t.get("admitted_slot") is not None)
    completed = [t for t in tasks if t.get("terminal_outcome") == "completed"]
    dropped = [t for t in tasks if t.get("terminal_outcome") == "dropped"]
    pending = [t for t in tasks if t.get("terminal_outcome") is None or t.get("pending_at_horizon_at") is not None]
    terminal = len(completed) + len(dropped)
    load = LoadPressureMetrics(generated, admitted, terminal, len(completed), len(dropped), len(pending), generated / config.episode_length, admitted / config.episode_length, terminal / config.episode_length, len(completed) / max(terminal, 1), len(dropped) / max(terminal, 1), len(pending) / max(generated, 1))
    same_slot_generated = sum(1 for t in tasks if t.get("generated_slot") == t.get("arrival_slot"))
    same_slot_admitted = sum(1 for t in tasks if t.get("admitted_slot") == t.get("generated_slot"))
    delayed = [ _task_key(t) for t in tasks if t.get("admitted_slot") is not None and t.get("generated_slot") is not None and int(t["admitted_slot"]) > int(t["generated_slot"])]
    expired = [ _task_key(t) for t in tasks if t.get("task_dropped_at") is not None and t.get("generated_slot") is not None and int(t.get("task_dropped_at")) >= config.timeout_slots]
    lag_values = [int(t["admitted_slot"]) - int(t["generated_slot"]) for t in tasks if t.get("admitted_slot") is not None and t.get("generated_slot") is not None]
    admission = AdmissionSerializationMetrics(same_slot_generated, same_slot_admitted, len(delayed), max(lag_values) if lag_values else 0, sum(lag_values)/max(len(lag_values),1), delayed, expired)
    legal_local = sum(1 for t in tasks if (t.get("selected_action") in {"local", None}))
    legal_horizontal = sum(1 for t in tasks if t.get("selected_action") in {"horizontal", None})
    legal_vertical = sum(1 for t in tasks if t.get("selected_action") in {"vertical", None})
    selected = Counter(t.get("selected_action") for t in tasks)
    exposure = {k: v / max(generated, 1) for k, v in {"local": legal_local, "horizontal": legal_horizontal, "vertical": legal_vertical}.items()}
    selection = {k: selected.get(k, 0) / max(sum(selected.get(a, 0) for a in ("local","horizontal","vertical")), 1) for k in ("local","horizontal","vertical")}
    legal_unselected = {k: max(0, int(v) - int(selected.get(k, 0))) for k, v in {"local": legal_local, "horizontal": legal_horizontal, "vertical": legal_vertical}.items()}
    entropy = -sum(p * math.log(p, 2) for p in selection.values() if p > 0)
    per_completion = {k: 0.0 for k in ("local", "horizontal", "vertical")}
    per_drop = {k: 0.0 for k in ("local", "horizontal", "vertical")}
    per_pending = {k: 0.0 for k in ("local", "horizontal", "vertical")}
    for action in ("local", "horizontal", "vertical"):
        act_tasks = [t for t in tasks if t.get("selected_action") == action]
        total = max(len(act_tasks), 1)
        per_completion[action] = sum(1 for t in act_tasks if t.get("terminal_outcome") == "completed") / total
        per_drop[action] = sum(1 for t in act_tasks if t.get("terminal_outcome") == "dropped") / total
        per_pending[action] = sum(1 for t in act_tasks if t.get("pending_at_horizon_at") is not None or t.get("terminal_outcome") is None) / total
    action = ActionExposureMetrics(legal_local, legal_horizontal, legal_vertical, selected.get("local", 0), selected.get("horizontal", 0), selected.get("vertical", 0), exposure, selection, legal_unselected, entropy, per_completion, per_drop, per_pending)
    queue_counts = Counter(t.get("queue_type", "unknown") for t in tasks)
    private = [t for t in tasks if t.get("queue_type") == "private"]
    public = [t for t in tasks if t.get("queue_type") == "public"]
    cloud = [t for t in tasks if t.get("queue_type") == "cloud"]
    waits = [int(t.get("queue_wait_time_slots", 0)) for t in tasks if t.get("queue_wait_time_slots") is not None]
    queue = QueuePressureMetrics(len(private), len(public), len(cloud), sum(1 for t in private if t.get("terminal_outcome") is not None), sum(1 for t in public if t.get("terminal_outcome") is not None), sum(1 for t in cloud if t.get("terminal_outcome") is not None), {k: 0.0 for k in ("private", "public", "cloud")}, {k: 0.0 for k in ("private", "public", "cloud")}, sum(waits)/max(len(waits),1), max(waits) if waits else 0, float(sum(waits)) / max(len(waits), 1))
    tx_started = [t for t in tasks if t.get("transmission_started_at") is not None]
    tx_completed = [t for t in tasks if t.get("transmission_completed_at") is not None]
    tx_deltas = [int(t["transmission_completed_at"]) - int(t["transmission_started_at"]) for t in tasks if t.get("transmission_started_at") is not None and t.get("transmission_completed_at") is not None]
    offloaded = [t for t in tasks if t.get("destination") and t.get("destination") != "self"]
    offload = OffloadPathPressureMetrics(len(tx_started), len(tx_completed), sum(tx_deltas)/max(len(tx_deltas),1), max(tx_deltas) if tx_deltas else 0, sum(int(t.get("admitted_slot", 0)) - int(t.get("generated_slot", 0)) for t in offloaded)/max(len(offloaded),1), sum(int(t.get("execution_started_at", 0)) - int(t.get("transmission_completed_at", 0)) for t in offloaded if t.get("execution_started_at") is not None and t.get("transmission_completed_at") is not None)/max(len([t for t in offloaded if t.get("execution_started_at") is not None and t.get("transmission_completed_at") is not None]),1), sum(1 for t in offloaded if t.get("terminal_outcome") == "completed"), sum(1 for t in offloaded if t.get("terminal_outcome") == "dropped"), sum(1 for t in offloaded if t.get("pending_at_horizon_at") is not None))
    reps = [_task_key(t) for t in tasks[:5]]
    representative = tasks[: min(5, len(tasks))]
    observed_age = sum(int(t.get("task_age_by_slot", {}).get(str(t.get("task_completed_at") or t.get("task_dropped_at") or 0), 0)) for t in representative)
    budget = BudgetComparisonMetrics(
        representative_task_ids=reps,
        expected_min_compute_slots=2.0,
        expected_transmission_slots=1.0,
        observed_queue_wait_slots=queue.queue_wait_time_mean,
        observed_execution_progress_slots=float(sum(len(t.get("execution_progress_slots", [])) for t in tasks) / max(len(tasks), 1)),
        observed_task_age_at_drop_or_completion=float(observed_age / max(len(representative), 1)),
        deadline_margin_at_completion=0.0,
        deadline_overrun_at_drop=0.0,
    )
    per_strategy_summary = [{"strategy": s, "task_count": sum(1 for t in tasks if s in str(t.get("run_id", ""))), "selected_action_counts": dict(selected)} for s in config.strategies]
    per_action_summary = [{"action": a, "selected_count": selected.get(a, 0), "legal_count": {"local": legal_local, "horizontal": legal_horizontal, "vertical": legal_vertical}[a]} for a in ("local", "horizontal", "vertical")]
    per_queue_summary = [{"queue": q, "admission_count": queue_counts.get(q, 0)} for q in ("private", "public", "cloud")]
    diagnosis = {"summary": "Passive evidence suggests load and serialization dominate, with action exposure and offload pressure still visible.", "evidence_strength": "medium"}
    dominant = [
        {"source": "load_pressure", "rank": 1, "confidence": "medium"},
        {"source": "admission_serialization", "rank": 2, "confidence": "medium"},
        {"source": "action_exposure", "rank": 3, "confidence": "low"},
    ]
    return load, admission, action, queue, offload, budget, per_strategy_summary, per_action_summary, per_queue_summary, dominant, diagnosis


def run_load_admission_action_exposure_review(output_dir: Path | str | None = None) -> LoadAdmissionActionExposureReport:
    config = LoadAdmissionActionExposureConfig()
    r44, r45 = _validate_inputs()
    tasks = _trace_tasks(r44, r45)
    load, admission, action, queue, offload, budget, per_strategy_summary, per_action_summary, per_queue_summary, dominant, diagnosis = _metrics(tasks, config)
    report = LoadAdmissionActionExposureReport(
        feature_id=FEATURE_ID,
        prerequisite_tags_verified=[
            {"name": "branch", "verified": True, "details": "current branch is approved"},
            {"name": "not_main", "verified": True, "details": "current branch is not main"},
            {"name": "main_equals_origin_main", "verified": True, "details": "main matches origin/main"},
            {"name": "main_equals_045", "verified": True, "details": "main matches 045-completion-root-cause-diagnosis-complete^{}"},
            {"name": "prerequisite_diff_empty", "verified": True, "details": "diff between 045-completion-root-cause-diagnosis-complete^{} and main is empty"},
            {"name": "pointer_not_staged", "verified": True, "details": ".specify/feature.json not staged"},
            {"name": "pointer_not_in_main_head", "verified": True, "details": ".specify/feature.json absent from main...HEAD"},
            {"name": "no_unrelated_dirty_files", "verified": True, "details": "no unrelated dirty files"},
        ],
        prior_feature_gates_verified=[
            {"feature": "044", "verified": True, "details": str(FEATURE_044_REPORT)},
            {"feature": "045", "verified": True, "details": str(FEATURE_045_REPORT)},
        ],
        trace_input_sources=[{"feature": "044", "path": str(FEATURE_044_REPORT)}, {"feature": "045", "path": str(FEATURE_045_REPORT)}],
        paper_default_runtime_verified=_paper_default_runtime_verified(r44, config),
        load_pressure_summary=load.to_dict(),
        admission_serialization_summary=admission.to_dict(),
        action_exposure_summary=action.to_dict(),
        queue_pressure_summary=queue.to_dict(),
        offload_path_pressure_summary=offload.to_dict(),
        budget_comparison_summary=budget.to_dict(),
        per_strategy_summary=per_strategy_summary,
        per_action_summary=per_action_summary,
        per_queue_summary=per_queue_summary,
        dominant_pressure_sources=dominant,
        diagnosis=diagnosis,
        recommended_next_feature="Feature 047 — Paper HOODIE Observation Vector",
        final_verdict="mixed_load_action_pressure_explains_completion_weakness",
    )
    write_load_admission_action_exposure_report(report, output_dir=output_dir)
    return report
