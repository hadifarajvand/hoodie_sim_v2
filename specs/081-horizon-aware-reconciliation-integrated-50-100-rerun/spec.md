# Feature 081 — Horizon-Aware Reconciliation Wiring and Integrated 50/100 Campaign Rerun

## Goal
Wire the horizon-aware (recovered-reward) reconciliation from Feature 080 into a
real 50/100 evaluation campaign so campaign-level reward and terminal
reconciliation pass without inheriting Feature 072's failed status.

## Root cause addressed
`horizon_finalized_tasks_counted_as_reward_bearing_without_reward_emitted_event`.
Tasks force-finalized at the episode horizon arrive via `info["finalized_tasks"]`
with `terminal_outcome` completed/dropped but no `reward_emitted` event. The
canonical reconstruction assigned them reward while the raw stream did not,
producing a positive `raw - canonical` delta (max 3400) for all policies.

## Strategy
`horizon_aware_recovered_reward_event`: a horizon-finalized completed/dropped
task with no raw reward event is treated as a *recovered* reward event whose
value is recovered from canonical terminal evidence and explicitly marked. Then
`raw_plus_recovered_reward_total == canonical_reward_total` and
`raw_plus_horizon_terminal_count == canonical_terminal_task_count`.

No environment, reward, policy, or DAL semantics are modified.

## Scope
- Budgets: [50, 100]; max 100; eval episodes 100; episode length 110.
- Calibration: `paper_aligned_feasible_v1`; state profiles:
  `deadline_queue_feasibility_v1` and `legacy_minimal`.
- Policies: candidate (both profiles) at 50/100 + fixed local/horizontal/vertical
  + random legal.

## Entry point
`python -m src.analysis.paper_faithful_simulation_production_pipeline.runner --json --integrated-horizon-aware-rerun`

## Gates
14 readiness gates; verdict `..._ready` only if all 14 pass, otherwise
`..._blocked`.

## Claim safety
No paper-reproduction, exact-numerical, or superiority claims. No training beyond
budget 100.
