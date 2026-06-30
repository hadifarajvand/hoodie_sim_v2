# Deeper Environment Service-Start Instrumentation Plan

**Date**: 2026-06-30
**Repository**: /Users/hadi/Documents/GitHub/hoodie_sim_v2
**Branch**: main
**Base commit**: 766c430eb8e90f1483c4f1bccd7752c71af9a58b
**Classification**: audit (planning only)

## 1. Objective

Observe service-start events and service progression inside the environment/queue layer to explain zero completions in bounded runs. The current trainer-level TraceCollector can observe arrivals, actions, drops, pending-at-horizon, rewards, and sampled public queue lengths, but cannot observe when or whether a task actually begins processing at the environment level.

## 2. Evidence Basis

- ✅ `task_arrived` observable via trainer TraceCollector
- ✅ `action_selected` observable via trainer TraceCollector
- ✅ `task_dropped` observable via trainer TraceCollector
- ✅ `task_pending_at_horizon` observable via trainer TraceCollector
- ✅ `reward_released` observable via trainer TraceCollector
- ✅ `queue_length_sampled` observable via trainer TraceCollector (public queue lengths only, 12000 samples across 3×200)
- ❌ `service_started` NOT observable via trainer TraceCollector
- ❌ Zero completions remain unexplained (3×200: completed_task_count = 0, dropped = 4, pending_at_horizon = 3)

Key gap: The trainer-level TraceCollector records events at the decision-loop boundary but does not inspect the environment's internal `LifecycleTraceRecorder` events (available in `info["lifecycle_trace_events"]` after each `env.step()`). The environment already emits `execution_started` (via `_record_execution_progress`) and `task_admitted` events internally — these are not surfaced to the trainer's trace.

## 3. Source Audit Basis

### `trainer.py` — TraceCollector call sites
- `_episode_rollout` records: `action_selected`, `task_arrived`, `task_completed`, `task_dropped`, `reward_released`, `task_pending_at_horizon`, `queue_length_sampled`
- `queue_length_sampled` reads `env._public_queues` directly (line 396) — trainer already reaches into env internals
- The environment's `info` dict contains `"lifecycle_trace_events"` (a `snapshot()` of the `LifecycleTraceRecorder`) — the trainer never reads it
- Trainer does not inspect `info.get("lifecycle_trace_events")` to bridge environment-level events into the trace

### `gym_adapter.py` — step flow and LifecycleTraceRecorder use
- `HoodieGymEnvironment.step()` calls `_admit_current_task`, `_progress_offloading_queues`, `_progress_execution_queues`
- Each of these calls `_record_trace_event(...)` which emits into `LifecycleTraceRecorder`
- LifecycleTraceRecorder records: `task_generated`, `task_admitted`, `transmission_started`, `transmission_completed`, `execution_started`, `execution_progress`, `execution_completed`, `deadline_reached`, `deadline_expired`, `task_completed`, `task_dropped`, `reward_emitted`, `pending_at_horizon`
- `_build_info()` includes `"lifecycle_trace_events": self.trace_recorder.snapshot()` (line 641)
- The environment's `lifecycle_trace_events` are a rich per-slot event sequence — they are simply not consumed by the trainer

### `execution_helper.py` — service/dispatch responsibilities
- `step_execution()` consumes compute capacity from a task's `cycles_remaining`
- Returns `ExecutionProgressRecord` with `cycles_before`, `cycles_consumed`, `cycles_after`, `completed`
- Does NOT emit its own trace events — all tracing is done by `gym_adapter.py`'s `_record_execution_progress` and `_maybe_finalize_head` / `_progress_shared_execution_queues`
- The `OffloadTraceLedger` in `_maybe_finalize_head` and `_progress_shared_execution_queues` emits `execution_started` and `execution_completed`

### `lifecycle_trace.py` — trace model
- `LifecycleTraceEvent` dataclass with 45 fields covering task identity, action context, timing, compute cycles, transmission, terminal outcome, reward
- `LifecycleTraceRecorder` with `record()`, `emit()`, `snapshot()`, `clear()` — same pattern as trainer TraceCollector but richer schema
- `LifecycleTraceConfig` with `trace_enabled: bool`

### `offload_trace_schema.py` — event schema
- `OFFLOAD_LIFECYCLE_EVENTS` tuple: `selected_action`, `queued_public`, `offloaded_cloud`, `transmission_started`, `transmission_completed`, `execution_started`, `execution_completed`, `dropped_timeout`, `reward_emitted`

### `offload_trace_ledger.py` — ledger responsibilities
- Per-task `OffloadTraceLedger` tracks event sequences for each task during its lifecycle
- Emits into the OFFLOAD_LIFECYCLE_EVENTS set only
- `snapshot()` returns a tuple of event strings for use in `info["finalized_tasks"][...]["offload_lifecycle_events"]`

## 4. Scope

- Phase 1 only
- HOODIE baseline only
- `paper_default` path only
- Instrumentation only (additive, read-only hooks)
- No semantic changes to reward, action selection, timing, queue ordering, or task generation
- No full campaign execution
- No figure generation
- No Phase 2 / DCQ-MADRL work
- No hyperparameter tuning

## 5. Candidate Deeper Events

| Event | When | Why Needed |
|-------|------|------------|
| `service_enqueue` | Task placed on a private/public queue after admission | Distinguish "admitted to queue" from "actually started processing" |
| `service_started` | First slot where compute cycles are consumed from the task | Pin the exact slot where service begins |
| `service_progressed` | Each slot where cycles_remaining decreases but task not yet done | Track partial progress across slots |
| `service_completed` | Final slot where cycles_remaining reaches zero | Confirm service finished before terminal_outcome |
| `service_dropped` | A task in service is dropped (deadline expired mid-execution) | Distinguish pre-drop service from never-started |
| `queue_depth_changed` | Any enqueue/dequeue changes queue depth | Per-resource queue dynamics (full observable) |
| `task_finalized` | Task leaves the environment's active tracking (`_active_tasks` / `_history`) | Complement terminal_outcome with environment-side lifecycle bookkeeping |
| `lifecycle_trace_recorded` | A batch of environment LifecycleTraceEvents is bridged into the trainer trace | Bulk bridge event — one per step — avoiding event-by-event duplication |
| `reward_released` | Reward is emitted by the environment (already at trainer level) | Already exists; listed for completeness |

## 6. Proposed Instrumentation Architecture

Leverage the existing dual-layer trace system rather than creating a third:

1. **Trainer-layer TraceCollector** (existing): Keep as the high-level loop trace for action selection, arrivals, completions, drops, and queue samples.
2. **Environment-layer LifecycleTraceRecorder** (existing): Already records detailed per-slot lifecycle events. The gap is that these events are not bridged into the trainer's trace or audit report.
3. **Bridge layer** (new): In `_episode_rollout`, after `env.step()` returns, read `info.get("lifecycle_trace_events", [])` and optionally forward them. This could be:
   - (a) A new `lifecycle_trace_recorded` event in the trainer TraceCollector that summarizes or batches the environment events
   - (b) Direct inclusion of `info["lifecycle_trace_events"]` in the audit report alongside trainer trace events
   - (c) Both — keep trainer TraceCollector events as the primary trace, include environment events as supplementary context

Design constraints:
- Reuse existing LifecycleTraceRecorder / lifecycle trace structures — do not duplicate
- The trainer TraceCollector remains the primary analysis interface
- Environment events are read-only snapshots from `info["lifecycle_trace_events"]`
- If deeper queue-level events are needed (e.g., `queue_depth_changed` on every mutation), add them to the environment's LifecycleTraceRecorder — not to a new system
- Preserve the disabled-by-default contract: when `trace_config.trace_enabled=False`, the environment records nothing

## 7. Data Schema

Each bridged or recorded event contains:

| Field | Type | Source | Description |
|-------|------|--------|-------------|
| `episode_id` | int | trainer | Current episode index |
| `slot` | int | trainer | Decision loop slot at time of step |
| `env_slot` | int | environment | Environment's internal `current_slot` (may differ from loop slot if drift occurs) |
| `task_id` | int\|str | environment | Task identifier |
| `resource_id` | str | environment | Specific queue instance identifier (e.g., `"private:1"`, `"public:2:1"`, `"offloading:1:2"`) |
| `resource_type` | str | environment | `private`, `public`, `offloading`, `cloud` |
| `queue_depth_before` | int | environment | Tasks in queue before mutation |
| `queue_depth_after` | int | environment | Tasks in queue after mutation |
| `required_work` | float | environment | `cycles_required` at event time |
| `completed_work` | float | environment | `cycles_consumed` this slot |
| `remaining_work` | float | environment | `cycles_remaining` after this slot |
| `terminal_outcome` | str\|None | environment | `completed`, `dropped`, or `None` if not terminal |
| `lifecycle_event_source` | str | environment | Original event type from LifecycleTraceRecorder (e.g., `"execution_started"`, `"execution_progress"`) |

## 8. Files Likely Affected in Future Implementation

| File | Likely Change |
|------|---------------|
| `src/environment/gym_adapter.py` | May add `queue_depth_changed` events at enqueue/dequeue points; expose lifecycle trace in info if not already |
| `src/environment/execution_helper.py` | No change needed unless richer progress metadata is required |
| `src/environment/lifecycle_trace.py` | May extend `LifecycleTraceEvent` fields if queue-depth tracking is needed |
| `src/environment/offload_trace_schema.py` | May add new event types if queue-layer events require them |
| `src/environment/offload_trace_ledger.py` | No change expected (ledger is per-task offload only) |
| `src/analysis/trace_collector.py` | May add a `lifecycle_trace_recorded` event type or a bridge method |
| `src/analysis/full_training_reproduction_campaign/trainer.py` | May read `info["lifecycle_trace_events"]` and forward to TraceCollector or audit |
| `src/analysis/task_arrival_completion_timing_audit.py` | May include environment trace events in the audit report |
| `tests/integration/test_task_arrival_completion_timing_audit.py` | Add test verifying disabled behavior unchanged; optionally test bridge |
| `docs/run-logs/` | New evidence report after instrumented run |

## 9. Safety Constraints

- All instrumentation must be event hooks only — no changes to reward computation, action selection, timing, compute capacity, or task generation
- All environment-level instrumentation must be guarded by `trace_config.trace_enabled` (already in place)
- All trainer-level instrumentation must be guarded by `trace_collector is not None and trace_collector.enabled` (already in place)
- When disabled, behavior must be provably identical to baseline
- No changes to queue ordering semantics
- No changes to task generation or arrival patterns
- No changes to `paper_default` configuration
- Existing tests must continue to pass with tracing disabled

## 10. Bounded Validation Plan

| Step | Action | Bound | Condition |
|------|--------|-------|-----------|
| 1 | Run instrumented 3×200 | 3 episodes × 200 slots | First validation; must complete |
| 2 | If step 1 shows `service_started` events but zero completions, run 3×500 | 3 episodes × 500 slots | Only if step 1 is safe and informative |
| 3 | Do not exceed 3×500 | Hard cap | No full campaign, no unbounded runs |
| 4 | Do not run full campaign | Hard cap | Only after explicit Phase 1 full-campaign approval gate |

## 11. Acceptance Criteria for Future Implementation

- `service_started` observable: The audit report should honestly report whether any task began processing (true/false, first slot, count)
- `service_progressed` observable: If tasks receive compute cycles, cycles_consumed/remaining should be visible per slot
- `queue_depth_changed` observable: Queue depth changes at enqueue/dequeue are visible per resource
- Lifecycle/finalization path connected: Environment `lifecycle_trace_events` appear in or alongside the audit report
- `completed_task_count` remains honest: No inflation or suppression from the new trace path
- Disabled behavior unchanged: All existing tests pass with tracing disabled
- Artifacts not committed: Runtime outputs stay in `artifacts/analysis/` and are gitignored

## 12. Decision Gate

After implementing and running the instrumented bounded validation:

| Finding | Recommended Next Step |
|---------|-----------------------|
| **Service never starts** (zero `execution_started` / `service_started` events despite arrivals) | Action/service-dispatch audit plan — investigate why selected actions don't result in queue admission → compute dispatch |
| **Service starts but work never decreases** (`execution_started` present but cycles_remaining stays flat across slots) | Service-progress repair/audit plan — investigate compute capacity allocation, zero-consumption slots, or preemption |
| **Service progresses but horizon too short** (cycles_remaining decreases but never reaches zero before episode end) | Bounded horizon extension plan — increase episode length to capture completions |
| **Service completes but count remains zero** (cycles_remaining reaches zero but terminal_outcome not set to `completed`) | Completion-accounting repair plan — fix the wiring between `completion_slot` and `terminal_outcome` |
| **No safe instrumentation point found** (environment trace events are not reliably reachable from trainer) | Environment trace design review — redesign the bridge between environment and trainer trace systems |

## 13. Non-Goals

- No implementation in this task (planning only)
- No source edits beyond this plan
- No full training or full campaign execution
- No figure generation
- No Phase 2 / DCQ-MADRL work
- No hyperparameter tuning
