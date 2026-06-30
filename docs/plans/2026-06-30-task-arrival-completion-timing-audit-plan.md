# Task-Arrival and Completion Timing Audit Plan

**Date**: 2026-06-30  
**Repository**: /Users/hadi/Documents/GitHub/hoodie_sim_v2  
**Branch**: main  
**Base commit**: 226242f09b83ec61d9367072353d6a253a938740  
**Classification**: audit (planning only)

## 1. Objective

Identify why paper_default bounded diagnostics produce dropped/pending tasks but zero completed tasks.

## 2. Evidence Basis

| Run | Bound | completed_task_count | dropped_task_count | pending_at_horizon_count |
|-----|-------|---------------------|--------------------|--------------------------|
| Bounded pilot (3×50) | 3 episodes × 50 slots | 0 | 0 | 3 |
| Completion-positive diagnostic (3×200) | 3 episodes × 200 slots | 0 | 4 | 3 |

Key observations:
- 3×50: no drops, no completions, 3 pending at horizon
- 3×200: 4 drops (episodes 1 and 2), still 0 completions, 3 pending at horizon
- Increasing horizon from 50 to 200 slots produced drops but no completions
- Average reward is -40.0 (negative, driven by drop penalties)
- Loss values are finite and non-zero (537 loss values across 3 episodes at 200 slots)

## 3. Hypotheses to Test

1. **Late task arrivals**: Task arrivals occur too late relative to bounded horizon for any task to complete before episode ends
2. **Service time too long**: Service time / processing density is too large for tasks to complete within 200 slots even when they arrive early
3. **Completion wiring bug**: Queue/service completion event is not wired correctly — the environment may process tasks but not report completion
4. **Reward/completion mismatch**: Reward availability is based on drops but not on completions; completion accounting may be separate from reward accounting
5. **Action selection gap**: Cloud/edge/local service selection may not advance completion state — agent may select actions that do not contribute to task processing
6. **Horizon truncation**: Episode horizon truncates active tasks before completion accounting; tasks that would complete at slot > episode_length are counted as pending, not completed

## 4. Files/Modules to Inspect Later

### Known files
- `src/analysis/full_training_reproduction_campaign/trainer.py` — episode rollout logic, completion/drop counting
- `src/analysis/run_completion_positive_diagnostic.py` — diagnostic runner, metric collection
- `src/analysis/run_bounded_paper_default_pilot.py` — bounded pilot runner
- `src/analysis/full_training_reproduction_campaign/config.py` — CampaignConfig and paper_default settings

### Files to discover
- Environment task generation module (where tasks are created/arrive)
- Reward/completion/drop accounting module (how completions are detected and counted)
- Queue/service model (how tasks are processed, service time calculation)
- Action space definition (what each of the 22 actions does)
- State space definition (74D state composition)

## 5. Proposed Audit Instrumentation

Add per-episode diagnostic probes (read-only, no semantic changes):

| Instrumentation Point | Data Captured |
|-----------------------|---------------|
| `first_arrival_slot` | Slot number when first task arrives in the episode |
| `first_service_start_slot` | Slot number when first task starts being processed |
| `first_completion_slot` | Slot number when first task completes (or None if no completion) |
| `first_drop_slot` | Slot number when first task is dropped |
| `task_service_time_distribution` | List of (arrival_slot, service_start_slot, completion_or_drop_slot, outcome) per task |
| `selected_action_distribution` | Histogram of agent-selected actions per episode |
| `queue_lengths_over_time` | Queue depth sampled every N slots |
| `completion_drop_cause_summary` | Per-task: completed/dropped/pending_at_horizon with cause |

These probes would be added in a separate instrumentation module that wraps the `DDQNTrainer._episode_rollout` method without modifying it.

## 6. Acceptance Criteria for Future Implementation

- Audit report explains why `completed_task_count` is zero in bounded runs
- No semantic changes made during audit (instrumentation is additive only)
- No full campaign run triggered
- Bounded diagnostic remains ≤ 3×500
- Runtime artifacts are not committed to the repository
- Instrumentation module can be removed without affecting trainer behavior

## 7. Risks

- **Model/environment mismatch**: The issue may be that the HOODIE environment is designed for longer horizons (paper uses 5000 episodes × 110 slots); bounded runs may simply be too short
- **Horizon insufficiency**: Completion may require longer than any safe bounded horizon; the paper-default full_campaign_episode_length is 110 slots but the budget is 5000 episodes, meaning convergence occurs over many episodes
- **Missing timing assumptions**: The paper may assume task arrival distributions or service time parameters not yet replicated in our environment
- **False positive bug report**: Risk of identifying a "bug" that is actually correct behavior under short horizons
- **Instrumentation overhead**: Adding probes may slow down bounded runs; should be minimal and removable

## 8. Decision Gate

After audit implementation, route based on findings:

| Finding | Action |
|---------|--------|
| Audit proves horizon too short (tasks arrive but cannot complete in time) | Create bounded horizon extension plan (e.g., 3×500 or longer) |
| Audit proves wiring bug (completions occur but are not counted) | Create minimal repair plan for the affected module |
| Audit proves no bug and no safe bounded completion possible | Require explicit full-campaign approval before proceeding |

## 9. Non-Goals

- No source code changes (planning only)
- No bug fixes
- No full training or full campaign execution
- No figure reproduction
- No Phase 2 / DCQ-MADRL work
- No hyperparameter tuning
- No environment parameter changes

## 10. Proposed Implementation Order (After This Plan Is Approved)

1. Read and map the environment task generation pipeline
2. Read and map the completion/drop accounting pipeline
3. Create instrumentation wrapper module (`src/analysis/task_arrival_audit_instrumentation.py`)
4. Run instrumented bounded diagnostic (3×200, then optionally 3×500)
5. Analyze instrumentation output
6. Write audit report (`docs/run-logs/YYYY-MM-DD-task-arrival-completion-timing-audit.md`)
7. Route to appropriate next step via decision gate above