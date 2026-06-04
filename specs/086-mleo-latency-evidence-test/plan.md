# Implementation Plan: Feature 086 HOODIE System-Model Fidelity Gate

## Branch

`086-mleo-latency-evidence-test`

Base branch: `085-hoodie-paper-baseline-fidelity-audit`

## Goal

Turn Feature 086 into the final Chapter/System-Model fidelity gate before output comparison. The implemented gate now produces the `system_model_fidelity_ready_for_output_comparison` verdict while preserving conservative claim boundaries for the remaining approximations.

## Governing Workflow

Follow Spec Kit discipline:

1. Treat `spec.md`, `plan.md`, `tasks.md`, `contracts/validation-rules.md`, matrices, and quickstart as the governing contract.
2. Update Spec Kit files first when implementation evidence changes.
3. Implement code/tests/artifacts only for the feature scope.
4. Mark checklist/task items complete only when evidence exists.
5. Do not introduce thesis/DCQ/custom proposed method code.

## Paper Scope to Validate

Audit the HOODIE paper system-model chapter using:

- `resources/papers/hoodie/ocr/merged.txt`
- `resources/papers/hoodie/original/HOODIE_paper.pdf` only if OCR is ambiguous

Required mechanisms:

1. three-tier topology: task source/IoT or MD layer, edge agents, cloud;
2. edge agent set and cloud node;
3. horizontal EA-to-EA connectivity and legality constraints;
4. vertical EA-to-cloud path;
5. task ID, data/input size, processing density or CPU demand, timeout/deadline;
6. task arrival/workload model;
7. local/private queue;
8. offloading queue;
9. public/cloud queue;
10. local execution delay;
11. horizontal transmission delay;
12. vertical transmission delay;
13. remote/cloud execution delay;
14. waiting time and completion time;
15. timeout, deadline violation, unavailability, and drop semantics;
16. hybrid action model: local, horizontal, vertical;
17. two-stage decision boundary: local-vs-offload and destination selection, or documented runtime approximation;
18. HOODIE proposed-method claim boundary;
19. paper baselines: RO, FLC, VO, HO, BCO, MLEO;
20. MLEO minimum estimated total latency behavior;
21. reward/cost model boundary;
22. output metric readiness.

## Status Labels

Use exactly these labels:

- `exact`
- `approximate_documented`
- `missing`
- `wrong`
- `not_exercised`

Any required mechanism with `missing`, `wrong`, or `not_exercised` blocks readiness unless explicitly scoped out with evidence.

## Implementation Phases

### Phase 1 — Extract and Map

- Read the paper OCR/PDF.
- Fill `system-model-gap-matrix.md` with paper mechanism, expected simulator behavior, current code/artifact evidence, status, and required fix.
- Fill `metric-readiness-matrix.md` with paper-comparison vs repository-diagnostic classification.

### Phase 2 — Repair Blocking Gaps

Repair or document:

- horizontal topology/adjacency if only implicit;
- deterministic workload approximation if stochastic arrivals are not implemented;
- LSTM/forecast interface-only boundary;
- queue timing evidence for private/offloading/public/cloud queues;
- local/horizontal/vertical delay evidence;
- timeout/drop/illegal-action evidence;
- reward/cost claim boundary.

### Phase 3 — Add Tests

Add tests proving:

- active policies are exactly `HOODIE`, `RO`, `FLC`, `VO`, `HO`, `BCO`, `MLEO`;
- legacy labels are absent from active outputs;
- local, horizontal, vertical paths are exercised;
- illegal horizontal destination is rejected;
- timeout/drop behavior is exercised;
- queue timing is represented or documented;
- MLEO chooses minimum total delay and not minimum queue length.

### Phase 4 — Generate Artifacts

Create `artifacts/feature_086_system_model_fidelity/` with:

- `mechanism_coverage.json`
- `mechanism_coverage.csv`
- `system_model_gap_matrix.json`
- `system_model_gap_matrix.md`
- `metric_readiness_matrix.json`
- `metric_readiness_matrix.md`
- `scenario_mechanism_coverage.json`
- `hoodie_mleo_tie_evidence.json`
- `feature_086_system_model_fidelity_report.json`
- `feature_086_system_model_fidelity_report.md`

### Phase 5 — Final Gate

Final report must state one of:

- `system_model_fidelity_ready_for_output_comparison`
- `system_model_fidelity_blocked`

The current artifact bundle uses `system_model_fidelity_ready_for_output_comparison` and lists the remaining approximations honestly.
