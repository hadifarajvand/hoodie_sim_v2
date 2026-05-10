# Feature Specification: Reference Task Lifecycle Kernel

**Feature Branch**: `017-reference-task-lifecycle-kernel`  
**Created**: 2026-05-09  
**Status**: Draft  
**Input**: User description: "Feature 017 — Reference Task Lifecycle Kernel"

## Clarifications

### Session 2026-05-09

- Q: What is the deterministic lifecycle event ordering for reference runs? → A: `created` always occurs first, `selected_action` is recorded before any queue/offload event, and all subsequent events follow the path-specific order defined in the acceptance scenarios below.
- Q: What is the timeout boundary behavior? → A: The task is considered timed out when it reaches the documented terminal timeout boundary; the exact boundary is treated as a deterministic reference constant in the tests, not a simulator repair target.
- Q: When does `reward_emitted` occur? → A: It occurs only in the same terminal slot as `execution_completed` or `dropped_timeout`, never at decision time.
- Q: Does horizontal offload require transmission events before queueing? → A: Yes. For the reference path, `selected_action` is followed by `queued_public`, then `transmission_started`, `transmission_completed`, `execution_started`, `execution_completed`, and `reward_emitted`.
- Q: Does vertical offload include `offloaded_cloud` plus transmission/execution events? → A: Yes. For the reference path, `selected_action` is followed by `offloaded_cloud`, `transmission_started`, `transmission_completed`, `execution_started`, `execution_completed`, and `reward_emitted`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Deterministic local task ledger (Priority: P1)

As a maintainer, I want a minimal reference lifecycle engine that can process a single hand-fed task with a hand-fed action and emit a deterministic ledger so that task lifecycle behavior can be audited without relying on the simulator.

**Why this priority**: This is the smallest useful slice. Without a deterministic ledger for a single task, there is no reference behavior to audit.

**Independent Test**: Provide one task and a local-compute action, then verify the emitted ledger always contains the same ordered lifecycle events and terminal state.

**Acceptance Scenarios**:

1. **Given** a single created task and a local-compute action, **When** the reference engine advances the task lifecycle, **Then** it emits `created`, `selected_action`, `execution_started`, `execution_completed`, and `reward_emitted` in deterministic order with no queue or transmission events.
2. **Given** the same inputs and ties in the same slot, **When** the lifecycle is replayed, **Then** the ledger order is identical across runs.
3. **Given** a timeout boundary reached by the task, **When** the lifecycle advances, **Then** the terminal event is `dropped_timeout` and `reward_emitted` occurs in the same terminal slot.

---

### User Story 2 - Deterministic offload lifecycles (Priority: P2)

As a maintainer, I want horizontal and vertical offload lifecycles to be represented as explicit reference paths so that offload semantics can be compared against the paper-backed registry without mutating the simulator.

**Why this priority**: Offload behavior is the main place where lifecycle drift tends to hide. It must be expressible independently of policies and campaigns.

**Independent Test**: Feed one task plus a horizontal-offload action and one task plus a vertical-offload action, then verify each path produces the expected ordered ledger and terminal state.

**Acceptance Scenarios**:

1. **Given** a task with a horizontal-offload action, **When** the lifecycle is advanced, **Then** the ledger records `selected_action`, `queued_public`, `transmission_started`, `transmission_completed`, `execution_started`, `execution_completed`, and `reward_emitted` in deterministic order.
2. **Given** a task with a vertical-offload action, **When** the lifecycle is advanced, **Then** the ledger records `selected_action`, `offloaded_cloud`, `transmission_started`, `transmission_completed`, `execution_started`, `execution_completed`, and `reward_emitted` in deterministic order.
3. **Given** a same-slot tie between two offload-complete tasks, **When** the lifecycle is advanced, **Then** the ledger order is stable across repeated runs and is not affected by incidental execution order.

---

### User Story 3 - Timeout and delayed reward reference behavior (Priority: P3)

As a maintainer, I want timeout and delayed-reward semantics to be fixed in the reference engine so that completion and drop behavior can be audited without inventing new simulator behavior.

**Why this priority**: Reward timing and timeout handling are the main failure modes for lifecycle auditing, but they only matter after the basic paths exist.

**Independent Test**: Feed a task that times out and verify the ledger ends in a drop state and emits reward only on the terminal event, not at decision time.

**Acceptance Scenarios**:

1. **Given** a task that reaches the timeout boundary, **When** the lifecycle advances, **Then** it emits `dropped_timeout` and `reward_emitted` only on the terminal slot.
2. **Given** a task that completes successfully, **When** the lifecycle advances, **Then** it emits `reward_emitted` only after `execution_completed`, never at `selected_action`.
3. **Given** a task with ambiguous reward timing, **When** the lifecycle advances, **Then** reward emission is deferred until the terminal completion or drop event and never earlier.

---

### Edge Cases

- What happens when two tasks share the same slot? The reference ledger must still order events deterministically.
- What happens when a task is handed an unsupported action? The engine must reject it as unresolved or assumption-backed, not invent a new lifecycle path.
- What happens when a task reaches the timeout boundary exactly? The boundary condition must be documented and tested explicitly.
- What happens when reward timing is ambiguous? The engine must emit reward only on terminal completion or drop, never on decision.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a minimal deterministic task lifecycle engine that accepts hand-fed task inputs and hand-fed actions without policy selection or campaign orchestration.
- **FR-002**: The system MUST emit a task ledger that records observable lifecycle events in deterministic order.
- **FR-003**: The system MUST support the lifecycle events `created`, `selected_action`, `queued_private`, `queued_public`, `offloaded_cloud`, `transmission_started`, `transmission_completed`, `execution_started`, `execution_completed`, `dropped_timeout`, and `reward_emitted`.
- **FR-004**: The system MUST support one-task local compute, one-task horizontal offload, one-task vertical offload, timeout/drop, delayed reward, and same-slot tie ordering as independently testable reference cases.
- **FR-005**: The system MUST emit `reward_emitted` only on terminal completion or drop, never at decision time.
- **FR-006**: The system MUST define deterministic ledger ordering for same-slot or tie conditions so that repeated runs with the same inputs produce identical event sequences.
- **FR-007**: The system MUST reject or clearly document any unsupported lifecycle path as unresolved or assumption-backed rather than inventing paper-validated behavior.
- **FR-008**: The system MUST not mutate `HoodieGymEnvironment`, existing campaign artifacts, baseline artifacts, or any simulator runtime behavior.
- **FR-009**: The system MUST not introduce policies, baselines, training loops, evaluation metric changes, dependency changes, or external simulation dependencies such as DRL, TorchRL, Gymnasium, ns-3, or ns-3-gym.
- **FR-010**: The specification MUST distinguish between reference behavior that is explicitly testable and paper details that remain unresolved or assumption-backed.

### Key Entities *(include if feature involves data)*

- **Task**: A single hand-fed task instance that moves through a deterministic lifecycle and ends in completion or timeout/drop.
- **Action**: A hand-fed decision applied to a task, limited to local compute, horizontal offload, or vertical offload for the reference tests.
- **Lifecycle Event**: An observable ledger entry representing a state transition or terminal outcome for a task.
- **Task Ledger**: The ordered record of events for one task, used as the reference output for tests.
- **Terminal State**: The final lifecycle condition of a task, either successful completion or timeout/drop.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A single-task local-compute reference run produces the same ledger ordering across repeated executions with identical inputs.
- **SC-002**: Horizontal offload and vertical offload reference runs each produce their full expected lifecycle event sequence without relying on policy or campaign code.
- **SC-003**: Timeout/drop reference runs emit the terminal drop event and the delayed reward event only after the drop is reached.
- **SC-004**: Same-slot or tie conditions do not change the emitted ledger order across repeated runs.
- **SC-005**: The specification can be used as a reference for auditing lifecycle drift without changing simulator behavior.

## Assumptions

Any assumption that materially changes code, workflow, or repository state MUST be recorded and
presented for user approval before implementation depends on it.

- The reference engine is intentionally smaller than the simulator and is not a replacement for it.
- Unsupported paper details remain unresolved or assumption-backed rather than being filled in as facts.
- The test harness may define the precise tie-break order as long as it is deterministic and documented.
- The reference engine is allowed to represent terminal reward timing without matching any undocumented simulator shortcut.
- Horizontal offload in the reference kernel uses `queued_public` before transmission events; vertical offload uses `offloaded_cloud` before transmission events.
- The timeout boundary is a deterministic test constant, not a claim about simulator internals.

## Production Constraints

- [x] Performance budgets identified
- [x] Artifact handling rules identified
- [x] Security and secret-hygiene constraints identified
- [x] CI quality gate impact identified

## Public Interfaces Affected

- [ ] Environment reset/step
- [ ] Policy interface
- [x] Task model
- [ ] Topology interface
- [x] Runtime model interface
- [ ] Evaluation metric interface
- [ ] Config schema
- [x] Artifact schema

## Config / Schema Impact

- [x] Required config fields identified
- [x] Validation rules identified
- [x] Backward-compatibility impact identified

## Artifact Impact

- [ ] Raw metrics
- [ ] Plots
- [ ] Reports
- [ ] Checkpoints
- [x] Debug traces
- [x] Validation summaries

## Security Considerations

- [x] Secrets / tokens / credentials reviewed
- [x] Remote code execution reviewed
- [x] External references documented

## Definition of Done

- [ ] Spec matched by plan
- [ ] Tests identified
- [ ] Assumptions documented
- [ ] Configs validated or updated
- [ ] Paper-to-code mapping updated
- [ ] Artifacts handled per lifecycle rules
- [ ] Review and merge gate satisfied
