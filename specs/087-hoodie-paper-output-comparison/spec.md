# Feature 087: HOODIE Paper Output Comparison

## Purpose

Feature 087 compares the repository's HOODIE simulator outputs against the reported evaluation outputs of the HOODIE paper.

This feature starts only after Feature 086 declared:

`system_model_fidelity_ready_for_output_comparison`

Feature 087 must carry forward every Feature 086 approximation as a claim boundary. It must not claim exact full empirical reproduction unless the evidence proves it.

## Scope

Feature 087 must:

1. Extract the paper's reported output metrics, scenarios, figures, tables, and qualitative result claims from the HOODIE paper.
2. Map paper outputs to simulator-generated outputs.
3. Use only approved paper-comparison metrics unless the paper explicitly supports additional metrics.
4. Generate comparison artifacts showing simulator output, paper output/reference, absolute difference, relative difference where possible, and interpretation.
5. Clearly separate paper-comparison metrics from repository diagnostics.
6. Produce a final report that says whether the simulator outputs are aligned, partially aligned, divergent, or not comparable.

## Required Claim Boundary

Feature 087 comparison is performed under documented Feature 086 approximations, including:

- three-tier topology approximation;
- edge agent/cloud representation approximation;
- horizontal legality model approximation;
- vertical cloud path approximation;
- task/workload approximation;
- queue behavior approximation;
- local/offloading/public queue evidence-layer modeling;
- local/horizontal/vertical delay evidence-layer modeling;
- waiting/completion timing approximation;
- timeout/drop semantics approximation;
- two-stage decision boundary approximation;
- reward/cost boundary approximation.

These approximations do not block comparison, but they must be included in the final interpretation.

## Approved Paper-Comparison Metrics

Allowed as paper-comparison candidates:

- `task_completion_delay`
- `task_drop_ratio`
- `completion_rate`
- `average_reward`
- `total_reward`
- `throughput`

Repository diagnostics only unless the paper directly supports them:

- `timeout_drop_rate`
- `unavailable_drop_rate`
- `deadline_violation_rate`
- `queue_stability_score`
- `illegal_action_rejection_count`

## Required Paper Output Extraction

The implementation must inspect:

- `resources/papers/hoodie/ocr/merged.txt`
- `resources/papers/hoodie/original/HOODIE_paper.pdf` when OCR is ambiguous for figures/tables/values

Extract:

- paper figures and captions;
- paper tables;
- metrics reported in text;
- scenario variables / x-axes;
- compared policies;
- reported qualitative claims;
- numeric values if explicitly available;
- digitized/approximated values only if documented as approximations.

## Out of Scope

- No thesis method.
- No DCQ.
- No custom queue redesign.
- No new proposed method.
- No new HOODIE algorithm change unless a verified paper-output comparison bug is found and separately documented.
- No full empirical reproduction claim unless exact training, stochastic workload, topology, and paper figures are validated.

## Acceptance Criteria

Feature 087 passes only if:

1. Paper output extraction matrix exists.
2. Simulator output comparison matrix exists.
3. All comparison metrics are classified.
4. Feature 086 approximations are carried forward into the final report.
5. Comparison artifacts are generated under `artifacts/feature_087_paper_output_comparison/`.
6. Final report declares exactly one verdict:
   - `paper_output_comparison_ready`
   - `paper_output_comparison_partial`
   - `paper_output_comparison_blocked`
7. The report does not overclaim full reproduction.
