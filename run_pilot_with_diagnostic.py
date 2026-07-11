#!/usr/bin/env python3
"""
Run a bounded 3x200 pilot of the paper_default configuration with the new 
completion accounting mismatch diagnostic enabled.
"""

import json
import os
from src.analysis.full_training_reproduction_campaign.config import CampaignConfig
from src.analysis.full_training_reproduction_campaign.trainer import DDQNTrainer
from src.analysis.task_arrival_completion_timing_audit import make_enabled_trace_collector
from src.analysis.completion_accounting_mismatch_diagnostic import diagnose, format_evidence


def main():
    print("Running bounded 3x200 pilot with completion accounting mismatch diagnostic...")
    
    os.makedirs("docs/run-logs", exist_ok=True)
    os.makedirs("artifacts/analysis/completion-accounting-mismatch-diagnostic", exist_ok=True)
    
    config = CampaignConfig.paper_default()
    config.pilot_episode_length = 200
    config.readiness_probe_episode_count = 3
    
    print(f"Configuration: {config.pilot_episode_length} slots per episode, {config.readiness_probe_episode_count} episodes")
    
    trace_collector = make_enabled_trace_collector()
    trainer = DDQNTrainer(config, trace_collector=trace_collector)
    
    pilot_result = trainer.run_pilot(
        episodes=config.readiness_probe_episode_count,
        episode_length=config.pilot_episode_length
    )
    
    print(f"Pilot completed: {pilot_result.episodes_completed} episodes")
    completed_count = pilot_result.evaluation_summary.get("completed_task_count", 0)
    dropped_count = pilot_result.evaluation_summary.get("dropped_task_count", 0)
    print(f"Completed tasks: {completed_count}")
    print(f"Dropped tasks: {dropped_count}")
    
    lifecycle_events_raw = trace_collector.get_events()
    print(f"Trace collector captured {len(lifecycle_events_raw)} events")
    
    lifecycle_events = [e for e in lifecycle_events_raw if e.get("task_id") is not None]
    
    finalized_tasks: dict[str, dict] = {}
    for event_dict in lifecycle_events_raw:
        et = event_dict.get("event_type", "")
        if et in ("task_completed", "task_dropped"):
            task_id = str(event_dict.get("task_id", "unknown"))
            if task_id not in finalized_tasks:
                outcome = event_dict.get("terminal_outcome", "unknown")
                finalized_tasks[task_id] = {
                    "task_id": task_id,
                    "terminal_outcome": outcome,
                    "completion_slot": event_dict.get("slot") if outcome == "completed" else None,
                    "drop_slot": event_dict.get("slot") if outcome in ("dropped", "expired") else None,
                }
    
    print(f"Diagnostic inputs:")
    print(f"- Lifecycle events: {len(lifecycle_events_raw)}")
    print(f"- Finalized tasks: {len(finalized_tasks)}")
    print(f"- Trainer completed: {completed_count}")
    print(f"- Trainer dropped: {dropped_count}")
    
    diagnostic_output = diagnose(
        timing_audit={},
        lifecycle_events=lifecycle_events_raw,
        finalized_tasks=finalized_tasks,
        trainer_completed=completed_count,
        trainer_dropped=dropped_count
    )
    
    evidence_text = format_evidence(diagnostic_output)
    evidence_path = "docs/run-logs/2026-06-30-completion-accounting-mismatch-diagnostic-evidence.md"
    with open(evidence_path, "w") as f:
        f.write(evidence_text)
    print(f"Evidence report written to: {evidence_path}")
    
    json_path = "artifacts/analysis/completion-accounting-mismatch-diagnostic/diagnostic_output.json"
    with open(json_path, "w") as f:
        json.dump(diagnostic_output, f, indent=2, default=str)
    print(f"Diagnostic output written to: {json_path}")
    
    verdict = diagnostic_output["verdict"]
    summary = diagnostic_output["accounting_summary"]
    
    print("\n=== DIAGNOSTIC RESULTS ===")
    print(f"Verdict: {verdict}")
    print(f"Execution completed count: {summary['execution_completed_count']}")
    print(f"Finalized completed count: {summary['finalized_completed_count']}")
    print(f"Finalized dropped count: {summary['finalized_dropped_count']}")
    print(f"Trainer completed task count: {summary['trainer_completed_task_count']}")
    print(f"Trainer dropped task count: {summary['trainer_dropped_task_count']}")
    print(f"Mismatch task IDs: {summary['mismatch_task_ids']}")
    
    return {"verdict": verdict, "summary": summary, "evidence_path": evidence_path, "json_path": json_path}


if __name__ == "__main__":
    result = main()
    print(f"\nPilot with diagnostic completed successfully.")