# Tasks: Feature 087 HOODIE Paper Output Comparison

## A. Paper Output Extraction

- [ ] A001 Read `resources/papers/hoodie/ocr/merged.txt` for evaluation/output sections.
- [ ] A002 Use `resources/papers/hoodie/original/HOODIE_paper.pdf` for ambiguous figures/tables/values.
- [ ] A003 Extract all evaluation figures and captions.
- [ ] A004 Extract all evaluation tables.
- [ ] A005 Extract all reported metrics.
- [ ] A006 Extract all compared policies per figure/table.
- [ ] A007 Extract scenario variables and x-axis parameters.
- [ ] A008 Extract numeric values where explicitly available.
- [ ] A009 Mark digitized/estimated values as approximate.
- [ ] A010 Create `paper-output-extraction-matrix.md`.

## B. Simulator Output Inventory

- [ ] B001 Inspect `artifacts/feature_085_full_audit/`.
- [ ] B002 Inspect `artifacts/feature_086_system_model_fidelity/`.
- [ ] B003 Confirm active policy set is exactly `HOODIE`, `RO`, `FLC`, `VO`, `HO`, `BCO`, `MLEO`.
- [ ] B004 Confirm invalid active labels are absent from Feature 087 outputs.
- [ ] B005 Regenerate simulator outputs if needed.
- [ ] B006 Create `simulator-output-inventory.md`.

## C. Metric Alignment

- [ ] C001 Align `task_completion_delay` to paper metric/output.
- [ ] C002 Align `task_drop_ratio` to paper metric/output.
- [ ] C003 Align `completion_rate` if paper supports it or as derived metric.
- [ ] C004 Align `average_reward` if paper reports reward.
- [ ] C005 Align `total_reward` if paper reports total reward or cumulative reward.
- [ ] C006 Align `throughput` if paper reports throughput.
- [ ] C007 Mark `timeout_drop_rate` as diagnostic unless paper explicitly supports it.
- [ ] C008 Mark `unavailable_drop_rate` as diagnostic unless paper explicitly supports it.
- [ ] C009 Mark `deadline_violation_rate` as diagnostic unless paper explicitly supports it.
- [ ] C010 Mark `queue_stability_score` as repository diagnostic.
- [ ] C011 Mark `illegal_action_rejection_count` as repository diagnostic.
- [ ] C012 Create `metric-alignment-matrix.md`.

## D. Comparison Artifacts

- [ ] D001 Generate `artifacts/feature_087_paper_output_comparison/paper_output_extraction.json`.
- [ ] D002 Generate `artifacts/feature_087_paper_output_comparison/paper_output_extraction.md`.
- [ ] D003 Generate `artifacts/feature_087_paper_output_comparison/simulator_output_inventory.json`.
- [ ] D004 Generate `artifacts/feature_087_paper_output_comparison/simulator_output_inventory.md`.
- [ ] D005 Generate `artifacts/feature_087_paper_output_comparison/metric_alignment_matrix.json`.
- [ ] D006 Generate `artifacts/feature_087_paper_output_comparison/metric_alignment_matrix.md`.
- [ ] D007 Generate `artifacts/feature_087_paper_output_comparison/comparison_by_metric.json`.
- [ ] D008 Generate `artifacts/feature_087_paper_output_comparison/comparison_by_metric.csv`.
- [ ] D009 Generate `artifacts/feature_087_paper_output_comparison/comparison_by_policy.json`.
- [ ] D010 Generate `artifacts/feature_087_paper_output_comparison/comparison_by_policy.csv`.
- [ ] D011 Generate `artifacts/feature_087_paper_output_comparison/figure_comparison_coverage.json`.
- [ ] D012 Generate `artifacts/feature_087_paper_output_comparison/ranking_agreement.json`.
- [ ] D013 Generate final report JSON and Markdown.

## E. Report Requirements

- [ ] E001 Carry forward Feature 086 approximation boundary.
- [ ] E002 Report paper figure/table coverage.
- [ ] E003 Report comparable vs non-comparable outputs.
- [ ] E004 Report numeric differences where paper values exist.
- [ ] E005 Report ranking agreement by metric/policy.
- [ ] E006 Report qualitative agreement/disagreement.
- [ ] E007 Separate paper-comparison metrics from repository diagnostics.
- [ ] E008 Declare one verdict: `paper_output_comparison_ready`, `paper_output_comparison_partial`, or `paper_output_comparison_blocked`.
- [ ] E009 Avoid full empirical reproduction claims unless evidence supports them.

## F. Validation

- [ ] F001 Run `git diff --check`.
- [ ] F002 Run runtime evaluation unit tests.
- [ ] F003 Run relevant output-comparison unit tests.
- [ ] F004 Run relevant integration tests.
- [ ] F005 Validate Feature 085 artifacts.
- [ ] F006 Validate Feature 086 artifacts.
- [ ] F007 Generate and validate Feature 087 artifacts.
- [ ] F008 Commit with `Implement Feature 087 HOODIE paper output comparison`.
