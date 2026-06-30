# Completion Accounting Mismatch Investigation Plan

- **Verdict**: `bridge_needs_completion_accounting_repair`
- **Basis commit**: `6fdb978b15d780053f1345fc33d46cce17479ed8`
- **Date**: 2026-06-30
- **Status**: planning only — no repair

## 1. Objective

Explain why the environment lifecycle trace reports `execution_completed=8` events while the trainer reports `completed_task_count=0` in a bounded 3×200 run of the HOODIE baseline on the paper_default path.

## 2. Evidence Basis

| Field | Value |
|---|---|
| `completed_task_count` (trainer) | 0 |
| `execution_completed_count` (lifecycle) | 8 |
| `dropped_task_count` (trainer) | 4 |
| `pending_at_horizon_count` (trainer) | 3 |
| `bridged_lifecycle_event_count` | 4,811 |
| `duplicate_bridge_guard_enabled` | True |
| `completion_accounting_mismatch` | True |
| `service_started_observable` | True |
| `service_progress_observable` | True |
| `service_completed_observable` | True |
| `first_service_start_slot` | 0 |
| `deadline_reached` (lifecycle) | 8 |
| `deadline_expired` (lifecycle) | 8 |
| `task_dropped` (lifecycle) | 12 |
| `reward_emitted` (lifecycle) | 8 |
| `reward_released` (lifecycle) | 4 |
| Deduplicated bridge | accepted and verified |
| Trace event counts | plausible (O(n), not O(n²)) |

The exact relationship between `execution_completed`, `task_completed`, `task_dropped`, `deadline_expired`, and `finalized_tasks` is not yet proven.

## 3. Scope

- Phase 1 only
- HOODIE baseline only
- paper_default path
- Investigation and planning only
- No semantic changes to reward, action, timing, queue, or task generation
- No full campaign
- No figure generation
- No Phase 2 / DCQ-MADRL
- No hyperparameter tuning

## 4. Source Areas to Inspect

| File | Relevance |
|---|---|
| `src/environment/gym_adapter.py` | `step()` return shape, `info["finalized_tasks"]`, `info["lifecycle_trace_events"]` |
| `src/environment/environment.py` | Task lifecycle state machine, terminal_outcome assignment, execution phase transitions |
| `src/environment/execution_helper.py` | Execution phase logic, when `execution_completed` is emitted vs when task is truly finished |
| `src/environment/lifecycle_trace.py` | `LifecycleTraceRecorder`, snapshot semantics, event type definitions |
| `src/environment/offload_trace_ledger.py` | Offload/completion trace, task finalization, `finalized_tasks` construction |
| `src/analysis/full_training_reproduction_campaign/trainer.py` | `completed_task_count` counting logic, `dropped_task_count` counting logic, `finalized_tasks` consumption |
| `src/analysis/task_arrival_completion_timing_audit.py` | Audit field definitions, mismatch detection logic |
| Tests covering `finalized_tasks`, `terminal_outcome`, `completion_slot`, reward emission | Verify expected behavior of each lifecycle transition |

## 5. Questions to Answer Before Repair

1. Does `execution_completed` always mean a task's `terminal_outcome` should be `completed`?
   - Or does it signal an execution phase finishing, after which the task may still transition to a different terminal state?

2. Can a task have `execution_completed` and later become `deadline_expired` or `task_dropped`?
   - Sequence question: is `execution_completed` a mid-lifecycle event or a terminal event?

3. Are `execution_completed` events emitted for partial execution phases rather than final task completion?
   - Multi-phase execution could emit multiple `execution_completed` events per task

4. Are completed tasks present in `info["finalized_tasks"]` but missed by the trainer?
   - Does the trainer inspect `finalized_tasks` or rely on a different signal?

5. Does the trainer count completions only from `finalized_tasks`?
   - What is the exact source of `completed_task_count` in the trainer?

6. Are task IDs preserved between lifecycle trace, `finalized_tasks`, replay transitions, and reward events?
   - Can we join lifecycle events to finalized tasks by task_id?

7. Does reward emission use terminal outcome or execution completion?
   - `reward_emitted=8` matches `execution_completed=8` and `deadline_reached=8` — which drives reward?

8. Why does `task_dropped=12` (lifecycle) but `dropped_task_count=4` (trainer)?
   - Is this a deduplication artifact, an aggregation difference, or a real accounting gap?

## 6. Candidate Diagnostic Outputs for Future Implementation

### Per-task lifecycle table

| Column | Source |
|---|---|
| task_id | lifecycle trace / finalized_tasks |
| first_arrival_slot | lifecycle trace `task_arrived` |
| service_start_slot | lifecycle trace `execution_started` |
| execution_completed_slot | lifecycle trace `execution_completed` |
| deadline_expired_slot | lifecycle trace `deadline_expired` |
| task_completed_slot | lifecycle trace `task_completed` (if exists) |
| task_dropped_slot | lifecycle trace `task_dropped` |
| reward_emitted_slot | lifecycle trace `reward_emitted` |
| finalized_task_terminal_outcome | `info["finalized_tasks"]` |

### Mismatch table

| Column | Source |
|---|---|
| task_id | join key |
| execution_completed_exists | lifecycle trace |
| finalized_task_exists | `info["finalized_tasks"]` |
| finalized_terminal_outcome | `info["finalized_tasks"]["terminal_outcome"]` |
| counted_by_trainer | trainer counter |

### Accounting summary

| Field | Source |
|---|---|
| execution_completed_count | lifecycle trace |
| lifecycle_task_completed_count | lifecycle trace `task_completed` |
| lifecycle_task_dropped_count | lifecycle trace `task_dropped` |
| finalized_completed_count | `finalized_tasks` terminal_outcome=completed |
| finalized_dropped_count | `finalized_tasks` terminal_outcome=dropped/timeout |
| trainer_completed_task_count | trainer counter |
| trainer_dropped_task_count | trainer counter |

## 7. Safety Constraints

- No counter repair until per-task lifecycle evidence proves the correct mapping
- Do not set `completed_task_count` equal to `execution_completed_count` blindly
- Do not change reward logic
- Do not change `terminal_outcome` logic
- Do not change task generation, queues, timing, or action selection
- Artifacts not committed (runtime JSON/MD go to `artifacts/` only, gitignored)

## 8. Bounded Validation Plan for Future Diagnostic

1. Run 3×200 first with per-task lifecycle instrumentation
2. Optionally 3×500 only if 3×200 evidence is inconclusive and safe
3. Do not exceed 3×500
4. No full campaign

## 9. Acceptance Criteria for Future Diagnostic

- Identify each of the 8 `execution_completed` lifecycle events by task_id
- Determine whether each ended as completed, dropped, pending, or unknown
- Determine whether each appeared in `finalized_tasks`
- Determine whether the trainer counter missed a completed task or correctly ignored a non-terminal execution completion
- Produce evidence report and runtime JSON/MD artifacts
- No runtime artifacts committed

## 10. Decision Gate

Based on the diagnostic results, route to exactly one repair path:

| Condition | Action |
|---|---|
| `execution_completed` events correspond to tasks that were later dropped/expired | No repair needed; update interpretation and audit verdict |
| `execution_completed` corresponds to completed tasks absent from `finalized_tasks` | Environment finalization repair plan |
| `finalized_tasks` contains completed tasks but trainer misses them | Trainer accounting repair plan |
| Lifecycle and `finalized_tasks` disagree on terminal state | Lifecycle/finalization consistency repair plan |
| Evidence remains inconclusive | Targeted per-task diagnostic implementation |

## 11. Non-Goals

- No repair in this task
- No source edits beyond this plan
- No full campaign
- No figure generation
- No Phase 2 / DCQ-MADRL
- No hyperparameter tuning
