# Completion Accounting Mismatch Diagnostic — Evidence Report

- **Date**: 2026-07-01
- **Source**: `src/analysis/completion_accounting_mismatch_diagnostic.py`
- **Artifacts**: `artifacts/analysis/completion-accounting-mismatch-diagnostic/`
- **Verdict**: `diagnostic_needs_trainer_accounting_repair`

## Bounded Run Configuration

| Parameter | Value |
|-----------|-------|
| Episodes | 3 |
| Slots per episode | 200 |
| Baseline | HOODIE paper_default |
| Trace enabled | Yes |
| Training steps per rollout | 1 |

## Summary Counts

| Counter | Value |
|---------|-------|
| execution_completed_count | 3 |
| lifecycle_task_completed_count | 0 |
| lifecycle_task_dropped_count | 3 |
| finalized_completed_count | 0 |
| finalized_dropped_count | 3 |
| trainer_completed_task_count | 0 |
| trainer_dropped_task_count | 4 |
| aggregate_completed_diff | 0 |
| aggregate_dropped_diff | 1 |
| orphan_finalized_task_ids | [] |

## Classification Breakdown

| Classification | Count |
|----------------|-------|
| execution_completed_then_dropped | 3 |
| pending_or_unknown | 197 |

## Findings

1. **Lifecycle-to-finalized consistency**: 3 tasks with `execution_completed` lifecycle events all have finalized "dropped" entries — lifecycle and finalized tracking are internally consistent.

2. **Trainer overcount**: `trainer_dropped_task_count` (4) exceeds the number of unique finalized-dropped task IDs (3). Root cause: the environment emits duplicate `finalized_tasks` entries for a single task across steps (e.g., first as "completed", later as "dropped"). The trainer's per-entry counter (`+= 1` for each finalized task) double-counts tasks that appear in multiple steps. A deduplicated-by-task-id count would yield 3, matching the lifecycle-to-finalized count.

3. **No orphans**: All finalized task IDs appear in lifecycle events (`orphan_finalized_task_ids: []`).

## Verdict

The trainer's completion/drop counters need repair. The correct fix is to deduplicate `finalized_tasks` by `task_id` before counting, keeping the last occurrence's `terminal_outcome` as the authoritative state for each task.

## Related Tests

```
tests/integration/test_completion_accounting_mismatch_diagnostic.py — 7/7 passed
tests/unit/trace_collector/test_trace_collector_instrumentation.py — 10/10 passed
tests/unit/config/test_paper_default_campaign_config.py — 16/16 passed
```
