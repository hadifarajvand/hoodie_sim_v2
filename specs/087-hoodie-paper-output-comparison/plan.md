# Implementation Plan: Feature 087 HOODIE Paper Output Comparison

## Branch

`087-hoodie-paper-output-comparison`

Base branch: `086-mleo-latency-evidence-test`

Base commit at creation: `d70170fc11e7a4975bf5e67ce38c8f5613f8b5e7`

## Goal

Compare simulator outputs against HOODIE paper outputs using only metrics and claims that are supported by the paper and approved by Feature 086.

## Phase 1 — Paper Output Extraction

1. Read `resources/papers/hoodie/ocr/merged.txt`.
2. Use `resources/papers/hoodie/original/HOODIE_paper.pdf` for ambiguous OCR, figures, charts, tables, and captions.
3. Extract:
   - all evaluation figures;
   - all evaluation tables;
   - all metrics reported by the paper;
   - x-axis variables and scenario parameters;
   - policy set used in each comparison;
   - paper qualitative claims;
   - numeric values if directly available;
   - digitized/estimated values only with an explicit approximation label.
4. Create `paper-output-extraction-matrix.md`.

## Phase 2 — Simulator Output Inventory

1. Inspect Feature 085 and Feature 086 artifacts:
   - `artifacts/feature_085_full_audit/`
   - `artifacts/feature_086_system_model_fidelity/`
2. Identify simulator metrics and policy rows available for comparison.
3. Regenerate simulator outputs if needed using the runtime evaluation runner.
4. Preserve active policies exactly:
   - `HOODIE`, `RO`, `FLC`, `VO`, `HO`, `BCO`, `MLEO`
5. Create `simulator-output-inventory.md`.

## Phase 3 — Metric Alignment

1. Use approved paper-comparison metrics:
   - `task_completion_delay`
   - `task_drop_ratio`
   - `completion_rate`
   - `average_reward`
   - `total_reward`
   - `throughput`
2. Mark repository diagnostics separately:
   - `timeout_drop_rate`
   - `unavailable_drop_rate`
   - `deadline_violation_rate`
   - `queue_stability_score`
   - `illegal_action_rejection_count`
3. For every paper metric, classify mapping status:
   - `exact_metric_match`
   - `derived_metric_match`
   - `approximate_metric_match`
   - `not_available_in_simulator`
   - `not_reported_by_paper`
4. Create `metric-alignment-matrix.md`.

## Phase 4 — Output Comparison

For every comparable paper output:

1. Match paper metric, policy set, scenario, and x-axis variable to simulator output.
2. Compute:
   - simulator value;
   - paper value/reference if available;
   - absolute difference;
   - relative difference where meaningful;
   - ranking agreement;
   - qualitative agreement.
3. Mark comparison status:
   - `aligned`
   - `partially_aligned`
   - `divergent`
   - `not_comparable`
4. Create generated artifacts in:
   - `artifacts/feature_087_paper_output_comparison/`

## Phase 5 — Report and Claim Boundary

Final report must include:

- Feature 086 readiness boundary;
- remaining approximations carried forward;
- comparison matrices;
- metric caveats;
- figure/table coverage;
- policy ranking comparison;
- numeric comparison where available;
- qualitative agreement/disagreement;
- final verdict.

Final verdict must be one of:

- `paper_output_comparison_ready`
- `paper_output_comparison_partial`
- `paper_output_comparison_blocked`

## Required Generated Artifacts

Preferred artifact directory:

`artifacts/feature_087_paper_output_comparison/`

Required files:

- `paper_output_extraction.json`
- `paper_output_extraction.md`
- `simulator_output_inventory.json`
- `simulator_output_inventory.md`
- `metric_alignment_matrix.json`
- `metric_alignment_matrix.md`
- `comparison_by_metric.json`
- `comparison_by_metric.csv`
- `comparison_by_policy.json`
- `comparison_by_policy.csv`
- `figure_comparison_coverage.json`
- `ranking_agreement.json`
- `feature_087_paper_output_comparison_report.json`
- `feature_087_paper_output_comparison_report.md`

## Validation

Run:

- `git diff --check`
- unit tests relevant to runtime evaluation and output comparison
- integration tests relevant to generated reports
- Feature 085 artifact validation
- Feature 086 artifact validation
- Feature 087 artifact generation and validation

Do not proceed if Feature 087 report overclaims exact full reproduction.
