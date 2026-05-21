# Feature Specification: Completion Root-Cause Diagnosis Using Passive Lifecycle Traces

**Feature Branch**: `045-completion-root-cause-diagnosis`  
**Created**: 2026-05-20  
**Status**: Draft  
**Input**: User description: "Use Feature 044 passive lifecycle traces to diagnose why task completions are weak or absent under paper-default runtime."

## Clarifications

### Session 2026-05-20

- Q: Should this feature repair runtime behavior if a bug is found? → A: No. It is diagnostic only and must not alter runtime semantics.
- Q: Should this feature run training or optimize policies? → A: No. It must not run training, optimizer updates, replay training, or target updates.
- Q: Should this feature claim paper reproduction? → A: No. It must not claim paper reproduction; it only explains completion root causes using passive traces.
- Q: Should Feature 045 consume Feature 044 passive traces only? → A: Yes. It may rerun the Feature 044 trace runner if needed, but must not add new instrumentation or change runtime semantics.
- Q: Should diagnosis use T=110 paper-default runs? → A: Yes.
- Q: Which seeds should be used? → A: Use seeds [0, 1, 2] for consistency with Features 042–044.
- Q: Which strategies should be analyzed? → A: Use `environment_default_policy_probe`, `force_local_legal_probe`, `force_horizontal_legal_probe`, `force_vertical_legal_probe`, and `mixed_legal_round_robin_probe`.
- Q: Should the diagnosis allow multiple root causes? → A: Yes. Rank dominant root causes by evidence strength.
- Q: Should each root-cause class include confidence? → A: Yes. Use low, medium, and high.
- Q: If runtime behavior is proven wrong, what comes next? → A: Feature 046 - Runtime Repair for Completion Lifecycle. If runtime is valid but load/action exposure is the issue, proceed to observation vector, exploration, or loss sequence.
- Q: Should pointer-sensitive older report tests be included? → A: No. Validate older features through committed artifacts and safe tests only.

## Additional Specification Constraints

- The feature MUST consume passive lifecycle traces produced by Feature 044 and MUST NOT change simulator behavior.
- The feature MUST diagnose completion root causes using evidence from paper-default `T = 110` runs.
- The feature MUST preserve the distinction between runtime observation, load/configuration effects, policy/action exposure effects, formula mismatches, and inconclusive evidence.
- The feature MUST not attempt runtime repair, training, policy optimization, or reproduction claims.
- The feature MUST surface the most likely root cause class for each diagnostic run and identify the next feature type needed if diagnosis remains unresolved.
- The feature MUST use the approved paper-default runtime configuration for diagnosis and MUST treat trace depth limitations as an evidence issue rather than an excuse to infer missing facts.
- The feature MUST consume Feature 044 passive traces only and MAY rerun the Feature 044 trace runner if needed, but MUST NOT add new instrumentation or change runtime semantics.
- The feature MUST diagnose paper-default `T = 110` runs using seeds `[0, 1, 2]` and the approved Feature 044 strategy set.
- The diagnosis MAY report multiple root causes, but it MUST rank them by evidence strength and confidence.
- Each root-cause class MUST carry a confidence value of low, medium, or high.
- Runtime repair MUST only be recommended when a runtime-fault predicate is explicitly true and supported by evidence, such as completion/counter-path mismatch, deadline/drop ordering failure, formula unit mismatch, proven capacity or accounting inconsistency, or a proven drop despite sufficient remaining budget under the current queues, transmission, and deadline constraints.
- The feature MUST NOT classify a run as runtime-repair-required merely because many tasks drop if completions exist and formula, reward, and deadline ordering remain consistent.
- If completions exist and formula, reward, and deadline ordering remain consistent, the report MUST classify the issue as configuration/load or policy/action-exposure unless a runtime-fault predicate is explicitly true.
- If execution progresses but deadline expiry arrives first while formula, reward, and ordering remain valid, the report MUST classify that evidence as deadline/load pressure unless additional evidence proves a runtime fault.
- If runtime behavior is proven wrong, the next feature MUST be Feature 046 - Runtime Repair for Completion Lifecycle.
- If runtime behavior is valid but load or action exposure is the issue, the report MUST route toward observation vector, exploration, or loss-sequence work rather than runtime repair.
- Pointer-sensitive older report tests MUST remain out of scope; older features must be validated through committed artifacts and safe tests only.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Diagnose the completion bottleneck root cause (Priority: P1)

As an analyst, I want a passive, evidence-backed diagnosis of why completions are weak or absent so I can decide whether the next feature should be a runtime repair, a policy/exposure change, a formula audit, or a deeper trace pass.

**Why this priority**: Feature 043 could not isolate the completion breakpoint, and Feature 044 only made passive evidence available. This feature exists to turn that evidence into a root-cause class.

**Independent Test**: Run the diagnosis on paper-default `T = 110` traces and confirm the report classifies the dominant root cause or states clearly when evidence is still insufficient.

**Acceptance Scenarios**:

1. **Given** passive lifecycle traces from a paper-default run, **When** the diagnosis is generated, **Then** each unfinished task is classified into an evidence-backed lifecycle path or marked inconclusive.
2. **Given** the same traces, **When** the diagnosis is generated, **Then** the report identifies whether the likely next feature is runtime repair, observation-vector adjustment, loss-contract audit, exploration-schedule change, or load/configuration audit.

---

### User Story 2 - Explain whether completions are blocked by the system or by the load pattern (Priority: P2)

As a reviewer, I want the diagnosis to separate queue pressure, admission overload, action exposure bias, transmission delay mismatch, and deadline ordering issues so I can distinguish configuration/load explanations from true runtime bugs.

**Why this priority**: Without separating load-driven causes from ordering or formula issues, the diagnosis would still be too vague to guide follow-up work.

**Independent Test**: Confirm the report distinguishes the major root-cause classes and supports the classification with task-level evidence.

**Acceptance Scenarios**:

1. **Given** traces with long queue waits or repeated admission delays, **When** the diagnosis is generated, **Then** the report can attribute the bottleneck to queue pressure or admission overload rather than hallucinating a completion bug.
2. **Given** traces with completion-progress but deadline expiry arriving first, **When** the diagnosis is generated, **Then** the report classifies the issue as a deadline/execution ordering problem instead of a reward or counter problem.

### Edge Cases

- What if the trace evidence is too shallow to distinguish completion from drop ordering?
- What if a task is admitted but never makes measurable execution progress?
- What if completions occur in some runs but not others under the same paper-default configuration?
- What if the trace shows completion evidence but the reward or counter path looks wrong?
- What if the report cannot separate action exposure bias from load-driven queue pressure?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST consume passive lifecycle trace reports and trace events from Feature 044 as its primary diagnostic input.
- **FR-002**: The system MUST reconstruct each task’s lifecycle from generated, admitted, transmission, execution, deadline, terminal outcome, and reward evidence.
- **FR-003**: The system MUST classify each task trace into one of the approved root-cause classes or explicitly mark the evidence as inconclusive.
- **FR-004**: The system MUST distinguish queue pressure from task-generation/admission overload, action exposure bias, local/private queue blockage, public/cloud queue blockage, transmission-delay/admission mismatch, execution-progress-before-deadline loss, completion/counter-path mismatch, deadline/drop ordering issues, formula unit mismatch, no completion problem, and inconclusive evidence.
- **FR-005**: The system MUST report task-level evidence for generated slot, admitted slot, selected action, destination, queue type, transmission timing, execution timing, deadline timing, terminal outcome, remaining work over time, task age over time, and reward timing.
- **FR-006**: The system MUST aggregate evidence into per-root-cause summaries with explicit confidence and next-action guidance.
- **FR-007**: The system MUST produce report artifacts that are readable as both JSON and Markdown.
- **FR-008**: The system MUST record the paper-default runtime configuration used for diagnosis.
- **FR-009**: The system MUST indicate whether the next feature should focus on runtime repair, observation vectors, loss contracts, exploration scheduling, or load/configuration audit.
- **FR-010**: The system MUST not modify simulator behavior, rewards, timing, topology legality, or policy behavior.
- **FR-011**: The system MUST not run training, optimizer steps, replay training, or target updates.
- **FR-012**: The system MUST not claim paper reproduction.
- **FR-013**: The system MUST keep trace depth limitations explicit and MUST not infer unsupported causes when evidence is insufficient.
- **FR-014**: The system MUST use Feature 044 passive traces only and MUST NOT add new instrumentation or change runtime semantics.
- **FR-015**: The system MUST analyze paper-default `T = 110` runs using seeds `[0, 1, 2]` and the approved Feature 044 strategy set.
- **FR-016**: The system MUST support multiple root-cause classes per diagnosis, ranked by evidence strength.
- **FR-017**: The system MUST assign each root-cause class a confidence value of low, medium, or high.
- **FR-018**: The system MUST route runtime-proven failures to Feature 046 - Runtime Repair for Completion Lifecycle.
- **FR-019**: The system MUST route load or action-exposure explanations toward observation-vector, exploration, or loss-sequence follow-up rather than runtime repair.
- **FR-020**: The system MUST keep older pointer-sensitive report tests out of scope and rely on committed artifacts and safe tests for prior feature validation.
- **FR-021**: The system MUST only recommend runtime repair when a runtime-fault classifier is detected, including completion/counter-path mismatch, deadline/drop ordering failure, formula unit mismatch, proven capacity or accounting inconsistency, or proven drop despite sufficient remaining budget under current queues, transmission, and deadline constraints.
- **FR-022**: The system MUST classify evidence as configuration/load or policy/action-exposure when completions exist and formula, reward, and deadline ordering remain consistent, unless a runtime-fault classifier is explicitly detected.
- **FR-023**: The system MUST treat execution-progress-before-deadline-loss as deadline/load pressure unless additional evidence proves a runtime fault.

### Key Entities *(include if feature involves data)*

- **Task Lifecycle Reconstruction**: Per-task evidence that captures how a task moved from generation through terminal outcome.
- **Root Cause Evaluation**: A structured assessment for one candidate explanation of weak or absent completions.
- **Diagnosis Report**: A passive analysis artifact that explains the dominant root cause and the recommended next feature type.
- **Runtime Repair Verdict**: A diagnosis outcome that is permitted only when the evidence proves a runtime fault class, not merely because completion is weak or drops are frequent.
- **Paper-Default Diagnosis Run**: A diagnostic pass over paper-default `T = 110` traces using the approved runtime configuration.
- **Feature Routing Outcome**: The follow-up feature type recommended by the diagnosis, such as runtime repair, observation vector, exploration, loss sequence, or load/configuration audit.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For each sampled paper-default run, the report classifies every unfinished task into a lifecycle root-cause class or marks it inconclusive with an explicit reason.
- **SC-002**: The report identifies a dominant root-cause class in 100% of sampled runs where enough evidence exists to support a dominant explanation.
- **SC-003**: The report distinguishes at least 10 approved root-cause classes and reserves an explicit inconclusive class for insufficient evidence.
- **SC-004**: The report outputs task-level lifecycle reconstruction evidence for generated, admitted, transmission, execution, deadline, terminal outcome, and reward stages in every sampled run.
- **SC-005**: The report clearly recommends the next feature type in every sampled run, choosing from runtime repair, observation vector, loss contract, exploration schedule, or load/configuration audit, and only recommends runtime repair when a runtime-fault classifier is explicitly detected.
- **SC-006**: The feature introduces no runtime repair, no training, and no paper reproduction claim.
- **SC-007**: The diagnosis uses seeds `[0, 1, 2]` and the approved Feature 044 strategy set in every sampled paper-default run.
- **SC-008**: Each sampled run includes a ranked set of dominant root causes with confidence values and a follow-up feature recommendation.

## Assumptions

- Feature 044 passive lifecycle traces are sufficiently rich to support root-cause diagnosis without additional runtime changes.
- Paper-default `T = 110` remains the primary diagnosis horizon.
- If evidence cannot discriminate between two plausible causes, the report should say so rather than guess.

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
