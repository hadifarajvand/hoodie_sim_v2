# Feature 089 Same-Branch Completion Handoff

## Decision

Do not create Feature 090 and do not create a new branch. Continue on `089-hoodie-paper-metrics-figure-catalog`.

Feature 089 must own both:

1. the extracted paper Figure 8-11 catalog; and
2. the simulator output and analysis artifacts for the implementable paper figures.

## Current State To Preserve

- Figure 10a-10f are the only `ready_now` simulator-generated outputs.
- Figure 9a-9e are `reference_only` and `blocked_by_simulator_support`.
- Figure 8a, Figure 8b, and Figure 11 are `future_required` because they need trained DRL/LSTM behavior.
- Feature 086 and Feature 080 claim boundaries must be carried forward.

## Required Next Work On This Same Branch

The next implementation pass must complete Feature 089 by doing the following:

1. Audit the current Feature 089 runner and artifacts.
2. Prove whether Figure 10a-10f artifacts are real simulator sweep outputs or static placeholders.
3. If any Figure 10 artifact is static-only, repair generation so Figure 10a-10f are generated from runtime evaluation output or a documented deterministic sweep adapter.
4. Generate final Figure 10 analysis artifacts.
5. Keep Figure 9 blocked/reference-only unless actual simulator support for varying N, data-rate scenarios, reward sweeps, and action-distribution sweeps exists.
6. Keep Figure 8a, Figure 8b, and Figure 11 training/LSTM-gated.
7. Produce a final Feature 089 completion report.

## Required Final Artifacts

Under `artifacts/feature_089_paper_metrics_catalog/`, add or update:

- `figure_10_output_audit.json`
- `figure_10_output_audit.md`
- `figure_10_analysis_summary.json`
- `figure_10_analysis_summary.md`
- `feature_089_completion_report.json`
- `feature_089_completion_report.md`

## Final Verdict Values

Use exactly one:

- `feature_089_complete_for_figure_10_analysis`
- `feature_089_partial_placeholder_outputs_detected`
- `feature_089_blocked`

A complete verdict is allowed only if Figure 10a-10f are generated from simulator/runtime sweep logic or from a documented deterministic sweep adapter that uses current simulator metrics.

## Scope Guard

Do not create a new feature. Do not create a new branch. Do not change HOODIE/baseline semantics. Do not claim Figure 8, Figure 9, or Figure 11 reproduction unless their blockers are actually removed and validated.
