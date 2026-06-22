# Training stability & exploration repair

**Verdict:** `training_stability_repair_blocked` (training-health)  
**Recommended next step:** `inspect_reward_signal`

**Root cause:** missing_epsilon_greedy_exploration_in_training_rollout  
**Fix:** configurable epsilon-greedy exploration enabled in training rollout (paper Algorithm 1 line 16)

## Readiness gates
- reward_reconciliation_passed: `True`
- terminal_reconciliation_passed: `True`
- raw_vs_canonical_reward_delta_zero: `True`
- terminal_coverage_one: `True`
- completion_nonzero: `True`
- drop_or_deadline_pressure_active: `True`
- metric_schema_valid: `True`
- no_nan_inf: `True`
- legal_action_only: `True`
- claim_safety_passed: `True`
- exploration_random_action_ratio_nonzero_during_training: `True`
- q_values_have_nonzero_action_separation: `True`
- completion_or_reward_changes_across_budgets: `True`
- candidate_action_collapse_resolved: `False`
- learning_recovered: `True`

## Epsilon schedule (per budget)
- budget 50: epsilon=0.752, random_ratio=0.883
- budget 100: epsilon=0.505, random_ratio=0.759
- budget 200: epsilon=0.344, random_ratio=0.676
- budget 300: epsilon=0.191, random_ratio=0.602
- budget 500: epsilon=0.050, random_ratio=0.456
- budget 750: epsilon=0.050, random_ratio=0.349
- budget 1000: epsilon=0.050, random_ratio=0.287

## Per-policy (L/H/V = action counts)
| policy | budget | completion | drop | L/H/V | reward_recon | term_recon |
|---|---|---|---|---|---|---|
| candidate_learned_policy_at_50 | 50 | 0.166 | 0.740 | 0/10412/0 | True | True |
| candidate_learned_policy_at_100 | 100 | 0.135 | 0.771 | 0/0/10412 | True | True |
| candidate_learned_policy_at_200 | 200 | 0.135 | 0.771 | 0/0/10412 | True | True |
| candidate_learned_policy_at_300 | 300 | 0.135 | 0.771 | 0/0/10412 | True | True |
| candidate_learned_policy_at_500 | 500 | 0.135 | 0.771 | 0/0/10412 | True | True |
| candidate_learned_policy_at_750 | 750 | 0.135 | 0.771 | 0/0/10412 | True | True |
| candidate_learned_policy_at_1000 | 1000 | 0.246 | 0.663 | 10412/0/0 | True | True |
| fixed_local_policy | None | 0.246 | 0.663 | 10412/0/0 | True | True |
| fixed_horizontal_policy | None | 0.166 | 0.740 | 0/10412/0 | True | True |
| fixed_vertical_policy | None | 0.135 | 0.771 | 0/0/10412 | True | True |
| random_legal_policy | None | 0.243 | 0.666 | 3431/3495/3486 | True | True |

## Learning health
- action_collapse_detected: `True`
- matches_baseline: `fixed_local_policy`
- no_learning_progress: `False`
- learning_health_ok: `False`

No paper-reproduction or superiority claims are made.

## Honest finding

The **exploration-collapse root cause is fixed**: training now explores (epsilon-greedy active, random ratio 0.88->0.29), replay diversifies, Q-values separate (gap ~1.19), and the greedy evaluation policy is **no longer frozen** — across budgets it selects horizontal (b=50), vertical (b=100-750), then local (b=1000), i.e. all three single-action signatures appear. **However**, the eval policy still collapses to ONE action per checkpoint (state-insensitive greedy ranking), so strict learning recovery is not achieved. This remaining issue is a reward-signal / state-discrimination problem, NOT exploration. Verdict is therefore blocked for training health with next step `inspect_reward_signal`. No paper-reproduction or superiority claims are made.
