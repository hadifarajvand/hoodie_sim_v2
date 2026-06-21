# EULS Phase 32 — Horizon-Aware Reconciliation Integrated 50/100

## Context
Feature 080 identified that the evaluation reconciliation counted horizon-
finalized terminal tasks as reward-bearing even though the environment emits no
`reward_emitted` event for tasks truncated at the episode horizon. Feature 080
implemented and unit-tested the fix in isolation; Feature 081 wires it into the
integrated 50/100 campaign.

## Reward emission semantics (unchanged)
`src/environment/gym_adapter.py::_record_outcome` emits `reward_emitted`
co-located with `task_completed`/`task_dropped`. The reward value is
`-phi_private(completion_slot, arrival_slot)` for completions and `-40` for
drops (`src/environment/reward_timing.py`). The canonical reconstruction uses the
identical formula, so per-task values match; the only divergence was *count* of
reward-bearing tasks at the horizon boundary.

## Recovered-reward strategy
For each evaluated policy, `horizon_aware_recovered_reconciliation` partitions
terminal tasks into:
- raw reward-bearing (has a `reward_emitted` event), and
- horizon-finalized (terminal outcome but no reward event).

Horizon-finalized terminal tasks are recovered: their canonical reward is added
to `raw_plus_recovered_reward_total` and logged in a recovered-reward ledger, so
the raw+recovered universe equals the canonical universe and the delta is 0.0
with `terminal_event_coverage_ratio == 1.0`.

## Discriminator
`raw_reward_event_count == 0` on a completed/dropped task record (the
`terminal_event_source` field is uniformly `env_step_finalized_tasks` and cannot
be used as the discriminator).

## Harness reuse
The campaign reuses `StateRepresentationTrainingSession` (Feature 072) for
training and `evaluate_policy_on_trace_bank_terminal_repaired` for evaluation;
the recovered reconciliation is applied post-hoc to each policy's
`task_records`. No trainer/replay/env file was modified.
