# Reward-signal / state-action discrimination repair

**Verdict:** `reward_signal_state_action_repair_blocked`  
**Recommended next step:** `inspect_workload_topology_bias`

**Root cause:** per_step_aggregate_reward_misattributed_to_single_decision_broke_credit_assignment  
**Fix:** per-task delayed-reward credit assignment (paper Algorithm 1)

## Readiness gates
- reward_reconciliation_passed: `True`
- terminal_reconciliation_passed: `True`
- raw_vs_canonical_reward_delta_zero: `True`
- terminal_coverage_one: `True`
- metric_schema_valid: `True`
- completion_nonzero: `True`
- drop_or_deadline_pressure_active: `True`
- no_nan_inf: `True`
- legal_action_only: `True`
- claim_safety_passed: `True`
- eval_action_collapse_reduced: `False`
- candidate_no_longer_signature_matches_fixed_local: `False`
- q_values_state_dependent: `True`
- advantage_gap_varies_by_state: `True`
- selected_action_feasible_ratio_improved: `False`
- completion_or_reward_changes_across_budget: `False`
- per_action_return_separation_detected: `True`
- learning_recovered: `False`

## Per-policy (L/H/V = action counts)
| policy | budget | completion | drop | L/H/V | reward_recon | term_recon |
|---|---|---|---|---|---|---|
| candidate_learned_policy_at_50 | 50 | 0.246 | 0.663 | 10412/0/0 | True | True |
| candidate_learned_policy_at_100 | 100 | 0.246 | 0.663 | 10412/0/0 | True | True |
| candidate_learned_policy_at_200 | 200 | 0.246 | 0.663 | 10412/0/0 | True | True |
| candidate_learned_policy_at_300 | 300 | 0.246 | 0.663 | 10412/0/0 | True | True |
| candidate_learned_policy_at_500 | 500 | 0.246 | 0.663 | 10412/0/0 | True | True |
| candidate_learned_policy_at_750 | 750 | 0.246 | 0.663 | 10412/0/0 | True | True |
| candidate_learned_policy_at_1000 | 1000 | 0.246 | 0.663 | 10412/0/0 | True | True |
| fixed_local_policy | None | 0.246 | 0.663 | 10412/0/0 | True | True |
| fixed_horizontal_policy | None | 0.166 | 0.740 | 0/10412/0 | True | True |
| fixed_vertical_policy | None | 0.135 | 0.771 | 0/0/10412 | True | True |
| random_legal_policy | None | 0.243 | 0.666 | 3431/3495/3486 | True | True |

No paper-reproduction or superiority claims are made.
