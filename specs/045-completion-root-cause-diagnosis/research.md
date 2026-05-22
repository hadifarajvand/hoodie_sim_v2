# Research: Completion Root-Cause Diagnosis Using Passive Lifecycle Traces

## Decision 1: Trace input source

- Decision: Consume Feature 044 passive lifecycle traces only, and rerun the Feature 044 trace runner only when the report needs to be regenerated.
- Rationale: Feature 045 must remain diagnostic-only and must not add new instrumentation.
- Alternatives considered: Adding new runtime tracing or ad-hoc fixtures, both rejected because they would blur diagnosis with repair.

## Decision 2: Diagnosis horizon and seeds

- Decision: Use paper-default `T = 110` runs with seeds `[0, 1, 2]`.
- Rationale: This keeps Feature 045 aligned with Features 042–044 and ensures comparable evidence across the sequence.
- Alternatives considered: Broadening to new seeds or different horizons, rejected because that would make root-cause comparisons harder to interpret.

## Decision 3: Root-cause output model

- Decision: Allow multiple root-cause classes per run, ranked by evidence strength, with confidence labels `low`, `medium`, and `high`.
- Rationale: Completion problems may have layered causes, and forcing a single cause too early would hide real evidence.
- Alternatives considered: Single-label classification only, rejected because it would overfit ambiguous traces.

## Decision 4: Follow-up routing

- Decision: Route runtime-proven failures to Feature 046 - Runtime Repair for Completion Lifecycle; route valid runtime/load issues to observation-vector, exploration, or loss-sequence follow-up.
- Rationale: Feature 045 is the diagnostic branch point, not the fix.
- Alternatives considered: Reusing Feature 045 for repair, rejected because that violates the scope and the clarified decisions.

## Decision 5: Prior feature validation

- Decision: Validate older features through committed artifacts and safe tests only; do not include pointer-sensitive older report tests.
- Rationale: Pointer-sensitive report tests are incompatible with the active Feature 045 workspace state and would create false blockers.
- Alternatives considered: Running the older pointer-sensitive report tests, rejected because they are scope-incompatible.

## Decision 6: Report outputs

- Decision: Produce JSON and Markdown report artifacts under `artifacts/analysis/completion-root-cause-diagnosis/`.
- Rationale: The diagnosis must be machine-readable and reviewable.
- Alternatives considered: Console-only output, rejected because it would not support auditability or downstream analysis.
