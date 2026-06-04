# Tasks: Feature 086 HOODIE System-Model Mechanism Fidelity Gate

## A. Paper Extraction

- [ ] A001 Read `resources/papers/hoodie/ocr/merged.txt` for system-model obligations.
- [ ] A002 Use the original PDF only where OCR is ambiguous.
- [ ] A003 Extract topology obligations.
- [ ] A004 Extract task model obligations.
- [ ] A005 Extract queue model obligations.
- [ ] A006 Extract local, horizontal, and vertical delay obligations.
- [ ] A007 Extract waiting, completion, timeout, and drop obligations.
- [ ] A008 Extract action/offloading and decision-boundary obligations.
- [ ] A009 Extract reward/cost and output metric obligations.

## B. Code Mapping

- [ ] B001 Map topology to code/config/scenarios.
- [ ] B002 Map task attributes to code/config/scenarios.
- [ ] B003 Map queues to code/config/scenarios.
- [ ] B004 Map delay calculations to code/config/scenarios.
- [ ] B005 Map drop/timeout behavior to code/config/scenarios.
- [ ] B006 Map active policy set to registry/artifacts.
- [ ] B007 Create or update `system-model-gap-matrix.md`.
- [ ] B008 Classify each mechanism as `exact`, `approximate_documented`, `missing`, `wrong`, or `not_exercised`.

## C. Gap Repair

- [ ] C001 Repair or document horizontal adjacency/connectivity.
- [ ] C002 Repair or document deterministic workload approximation.
- [ ] C003 Repair or document forecast/LSTM interface boundary.
- [ ] C004 Add evidence for local/private queue timing.
- [ ] C005 Add evidence for horizontal offloading timing.
- [ ] C006 Add evidence for vertical/cloud timing.
- [ ] C007 Add evidence for timeout/drop handling.
- [ ] C008 Add evidence for illegal horizontal destination rejection.
- [ ] C009 Add evidence for reward/cost boundary.

## D. Tests

- [ ] D001 Add MLEO numeric test where smallest queue is not smallest total delay.
- [ ] D002 Assert MLEO selects minimum total estimated latency.
- [ ] D003 Add/verify local execution path test.
- [ ] D004 Add/verify horizontal offload path test.
- [ ] D005 Add/verify vertical/cloud path test.
- [ ] D006 Add/verify queue timing test or documented evidence.
- [ ] D007 Add/verify timeout/drop test.
- [ ] D008 Add/verify illegal action rejection test.
- [ ] D009 Add/verify active policy exact-set test.
- [ ] D010 Add/verify legacy label absence test.

## E. Metrics and Outputs

- [ ] E001 Create or update `metric-readiness-matrix.md`.
- [ ] E002 Classify `task_completion_delay`.
- [ ] E003 Classify `task_drop_ratio`.
- [ ] E004 Classify `completion_rate`.
- [ ] E005 Classify reward metrics.
- [ ] E006 Classify throughput.
- [ ] E007 Classify repository diagnostic metrics.

## F. Artifacts

- [ ] F001 Generate `artifacts/feature_086_system_model_fidelity/mechanism_coverage.json`.
- [ ] F002 Generate `artifacts/feature_086_system_model_fidelity/mechanism_coverage.csv`.
- [ ] F003 Generate `artifacts/feature_086_system_model_fidelity/system_model_gap_matrix.json`.
- [ ] F004 Generate `artifacts/feature_086_system_model_fidelity/system_model_gap_matrix.md`.
- [ ] F005 Generate `artifacts/feature_086_system_model_fidelity/metric_readiness_matrix.json`.
- [ ] F006 Generate `artifacts/feature_086_system_model_fidelity/metric_readiness_matrix.md`.
- [ ] F007 Generate `artifacts/feature_086_system_model_fidelity/scenario_mechanism_coverage.json`.
- [ ] F008 Generate `artifacts/feature_086_system_model_fidelity/hoodie_mleo_tie_evidence.json`.
- [ ] F009 Generate final Feature 086 report JSON and Markdown.

## G. Validation

- [ ] G001 Run `git diff --check`.
- [ ] G002 Run runtime evaluation unit tests.
- [ ] G003 Run MLEO-focused tests.
- [ ] G004 Run runtime evaluation integration tests.
- [ ] G005 Validate Feature 085 artifacts.
- [ ] G006 Validate Feature 086 artifacts.
- [ ] G007 Commit with `Implement Feature 086 HOODIE system model fidelity gate`.
