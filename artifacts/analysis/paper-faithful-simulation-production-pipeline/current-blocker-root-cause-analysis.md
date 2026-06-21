# Current blocker root-cause analysis (Feature 072)

- reward_reconciliation_passed: `False`
- terminal_reconciliation_passed: `False`
- raw_vs_canonical_reward_delta_max: `3400.0`
- root_cause: `horizon_finalized_tasks_counted_as_reward_bearing_without_reward_emitted_event`
- fix_class: `analysis_only_reconciliation_repair`

## Answers

- **q1_why_completion_nonzero_but_reward_unreconciled**: Decision-time state injection restored feasible action selection so tasks complete, but it shifted transition timing so ~75-85 more tasks per campaign are force-finalized at the episode horizon via info['finalized_tasks']. Those tasks carry terminal_outcome completed/dropped but no reward_emitted event; canonical recompute assigns them reward while raw event stream does not -> positive delta exceeding 1e-9 tolerance.
- **q2_why_terminal_unreconciled**: raw_terminal_event_count counts only env reward/terminal trace events; canonical_terminal_task_count additionally includes horizon-finalized tasks, so the two universes differ -> terminal_reconciled false.
- **q3_failure_location**: analysis/aggregation (canonical reconstruction in repaired_terminal_evaluator), NOT environment, reward, or policy code.
- **q4_replay_transition_consistency**: ReplayTransition stores action-time state/action/reward/next_state consistently; the divergence is in post-hoc reconciliation, not the stored transitions.
- **q5_multiple_finalized_tasks_per_step**: Multiple finalized_tasks per env.step are iterated correctly, but each is counted canonical-terminal even without a reward_emitted event -> over-counting at the horizon.
- **q6_reward_counted**: raw reward is per reward_emitted event (per-task); canonical reward is per completed/dropped task; mismatch arises for horizon-only-terminal tasks.
- **q7_terminal_counted**: raw terminal per trace event (per-task with reward); canonical per completed/dropped task including horizon-finalized.
- **q8_identity_keys**: Both paths use canonical_task_key(trace_id, episode, task_id); identity keys are consistent.
- **q9_state_profile_semantics**: The new state profile changes observation features only; the reconciliation break is a pre-existing boundary condition exposed by timing shift, not a transition-semantics change.
