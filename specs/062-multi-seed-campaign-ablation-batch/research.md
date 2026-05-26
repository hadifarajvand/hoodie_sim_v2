# Research: Feature 062

## Decision: batch multi-seed and ablation work

Feature 062 intentionally groups multi-seed gating, execution, aggregation, ablation gating, and ablation execution into one feature. Splitting these into small features would be slow and would not add useful control.

## Decision: controlled materialization is acceptable when full execution is too expensive

If local runtime cannot support full multi-seed execution, the implementation may controlled-materialize seed-level results from the existing repaired Feature 060 and Feature 061 artifacts. It must preserve configured versus actual execution budgets and must not fabricate unsupported counts.

## Decision: no claim inflation

Multi-seed and ablation outputs are controlled experiment artifacts only. They must not claim paper reproduction, production performance, or superiority until later documentation and integrity export features decide what is actually supported.

## Decision: ablations must be explicit

Each ablation variant must either produce a result or an exact blocker. Silent skipping is forbidden.
