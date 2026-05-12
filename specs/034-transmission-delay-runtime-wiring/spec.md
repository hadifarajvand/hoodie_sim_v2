# Feature Specification: Transmission Delay Runtime Wiring

**Feature Branch**: `034-transmission-delay-runtime-wiring`  
**Created**: 2026-05-12  
**Status**: Draft  
**Input**: User description: "Feature 034 — Transmission Delay Runtime Wiring"

## User Scenarios & Testing *(mandatory)*

## Clarifications

### Session 2026-05-12

- Q: Confirm task.size is Mbits in runtime traces/config and payload_bits should be derived as `mbits_to_bits(task.size)`. → A: Confirmed. `task.size` is measured in Mbits in runtime traces/config, and `payload_bits = mbits_to_bits(task.size)`.
- Q: Confirm horizontal/offload_horizontal uses `LinkRateConfig.horizontal_data_rate_bps` from R_H = 30 Mbps. → A: Confirmed. Horizontal/offload_horizontal uses `LinkRateConfig.horizontal_data_rate_bps` from R_H = 30 Mbps.
- Q: Confirm vertical/offload_vertical uses `LinkRateConfig.vertical_data_rate_bps` / cloud-facing vertical rate from R_V = 10 Mbps and no separate cloud-specific data rate is introduced. → A: Confirmed. Vertical/offload_vertical uses the cloud-facing vertical rate from R_V = 10 Mbps and no separate cloud-specific data rate is introduced.
- Q: Confirm `compute_transmission_delay()` with `LinkRateConfig.rounding_policy` is the single source of `delay_slots`, with default rounding remaining `ceil` unless explicitly changed. → A: Confirmed. `compute_transmission_delay()` with `LinkRateConfig.rounding_policy` is the single source of `delay_slots`, and the default rounding remains `ceil`.
- Q: Confirm the offload admission boundary semantics. → A: Confirmed. Transmission completes when `current_slot >= transmission_started_at + delay_slots`. For `delay_slots = 0`, admission occurs deterministically on the same step when the boundary is satisfied.
- Q: Confirm the transmission metadata fields to record. → A: Confirmed. Record `transmission_started_at`, `transmission_completed_at`, `transmission_delay_slots`, `transmission_delay_seconds`, `transmission_payload_bits`, `transmission_data_rate_bps`, and `transmission_rate_source`.
- Q: Confirm timeout/drop includes time spent in the offloading queue and no reward is emitted while a task is still transmitting. → A: Confirmed. Timeout/drop includes offloading-queue time, and reward is not emitted while a task is still transmitting.
- Q: Confirm Feature 034 scope boundaries. → A: Confirmed. Feature 034 does not redesign public/cloud capacity sharing, the execution-time contract, topology legality, policy behavior, training, or baseline campaign execution.

### User Story 1 - Payload-Based Offload Delay (Priority: P1)

As a simulator user, I need offloaded tasks to spend transmission time proportional to payload size and link rate so that horizontal and vertical offloads no longer complete in one fixed step.

**Why this priority**: This is the core defect. Without transmission delay, offloading is unrealistically instantaneous and corrupts runtime behavior.

**Independent Test**: Run the same offloaded task through horizontal and vertical paths and verify the transmission delay differs according to the configured data rate.

**Acceptance Scenarios**:

1. **Given** a horizontal offload with a nonzero payload, **When** it enters transmission, **Then** completion occurs only after the required number of transmission delay slots.
2. **Given** a vertical offload with the same payload, **When** it enters transmission, **Then** it takes longer than the horizontal path because the vertical rate is slower.

---

### User Story 2 - Deterministic Offload Queue Admission (Priority: P2)

As a researcher, I need offloading queues to admit tasks only after transmission delay is satisfied so that queue progression is deterministic and traceable.

**Why this priority**: Queue admission timing determines downstream execution timing and timeout behavior.

**Independent Test**: Advance an offloading queue one slot at a time and confirm that a task is not admitted until the documented transmission boundary.

**Acceptance Scenarios**:

1. **Given** a task in the offloading queue, **When** the current slot is still before the transmission boundary, **Then** the task remains in transmission.
2. **Given** the same task at the documented boundary, **When** the slot advances, **Then** the task moves into the next runtime queue exactly once.

---

### User Story 3 - Timeout and Reward Integrity (Priority: P3)

As a platform operator, I need transmission delay to count toward total runtime delay without changing reward timing so that timeout/drop handling remains correct.

**Why this priority**: Transmission delay must not break terminal-state handling or reward emission semantics.

**Independent Test**: Run an offloaded task that exceeds its deadline during transmission and verify it drops before reward emission.

**Acceptance Scenarios**:

1. **Given** a task still transmitting, **When** its deadline passes, **Then** the task drops and reward is emitted only at the terminal event.
2. **Given** a task that finishes transmission before its deadline, **When** it is admitted downstream, **Then** the existing execution contract remains unchanged.

### Edge Cases

- What happens when task payload is zero? The transmission delay is explicitly zero and admission is immediate.
- What happens when the offload rate is slower than expected? The delay increases according to the configured rate and slot duration.
- What happens when the task is local? No transmission delay is applied.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST apply transmission delay to horizontal offloads based on task payload size and horizontal link rate.
- **FR-002**: The system MUST apply transmission delay to vertical offloads based on task payload size and the cloud-facing vertical link rate.
- **FR-003**: The system MUST keep local execution free of transmission delay.
- **FR-004**: The system MUST defer offload queue admission until the computed transmission delay has elapsed.
- **FR-005**: The system MUST record deterministic transmission metadata for offloaded tasks.
- **FR-006**: The system MUST include transmission delay in total runtime delay when evaluating timeout and drop behavior.
- **FR-007**: The system MUST preserve delayed reward emission and must not change the reward equation.
- **FR-008**: The system MUST use the approved horizontal rate of 30 Mbps and cloud-facing vertical rate of 10 Mbps.
- **FR-009**: The system MUST preserve the execution-time contract from Feature 033 without changing compute-capacity execution behavior.
- **FR-010**: The system MUST avoid introducing a separate cloud-specific data rate distinct from the approved vertical rate.

### Key Entities *(include if feature involves data)*

- **Transmission Contract**: The rules that determine how many slots an offload must spend in transit before downstream admission.
- **Transmission Metadata**: The recorded payload, rate, delay, and boundary timestamps for an offloaded task.
- **Offload Path**: The horizontal or vertical route used to determine the applicable transmission rate.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A horizontal offload with a nonzero payload never completes transmission in fewer slots than required by the configured rate.
- **SC-002**: A vertical offload with the same payload takes more transmission slots than the horizontal case because the vertical rate is lower.
- **SC-003**: Offloading queue admission occurs exactly at the documented transmission boundary in repeated tests.
- **SC-004**: Timeout/drop cases that depend on transmission delay still resolve correctly in 100% of targeted regression tests.
- **SC-005**: Reward timing remains terminal-only in 100% of validated offload scenarios.

## Assumptions

- Feature 032 link-rate values remain authoritative: horizontal 30 Mbps and vertical 10 Mbps.
- Feature 033 execution-capacity behavior remains unchanged.
- Transmission delay is a runtime wiring concern, not a reward or topology redesign.
- Zero-payload handling should be explicit and deterministic.
- No separate cloud-specific transmission rate will be introduced.

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
