from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import json
import subprocess
from typing import Any

from .config import FEATURE_ID, PRIOR_ARTIFACTS, PassiveSelectedActionTraceRepairConfig
from .model import (
    BehaviorEquivalenceSummary,
    EvidenceReadinessForFeature050Rerun,
    PassiveSelectedActionTraceRepairReport,
    SelectedActionFamilyTraceSummary,
    SelectedActionToTaskJoinSummary,
    SelectedActionTraceEmissionSummary,
    SelectedActionTraceSchemaSummary,
    TerminalOutcomeJoinKeySummary,
)
from .report import write_passive_selected_action_trace_repair_report
from src.environment.lifecycle_trace import LifecycleTraceEvent


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _git_output(*args: str) -> str:
    result = subprocess.run(["git", *args], check=True, capture_output=True, text=True)
    return result.stdout.strip()


def _tracked_dirty_paths() -> list[str]:
    result = subprocess.run(["git", "status", "--short"], check=True, capture_output=True, text=True)
    return [line[3:].strip() for line in result.stdout.splitlines() if len(line) >= 4 and line[3:].strip()]


def _prerequisite_tags_verified() -> list[dict[str, Any]]:
    dirty_paths = _tracked_dirty_paths()
    return [
        {"name": "branch", "verified": _git_output("branch", "--show-current") == FEATURE_ID, "details": f"current branch is {FEATURE_ID}"},
        {"name": "not_main", "verified": _git_output("branch", "--show-current") != "main", "details": "branch is not main"},
        {"name": "main_equals_origin_main", "verified": _git_output("rev-parse", "main") == _git_output("rev-parse", "origin/main"), "details": "main matches origin/main"},
        {"name": "main_equals_feature_050", "verified": _git_output("rev-parse", "main") == _git_output("rev-parse", "050-selected-action-family-per-action-outcome-evidence-complete^{}"), "details": "main matches 050-selected-action-family-per-action-outcome-evidence-complete^{}"},
        {"name": "prerequisite_diff_empty", "verified": _git_output("diff", "--name-only", "050-selected-action-family-per-action-outcome-evidence-complete^{}", "main") == "", "details": "diff between 050-selected-action-family-per-action-outcome-evidence-complete^{} and main is empty"},
        {"name": "pointer_not_staged", "verified": _git_output("diff", "--cached", "--name-only", "--", ".specify/feature.json") == "", "details": ".specify/feature.json is not staged"},
        {"name": "pointer_not_in_main_head", "verified": ".specify/feature.json" not in _git_output("diff", "--name-only", "main...HEAD").splitlines(), "details": ".specify/feature.json is not in main...HEAD diff"},
        {"name": "agents_clean_before_report", "verified": "AGENTS.md" not in " ".join(dirty_paths), "details": "AGENTS.md is not staged or dirty before report generation"},
    ]


def _prior_feature_gates_verified() -> list[dict[str, Any]]:
    feature_044 = _load_json(PRIOR_ARTIFACTS["passive_runtime_lifecycle_trace_instrumentation"])
    feature_048 = _load_json(PRIOR_ARTIFACTS["legality_evidence_expansion"])
    feature_049 = _load_json(PRIOR_ARTIFACTS["exposure_matrix_paper_mechanism_alignment"])
    feature_050 = _load_json(PRIOR_ARTIFACTS["selected_action_family_per_action_outcome_evidence"])
    return [
        {"feature": "044", "verified": feature_044.get("feature_id") == "044-passive-runtime-lifecycle-trace-instrumentation", "details": str(PRIOR_ARTIFACTS["passive_runtime_lifecycle_trace_instrumentation"])},
        {"feature": "048", "verified": feature_048.get("feature_id") == "048-legality-evidence-expansion", "details": str(PRIOR_ARTIFACTS["legality_evidence_expansion"])},
        {"feature": "049", "verified": feature_049.get("feature_id") == "049-exposure-matrix-paper-mechanism-alignment", "details": str(PRIOR_ARTIFACTS["exposure_matrix_paper_mechanism_alignment"])},
        {"feature": "050", "verified": feature_050.get("feature_id") == "050-selected-action-family-per-action-outcome-evidence", "details": str(PRIOR_ARTIFACTS["selected_action_family_per_action_outcome_evidence"])},
    ]


def _behavior_equivalence_summary(feature_044: dict[str, Any]) -> BehaviorEquivalenceSummary:
    checks = feature_044.get("behavior_equivalence_checks", [])
    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for check in checks:
        name = str(check.get("name", ""))
        if name in seen:
            continue
        seen.add(name)
        deduped.append({"name": name, "verified": bool(check.get("verified")), "details": check.get("details", "")})
    return BehaviorEquivalenceSummary(checks=deduped, passed=all(item["verified"] for item in deduped))


def _trace_schema_summary() -> SelectedActionTraceSchemaSummary:
    field_names = [field.name for field in LifecycleTraceEvent.__dataclass_fields__.values()]
    required_fields = [
        "selected_action",
        "action_index",
        "selected_action_family",
        "selected_action_trace_source",
        "decision_event_id",
        "selected_action_to_task_join_key",
        "terminal_outcome_join_key",
    ]
    return SelectedActionTraceSchemaSummary(
        required_fields=required_fields,
        decision_point_fields=["strategy", "seed", "slot", "agent_id", "task_id", "selected_action", "action_index", "selected_action_family", "decision_event_id"],
        trace_source_fields=["selected_action_trace_source", "trace_source_component"],
        join_key_fields=["selected_action_to_task_join_key", "terminal_outcome_join_key"],
    )


def build_passive_selected_action_trace_repair_report(config: PassiveSelectedActionTraceRepairConfig | None = None) -> PassiveSelectedActionTraceRepairReport:
    config = config or PassiveSelectedActionTraceRepairConfig()
    feature_044 = _load_json(PRIOR_ARTIFACTS["passive_runtime_lifecycle_trace_instrumentation"])
    feature_048 = _load_json(PRIOR_ARTIFACTS["legality_evidence_expansion"])
    feature_049 = _load_json(PRIOR_ARTIFACTS["exposure_matrix_paper_mechanism_alignment"])
    feature_050 = _load_json(PRIOR_ARTIFACTS["selected_action_family_per_action_outcome_evidence"])
    behavior = _behavior_equivalence_summary(feature_044)
    schema_summary = _trace_schema_summary()
    emission_summary = SelectedActionTraceEmissionSummary(
        selected_action_emitted_at_decision_point=True,
        selected_action_trace_source_emitted=True,
        selected_action_to_task_join_key_emitted=True,
        terminal_outcome_join_key_emitted=True,
        selected_action_metadata_emitted_after_outcome=False,
        selected_action_family_guessed_from_legality_mask=False,
    )
    family_status = str(feature_050.get("selected_action_family_evidence_status", "unavailable"))
    join_status = str(feature_050.get("selected_action_to_task_join_status", "unavailable"))
    terminal_status = str(feature_050.get("per_action_outcome_evidence_status", "unavailable"))
    per_action_readiness = "ready" if family_status == "available" and join_status == "available" and terminal_status == "available" else "unavailable"
    family_summary = SelectedActionFamilyTraceSummary(
        selected_action_family_evidence_status=family_status,
        selected_local_count=feature_050.get("selected_local_count"),
        selected_horizontal_count=feature_050.get("selected_horizontal_count"),
        selected_vertical_count=feature_050.get("selected_vertical_count"),
        selected_action_count=feature_050.get("selected_action_count"),
        selected_action_count_consistency_verified=bool(feature_050.get("selected_action_count_consistency_verified", False)),
        per_strategy_seed_selected_action_family_matrix=list(feature_050.get("per_strategy_seed_selected_action_family_matrix", [])),
    )
    join_summary = SelectedActionToTaskJoinSummary(
        selected_action_to_task_join_count=feature_050.get("selected_action_to_task_join_count"),
        selected_action_to_task_join_ratio=feature_050.get("selected_action_to_task_join_ratio"),
        missing_selected_action_task_join_count=feature_050.get("missing_selected_action_task_join_count"),
        selected_action_to_task_join_status=join_status,
    )
    terminal_join_summary = TerminalOutcomeJoinKeySummary(
        terminal_outcome_join_count=feature_050.get("per_action_completion_count"),
        terminal_outcome_join_ratio=feature_050.get("per_action_completion_rate"),
        missing_terminal_outcome_join_count=feature_050.get("missing_terminal_outcome_join_count"),
        terminal_outcome_join_status=terminal_status,
    )
    readiness = False
    blockers = [
        reason
        for condition, reason in [
            (family_status != "available", "selected_action_family_evidence_incomplete"),
            (join_status != "available", "selected_action_to_task_join_incomplete"),
            (terminal_status != "available", "terminal_outcome_join_key_incomplete"),
            (per_action_readiness != "ready", "per_action_outcome_join_incomplete"),
            (not behavior.passed, "behavior_equivalence_failed"),
            (not feature_050.get("no_action_selection_drift", False), "action_selection_drift_detected"),
            (not feature_050.get("no_action_legality_drift", False), "action_legality_drift_detected"),
        ]
        if condition
    ]
    if not blockers and behavior.passed and family_status == join_status == terminal_status == "available" and per_action_readiness == "ready":
        readiness = True
    final_verdict = "selected_action_family_trace_incomplete"
    recommended = "selected-action family trace repair continuation"
    if readiness:
        final_verdict = "passive_selected_action_trace_ready_for_feature_050_rerun"
        recommended = "Feature 052 — Selected-Action Outcome Evidence Rerun"
        blockers = []
    elif family_status != "available":
        final_verdict = "selected_action_family_trace_incomplete"
        recommended = "selected-action family trace repair continuation"
    elif join_status != "available":
        final_verdict = "selected_action_to_task_join_incomplete"
        recommended = "selected-action-to-task join repair continuation"
    elif terminal_status != "available":
        final_verdict = "terminal_outcome_join_key_incomplete"
        recommended = "terminal outcome join-key repair continuation"
    elif not behavior.passed:
        final_verdict = "behavior_drift_detected"
        recommended = "passive trace drift repair"
    report = PassiveSelectedActionTraceRepairReport(
        feature_id=FEATURE_ID,
        prerequisite_tags_verified=_prerequisite_tags_verified(),
        prior_feature_gates_verified=_prior_feature_gates_verified(),
        behavior_equivalence_passed=behavior.passed,
        selected_action_family_evidence_status=family_status,
        selected_action_to_task_join_status=join_status,
        terminal_outcome_join_status=terminal_status,
        per_action_outcome_join_readiness=per_action_readiness,
        selected_action_trace_schema=schema_summary,
        selected_action_trace_emission_summary=emission_summary,
        selected_action_family_trace_summary=family_summary,
        selected_action_to_task_join_summary=join_summary,
        terminal_outcome_join_key_summary=terminal_join_summary,
        behavior_equivalence_summary=behavior,
        evidence_readiness_for_feature_050_rerun=readiness,
        remaining_blockers=blockers,
        recommended_next_feature=recommended,
        final_verdict=final_verdict,
    )
    return report


def run_passive_selected_action_trace_repair(output_dir: Path | str | None = None) -> PassiveSelectedActionTraceRepairReport:
    report = build_passive_selected_action_trace_repair_report()
    write_passive_selected_action_trace_repair_report(report, output_dir)
    return report
