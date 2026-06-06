# Reward Contract

## Purpose

This contract defines how the HOODIE runtime must represent reward semantics for terminal outcomes without starting DRL training.

## Contract Fields

- `success_reward_formula = -Phi_n(t)`
- `drop_reward_formula = -C`
- `drop_penalty_value = 40`
- `no_task_reward_policy = omitted_or_nan_not_numeric_zero`
- `delay_cost_unit = slots`
- `terminal_timing_policy = terminal_event_reward_with_origin_task_trace_link`
- `aggregation_policy = per_agent_cumulative_then_agent_average`
- `aggregation_classification = assumption_backed_for_exact_reduction_order`

## Evidence Mapping

- Eq. (20): no-task, success, and drop branches
- Eq. (21): private vs public delay-cost selector
- Eq. (22): `Phi_n^priv(t) = psi_n^priv(t) - t + 1`
- Eq. (23): normalized public delay-cost aggregation
- Eq. (24): discounted per-agent policy objective

## Runtime Boundaries

- Reward must not emit at `selected_action`
- Reward must emit only after terminal `completed` or `dropped` lifecycle events
- Reward emission must be trace-linked to the originating task
- Training code is out of scope for edits
