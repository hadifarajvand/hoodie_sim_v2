# Feature Specification: Paper HOODIE Network Implementation

**Feature Branch**: `[039-paper-hoodie-network-implementation]`  
**Created**: 2026-05-14  
**Status**: Draft  
**Input**: User description: "Implement the paper HOODIE neural-network architecture surface only: Dueling DQN, Double-DQN-compatible online/target network structure, and LSTM support according to the training foundation contracts from Feature 038."

## Clarifications

### Session 2026-05-14

- Q: Is torch already available in the approved interpreter environment? → A: If torch is already present, use it as-is. If it is not present, do not add dependencies; mark `dependency_status=blocked_missing_existing_torch` and stop without modifying dependency files.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Architecture Contract for Future Training (Priority: P1)

As a future training implementer, I need a frozen network architecture surface so that the model can be instantiated, validated, and inspected without starting training.

**Why this priority**: If the network surface is inconsistent, future training work cannot safely begin.

**Independent Test**: The architecture can be instantiated deterministically and its shapes can be validated without any optimization, replay sampling, or campaign execution.

**Acceptance Scenarios**:

1. **Given** the Feature 038 state/action contracts, **When** the architecture is instantiated, **Then** it exposes stable Q-values for the three approved action indices.
2. **Given** a deterministic seed for model initialization, **When** the architecture is created twice, **Then** the parameter structure and output shapes are identical.

### User Story 2 - Dueling, Double-DQN, and LSTM Separation (Priority: P2)

As a project maintainer, I need the Q-network, LSTM, and target-network responsibilities separated so that paper notation ambiguity does not leak into configuration or validation.

**Why this priority**: The paper’s reused notation is ambiguous; the implementation must make the architecture boundaries explicit.

**Independent Test**: The configuration and shape checks can confirm that Q-network hidden layers and LSTM hidden settings are independently defined and that online/target networks are architecture-compatible.

**Acceptance Scenarios**:

1. **Given** the network configuration, **When** it is validated, **Then** q-network hidden layers and LSTM hidden settings are independently represented and checked.
2. **Given** online and target network instances, **When** they are compared, **Then** they expose compatible forward APIs and identical output shapes.

### User Story 3 - Readiness-Aware Network Surface (Priority: P3)

As a project maintainer, I need the model surface to respect the Feature 038 readiness block so that network architecture work does not accidentally become training work.

**Why this priority**: The architecture must exist without implying training readiness or paper reproduction success.

**Independent Test**: Report artifacts and tests can show that no training loop, optimizer step, replay execution, or environment change was introduced.

**Acceptance Scenarios**:

1. **Given** the architecture report, **When** it is generated, **Then** it records the approved network configuration, compatibility checks, and the dependency status.
2. **Given** the Feature 038 readiness block, **When** this feature is reviewed, **Then** it does not claim training readiness or paper reproduction success.

### Edge Cases

- What happens when the Q-network hidden layers and the LSTM hidden size use the same paper notation but must be configured separately?
- How should the feature behave when torch is unavailable in the approved environment?
- What happens if the action mask is present only as metadata and not as a model output?
- How should the architecture report represent unresolved dependency availability without changing dependency files?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The feature MUST define a network architecture surface for HOODIE that is compatible with the Feature 038 state and action contracts.
- **FR-002**: The architecture MUST support a stable action space of three indices: local, horizontal, and vertical/cloud.
- **FR-003**: The architecture MUST separate q-network hidden layers from LSTM hidden configuration so the two concepts are independently configurable and independently validated.
- **FR-004**: The q-network hidden configuration MUST use three layers of width 1024 each.
- **FR-005**: The LSTM configuration MUST use a lookback window of 10, one LSTM layer, and hidden size 20.
- **FR-006**: The architecture MUST provide dueling value and advantage heads and MUST combine them into Q-values using a dueling-style aggregation.
- **FR-007**: The architecture MUST expose online-network and target-network instances that are architecture-compatible and share the same forward API shape.
- **FR-008**: The architecture MUST support Double-DQN-compatible action selection and target evaluation surfaces without implementing any training loss or update step.
- **FR-009**: The architecture MUST validate input and output shapes against the Feature 038 contracts and MUST not use privileged future information.
- **FR-010**: The architecture MUST define deterministic initialization behavior driven by the Feature 038 model-initialization seed.
- **FR-011**: The feature MUST create architecture report artifacts describing the config separation, shape validation, deterministic initialization, and dependency status.
- **FR-012**: The feature MUST record the failure state `dependency_blocked` if the approved environment does not provide the required network dependency and MUST not modify dependency files to resolve it.
- **FR-012a**: If the approved environment does not provide torch, the feature MUST set `dependency_status=blocked_missing_existing_torch` and stop without modifying dependency files.
- **FR-013**: The feature MUST NOT implement any training loop, optimizer step, replay sampling, replay buffer execution, gradient update loop, campaign runner, environment runtime change, baseline policy change, topology change, timeout/deadline change, execution change, transmission change, capacity-sharing change, reward-timing change, or reward-equation change.
- **FR-014**: The feature MUST NOT claim paper reproduction success or tune network output to resemble paper curves.
- **FR-015**: The feature MUST keep replay_memory_capacity=10000 and batch_size=64 as future-contract references only, not as live training behavior.
- **FR-016**: The architecture MUST consume Feature 038 state vectors in `batch_size x lookback_w x state_dim` form and MUST emit `batch_size x action_count` Q-values.
- **FR-017**: The architecture MUST keep `action_count = 3` and MUST preserve the Feature 038 stable action indices `0 local`, `1 horizontal`, and `2 vertical_cloud`.
- **FR-018**: The architecture MUST keep horizontal actions generic and helper-resolved rather than expanding to per-destination outputs.
- **FR-019**: The architecture MUST encode the `W=10` history with an LSTM before the 3 x 1024 Q-network body.
- **FR-020**: The architecture MUST branch the dueling value and advantage heads after the shared body, not before it.
- **FR-021**: The feature MUST limit Double-DQN scope to architecture surfaces only and MUST NOT implement loss computation or target-network update logic.
- **FR-022**: The feature MUST preserve the unresolved target-update frequency meaning from Feature 038 and MUST NOT resolve it in this feature.

### Key Entities *(include if feature involves data)*

- **Architecture Config**: The versioned network configuration describing Q-network hidden layers, LSTM settings, and output-action shape.
- **Online Network**: The primary network surface used for action selection surfaces in future work.
- **Target Network**: The companion network surface used for target evaluation surfaces in future work.
- **Dueling Heads**: The value and advantage heads that produce stable Q-values.
- **Shape Validation Report**: The artifact that records configuration separation, compatibility checks, and deterministic initialization status.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The architecture can be instantiated and validated without any training loop or optimizer step.
- **SC-002**: Shape validation confirms the three-action output space and the separated Q-network/LSTM configuration.
- **SC-003**: Deterministic initialization produces matching architecture structure and output shapes across repeated instantiations with the same seed.
- **SC-004**: The feature generates JSON and Markdown reports that explicitly record the dependency status and the no-training constraints.
- **SC-005**: The feature does not change runtime contracts, dependency files, or policy behavior, and it does not claim paper reproduction success.

## Assumptions

- Feature 038 remains the gatekeeper for training readiness, and this feature only prepares the architecture surface.
- The approved environment may already provide the required network dependency; if not, the feature must stop with a dependency-blocked report rather than changing dependency files.
- If torch is unavailable in the approved environment, the feature must stop with `dependency_status=blocked_missing_existing_torch` rather than adding dependencies or altering dependency files.
- The stable action space remains the three actions defined by Feature 038.
- The target-update meaning remains unresolved from Feature 038 and must not be reinterpreted here.
- Future replay and training work may reuse the architecture contract, but this feature itself does not perform those operations.

## Production Constraints

- [x] Performance budgets identified
- [x] Artifact handling rules identified
- [x] Security and secret-hygiene constraints identified
- [x] CI quality gate impact identified

The implementation must stop short of training and must not expand the repository scope beyond model architecture and report artifacts.

## Public Interfaces Affected

- [x] Runtime model interface
- [x] Config schema
- [x] Artifact schema
- [x] Evaluation metric interface

This feature defines architecture surfaces and validation artifacts only; it does not alter environment, policy, or reward interfaces.

## Config / Schema Impact

- [x] Required config fields identified
- [x] Validation rules identified
- [x] Backward-compatibility impact identified

The architecture config must separately encode q-network hidden layers, LSTM settings, and output-action sizing.

## Artifact Impact

- [x] Reports
- [x] Validation summaries

This feature requires architecture report artifacts only.

## Security Considerations

- [x] Secrets / tokens / credentials reviewed
- [x] Remote code execution reviewed
- [x] External references documented

No secret-bearing behavior is introduced. External references remain non-authoritative and must be mapped to the HOODIE paper or assumptions log before any borrowing is approved.

## Definition of Done

- [x] Spec matched by plan
- [x] Tests identified
- [x] Assumptions documented
- [x] Configs validated or updated
- [x] Paper-to-code mapping updated
- [x] Artifacts handled per lifecycle rules
- [x] Review and merge gate satisfied

Feature 039 is done when the architecture surface exists, shape and initialization tests pass, and the report artifacts explicitly confirm that no training or dependency drift occurred.
