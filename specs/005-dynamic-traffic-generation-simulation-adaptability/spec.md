# Feature Specification: 005-dynamic-traffic-generation-simulation-adaptability

**Feature Branch**: `005-dynamic-traffic-generation-simulation-adaptability`  
**Created**: 2026-05-01  
**Status**: Draft  
**Input**: User description: "Dynamic Traffic Generation & Simulation Adaptability"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Paper-Backed Traffic Scenarios (Priority: P1)

As a researcher, I want to select paper-backed traffic presets so that I can reproduce the paper’s
default workload and traffic-intensity sweeps without guessing parameters.

**Why this priority**: Traffic presets define the workload regime and are required before any
traffic evaluation can be trusted.

**Independent Test**: Select each preset and verify that the configured arrival probability, agent
count, episode length, slot duration, timeout, and task-size range match the documented preset.

**Acceptance Scenarios**:

1. **Given** the paper default preset, **When** the preset is loaded, **Then** the configuration
   reflects 20 agents, 110 time slots, arrival probability 0.5, slot duration 0.1 seconds, timeout
   20 slots, task sizes from 2.0 to 5.0 Mbits in 0.1 increments, and processing density 0.297.
2. **Given** the moderate, heavy, or extreme preset, **When** the preset is loaded, **Then** the
   scenario uses the documented probability and task-size range for that traffic intensity.

### User Story 2 - Deterministic Bernoulli Traffic Traces (Priority: P1)

As an evaluator, I want seeded Bernoulli traffic generation so that the same traffic configuration
and seed always produce the same per-agent, per-slot arrival trace.

**Why this priority**: Determinism is required for reproducible evaluation and fair comparison.

**Independent Test**: Generate a trace twice with the same configuration and seed and confirm that
the arrival records, task blueprints, and traffic summary are identical.

**Acceptance Scenarios**:

1. **Given** the same traffic configuration and seed, **When** traffic is generated, **Then** the
   resulting trace is identical across runs.
2. **Given** a different seed with the same traffic configuration, **When** traffic is generated,
   **Then** the trace may differ in arrival pattern while preserving the same configuration
   metadata.

### User Story 3 - Environment-Compatible Traffic Observability (Priority: P2)

As a simulation user, I want generated traffic to feed the existing environment boundary and expose
traffic-load summaries so that future adaptability features can observe workload intensity without
changing the lifecycle contract.

**Why this priority**: The traffic substrate is only useful if it can be consumed by the current
environment and inspected through summary metrics.

**Independent Test**: Load the generated trace through the existing environment boundary, step
through the episode, and verify same-slot multi-agent arrivals, terminal-only rewards, and traffic
summary metrics.

**Acceptance Scenarios**:

1. **Given** a generated traffic trace, **When** it is passed into the existing environment
   boundary, **Then** the environment can consume it without bypassing `reset(seed)` / `step(action)`.
2. **Given** a traffic trace with multiple arrivals in the same slot, **When** it is consumed, Then
   the arrivals are serialized deterministically using the existing environment ordering.

### Edge Cases

- What happens when a time slot has no arrivals for any agent?
- How are multiple arrivals in the same slot ordered for deterministic replay?
- What happens when the selected preset covers the full paper range but a trace ends early because
  the configured episode length is shorter than the maximum traffic window?
- How are full-trace and rolling-window traffic summaries reported when the window is larger than
  the available trace history?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The feature MUST provide a traffic configuration model with scenario name, number of
  agents, episode length, arrival probability, slot duration in seconds, timeout slots, task-size
  minimum, task-size maximum, task-size step, and processing density.
- **FR-002**: The feature MUST provide paper-backed scenario presets for paper_default, moderate,
  heavy, and extreme traffic, using the documentated probability and task-size ranges.
- **FR-003**: The feature MUST generate deterministic Bernoulli traffic traces from a seed by
  evaluating each agent at each time slot independently and creating exactly one task when the
  sampled arrival condition is met.
- **FR-004**: Generated traffic records MUST include task identifier, source agent identifier,
  arrival slot, task size, processing density, timeout length, and absolute deadline slot.
- **FR-005**: Same-slot arrivals across different agents MUST be serialized deterministically using
  the existing environment ordering so that replay is stable.
- **FR-006**: Generated traffic traces MUST be consumable by the existing environment boundary
  without changing the lifecycle contract of `reset(seed)` and `step(action)`.
- **FR-007**: The feature MUST provide traffic summary outputs for configured arrival probability,
  observed arrival probability, total arrivals, arrivals per slot, arrivals per agent, scenario
  name, and seed.
- **FR-008**: The feature MUST support both full-trace and rolling-window traffic observability so
  future adaptability features can inspect workload intensity without adding traffic-model
  switching.
- **FR-009**: The feature MUST update paper-to-code mapping and assumptions documentation for the
  dynamic traffic generator and its environment compatibility.
- **FR-010**: The feature MUST NOT introduce undocumented traffic distributions or simulator
  dependencies beyond the existing approved repository stack.

### Key Entities

- **Traffic Configuration**: The chosen scenario settings that define agent count, time horizon,
  arrival probability, slot duration, timeout, task-size range, and processing density.
- **Traffic Scenario Preset**: A named configuration profile such as paper_default, moderate,
  heavy, or extreme.
- **Traffic Trace**: The seeded per-agent, per-slot arrival record used to build a reproducible
  workload.
- **Traffic Summary**: The observed workload statistics derived from a trace, including arrival
  probability, arrivals per slot, arrivals per agent, scenario name, and seed.
- **Traffic Task Record**: A single generated task arrival entry with the fields needed for the
  existing environment boundary to consume it.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Two traffic generations created from the same configuration and seed produce identical
  traces and identical summary metrics in 100% of repeated runs.
- **SC-002**: The paper default preset reproduces the documented parameters exactly: 20 agents, 110
  slots, arrival probability 0.5, slot duration 0.1 seconds, timeout 20 slots, task size from 2.0
  to 5.0 Mbits in 0.1 increments, and processing density 0.297.
- **SC-003**: The moderate, heavy, and extreme presets reproduce the documented traffic-intensity
  values with no undocumented distribution changes.
- **SC-004**: Generated traffic can be consumed by the existing environment boundary in a complete
  episode run without any lifecycle contract changes in all tested cases.
- **SC-005**: Traffic summaries report configured and observed arrival probabilities, total
  arrivals, arrivals per slot, arrivals per agent, scenario name, and seed for every generated
  trace.

## Assumptions

- The paper-backed task-size lists use 0.1 Mbit increments wherever a range is specified, matching
  the recovered default sequence `[2, 2.1, ..., 5]`.
- Deterministic same-slot ordering follows the existing environment’s agent ordering rules rather
  than introducing a second ordering policy.
- Full-trace traffic summaries are the default observability output; rolling-window summaries are an
  additional inspection view over the same generated trace.
- No new assumption beyond the paper-backed Bernoulli arrival model and the documented scenario
  presets is introduced by this feature.
