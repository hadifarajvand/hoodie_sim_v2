# Tasks: Feature 086 MLEO Latency Evidence Test

## A. Inspection

- [ ] A001 Inspect `src/policies/mleo.py` for candidate construction and `total_delay` behavior.
- [ ] A002 Inspect runtime adapter in `src/analysis/hoodie_runtime_evaluation_runner/policies.py`.
- [ ] A003 Identify where candidate delay evidence is exposed: `last_candidates`, trace details, or artifacts.

## B. Numeric MLEO Tests

- [ ] B001 Add a deterministic test context with local, horizontal, and vertical candidates.
- [ ] B002 Make the smallest-queue candidate different from the smallest-total-delay candidate.
- [ ] B003 Assert MLEO selects the minimum-total-delay candidate.
- [ ] B004 Assert candidate `total_delay` values explicitly.
- [ ] B005 Assert the test would fail under queue-length-only selection.

## C. HOODIE/MLEO Tie Evidence

- [ ] C001 Compare HOODIE and MLEO selected actions across deterministic benchmark rows or traces.
- [ ] C002 Count selected actions by policy and scenario.
- [ ] C003 Determine whether the aggregate tie is caused by identical action selection or by metric convergence after different actions.
- [ ] C004 Add report/artifact evidence explaining the tie.
- [ ] C005 Add a test that fails if tie evidence is absent.

## D. Documentation and Validation

- [ ] D001 Update Feature 086 quickstart with final validation commands.
- [ ] D002 Update validation rules if evidence format differs from initial plan.
- [ ] D003 Run `git diff --check`.
- [ ] D004 Run unit tests for runtime evaluation policies.
- [ ] D005 Run MLEO-focused tests.
- [ ] D006 Run runtime evaluation integration tests.
- [ ] D007 Validate Feature 085 artifacts remain valid.
- [ ] D008 Commit changes with `Implement Feature 086 MLEO latency evidence test`.
