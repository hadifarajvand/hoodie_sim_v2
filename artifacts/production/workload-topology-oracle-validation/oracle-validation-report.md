# Workload / Topology Oracle Validation

**Verdict:** `mixed_policy_outperforms_fixed_local`
**Classification:** `algorithm_state_action_policy_learning_failure`
**Recommended next step:** `inspect_algorithm_fidelity_against_paper`
**Evaluation episodes:** 100 (episode length 110, calibrated env, no training, no 5000)
**Reconciliation all pass:** True

| policy | completion | drop | reward/task | reward/decision |
|---|---|---|---|---|
| fixed_local | 0.246 | 0.663 | -28.993 | -29.252 |
| fixed_horizontal | 0.166 | 0.740 | -31.499 | -31.781 |
| fixed_vertical | 0.135 | 0.771 | -32.408 | -32.697 |
| random_legal | 0.243 | 0.666 | -29.113 | -29.373 |
| capacity_proportional_split | 0.259 | 0.652 | -28.621 | -28.876 |
| slack_feasibility_oracle | 0.246 | 0.663 | -28.993 | -29.252 |

## Mixed vs fixed_local
- **capacity_proportional_split**: completion gain +0.012, reward/task gain +0.372 -> beats fixed_local: **True**
- **slack_feasibility_oracle**: completion gain +0.000, reward/task gain +0.000 -> beats fixed_local: **False**

## Conclusion
A non-learned mixed policy (capacity_proportional_split) measurably outperforms fixed_local on the paper-faithful calibrated environment, by a modest but consistent margin (completion +0.0121, reward/task +0.372), and it also exceeds random_legal on both metrics. The margin is small, so this is NOT a claim of large headroom; but because a trivial capacity-proportional split (no training) already beats a pure-local policy, the environment ADMITS a better mixed policy that the DRL agent failed to learn. The per-checkpoint collapse to pure-local therefore leaves measurable performance on the table -> the residual issue is policy-learning / algorithm fidelity (state-action discrimination, training budget, exploration), not solely workload bias.