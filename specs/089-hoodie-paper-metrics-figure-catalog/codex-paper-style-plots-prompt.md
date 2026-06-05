# Codex Prompt: Feature 089 Paper-Style Plots

```text
You are working in repository:

/Users/hadi/Documents/GitHub/hoodie_sim_v2

Current branch:

089-hoodie-paper-metrics-figure-catalog

Goal:

Generate paper-style chart outputs for HOODIE paper Figures 8, 9, 10, and 11 using the repository's own generated simulator outputs and gated/status artifacts.

Do not create a new feature. Do not create a new branch.

Important distinction:
- The chart structure should follow the paper: same figure IDs, x-axis, y-axis, legend/series meaning, and caption intent.
- The plotted numeric values must be our simulator outputs, not paper values.
- Do not tune or modify the simulator to make curves match the paper.

Hard rule:
Do not modify policy, reward, queue, routing, model, or simulator semantics to make outputs closer to the paper.

Allowed changes:
- plotting code;
- artifact formatting;
- plot manifests;
- report generation;
- status/gated plots for unavailable training/LSTM figures.

Forbidden changes:
- changing HOODIE or baseline behavior;
- changing delay/drop/reward calculations;
- fabricating training curves;
- fabricating LSTM ablation curves;
- claiming exact paper reproduction.

Source-of-truth files:
- specs/089-hoodie-paper-metrics-figure-catalog/paper-style-plotting-requirements.md
- artifacts/feature_089_paper_metrics_catalog/output_usage_bundle/figure_10_plot_ready_combined.csv
- artifacts/feature_089_paper_metrics_catalog/output_usage_bundle/figure_9_plot_ready_combined.csv
- artifacts/feature_089_paper_metrics_catalog/output_usage_bundle/figure_output_index.json
- artifacts/feature_089_paper_metrics_catalog/figure_8a_learning_rate_convergence_status.json
- artifacts/feature_089_paper_metrics_catalog/figure_8b_discount_factor_convergence_status.json
- artifacts/feature_089_paper_metrics_catalog/figure_11_lstm_ablation_status.json

Required output directory:

artifacts/feature_089_paper_metrics_catalog/paper_style_plots/

Required PNG plots:
- figure_8a_learning_rate_convergence_status.png
- figure_8b_discount_factor_convergence_status.png
- figure_9a_reward_vs_arrival_probability.png
- figure_9b_action_distribution_vs_arrival_probability.png
- figure_9c_reward_vs_cpu_capacity.png
- figure_9d_reward_vs_agent_count_traffic.png
- figure_9e_reward_vs_agent_count_data_rate.png
- figure_10a_delay_vs_arrival_probability.png
- figure_10b_delay_vs_cpu_capacity.png
- figure_10c_delay_vs_timeout.png
- figure_10d_drop_ratio_vs_arrival_probability.png
- figure_10e_drop_ratio_vs_cpu_capacity.png
- figure_10f_drop_ratio_vs_timeout.png
- figure_11_lstm_ablation_status.png

Optional but preferred:
- matching SVG files for every PNG.

Required manifest/report:
- paper_style_plot_manifest.json
- paper_style_plot_report.md

Plot requirements:

Figure 8a:
- If real trained learning-rate traces exist, line chart with x=Training Episode 0..5000 and y=Average/Accumulated Reward, series alpha_lr = 1e-9, 5e-9, 1e-8, 1e-7, 5e-7, 7e-7.
- If traces do not exist, generate a gated/status plot saying training traces are required. Do not fake curves.

Figure 8b:
- If real trained discount-factor traces exist, line chart with x=Training Episode 0..5000 and y=Average/Accumulated Reward, series gamma = 0.2, 0.4, 0.6, 0.8, 0.99.
- If traces do not exist, generate a gated/status plot. Do not fake curves.

Figure 9a:
- Multi-line chart.
- x=Task Arrival Probability P.
- y=Average Reward (a.u.).
- series=N values or supported approximation series from output bundle.
- Must visibly preserve approximation status in title, subtitle, or caption metadata.

Figure 9b:
- Grouped bar chart.
- x=Action Type: Local, Horizontal, Vertical.
- y=Actions Count or Action Share.
- groups/task probabilities: 0.1,0.3,0.5,0.7,0.9 where available.
- Must use our action-distribution output.

Figure 9c:
- Multi-line chart.
- x=CPU Computation Capacity (GHz).
- y=Average Reward (a.u.).
- series=N values or supported approximation series.

Figure 9d:
- Multi-line chart.
- x=Number of Agents N.
- y=Average Reward (a.u.).
- series=Moderate, Heavy, Extreme traffic.
- Use generated_with_approximation rows only; do not fake unsupported values.

Figure 9e:
- Multi-line chart.
- x=Number of Agents N.
- y=Average Reward (a.u.).
- series=Balanced, Horizontal-centric, Vertical-centric.
- Use generated_with_approximation rows only; do not fake unsupported values.

Figure 10a:
- Multi-line chart.
- x=Task Arrival Probability P.
- y=Average Delay (sec), paper-style negative delay.
- series=HOODIE, RO, FLC, VO, HO, BCO, MLEO.

Figure 10b:
- Multi-line chart.
- x=CPU Computation Capacity (GHz).
- y=Average Delay (sec), paper-style negative delay.
- series=HOODIE, RO, FLC, VO, HO, BCO, MLEO.

Figure 10c:
- Multi-line chart.
- x=Task Timeout (sec).
- y=Average Delay (sec), paper-style negative delay.
- series=HOODIE, RO, FLC, VO, HO, BCO, MLEO.

Figure 10d:
- Multi-line chart.
- x=Task Arrival Probability P.
- y=Drop Ratio (x100%).
- series=HOODIE, RO, FLC, VO, HO, BCO, MLEO.

Figure 10e:
- Multi-line chart.
- x=CPU Computation Capacity (GHz).
- y=Drop Ratio (x100%).
- series=HOODIE, RO, FLC, VO, HO, BCO, MLEO.

Figure 10f:
- Multi-line chart.
- x=Task Timeout (sec).
- y=Drop Ratio (x100%).
- series=HOODIE, RO, FLC, VO, HO, BCO, MLEO.

Figure 11:
- If real trained with-LSTM/no-LSTM traces exist, two-line chart with x=Training Episode 0..3000 and y=Average Delay (sec), series Without LSTM and With LSTM.
- If traces do not exist, generate a gated/status plot saying trained LSTM/no-LSTM traces are required. Do not fake curves.

Implementation notes:
- Prefer a dependency-light matplotlib implementation.
- Do not use seaborn.
- Do not use custom colors unless already standard in the local plotting utility; default matplotlib color cycle is acceptable.
- Every plot should include enough title/subtitle/caption metadata to show whether it is simulator output or gated/status-only.
- The report must explicitly say no output-sync tuning was performed.

Tests and validation:
- Add or update tests to verify all required PNGs exist.
- Verify manifest contains all 14 figures/subfigures.
- Verify Figure 8/11 plots are status/gated if no traces exist.
- Verify Figure 9 plots are marked approximation-tagged.
- Verify Figure 10 plots are simulator-output plots.

Validation commands:
- git diff --check
- src/.venvmac/bin/python -m unittest tests.unit.test_hoodie_paper_metrics_figure_catalog
- src/.venvmac/bin/python -m unittest tests.integration.test_hoodie_paper_metrics_figure_catalog_report
- src/.venvmac/bin/python -m unittest tests.unit.test_hoodie_paper_metrics_output_usage_bundle tests.integration.test_hoodie_paper_metrics_output_usage_bundle
- src/.venvmac/bin/python -m analysis.hoodie_paper_metrics_figure_catalog --generate-artifacts --validate-artifacts --artifact-dir artifacts/feature_089_paper_metrics_catalog

Commit message:
Add Feature 089 paper-style plots

Final response must include:
- branch name
- final commit SHA
- files changed
- commands run and results
- generated plot paths
- final verdict
- confirmation that plotted numeric values are simulator outputs, not paper values
- confirmation that no output-sync tuning was performed
- confirmation that Figure 8/11 numeric curves were not faked
```
