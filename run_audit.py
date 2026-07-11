#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

from src.analysis.task_arrival_completion_timing_audit import (
    run_task_arrival_completion_timing_audit,
    write_artifacts,
)

def main():
    print("Running bounded audit (3 episodes x 200 slots) with TraceCollector enabled...")
    report = run_task_arrival_completion_timing_audit(episodes=3, episode_length=200)
    json_path, md_path = write_artifacts(report)
    print(f"Audit completed.")
    print(f"JSON report: {json_path}")
    print(f"Markdown report: {md_path}")
    print(f"Verdict: {report['verdict']}")
    # Also print trace info for verification
    trace_info = report.get('trace_info', {})
    print(f"Trace collector enabled: {trace_info.get('trace_collector_enabled')}")
    print(f"Trace event counts: {trace_info.get('trace_event_counts')}")

if __name__ == '__main__':
    main()