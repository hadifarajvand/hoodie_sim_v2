# Feature 089 Output Usage Bundle Handoff

## Decision

Continue on the same branch:

`089-hoodie-paper-metrics-figure-catalog`

Do not create a new feature and do not create a new branch.

## Goal

Create a usable output bundle from the already generated Figure 10 and Figure 9 artifacts.

The goal is to make the current simulator outputs easy to use for analysis, plotting, thesis discussion, and later report generation.

This is **not** a paper-sync or curve-fitting task.

## Hard Rule: No Output Sync Tuning

Do not modify model, policy, reward, queue, routing, or simulator semantics to make outputs look closer to the HOODIE paper.

Allowed work:

- collect existing artifacts;
- normalize CSV/JSON formats;
- create plot-ready tables;
- create summary tables;
- create a figure-output index;
- create a thesis/report-ready summary;
- preserve claim boundaries and approximation notes.

Forbidden work:

- changing HOODIE behavior to improve paper alignment;
- changing baseline behavior to create separation;
- changing delay/drop/reward formulas to match paper curves;
- fabricating training or LSTM curves;
- claiming exact paper reproduction.

## Inputs

Use existing artifacts under:

`artifacts/feature_089_paper_metrics_catalog/`

Required Figure 10 inputs:

- `figure_10a_delay_vs_arrival_probability.csv/json`
- `figure_10b_delay_vs_cpu_capacity.csv/json`
- `figure_10c_delay_vs_timeout.csv/json`
- `figure_10d_drop_ratio_vs_arrival_probability.csv/json`
- `figure_10e_drop_ratio_vs_cpu_capacity.csv/json`
- `figure_10f_drop_ratio_vs_timeout.csv/json`
- `figure_10_comparison_analysis_report.json/md`
- `figure_10_trend_analysis.json/md`
- `figure_10_ranking_analysis.json/md`
- `figure_10_paper_claim_alignment.json/md`

Required Figure 9 inputs:

- `figure_9a_reward_vs_arrival_probability.csv/json`
- `figure_9b_action_distribution_vs_arrival_probability.csv/json`
- `figure_9c_reward_vs_cpu_capacity.csv/json`
- `figure_9d_reward_vs_agent_count_traffic.csv/json`
- `figure_9e_reward_vs_agent_count_data_rate.csv/json`
- `remaining_figure_outputs_report.json/md`

Gated/reference inputs:

- `figure_8a_learning_rate_convergence_status.json/md`
- `figure_8b_discount_factor_convergence_status.json/md`
- `figure_11_lstm_ablation_status.json/md`

## Required Output Bundle

Create or update these files under:

`artifacts/feature_089_paper_metrics_catalog/output_usage_bundle/`

Required files:

- `README.md`
- `figure_output_index.json`
- `figure_output_index.md`
- `figure_10_plot_ready_combined.csv`
- `figure_10_plot_ready_combined.json`
- `figure_9_plot_ready_combined.csv`
- `figure_9_plot_ready_combined.json`
- `figure_10_analysis_digest.md`
- `figure_9_analysis_digest.md`
- `gated_figures_status_digest.md`
- `claim_boundary_digest.md`
- `output_usage_manifest.json`
- `output_usage_report.md`

## Required Content

### Figure Output Index

For each figure/subfigure, include:

- `figure_id`
- `figure_family`
- `metric`
- `status`
- `artifact_paths`
- `plot_ready_available`
- `support_status`
- `claim_boundary`
- `notes`

### Figure 10 Combined Output

Combine Figure 10a-10f into one plot-ready table with normalized columns:

- `figure_id`
- `metric`
- `policy`
- `x_axis_name`
- `x_axis_value`
- `raw_value`
- `paper_style_value`
- `value_units`
- `claim_boundary`

For delay figures, preserve raw positive delay and paper-style negative delay.

For drop-ratio figures, preserve raw ratio and percent.

### Figure 9 Combined Output

Combine Figure 9a-9e into one plot-ready table with normalized columns:

- `figure_id`
- `metric`
- `policy`
- `x_axis_name`
- `x_axis_value`
- `series_name`
- `raw_value`
- `support_status`
- `approximation_note`
- `claim_boundary`

If a Figure 9 output is generated with approximation, do not hide that fact.

### Digests

Create human-readable Markdown digests:

- Figure 10 digest: what outputs exist, metrics, policies, sweeps, and key analysis result.
- Figure 9 digest: what outputs exist, what is approximate, and what can be plotted.
- Gated figures digest: Figure 8a, 8b, and 11 are not generated because training/LSTM traces are required.
- Claim boundary digest: no output-sync tuning, no exact paper reproduction claim, Feature 086 and Feature 080 boundaries preserved.

## Final Verdict

The output usage report must declare exactly one verdict:

- `feature_089_output_bundle_ready`
- `feature_089_output_bundle_partial`
- `feature_089_output_bundle_blocked`

Use `ready` if Figure 10 and Figure 9 outputs are all indexed and bundle artifacts are generated, even if Figure 9 rows are approximation-tagged and Figure 8/11 are gated.

## Validation Requirements

Validate that:

- all Figure 10a-10f artifacts are present;
- all Figure 9a-9e artifacts are present;
- Figure 8a/8b/11 gated status artifacts are present;
- combined Figure 10 table includes all six subfigures;
- combined Figure 9 table includes all five subfigures;
- claim-boundary fields are not empty;
- no output-sync tuning is claimed or performed;
- no fake training/LSTM curves are included.
