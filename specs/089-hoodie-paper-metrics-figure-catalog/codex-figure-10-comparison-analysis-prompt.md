# Codex Prompt: Feature 089 Figure 10 Comparison Analysis

Use this prompt on the same branch. Do not create a new feature or branch.

```text
You are working in repository:

/Users/hadi/Documents/GitHub/hoodie_sim_v2

Current branch:

089-hoodie-paper-metrics-figure-catalog

Goal:

Complete the next Feature 089 step: analyze validated simulator-generated Figure 10a-10f outputs against the HOODIE paper's Figure 10 qualitative claims.

Do not create a new feature. Do not create a new branch.

Source-of-truth files:

- specs/089-hoodie-paper-metrics-figure-catalog/figure-10-comparison-analysis-handoff.md
- specs/089-hoodie-paper-metrics-figure-catalog/paper-figures-8-9-extracted.md
- specs/089-hoodie-paper-metrics-figure-catalog/paper-metrics-extracted.md
- specs/089-hoodie-paper-metrics-figure-catalog/simulator-output-requirements.md
- artifacts/feature_089_paper_metrics_catalog/feature_089_completion_report.json
- artifacts/feature_089_paper_metrics_catalog/figure_10_output_audit.json
- artifacts/feature_089_paper_metrics_catalog/figure_10_analysis_summary.json

Figure 10 input artifacts:

- artifacts/feature_089_paper_metrics_catalog/figure_10a_delay_vs_arrival_probability.csv
- artifacts/feature_089_paper_metrics_catalog/figure_10a_delay_vs_arrival_probability.json
- artifacts/feature_089_paper_metrics_catalog/figure_10b_delay_vs_cpu_capacity.csv
- artifacts/feature_089_paper_metrics_catalog/figure_10b_delay_vs_cpu_capacity.json
- artifacts/feature_089_paper_metrics_catalog/figure_10c_delay_vs_timeout.csv
- artifacts/feature_089_paper_metrics_catalog/figure_10c_delay_vs_timeout.json
- artifacts/feature_089_paper_metrics_catalog/figure_10d_drop_ratio_vs_arrival_probability.csv
- artifacts/feature_089_paper_metrics_catalog/figure_10d_drop_ratio_vs_arrival_probability.json
- artifacts/feature_089_paper_metrics_catalog/figure_10e_drop_ratio_vs_cpu_capacity.csv
- artifacts/feature_089_paper_metrics_catalog/figure_10e_drop_ratio_vs_cpu_capacity.json
- artifacts/feature_089_paper_metrics_catalog/figure_10f_drop_ratio_vs_timeout.csv
- artifacts/feature_089_paper_metrics_catalog/figure_10f_drop_ratio_vs_timeout.json

Required analysis:

For each Figure 10 subfigure:

1. Compute per-sweep policy ranking.
2. Compute aggregate ranking across the sweep.
3. Identify whether HOODIE ranks best, tied-best, near-best, or not-best.
4. Identify whether MLEO ties or diverges from HOODIE.
5. Identify worst or consistently weak baselines.
6. Analyze trend direction across the x-axis.
7. Compare trend/ranking against the paper's qualitative claim.
8. Record whether numeric paper-value comparison is unavailable because values were not digitized.
9. Record whether Feature 088 approximation repair is likely needed before stronger claims.

Metric handling:

- For delay figures 10a, 10b, and 10c, use paper-style negative delay for paper-facing ranking because the paper says average delay is negative by convention. Also preserve raw positive delay in artifacts.
- For drop figures 10d, 10e, and 10f, use lower drop_ratio as better. Preserve both raw ratio and percent.

Paper qualitative claims to check:

- Figure 10a: HOODIE should achieve lower average delay across task-arrival-probability sweeps; MLEO is strong but should fall behind HOODIE at high load.
- Figure 10d: HOODIE should achieve the lowest drop ratio across task-arrival-probability sweeps; FLC and HO are weak at high load; MLEO is competitive but struggles in extreme conditions.
- Figure 10b: increasing CPU capacity should generally reduce average delay; HOODIE should remain better than baselines.
- Figure 10e: increasing CPU capacity should generally reduce drop ratio; HOODIE should show strong reduction, especially at low CPU capacity.
- Figure 10c: increasing timeout from 9.6 to 10.4 sec should slightly improve average delay; HOODIE should remain lower-delay than baselines.
- Figure 10f: increasing timeout from 1.6 to 2.4 sec should reduce drop ratio; HOODIE should maintain the lowest drop ratio.

Required output artifacts under artifacts/feature_089_paper_metrics_catalog/:

- figure_10_trend_analysis.json
- figure_10_trend_analysis.md
- figure_10_ranking_analysis.json
- figure_10_ranking_analysis.md
- figure_10_paper_claim_alignment.json
- figure_10_paper_claim_alignment.md
- figure_10_comparison_analysis_report.json
- figure_10_comparison_analysis_report.md

Optional but preferred:

- figure_10a_plot_ready.csv
- figure_10b_plot_ready.csv
- figure_10c_plot_ready.csv
- figure_10d_plot_ready.csv
- figure_10e_plot_ready.csv
- figure_10f_plot_ready.csv

Final verdict must be exactly one of:

- figure_10_comparison_analysis_ready
- figure_10_comparison_analysis_partial
- figure_10_comparison_analysis_blocked

Use `figure_10_comparison_analysis_partial` if paper numeric values were not digitized and the analysis is qualitative/trend/ranking-based only.

Scope constraints:

- Do not introduce thesis method.
- Do not introduce DCQ.
- Do not redesign queues.
- Do not modify HOODIE or baseline policy semantics.
- Do not claim full empirical paper reproduction.
- Carry Feature 086 approximations.
- Carry Feature 080 training/LSTM boundary.
- Keep Figure 9 blocked/reference-only unless actual simulator support is implemented and validated.
- Keep Figure 8 and Figure 11 future-required unless trained DRL/LSTM artifacts exist.

Validation commands:

- git diff --check
- src/.venvmac/bin/python -m unittest tests.unit.test_hoodie_paper_metrics_figure_catalog
- src/.venvmac/bin/python -m unittest tests.integration.test_hoodie_paper_metrics_figure_catalog_report
- src/.venvmac/bin/python -m analysis.hoodie_paper_metrics_figure_catalog --generate-artifacts --validate-artifacts --artifact-dir artifacts/feature_089_paper_metrics_catalog

Add tests or extend existing tests to validate the new Figure 10 trend/ranking/claim-alignment artifacts.

Commit message:

Add Feature 089 Figure 10 comparison analysis

Final response must include:

- branch name
- final commit SHA
- files changed
- commands run and results
- generated analysis artifact paths
- final verdict
- whether paper numeric digitization was performed
- whether analysis is numeric, qualitative, ranking-based, or mixed
- whether HOODIE matches paper claims by figure
- whether Feature 088 repair is recommended before stronger claims
```
