# Feature 089 Remaining Figure Output Implementation Handoff

## Decision

Continue on the same branch:

`089-hoodie-paper-metrics-figure-catalog`

Do not create Feature 090. Do not create a new branch.

## Updated Goal

Feature 089 must now produce the remaining figure-output artifacts that are feasible from the current simulator without changing HOODIE/baseline semantics to make outputs look like the paper.

The project goal for this step is **output availability**, not exact visual or numeric matching against the HOODIE paper.

## Hard Rule: No Output Sync Tuning

Do not tune, edit, bias, or reshape simulator logic to make generated outputs closer to the paper plots.

Allowed:

- add sweep runners;
- add artifact writers;
- add plot-ready CSV/JSON outputs;
- expose existing simulator metrics in figure-specific shape;
- document when a figure is generated from deterministic/current-simulator behavior rather than trained paper behavior.

Forbidden:

- changing HOODIE policy behavior to match a paper curve;
- changing baseline policy behavior to create separation;
- changing reward, delay, drop, or queue semantics only to sync with the paper;
- fabricating training curves or LSTM ablation curves from non-training data;
- claiming exact paper reproduction.

## Current State

Already implemented and accepted:

- Figure 10a-10f simulator outputs exist and are validated.
- Figure 10 comparison analysis exists and is partial/ranking-based.
- Figure 9a-9e are currently reference-only / blocked.
- Figure 8a, Figure 8b, and Figure 11 are future-required / training-LSTM-gated.

## Required Next Implementation

### Priority A: Unblock Figure 9 Outputs

Implement current-simulator output artifacts for Figure 9a-9e using deterministic/current-runtime sweep adapters where feasible.

These outputs must be labeled as current-simulator behavior outputs, not exact trained-paper reproduction.

Required Figure 9 artifacts:

- `figure_9a_reward_vs_arrival_probability.csv`
- `figure_9a_reward_vs_arrival_probability.json`
- `figure_9b_action_distribution_vs_arrival_probability.csv`
- `figure_9b_action_distribution_vs_arrival_probability.json`
- `figure_9c_reward_vs_cpu_capacity.csv`
- `figure_9c_reward_vs_cpu_capacity.json`
- `figure_9d_reward_vs_agent_count_traffic.csv`
- `figure_9d_reward_vs_agent_count_traffic.json`
- `figure_9e_reward_vs_agent_count_data_rate.csv`
- `figure_9e_reward_vs_agent_count_data_rate.json`

Figure 9 requirements:

- Figure 9a: average_reward vs task arrival probability, HOODIE only, curves N=10/15/20 if supported; otherwise include N field and mark unsupported N values honestly.
- Figure 9b: action count/share for Local, Horizontal, Vertical vs task arrival probability, HOODIE only.
- Figure 9c: average_reward vs CPU capacity, HOODIE only, CPU sweep [4,5,6,7,8,9], curves N=10/15/20 if supported.
- Figure 9d: average_reward vs number of agents [10,15,20,25,30] under Moderate/Heavy/Extreme traffic scenarios.
- Figure 9e: average_reward vs number of agents [10,15,20,25,30] under Balanced, Horizontal-centric, and Vertical-centric data-rate scenarios.

If the current simulator cannot truly vary N, traffic ranges, or data-rate configuration, do not fake it. Implement the maximum supported output and include per-row fields:

- `support_status`: `generated`, `generated_with_approximation`, or `not_supported`
- `claim_boundary`
- `approximation_note`

### Priority B: Figure 8 and Figure 11 Gated Output Artifacts

Do not fabricate training or LSTM curves.

For Figure 8a, Figure 8b, and Figure 11, generate explicit gated artifacts that say whether required training/LSTM traces exist.

Required gated artifacts:

- `figure_8a_learning_rate_convergence_status.json`
- `figure_8a_learning_rate_convergence_status.md`
- `figure_8b_discount_factor_convergence_status.json`
- `figure_8b_discount_factor_convergence_status.md`
- `figure_11_lstm_ablation_status.json`
- `figure_11_lstm_ablation_status.md`

If real trained traces are available in the repo, generate plot-ready output from those traces. If not, mark status as:

- `not_generated_training_required` for Figure 8a/8b;
- `not_generated_lstm_training_required` for Figure 11.

Do not generate fake convergence curves from deterministic benchmark rows.

## Required Final Report

Add or update:

- `artifacts/feature_089_paper_metrics_catalog/remaining_figure_outputs_report.json`
- `artifacts/feature_089_paper_metrics_catalog/remaining_figure_outputs_report.md`

The report must state:

- Figure 10 status: already implemented and validated.
- Figure 9 status: generated / partially generated / not supported, by subfigure.
- Figure 8 status: generated from real training traces or gated not-generated.
- Figure 11 status: generated from real LSTM traces or gated not-generated.
- No output-sync tuning was performed.
- No thesis/DCQ/custom method was introduced.
- Feature 086 and Feature 080 claim boundaries were preserved.

## Verdict Values

Use exactly one:

- `feature_089_all_feasible_outputs_generated`
- `feature_089_remaining_outputs_partial`
- `feature_089_remaining_outputs_blocked`

Use `partial` if Figure 9 is only partially supported or Figure 8/11 are correctly gated because trained traces are unavailable.

## Validation Requirements

Validate that:

- Figure 10 artifacts still exist and pass validation.
- Figure 9 artifacts exist for all 9a-9e, even if some rows are `not_supported`.
- Figure 8a/8b/11 status artifacts exist.
- No fake training/LSTM curves are generated.
- No policy/model semantics are modified for output matching.
- All outputs carry claim-boundary fields.
