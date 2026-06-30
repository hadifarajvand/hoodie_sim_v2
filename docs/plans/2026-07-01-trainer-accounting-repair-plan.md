# Trainer Accounting Repair Plan

## 1. Objective

Repair trainer completion/drop accounting so `finalized_tasks` are counted by unique `task_id` and final `terminal_outcome`, not duplicate per-step entries.

## 2. Evidence Basis

- Completion accounting mismatch diagnostic accepted (`docs/run-logs/2026-07-01-completion-accounting-mismatch-diagnostic-evidence.md`)
- Bounded 3×200 paper_default run:
  - `finalized_dropped_count = 3`
  - `trainer_dropped_task_count = 4`
  - `aggregate_dropped_diff = 1`
- Root cause: `trainer.py` line 368-369 counts per-entry, not per-unique-task-id
- Execution-completed tasks all ended as dropped (not completed), so no blind `completed_task_count = execution_completed_count` repair

## 3. Scope

- Phase 1 only
- HOODIE baseline only, paper_default path
- Minimal accounting repair only
- No reward/action/timing/queue/task-generation semantic changes
- No full campaign, no figure generation, no Phase 2/DCQ-MADRL, no hyperparameter tuning

## 4. Source Areas to Inspect Before Repair

| File | Relevance |
|------|-----------|
| `src/analysis/full_training_reproduction_campaign/trainer.py` | Lines 360-369, 725-730: per-entry counter loops |
| `src/analysis/task_arrival_completion_timing_audit.py` | Similar accounting patterns |
| `src/analysis/completion_accounting_mismatch_diagnostic.py` | Diagnostic will re-validate after repair |
| `tests/` | Tests for rollout summaries, finalized_tasks, dropped/completed counters |

## 5. Proposed Repair Design

### 5.1 Deduplication within each episode rollout

In `_episode_rollout()` (line 360) and `_collect_test_rollout_data()` (line 725):

```
for ft in info.get("finalized_tasks", []):
    tid = str(ft.get("task_id", ""))
    if tid:
        seen_task_ids[tid] = ft  # last outcome wins per task_id
```

Then at episode end, count from `seen_task_ids`:

```
for ft in seen_task_ids.values():
    outcome = ft.get("terminal_outcome")
    if outcome == "completed":
        completed_task_count += 1
    elif outcome == "dropped":
        dropped_task_count += 1
```

### 5.2 Preserve existing reward/replay logic

- Reward-bearing transition count must remain unchanged — the step-by-step `reward_available` and `terminal` flags (lines 361-363) are semantically separate from task counting
- Do not alter replay reward values, terminal flags, task finalization, or environment output

### 5.3 Diagnostic comparison

Keep the diagnostic able to compare raw per-entry counts from the runner against the deduplicated trainer counters. The runner's `trainer_completed_total`/`trainer_dropped_total` currently matches the old per-entry logic — after repair, the runner should also deduplicate to match new trainer behavior.

## 6. Required Tests for Future Implementation

| Test | Description |
|------|-------------|
| `test_duplicate_finalized_task_ids_counted_once` | Two finalized_task entries with same task_id → counted as 1 |
| `test_last_terminal_outcome_wins` | Duplicate IDs with different terminal_outcome → last wins |
| `test_completed_and_dropped_unique_counts` | Mix of unique + duplicate IDs → correct per-outcome totals |
| `test_reward_count_separate_from_task_count` | Reward transitions unchanged after dedup |
| `test_existing_bounded_diagnostics_still_pass` | Existing diagnostic + trace tests pass |
| `test_full_campaign_remains_disabled` | No accidental campaign enabling |

## 7. Bounded Validation Plan

1. Run unit/integration tests first
2. Run bounded 3×200 diagnostic after repair
3. Expected post-repair:
   - `trainer_dropped_task_count == finalized_dropped_count` (3)
   - `aggregate_dropped_diff == 0`
   - `trainer_completed_task_count` remains 0 unless `finalized_completed_count > 0`
4. Do not exceed 3×500
5. Do not run full campaign

## 8. Safety Constraints

- No reward logic changes
- No environment `finalized_tasks` emission changes yet
- No `terminal_outcome` logic changes
- No task generation, queue, timing, or action selection changes
- Do not count `execution_completed` as completed directly
- No runtime artifacts committed

## 9. Acceptance Criteria for Future Repair

- Diagnostic verdict changes away from `diagnostic_needs_trainer_accounting_repair`
- `aggregate_completed_diff == 0`
- `aggregate_dropped_diff == 0`
- Trainer counters equal unique finalized terminal outcomes
- All tests pass
- Bounded run only (≤ 3×500)
- No runtime artifacts committed

## 10. Decision Gate

| Condition | Action |
|-----------|--------|
| Deduplicated trainer counters match finalized outcomes | Close accounting repair, produce updated bounded evidence package |
| Mismatch remains after dedup | Inspect environment finalized_tasks duplicate emission |
| Completed tasks emerge | Verify trainer completed accounting separately |
| Reward count changes unexpectedly | Block and revert |

## 11. Non-Goals

- No implementation in this plan task
- No source edits beyond this plan
- No full campaign
- No figure generation
- No Phase 2/DCQ-MADRL
- No hyperparameter tuning

## 12. Known Diagnostic Cleanup Note

In `completion_accounting_mismatch_diagnostic.py`, `classify_accounting()` line 80 uses `not execution_completed_slot` which treats slot 0 as falsy. Change to `execution_completed_slot is None` in a future cleanup to avoid misclassifying slot 0.
