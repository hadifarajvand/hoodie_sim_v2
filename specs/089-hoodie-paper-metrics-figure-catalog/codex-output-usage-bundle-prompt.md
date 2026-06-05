# Codex Prompt: Feature 089 Output Usage Bundle

```text
You are working in repository:

/Users/hadi/Documents/GitHub/hoodie_sim_v2

Current branch:

089-hoodie-paper-metrics-figure-catalog

Goal:

Create a usable output bundle from the already generated Figure 10 and Figure 9 artifacts on the same branch.

Do not create a new feature. Do not create a new branch.

This task is about extracting, organizing, combining, and documenting the outputs we already have. It is not about changing simulator behavior or forcing outputs to match the paper.

Hard rule:
Do not tune, edit, bias, or reshape simulator/model/policy/reward/queue logic to make outputs look closer to the paper. Allowed changes are artifact aggregation, output indexing, plot-ready formatting, validation, and report generation only.

Source-of-truth files:
- specs/089-hoodie-paper-metrics-figure-catalog/output-usage-bundle-handoff.md
- artifacts/feature_089_paper_metrics_catalog/remaining_figure_outputs_report.json
- artifacts/feature_089_paper_metrics_catalog/figure_10_comparison_analysis_report.json
- artifacts/feature_089_paper_metrics_catalog/feature_089_completion_report.json

Input artifacts:

Figure 10:
- artifacts/feature_089_paper_metrics_catalog/figure_10a_delay_vs_arrival_probability.csv
- artifacts/feature_089_paper_metrics_catalog/figure_10b_delay_vs_cpu_capacity.csv
- artifacts/feature_089_paper_metrics_catalog/figure_10c_delay_vs_timeout.csv
- artifacts/feature_089_paper_metrics_catalog/figure_10d_drop_ratio_vs_arrival_probability.csv
- artifacts/feature_089_paper_metrics_catalog/figure_10e_drop_ratio_vs_cpu_capacity.csv
- artifacts/feature_089_paper_metrics_catalog/figure_10f_drop_ratio_vs_timeout.csv

Figure 9:
- artifacts/feature_089_paper_metrics_catalog/figure_9a_reward_vs_arrival_probability.csv
- artifacts/feature_089_paper_metrics_catalog/figure_9b_action_distribution_vs_arrival_probability.csv
- artifacts/feature_089_paper_metrics_catalog/figure_9c_reward_vs_cpu_capacity.csv
- artifacts/feature_089_paper_metrics_catalog/figure_9d_reward_vs_agent_count_traffic.csv
- artifacts/feature_089_paper_metrics_catalog/figure_9e_reward_vs_agent_count_data_rate.csv

Gated figures:
- artifacts/feature_089_paper_metrics_catalog/figure_8a_learning_rate_convergence_status.json
- artifacts/feature_089_paper_metrics_catalog/figure_8b_discount_factor_convergence_status.json
- artifacts/feature_089_paper_metrics_catalog/figure_11_lstm_ablation_status.json

Required output directory:

artifacts/feature_089_paper_metrics_catalog/output_usage_bundle/

Required output files:
- README.md
- figure_output_index.json
- figure_output_index.md
- figure_10_plot_ready_combined.csv
- figure_10_plot_ready_combined.json
- figure_9_plot_ready_combined.csv
- figure_9_plot_ready_combined.json
- figure_10_analysis_digest.md
- figure_9_analysis_digest.md
- gated_figures_status_digest.md
- claim_boundary_digest.md
- output_usage_manifest.json
- output_usage_report.md

Required transformations:

1. Build figure_output_index.
   For each Figure 10a-10f, Figure 9a-9e, Figure 8a, Figure 8b, and Figure 11, include:
   - figure_id
   - figure_family
   - metric
   - status
   - artifact_paths
   - plot_ready_available
   - support_status
   - claim_boundary
   - notes

2. Build combined Figure 10 plot-ready table.
   Normalize rows to columns:
   - figure_id
   - metric
   - policy
   - x_axis_name
   - x_axis_value
   - raw_value
   - paper_style_value
   - value_units
   - claim_boundary

   Delay figures must preserve raw positive delay and paper-style negative delay.
   Drop figures must preserve raw drop ratio and percent.

3. Build combined Figure 9 plot-ready table.
   Normalize rows to columns:
   - figure_id
   - metric
   - policy
   - x_axis_name
   - x_axis_value
   - series_name
   - raw_value
   - support_status
   - approximation_note
   - claim_boundary

   Figure 9 rows generated_with_approximation must remain explicitly marked.

4. Build digest Markdown files.
   - figure_10_analysis_digest.md
   - figure_9_analysis_digest.md
   - gated_figures_status_digest.md
   - claim_boundary_digest.md

5. Build output_usage_manifest.json and output_usage_report.md.
   Final verdict must be exactly one of:
   - feature_089_output_bundle_ready
   - feature_089_output_bundle_partial
   - feature_089_output_bundle_blocked

   Use ready if Figure 10 and Figure 9 outputs are present and indexed, even if Figure 9 is approximation-tagged and Figure 8/11 are gated.

Validation requirements:
- all Figure 10a-10f artifacts are present;
- all Figure 9a-9e artifacts are present;
- Figure 8a/8b/11 gated artifacts are present;
- combined Figure 10 table includes all six Figure 10 subfigures;
- combined Figure 9 table includes all five Figure 9 subfigures;
- claim_boundary fields are populated;
- no fake training/LSTM curves are created;
- no output-sync tuning is performed.

Tests:
Add or update tests to validate the output usage bundle.

Commands to run:
- git diff --check
- src/.venvmac/bin/python -m unittest tests.unit.test_hoodie_paper_metrics_figure_catalog
- src/.venvmac/bin/python -m unittest tests.integration.test_hoodie_paper_metrics_figure_catalog_report
- src/.venvmac/bin/python -m analysis.hoodie_paper_metrics_figure_catalog --generate-artifacts --validate-artifacts --artifact-dir artifacts/feature_089_paper_metrics_catalog

Commit message:
Add Feature 089 output usage bundle

Final response must include:
- branch name
- final commit SHA
- files changed
- commands run and results
- output bundle artifact paths
- final verdict
- explicit confirmation that no output-sync tuning was performed
```
