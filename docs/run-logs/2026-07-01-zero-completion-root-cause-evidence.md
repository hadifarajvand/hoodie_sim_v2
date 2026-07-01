# Zero-Completion Root Cause — Evidence Report

- **Date**: 2026-07-01
- **Root cause**: `build_deterministic_trace` in `src/evaluation/trace_protocol.py`
- **Affected path**: paper_default → DDQN trainer → `_build_environment` → `HoodieGymEnvironment.reset()` → `build_deterministic_trace`

## Root Cause

`build_deterministic_trace` (trace_protocol.py:51-76) generates tasks using hardcoded `randint()` ranges that are **completely misaligned** with the paper_default `TrafficConfig` parameters:

| Parameter | paper_default TrafficConfig | build_deterministic_trace | Factor |
|-----------|---------------------------|--------------------------|--------|
| size | 2.0—5.0 mbits | randint(10, 100) | **20× too large** |
| processing_density | 0.297 gcycles/mbit | randint(1, 5) | **3—17× too large** |
| timeout_length | 20 slots | randint(2, 5) | **4—10× too small** |
| source_agent_id | 1—20 | (index % 3) + 1 → 1—3 | **only 3 agents** |
| deadline formula | arrival + phi - 1 | arrival + timeout | **off by 1** |

**Combined effect on cycles_required**: The blueprint `__post_init__` computes `cycles_required = size × processing_density`. With paper_default params this should be `2.0×0.297 = 0.594` to `5.0×0.297 = 1.485` gcycles. Instead the trace produces **10×1=10** to **100×5=500** gcycles — a **10—1000× inflation**.

**Combined effect on deadlines**: With timeout=2—5 slots and `absolute_deadline_slot = arrival + timeout`, a task arriving at slot 0 has deadline at slot 2—5. But `has_expired` uses `>=`. The task expires after 2—5 slots of processing, having consumed only 0.5×2=1.0 at most of its 10—500 required gcycles.

**Agent concentration**: Only agents 1—3 generate tasks, concentrating ~200 tasks on 3 private queues (0.5 gcycles/slot each) instead of spreading across 20 agents.

## Trace Path Confirmation

This root cause applies to **both** the deterministic evaluation path and the active DDQN trainer path:

| Step | File | Line | What happens |
|------|------|------|-------------|
| 1 | `trainer.py:_build_environment` | 170—179 | Creates `HoodieGymEnvironment` **without** `trace_source` argument |
| 2 | `gym_adapter.py:__init__` | 48 | `trace_source` defaults to `None` |
| 3 | `trainer.py:_episode_rollout` | 270 | Calls `env.reset(seed=seed)` |
| 4 | `gym_adapter.py:reset` | 85—93 | `trace_source is None` → else branch → calls `build_deterministic_trace()` |

**Verdict**: The active DDQN paper_default trainer path is **directly confirmed** to use `build_deterministic_trace()` for every episode. The zero-completion symptom arises from the same misaligned task parameters in both paths.

## Confirmed by Diagnostic Run

```
3 × 200 slots, all actions="local" (only legal action due to mask mapping)
600 transitions total
0 completed, 4 dropped, remaining 596 pending in queues
Private queue depth at horizon: 197—200 (all loaded tasks stuck)
Public queue depth: 0 at all times (no offloading possible)
```

## Downstream Impacts

1. **All tasks are structurally infeasible**: Even a minimal task (size=10, density=1) needs 10/0.5=20 slots of compute, but expires in 2—5 slots. Every task that reaches terminal state does so via deadline expiry with `terminal_outcome="dropped"`, never via completion.

2. **Only 4 tasks ever finalized across 3×200 episodes**: The remaining 596 loaded tasks persist in private queues without reaching the deadline (they were loaded too late in the episode and never accumulated enough compute to trigger the `finalize` code path).

3. **Low action diversity**: The paper_action_space 22-action mapping is reduced to always-"local" by `legal_action_mask_to_tuple` (replay.py:69-70) which looks up `mask["legal_action_mask"]` — a key that doesn't exist in the observation dict's 6-key mask. Fallback to `[False]*22` masks all actions, argmax returns index 0 ("local").

4. **Offloading never exercised**: No tasks go to public queues or cloud, so the entire horizontal/vertical action space is dead weight in training.

## If This Were a Fix (diagnostic only — no fix applied)

The fix would be in `build_deterministic_trace`:

```python
# BEFORE (trace_protocol.py:56-58):
size = rng.randint(10, 100)
processing_density = rng.randint(1, 5)
timeout_length = rng.randint(2, 5)
absolute_deadline_slot = arrival_slot + timeout_length

# AFTER (paper_default-consistent):
size = round(rng.uniform(2.0, 5.0), 1)
processing_density = 0.297
timeout_length = 20
absolute_deadline_slot = arrival_slot + timeout_length - 1
```

Additionally `legal_action_mask_to_tuple` should be updated to correctly interpret the paper_default 6-key mask, or the action selection should use the paper 22-action space directly with proper legal mappings.

## Files Changed (for optional evidence only)

| File | Line(s) | Issue |
|------|---------|-------|
| `src/evaluation/trace_protocol.py` | 56—59 | Wrong randint ranges for paper_default |
| `src/evaluation/trace_protocol.py` | 58 | timeout_length too small |
| `src/evaluation/trace_protocol.py` | 59 | deadline formula wrong |
| `src/analysis/full_training_reproduction_campaign/replay.py` | 69—70 | `legal_action_mask_to_tuple` 22-action mode always returns all-False |
| `src/analysis/full_training_reproduction_campaign/replay.py` | 21—28 | `ACTION_INDEX_TO_SEMANTICS_PAPER` maps to `horizontal_N` not in mask |
| `src/analysis/full_training_reproduction_campaign/trainer.py` | 291 | `semantics_to_action_index` uses 3-key map, crashes on paper actions |
