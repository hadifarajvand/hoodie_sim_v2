# Feature 089: HOODIE Paper Figure Catalog and Simulator Output Extension

## Purpose

Feature 089 has two mandatory parts:

1. Register all HOODIE paper figures 8, 9, 10, and 11 with extracted metric, axis, scenario, policy, and output requirements.
2. Add the required simulator output-extension specification so later implementation can generate the same figure families from our simulator.

This feature must first extract and preserve the paper figure requirements from the OCR and the original PDF. After the figure catalog is accepted, the same feature will implement or extend simulator outputs for the selected figures.

## Source of Truth

Use both paper sources:

- OCR text: `resources/papers/hoodie/ocr/merged.txt`
- Original PDF: `resources/papers/hoodie/original/HOODIE_paper.pdf`

The PDF must be used to resolve OCR ambiguity, especially for figure captions, axis labels, tick values, and Figure 10 timeout-axis values.

## Figure Families To Register

Feature 089 must register these figure families:

- Figure 8: learning parameter and convergence curves
- Figure 9: HOODIE behavior and scalability analysis
- Figure 10: comparative analysis against paper baselines
- Figure 11: LSTM inclusion ablation

## Required Catalog Fields

For every figure/subfigure, record:

- figure ID, for example `Figure 10a`
- paper section
- caption or caption summary
- metric / y-axis
- x-axis variable
- sweep values or ranges when available
- policy set or curve set
- scenario setup
- whether the figure requires training, deterministic evaluation, LSTM, or simulator sweep only
- priority for implementation
- extraction confidence: `high`, `medium`, or `low`
- output status: `required_now`, `later_training_required`, `later_lstm_required`, or `reference_only`
- simulator output requirements
- claim boundary

## Priority Policy

Priority 1: implement simulator outputs first for Figure 10a-10f.

These are the paper's main comparative-analysis figures and must use policies:

- HOODIE
- RO
- FLC
- VO
- HO
- BCO
- MLEO

Priority 2: implement HOODIE behavior figures after Priority 1:

- Figure 9a
- Figure 9b
- Figure 9c
- Figure 9d
- Figure 9e

Priority 3: catalog but do not implement until trained components exist:

- Figure 8a
- Figure 8b
- Figure 11

## Output Extension Scope

The simulator output extension must define future artifact outputs for:

- average task completion delay sweeps
- task drop ratio sweeps
- average reward sweeps
- action distribution sweeps
- convergence curves only when training exists
- LSTM ablation only when trained LSTM behavior exists

## Claim Boundary

Feature 089 does not remove Feature 086 approximations. Output generation must carry forward the Feature 086 claim boundary.

Feature 089 must not claim full empirical reproduction of the HOODIE paper unless the exact training, stochastic workload, topology, and figure digitization requirements are satisfied.

## Out of Scope

- No thesis method
- No DCQ
- No custom queue redesign
- No new proposed method
- No unsupported full empirical paper reproduction claim

## Acceptance Criteria

Feature 089 is acceptable only when:

1. Figures 8, 9, 10, and 11 are fully cataloged.
2. The PDF has been used to verify ambiguous OCR fields.
3. Figure 10a-10f output requirements are marked Priority 1.
4. Simulator output-extension requirements are specified for all required figure families.
5. Training-only and LSTM-only figures are not silently treated as deterministic evaluation figures.
6. Generated artifacts include both machine-readable JSON and human-readable Markdown catalogs.
7. Final report clearly states which figures will be generated now, later, or only cataloged as references.
