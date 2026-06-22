# Full Paper Campaign — Execution Report

- **Verdict:** `full_campaign_completed_learning_still_blocked`
- **Next step:** `implement_true_per_EA_distributed_models`
- Executed 5000: True | Abort: None | Wall: 1.077 h

## Summary

The full 5000-episode campaign completed successfully with exact reconciliation.
Candidate improved modestly over fixed_local. Candidate nearly matched, but did
not exceed, capacity_proportional_split on completion. Candidate became
local-dominant with late horizontal usage, not a balanced distributed mixed
policy. No paper reproduction, exact numerical reproduction, or superiority claim
is made. Remaining limitation: shared-parameter trainer vs paper per-EA
distributed models.

## Candidate vs comparators (final)

- Final candidate: 0.255 compl / -28.32 rwd-task
- Best candidate: 0.258 compl / -28.28 rwd-task
- fixed_local: 0.246 compl / -28.99 rwd-task
- capacity_split: 0.257 compl / -28.64 rwd-task
- random_legal: 0.243 compl / -29.11 rwd-task

## Learning health

- Local-dominant policy: True
- Exact all-local (fixed_local) signature at final checkpoint: False
- Horizontal action usage emerged after ep4000: True (ep4000 7890/2522/0, ep4500 6585/3827/0, ep5000 6443/3969/0)
- Vertical action usage (final): False
- True balanced mixed / load-spreading policy learned: False
- Completion trend: +0.0081 | Reward/task trend: +0.673
- Candidate vs fixed_local: +0.0081 | Candidate vs capacity_split: -0.0027

> Note: the candidate remains local-dominant, but is no longer exactly all-local at
> late checkpoints — horizontal usage emerged after ep4000.

## Reconciliation

- Reconciled all: True | raw-vs-canonical delta max: 0.0 | terminal coverage: 1.0

## Commit metadata

- runtime_commit_sha: f00d1195dc3e7bc9bd929095e8a1dee73cde2493 (commit the campaign ran from)
- results_commit_sha: afa255984293888d6b183bb2022e9d3c5f4e0b9c (commit storing analyzed artifacts)

## Claim safety

- training_5000_run: True (the 5000 campaign was executed)
- paper_reproduction_claim_made: False
- exact_numerical_reproduction_claim_made: False
- performance_superiority_claim_made: False
- baseline_superiority_claim_made: False
- reward_function_modified: False | environment_semantics_modified: False
- Note: 5000 training was executed, but no reproduction, exact numerical, superiority, or baseline-superiority claim is made.
