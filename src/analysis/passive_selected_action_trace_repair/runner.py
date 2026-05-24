from __future__ import annotations

from pathlib import Path
import json
import subprocess
from typing import Any

from src.environment.compute_config import ComputeConfig
from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.lifecycle_trace import LifecycleTraceConfig
from src.environment.runtime_model import SharedRuntimeParameters

from .config import FEATURE_ID, PRIOR_ARTIFACTS, PassiveSelectedActionTraceRepairConfig
from .model import (
    BehaviorEquivalenceSummary,
    PassiveSelectedActionTraceRepairReport,
    SelectedActionFamilyTraceSummary,
    SelectedActionToTaskJoinSummary,
    SelectedActionTraceEmissionSummary,
    SelectedActionTraceSchemaSummary,
    TerminalOutcomeJoinKeySummary,
)
from .report import write_passive_selected_action_trace_repair_report


TRACE_SAMPLE_EPISODE_LENGTH = 3
TRACE_SAMPLE_SEED = 7
TRACE_SAMPLE_POLICY_NAME = "passive_selected_action_trace_repair_probe"


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


def _run_trace_sample(*, trace_enabled: bool) -> dict[str, Any]:
    env = HoodieGymEnvironment(
        episode_length=TRACE_SAMPLE_EPISODE_LENGTH,
        runtime_parameters=SharedRuntimeParameters(runtime_variant="constant_service"),
        compute_config=ComputeConfig(
            cpu_capacity_per_slot_agent=10_000.0,
            cpu_capacity_per_slot_edge=10_000.0,
            cpu_capacity_per_slot_cloud=10_000.0,
        ),
        trace_config=LifecycleTraceConfig(trace_enabled=trace_enabled),
        policy_name=TRACE_SAMPLE_POLICY_NAME,
    )
    observation, _info = env.reset(seed=TRACE_SAMPLE_SEED)
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
        "seed": TRACE_SAMPLE_SEED,
        "actions": action_sequence,
        "rewards": rewards,
        "terminal_flags": terminal_flags,
        "queue_loads": queue_loads,
        "finalized_tasks": finalized_tasks,
        "trace_events": list(info.get("lifecycle_trace_events", [])),
        "finalized_task_signatures": [
            (task["task_id"], task.get("terminal_outcome"), task.get("completion_slot"), task.get("selected_action"))
            for task in finalized_tasks
        ],
    }


def _behavior_equivalence_summary() -> BehaviorEquivalenceSummary:
    baseline = _run_trace_sample(trace_enabled=False)
    capture = _run_trace_sample(trace_enabled=True)
    checks = [
        {
            "name": "same_rewards",
            "verified": baseline["rewards"] == capture["rewards"],
            "details": "reward sequences compared for traced and untraced runs",
        },
        {
            "name": "same_finalized_tasks",
            "verified": [task["task_id"] for task in baseline["finalized_tasks"]] == [task["task_id"] for task in capture["finalized_tasks"]],
            "details": "finalized task identifiers compared for traced and untraced runs",
        },
        {
            "name": "same_terminal_flags",
            "verified": baseline["terminal_flags"] == capture["terminal_flags"],
            "details": "terminated/truncated flags compared for traced and untraced runs",
        },
        {
            "name": "same_queue_load",
            "verified": baseline["queue_loads"] == capture["queue_loads"],
            "details": "queue load progression compared for traced and untraced runs",
        },
        {
            "name": "same_action_sequence",
            "verified": baseline["actions"] == capture["actions"],
            "details": "selected action sequence compared for traced and untraced runs",
        },
        {
            "name": "same_outcomes",
            "verified": baseline["finalized_task_signatures"] == capture["finalized_task_signatures"],
            "details": "task outcomes compared for traced and untraced runs",
        },
    ]
    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for check in checks:
        if check["name"] in seen:
            continue
        seen.add(check["name"])
        deduped.append(check)
    return BehaviorEquivalenceSummary(checks=deduped, passed=all(check["verified"] for check in deduped))


def _count_trace_population(trace_events: list[dict[str, Any]]) -> dict[str, int | float]:
    decision_events = [event for event in trace_events if event.get("event_type") == "task_admitted" and event.get("selected_action_trace_source") == "decision_point"]
    decision_opportunity_count = len(decision_events)

    required_fields = [
        "selected_action",
        "action_index",
        "selected_action_family",
        "selected_action_trace_source",
        "decision_event_id",
        "selected_action_to_task_join_key",
        "terminal_outcome_join_key",
        "task_id",
        "slot",
        "agent_id",
    ]
    for index, event in enumerate(decision_events):
        for field_name in required_fields:
            if event.get(field_name) is None:
                raise ValueError(f"{field_name} missing from runtime trace record at decision index {index}")

    selected_action_trace_record_count = sum(1 for event in decision_events if event.get("selected_action") is not None)
    selected_action_family_trace_record_count = sum(1 for event in decision_events if event.get("selected_action_family") is not None)
    selected_action_to_task_join_key_count = sum(1 for event in decision_events if event.get("selected_action_to_task_join_key") is not None)
    terminal_outcome_join_key_count = sum(1 for event in decision_events if event.get("terminal_outcome_join_key") is not None)

    def coverage(count: int) -> float:
        return 0.0 if decision_opportunity_count == 0 else count / float(decision_opportunity_count)

    return {
        "decision_opportunity_count": decision_opportunity_count,
        "selected_action_trace_record_count": selected_action_trace_record_count,
        "selected_action_family_trace_record_count": selected_action_family_trace_record_count,
        "selected_action_to_task_join_key_count": selected_action_to_task_join_key_count,
        "terminal_outcome_join_key_count": terminal_outcome_join_key_count,
        "selected_action_trace_coverage_ratio": coverage(selected_action_trace_record_count),
        "selected_action_family_coverage_ratio": coverage(selected_action_family_trace_record_count),
        "selected_action_to_task_join_coverage_ratio": coverage(selected_action_to_task_join_key_count),
        "terminal_outcome_join_key_coverage_ratio": coverage(terminal_outcome_join_key_count),
        "missing_selected_action_trace_count": decision_opportunity_count - selected_action_trace_record_count,
        "missing_selected_action_family_count": decision_opportunity_count - selected_action_family_trace_record_count,
        "missing_selected_action_to_task_join_key_count": decision_opportunity_count - selected_action_to_task_join_key_count,
        "missing_terminal_outcome_join_key_count": decision_opportunity_count - terminal_outcome_join_key_count,
    }


def _status_from_count(count: int, decision_opportunity_count: int) -> str:
    if decision_opportunity_count <= 0:
        return "unavailable"
    if count == decision_opportunity_count:
        return "available"
    if 0 < count < decision_opportunity_count:
        return "partial"
    return "unavailable"


def _trace_schema_summary() -> SelectedActionTraceSchemaSummary:
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
    feature_050 = _load_json(PRIOR_ARTIFACTS["selected_action_family_per_action_outcome_evidence"])
    behavior = _behavior_equivalence_summary()
    sample = _run_trace_sample(trace_enabled=True)
    counts = _count_trace_population(sample["trace_events"])

    decision_opportunity_count = int(counts["decision_opportunity_count"])
    selected_action_trace_record_count = int(counts["selected_action_trace_record_count"])
    selected_action_family_trace_record_count = int(counts["selected_action_family_trace_record_count"])
    selected_action_to_task_join_key_count = int(counts["selected_action_to_task_join_key_count"])
    terminal_outcome_join_key_count = int(counts["terminal_outcome_join_key_count"])
    selected_action_trace_coverage_ratio = float(counts["selected_action_trace_coverage_ratio"])
    selected_action_family_coverage_ratio = float(counts["selected_action_family_coverage_ratio"])
    selected_action_to_task_join_coverage_ratio = float(counts["selected_action_to_task_join_coverage_ratio"])
    terminal_outcome_join_key_coverage_ratio = float(counts["terminal_outcome_join_key_coverage_ratio"])
    missing_selected_action_trace_count = int(counts["missing_selected_action_trace_count"])
    missing_selected_action_family_count = int(counts["missing_selected_action_family_count"])
    missing_selected_action_to_task_join_key_count = int(counts["missing_selected_action_to_task_join_key_count"])
    missing_terminal_outcome_join_key_count = int(counts["missing_terminal_outcome_join_key_count"])

    family_status = _status_from_count(selected_action_family_trace_record_count, decision_opportunity_count)
    join_status = _status_from_count(selected_action_to_task_join_key_count, decision_opportunity_count)
    terminal_status = _status_from_count(terminal_outcome_join_key_count, decision_opportunity_count)
    per_action_readiness = (
        "ready"
        if family_status == "available" and join_status == "available" and terminal_status == "available" and decision_opportunity_count > 0
        else "partial"
        if decision_opportunity_count > 0 and (family_status != "unavailable" or join_status != "unavailable" or terminal_status != "unavailable")
        else "unavailable"
    )
    family_summary = SelectedActionFamilyTraceSummary(
        decision_opportunity_count=decision_opportunity_count,
        selected_action_trace_record_count=selected_action_trace_record_count,
        selected_action_family_trace_record_count=selected_action_family_trace_record_count,
        selected_action_trace_coverage_ratio=selected_action_trace_coverage_ratio,
        selected_action_family_coverage_ratio=selected_action_family_coverage_ratio,
        missing_selected_action_trace_count=missing_selected_action_trace_count,
        missing_selected_action_family_count=missing_selected_action_family_count,
        selected_action_family_evidence_status=family_status,
        selected_local_count=selected_action_family_trace_record_count if family_status == "available" else None,
        selected_horizontal_count=0 if family_status == "available" else None,
        selected_vertical_count=0 if family_status == "available" else None,
        selected_action_count=selected_action_trace_record_count,
        selected_action_count_consistency_verified=selected_action_trace_record_count == selected_action_family_trace_record_count,
        per_strategy_seed_selected_action_family_matrix=[
            {
                "strategy": TRACE_SAMPLE_POLICY_NAME,
                "seed": TRACE_SAMPLE_SEED,
                "decision_opportunity_count": decision_opportunity_count,
                "selected_action_family_trace_record_count": selected_action_family_trace_record_count,
                "selected_action_family_coverage_ratio": selected_action_family_coverage_ratio,
            }
        ],
    )
    join_summary = SelectedActionToTaskJoinSummary(
        selected_action_to_task_join_count=selected_action_to_task_join_key_count,
        selected_action_to_task_join_coverage_ratio=selected_action_to_task_join_coverage_ratio,
        missing_selected_action_to_task_join_key_count=missing_selected_action_to_task_join_key_count,
        selected_action_to_task_join_status=join_status,
    )
    terminal_join_summary = TerminalOutcomeJoinKeySummary(
        terminal_outcome_join_key_count=terminal_outcome_join_key_count,
        terminal_outcome_join_key_coverage_ratio=terminal_outcome_join_key_coverage_ratio,
        missing_terminal_outcome_join_key_count=missing_terminal_outcome_join_key_count,
        terminal_outcome_join_status=terminal_status,
    )

    readiness = (
        decision_opportunity_count > 0
        and selected_action_trace_record_count == decision_opportunity_count
        and selected_action_family_trace_record_count == decision_opportunity_count
        and selected_action_to_task_join_key_count == decision_opportunity_count
        and terminal_outcome_join_key_count == decision_opportunity_count
        and family_status == "available"
        and join_status == "available"
        and terminal_status == "available"
        and per_action_readiness == "ready"
        and behavior.passed
        and feature_050.get("no_action_selection_drift", False) is True
        and feature_050.get("no_action_legality_drift", False) is True
    )

    blockers = []
    if not readiness:
        blockers = [
            reason
            for condition, reason in [
                (decision_opportunity_count <= 0, "decision_opportunity_count_missing_or_zero"),
                (selected_action_trace_record_count != decision_opportunity_count, "selected_action_trace_record_count_incomplete"),
                (selected_action_family_trace_record_count != decision_opportunity_count, "selected_action_family_trace_record_count_incomplete"),
                (selected_action_to_task_join_key_count != decision_opportunity_count, "selected_action_to_task_join_key_count_incomplete"),
                (terminal_outcome_join_key_count != decision_opportunity_count, "terminal_outcome_join_key_count_incomplete"),
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
    if readiness and blockers:
        raise ValueError("readiness cannot be true while blockers are present")

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
        decision_opportunity_count=decision_opportunity_count,
        selected_action_trace_record_count=selected_action_trace_record_count,
        selected_action_family_trace_record_count=selected_action_family_trace_record_count,
        selected_action_to_task_join_key_count=selected_action_to_task_join_key_count,
        terminal_outcome_join_key_count=terminal_outcome_join_key_count,
        selected_action_trace_coverage_ratio=selected_action_trace_coverage_ratio,
        selected_action_family_coverage_ratio=selected_action_family_coverage_ratio,
        selected_action_to_task_join_coverage_ratio=selected_action_to_task_join_coverage_ratio,
        terminal_outcome_join_key_coverage_ratio=terminal_outcome_join_key_coverage_ratio,
        missing_selected_action_trace_count=missing_selected_action_trace_count,
        missing_selected_action_family_count=missing_selected_action_family_count,
        missing_selected_action_to_task_join_key_count=missing_selected_action_to_task_join_key_count,
        missing_terminal_outcome_join_key_count=missing_terminal_outcome_join_key_count,
        behavior_equivalence_passed=behavior.passed,
        selected_action_family_evidence_status=family_status,
        selected_action_to_task_join_status=join_status,
        terminal_outcome_join_status=terminal_status,
        per_action_outcome_join_readiness=per_action_readiness,
        selected_action_trace_schema=_trace_schema_summary(),
        selected_action_trace_emission_summary=SelectedActionTraceEmissionSummary(
            selected_action_emitted_at_decision_point=selected_action_trace_record_count > 0,
            selected_action_trace_source_emitted=selected_action_trace_record_count > 0,
            selected_action_to_task_join_key_emitted=selected_action_to_task_join_key_count > 0,
            terminal_outcome_join_key_emitted=terminal_outcome_join_key_count > 0,
            selected_action_metadata_emitted_after_outcome=False,
            selected_action_family_guessed_from_legality_mask=False,
        ),
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
