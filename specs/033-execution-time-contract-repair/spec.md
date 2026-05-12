# Feature Specification: Execution-Time Contract Repair

**Feature Branch**: `033-execution-time-contract-repair`  
**Created**: 2026-05-12  
**Status**: Draft  
**Input**: User description: "Feature 033 — Execution-Time Contract Repair"

## User Scenarios & Testing *(mandatory)*

## Clarifications

### Session 2026-05-12

- Q: Confirm every execution destination consumes at most the configured compute capacity per simulator slot, with local/private using `ComputeConfig.cpu_capacity_per_slot_agent`, public/edge/horizontal using `ComputeConfig.cpu_capacity_per_slot_edge`, and cloud/vertical using `ComputeConfig.cpu_capacity_per_slot_cloud`. → A: Confirmed. Every execution destination consumes at most its configured compute capacity per simulator slot, with local/private using `ComputeConfig.cpu_capacity_per_slot_agent`, public/edge/horizontal using `ComputeConfig.cpu_capacity_per_slot_edge`, and cloud/vertical using `ComputeConfig.cpu_capacity_per_slot_cloud`.
- Q: Confirm the current local-compute shortcut in `step_execution` must be removed. → A: Confirmed. The shortcut that allows local/private execution to consume all remaining cycles immediately when `cycles_required` exceeds capacity is invalid and must be removed.
- Q: Define the completion-slot contract for a task that finishes during slot `t`. → A: Completion is recorded at the end of the current processing slot `t`, and reward timing must not be changed.
- Q: Confirm whether `SharedRuntimeParameters` / `advance_shared_runtime` creates a conflicting execution-time model. → A: The feature does not rewrite the runtime model unless tests prove it is necessary; the scope is limited to repairing execution-time correctness where the current execution helper conflicts with the compute-capacity contract.
- Q: Confirm timeout/drop interaction with multi-slot execution. → A: Timeout/drop is evaluated against actual multi-slot execution progress, and a task that has not consumed all required cycles must not be terminal completed.

### User Story 1 - Capacity-Bounded Execution (Priority: P1)

As a model or evaluator consuming the simulator, I need each execution destination to process at most its configured slot capacity so that multi-slot tasks behave consistently across local, public, and cloud execution.

**Why this priority**: This is the defect that invalidates delay, timeout, and reward semantics. Without it, the simulator can finish work too early and corrupt every downstream result.

**Independent Test**: Run a task whose required cycles exceed the configured per-slot capacity and verify it takes multiple slots to complete, with progress capped each slot.

**Acceptance Scenarios**:

1. **Given** a task requiring more cycles than the configured capacity, **When** it executes locally, **Then** it consumes no more than the local slot capacity in a single slot and remains unfinished.
2. **Given** a task requiring exactly the configured capacity, **When** it executes on any supported destination, **Then** it completes according to the documented completion-slot contract.

---

### User Story 2 - Consistent Destination Accounting (Priority: P2)

As a simulator user, I need local, public, and cloud execution to follow the same accounting rule so that destination choice changes where work runs, not how capacity is applied.

**Why this priority**: Destination-specific shortcuts create invalid comparisons and make the runtime behavior inconsistent.

**Independent Test**: Execute equivalent tasks on local, public, and cloud destinations and verify the per-slot cycle consumption matches the configured capacity for each destination kind.

**Acceptance Scenarios**:

1. **Given** equivalent tasks routed to local, public, and cloud destinations, **When** each task advances one simulator slot, **Then** each consumes at most the configured capacity for that destination kind.
2. **Given** a task spanning multiple slots, **When** its remaining cycles are observed across steps, **Then** the remaining cycles decrease monotonically until completion.

---

### User Story 3 - Timeout and Reward Integrity (Priority: P3)

As a researcher relying on terminal outcomes, I need timeout/drop evaluation and delayed reward emission to remain intact while execution now spans multiple slots.

**Why this priority**: Fixing execution duration must not break the environment’s terminal-state handling or reward timing.

**Independent Test**: Run a task that spans several slots and another that times out while in progress, then verify completion/drop handling and reward emission happen only at terminal resolution.

**Acceptance Scenarios**:

1. **Given** a task that completes after multiple execution slots, **When** the final slot is processed, **Then** completion is recorded at the end of that slot and reward is emitted only once.
2. **Given** a task that exceeds its deadline before finishing, **When** timeout is evaluated after execution progress, **Then** the task is dropped and no premature reward is emitted.

### Edge Cases

- What happens when a task requires exactly one slot of capacity? It should complete according to the documented completion-slot contract and not spill into an extra slot.
- What happens when a task has zero remaining cycles at the start of a step? It should not consume additional capacity.
- What happens when a destination kind has no distinct execution path? It should still obey the same slot-capacity rule as other destinations.
- If a task crosses a timeout boundary before consuming all required cycles, the timeout/drop path wins after execution progress and before reward emission.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST cap execution progress for each supported destination kind to the configured per-slot compute capacity.
- **FR-002**: The system MUST apply the same execution accounting rule to local/private, public/edge, and cloud execution.
- **FR-003**: The system MUST require multiple simulator slots for any task whose remaining cycles exceed a destination’s per-slot capacity.
- **FR-004**: The system MUST record task completion only after the final slot’s execution progress has been applied.
- **FR-005**: The system MUST keep timeout and drop evaluation after execution progress and before reward emission.
- **FR-006**: The system MUST preserve delayed reward emission so rewards are emitted only on terminal completion or drop.
- **FR-007**: The system MUST preserve Feature 032 capacity values and must not alter topology, link rate, vertical/cloud legality, or aggregation semantics.
- **FR-008**: The system MUST remove any shortcut that allows a local task to consume all remaining cycles in a single slot when its required cycles exceed configured capacity.
- **FR-009**: The system MUST expose deterministic completion-slot semantics that are consistent across supported destinations.
- **FR-010**: The system MUST evaluate timeout and drop state after execution progress for the current slot and before reward emission.
- **FR-011**: The system MUST preserve the existing environment step reward timing contract while making completion-slot recording explicit.

### Key Entities *(include if feature involves data)*

- **Execution Contract**: The rule set describing how many cycles a destination may consume per simulator slot and when completion is recorded.
- **Task Cycle State**: The remaining cycles and completion state of a task as it progresses through slots.
- **Destination Kind**: The supported execution targets subject to the same slot-capacity accounting rule.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A task requiring more than the smallest configured slot capacity completes in more than one simulator slot in 100% of tested cases.
- **SC-002**: For all supported destination kinds, single-slot cycle consumption never exceeds the configured per-slot capacity in repeated tests.
- **SC-003**: Timeout/drop cases still resolve correctly after multi-slot execution in 100% of targeted regression tests.
- **SC-004**: Reward is emitted only at terminal completion or drop in 100% of the validated scenarios.
- **SC-005**: The repaired execution contract produces no regressions in topology, link rate, aggregation, or Feature 032 legality behavior.

## Assumptions

- Feature 032 capacities remain authoritative for local/private, public/edge, and cloud execution.
- The existing environment step lifecycle remains the user-facing completion-slot contract unless the repair requires a documented correction.
- No transmission-delay runtime wiring is introduced in this feature.
- No public/cloud capacity-sharing redesign is introduced in this feature.
- The execution-time repair should preserve existing topology, link-rate, timeout, aggregation, and reward timing behavior except for correcting the one-slot shortcut.
- SharedRuntimeParameters / advance_shared_runtime remain unchanged unless tests prove they conflict with the repaired execution contract.

## Production Constraints

- [ ] Performance budgets identified
- [ ] Artifact handling rules identified
- [ ] Security and secret-hygiene constraints identified
- [ ] CI quality gate impact identified

## Public Interfaces Affected

- [ ] Environment reset/step
- [ ] Policy interface
- [ ] Task model
- [ ] Topology interface
- [ ] Runtime model interface
- [ ] Evaluation metric interface
- [ ] Config schema
- [ ] Artifact schema

## Config / Schema Impact

- [x] Required config fields identified
- [x] Validation rules identified
- [x] Backward-compatibility impact identified

## Artifact Impact

- [ ] Raw metrics
- [ ] Plots
- [ ] Reports
- [ ] Checkpoints
- [ ] Debug traces
- [ ] Validation summaries

## Security Considerations

- [ ] Secrets / tokens / credentials reviewed
- [ ] Remote code execution reviewed
- [ ] External references documented

## Definition of Done

- [ ] Spec matched by plan
- [ ] Tests identified
- [ ] Assumptions documented
- [ ] Configs validated or updated
- [ ] Paper-to-code mapping updated
- [ ] Artifacts handled per lifecycle rules
- [ ] Review and merge gate satisfied
