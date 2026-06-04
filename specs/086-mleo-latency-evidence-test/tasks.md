# Tasks: Feature 086 HOODIE System-Model Fidelity Gate

## Current Implementation State

The branch already contains a successful MLEO latency-evidence implementation. Do not redo that as the main deliverable. Preserve it and complete the broader system-model fidelity gate.

## A. Preserve Completed MLEO Work

- [x] A001 Preserve numeric MLEO test where queue-minimum candidate is not delay-minimum candidate.
- [x] A002 Preserve proof that MLEO selects minimum estimated total delay.
- [x] A003 Preserve HOODIE/MLEO tie evidence in Feature 085 audit report/manifest.
- [x] A004 Preserve Feature 085 artifact validation.

## B. Paper System-Model Extraction

- [ ] B001 Read `resources/papers/hoodie/ocr/merged.txt` for Chapter/System-Model obligations.
- [ ] B002 Use `resources/papers/hoodie/original/HOODIE_paper.pdf` only where OCR is ambiguous.
- [ ] B003 Extract topology obligations: task-source/IoT/MD layer, Edge Agents, Cloud.
- [ ] B004 Extract connectivity obligations: horizontal EA-to-EA legality and vertical EA-to-cloud path.
- [ ] B005 Extract task-model obligations: ID, data/input size, CPU demand or processing density, timeout/deadline, arrivals/workload.
- [ ] B006 Extract queue obligations: private/local, offloading, public/cloud.
- [ ] B007 Extract delay obligations: local execution, horizontal transmission, vertical transmission, remote/cloud execution, waiting, completion.
- [ ] B008 Extract drop obligations: timeout, deadline violation, unavailability, illegal action handling if represented.
- [ ] B009 Extract action/decision obligations: local, horizontal, vertical, two-stage boundary or runtime approximation.
- [ ] B010 Extract policy obligations: HOODIE, RO, FLC, VO, HO, BCO, MLEO.
- [ ] B011 Extract reward/cost and output metric obligations.

## C. Code Mapping and Gap Classification

- [ ] C001 Map each paper mechanism to code in `src/analysis/hoodie_runtime_evaluation_runner/`, `src/analysis/hoodie_proposed_method/`, `src/policies/`, tests, and artifacts.
- [ ] C002 Update `system-model-gap-matrix.md` with paper expectation, simulator behavior, code/test/artifact evidence, status, and required fix.
- [ ] C003 Use only statuses: `exact`, `approximate_documented`, `missing`, `wrong`, `not_exercised`.
- [ ] C004 Treat `missing`, `wrong`, and `not_exercised` as blocking unless explicitly scoped out with evidence.
- [ ] C005 Convert generic placeholders in matrices into concrete evidence rows.

## D. Gap Repair and Evidence

- [ ] D001 Make horizontal topology/adjacency/legality explicit in config/model/scenarios or document existing representation with tests.
- [ ] D002 Document deterministic workload approximation if stochastic arrivals are not implemented.
- [ ] D003 Document LSTM/forecast as interface-only unless trained forecast behavior is actually implemented.
- [ ] D004 Add evidence for local/private queue timing.
- [ ] D005 Add evidence for horizontal offloading timing.
- [ ] D006 Add evidence for vertical/cloud timing.
- [ ] D007 Add evidence for public/cloud queue behavior or document approximation.
- [ ] D008 Add evidence for timeout/drop/deadline behavior.
- [ ] D009 Add evidence for illegal horizontal destination rejection.
- [ ] D010 Add evidence for reward/cost formula boundary.

## E. Tests

- [ ] E001 Add/verify active policy exact-set test: `HOODIE`, `RO`, `FLC`, `VO`, `HO`, `BCO`, `MLEO`.
- [ ] E002 Add/verify legacy label absence test for active outputs: `MQO`, `Minimum Queue Offloader`, `ORIGINAL_HOODIE_BASELINE`, `HOODIE_PROPOSED`.
- [ ] E003 Add/verify local execution path test.
- [ ] E004 Add/verify horizontal offload path and legality test.
- [ ] E005 Add/verify vertical/cloud path test.
- [ ] E006 Add/verify private/offloading/public queue evidence test or validation artifact test.
- [ ] E007 Add/verify timeout/drop behavior test.
- [ ] E008 Add/verify Feature 086 artifact schema/readiness test.

## F. Metric Readiness

- [ ] F001 Update `metric-readiness-matrix.md` with concrete paper/repository classification.
- [ ] F002 Mark `task_completion_delay` as paper primary candidate only if denominator/filtering is mapped.
- [ ] F003 Mark `task_drop_ratio` as paper primary candidate only if denominator/drop semantics are mapped.
- [ ] F004 Mark `completion_rate` as derived/reliability metric.
- [ ] F005 Confirm or limit reward metrics according to paper formula evidence.
- [ ] F006 Confirm or limit throughput according to paper output evidence.
- [ ] F007 Keep `queue_stability_score` and `illegal_action_rejection_count` as repository diagnostics unless paper defines them.

## G. Feature 086 Artifacts

- [ ] G001 Generate `artifacts/feature_086_system_model_fidelity/mechanism_coverage.json`.
- [ ] G002 Generate `artifacts/feature_086_system_model_fidelity/mechanism_coverage.csv`.
- [ ] G003 Generate `artifacts/feature_086_system_model_fidelity/system_model_gap_matrix.json`.
- [ ] G004 Generate `artifacts/feature_086_system_model_fidelity/system_model_gap_matrix.md`.
- [ ] G005 Generate `artifacts/feature_086_system_model_fidelity/metric_readiness_matrix.json`.
- [ ] G006 Generate `artifacts/feature_086_system_model_fidelity/metric_readiness_matrix.md`.
- [ ] G007 Generate `artifacts/feature_086_system_model_fidelity/scenario_mechanism_coverage.json`.
- [ ] G008 Generate or copy forward `artifacts/feature_086_system_model_fidelity/hoodie_mleo_tie_evidence.json`.
- [ ] G009 Generate `artifacts/feature_086_system_model_fidelity/feature_086_system_model_fidelity_report.json`.
- [ ] G010 Generate `artifacts/feature_086_system_model_fidelity/feature_086_system_model_fidelity_report.md`.

## H. Final Validation

- [ ] H001 Run `git diff --check`.
- [ ] H002 Run runtime evaluation unit tests.
- [ ] H003 Run MLEO-focused tests.
- [ ] H004 Run runtime evaluation integration tests.
- [ ] H005 Validate Feature 085 artifacts.
- [ ] H006 Validate Feature 086 artifacts.
- [ ] H007 Final Feature 086 report declares exactly one verdict: `system_model_fidelity_ready_for_output_comparison` or `system_model_fidelity_blocked`.
- [ ] H008 Commit with `Implement Feature 086 HOODIE system model fidelity gate`.
