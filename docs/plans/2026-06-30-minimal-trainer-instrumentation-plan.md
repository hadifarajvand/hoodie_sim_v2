# Minimal Trainer Instrumentation Plan for Service-Start and Queue-Length Observability

**Date**: 2026-06-30  
**Repository**: /Users/hadi/Documents/GitHub/hoodie_sim_v2  
**Branch**: main  
**Base commit**: 1de43f2cdb125c8a8b1d790ec623f4690ad12f36  
**Classification**: audit (planning only)

## 1. Objective

Add minimal optional observability hooks/probes to the DDQNTrainer and environment to explain zero completions in bounded runs, specifically to observe:
- Service start timing (when a task begins processing after arrival)
- Queue length over time (per-resource queue depths)
- Completion/drop/pending lifecycle events

This instrumentation must be additive and read-only, preserving all existing semantics.

## 2. Evidence Basis

From the read-only task-arrival/completion timing audit (3×200 slots):
- ✅ `first_arrival_slot` observable: tasks arrive as early as slot 0 (mean 99.5)
- ✅ `first_completion_slot` observable: but no completion events recorded (0 completions)
- ✅ `first_drop_slot` observable: 4 drop events observed
- ✅ `reward_events` observable: all rewards negative (drop penalties)
- ❌ `first_service_start_slot` NOT observable: internal service start not exposed
- ❌ `queue_lengths` NOT observable: per-resource queue depths over time not exposed

Key findings:
- Tasks arrive and are processed (actions selected, rewards emitted on terminal states)
- No tasks complete within the 200-slot horizon; some are dropped, some pending at horizon
- The system is making progress (loss values finite, actions legal) but not reaching task completion

## 3. Scope

- **Phase 1 only**
- **HOODIE baseline only** (paper_default path)
- **Instrumentation only** (no semantic changes)
- **Bounded runs only** (max 3×500 slots)
- **No full campaign execution**
- **No figure generation**
- **No Phase 2/DCQ-MADRL work**
- **No hyperparameter tuning**

## 4. Candidate Instrumentation Approach

Introduce an optional `TraceCollector` object that can be passed into diagnostic paths (e.g., `run_task_arrival_completion_timing_audit`, `run_completion_positive_diagnostic`) or directly into `DDQNTrainer._episode_rollout` if needed.

**Design principles:**
- **Optional**: Default `None` or disabled collector; when `None`, no overhead or changes
- **Additive**: Only records events; does not modify actions, rewards, state transitions, or timing
- **Pass-through**: If provided, the trainer/environment calls its methods at key points
- **Stateless accumulation**: Collects timestamped events for post-episode analysis

**Implementation sketch:**
```python
class TraceCollector:
    def __init__(self, enabled=False):
        self.enabled = enabled
        self.events = []  # list of dicts

    def record(self, episode_id, slot, event_type, **metadata):
        if not self.enabled:
            return
        self.events.append({
            "episode_id": episode_id,
            "slot": slot,
            "event_type": event_type,
            **metadata,
        })

    def clear(self):
        self.events = []

    def get_events(self):
        return list(self.events)
```

## 5. Events to Capture

| Event Type | When to Call | Key Metadata |
|------------|--------------|--------------|
| `task_arrived` | When a task is generated and added to pending arrivals | `task_id`, `arrival_slot`, `source_agent_id`, `size_mbits`, `processing_density` |
| `action_selected` | After agent selects an action (before environment step) | `action_id`, `legal_action_mask`, `state_snapshot` (optional) |
| `service_started` | When a task begins processing (moves from pending to active service) | `task_id`, `service_start_slot`, `resource_type` (local/horizontal/vertical), `queue_depth_before` |
| `queue_length_sampled` | Periodic sampling of queue depths (e.g., every slot or on change) | `resource_type`, `queue_depth`, `sample_reason` (`periodic`, `change`) |
| `task_completed` | When a task reaches terminal state with reason "completed" | `task_id`, `completion_slot`, `service_duration_slots`, `reward_emitted` |
| `task_dropped` | When a task reaches terminal state with reason "dropped" | `task_id`, `drop_slot`, `service_duration_slots`, `reward_emitted` |
| `task_pending_at_horizon` | When episode ends with task still in service or queue | `task_id`, `horizon_slot`, `service_duration_slots_so_far`, `remaining_work_estimate` |
| `reward_released` | When reward is made available (terminal transition) | `task_id`, `reward_value`, `terminal_reason` |

## 6. Data Schema

Each event record contains:
- `episode_id`: int (current episode index)
- `slot`: int (current simulation slot)
- `event_type`: str (one of the above)
- `task_id`: str or int (if applicable)
- `action_id`: int (if applicable)
- `queue_name` or `resource_id`: str (e.g., "local_queue_agent_1", "horizontal_offload_queue", "vertical_offload_queue")
- `event_type`: str (as above)
- `metadata`: dict (event-specific details as above)

## 7. Files Likely Affected in Future Implementation

- `src/analysis/full_training_reproduction_campaign/trainer.py`  
  - Modify `DDQNTrainer.__init__` to accept optional `trace_collector`  
  - Pass `trace_collector` to `_episode_rollout`  
  - In `_episode_rollout`, call trace methods at appropriate points (after checking enabled)  
  - Potentially expose queue lengths via environment access (if available)

- `src/analysis/task_arrival_completion_timing_audit.py`  
  - Instantiate optional `TraceCollector` (default disabled)  
  - Pass it to the diagnostic run  
  - Include trace events in the audit report if enabled and non-empty

- `tests/integration/test_task_arrival_completion_timing_audit.py`  
  - Add tests for trace collector functionality  
  - Verify that when enabled, service_start and queue_length events are recorded  
  - Verify that when disabled, behavior is identical to baseline

- New module: `src/analysis/trace_collector.py`  
  - Define the `TraceCollector` class  
  - Provide factory functions for enabled/disabled instances

## 8. Safety Constraints for Future Implementation

- The `TraceCollector` must be **optional** with a default disabled state
- When disabled (`None` or `enabled=False`), the trainer/environment must behave **identically** to the current baseline
- No changes to `CampaignConfig.paper_default()` semantics
- No changes to reward computation, action selection logic, or timing
- No changes to queueing or service mechanics
- Bounded runs must remain ≤ 3×500 slots
- No full campaign execution triggered
- Runtime artifacts (if any) must not be committed to the repository

## 9. Acceptance Criteria for Future Implementation

- **Behavior unchanged with tracing disabled**:  
  All existing tests pass with `trace_collector=None` or `enabled=False`
- **Tracing enabled produces evidence**:  
  When `trace_collector` is enabled, the audit report includes service_start and queue_length events
- **Honest completion reporting**:  
  `completed_task_count` remains accurately reported (no inflation or suppression)
- **Artifacts not committed**:  
  Any runtime trace outputs remain in `artifacts/analysis/` and are not committed

## 10. Decision Gate

After implementing and running the minimal trainer instrumentation:

| Tracing Outcome | Recommended Next Step |
|-----------------|------------------------|
| **Service never starts** (no `service_started` events despite arrivals) | Action/service-dispatch audit plan (investigate why selected actions don't initiate processing) |
| **Service starts but no completion** (service_start events present, but no `task_completed` before horizon) | Service-time/horizon audit plan (investigate if service time per task exceeds horizon, or if preemption occurs) |
| **Completions occur but not counted** (trace shows `task_completed` but audit reports 0 completions) | Minimal completion-accounting repair plan (fix the wiring between environment terminal state and agent's completion counter) |
| **No bug, horizon insufficient** (tasks complete but after horizon; service starts promptly) | Bounded horizon extension plan (increase episode length to capture completions) |

## 11. Non-Goals

- No implementation in this task (planning only)
- No source edits beyond this plan
- No full training or full campaign execution
- No figure generation
- No Phase 2 / DCQ-MADRL work
- No hyperparameter tuning

## 12. Proposed Implementation Order (After This Plan Is Approved)

1. Define `TraceCollector` class in new module `src/analysis/trace_collector.py`
2. Modify `DDQNTrainer` to accept optional trace collector and call trace methods at key points (guarded by enabled flag)
3. Update the task-arrival completion timing audit to optionally use tracing
4. Write tests for trace collector (disabled/enabled behavior)
5. Run instrumented audit (3×200, then optionally 3×500) with tracing enabled
6. Analyze trace output and write evidence report
7. Route to appropriate next step via decision gate above