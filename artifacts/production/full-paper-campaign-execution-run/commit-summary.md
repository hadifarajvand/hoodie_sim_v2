# Commit summary

run: execute full paper campaign with guarded config (metadata cleaned)
- Verdict: full_campaign_completed_learning_still_blocked
- Abort: None
- Wall: 1.077 h
- Executed 5000: True (claim_safety.training_5000_run corrected to true).
- Learning health: local-dominant; not exactly all-local at late checkpoints
  (horizontal usage emerged after ep4000); no balanced mixed/load-spreading policy learned.
- runtime_commit_sha: f00d1195dc3e7bc9bd929095e8a1dee73cde2493
- results_commit_sha: afa255984293888d6b183bb2022e9d3c5f4e0b9c
- No reward/env/topology/reconciliation/metric semantics changed; raw result values unchanged; no superiority claims.
