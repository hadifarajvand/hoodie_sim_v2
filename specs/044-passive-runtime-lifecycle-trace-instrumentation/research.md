# Research: Passive Runtime Lifecycle Trace Instrumentation

## Decision 1: Trace exposure path

- **Decision**: Expose passive trace records through the existing environment `info` dict and the analysis runner collection path.
- **Rationale**: This preserves the existing orchestration model and avoids inventing a new dependency or transport layer for instrumentation.
- **Alternatives considered**:
  - A dedicated side-channel or file stream per step. Rejected because it complicates validation and increases the chance of changing runtime behavior.
  - A new external logging dependency. Rejected because the feature must remain dependency-neutral.

## Decision 2: Trace toggle behavior

- **Decision**: Make tracing opt-in via config or flag, with disabled as the default where feasible.
- **Rationale**: A disabled default minimizes the risk of unintentional overhead or behavior drift in non-diagnostic runs.
- **Alternatives considered**:
  - Always-on tracing. Rejected because it would impose overhead on every run and makes equivalence validation harder.
  - Separate debug-only code path. Rejected because it risks diverging behavior between traced and untraced runs.

## Decision 3: Event granularity

- **Decision**: Emit execution progress events for each slot where compute capacity is actually consumed, and include before/consumed/after/capacity values.
- **Rationale**: Feature 043 needs enough detail to distinguish no execution, partial execution, and completion-related counter gaps.
- **Alternatives considered**:
  - Only emit start/end events. Rejected because it does not distinguish partial progress from no progress.
  - Aggregate progress only at terminal state. Rejected because it hides the timing needed for ordering diagnosis.

## Decision 4: Ordering evidence

- **Decision**: Record event ordering with enough fidelity to determine whether deadline expiration, terminal drop, or execution completion happened first.
- **Rationale**: This ordering is the core diagnostic requirement for the upstream completion-lifecycle audit.
- **Alternatives considered**:
  - Store only terminal outcomes. Rejected because terminal outcomes alone cannot explain whether execution progressed.

## Decision 5: Diagnosis readiness report

- **Decision**: Produce a passive analysis report that summarizes trace coverage, trace sources, and readiness for downstream diagnosis.
- **Rationale**: The report is the user-facing evidence that the trace is sufficient for Feature 043 or that instrumentation remains incomplete.
- **Alternatives considered**:
  - Add only raw traces without a summary. Rejected because raw traces alone are too expensive to audit repeatedly.

## Decision 6: Runtime repair boundary

- **Decision**: If trace output reveals a runtime bug, report it and recommend a dedicated repair feature instead of fixing it here.
- **Rationale**: This feature is diagnostic instrumentation, not remediation.
- **Alternatives considered**:
  - Quietly repair the runtime while adding trace metadata. Rejected because it would conflate diagnosis with behavior change.

## Decision 7: Compatibility with existing runtime contracts

- **Decision**: Preserve environment ownership of orchestration, delayed reward semantics, pending-at-horizon non-terminal behavior, exact-deadline acceptance, timeout expiration, and capacity-sharing rules.
- **Rationale**: These are already established runtime contracts and must remain unchanged while tracing is added.
- **Alternatives considered**:
  - Reworking runtime internals for cleaner instrumentation hooks. Rejected because it raises semantic drift risk.
