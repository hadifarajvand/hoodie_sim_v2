# Feature Specification: Passive Runtime Lifecycle Trace Instrumentation

**Feature Branch**: `044-passive-runtime-lifecycle-trace-instrumentation`  
**Created**: 2026-05-20  
**Status**: Draft  
**Input**: User description: "Add passive runtime lifecycle trace instrumentation so the simulator can expose enough evidence to diagnose why Feature 042 and Feature 043 showed drops but no completions under paper-default T=110."

## Clarifications

### Session 2026-05-20

- Q: Should this feature be allowed to touch `src/environment/`? → A: Yes, but only for passive trace instrumentation. No semantic behavior changes.
- Q: Should tracing be opt-in or always-on? → A: Opt-in via config/flag, with disabled as default if possible. Tests must prove disabled behavior is unchanged.
- Q: Where should trace events be exposed? → A: Through existing environment `info` dict / analysis runner collection path. Do not invent a new dependency.
- Q: Should `execution_progress` be emitted every slot? → A: Yes, if a task consumes compute capacity in that slot. It must include `cycles_before`, `cycles_consumed`, `cycles_after`, and `compute_capacity_gcycles_per_slot`.
- Q: Should trace ordering prove whether deadline/drop happens before or after execution completion? → A: Yes. This is the whole point.
- Q: Should this feature rerun paper-default `T=110` probes after instrumentation? → A: Yes, diagnostic only. No training.
- Q: If tracing reveals a bug, should this feature fix it? → A: No. It should report the bug and recommend a dedicated repair feature.
- Q: Should Feature 044 run pointer-sensitive older report tests? → A: No. Validate older features through committed artifacts and safe non-pointer-sensitive tests only.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Expose lifecycle evidence for diagnosis (Priority: P1)

As an analyst, I want passive lifecycle trace events exposed during a paper-default run so I can see exactly what happened to each task, even when the final outcome is a drop or a pending-at-horizon state.

**Why this priority**: Feature 043 could not distinguish missing completions from missing evidence. Without trace events, the diagnostic path remains blind.

**Independent Test**: Run the simulator with tracing enabled and confirm the trace includes lifecycle breakpoints for generated, admitted, transmission, execution, completion, drop, reward, and pending-at-horizon states without changing the observed outcomes.

**Acceptance Scenarios**:

1. **Given** a paper-default `T = 110` run, **When** tracing is enabled, **Then** the trace shows each task’s lifecycle steps and terminal outcome where available.
2. **Given** the same run, **When** tracing is disabled, **Then** the simulator produces the same decisions, rewards, and final outcomes as before.

---

### User Story 2 - Preserve simulator behavior while tracing (Priority: P2)

As a reviewer, I want trace collection to be passive so I can trust that instrumentation did not alter the simulator’s decisions, timing, or rewards.

**Why this priority**: Instrumentation that changes behavior would invalidate the diagnosis and create a new bug.

**Independent Test**: Compare enabled-vs-disabled tracing runs and confirm all externally visible outcomes stay identical.

**Acceptance Scenarios**:

1. **Given** tracing is disabled, **When** a paper-default run executes, **Then** the simulator behaves exactly as it did before instrumentation.
2. **Given** tracing is enabled, **When** the same run executes, **Then** the same actions, rewards, and terminal outcomes are produced.

---

### User Story 3 - Produce diagnosis-ready trace artifacts (Priority: P3)

As an analyst, I want a report that summarizes trace coverage and readiness so I can tell whether Feature 043 can now distinguish runtime behavior, counter gaps, queue pressure, or formula mismatch.

**Why this priority**: The point of instrumentation is not raw verbosity; it is diagnostic readiness.

**Independent Test**: Generate the instrumentation report from a paper-default run and verify it summarizes trace coverage, trace sources, and readiness for the next diagnostic feature.

**Acceptance Scenarios**:

1. **Given** a traced paper-default run, **When** the report is generated, **Then** it states whether the trace is sufficient to diagnose lifecycle breakpoints.
2. **Given** trace coverage is incomplete, **When** the report is generated, **Then** it clearly marks instrumentation as incomplete and identifies the missing lifecycle evidence.

### Edge Cases

- What happens when a task is generated but never admitted before the horizon?
- How does the trace represent a task that starts execution but does not finish?
- What happens when a task is dropped before any compute progress is observable?
- How does the instrumentation behave when tracing is turned off entirely?
- What happens if the trace captures the terminal outcome but not enough intermediate lifecycle detail to explain it?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose passive lifecycle trace events for paper-default runs without changing simulator decisions, timing, rewards, or outcomes.
- **FR-002**: The trace MUST include lifecycle events for generated, admitted, transmission started, transmission completed, execution started, execution progress, execution completed, deadline reached, deadline expired, task completed, task dropped, reward emitted, and pending-at-horizon states where those states occur.
- **FR-003**: The trace MUST attach enough task context to each event to support post-run diagnosis of lifecycle breakpoints.
- **FR-004**: The trace MUST expose the source component responsible for each event so analysts can distinguish environment-owned behavior from passive reporting.
- **FR-005**: The trace MUST preserve the same externally visible outcomes when tracing is enabled or disabled.
- **FR-006**: The system MUST provide a report that summarizes trace coverage and states whether the trace is sufficient to diagnose why completions were absent.
- **FR-007**: The report MUST identify whether trace evidence is sufficient to distinguish execution never started, execution progressed but did not complete, completion was emitted but not reflected in counters, or deadline/drop occurred first.
- **FR-008**: The trace and report MUST support paper-default `T = 110` analysis without claiming paper reproduction.
- **FR-009**: The instrumentation MUST remain passive and MUST NOT alter action legality, queue scheduling, execution math, transmission math, deadline behavior, reward timing, or capacity sharing behavior.
- **FR-010**: The instrumentation MUST retain compatibility with the existing environment orchestration model where the environment owns orchestration and helper components remain helper-only.
- **FR-011**: The report MUST record whether the trace is complete enough for Feature 043 to determine the next diagnostic step.
- **FR-012**: The system MUST reject any attempt to use tracing as a shortcut to fabricate completion evidence or terminal rewards.
- **FR-013**: When tracing is enabled, the system MUST expose trace data through existing environment `info` output and the analysis runner path rather than a new dependency or external service.
- **FR-014**: The trace MUST support opt-in configuration and preserve disabled-by-default behavior where feasible.
- **FR-015**: The report MUST preserve ordering evidence needed to determine whether deadline expiration, terminal drop, or execution completion happened first.

### Key Entities *(include if feature involves data)*

- **Lifecycle Trace Event**: A passive record of a task lifecycle moment, including the event type, slot, task context, and observable state at that moment.
- **Trace Coverage Summary**: A diagnostic summary of which lifecycle stages were observed and which remained unobserved during a run.
- **Instrumentation Readiness Report**: A report that states whether the trace is sufficient for downstream completion-lifecycle diagnosis.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A paper-default traced run exposes enough lifecycle detail to identify at least one of the following for each unfinished task: execution never started, execution progressed but did not complete, completion evidence was present, or deadline/drop occurred first.
- **SC-002**: Runs with tracing disabled and runs with tracing enabled produce identical externally visible decisions, rewards, and final task outcomes for the same seed and inputs.
- **SC-003**: The instrumentation report clearly states whether lifecycle evidence is sufficient for Feature 043 diagnosis in 100% of sampled paper-default runs.
- **SC-004**: The trace report includes complete coverage summaries for all required lifecycle stages in the paper-default diagnostic scope.
- **SC-005**: The feature introduces no paper-reproduction claim and no training-related behavior.

## Assumptions

- The existing simulator already exposes enough internal state to record passive lifecycle evidence without changing behavior.
- Paper-default `T = 110` remains the diagnostic horizon for this feature.
- Trace verbosity may be controlled by a passive flag or equivalent runtime switch, and the default should be disabled where feasible.
- If some lifecycle stages cannot be observed without altering behavior, the feature should report that limitation rather than infer or fabricate missing evidence.

## Production Constraints

- [x] Performance budgets identified
- [x] Artifact handling rules identified
- [x] Security and secret-hygiene constraints identified
- [x] CI quality gate impact identified

## Public Interfaces Affected

- [x] Environment reset/step
- [x] Runtime model interface
- [x] Evaluation metric interface
- [x] Config schema
- [x] Artifact schema

## Config / Schema Impact

- [x] Required config fields identified
- [x] Validation rules identified
- [x] Backward-compatibility impact identified

## Artifact Impact

- [x] Raw metrics
- [x] Debug traces
- [x] Reports
- [x] Validation summaries

## Security Considerations

- [x] Secrets / tokens / credentials reviewed
- [x] Remote code execution reviewed
- [x] External references documented

## Definition of Done

- [x] Spec matched by plan
- [x] Tests identified
- [x] Assumptions documented
- [x] Configs validated or updated
- [x] Paper-to-code mapping updated
- [x] Artifacts handled per lifecycle rules
- [x] Review and merge gate satisfied
