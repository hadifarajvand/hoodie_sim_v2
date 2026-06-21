# Final production simulation report

**Verdict:** `paper_faithful_simulation_production_ready_for_next_smoke`

**Recommended next step:** `run_extended_medium_smoke`

**Paper source:** `resources/papers/hoodie/original/HOODIE_paper.pdf` (OCR text staged; 17 params extracted)

## Readiness gates
- scope_clean: `True`
- paper_mechanism_map_completed: `True`
- paper_metric_schema_completed: `True`
- workload_feasible_nontrivial: `True`
- completion_nonzero: `True`
- drop_or_deadline_pressure_active: `True`
- reward_reconciliation_passed: `True`
- terminal_reconciliation_passed: `True`
- metric_universe_consistency_passed: `True`
- state_profile_consistent: `True`
- no_nan_inf_state: `True`
- legal_action_only: `True`
- baseline_metrics_valid: `True`
- candidate_metrics_valid: `True`
- claim_safety_passed: `True`
- medium_smoke_completed: `True`

## Per-policy metrics
| policy | budget | completed | dropped | completion | drop | reward_recon | term_recon |
|---|---|---|---|---|---|---|---|
| candidate_learned_policy_at_300 | 300 | 2589 | 6961 | 0.246 | 0.663 | True | True |
| candidate_learned_policy_at_500 | 500 | 2589 | 6961 | 0.246 | 0.663 | True | True |
| candidate_learned_policy_at_750 | 750 | 2589 | 6961 | 0.246 | 0.663 | True | True |
| candidate_learned_policy_at_1000 | 1000 | 2589 | 6961 | 0.246 | 0.663 | True | True |
| fixed_local_policy | None | 2589 | 6961 | 0.246 | 0.663 | True | True |
| fixed_horizontal_policy | None | 1743 | 7778 | 0.166 | 0.740 | True | True |
| fixed_vertical_policy | None | 1413 | 8099 | 0.135 | 0.771 | True | True |
| random_legal_policy | None | 2551 | 7001 | 0.243 | 0.666 | True | True |

## Claim safety
- paper_reproduction_claim_made: `False`
- exact_numerical_reproduction_claim_made: `False`
- performance_superiority_claim_made: `False`
- baseline_superiority_claim_made: `False`
- training_5000_run: `False`
- max_training_budget_executed: `1000`
- energy_metric_status: `not_implemented`
- claim_safety_passed: `True`

## Learning health (extended smoke finding)

- candidate_action_collapse_detected: `True`
- no_learning_progress_detected: `True`
- candidate_action_signature_matches_baseline: `fixed_local_policy`
- learning_health_ok: `False`

> Pipeline is stable and fully reconciled, but the learned candidate degenerated to a single-action policy with no reward/completion improvement across budgets; this is a training/exploration blocker, not a pipeline blocker.

**Recommended next step: `fix_training_stability`** — the pipeline (reconciliation, schema, gates) is stable across budgets 300→1000, but the learned candidate degenerated to a local-only policy with no reward/completion improvement. This is a training/exploration blocker, not a pipeline blocker. No paper-reproduction or superiority claims are made.
