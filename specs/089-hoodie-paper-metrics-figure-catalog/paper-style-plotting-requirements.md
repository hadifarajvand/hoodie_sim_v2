# Feature 089 Paper-Style Plotting Requirements

## Decision

Continue on the same branch:

`089-hoodie-paper-metrics-figure-catalog`

Do not create a new feature and do not create a new branch.

## Goal

Generate paper-style chart outputs for HOODIE paper Figures 8, 9, 10, and 11.

Paper-style means:

- same figure family and subfigure naming;
- same x-axis variable;
- same y-axis metric;
- same legend/series meaning;
- same caption/description structure;
- same chart intent.

Paper-style does **not** mean:

- same numeric values as the paper;
- tuning outputs to match paper curves;
- changing simulator logic to improve visual agreement;
- fabricating unavailable training/LSTM curves.

The plotted numeric values must come from the repository's generated simulator artifacts or from explicit gated/status artifacts. The paper provides the chart structure, not the plotted values.

## Hard Rule: No Output-Sync Tuning

Do not modify policy, reward, queue, routing, model, or simulator semantics to make plots look closer to the paper.

Allowed:

- create plotting utilities;
- create PNG/SVG/PDF chart artifacts;
- create plot-ready CSV/JSON tables;
- aggregate existing Feature 089 outputs;
- create status/gated placeholder charts for figures that cannot be numerically generated yet;
- preserve claim boundaries in captions and reports.

Forbidden:

- changing HOODIE decisions to separate from MLEO;
- changing baseline logic to create paper-like ranking;
- changing delay/drop/reward formulas to match paper values;
- fabricating training episodes or LSTM ablation curves;
- claiming exact empirical paper reproduction.

## Corrected Status Interpretation

### Figure 9a-9e

Current status: `generated_with_approximation`.

Correct interpretation:

- simulator outputs exist;
- outputs may be generated from deterministic/current-runtime approximations;
- these outputs are usable for our own paper-style plots;
- they are not exact trained-HOODIE reproduction;
- they must carry `support_status`, `approximation_note`, and `claim_boundary`.

Do not describe Figure 9 as merely non-comparable if the output artifacts exist. The correct claim is:

`Figure 9 outputs are available as current-simulator, approximation-tagged outputs and may be plotted with paper-style axes and legends, but must not be claimed as exact paper reproduction.`

### Figure 8a, Figure 8b, and Figure 11

Current status: gated.

Correct interpretation:

- no trained convergence or trained LSTM/no-LSTM numerical traces currently exist;
- do not fabricate numeric curves;
- still create paper-style chart-status artifacts for these figures;
- if no traces exist, output a gated/status plot or report panel that clearly says training/LSTM traces are required;
- if real traces are later added, the same plotting structure should render numeric curves.

The correct claim is:

`Figure 8a, Figure 8b, and Figure 11 chart structures are defined and gated-status artifacts must be emitted now; numeric curve plots require real trained DRL/LSTM traces and must not be faked.`

## Required Paper-Style Chart Families

### Figure 8a

- Chart type: line chart if real training traces exist; gated status panel otherwise.
- x-axis: Training Episode, range 0 to 5000.
- y-axis: Average/Accumulated Reward, arbitrary units.
- Series: learning-rate sweep: `1e-9`, `5e-9`, `1e-8`, `1e-7`, `5e-7`, `7e-7`.
- Current output: gated status artifact unless real training traces exist.

### Figure 8b

- Chart type: line chart if real training traces exist; gated status panel otherwise.
- x-axis: Training Episode, range 0 to 5000.
- y-axis: Average/Accumulated Reward, arbitrary units.
- Series: discount-factor sweep: `0.2`, `0.4`, `0.6`, `0.8`, `0.99`.
- Current output: gated status artifact unless real training traces exist.

### Figure 9a

- Chart type: multi-line chart.
- x-axis: Task Arrival Probability `P`.
- y-axis: Average Reward `(a.u.)`.
- Series: `N=10`, `N=15`, `N=20` if supported; otherwise approximation-tagged supported series.
- Data source: current simulator Figure 9a artifact.

### Figure 9b

- Chart type: grouped bar chart.
- x-axis: Action Type: `Local`, `Horizontal`, `Vertical`.
- y-axis: Actions Count or Action Share.
- Series/groups: task probabilities `0.1`, `0.3`, `0.5`, `0.7`, `0.9`.
- Data source: current simulator Figure 9b artifact.

### Figure 9c

- Chart type: multi-line chart.
- x-axis: CPU Computation Capacity `(GHz)`.
- y-axis: Average Reward `(a.u.)`.
- Series: `N=10`, `N=15`, `N=20` if supported; otherwise approximation-tagged supported series.
- Data source: current simulator Figure 9c artifact.

### Figure 9d

- Chart type: multi-line chart.
- x-axis: Number of Agents `N`.
- y-axis: Average Reward `(a.u.)`.
- Series: `Moderate Traffic`, `Heavy Traffic`, `Extreme Traffic`.
- Data source: current simulator Figure 9d artifact, with approximation metadata.

### Figure 9e

- Chart type: multi-line chart.
- x-axis: Number of Agents `N`.
- y-axis: Average Reward `(a.u.)`.
- Series: `Balanced`, `Horizontal-centric`, `Vertical-centric`.
- Data source: current simulator Figure 9e artifact, with approximation metadata.

### Figure 10a

- Chart type: multi-line chart.
- x-axis: Task Arrival Probability `P`.
- y-axis: Average Delay `(sec)`, paper-style negative delay.
- Series: `HOODIE`, `RO`, `FLC`, `VO`, `HO`, `BCO`, `MLEO`.
- Data source: current simulator Figure 10a artifact.

### Figure 10b

- Chart type: multi-line chart.
- x-axis: CPU Computation Capacity `(GHz)`.
- y-axis: Average Delay `(sec)`, paper-style negative delay.
- Series: `HOODIE`, `RO`, `FLC`, `VO`, `HO`, `BCO`, `MLEO`.
- Data source: current simulator Figure 10b artifact.

### Figure 10c

- Chart type: multi-line chart.
- x-axis: Task Timeout `(sec)`.
- y-axis: Average Delay `(sec)`, paper-style negative delay.
- Series: `HOODIE`, `RO`, `FLC`, `VO`, `HO`, `BCO`, `MLEO`.
- Data source: current simulator Figure 10c artifact.

### Figure 10d

- Chart type: multi-line chart.
- x-axis: Task Arrival Probability `P`.
- y-axis: Drop Ratio `(x100%)`.
- Series: `HOODIE`, `RO`, `FLC`, `VO`, `HO`, `BCO`, `MLEO`.
- Data source: current simulator Figure 10d artifact.

### Figure 10e

- Chart type: multi-line chart.
- x-axis: CPU Computation Capacity `(GHz)`.
- y-axis: Drop Ratio `(x100%)`.
- Series: `HOODIE`, `RO`, `FLC`, `VO`, `HO`, `BCO`, `MLEO`.
- Data source: current simulator Figure 10e artifact.

### Figure 10f

- Chart type: multi-line chart.
- x-axis: Task Timeout `(sec)`.
- y-axis: Drop Ratio `(x100%)`.
- Series: `HOODIE`, `RO`, `FLC`, `VO`, `HO`, `BCO`, `MLEO`.
- Data source: current simulator Figure 10f artifact.

### Figure 11

- Chart type: two-line chart if real trained LSTM/no-LSTM traces exist; gated status panel otherwise.
- x-axis: Training Episode, range 0 to 3000.
- y-axis: Average Delay `(sec)`.
- Series: `Without LSTM`, `With LSTM`.
- Current output: gated status artifact unless real LSTM/no-LSTM training traces exist.

## Required Plot Artifacts

Generate under:

`artifacts/feature_089_paper_metrics_catalog/paper_style_plots/`

Required output files:

- `figure_8a_learning_rate_convergence_status.png`
- `figure_8b_discount_factor_convergence_status.png`
- `figure_9a_reward_vs_arrival_probability.png`
- `figure_9b_action_distribution_vs_arrival_probability.png`
- `figure_9c_reward_vs_cpu_capacity.png`
- `figure_9d_reward_vs_agent_count_traffic.png`
- `figure_9e_reward_vs_agent_count_data_rate.png`
- `figure_10a_delay_vs_arrival_probability.png`
- `figure_10b_delay_vs_cpu_capacity.png`
- `figure_10c_delay_vs_timeout.png`
- `figure_10d_drop_ratio_vs_arrival_probability.png`
- `figure_10e_drop_ratio_vs_cpu_capacity.png`
- `figure_10f_drop_ratio_vs_timeout.png`
- `figure_11_lstm_ablation_status.png`

Also generate:

- `paper_style_plot_manifest.json`
- `paper_style_plot_report.md`

Optional but preferred:

- matching `.svg` files for every PNG.

## Plot Report Requirements

The report must state:

- plot files generated;
- data source for each plot;
- whether plot is numeric or gated/status-only;
- whether output values come from simulator or from status metadata;
- no output-sync tuning was performed;
- Figure 8/11 numeric curves were not faked;
- Figure 9 plots are approximation-tagged current-simulator outputs;
- Figure 10 plots are current-simulator outputs;
- no exact paper reproduction claim.

## Final Verdict

Use exactly one:

- `feature_089_paper_style_plots_ready`
- `feature_089_paper_style_plots_partial`
- `feature_089_paper_style_plots_blocked`

Use `ready` if all required PNGs and manifest/report exist, even if Figure 8/11 are gated-status plots rather than numeric curves.
