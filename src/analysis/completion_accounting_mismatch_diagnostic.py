# Completion Accounting Mismatch Diagnostic

"""
Diagnostic-only module for investigating the execution_completed vs trainer counter mismatch.

This module does not repair counters. It collects and classifies per-trace lifecycle data.

Outputs:
- Per-task lifecycle rows
- Mismatch table
- Accounting summary
- Verdict
"""

import json
import os
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, TypedDict


class TaskLifecycleRow(TypedDict):
    task_id: str
    episode_id: int
    first_arrival_slot: int
    service_start_slot: int
    execution_completed_slot: Optional[int]
    deadline_reached_slot: Optional[int]
    deadline_expired_slot: Optional[int]
    task_completed_slot: Optional[int]
    task_dropped_slot: Optional[int]
    reward_emitted_slot: Optional[int]
    finalized_task_exists: bool
    finalized_terminal_outcome: Optional[str]
    finalized_completion_slot: Optional[int]
    finalized_drop_slot: Optional[int]
    trainer_counted_completed: bool
    trainer_counted_dropped: bool
    accounting_classification: str


class MismatchRow(TypedDict):
    task_id: str
    execution_completed_exists: bool
    finalized_task_exists: bool
    finalized_terminal_outcome: Optional[str]
    counted_by_trainer: str
    classification: str


class AccountingSummary(TypedDict):
    execution_completed_count: int
    lifecycle_task_completed_count: int
    lifecycle_task_dropped_count: int
    finalized_completed_count: int
    finalized_dropped_count: int
    trainer_completed_task_count: int
    trainer_dropped_task_count: int
    execution_completed_task_ids: List[str]
    finalized_completed_task_ids: List[str]
    finalized_dropped_task_ids: List[str]
    mismatch_task_ids: List[str]
    orphan_finalized_task_ids: List[str]
    aggregate_completed_diff: int
    aggregate_dropped_diff: int


class DiagnosticOutput(TypedDict):
    task_lifecycle_rows: List[TaskLifecycleRow]
    mismatch_table: List[MismatchRow]
    accounting_summary: AccountingSummary
    verdict: str


def classify_accounting(
    execution_completed_slot: Optional[int],
    finalized_terminal_outcome: Optional[str],
    counted_by_trainer: str
) -> str:
    if execution_completed_slot is None:
        return "pending_or_unknown"

    if not finalized_terminal_outcome:
        return "execution_completed_without_finalized_task"

    if finalized_terminal_outcome == "completed":
        if counted_by_trainer == "completed":
            return "execution_completed_then_completed"
        elif counted_by_trainer == "dropped":
            return "finalized_completed_missed_by_trainer"
        else:
            return "finalized_completed_missed_by_trainer"

    elif finalized_terminal_outcome in ("dropped", "expired"):
        if counted_by_trainer == "dropped":
            return "execution_completed_then_dropped"
        else:
            return "execution_completed_then_dropped"

    return "lifecycle_finalized_disagreement"


def diagnose(
    timing_audit: dict,
    lifecycle_events: List[Dict[str, Any]],
    finalized_tasks: List[Dict[str, Any]],
    trainer_completed: int,
    trainer_dropped: int
) -> DiagnosticOutput:
    """
    Diagnostic comparison of lifecycle trace events vs finalized tasks vs trainer counters.

    Parameters
    ----------
    lifecycle_events: dicts from environment trace recorder snapshot (LifecycleTraceEvent.to_dict())
    finalized_tasks: dicts from environment info["finalized_tasks"]
    trainer_completed: aggregate count of tasks the trainer counted as completed
    trainer_dropped: aggregate count of tasks the trainer counted as dropped
    """
    if not lifecycle_events:
        return {
            "task_lifecycle_rows": [],
            "mismatch_table": [],
            "accounting_summary": {
                "execution_completed_count": 0,
                "lifecycle_task_completed_count": 0,
                "lifecycle_task_dropped_count": 0,
                "finalized_completed_count": 0,
                "finalized_dropped_count": 0,
                "trainer_completed_task_count": 0,
                "trainer_dropped_task_count": 0,
                    "execution_completed_task_ids": [],
                "finalized_completed_task_ids": [],
                "finalized_dropped_task_ids": [],
                "mismatch_task_ids": [],
                "orphan_finalized_task_ids": [],
                "aggregate_completed_diff": 0,
                "aggregate_dropped_diff": 0
            },
            "verdict": "diagnostic_inconclusive"
        }

    task_slots: Dict[str, dict] = {}

    for event in lifecycle_events:
        raw_task_id = event.get("task_id")
        task_id = str(raw_task_id) if raw_task_id is not None else str(id(event))
        if task_id not in task_slots:
            task_slots[task_id] = {
                "task_id": task_id,
                "episode_id": event.get("episode_id", 0),
                "first_arrival_slot": None,
                "service_start_slot": None,
                "execution_completed_slot": None,
                "deadline_reached_slot": None,
                "deadline_expired_slot": None,
                "task_completed_slot": None,
                "task_dropped_slot": None,
                "reward_emitted_slot": None
            }

        event_type = event.get("event_type")
        slot = event.get("slot")

        if event_type == "task_arrived":
            if task_slots[task_id]["first_arrival_slot"] is None or slot < task_slots[task_id]["first_arrival_slot"]:
                task_slots[task_id]["first_arrival_slot"] = slot
        elif event_type == "execution_started":
            task_slots[task_id]["service_start_slot"] = slot
        elif event_type == "execution_completed":
            task_slots[task_id]["execution_completed_slot"] = slot
        elif event_type == "deadline_reached":
            task_slots[task_id]["deadline_reached_slot"] = slot
        elif event_type == "deadline_expired":
            task_slots[task_id]["deadline_expired_slot"] = slot
        elif event_type == "task_completed":
            task_slots[task_id]["task_completed_slot"] = slot
        elif event_type == "task_dropped":
            task_slots[task_id]["task_dropped_slot"] = slot
        elif event_type == "reward_emitted":
            task_slots[task_id]["reward_emitted_slot"] = slot

    finalized_by_id: Dict[str, dict] = {}
    for ft in finalized_tasks:
        fid = str(ft.get("task_id", ""))
        if fid:
            finalized_by_id[fid] = ft

    # Build trainer-completed/dropped ID sets from finalized_tasks.
    # These represent what the trainer SHOULD have counted.
    # The trainer_completed/trainer_dropped aggregate counts (passed in) are what it
    # ACTUALLY counted. A mismatch occurs when the IDs don't match the counts.
    trainer_should_have_completed: Set[str] = set()
    trainer_should_have_dropped: Set[str] = set()

    for ft in finalized_tasks:
        fid = str(ft.get("task_id", ""))
        outcome = ft.get("terminal_outcome")
        if outcome == "completed":
            trainer_should_have_completed.add(fid)
        elif outcome == "dropped":
            trainer_should_have_dropped.add(fid)

    task_lifecycle_rows: List[TaskLifecycleRow] = []
    mismatch_table: List[MismatchRow] = []

    execution_completed_task_ids: List[str] = []
    finalized_completed_task_ids: List[str] = []
    finalized_dropped_task_ids: List[str] = []
    mismatch_task_ids: List[str] = []

    lifecycle_task_completed_count = 0
    lifecycle_task_dropped_count = 0

    for task_id, slots in task_slots.items():
        ft = finalized_by_id.get(task_id)
        finalized_task_exists = ft is not None
        finalized_terminal_outcome = ft.get("terminal_outcome") if ft else None
        finalized_completion_slot = ft.get("completion_slot") if ft else None
        finalized_drop_slot = ft.get("drop_slot") if ft else None

        trainer_counted_completed = task_id in trainer_should_have_completed
        trainer_counted_dropped = task_id in trainer_should_have_dropped

        if trainer_counted_completed:
            counted_by_trainer = "completed"
        elif trainer_counted_dropped:
            counted_by_trainer = "dropped"
        else:
            counted_by_trainer = "unknown"

        classification = classify_accounting(
            slots["execution_completed_slot"],
            finalized_terminal_outcome,
            counted_by_trainer
        )

        if slots["task_completed_slot"] is not None:
            lifecycle_task_completed_count += 1
        if slots["task_dropped_slot"] is not None:
            lifecycle_task_dropped_count += 1

        row: TaskLifecycleRow = {
            "task_id": task_id,
            "episode_id": slots["episode_id"],
            "first_arrival_slot": slots["first_arrival_slot"] if slots["first_arrival_slot"] is not None else -1,
            "service_start_slot": slots["service_start_slot"] if slots["service_start_slot"] is not None else -1,
            "execution_completed_slot": slots["execution_completed_slot"],
            "deadline_reached_slot": slots.get("deadline_reached_slot"),
            "deadline_expired_slot": slots.get("deadline_expired_slot"),
            "task_completed_slot": slots.get("task_completed_slot"),
            "task_dropped_slot": slots.get("task_dropped_slot"),
            "reward_emitted_slot": slots.get("reward_emitted_slot"),
            "finalized_task_exists": finalized_task_exists,
            "finalized_terminal_outcome": finalized_terminal_outcome,
            "finalized_completion_slot": finalized_completion_slot,
            "finalized_drop_slot": finalized_drop_slot,
            "trainer_counted_completed": trainer_counted_completed,
            "trainer_counted_dropped": trainer_counted_dropped,
            "accounting_classification": classification
        }
        task_lifecycle_rows.append(row)

        if slots["execution_completed_slot"] is not None:
            execution_completed_task_ids.append(task_id)

        if finalized_task_exists and finalized_terminal_outcome == "completed":
            finalized_completed_task_ids.append(task_id)
        if finalized_task_exists and finalized_terminal_outcome in ("dropped", "expired"):
            finalized_dropped_task_ids.append(task_id)

        is_mismatch = (
            slots["execution_completed_slot"] is not None
            and (
                not finalized_task_exists
            )
        )
        if is_mismatch:
            mismatch_task_ids.append(task_id)
            mismatch_table.append({
                "task_id": task_id,
                "execution_completed_exists": slots["execution_completed_slot"] is not None,
                "finalized_task_exists": finalized_task_exists,
                "finalized_terminal_outcome": finalized_terminal_outcome,
                "counted_by_trainer": counted_by_trainer,
                "classification": classification
            })

    # Aggregate-level mismatch: compare trainer aggregate counts against ALL finalized task entries.
    # Count per-entry (not deduplicated by task_id) to match the trainer's per-episode counting.
    # The trainer counts by terminal_outcome, so use the same criterion:
    expected_completed = sum(1 for ft in finalized_tasks if ft.get("terminal_outcome") == "completed")
    expected_dropped = sum(1 for ft in finalized_tasks if ft.get("terminal_outcome") == "dropped")
    aggregate_mismatch_completed = trainer_completed != expected_completed
    aggregate_mismatch_dropped = trainer_dropped != expected_dropped

    # Identify orphan finalized tasks: task IDs in finalized_tasks that never appeared in lifecycle events.
    lifecycle_task_ids: Set[str] = set()
    for event in lifecycle_events:
        raw_tid = event.get("task_id")
        if raw_tid is not None:
            lifecycle_task_ids.add(str(raw_tid))

    orphan_finalized_task_ids: List[str] = []
    for ft in finalized_tasks:
        fid = str(ft.get("task_id", ""))
        if fid and fid not in lifecycle_task_ids:
            orphan_finalized_task_ids.append(fid)

    accounting_summary: AccountingSummary = {
        "execution_completed_count": len(execution_completed_task_ids),
        "lifecycle_task_completed_count": lifecycle_task_completed_count,
        "lifecycle_task_dropped_count": lifecycle_task_dropped_count,
        "finalized_completed_count": len(finalized_completed_task_ids),
        "finalized_dropped_count": len(finalized_dropped_task_ids),
        "trainer_completed_task_count": trainer_completed,
        "trainer_dropped_task_count": trainer_dropped,
        "execution_completed_task_ids": execution_completed_task_ids,
        "finalized_completed_task_ids": finalized_completed_task_ids,
        "finalized_dropped_task_ids": finalized_dropped_task_ids,
        "mismatch_task_ids": mismatch_task_ids,
        "orphan_finalized_task_ids": orphan_finalized_task_ids,
        "aggregate_completed_diff": trainer_completed - expected_completed,
        "aggregate_dropped_diff": trainer_dropped - expected_dropped,
    }

    # Verdict derivation from classifications and aggregate mismatch
    classifications = [r["accounting_classification"] for r in task_lifecycle_rows]
    has_env_repair = "execution_completed_without_finalized_task" in classifications
    has_trainer_repair = aggregate_mismatch_completed or aggregate_mismatch_dropped
    has_exec_then_dropped = "execution_completed_then_dropped" in classifications
    has_exec_then_completed = "execution_completed_then_completed" in classifications

    if has_env_repair:
        verdict = "diagnostic_needs_environment_finalization_repair"
    elif has_trainer_repair:
        verdict = "diagnostic_needs_trainer_accounting_repair"
    elif has_exec_then_dropped and not has_exec_then_completed:
        verdict = "diagnostic_no_repair_needed_update_interpretation"
    elif has_exec_then_completed and not has_exec_then_dropped and not has_env_repair:
        verdict = "diagnostic_consistent"
    elif not execution_completed_task_ids:
        verdict = "diagnostic_inconclusive"
    else:
        verdict = "diagnostic_no_repair_needed_update_interpretation"

    return {
        "task_lifecycle_rows": task_lifecycle_rows,
        "mismatch_table": mismatch_table,
        "accounting_summary": accounting_summary,
        "verdict": verdict
    }


def format_evidence(diagnostic_output: DiagnosticOutput) -> str:
    summary = diagnostic_output["accounting_summary"]
    rows = diagnostic_output["task_lifecycle_rows"]
    mismatches = diagnostic_output["mismatch_table"]

    lines = [
        "# Completion Accounting Mismatch Diagnostic Evidence",
        "",
        "## 1. Bounded Run Summary",
        f"- execution_completed_count: {summary['execution_completed_count']}",
        f"- lifecycle_task_completed_count: {summary['lifecycle_task_completed_count']}",
        f"- lifecycle_task_dropped_count: {summary['lifecycle_task_dropped_count']}",
        f"- finalized_completed_count: {summary['finalized_completed_count']}",
        f"- finalized_dropped_count: {summary['finalized_dropped_count']}",
        f"- trainer_completed_task_count: {summary['trainer_completed_task_count']}",
        f"- trainer_dropped_task_count: {summary['trainer_dropped_task_count']}",
        f"- aggregate_completed_diff: {summary['aggregate_completed_diff']}",
        f"- aggregate_dropped_diff: {summary['aggregate_dropped_diff']}",
        f"- orphan_finalized_task_ids: {summary['orphan_finalized_task_ids']}",
        "",
        "## 2. Execution Completed Task IDs",
        "```",
    ]
    if summary["execution_completed_task_ids"]:
        for tid in summary["execution_completed_task_ids"]:
            lines.append(tid)
    else:
        lines.append("None")
    lines.extend(["```", "", "## 3. Mismatch Task IDs", "```"])
    if summary["mismatch_task_ids"]:
        for tid in summary["mismatch_task_ids"]:
            lines.append(tid)
    else:
        lines.append("None")
    lines.extend(["```", "", "## 4. Mismatch Table"])

    header = "| task_id | execution_completed | finalized_task | finalized_outcome | counted_by_trainer | classification |"
    sep = "|--------|----------------------|----------------|-------------------|--------------------|----------------|"
    lines.extend(["", header, sep])

    if mismatches:
        for m in mismatches:
            ec = "✓" if m["execution_completed_exists"] else "✗"
            ft = "✓" if m["finalized_task_exists"] else "✗"
            outcome = m["finalized_terminal_outcome"] or "-"
            counted = m["counted_by_trainer"]
            cls = m["classification"]
            lines.append(f"| {m['task_id']} | {ec} | {ft} | {outcome} | {counted} | {cls} |")
    else:
        lines.append("| None | ✗ | ✗ | - | - | None |")

    lines.extend(["", "## 5. Accounting Classifications Summary"])
    if rows:
        cls_counts = Counter(r["accounting_classification"] for r in rows)
        for cls_name, count in sorted(cls_counts.items()):
            lines.append(f"- {cls_name}: {count}")
    else:
        lines.append("- No valid tasks found")

    lines.extend([
        "",
        "## 6. Diagnostic Verdict",
        f"- **verdict**: `{diagnostic_output['verdict']}`",
        ""
    ])
    return "\n".join(lines)


def run_completion_accounting_mismatch_diagnostic(
    episodes: int = 3,
    episode_length: int = 200,
) -> DiagnosticOutput:
    """
    Run a bounded rollout and collect diagnostic data comparing lifecycle events
    against trainer counters. Does NOT train the network (diagnostic-only pass).

    Returns DiagnosticOutput with per-task lifecycle rows, mismatch table,
    accounting summary, and verdict.
    """
    from src.analysis.full_training_reproduction_campaign.config import CampaignConfig
    from src.analysis.full_training_reproduction_campaign.trainer import DDQNTrainer, _build_environment
    from src.analysis.trace_collector import make_enabled_trace_collector

    config = CampaignConfig.paper_default()
    tracer = make_enabled_trace_collector()
    trainer = DDQNTrainer(config, trace_collector=tracer)

    all_lifecycle_event_dicts: List[Dict[str, Any]] = []
    all_finalized_tasks: List[Dict[str, Any]] = []
    trainer_completed_total = 0
    trainer_dropped_total = 0

    for ep_idx in range(episodes):
        seed = config.seed_bundle.training_trace_generation_seed + ep_idx
        env = _build_environment(
            config,
            episode_length=episode_length,
            seed=seed,
            trace_enabled=True,
        )
        env.reset(seed=seed)
        history = trainer._initial_history(episode_length=episode_length)

        ep_lifecycle_events: List[Dict[str, Any]] = []
        ep_finalized_tasks: List[Dict[str, Any]] = []

        while True:
            current_task = env.current_task
            if current_task is not None:
                observation = env.observe_flat(current_task)
                state_tensor = trainer._state_tensor(history)
                legal_mask = observation.get("legal_action_mask", {})
                action = trainer.policy.choose_action(state_tensor, legal_mask)
            else:
                observation = env.observe_flat()
                action = None

            next_observation, reward, terminated, truncated, info = env.step(action)

            for event_dict in info.get("lifecycle_trace_events", []):
                event_dict["episode_id"] = ep_idx
            ep_lifecycle_events.extend(info.get("lifecycle_trace_events", []))

            ep_finalized_tasks.extend(info.get("finalized_tasks", []))

            for ft in info.get("finalized_tasks", []):
                outcome = ft.get("terminal_outcome")
                if outcome == "completed":
                    trainer_completed_total += 1
                elif outcome == "dropped":
                    trainer_dropped_total += 1

            if current_task is not None:
                next_current_task = env.current_task
                if config.state_dim == 3:
                    from src.analysis.full_training_reproduction_campaign.replay import build_state_vector
                    next_feature = build_state_vector(
                        observation=next_observation,
                        current_task=next_current_task,
                        episode_length=episode_length,
                    )
                else:
                    next_feature = trainer._compute_state_vector(next_observation, env)
                history.append(next_feature)

            if terminated or truncated:
                break

        all_lifecycle_event_dicts.extend(ep_lifecycle_events)
        all_finalized_tasks.extend(ep_finalized_tasks)

    return diagnose(
        timing_audit={},
        lifecycle_events=all_lifecycle_event_dicts,
        finalized_tasks=all_finalized_tasks,
        trainer_completed=trainer_completed_total,
        trainer_dropped=trainer_dropped_total,
    )


def write_artifacts(diagnostic_output: DiagnosticOutput) -> tuple[Path, Path]:
    OUTPUT_DIR = Path(os.getenv(
        "DIAGNOSTIC_OUTPUT_DIR",
        "artifacts/analysis/completion-accounting-mismatch-diagnostic"
    ))
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUTPUT_DIR / "diagnostic_output.json"
    md_path = OUTPUT_DIR / "diagnostic_evidence.md"

    json_path.write_text(
        json.dumps(diagnostic_output, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    md_content = format_evidence(diagnostic_output)
    md_path.write_text(md_content, encoding="utf-8")
    return json_path, md_path


if __name__ == "__main__":
    output = run_completion_accounting_mismatch_diagnostic()
    json_path, md_path = write_artifacts(output)
    print(f"JSON: {json_path}")
    print(f"MD:   {md_path}")
    print(f"Verdict: {output['verdict']}")
