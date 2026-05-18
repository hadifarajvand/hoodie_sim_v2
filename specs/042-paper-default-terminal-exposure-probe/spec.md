# Feature Specification: Paper-default Terminal Exposure Probe

**Feature Branch**: `042-paper-default-terminal-exposure-probe`  
**Created**: 2026-05-18  
**Status**: Draft  
**Input**: User description: "Diagnose why the simulator does not yet produce reward-bearing terminal outcomes under the current training-readiness campaign. Feature 041 correctly blocked full training because the readiness probe produced terminal_transition_count = 0 and reward_bearing_transition_count = 0. Feature 042 must run a paper-default terminal exposure probe using T=110 slots, not the short T=20 readiness probe. The goal is to prove whether completion/drop terminal events appear under the repaired runtime contracts when the paper-default episode horizon is used."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Probe Operator (Priority: P1)

As a campaign operator, I want to run a paper-default terminal exposure probe so that I can see whether completion or drop outcomes appear when the full paper horizon is used.

**Why this priority**: The feature exists to answer a blocking diagnostic question before any further training work proceeds.

**Independent Test**: Run the probe at T=110 and verify that it records terminal exposure evidence, or clearly reports that none was observed, without changing runtime behavior.

**Acceptance Scenarios**:

1. **Given** the repaired runtime contracts and paper-default configuration, **When** the terminal exposure probe runs with T=110, **Then** it reports terminal and reward-bearing exposure counters for the full episode horizon.
2. **Given** a run where no terminal outcomes appear, **When** the report is generated, **Then** it clearly states that terminal exposure remains absent under the paper-default probe.

---

### User Story 2 - Strategy Analyst (Priority: P2)

As a researcher, I want to compare deterministic probe strategies so that I can determine whether terminal exposure depends on how legal actions are selected.

**Why this priority**: The diagnosis is more useful if it can separate environment behavior from action-selection behavior without redesigning policy or training.

**Independent Test**: Execute the configured probe strategies and compare their terminal exposure counters, action legality, and lifecycle traces.

**Acceptance Scenarios**:

1. **Given** multiple deterministic probe strategies, **When** the probe runs each strategy, **Then** the report separates local, horizontal, and vertical/cloud action behavior.
2. **Given** a strategy that cannot select a legal action, **When** the probe runs, **Then** the report records the mask failure without inventing terminal outcomes.

---

### User Story 3 - Diagnostic Reporter (Priority: P3)

As a stakeholder, I want a clear diagnostic report so that I can decide the next feature based on evidence rather than assumptions.

**Why this priority**: The feature is only useful if the result is traceable, reproducible, and honest about whether terminal exposure exists.

**Independent Test**: Generate the report artifacts and verify that they contain the paper-default runtime, the per-strategy counters, and an explicit next-step recommendation.

**Acceptance Scenarios**:

1. **Given** a completed probe run, **When** the report is written, **Then** it records the paper-default runtime, probe strategy results, aggregate terminal exposure summary, and final verdict.
2. **Given** no terminal exposure is observed, **When** the report is written, **Then** it recommends the next diagnostic feature without claiming reproduction or changing simulator semantics.

### Edge Cases

- What happens when a strategy cannot select a legal action for a given state?
- What happens when the probe reaches T=110 and still observes no terminal outcomes?
- What happens when a reward is missing or omitted for a transition that should not be terminal?
- What happens when pending-at-horizon transitions appear near the end of the episode?
- What happens when the environment emits terminal outcomes for one action type but not others?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST support a paper-default terminal exposure probe that runs with the repaired paper-default runtime horizon of `T = 110` slots.
- **FR-002**: The system MUST support deterministic probe strategies that can separately exercise default policy behavior, forced-local legal action selection, forced-horizontal legal action selection, forced-vertical/cloud legal action selection, and optional mixed legal action selection.
- **FR-003**: The system MUST report, for each probe strategy and seed, the counters and ratios needed to diagnose terminal exposure, reward-bearing exposure, action legality, and lifecycle integrity.
- **FR-004**: The system MUST preserve delayed reward timing so that rewards are emitted only on completion or drop events and pending-at-horizon transitions remain non-terminal.
- **FR-005**: The system MUST not change runtime semantics, reward timing, topology legality, policy behavior, or action legality rules in order to force terminal outcomes.
- **FR-006**: The system MUST not train, update a target network, sample replay for learning, or otherwise convert the probe into a training workflow.
- **FR-007**: The system MUST generate JSON and Markdown report artifacts that summarize the probe configuration, per-strategy results, aggregate terminal exposure, the recommended next feature, and the audit flags proving the probe did not train, mutate runtime behavior, or claim reproduction.
- **FR-008**: The system MUST clearly distinguish local, horizontal, and vertical/cloud action behavior in the probe results.
- **FR-009**: The system MUST record whether the paper-default probe observed any terminal outcomes, any reward-bearing terminal outcomes, and any pending-at-horizon transitions.
- **FR-010**: The system MUST reject fake terminal outcomes, fake reward injection, and curve-fitted or simulator-tuned diagnostics.
- **FR-011**: The system MUST preserve the approved paper-default runtime assumptions for `N = 20`, `T = 110`, `P = 0.5`, `Δ = 0.1 sec`, timeout `= 20 slots / 2 sec`, `CPU private = 0.5 gcycles/slot`, `CPU public = 0.5 gcycles/slot`, `CPU cloud = 3.0 gcycles/slot`, `R_H = 30 Mbps`, `R_V = 10 Mbps`, the Figure 7 approved topology, neighbor-only horizontal legality, and vertical/cloud independence from Figure 7 adjacency.
- **FR-012**: The system MUST support a lifecycle-integrity check that verifies the probe trace is internally consistent and does not fabricate terminal or reward-bearing transitions.
- **FR-013**: The terminal exposure report schema MUST require the following audit flags and each flag MUST be true: `no_training_started`, `no_optimizer_step`, `no_replay_training`, `no_target_update_execution`, `no_dependency_drift`, `no_environment_contract_drift`, `no_policy_drift`, `no_reward_timing_change`, `no_curve_fitting`, `no_simulator_output_tuning`, and `no_paper_reproduction_claim`.
- **FR-014**: The terminal exposure report schema MUST require `final_verdict`, `diagnosis`, and `recommended_next_feature`, and MUST fail validation if any required audit flag is missing or false.

### Key Entities

- **ProbeConfiguration**: The paper-default runtime, episode horizon, and deterministic strategy settings used to run the exposure probe.
- **ProbeStrategyResult**: The per-strategy outcome summary, including legality, terminal exposure, reward exposure, and lifecycle integrity.
- **TerminalExposureSummary**: The aggregate probe result indicating whether terminal and reward-bearing outcomes were observed under the paper-default horizon.
- **ProbeReport**: The diagnostic output containing the probe configuration, strategy results, aggregate summary, and recommended next feature.
- **ProbeAuditFlags**: The boolean audit fields proving the probe remained diagnostic-only and did not claim reproduction.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A paper-default probe run completes at `T = 110` and records terminal exposure counters for each configured strategy.
- **SC-002**: The report can distinguish local, horizontal, and vertical/cloud action behavior and shows whether each strategy selected legal actions.
- **SC-003**: The report explicitly states whether terminal transitions and reward-bearing terminal transitions were present, with zero ambiguity about the outcome.
- **SC-004**: The report artifacts are reproducible from the same deterministic seeds and do not claim paper reproduction or simulator tuning.
- **SC-005**: The probe preserves delayed reward timing and pending-at-horizon behavior without converting non-terminal transitions into terminal samples.
- **SC-006**: The report schema fails validation if any required anti-training, no-drift, or no-reproduction audit flag is missing or false.

## Assumptions

Any assumption that materially changes code, workflow, or repository state MUST be recorded and presented for user approval before implementation depends on it.

- The paper-default probe is diagnostic only and does not authorize training.
- The probe uses the repaired runtime contracts already established by prior features.
- Deterministic strategies are for diagnosis, not policy redesign.
- If no terminal exposure is observed, the correct outcome is an honest diagnostic report, not a runtime change.
- The approved paper-default runtime assumptions remain fixed and are not subject to tuning in this feature.

## Production Constraints

- [x] Performance budgets identified
- [x] Artifact handling rules identified
- [x] Security and secret-hygiene constraints identified
- [x] CI quality gate impact identified

## Public Interfaces Affected

- [x] Environment reset/step
- [x] Policy interface
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

- [x] Raw metrics
- [x] Plots
- [x] Reports
- [x] Checkpoints
- [x] Debug traces
- [x] Validation summaries

## Security Considerations

- [x] Secrets / tokens / credentials reviewed
- [x] Remote code execution reviewed
- [x] External references documented

## Definition of Done

- [x] Spec matched by plan
- [x] Tests identified
- [x] Assumptions documented
- [x] Configs validated or updated
- [x] Paper-to-code mapping updated
- [x] Artifacts handled per lifecycle rules
- [x] Review and merge gate satisfied
