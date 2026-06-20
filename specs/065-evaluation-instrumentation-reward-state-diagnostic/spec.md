# Feature Specification: Feature 065 - Evaluation Instrumentation and Reward/State Diagnostic Repair

**Feature Branch**: `[065-evaluation-instrumentation-reward-state-diagnostic]`
**Created**: 2026-06-20
**Status**: Draft
**Input**: User description: "Feature 065 Evaluation Instrumentation and Reward/State Diagnostic Repair"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Instrument the missing evaluation evidence

As an analyst, I can log evaluation actions, masks, outcomes, and reward decomposition at each staged checkpoint so I can explain whether the earlier static reward was a measurement blind spot or a real signal limitation.

**Independent Test**: Run the feature and verify every checkpoint contains evaluation action distribution, per-action outcome attribution, and reward decomposition derived from evaluation episodes rather than replay.

### User Story 2 - Diagnose state coverage and policy effect

As a reviewer, I can see what the policy state includes and how candidate and fixed policies behave on the same trace bank so I can decide whether the next fix is reward, state representation, or metric aggregation.

**Independent Test**: Run the feature and verify the state-feature audit and policy-effect diagnostic are generated and internally consistent.

### Edge Cases

- What happens when cumulative staged training cannot be reproduced without semantic changes? The feature must stop and report a blocked verdict.
- What happens when the same evaluation reward persists even after instrumentation? The report must keep the diagnosis descriptive and avoid superiority claims.
- What happens when a metric cannot be derived from real execution? The feature must set it to `null` and explain the gap.

## Requirements *(mandatory)*

- **FR-001**: The feature MUST rerun a controlled staged diagnostic campaign at budgets `[100, 150, 200, 500]` without exceeding 500 training episodes.
- **FR-002**: The feature MUST record evaluation action logging from evaluation episodes, not from replay.
- **FR-003**: The feature MUST distinguish replay-window action counts from cumulative training action counts.
- **FR-004**: The feature MUST compute per-action outcome attribution and reward decomposition for each checkpoint.
- **FR-005**: The feature MUST audit the state features visible to the policy and those only present in the environment or diagnostics.
- **FR-006**: The feature MUST compare candidate and fixed policies on the same evaluation trace bank.
- **FR-007**: The feature MUST not modify reward semantics, environment semantics, policy semantics, DAL, or replay semantics.
- **FR-008**: The feature MUST not claim model superiority or paper reproduction.
- **FR-009**: The feature MUST generate the required JSON, Markdown, and matplotlib figure artifacts under the required output directory.

## Success Criteria *(mandatory)*

- **SC-001**: The output contains exactly four staged checkpoints with cumulative budgets `100`, `150`, `200`, and `500`.
- **SC-002**: The output proves the evaluation action distribution is sourced from evaluation episodes.
- **SC-003**: The output proves replay-window action counts are not being mistaken for full training history.
- **SC-004**: The output includes a state-feature audit and a policy-effect diagnostic.
- **SC-005**: The report stays claim-safe and routes to a diagnostic next step, not to unsupported superiority claims.
