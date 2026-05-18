# Feature Specification: Smoke Training

**Feature Branch**: `[040-smoke-training]`  
**Created**: 2026-05-18  
**Status**: Draft  
**Input**: User description: "Implement a tiny deterministic training smoke run to verify that the Feature 039 model surface, replay-transition handling, delayed reward handling, and reporting path can execute without runtime failure."

## Clarifications

### Session 2026-05-18

- Q: Smoke data source → A: Use tiny deterministic fixture transitions as the primary smoke source, with an optional environment smoke rollout only for interface validation.
- Q: Optimizer steps → A: Exactly 1 optimizer step.
- Q: Target network → A: Instantiate target network only; do not sync or update it.
- Q: Loss function → A: Use a minimal MSE smoke loss over deterministic fixture targets.
- Q: Replay buffer → A: Do not implement a production replay buffer; use only a tiny smoke fixture schema.
- Q: Readiness gate → A: No override; Feature 040 is a smoke-only technical exception and full training remains blocked.
- Q: Report interpretation → A: Do not include performance metrics; report engineering smoke metrics only.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Smoke Validation Run (Priority: P1)

As a maintainer, I want a tiny, deterministic smoke training run so that I can verify the Feature 039 model surface, replay handling, and training path execute without runtime failure.

**Why this priority**: This is the primary gate for proving the feature can run end-to-end at a bounded scale.

**Independent Test**: Run a single bounded smoke execution against deterministic fixture transitions and confirm it completes, produces a finite loss, and updates at least one model parameter.

**Acceptance Scenarios**:

1. **Given** the Feature 039 architecture and a fixed smoke seed, **When** the smoke run starts, **Then** it completes within the bounded step limit and produces a finite loss.
2. **Given** deterministic fixture transitions, **When** the smoke run consumes them, **Then** the run respects delayed reward handling and does not invent terminal rewards.

---

### User Story 2 - Deterministic Repeatability (Priority: P2)

As a maintainer, I want the smoke run to repeat deterministically so that I can tell whether the result is stable or just luck.

**Why this priority**: A smoke test is only useful if the same seed reproduces the same summary and update behavior.

**Independent Test**: Execute the same bounded smoke scenario twice with the same seed bundle and confirm the summaries match on the recorded smoke fields.

**Acceptance Scenarios**:

1. **Given** the same seed bundle and the same fixture, **When** the smoke run is repeated, **Then** the recorded smoke summary matches across runs.
2. **Given** a different seed bundle, **When** the smoke run is repeated, **Then** the summary can differ only in seed-sensitive fields and not in scope or contract checks.

---

### User Story 3 - Smoke Reporting and Guardrails (Priority: P3)

As a maintainer, I want a report of what the smoke run did and did not do so that nobody mistakes the run for full training or paper reproduction.

**Why this priority**: The feature must be auditable and must not overclaim what was tested.

**Independent Test**: Inspect the report artifacts and confirm they state the smoke scope, target-update restriction, and the absence of any paper-reproduction claim or performance metrics.

**Acceptance Scenarios**:

1. **Given** the smoke report, **When** it is generated, **Then** it records the dependency status, smoke scope, replay contract, loss result, parameter-update result, and repeatability result.
2. **Given** the report artifacts, **When** a reviewer reads them, **Then** they can verify that no target-network sync, no full training loop, and no paper reproduction claim occurred.

### Edge Cases

- What happens when a replay transition is pending at the horizon and must remain non-terminal?
- What happens when a smoke batch contains no reward-bearing terminal transition?
- How does the feature behave if the smoke run produces a non-finite loss?
- What happens if the same seed bundle is reused and the smoke summary changes unexpectedly?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The feature MUST provide a bounded smoke training path that exercises the Feature 039 model surface and the Feature 038 state/action/replay contract without becoming full training.
- **FR-002**: The smoke run MUST preserve delayed reward handling, including the rule that non-terminal transitions keep `reward_available=false` and terminal transitions alone may set `reward_available=true`.
- **FR-003**: The smoke run MUST perform exactly 1 optimizer step and MUST verify that at least one online-network parameter changes.
- **FR-004**: The smoke run MUST validate that the computed minimal MSE smoke loss is finite for the bounded smoke batch or fixture targets.
- **FR-005**: The smoke run MUST instantiate online and target network surfaces but MUST NOT execute target-network sync or update logic.
- **FR-006**: The smoke run MUST produce report artifacts that record the smoke batch summary, optimizer-step summary, loss summary, parameter-update summary, deterministic repeatability result, and target-update restriction, and MUST omit performance metrics.
- **FR-007**: The smoke run MUST be deterministic when rerun with the same seed bundle and bounded fixture.
- **FR-008**: The smoke run MUST NOT claim paper reproduction success, convergence, performance improvement, or training readiness.
- **FR-009**: The smoke run MUST NOT add dependency files, runtime/environment semantics, baseline policy changes, or reward-timing changes.
- **FR-010**: The smoke run MUST preserve the Feature 038 unresolved target-update meaning and MUST report that target-network update execution did not occur.
- **FR-011**: If a rollout path is used, it MUST run through the existing simulator environment contract, and it MUST be used only for interface validation rather than as a replacement for deterministic fixture smoke data.
- **FR-012**: If a fixture path is used, the fixture MUST be explicitly labeled as a smoke fixture and MUST NOT be treated as simulator evidence.

### Key Entities *(include if feature involves data)*

- **Smoke Run**: A bounded validation execution that exercises the model, replay, and training path.
- **Smoke Fixture**: A tiny deterministic transition set or rollout used only to verify smoke behavior.
- **Seed Bundle**: The deterministic seed set that controls repeatability of the smoke run.
- **Smoke Report**: The artifact that records what was exercised and what was intentionally not exercised.
- **Transition Record**: A replay or rollout record used by the smoke run, including delayed reward metadata.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A bounded smoke run completes within the fixed one-step budget in the approved environment.
- **SC-002**: Two runs with the same seed bundle produce matching smoke summaries and the same parameter-update verdict.
- **SC-003**: The smoke loss remains finite and at least one online-network parameter changes during the fixed smoke step budget.
- **SC-004**: The generated report artifacts clearly state the smoke scope, the no-target-update restriction, the absence of any paper-reproduction claim, and the omission of performance metrics.
- **SC-005**: The feature leaves dependency files and runtime/policy/reward contracts unchanged.

## Assumptions

- Feature 039’s architecture surface is already available and remains unchanged.
- The approved interpreter already provides torch, so this feature may reuse the existing network surface without adding dependencies.
- The smoke run is intentionally tiny and is only a bounded engineering validation, not a scientific training result.
- The primary smoke data source is deterministic fixture transitions; environment rollout, if used, is optional and limited to interface validation.
- Feature 038’s target-update frequency meaning remains unresolved and must not be resolved by this feature.
- Any fixture-based smoke transitions are validation artifacts only and do not represent paper evidence.
- The report must exclude performance metrics and report only engineering smoke metrics.

## Production Constraints

- [x] Performance budgets identified
- [x] Artifact handling rules identified
- [x] Security and secret-hygiene constraints identified
- [x] CI quality gate impact identified

The smoke run must stay bounded and must not expand into long-running training or evaluation.

## Public Interfaces Affected

- [x] Runtime model interface
- [x] Replay contract
- [x] Config schema
- [x] Artifact schema
- [x] Evaluation metric interface

This feature exercises existing interfaces and records smoke-only outcomes.

## Config / Schema Impact

- [x] Required config fields identified
- [x] Validation rules identified
- [x] Backward-compatibility impact identified

The smoke run needs deterministic seed controls, bounded step limits, and explicit smoke-report fields.

## Artifact Impact

- [x] Reports
- [x] Validation summaries
- [x] Debug traces

This feature requires smoke-specific report artifacts only.

## Security Considerations

- [x] Secrets / tokens / credentials reviewed
- [x] Remote code execution reviewed
- [x] External references documented

The feature does not introduce secrets or external execution behavior beyond existing project contracts.

## Definition of Done

- [x] Spec matched by plan
- [x] Tests identified
- [x] Assumptions documented
- [x] Configs validated or updated
- [x] Paper-to-code mapping updated
- [x] Artifacts handled per lifecycle rules
- [x] Review and merge gate satisfied

Feature 040 is done when the smoke run is deterministic, bounded, reports finite loss and parameter change, and does not execute target sync or claim paper reproduction.
