# Feature Specification: Load, Admission, and Action-Exposure Review

**Feature Branch**: `046-load-admission-action-exposure-review`  
**Created**: 2026-05-22  
**Status**: Draft  
**Input**: User description: "Quantify whether the paper-default completion weakness diagnosed by Feature 045 is caused by load pressure, admission serialization, action exposure, queue distribution, or probe/policy action selection."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Explain weak completion with full-population evidence (Priority: P1)

As an analyst, I want the review to explain completion weakness from the complete passive evidence bank so that the conclusion is scientifically defensible.

**Why this priority**: The review is only useful if it distinguishes real system pressure from an artifact of incomplete evidence.

**Independent Test**: The review can be validated by checking that every aggregate metric and final verdict is derived from a full evidence population, not from a small representative sample, and that sample-only evidence is forced into an inconclusive diagnosis.

**Acceptance Scenarios**:

1. **Given** a complete passive evidence bank for the paper-default runs, **When** the review is generated, **Then** the report quantifies load pressure, admission serialization, action exposure, queue pressure, and offload-path pressure from that same full population.
2. **Given** only a representative trace sample, **When** the review is generated, **Then** the report classifies the diagnosis as inconclusive instead of promoting sample-based exposure findings to a final verdict.

---

### User Story 2 - Separate admission serialization from action exposure (Priority: P2)

As a reviewer, I want to know whether same-slot backlog and legal-action exposure are trace-backed so that exposure claims are not invented from missing data.

**Why this priority**: A completion problem cannot be attributed to action exposure unless the evidence shows what legal actions were actually available and what was selected.

**Independent Test**: The review can be validated by confirming that legal-action counts and legal-but-unselected counts are reported only when legal-mask or equivalent exposure data is present for the full evidence population, and otherwise the report marks exposure as insufficient data.

**Acceptance Scenarios**:

1. **Given** legal-mask or equivalent exposure data for the full evidence population, **When** the review is generated, **Then** the report quantifies legal local, horizontal, and vertical exposure against selected actions.
2. **Given** that legal-mask data is unavailable, **When** the review is generated, **Then** the report marks action exposure as insufficient for verdict-making instead of reporting fake zero counts.

---

### User Story 3 - Explain queue and offload pressure without mixing populations (Priority: P3)

As an analyst, I want queue and offload pressure to be computed from the same evidence population as load metrics so that denominators stay comparable.

**Why this priority**: Mixing a full-population load total with sample-only queue or offload rates creates a false diagnosis.

**Independent Test**: The review can be validated by confirming that queue pressure, offload-path pressure, and representative budget comparisons use the same underlying evidence population as the aggregate load metrics or are explicitly excluded from the verdict, and that lifecycle samples are never used as aggregate denominators.

**Acceptance Scenarios**:

1. **Given** a full reconstructed lifecycle dataset, **When** the review is generated, **Then** queue and offload metrics are computed from that same dataset and use matching denominators.
2. **Given** only lifecycle trace samples, **When** the review is generated, **Then** queue and offload metrics may be shown only as examples and must not drive the final verdict.

### Edge Cases

- What if completions exist but they are too sparse to support a confident pressure ranking?
- What if only a small representative lifecycle sample is available for a strategy or seed?
- What if load totals are available but legal-action exposure data is missing?
- What if queue or offload metrics can be reconstructed only for a subset of runs?
- What if the evidence is internally consistent but insufficient to separate load from action exposure?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST consume Feature 044 passive lifecycle evidence and the Feature 045 completion root-cause report as the primary diagnostic inputs.
- **FR-002**: The system MUST preserve the approved paper-default runtime configuration, including `N = 20`, `T = 110`, `P = 0.5`, `slot_duration_seconds = 0.1`, `timeout_slots = 20`, task size bounds `[2.0, 5.0]`, processing density `0.297`, private/public/cloud CPU `0.5/0.5/3.0`, horizontal rate `30 Mbps`, vertical rate `10 Mbps`, and the approved Figure 7 topology constraints.
- **FR-003**: The system MUST quantify load pressure using generated-task, admitted-task, terminal-task, completed-task, dropped-task, and pending-at-horizon counts and rates from the same evidence population used for the verdict.
- **FR-004**: The system MUST quantify admission serialization using same-slot generation counts, same-slot admission counts, backlog counts, serialization lag, and tasks delayed or expired because of admission delay.
- **FR-005**: The system MUST quantify action exposure using trace-backed legal-action counts, selected-action counts, exposure ratios, selection ratios, action entropy, and per-action completion/drop/pending rates.
- **FR-006**: The system MUST treat action exposure as insufficient for verdict-making when legal-mask or equivalent exposure data is unavailable.
- **FR-007**: The system MUST quantify queue pressure using private, public, and cloud queue counts, queue terminal outcomes, and queue wait-time summaries only when those metrics come from the same evidence population as the load metrics.
- **FR-008**: The system MUST quantify offload-path pressure using transmission start/completion counts, transmission-delay summaries, transmission-to-admission lag, execution-start lag, and offloaded task outcomes only when those metrics come from the same evidence population as the load metrics.
- **FR-009**: The system MUST compare representative task budgets against observed queue wait, transmission delay, execution progress, task age at terminal outcome, deadline margin at completion, and deadline overrun at drop, but it MUST use representative examples only for illustration unless the same full evidence population supports the aggregate metrics.
- **FR-010**: The system MUST produce a ranked diagnosis that can distinguish load pressure, admission serialization, action exposure, queue pressure, offload-path pressure, or mixed causes.
- **FR-011**: The system MUST recommend the next feature type honestly based on the dominant pressure source and MUST not recommend runtime repair.
- **FR-012**: The system MUST not change runtime behavior, policy behavior, reward timing, deadline logic, transmission logic, queue semantics, or topology legality.
- **FR-013**: The system MUST not run training, optimizer steps, replay training, or target updates.
- **FR-014**: The system MUST not tune simulator outputs, fit curves to force a conclusion, or claim paper reproduction.
- **FR-015**: The system MUST keep trace evidence passive and MUST not invent new trace events or add new instrumentation.
- **FR-016**: The system MUST analyze paper-default traces across the approved strategy grid and seeds `[0, 1, 2]`.
- **FR-017**: The system MUST emit both JSON and Markdown report artifacts for review and downstream planning.
- **FR-018**: The system MUST explicitly state when evidence is insufficient to separate load, admission, action exposure, queue pressure, and offload-path pressure.
- **FR-019**: The system MUST treat pending-at-horizon work as non-terminal and distinguish it from completed and dropped work.
- **FR-020**: The system MUST preserve the distinction between local, horizontal, and vertical action families when quantifying action exposure.
- **FR-021**: The system MUST not mix full-population load totals with sample-only action, queue, or offload metrics in a way that changes the verdict denominator, and it MUST record the evidence population for each metric group.
- **FR-022**: The system MUST only mention runtime repair when a verified runtime-fault contradiction is discovered and supported by trace-derived evidence.
- **FR-023**: The system MUST use canonical next-feature terminology: `Feature 047 — Paper HOODIE Observation Vector`, `Feature 048 — Delayed-Reward DDQN Loss Contract`, `Feature 049 — Exploration Schedule Contract`, and `exposure-matrix review`.
- **FR-024**: The system MUST classify the diagnosis as `diagnosis_inconclusive_requires_deeper_exposure_matrix` when only representative lifecycle samples are available for exposure, queue, or offload analysis.
- **FR-025**: The system MUST include Feature 037, Feature 038, Feature 039, Feature 040, Feature 041, Feature 042, Feature 043, Feature 044, and Feature 045 artifacts in the prior-feature gate validation set.
- **FR-026**: The system MUST expose `evidence_population_by_metric_group`, `sample_usage_policy`, `action_exposure_data_status`, `legal_action_exposure_evidence_source`, `metric_population_consistency_verified`, and `aggregate_metrics_not_sample_derived` in the report.
- **FR-027**: The system MUST mark `action_exposure_data_status = insufficient_data_for_legal_action_exposure` when trace-backed legal-mask or equivalent exposure data is unavailable, and it MUST not substitute fake zero legal-action counts.
- **FR-028**: The system MUST allow `load_pressure_explains_completion_weakness` only when load and exposure metrics share the same full evidence population or when exposure data is explicitly unavailable and excluded from the verdict.
- **FR-029**: The system MUST allow `action_exposure_explains_completion_weakness` only when legal-vs-selected exposure is trace-backed from real legal-mask or equivalent exposure data.
- **FR-030**: The system MUST allow `mixed_load_action_pressure_explains_completion_weakness` only when load and action exposure are both full-population or explicitly comparable.
- **FR-031**: The system MUST not emit a non-inconclusive verdict when exposure, queue, or offload analysis exists only as representative lifecycle samples.

### Key Entities *(include if feature involves data)*

- **Full Evidence Population**: The complete passive trace bank or reconstructed lifecycle dataset used for aggregate load, action, queue, and offload analysis.
- **Representative Trace Sample**: A small illustrative slice of lifecycle evidence that may be cited for examples but not for verdict-driving aggregate metrics.
- **Evidence Population Metadata**: The per-metric annotation describing whether a metric came from the full passive trace bank, the full reconstructed lifecycle dataset, or a representative sample.
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

- **SC-001**: For each paper-default run analyzed, the report quantifies load, admission, action exposure, queue, and offload-path pressure using explicit counts and rates from the same evidence population.
- **SC-002**: The report distinguishes at least four pressure categories in runs where the evidence supports that separation.
- **SC-003**: The report identifies the dominant pressure source or states that the evidence is inconclusive in 100% of sampled runs.
- **SC-004**: The report includes per-strategy and per-action summaries for all approved strategies and action families when full evidence supports those summaries, or it explicitly marks them unavailable for verdict-making.
- **SC-005**: The report includes representative task-level budget comparisons for sampled runs and uses them only as supporting examples unless they are backed by the same full evidence population.
- **SC-006**: The report recommends the next feature type without proposing runtime repair, training, or policy redesign, unless a verified runtime-fault contradiction is discovered and explicitly named.
- **SC-007**: The feature introduces no runtime changes, no training, no optimizer activity, no replay training, no target updates, and no paper reproduction claim.
- **SC-008**: The report remains readable as both JSON and Markdown and is produced for every sampled paper-default run.
- **SC-009**: If only representative samples exist for exposure, queue, or offload analysis, the report must resolve to `diagnosis_inconclusive_requires_deeper_exposure_matrix`.
- **SC-010**: The report exposes the evidence population for each metric group and marks sample-derived aggregates as incomparable whenever a full-population denominator is unavailable.

## Assumptions

- Feature 044 passive traces and the Feature 045 report are expected to contain enough complete lifecycle evidence for aggregate diagnosis where the verdict is not declared inconclusive.
- Representative lifecycle samples may be used for examples, but not for aggregate metrics or verdict denominators.
- If legal-mask data is missing, action exposure must be treated as unavailable rather than inferred from zero counts.
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
