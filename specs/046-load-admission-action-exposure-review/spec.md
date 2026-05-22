# Feature Specification: Load, Admission, and Action-Exposure Review

**Feature Branch**: `046-load-admission-action-exposure-review`  
**Created**: 2026-05-22  
**Status**: Draft  
**Input**: User description: "Quantify whether the paper-default completion weakness diagnosed by Feature 045 is caused by load pressure, admission serialization, action exposure, queue distribution, or probe/policy action selection."

## Clarifications

### Session 2026-05-22

- Q: Should Feature 046 change runtime behavior to reduce drops? → A: No. Diagnosis only.
- Q: Should Feature 046 consume Feature 044/045 trace/report artifacts rather than adding new instrumentation? → A: Yes. It may run existing passive trace analysis if needed, but must not modify runtime or instrumentation.
- Q: Should the review use T=110? → A: Yes.
- Q: Should it use the same seeds/strategies as Features 042–045? → A: Yes. Seeds [0, 1, 2] and the five approved probe strategies.
- Q: Should legal-but-unselected action counts be tracked? → A: Yes. Without this, action exposure bias cannot be quantified.
- Q: Should same-slot generated tasks and serialized admission lag be measured? → A: Yes. Same-slot serialization is a project constraint and may explain backlog/drop behavior.
- Q: Should this feature recommend runtime repair? → A: No, unless it uncovers a verified runtime-fault contradiction backed by trace evidence. Current Feature 045 says runtime repair is not supported.
- Q: Should pointer-sensitive older report tests be run? → A: No. Validate older features through committed artifacts and safe tests only.
- Q: Should AGENTS.md be ignored? → A: No. It must be restored/stashed if dirty. It must not be committed or added to .gitignore.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Explain whether weak completion is load-driven (Priority: P1)

As an analyst, I want a passive breakdown of generated, admitted, terminal, and pending work so I can tell whether paper-default completion weakness is primarily caused by too much work for the runtime horizon.

**Why this priority**: Feature 045 already ruled out runtime repair as the default next step. The most important remaining question is whether the observed weakness is simply the expected result of load under the paper-default setup.

**Independent Test**: Run the review on paper-default traces and confirm the report quantifies load pressure using generated, admitted, completed, dropped, and pending-at-horizon counts and rates.

**Acceptance Scenarios**:

1. **Given** paper-default passive traces, **When** the review is generated, **Then** the report quantifies load pressure with counts and rates for generated, admitted, terminal, completed, dropped, and pending work.
2. **Given** the same traces, **When** the report is generated, **Then** the report states whether the completion weakness is best explained by load pressure, admission serialization, action exposure, queue pressure, offload-path pressure, or a mixed cause.

---

### User Story 2 - Separate admission serialization from action exposure (Priority: P2)

As a reviewer, I want to distinguish same-slot admission backlog from action-selection bias so I can tell whether the issue is too much work entering the system or the system repeatedly exposing the same action patterns.

**Why this priority**: A load-heavy report is not enough on its own. The next most useful distinction is whether the bottleneck is caused by serialized admissions or by action exposure that repeatedly favors one path over others.

**Independent Test**: Confirm the report distinguishes same-slot generation/admission backlog, legal-but-unselected actions, and per-action completion/drop/pending rates.

**Acceptance Scenarios**:

1. **Given** traces with multiple tasks created in the same slot, **When** the review is generated, **Then** the report quantifies admission serialization backlog and the lag it introduces.
2. **Given** traces with legal local, horizontal, and vertical actions, **When** the review is generated, **Then** the report identifies whether one action type is overexposed while other legal actions are underselected.

---

### User Story 3 - Explain queue and offload pressure (Priority: P3)

As an analyst, I want to break down private, public, cloud, and offload-path pressure so I can understand whether transmission, queueing, or execution budget consumption is the dominant source of weakness.

**Why this priority**: Even when overall load is the main issue, the follow-up decision depends on whether the pressure is concentrated in private queues, offloaded queues, or transmission and execution delays.

**Independent Test**: Confirm the report separates queue pressure from offload-path pressure and compares representative task budgets against observed waiting, transmission, execution, and deadline behavior.

**Acceptance Scenarios**:

1. **Given** traces with offloaded tasks, **When** the review is generated, **Then** the report compares transmission delay, admission lag, and execution-start lag for those tasks.
2. **Given** traces with private, public, and cloud queues, **When** the review is generated, **Then** the report identifies which queue family contributes most to the completion weakness.

### Edge Cases

- What if completions exist but they are too sparse to explain the overall drop rate?
- What if same-slot generated tasks are admitted one at a time in a deterministic order?
- What if legal actions exist but one action family is selected far more often than others?
- What if offloaded tasks are delayed mainly by transmission rather than queueing?
- What if different strategies show different dominant pressure sources under the same paper-default runtime?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST consume Feature 044 passive lifecycle traces and the Feature 045 completion root-cause report as the primary diagnostic inputs.
- **FR-002**: The system MUST preserve the approved paper-default runtime configuration, including `N = 20`, `T = 110`, `P = 0.5`, `slot_duration_seconds = 0.1`, `timeout_slots = 20`, task size bounds `[2.0, 5.0]`, processing density `0.297`, private/public/cloud CPU `0.5/0.5/3.0`, horizontal rate `30 Mbps`, vertical rate `10 Mbps`, and the approved Figure 7 topology constraints.
- **FR-003**: The system MUST quantify load pressure using generated-task, admitted-task, terminal-task, completed-task, dropped-task, and pending-at-horizon counts and rates.
- **FR-004**: The system MUST quantify admission serialization using same-slot generation counts, same-slot admission counts, backlog counts, serialization lag, and tasks delayed or expired because of admission delay.
- **FR-005**: The system MUST quantify action exposure using legal-action counts, selected-action counts, exposure ratios, selection ratios, action entropy, and per-action completion/drop/pending rates.
- **FR-006**: The system MUST quantify queue pressure using private, public, and cloud queue counts, queue terminal outcomes, and queue wait-time summaries.
- **FR-007**: The system MUST quantify offload-path pressure using transmission start/completion counts, transmission-delay summaries, transmission-to-admission lag, execution-start lag, and offloaded task outcomes.
- **FR-008**: The system MUST compare representative task budgets against observed queue wait, transmission delay, execution progress, task age at terminal outcome, deadline margin at completion, and deadline overrun at drop.
- **FR-009**: The system MUST produce a ranked diagnosis that can distinguish load pressure, admission serialization, action exposure, queue pressure, offload-path pressure, or mixed causes.
- **FR-010**: The system MUST recommend the next feature type honestly based on the dominant pressure source and MUST not recommend runtime repair.
- **FR-011**: The system MUST not change runtime behavior, policy behavior, reward timing, deadline logic, transmission logic, queue semantics, or topology legality.
- **FR-012**: The system MUST not run training, optimizer steps, replay training, or target updates.
- **FR-013**: The system MUST not tune simulator outputs, fit curves to force a conclusion, or claim paper reproduction.
- **FR-014**: The system MUST keep trace evidence passive and MUST not invent new trace events or add new instrumentation.
- **FR-015**: The system MUST analyze paper-default traces across the approved strategy grid and seeds `[0, 1, 2]`.
- **FR-016**: The system MUST emit both JSON and Markdown report artifacts for review and downstream planning.
- **FR-017**: The system MUST explicitly state when evidence is insufficient to separate load, admission, action exposure, queue pressure, and offload-path pressure.
- **FR-018**: The system MUST treat pending-at-horizon work as non-terminal and distinguish it from completed and dropped work.
- **FR-019**: The system MUST preserve the distinction between local, horizontal, and vertical action families when quantifying action exposure.
- **FR-020**: The system MUST identify whether the observed completion/drop ratio is an expected effect of load and serialization or a sign that action exposure is underexplored.
- **FR-021**: The system MUST not recommend runtime repair for evidence that is only load pressure, admission serialization, action exposure bias, queue pressure, offload path pressure, or mixed load/action pressure.
- **FR-022**: The system MUST only mention runtime repair when a verified runtime-fault contradiction is discovered and supported by trace-derived evidence.
- **FR-023**: The system MUST use canonical next-feature terminology: `Feature 047 — Paper HOODIE Observation Vector`, `Feature 048 — Delayed-Reward DDQN Loss Contract`, `Feature 049 — Exploration Schedule Contract`, and `exposure-matrix review`.

### Key Entities *(include if feature involves data)*

- **Load Pressure Summary**: Aggregated counts and rates describing the overall amount of work created, admitted, completed, dropped, and left pending within the paper-default horizon.
- **Admission Serialization Summary**: Measurements that show whether same-slot arrivals are handled sequentially in a way that creates backlog.
- **Action Exposure Summary**: A breakdown of how often each legal action family is exposed and selected, and how those selections correlate with terminal outcomes.
- **Queue Pressure Summary**: A breakdown of pressure across private, public, and cloud queues.
- **Offload-Path Pressure Summary**: Measurements describing transmission, admission, and execution delays for offloaded work.
- **Budget Comparison Summary**: Representative task comparisons between expected budget and observed waiting, progress, and terminal behavior.
- **Diagnosis Report**: The final passive analysis artifact that names the dominant pressure source and the recommended next feature type.
- **Runtime-Fault Contradiction**: A trace-backed contradiction against Feature 045 evidence, such as reward/counter failure despite completion, deadline/drop/reward ordering violation, formula/unit mismatch in trace-derived budget calculations, or a drop despite sufficient observed budget.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For each paper-default run analyzed, the report quantifies load, admission, action exposure, queue, and offload-path pressure using explicit counts and rates.
- **SC-002**: The report distinguishes at least four pressure categories in runs where the evidence supports that separation.
- **SC-003**: The report identifies the dominant pressure source or states that the evidence is inconclusive in 100% of sampled runs.
- **SC-004**: The report includes per-strategy and per-action summaries for all approved strategies and action families in every sampled run.
- **SC-005**: The report includes representative task-level budget comparisons for sampled runs and uses them to explain the dominant pressure source.
- **SC-006**: The report recommends the next feature type without proposing runtime repair, training, or policy redesign, unless a verified runtime-fault contradiction is discovered and explicitly named.
- **SC-007**: The feature introduces no runtime changes, no training, no optimizer activity, no replay training, no target updates, and no paper reproduction claim.
- **SC-008**: The report remains readable as both JSON and Markdown and is produced for every sampled paper-default run.

## Assumptions

- Feature 044 passive traces and the Feature 045 report are sufficiently rich to support this review without new instrumentation.
- Paper-default `T = 110` remains the correct horizon for this review.
- If the evidence cannot separate action exposure from load-driven queue pressure, the report should say so rather than forcing a conclusion.
- Recommendation categories are limited to follow-up work that deepens passive diagnosis or explores action exposure and load assumptions; runtime repair is out of scope.

## Production Constraints

- [x] Performance budgets identified
- [x] Artifact handling rules identified
- [x] Security and secret-hygiene constraints identified
- [x] CI quality gate impact identified

## Public Interfaces Affected

- [x] Environment reset/step
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
- [x] Debug traces
- [x] Reports
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
