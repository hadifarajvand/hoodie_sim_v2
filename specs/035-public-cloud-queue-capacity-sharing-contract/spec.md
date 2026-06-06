# Feature Specification: Public/Cloud Queue Capacity Sharing Contract

**Feature Branch**: `035-public-cloud-queue-capacity-sharing-contract`  
**Created**: 2026-05-12  
**Status**: Draft  
**Input**: User description: "Feature 035 — Public/Cloud Queue Capacity Sharing Contract"

## User Scenarios & Testing *(mandatory)*

## Clarifications

### Session 2026-05-12

- Q: Confirm each destination EA public host has fixed public capacity per slot and that it does not multiply by the number of source queues. → A: Confirmed. Each destination EA public host has fixed public capacity per slot `ComputeConfig.cpu_capacity_per_slot_edge`, and it does not multiply by the number of source queues.
- Q: Confirm cloud has one fixed global capacity per slot and that it does not multiply by the number of source queues. → A: Confirmed. Cloud has one fixed global capacity per slot `ComputeConfig.cpu_capacity_per_slot_cloud`, and it does not multiply by the number of source queues.
- Q: Confirm the default sharing rule for active queue heads at slot start. → A: Confirmed. Use deterministic equal-share across active queue heads at slot start, with `per_head_capacity = host_capacity / k`.
- Q: Confirm the definition of an active head. → A: Confirmed. An active head is the first task in a public queue that is ready for execution at the beginning of the slot; queued tasks behind the head are not active heads.
- Q: Confirm the redistribution policy when a task finishes early. → A: Confirmed. No same-slot leftover redistribution; unused share is not reassigned until the next slot.
- Q: Confirm how hosts are grouped for sharing. → A: Confirmed. Public queues are grouped by destination EA `host_node_id`, cloud queues are grouped under `host_node_id == "cloud"`, and the public EA capacity pool is separate from the cloud capacity pool.
- Q: Confirm the deterministic ordering requirement. → A: Confirmed. Process host groups and active heads in stable deterministic order without random scheduling.

### User Story 1 - Shared Public Capacity (Priority: P1)

As a simulator user, I need multiple public queues targeting the same edge host to share that host's public CPU capacity fairly and deterministically so that one host cannot be over-consumed by parallel queue heads.

**Why this priority**: This fixes the core capacity-duplication defect for edge offloading and prevents inflated performance results.

**Independent Test**: Create two active public queues that target the same edge host and verify the host's total CPU consumption per slot stays within the configured limit while each head receives an equal share.

**Acceptance Scenarios**:

1. **Given** two active public queues targeting the same edge host, **When** the simulator advances one slot, **Then** the host's total CPU consumption does not exceed the configured edge capacity and each active head receives the same share.
2. **Given** a single active public queue targeting an edge host, **When** the simulator advances one slot, **Then** that queue can consume the full configured edge capacity for that host.
3. **Given** two active public queues targeting different edge hosts, **When** the simulator advances one slot, **Then** each host uses its own configured edge capacity independently.

---

### User Story 2 - Shared Cloud Capacity (Priority: P2)

As a simulator user, I need cloud-bound queues to share the cloud CPU capacity deterministically so that cloud offloading does not multiply CPU capacity when multiple queues are active at once.

**Why this priority**: Cloud over-consumption creates the same fiction as edge duplication, but in the cloud path.

**Independent Test**: Create multiple active cloud queues and verify the cloud's total CPU consumption per slot stays within the configured cloud capacity while each active head receives an equal share.

**Acceptance Scenarios**:

1. **Given** two active cloud queues, **When** the simulator advances one slot, **Then** the cloud's total CPU consumption does not exceed the configured cloud capacity and both active heads receive the same share.
2. **Given** a single active cloud queue, **When** the simulator advances one slot, **Then** that queue can consume the full configured cloud capacity.

---

### User Story 3 - Deterministic Scheduling and Regression Safety (Priority: P3)

As a simulator maintainer, I need the shared-capacity contract to remain deterministic and isolated from unrelated behavior so that the fix is testable and does not alter local execution, transmission delay, or reward timing.

**Why this priority**: Determinism and regression safety keep the fix reviewable and prevent accidental scope creep.

**Independent Test**: Run the same multi-queue setup repeatedly and verify the same heads receive the same shares in the same order, with no changes to local/private behavior or reward timing.

**Acceptance Scenarios**:

1. **Given** the same set of active public or cloud queues, **When** the simulator runs multiple times with the same inputs, **Then** the share allocation order and per-slot consumption are identical.
2. **Given** local/private execution, **When** the simulator runs under this feature, **Then** local/private queue behavior remains unchanged.
3. **Given** transmission-delayed offloads and terminal reward handling, **When** the simulator runs under this feature, **Then** transmission delay and reward timing remain unchanged.

### Edge Cases

- What happens when only one queue targets a host? That queue receives the full host capacity for the slot.
- What happens when several queues target the same host? The host capacity is split evenly across the active heads for that slot.
- What happens when a head finishes early within a slot? Any leftover capacity is not redistributed until the next slot.
- What happens when queues target different hosts? Each host shares capacity independently.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST ensure that each edge host consumes no more than its configured public CPU capacity in any simulator slot.
- **FR-002**: The system MUST ensure that each cloud host consumes no more than its configured cloud CPU capacity in any simulator slot.
- **FR-003**: The system MUST share a host's capacity evenly across all active queue heads targeting that host at the start of the slot.
- **FR-004**: The system MUST apply a deterministic ordering when selecting active public and cloud queue heads for sharing.
- **FR-005**: The system MUST keep different hosts independent so that queues targeting different hosts do not affect each other's per-slot capacity.
- **FR-006**: The system MUST leave local/private queue behavior unchanged unless required for regression comparison.
- **FR-007**: The system MUST preserve the Feature 033 execution-capacity contract and the Feature 034 transmission-delay contract.
- **FR-008**: The system MUST not redistribute leftover capacity from early completion within the same slot.
- **FR-009**: The system MUST produce repeatable results for the same queue configuration and input order.
- **FR-010**: The system MUST avoid claiming this behavior as paper-recovered unless explicitly documented elsewhere.
- **FR-011**: The system MUST treat public EA capacity as `ComputeConfig.cpu_capacity_per_slot_edge` per destination host, independent of the number of source queues.
- **FR-012**: The system MUST treat cloud capacity as `ComputeConfig.cpu_capacity_per_slot_cloud` for the global cloud host, independent of the number of source queues.
- **FR-013**: The system MUST define an active head as the first task in a public queue that is ready for execution at the beginning of the slot.
- **FR-014**: The system MUST group horizontal/public queues by destination EA `host_node_id` and cloud queues under `host_node_id == "cloud"`.

### Key Entities *(include if data involved)*

- **Public Queue Host**: An edge host that can serve multiple public queues while enforcing a fixed per-slot CPU budget.
- **Cloud Queue Host**: The shared cloud execution host that can serve multiple queues while enforcing a fixed per-slot CPU budget.
- **Active Queue Head**: The queue head selected at slot start to receive a share of host capacity.
- **Capacity Share**: The per-head portion of a host's slot capacity under the equal-share rule.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A single active public queue can consume up to 100% of its host's public CPU capacity in a slot.
- **SC-002**: Two active public queues targeting the same host each receive 50% of that host's public CPU capacity, and the host total never exceeds 100%.
- **SC-003**: Two active public queues targeting different hosts each receive the full capacity of their own host in the same slot.
- **SC-004**: Two active cloud queues each receive 50% of cloud capacity, and cloud total consumption never exceeds the configured cloud limit.
- **SC-005**: Repeating the same multi-queue scenario produces identical share allocation order and identical per-slot consumption.
- **SC-006**: Regression tests confirm local/private execution, transmission delay, and reward timing remain unchanged.
- **SC-007**: The same host never exceeds its configured capacity in a slot, even when multiple source queues target that host.

## Assumptions

- Feature 033 execution-capacity behavior remains authoritative for local/private execution.
- Feature 034 transmission-delay behavior remains authoritative for offload timing.
- The equal-share rule is the default capacity-sharing policy for both public and cloud hosts.
- Leftover capacity from early completion is intentionally not redistributed in the same slot.
- This feature is a runtime engineering contract for a missing mechanism and does not recover paper behavior or alter paper registries.

## Production Constraints

- [x] Performance budgets identified
- [x] Artifact handling rules identified
- [x] Security and secret-hygiene constraints identified
- [x] CI quality gate impact identified

## Public Interfaces Affected

- [x] Environment reset/step
- [ ] Policy interface
- [x] Task model
- [x] Topology interface
- [x] Runtime model interface
- [x] Evaluation metric interface
- [x] Config schema
- [x] Artifact schema

## Config / Schema Impact

- [x] Required config fields identified
- [x] Validation rules identified
- [x] Backward-compatibility impact identified

## Artifact Impact

- [ ] Raw metrics
- [ ] Plots
- [x] Reports
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
