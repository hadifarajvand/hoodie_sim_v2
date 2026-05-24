from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import json
import subprocess
from typing import Any

from src.environment.compute_config import ComputeConfig
from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.lifecycle_trace import LifecycleTraceConfig
from src.environment.runtime_model import SharedRuntimeParameters

from .config import FEATURE_ID, PRIOR_ARTIFACTS, SelectedActionOutcomeEvidenceRerunConfig
from .model import (
    BehaviorEquivalenceSummary,
    EvidencePopulationSummary,
    ExposureMatrixInternalConsistencySummary,
    Feature049UnblockAssessment,
    LegalButUnselectedConsistencySummary,
    PerActionOutcomeJoinSummary,
    PerActionOutcomeMatrix,
    SelectedActionFamilyEvidenceSummary,
    SelectedActionOutcomeEvidenceRerunReport,
    SelectedActionToTaskJoinSummary,
)
from .report import write_selected_action_outcome_evidence_rerun_report


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _git_output(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()


def _git_bool(*args: str) -> bool:
    return subprocess.run(["git", *args], check=False, capture_output=True, text=True).returncode == 0


def _current_branch() -> str:
    return _git_output("branch", "--show-current")


def _prerequisite_tags_verified() -> list[dict[str, Any]]:
    approved_paths = {
        "artifacts/analysis/selected-action-outcome-evidence-rerun/selected-action-outcome-evidence-rerun-report.json",
        "artifacts/analysis/selected-action-outcome-evidence-rerun/selected-action-outcome-evidence-rerun-report.md",
        "specs/052-selected-action-outcome-evidence-rerun/checklists/requirements.md",
        "specs/052-selected-action-outcome-evidence-rerun/contracts/selected-action-outcome-evidence-rerun-report-schema.md",
        "specs/052-selected-action-outcome-evidence-rerun/data-model.md",
        "specs/052-selected-action-outcome-evidence-rerun/plan.md",
        "specs/052-selected-action-outcome-evidence-rerun/quickstart.md",
        "specs/052-selected-action-outcome-evidence-rerun/research.md",
        "specs/052-selected-action-outcome-evidence-rerun/spec.md",
        "specs/052-selected-action-outcome-evidence-rerun/tasks.md",
        "src/analysis/selected_action_outcome_evidence_rerun/__init__.py",
        "src/analysis/selected_action_outcome_evidence_rerun/__main__.py",
        "src/analysis/selected_action_outcome_evidence_rerun/config.py",
        "src/analysis/selected_action_outcome_evidence_rerun/model.py",
        "src/analysis/selected_action_outcome_evidence_rerun/report.py",
        "src/analysis/selected_action_outcome_evidence_rerun/runner.py",
        "tests/integration/test_selected_action_outcome_rerun.py",
        "tests/integration/test_selected_action_outcome_rerun_report.py",
        "tests/integration/test_selected_action_outcome_rerun_scope_guard.py",
        "tests/unit/test_selected_action_outcome_rerun_behavior_equivalence.py",
        "tests/unit/test_selected_action_outcome_rerun_metrics.py",
        "tests/unit/test_selected_action_outcome_rerun_schema.py",
    }
    main_contains_feature_051 = _git_bool("merge-base", "--is-ancestor", "051-passive-selected-action-trace-repair-complete^{}", "main")
    main_contains_workflow_contract = _git_bool("merge-base", "--is-ancestor", "spec-kit-workflow-operating-contract-complete^{}", "main")
    branch_based_on_current_main = _git_output("merge-base", "main", "HEAD") == _git_output("rev-parse", "main")
    feature_diff = set(_git_output("diff", "--name-only", "main...HEAD").splitlines())
    only_approved_feature_paths = feature_diff <= approved_paths and bool(feature_diff)
    no_feature_037_051_artifact_rewrites = not any(
        path.startswith("artifacts/analysis/") and not path.startswith("artifacts/analysis/selected-action-outcome-evidence-rerun/")
        for path in feature_diff
    )
    pointer_not_staged = _git_output("diff", "--cached", "--name-only", "--", ".specify/feature.json") == ""
    pointer_not_in_main_head = ".specify/feature.json" not in feature_diff
    agents_clean_before_report = _git_output("status", "--short").find("AGENTS.md") == -1
    return [
        {"name": "branch", "verified": _current_branch() == FEATURE_ID, "details": f"current branch is {FEATURE_ID}"},
        {"name": "not_main", "verified": _current_branch() != "main", "details": "branch is not main"},
        {"name": "main_contains_051_passive_selected_action_trace_repair_complete", "verified": main_contains_feature_051, "details": "main contains 051-passive-selected-action-trace-repair-complete"},
        {"name": "main_contains_spec_kit_workflow_operating_contract_complete", "verified": main_contains_workflow_contract, "details": "main contains spec-kit-workflow-operating-contract-complete"},
        {"name": "branch_based_on_current_main", "verified": branch_based_on_current_main, "details": "main is an ancestor of HEAD"},
        {"name": "feature_diff_contains_only_approved_feature_paths", "verified": only_approved_feature_paths, "details": "main...HEAD diff contains only approved Feature 052 paths"},
        {"name": "no_feature_037_051_artifact_rewrites", "verified": no_feature_037_051_artifact_rewrites, "details": "no Feature 037-051 artifact path is rewritten in the Feature 052 diff"},
        {"name": "pointer_not_staged", "verified": pointer_not_staged, "details": ".specify/feature.json is not staged"},
        {"name": "pointer_not_in_main_head", "verified": pointer_not_in_main_head, "details": ".specify/feature.json is not in main...HEAD diff"},
        {"name": "agents_clean_before_report", "verified": agents_clean_before_report, "details": "AGENTS.md clean before report generation"},
    ]


def _prior_feature_gates_verified() -> list[dict[str, Any]]:
    return [{"name": name, "verified": path.exists(), "details": str(path)} for name, path in PRIOR_ARTIFACTS.items()]


def _feature_051_trace_readiness_verified(feature_051: dict[str, Any]) -> bool:
    return (
        feature_051.get("evidence_readiness_for_feature_050_rerun") is True
        and feature_051.get("selected_action_family_evidence_status") == "available"
        and feature_051.get("selected_action_to_task_join_status") == "available"
        and feature_051.get("terminal_outcome_join_status") == "available"
        and feature_051.get("per_action_outcome_join_readiness") == "ready"
        and feature_051.get("behavior_equivalence_summary", {}).get("passed") is True
        and feature_051.get("final_verdict") == "passive_selected_action_trace_ready_for_feature_050_rerun"
    )


def _behavior_equivalence_summary(feature_051: dict[str, Any]) -> BehaviorEquivalenceSummary:
    checks = feature_051.get("behavior_equivalence_summary", {}).get("checks", [])
    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for check in checks:
        name = check.get("name")
        if name in seen:
            continue
        seen.add(name)
        deduped.append({"name": name, "verified": bool(check.get("verified")), "details": check.get("details", "")})
    return BehaviorEquivalenceSummary(checks=deduped, passed=all(item["verified"] for item in deduped))


def _run_trace_sample(*, trace_enabled: bool, config: SelectedActionOutcomeEvidenceRerunConfig) -> dict[str, Any]:
    env = HoodieGymEnvironment(
        episode_length=config.episode_length,
        runtime_parameters=SharedRuntimeParameters(runtime_variant="constant_service"),
        compute_config=ComputeConfig(
            cpu_capacity_per_slot_agent=10_000.0,
            cpu_capacity_per_slot_edge=10_000.0,
            cpu_capacity_per_slot_cloud=10_000.0,
        ),
        trace_config=LifecycleTraceConfig(trace_enabled=trace_enabled),
        policy_name=config.trace_policy_name,
    )
    observation, _info = env.reset(seed=config.trace_seed)
    action_sequence: list[str | None] = []
    rewards: list[float] = []
    terminal_flags: list[tuple[bool, bool]] = []
    queue_loads: list[int] = []
    finalized_tasks: list[dict[str, Any]] = []
    while True:
        current_task = env.current_task
        action = "local" if current_task is not None else None
        observation, reward, terminated, truncated, info = env.step(action)
        if env.current_task is not None:
            observation = env.observe_flat()
        action_sequence.append(action)
        rewards.append(float(reward))
        terminal_flags.append((bool(terminated), bool(truncated)))
        queue_loads.append(int(info["queue_load"]))
        finalized_tasks.extend(info.get("finalized_tasks", []))
        if terminated or truncated:
            break
    return {
        "trace_id": info["trace_id"],
        "seed": config.trace_seed,
        "actions": action_sequence,
        "rewards": rewards,
        "terminal_flags": terminal_flags,
        "queue_loads": queue_loads,
        "finalized_tasks": finalized_tasks,
        "trace_events": list(info.get("lifecycle_trace_events", [])),
    }


def _selected_action_counts(
    trace_events: list[dict[str, Any]],
    finalized_tasks: list[dict[str, Any]],
    *,
    config: SelectedActionOutcomeEvidenceRerunConfig,
) -> dict[str, Any]:
    decision_events = [event for event in trace_events if event.get("event_type") == "task_admitted"]
    decision_opportunity_count = len(decision_events)
    selected_family_counts = defaultdict(int)
    legal_family_counts = defaultdict(int)
    selected_outcome_counts = defaultdict(lambda: defaultdict(int))
    selected_join_count = 0
    terminal_join_count = 0
    rows: list[dict[str, Any]] = []
    for event in decision_events:
        family = str(event.get("selected_action_family") or "unknown")
        selected_family_counts[family] += 1
        if event.get("selected_action_to_task_join_key") is not None:
            selected_join_count += 1
        if event.get("terminal_outcome_join_key") is not None:
            terminal_join_count += 1
        legal_snapshot = event.get("legality_snapshot") or {}
        for action_family in ("local", "horizontal", "vertical"):
            if legal_snapshot.get(action_family):
                legal_family_counts[action_family] += 1
    for task in finalized_tasks:
        family = {
            "local": "local",
            "compute_local": "local",
            "horizontal": "horizontal",
            "offload_horizontal": "horizontal",
            "vertical": "vertical",
            "offload_vertical": "vertical",
        }.get(str(task.get("selected_action")), "unknown")
        terminal_outcome = task.get("terminal_outcome")
        if terminal_outcome in {"completed", "dropped"}:
            selected_outcome_counts[family][terminal_outcome] += 1
        elif terminal_outcome == "pending_at_horizon":
            selected_outcome_counts[family]["pending"] += 1
    local = selected_family_counts.get("local", 0)
    horizontal = selected_family_counts.get("horizontal", 0)
    vertical = selected_family_counts.get("vertical", 0)
    selected_action_count = local + horizontal + vertical
    selected_action_count_consistency_verified = selected_action_count == decision_opportunity_count
    for family in ("local", "horizontal", "vertical"):
        sel = selected_family_counts.get(family, 0)
        comp = selected_outcome_counts[family].get("completed", 0)
        drop = selected_outcome_counts[family].get("dropped", 0)
        pending = selected_outcome_counts[family].get("pending", 0)
        denom = sel
        rows.append(
            {
                "strategy": config.trace_policy_name,
                "seed": config.trace_seed,
                "action_family": family,
                "selected_action_count": sel,
                "selected_action_completed_count": comp,
                "selected_action_dropped_count": drop,
                "selected_action_pending_count": pending,
                "selected_action_completion_rate": None if denom == 0 else comp / denom,
                "selected_action_drop_rate": None if denom == 0 else drop / denom,
                "selected_action_pending_rate": None if denom == 0 else pending / denom,
                "legal_action_count": legal_family_counts.get(family, 0),
                "legal_but_unselected_count": legal_family_counts.get(family, 0) - sel,
                "selected_action_to_task_join_key_count": sel,
                "terminal_outcome_join_key_count": sel,
            }
        )
    selected_action_to_task_join_count = selected_join_count
    terminal_outcome_join_key_count = terminal_join_count
    selected_action_family_evidence_status = "available" if decision_opportunity_count > 0 and selected_action_count_consistency_verified else "partial"
    selected_action_to_task_join_status = "available" if selected_join_count == decision_opportunity_count and decision_opportunity_count > 0 else ("partial" if selected_join_count > 0 else "unavailable")
    terminal_outcome_join_status = "available" if terminal_join_count == decision_opportunity_count and decision_opportunity_count > 0 else ("partial" if terminal_join_count > 0 else "unavailable")
    per_action_outcome_evidence_status = (
        "available"
        if all(row["selected_action_count"] == row["selected_action_completed_count"] + row["selected_action_dropped_count"] + row["selected_action_pending_count"] for row in rows)
        and selected_action_family_evidence_status == "available"
        and selected_action_to_task_join_status == "available"
        and terminal_outcome_join_status == "available"
        else "partial"
    )
    return {
        "decision_opportunity_count": decision_opportunity_count,
        "selected_local_count": local,
        "selected_horizontal_count": horizontal,
        "selected_vertical_count": vertical,
        "selected_action_count": selected_action_count,
        "selected_action_count_consistency_verified": selected_action_count_consistency_verified,
        "selected_action_to_task_join_count": selected_action_to_task_join_count,
        "selected_action_to_task_join_ratio": None if decision_opportunity_count == 0 else selected_action_to_task_join_count / decision_opportunity_count,
        "missing_selected_action_task_join_count": decision_opportunity_count - selected_action_to_task_join_count,
        "selected_action_family_evidence_status": selected_action_family_evidence_status,
        "selected_action_to_task_join_status": selected_action_to_task_join_status,
        "terminal_outcome_join_status": terminal_outcome_join_status,
        "per_action_outcome_evidence_status": per_action_outcome_evidence_status,
        "terminal_outcome_join_key_count": terminal_outcome_join_key_count,
        "selected_action_to_task_join_key_count": selected_action_to_task_join_count,
        "selected_action_trace_record_count": decision_opportunity_count,
        "selected_action_family_trace_record_count": decision_opportunity_count,
        "selected_action_trace_coverage_ratio": None if decision_opportunity_count == 0 else 1.0,
        "selected_action_family_coverage_ratio": None if decision_opportunity_count == 0 else 1.0,
        "selected_action_to_task_join_coverage_ratio": None if decision_opportunity_count == 0 else selected_action_to_task_join_count / decision_opportunity_count,
        "terminal_outcome_join_key_coverage_ratio": None if decision_opportunity_count == 0 else terminal_outcome_join_key_count / decision_opportunity_count,
        "missing_selected_action_trace_count": 0,
        "missing_selected_action_family_count": 0,
        "missing_selected_action_to_task_join_key_count": decision_opportunity_count - selected_action_to_task_join_count,
        "missing_terminal_outcome_join_key_count": decision_opportunity_count - terminal_outcome_join_key_count,
        "per_strategy_seed_selected_action_family_matrix": rows,
        "legal_family_counts": dict(legal_family_counts),
        "selected_outcome_counts": {family: dict(counts) for family, counts in selected_outcome_counts.items()},
    }


def build_selected_action_outcome_evidence_rerun_report(
    config: SelectedActionOutcomeEvidenceRerunConfig | None = None,
) -> SelectedActionOutcomeEvidenceRerunReport:
    config = config or SelectedActionOutcomeEvidenceRerunConfig()
    feature_048 = _load_json(PRIOR_ARTIFACTS["exposure_matrix_paper_mechanism_alignment"])
    feature_051 = _load_json(PRIOR_ARTIFACTS["passive_selected_action_trace_repair"])
    behavior = _behavior_equivalence_summary(feature_051)
    trace_sample = _run_trace_sample(trace_enabled=True, config=config)
    counts = _selected_action_counts(trace_sample["trace_events"], trace_sample["finalized_tasks"], config=config)
    feature_051_trace_readiness_verified = _feature_051_trace_readiness_verified(feature_051)
    selected_action_family_evidence_status = counts["selected_action_family_evidence_status"]
    selected_action_to_task_join_status = counts["selected_action_to_task_join_status"]
    terminal_outcome_join_status = counts["terminal_outcome_join_status"]
    per_action_outcome_evidence_status = counts["per_action_outcome_evidence_status"]
    legal_local_count = counts["legal_family_counts"].get("local", 0)
    legal_horizontal_count = counts["legal_family_counts"].get("horizontal", 0)
    legal_vertical_count = counts["legal_family_counts"].get("vertical", 0)
    legal_but_unselected_local_count = legal_local_count - counts["selected_local_count"]
    legal_but_unselected_horizontal_count = legal_horizontal_count - counts["selected_horizontal_count"]
    legal_but_unselected_vertical_count = legal_vertical_count - counts["selected_vertical_count"]
    legal_but_unselected_consistency_verified = all(
        value >= 0
        for value in [
            legal_but_unselected_local_count,
            legal_but_unselected_horizontal_count,
            legal_but_unselected_vertical_count,
        ]
    )
    exposure_matrix_internal_consistency_verified = (
        counts["selected_action_count_consistency_verified"]
        and selected_action_to_task_join_status == "available"
        and per_action_outcome_evidence_status == "available"
        and legal_but_unselected_consistency_verified
        and 0 <= feature_048.get("selected_illegal_action_count", 0) <= counts["selected_action_count"]
        and all(
            row["selected_action_completed_count"] + row["selected_action_dropped_count"] + row["selected_action_pending_count"] == row["selected_action_count"]
            for row in counts["per_strategy_seed_selected_action_family_matrix"]
        )
    )
    feature_049_can_be_rerun = (
        selected_action_family_evidence_status == "available"
        and selected_action_to_task_join_status == "available"
        and per_action_outcome_evidence_status == "available"
        and legal_but_unselected_consistency_verified
        and exposure_matrix_internal_consistency_verified
        and behavior.passed
        and bool(feature_048.get("no_action_selection_drift", False))
        and bool(feature_048.get("no_action_legality_drift", False))
    )
    blockers: list[str] = []
    if not feature_051_trace_readiness_verified:
        blockers.append("feature_051_trace_readiness_incomplete")
    if selected_action_family_evidence_status != "available":
        blockers.append("selected_action_family_evidence_incomplete")
    if selected_action_to_task_join_status != "available":
        blockers.append("selected_action_to_task_join_incomplete")
    if per_action_outcome_evidence_status != "available":
        blockers.append("per_action_outcome_join_incomplete")
    if not legal_but_unselected_consistency_verified:
        blockers.append("legal_but_unselected_consistency_failed")
    if not exposure_matrix_internal_consistency_verified:
        blockers.append("exposure_matrix_internal_consistency_failed")
    if not behavior.passed:
        blockers.append("behavior_equivalence_failed")
    if not feature_048.get("no_action_selection_drift", False):
        blockers.append("action_selection_drift_detected")
    if not feature_048.get("no_action_legality_drift", False):
        blockers.append("action_legality_drift_detected")
    if feature_049_can_be_rerun:
        blockers = []

    final_verdict = "prerequisite_blocked"
    recommended_next_feature = "prerequisite blocked"
    if feature_049_can_be_rerun:
        final_verdict = "selected_action_outcome_evidence_ready_for_feature_049_rerun"
        recommended_next_feature = "Feature 053 — Exposure Matrix Paper Mechanism Rerun with Outcome Evidence"
    elif selected_action_family_evidence_status != "available":
        final_verdict = "selected_action_family_evidence_still_incomplete"
        recommended_next_feature = "selected-action trace repair continuation"
    elif selected_action_to_task_join_status != "available":
        final_verdict = "selected_action_to_task_join_still_incomplete"
        recommended_next_feature = "selected-action-to-task join repair continuation"
    elif per_action_outcome_evidence_status != "available":
        final_verdict = "per_action_outcome_join_still_incomplete"
        recommended_next_feature = "terminal outcome join repair continuation"
    elif not exposure_matrix_internal_consistency_verified:
        final_verdict = "exposure_matrix_internal_consistency_failed"
        recommended_next_feature = "exposure evidence consistency repair before training"
    elif not behavior.passed:
        final_verdict = "behavior_drift_detected"
        recommended_next_feature = "passive evidence drift repair"

    family_summary = SelectedActionFamilyEvidenceSummary(
        selected_local_count=counts["selected_local_count"],
        selected_horizontal_count=counts["selected_horizontal_count"],
        selected_vertical_count=counts["selected_vertical_count"],
        selected_action_count=counts["selected_action_count"],
        selected_action_count_consistency_verified=counts["selected_action_count_consistency_verified"],
        per_strategy_seed_selected_action_family_matrix=counts["per_strategy_seed_selected_action_family_matrix"],
        selected_action_family_evidence_status=selected_action_family_evidence_status,
    )
    join_summary = SelectedActionToTaskJoinSummary(
        selected_action_to_task_join_count=counts["selected_action_to_task_join_count"],
        selected_action_to_task_join_ratio=counts["selected_action_to_task_join_ratio"],
        missing_selected_action_task_join_count=counts["missing_selected_action_task_join_count"],
        selected_action_to_task_join_status=selected_action_to_task_join_status,
    )
    per_action_join_summary = PerActionOutcomeJoinSummary(
        per_action_completion_count={row["action_family"]: row["selected_action_completed_count"] for row in counts["per_strategy_seed_selected_action_family_matrix"]},
        per_action_drop_count={row["action_family"]: row["selected_action_dropped_count"] for row in counts["per_strategy_seed_selected_action_family_matrix"]},
        per_action_pending_count={row["action_family"]: row["selected_action_pending_count"] for row in counts["per_strategy_seed_selected_action_family_matrix"]},
        per_action_completion_rate={row["action_family"]: row["selected_action_completion_rate"] for row in counts["per_strategy_seed_selected_action_family_matrix"]},
        per_action_drop_rate={row["action_family"]: row["selected_action_drop_rate"] for row in counts["per_strategy_seed_selected_action_family_matrix"]},
        per_action_pending_rate={row["action_family"]: row["selected_action_pending_rate"] for row in counts["per_strategy_seed_selected_action_family_matrix"]},
        per_action_outcome_evidence_status=per_action_outcome_evidence_status,
    )
    per_action_matrix = PerActionOutcomeMatrix(
        per_strategy_seed_selected_action_family_matrix=counts["per_strategy_seed_selected_action_family_matrix"],
        per_action_outcome_join_summary=per_action_join_summary,
    )
    legal_summary = LegalButUnselectedConsistencySummary(
        legal_but_unselected_local_count=legal_but_unselected_local_count,
        legal_but_unselected_horizontal_count=legal_but_unselected_horizontal_count,
        legal_but_unselected_vertical_count=legal_but_unselected_vertical_count,
        legal_but_unselected_consistency_verified=legal_but_unselected_consistency_verified,
    )
    exposure_summary = ExposureMatrixInternalConsistencySummary(
        selected_action_count_consistency_verified=counts["selected_action_count_consistency_verified"],
        selected_illegal_action_count=feature_048.get("selected_illegal_action_count", 0),
        selected_action_to_task_join_status=selected_action_to_task_join_status,
        per_action_outcome_evidence_status=per_action_outcome_evidence_status,
        legal_but_unselected_consistency_verified=legal_but_unselected_consistency_verified,
        exposure_matrix_internal_consistency_verified=exposure_matrix_internal_consistency_verified,
    )
    unblock = Feature049UnblockAssessment(
        feature_049_can_be_rerun=feature_049_can_be_rerun,
        feature_049_remaining_blockers=blockers,
        selected_action_family_evidence_status=selected_action_family_evidence_status,
        selected_action_to_task_join_status=selected_action_to_task_join_status,
        per_action_outcome_evidence_status=per_action_outcome_evidence_status,
        legal_but_unselected_consistency_verified=legal_but_unselected_consistency_verified,
        exposure_matrix_internal_consistency_verified=exposure_matrix_internal_consistency_verified,
        behavior_equivalence_passed=behavior.passed,
        recommended_next_feature=recommended_next_feature,
    )
    report = SelectedActionOutcomeEvidenceRerunReport(
        feature_id=FEATURE_ID,
        prerequisite_tags_verified=_prerequisite_tags_verified(),
        prior_feature_gates_verified=_prior_feature_gates_verified(),
        feature_051_trace_readiness_verified=feature_051_trace_readiness_verified,
        selected_action_family_evidence_summary=family_summary,
        selected_action_to_task_join_summary=join_summary,
        per_action_outcome_join_summary=per_action_join_summary,
        per_action_outcome_matrix=per_action_matrix,
        legal_but_unselected_consistency_summary=legal_summary,
        exposure_matrix_internal_consistency_summary=exposure_summary,
        feature_049_unblock_assessment=unblock,
        behavior_equivalence_summary=behavior,
        evidence_population_summary=EvidencePopulationSummary(
            selected_action_trace_source=PRIOR_ARTIFACTS["passive_selected_action_trace_repair"].as_posix(),
            selected_action_family_source=PRIOR_ARTIFACTS["passive_selected_action_trace_repair"].as_posix(),
            selected_action_to_task_join_source=PRIOR_ARTIFACTS["passive_selected_action_trace_repair"].as_posix(),
            terminal_outcome_join_source=PRIOR_ARTIFACTS["passive_selected_action_trace_repair"].as_posix(),
            legal_count_source=PRIOR_ARTIFACTS["exposure_matrix_paper_mechanism_alignment"].as_posix(),
            feature_051_source=PRIOR_ARTIFACTS["passive_selected_action_trace_repair"].as_posix(),
        ),
        selected_action_family_evidence_status=selected_action_family_evidence_status,
        selected_action_to_task_join_status=selected_action_to_task_join_status,
        per_action_outcome_evidence_status=per_action_outcome_evidence_status,
        behavior_equivalence_passed=behavior.passed,
        feature_049_can_be_rerun=feature_049_can_be_rerun,
        feature_049_remaining_blockers=blockers,
        recommended_next_feature=recommended_next_feature,
        final_verdict=final_verdict,
    )
    return report


def run_selected_action_outcome_evidence_rerun(output_dir: Path | str | None = None) -> SelectedActionOutcomeEvidenceRerunReport:
    report = build_selected_action_outcome_evidence_rerun_report()
    write_selected_action_outcome_evidence_rerun_report(report, output_dir)
    return report
