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
| candidate_learned_policy_at_50 | 50 | 1754 | 7767 | 0.167 | 0.739 | True | True |
| candidate_learned_policy_at_100 | 100 | 2589 | 6961 | 0.246 | 0.663 | True | True |
| candidate_learned_policy_at_200 | 200 | 2589 | 6961 | 0.246 | 0.663 | True | True |
| candidate_learned_policy_at_300 | 300 | 2589 | 6961 | 0.246 | 0.663 | True | True |
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
- max_training_budget_executed: `300`
- energy_metric_status: `not_implemented`
- claim_safety_passed: `True`
