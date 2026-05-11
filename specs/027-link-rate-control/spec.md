# Feature Specification: Link-Rate Control

**Feature Branch**: `[027-link-rate-control]`  
**Created**: 2026-05-11  
**Status**: Draft  
**Input**: User description: "Feature 027 — Link-Rate Control Hook and Transmission Delay Contract.

Create a controlled mechanism feature that adds a public, config-backed link-rate control hook and an explicit transmission-delay contract for HOODIE environment experiments.

Problem:
Feature 020 classified link_rate as an instrumentation_gap because the current environment has no direct public link-rate control hook. Feature 025 recovered paper-backed horizontal and vertical data rates, but did not recover a distinct cloud data-rate constant or Figure 7 adjacency. Feature 026 added lifecycle trace observability but did not solve link-rate control or topology legality.

Primary goal:
Expose controlled, reproducible link-rate configuration and transmission-delay calculation without curve fitting, topology fabrication, policy redesign, metric changes, or training.

Required controls:
- horizontal data rate control
- vertical data rate control
- per-edge/offload link rate control only if supported without paper-topology fabrication
- explicit unit conversion for bits, Mbits, bps, Mbps, seconds, and slots
- transmission delay calculation contract
- deterministic validation artifact proving link-rate changes affect transmission delay monotonically where controllable

Paper-backed defaults:
- horizontal_data_rate = 30 Mbps from Feature 025 registry
- vertical_data_rate = 10 Mbps from Feature 025 registry
- cloud_data_rate remains unrecoverable unless paper evidence exists
- Figure 7 adjacency remains unrecoverable
- legal horizontal destinations remain non-paper-backed

Out of scope:
- no curve fitting to paper plots
- no paper topology fabrication
- no Figure 7 adjacency injection
- no policy redesign
- no metric formula changes except explicit transmission-delay component reporting if already part of environment accounting
- no baseline redesign
- no campaign reruns
- no DRL training
- no neural-network/model/trainer code
- no TorchRL
- no Gymnasium
- no ns-3 or ns-3-gym
- no dependency or lockfile changes
- no paper-validity claim

Success condition:
The repo has a public, deterministic link-rate configuration contract and tests proving transmission-delay calculations respond correctly to controlled horizontal/vertical data rates. If per-edge link rates cannot be supported without topology fabrication, they must be marked unsupported or blocked, not invented.

Failure condition:
If link-rate control requires invented topology, policy mutation, metric redesign, or campaign curve fitting, stop and report the blocker."

## Clarifications

### Session 2026-05-11

- Q: How should link-rate control be scoped across horizontal, vertical, and per-edge/offload paths? → A: Keep link-rate control limited to the public horizontal/vertical defaults, and explicitly mark per-edge/offload control unsupported unless a runtime-backed non-paper hook exists.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Configure Link Rates (Priority: P1)

As a HOODIE experiment author, I want to configure horizontal and vertical link rates explicitly so that I can run reproducible experiments with known transmission characteristics.

**Why this priority**: Link-rate control is the primary feature value. Without it, the environment still treats link rate as an instrumentation gap.

**Independent Test**: Can be tested by setting horizontal and vertical rates to known values and verifying the configured transmission-delay contract responds deterministically.

**Acceptance Scenarios**:

1. **Given** a valid configuration with horizontal and vertical rates set, **When** an experiment starts, **Then** those rates are available as the active defaults for controlled transmission timing.
2. **Given** a configuration that omits cloud rate evidence, **When** the feature is used, **Then** cloud rate remains explicitly unrecoverable rather than fabricated.
3. **Given** a per-edge/offload rate request without a runtime-backed non-paper hook, **When** the feature is used, **Then** the request is reported as unsupported or blocked instead of being invented.

---

### User Story 2 - Compute Transmission Delay (Priority: P2)

As a HOODIE experiment author, I want an explicit transmission-delay contract so that link-rate changes produce predictable timing effects that can be validated.

**Why this priority**: The core value of the feature is not the configuration alone, but a deterministic delay relationship that can be verified in experiments.

**Independent Test**: Can be tested by comparing identical workloads across different allowed link rates and confirming the calculated delay changes monotonically where control is permitted.

**Acceptance Scenarios**:

1. **Given** the same payload size and two valid horizontal link rates, **When** the higher rate is selected, **Then** the computed transmission delay is lower than or equal to the lower-rate case.
2. **Given** the same payload size and two valid vertical link rates, **When** the higher rate is selected, **Then** the computed transmission delay is lower than or equal to the lower-rate case.
3. **Given** a payload described in bits, Mbits, bps, or Mbps, **When** transmission delay is calculated, **Then** the conversion is explicit and consistent across units.

---

### User Story 3 - Respect Topology Boundaries (Priority: P3)

As a researcher, I want unsupported per-edge link-rate control to remain blocked unless it can be supported without fabricating topology so that paper evidence is not overstated.

**Why this priority**: The feature must remain honest about what the paper and environment can support. Unsupported controls are still valuable if they are clearly blocked rather than invented.

**Independent Test**: Can be tested by requesting per-edge/offload link-rate control and verifying that unsupported cases are labeled blocked or unsupported instead of being fabricated.

**Acceptance Scenarios**:

1. **Given** no runtime-backed non-paper hook, **When** per-edge link-rate control is requested, **Then** it is reported as unsupported or blocked rather than invented.
2. **Given** known horizontal and vertical defaults, **When** the feature is validated, **Then** legal horizontal destinations remain non-paper-backed and unrecoverable from paper evidence.

### Edge Cases

- What happens when the same workload is evaluated under two different valid link rates and the computed delay does not change monotonically?
- How does the system report a per-edge link-rate request when no supported topology hook exists?
- What happens when a unit conversion is ambiguous between bits and bytes?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a public, config-backed control for horizontal data rate.
- **FR-002**: The system MUST provide a public, config-backed control for vertical data rate.
- **FR-003**: The system MUST preserve unrecoverable status for cloud data rate unless paper evidence exists.
- **FR-004**: The system MUST define an explicit transmission-delay contract that can be evaluated deterministically from payload size and link rate.
- **FR-005**: The system MUST support explicit unit conversion rules for bits, Mbits, bps, Mbps, seconds, and slots.
- **FR-006**: The system MUST produce a deterministic validation artifact demonstrating that controllable link-rate changes affect transmission delay monotonically in the expected direction.
- **FR-007**: The system MUST mark per-edge/offload link-rate control as unsupported or blocked when it cannot be provided without fabricating topology.
- **FR-008**: The system MUST preserve the unrecoverable status of Figure 7 adjacency.
- **FR-009**: The system MUST preserve the non-paper-backed status of legal horizontal destinations.
- **FR-010**: The system MUST not require curve fitting, policy redesign, metric redesign, training, or campaign reruns to expose link-rate control.
- **FR-011**: The system MUST report the supported default horizontal and vertical data rates as paper-backed defaults from the recovered registry.
- **FR-012**: The system MUST keep unsupported controls clearly labeled rather than implying proof that the paper supports them.

### Key Entities *(include if feature involves data)*

- **Link-Rate Setting**: A controlled rate value used to determine transmission delay for an experiment.
- **Transmission-Delay Contract**: The explicit relationship between payload size, unit conversion, and delay outcome.
- **Conversion Rule**: A normalized mapping between rate and size units used to avoid ambiguity.
- **Control Scope**: The boundary that distinguishes supported horizontal/vertical controls from unsupported per-edge controls.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: At least one validation artifact demonstrates deterministic delay changes when horizontal or vertical link rates are increased within the supported control range.
- **SC-002**: 100% of supported rate configurations use explicit unit conversion rules without ambiguity in the validation artifacts.
- **SC-003**: 100% of unsupported per-edge link-rate requests are labeled blocked or unsupported rather than fabricated.
- **SC-004**: The recovered default horizontal and vertical rates are available in the contract artifacts, and cloud rate remains explicitly unrecoverable unless evidence exists.
- **SC-005**: Users can distinguish supported rate control from topology-bound controls without reading implementation details.

## Assumptions

- Horizontal and vertical default rates are treated as paper-backed defaults from the recovered registry.
- Cloud rate remains unrecoverable unless paper evidence is later recovered.
- Any per-edge/offload link-rate capability must remain blocked unless it can be supported without fabricating topology.
- This feature may add explicit delay reporting only if it fits the existing environment accounting path and does not change metric formulas.

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

- [ ] Required config fields identified
- [ ] Validation rules identified
- [ ] Backward-compatibility impact identified

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
