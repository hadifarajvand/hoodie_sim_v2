# Reward Equation and Terminal Reward Contract Report

- feature_id: `029-reward-equation-terminal-reward-contract`
- schema_version: `1.0`
- final_verdict: `paper_backed_with_assumption_backed_aggregation`

## Recovered Equations
- Eq. `20`: `r_n(t+1) = NaN if x_n(t)=0; r_n(t+1) = -Phi_n(t) if successfully processed before timeout; r_n(t+1) = -C otherwise (task thrown)` [paper_backed]
- Eq. `21`: `Phi_n(t) = Phi_n^priv(t) if d_n^(1)=1; Phi_n(t) = Phi_n^pub(t) if d_n^(1)=0` [paper_backed]
- Eq. `22`: `Phi_n^priv(t) = psi_n^priv(t) - t + 1` [paper_backed]
- Eq. `23`: `Phi_n^pub(t) = sum over k in N \ {n} of sum over t' = t..T d_n,k^(2)(t) * (psi_n,k^pub(t') - t + 1)` [paper_backed_with_ocr_noise_caveat]
- Eq. `24`: `pi_n* = arg max over pi_n E[ sum_{t in T} gamma^(t-1) * r_n(t) | pi_n ]` [paper_backed]

## Reward Contract
- success_reward_formula: `-Phi_n(t)`
- reward_unit_policy: `negative_cost_in_slot_based_delay_units`
- drop_penalty_formula: `-C`
- no_task_reward_policy: `omitted_or_nan_not_numeric_zero`
- delay_cost_formula: `Phi_n(t) selected by private/local or public/offloaded delay cost`
- terminal_timing_policy: `terminal_event_reward_with_origin_task_trace_link`
- aggregation_policy: `assumption_backed`

## Runtime Audit
- selected_action_emits_reward: `False`
- reward_emitted_timing: `terminal_completion_or_drop`
- no_task_reward_runtime: `omitted_or_nan_not_numeric_zero`
- local_path: `HoodieGymEnvironment.step -> finalize_task_runtime_state_with_parameters -> emit_delayed_reward -> reward_for_terminal_task`
- offloaded_path: `HoodieGymEnvironment.step -> finalize_task_runtime_state_with_parameters -> emit_delayed_reward -> reward_for_terminal_task`

## Traceability Audit
- trace_linked: `True`
- lifecycle_events: `selected_action, queued_public, offloaded_cloud, transmission_started, transmission_completed, execution_started, execution_completed, dropped_timeout, reward_emitted`

## Final Verdict
paper_backed_with_assumption_backed_aggregation
