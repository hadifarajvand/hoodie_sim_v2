# Feature Specification: 007-adaptive-policy-offloading-decisions

**Feature Branch**: `007-adaptive-policy-offloading-decisions`  
**Created**: 2026-05-06  
**Status**: Draft  
**Input**: User description: "Adaptive Policy and Offloading Decisions"

## Clarifications

### Session 2026-05-06

- Q: Does this feature implement learned HOODIE DRL training? → A: No. Training, TorchRL, neural networks, replay learning, LSTM, and DQN architecture changes are out of scope.
- Q: Does this feature implement LSTM load forecasting? → A: No. The feature exposes observed load and existing summaries as policy inputs only; forecasting remains future work.
- Q: Does this feature implement model switching based on observed P? → A: No. The feature may pass observed P into policy context, but it must not select among trained model checkpoints.
- Q: Does HoodieGymEnvironment execute the adaptive policy internally? → A: No. Policies remain external callers and the environment remains policy-agnostic.
- Q: May the adaptive policy choose illegal actions and let the environment fix them? → A: No. The policy must choose legal actions; illegal-action handling remains strict and shared with no silent remapping.
- Q: What is the adaptive policy allowed to use? → A: legal_action_mask, task size/density/cycles/deadline fields, queue_load, latency_estimates / balance_hint, observed traffic summary when explicitly passed, compute/execution estimates when exposed, and topology metadata.
- Q: Is the policy allowed to inspect the full trace? → A: No. It may only use the current observation and explicitly supplied summaries that represent observed load.
- Q: Is this a replacement for FLC, HO, VO, RO, BCO, or MLEO? → A: No. It adds a new policy/baseline while preserving existing policies and the shared interface.
- Q: How should missing adaptive fields be handled? → A: Deterministically and safely. Missing observed traffic or compute estimate fields must not crash policy selection; the policy falls back to legal local action if available, otherwise canonical legal-action order.
- Q: What is the canonical action preference order for fallback? → A: local / compute_local, then horizontal / offload_horizontal, then vertical / offload_vertical, documented as an assumption-backed fallback.
- Q: Should this feature modify evaluation metrics? → A: No formula changes. It may add labels or metadata identifying the adaptive policy, but must not alter metric formulas.
- Q: What is the minimum useful implementation? → A: AdaptiveDecisionContext, context builder, AdaptiveOffloadingPolicy, tests for deterministic legal choices, and documentation.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Adaptive Decision Context (Priority: P1)

As a simulation user, I want the environment to expose a paper-backed adaptive decision bundle so that offloading decisions can be made from current task features, load information, and legal actions without mutating the environment lifecycle.

**Why this priority**: Adaptive decisions require a stable, testable context before any policy can respond to traffic and compute variation.

**Independent Test**: Build an adaptive decision context from an existing environment observation and verify it contains the current task, legal actions, queue/load state, compute estimates, and optional traffic summary data without changing environment state.

**Acceptance Scenarios**:

1. **Given** a current task and environment observation, **When** the adaptive context is built, **Then** it includes task features, legal actions, queue/load state, and available execution estimates.
2. **Given** an optional traffic summary, **When** the adaptive context is built, **Then** it includes observed load information without mutating the environment.

### User Story 2 - Conservative Adaptive Policy (Priority: P1)

As a simulation user, I want a conservative adaptive offloading policy that chooses only legal actions so that baseline decision-making can adapt to traffic and compute conditions without inventing unsupported behavior.

**Why this priority**: The policy is the user-facing decision point; it must be deterministic and legality-preserving before any adaptive behavior is useful.

**Independent Test**: Feed the same adaptive context into the policy repeatedly and verify it returns the same legal action each time for the same inputs.

**Acceptance Scenarios**:

1. **Given** a local-only topology, **When** the policy evaluates the current task, **Then** it returns a legal local action.
2. **Given** a topology with horizontal and cloud options, **When** the policy evaluates the current task under different load conditions, **Then** it returns a legal action consistent with the provided load and execution estimates.

### User Story 3 - Baseline Compatibility and No Lifecycle Bypass (Priority: P2)

As a simulation user, I want adaptive policy support to fit through the existing policy interface so that current baselines continue to work and the environment remains policy-agnostic.

**Why this priority**: Adaptive inputs must not fracture the existing policy path or introduce a special environment mode.

**Independent Test**: Run existing baseline policies and the adaptive policy through the same policy interface and verify the environment remains unchanged and policy selection stays external.

**Acceptance Scenarios**:

1. **Given** an existing baseline policy, **When** it runs through the policy interface, **Then** it continues to work unchanged.
2. **Given** the adaptive policy, **When** it makes a decision for the active task, **Then** the environment does not run policy logic internally and no illegal action is silently remapped.

### Edge Cases

- What happens when traffic summary data is unavailable?
- How does the policy behave when only local actions are legal?
- What happens when execution estimates are missing or incomplete?
- How does the system handle a requested action that is not legal under the current topology?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide an adaptive decision context containing the current task, current slot, legal action mask, queue/load state, execution estimates, and optional traffic summary signals when available.
- **FR-002**: The system MUST build the adaptive decision context from existing environment observation data and optional traffic summary data without mutating environment state.
- **FR-003**: The system MUST provide a conservative adaptive offloading policy that consumes the adaptive decision context through the existing policy interface.
- **FR-004**: The adaptive policy MUST choose only legal actions and MUST reject illegal choices rather than silently remapping them.
- **FR-005**: The adaptive policy MUST be deterministic for identical inputs.
- **FR-006**: The adaptive policy MUST support the same action space as existing policies: local computation, horizontal offloading, and vertical offloading.
- **FR-007**: Adaptive policy selection MUST remain external to the environment lifecycle boundary.
- **FR-008**: Existing baseline policies MUST continue to operate through the same policy interface path without requiring a special adaptive-only environment mode.
- **FR-009**: The feature MUST document the paper-backed decision inputs and any unresolved gaps in traceability documentation.
- **FR-010**: The feature MUST not change lifecycle ownership, introduce new traffic models, or add training-time learning behavior.
- **FR-011**: The policy MUST fall back deterministically to the canonical legal-action order when adaptive fields are missing, using local/compute_local first, then horizontal/offload_horizontal, then vertical/offload_vertical.
- **FR-012**: The feature MUST not modify evaluation metric formulas; it may only add labels or metadata identifying the adaptive policy.

### Key Entities *(include if feature involves data)*

- **Adaptive Decision Context**: The combined, read-only view of task features, load information, legal choices, and execution estimates used to support a policy decision.
- **Adaptive Offloading Policy**: A conservative decision-maker that uses the adaptive context to choose one legal action for the current task.
- **Traffic Summary**: The observed traffic/load summary used to inform adaptive decision-making when available.
- **Policy Context**: The existing interface wrapper that carries observations and legal-action constraints into a policy.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The adaptive decision context can be built from an existing environment observation in 100% of tested cases without changing environment state.
- **SC-002**: The adaptive policy returns a legal action in 100% of tested topologies and load conditions.
- **SC-003**: The adaptive policy returns the same action for identical inputs across repeated runs in 100% of deterministic tests.
- **SC-004**: Existing baseline policies continue to complete their primary task flow through the same policy interface in 100% of regression tests.
- **SC-005**: No dependency files are changed for this feature.

## Assumptions

- The adaptive policy is conservative by design and is intended as a paper-backed baseline aid, not a learned controller.
- Optional traffic summary data may be absent; in that case the adaptive policy falls back to existing legal-action behavior and other available environment signals.
- Any paper detail that cannot be recovered cleanly must be recorded as an explicit gap rather than invented.

## Production Constraints

- No new dependencies are added.
- No stochastic or learned decision model is introduced.
- The environment lifecycle owner remains unchanged.
- Policy selection remains external to the environment boundary.

## Public Interfaces Affected

- Environment reset/step
- Policy interface
- Traffic summary surface
- Evaluation runner interface
- Task model
- Topology interface
- Runtime model interface

## Config / Schema Impact

- Adaptive context fields must be identified and validated.
- Existing policy inputs remain backward compatible.
- Optional traffic-summary inputs must be handled safely when missing.

## Artifact Impact

- Raw metrics
- Debug traces
- Validation summaries
- Reports

## Security Considerations

- No secrets, tokens, or credentials are introduced.
- No remote execution surfaces are added.
- External paper-backed decision inputs must remain documented in assumptions and mapping notes.

## Definition of Done

- Spec matched by plan
- Tests identified
- Assumptions documented
- Configs validated or updated
- Paper-to-code mapping updated
- Artifacts handled per lifecycle rules
- Review and merge gate satisfied
