# Feature Specification: Full Training/Reproduction Campaign

**Feature Branch**: `041-full-training-reproduction-campaign`  
**Created**: 2026-05-18  
**Status**: Draft  
**Input**: User description: "Define and implement the first full HOODIE training/reproduction campaign only after all prior gates are verified: Feature 037 baseline revalidation complete, Feature 038 training foundation contract complete, Feature 039 paper HOODIE network implementation complete, Feature 040 smoke training complete."

## Clarifications

### Session 2026-05-18

- Q: Which target-update unit is approved for Feature 041? → A: `optimizer_step` (user-approved campaign assumption; not a paper-defined fact)
- Q: What minimum reward-bearing transition ratio is required before full training can proceed? → A: No fixed threshold; report readiness probe evidence and require manual approval.
- Q: Which campaign stages are in scope for Feature 041? → A: `readiness_probe + pilot_training + full_training_candidate`
- Q: What is the first executable pilot budget? → A: `10 episodes`, with `25 episodes` as the next pilot step if the first passes cleanly.
- Q: How should the full campaign budget behave? → A: `5000 episodes` is configurable but only executable behind an explicit command/flag.
- Q: What is the replay source for training? → A: Live `HoodieGymEnvironment` rollouts only.
- Q: How should evaluation be performed? → A: Fixed disjoint evaluation trace banks.
- Q: How should baseline comparison be handled? → A: Reference-only using Feature 037 artifacts for now.
- Q: Is automatic paper reproduction claim allowed? → A: No automatic claim.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Readiness Gate Operator (Priority: P1)

As a campaign operator, I want the system to run a preflight readiness probe before any full training so that I can confirm the campaign is eligible to proceed and see exactly why it is blocked if it is not.

**Why this priority**: This is the gate that prevents wasted compute and prevents the repo from pretending it is ready when the runtime evidence is still weak.

**Independent Test**: Run the readiness probe with a known sparse-terminal scenario and verify that it either blocks with a precise reason or advances to the next stage only when the approved gate is met.

**Acceptance Scenarios**:

1. **Given** the current campaign inputs and prior feature artifacts, **When** the readiness probe runs, **Then** it reports whether terminal/reward-bearing exposure is sufficient and whether the target-update unit has been explicitly approved.
2. **Given** an unapproved target-update unit or insufficient terminal exposure, **When** the readiness probe runs, **Then** full training is blocked with a reproducible reason.

---

### User Story 2 - Pilot Campaign Runner (Priority: P2)

As a campaign operator, I want to run a bounded pilot campaign after readiness passes so that I can validate the end-to-end training stack without jumping straight to the paper default budget.

**Why this priority**: The repo needs a staged path that proves the campaign machinery works before it consumes the full paper-sized budget.

**Independent Test**: Run the pilot stage with deterministic seeds and verify that it produces finite losses, legal actions, checkpoints, and disjoint train/eval traces without updating the target network unless the approved unit says it is allowed.

**Acceptance Scenarios**:

1. **Given** readiness has passed, **When** the pilot stage runs, **Then** the system performs only the bounded pilot budget and records its trace and checkpoint artifacts.
2. **Given** a pilot stage with legal actions and delayed rewards, **When** training executes, **Then** the replay and loss paths remain consistent with the Feature 038/039/040 contracts.

---

### User Story 3 - Reproduction Candidate Campaign (Priority: P3)

As a researcher, I want a full reproduction candidate campaign so that I can compare honest outcome evidence against the paper without tuning the simulator to fake success.

**Why this priority**: The final campaign is only useful if it records what happened, not what we wish had happened.

**Independent Test**: Run the candidate/full campaign after the prerequisite gates pass and verify that the reports clearly separate evidence from claims and never declare reproduction unless the metrics support it.

**Acceptance Scenarios**:

1. **Given** the readiness and pilot gates have passed, **When** the full campaign executes, **Then** it uses the paper-aligned defaults and emits reproducible metrics, checkpoints, and evaluation traces.
2. **Given** the outcome does not match paper-like behavior, **When** the report is written, **Then** it states the mismatch honestly and does not curve-fit or inflate the result.

---

### Edge Cases

- What happens when the terminal/reward-bearing exposure ratio is below the approved readiness threshold?
- What happens when the target-update unit has not been explicitly approved?
- What happens when pending-at-horizon transitions are present in replay?
- What happens when the campaign has enough data to continue but the pilot stage has not yet been passed?
- What happens when the trained policy fails to reproduce paper-like behavior?

### Readiness Probe Evidence

The readiness probe MUST report the following counters and approval fields:

- `probe_episode_count`
- `probe_step_count`
- `generated_task_count`
- `transition_count`
- `completed_task_count`
- `dropped_task_count`
- `pending_at_horizon_count`
- `terminal_transition_count`
- `reward_bearing_transition_count`
- `non_terminal_transition_count`
- `terminal_transition_ratio`
- `reward_bearing_transition_ratio`
- `pending_at_horizon_ratio`
- `illegal_action_count`
- `illegal_action_ratio`
- `action_count_by_type`
- `local_action_count`
- `horizontal_action_count`
- `vertical_action_count`
- `readiness_manual_approval_required`
- `readiness_manual_approval_status`
- `readiness_block_reason`

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support staged campaign execution with distinct `readiness_probe`, `pilot_training`, and `full_training_candidate` stages, and MUST gate any `final_reproduction_campaign` execution behind explicit readiness approval.
- **FR-002**: System MUST block full training until the readiness probe confirms the campaign is manually approved for readiness based on terminal/reward-bearing exposure evidence, the exact readiness counters are reported, and the target-update unit is explicitly approved.
- **FR-003**: System MUST expose the target-update cadence in terms of a single explicitly approved unit and MUST NOT infer a default unit. For Feature 041, the approved unit is `optimizer_step`.
- **FR-004**: System MUST preserve the paper-default campaign dimensions and core configuration values unless the campaign stage explicitly lowers them for readiness or pilot validation.
- **FR-004a**: System MUST support a first pilot budget of `10 episodes`, a follow-on pilot budget of `25 episodes` if the first pilot passes cleanly, and a full campaign budget of `5000 episodes` that is executable only behind an explicit command or flag.
- **FR-005**: System MUST use `HoodieGymEnvironment` together with the Feature 039 network API and the Feature 038 state/action/replay/seed/checkpoint contracts.
- **FR-006**: System MUST implement a full training replay pipeline that preserves legal actions, delayed reward emission, pending-at-horizon transitions, and no fake terminal transitions.
- **FR-007**: System MUST implement DDQN-compatible loss calculation and optimizer updates for campaign execution.
- **FR-008**: System MUST support checkpoint writing that records campaign stage, seed bundle, train/eval split, target-update unit, and reproducible metadata.
- **FR-009**: System MUST generate campaign readiness and training reports that distinguish readiness evidence, pilot evidence, reproduction claims, and baseline-reference-only context using Feature 037 artifacts; it MUST NOT rerun or redesign baselines in Feature 041.
- **FR-010**: System MUST keep train and evaluation traces disjoint.
- **FR-011**: System MUST not tune simulator outputs to resemble paper curves and MUST report mismatches honestly.
- **FR-012**: System MUST keep delayed rewards tied only to completion or drop events and MUST never convert pending-at-horizon transitions into terminal reward-bearing samples.
- **FR-013**: System MUST block full training unless the readiness probe has reported terminal/reward-bearing exposure evidence and a human has manually approved the campaign for progression.
- **FR-014**: System MUST preserve the paper defaults: `N = 20`, `T = 110`, `P = 0.5`, `Δ = 0.1 sec`, timeout `= 20 slots / 2 sec`, CPU `private=0.5`, `public=0.5`, `cloud=3.0 gcycles/slot`, `R_H = 30 Mbps`, `R_V = 10 Mbps`, `W = 10`, replay memory capacity `= 10000`, batch size `= 64`, learning rate `= 7e-7`, discount factor `= 0.99`, optimizer `= Adam`, loss `= MSE/DDQN-compatible TD loss`, and `drop_penalty = 40`.
- **FR-015**: System MUST preserve neighbor-only horizontal legality and action semantics from prior features.
- **FR-016**: System MUST record whether the result is readiness blocked, pilot passed, full-training completed without a reproduction claim, or full-training completed with a candidate reproduction claim.
- **FR-017**: System MUST collect replay from live `HoodieGymEnvironment` rollouts only and MUST NOT treat smoke fixtures or synthetic batches as training evidence.
- **FR-018**: System MUST use fixed disjoint evaluation trace banks and keep evaluation traces separate from training traces.
- **FR-020**: System MUST NOT make an automatic paper reproduction claim; the report MAY only state candidate reproduction when supported by metrics.

### Key Entities

- **CampaignConfig**: Campaign-wide configuration including stage budgets, approved target-update unit, exposure gate threshold, and paper-default parameters.
- **CampaignStage**: One of readiness probe, pilot training, full training candidate, or final reproduction campaign.
- **ReplayTransition**: A single transition record with action, reward availability, pending-at-horizon state, and delayed reward metadata.
- **Checkpoint**: A reproducible save point containing model state, optimizer state, seed bundle, stage, and trace metadata.
- **ReadinessProbeResult**: Outcome of the preflight gate including exposure ratio, gate status, and block reason if any.
- **TrainingRun**: A staged execution of pilot or full campaign training with recorded metrics and evaluation traces.
- **PilotBudget**: A bounded execution budget for staged campaign validation, starting at 10 episodes and optionally extending to 25 episodes if the first pilot passes cleanly.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A readiness probe run can determine in a single report whether the campaign is blocked, pilot-ready, or full-training eligible, with an explicit reason when blocked.
- **SC-002**: A pilot run completes without target-network sync unless the approved target-update unit permits it, and the recorded trace is reproducible from the same seed bundle.
- **SC-003**: A full training candidate run produces finite losses, legal actions, disjoint train/eval traces, and reproducible checkpoint metadata.
- **SC-004**: The final report clearly distinguishes evidence from claims and never asserts paper reproduction unless the recorded campaign metrics support it.
- **SC-005**: The system never converts pending-at-horizon transitions into terminal reward-bearing samples, and delayed rewards remain tied only to completion or drop.
- **SC-006**: The readiness probe, pilot stage, and full-campaign stage can each be run with deterministic seeds and produce reproducible staging reports.

## Assumptions

Any assumption that materially changes code, workflow, or repository state MUST be recorded and presented for user approval before implementation depends on it.

- Campaign stages are executed in order unless a stage is already blocked by the previous gate.
- The paper-default campaign budget is not assumed to be safe until readiness and pilot gates pass.
- Reproduction claim status is a report outcome, not a promise.
- Full training can be honest even when the result is ugly.
- The approved target-update unit is `optimizer_step` and is a user-approved campaign assumption, not a paper-defined fact.
- No fixed terminal/reward-bearing exposure threshold is assumed; the readiness probe must surface evidence and require explicit manual approval.
- The first pilot budget is `10 episodes`; if it passes cleanly, the next pilot budget may extend to `25 episodes`.
- The full campaign budget of `5000 episodes` is configurable but only executable behind an explicit command or flag.
- Evaluation uses fixed disjoint trace banks.
- Baseline comparison remains reference-only using Feature 037 artifacts.
- Automatic reproduction claims are disallowed.

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
