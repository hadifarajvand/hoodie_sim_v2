# Tasks: Feature 087 HOODIE Paper Output Comparison

## A. Paper Output Extraction

- [x] A001 Read `resources/papers/hoodie/ocr/merged.txt` for evaluation/output sections.
- [x] A002 Use `resources/papers/hoodie/original/HOODIE_paper.pdf` for ambiguous figures/tables/values.
- [x] A003 Extract all evaluation figures and captions.
- [x] A004 Extract all evaluation tables.
- [x] A005 Extract all reported metrics.
- [x] A006 Extract all compared policies per figure/table.
- [x] A007 Extract scenario variables and x-axis parameters.
- [x] A008 Extract numeric values where explicitly available.
- [x] A009 Mark digitized/estimated values as approximate.
- [x] A010 Create `paper-output-extraction-matrix.md`.

## B. Simulator Output Inventory

- [x] B001 Inspect `artifacts/feature_085_full_audit/`.
- [x] B002 Inspect `artifacts/feature_086_system_model_fidelity/`.
- [x] B003 Confirm active policy set is exactly `HOODIE`, `RO`, `FLC`, `VO`, `HO`, `BCO`, `MLEO`.
- [x] B004 Confirm invalid active labels are absent from Feature 087 outputs.
- [x] B005 Regenerate simulator outputs if needed.
- [x] B006 Create `simulator-output-inventory.md`.

## C. Metric Alignment

- [x] C001 Align `task_completion_delay` to paper metric/output.
- [x] C002 Align `task_drop_ratio` to paper metric/output.
- [x] C003 Align `completion_rate` if paper supports it or as derived metric.
- [x] C004 Align `average_reward` if paper reports reward.
- [x] C005 Align `total_reward` if paper reports total reward or cumulative reward.
- [x] C006 Align `throughput` if paper reports throughput.
- [x] C007 Mark `timeout_drop_rate` as diagnostic unless paper explicitly supports it.
- [x] C008 Mark `unavailable_drop_rate` as diagnostic unless paper explicitly supports it.
- [x] C009 Mark `deadline_violation_rate` as diagnostic unless paper explicitly supports it.
- [x] C010 Mark `queue_stability_score` as repository diagnostic.
- [x] C011 Mark `illegal_action_rejection_count` as repository diagnostic.
- [x] C012 Create `metric-alignment-matrix.md`.

## D. Comparison Artifacts

- [x] D001 Generate `artifacts/feature_087_paper_output_comparison/paper_output_extraction.json`.
- [x] D002 Generate `artifacts/feature_087_paper_output_comparison/paper_output_extraction.md`.
- [x] D003 Generate `artifacts/feature_087_paper_output_comparison/simulator_output_inventory.json`.
- [x] D004 Generate `artifacts/feature_087_paper_output_comparison/simulator_output_inventory.md`.
- [x] D005 Generate `artifacts/feature_087_paper_output_comparison/metric_alignment_matrix.json`.
- [x] D006 Generate `artifacts/feature_087_paper_output_comparison/metric_alignment_matrix.md`.
- [x] D007 Generate `artifacts/feature_087_paper_output_comparison/comparison_by_metric.json`.
- [x] D008 Generate `artifacts/feature_087_paper_output_comparison/comparison_by_metric.csv`.
- [x] D009 Generate `artifacts/feature_087_paper_output_comparison/comparison_by_policy.json`.
- [x] D010 Generate `artifacts/feature_087_paper_output_comparison/comparison_by_policy.csv`.
- [x] D011 Generate `artifacts/feature_087_paper_output_comparison/figure_comparison_coverage.json`.
- [x] D012 Generate `artifacts/feature_087_paper_output_comparison/ranking_agreement.json`.
- [x] D013 Generate final report JSON and Markdown.

## E. Report Requirements

- [x] E001 Carry forward Feature 086 approximation boundary.
- [x] E002 Report paper figure/table coverage.
- [x] E003 Report comparable vs non-comparable outputs.
- [x] E004 Report numeric differences where paper values exist.
- [x] E005 Report ranking agreement by metric/policy.
- [x] E006 Report qualitative agreement/disagreement.
- [x] E007 Separate paper-comparison metrics from repository diagnostics.
- [x] E008 Declare one verdict: `paper_output_comparison_ready`, `paper_output_comparison_partial`, or `paper_output_comparison_blocked`.
- [x] E009 Avoid full empirical reproduction claims unless evidence supports them.

## F. Validation

- [x] F001 Run `git diff --check`.
- [x] F002 Run runtime evaluation unit tests.
- [x] F003 Run relevant output-comparison unit tests.
- [x] F004 Run relevant integration tests.
- [x] F005 Validate Feature 085 artifacts.
- [x] F006 Validate Feature 086 artifacts.
- [x] F007 Generate and validate Feature 087 artifacts.
- [x] F008 Commit with `Implement Feature 087 HOODIE paper output comparison`.
