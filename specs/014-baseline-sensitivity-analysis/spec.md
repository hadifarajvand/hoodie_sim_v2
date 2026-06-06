# Feature Specification: Baseline Sensitivity Analysis

**Feature Branch**: `[014-baseline-sensitivity-analysis]`  
**Created**: 2026-05-07  
**Status**: Draft  
**Input**: User description: "Baseline Sensitivity Analysis"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Explain Trace Collapse (Priority: P1)

As a reviewer, I want to compare the committed campaign traces across scenarios and seeds so I can see whether the baseline collapse starts with the traffic inputs themselves.

**Why this priority**: If trace inputs are already indistinguishable, policy and metric differences are not the root cause.

**Independent Test**: Given the committed campaign artifacts, the analysis identifies identical or near-identical trace realizations across scenario pairs and seeds without modifying any files.

**Acceptance Scenarios**:

1. **Given** the paper baseline campaign artifacts are available, **When** the analysis runs, **Then** it reports whether `moderate` and `paper_default` traces are identical by seed.
2. **Given** trace inputs differ by distribution rather than exact content, **When** the analysis runs, **Then** it reports task-count, arrival-slot, and task-size distribution differences.

---

### User Story 2 - Explain Policy Collapse (Priority: P2)

As a reviewer, I want to compare policy behavior across the committed campaign artifacts so I can tell whether several baselines are making effectively the same choices.

**Why this priority**: If policy action choices collapse, apparent baseline differences can disappear even when the inputs vary.

**Independent Test**: Given the committed campaign artifacts, the analysis identifies policy groups with identical or near-identical action and outcome distributions.

**Acceptance Scenarios**:

1. **Given** the campaign artifacts show similar policy outcomes, **When** the analysis runs, **Then** it flags policy groups with identical or near-identical behavior.
2. **Given** action choices diverge but outcomes do not, **When** the analysis runs, **Then** it distinguishes action collapse from outcome masking.

---

### User Story 3 - Explain Saturation and Masking (Priority: P3)

As a reviewer, I want the analysis to estimate whether environment saturation, timeout pressure, or aggregation masking is hiding true differences so I can judge whether the collapse is structural or merely reported that way.

**Why this priority**: Even when traces and policies differ, totals and averages can hide that separation.

**Independent Test**: Given the committed campaign artifacts, the analysis explains whether high drop ratio and delay patterns are consistent with saturation, timeout/finalization pressure, or masked differences.

**Acceptance Scenarios**:

1. **Given** the campaign shows a high drop ratio, **When** the analysis runs, **Then** it reports whether saturation pressure is a plausible contributor.
2. **Given** metric summaries hide differences visible in raw artifacts, **When** the analysis runs, **Then** it reports that aggregation may be masking the differences.

---

### Edge Cases

- What happens when trace files are missing for one or more seeds?
- What happens when scenario traces are identical but policy distributions diverge?
- How does the analysis report ambiguity when multiple collapse causes are plausible?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The analysis MUST inspect committed campaign artifacts as read-only inputs and MUST not mutate them.
- **FR-002**: The analysis MUST report whether trace inputs are identical, same-count-but-different-arrival-slot, or different-count across scenario pairs and seeds.
- **FR-003**: The analysis MUST compare task-count, arrival-slot, and task-size distributions across scenarios and seeds.
- **FR-004**: The analysis MUST compare policy action distributions and terminal outcome distributions across policies.
- **FR-005**: The analysis MUST identify policy groups with identical or near-identical behavior.
- **FR-006**: The analysis MUST estimate whether environment saturation pressure is consistent with high drop ratio and delay patterns.
- **FR-007**: The analysis MUST identify whether timeout or finalization pressure may be contributing to the observed collapse.
- **FR-008**: The analysis MUST identify whether metric aggregation may be masking distinctions visible in raw artifacts.
- **FR-009**: The analysis MUST produce both machine-readable and human-readable reports.
- **FR-010**: The analysis MUST report missing or incomplete artifacts explicitly.
- **FR-011**: The analysis MUST be deterministic for the same input artifacts.
- **FR-012**: The analysis MUST not claim paper reproduction validity.

### Key Entities *(include if feature involves data)*

- **Campaign Artifact Set**: The committed baseline reproduction outputs that are treated as the source of truth for analysis.
- **Trace Comparison**: A comparison of trace realizations across scenarios and seeds using task counts, arrival slots, and task sizes.
- **Policy Behavior Signature**: A summary of action and terminal outcome distributions for a policy across the committed artifacts.
- **Sensitivity Report**: A deterministic analysis report explaining which inputs and behaviors are distinguishable and which are collapsed.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The analysis reports whether `moderate` and `paper_default` traces are identical for every shared seed present in the committed artifacts.
- **SC-002**: The analysis identifies the `BCO`, `FLC`, and `MLEO` policy equivalence pattern present in the committed baseline outputs.
- **SC-003**: The analysis identifies whether scenario differences are visible in trace inputs for at least one scenario comparison.
- **SC-004**: The analysis identifies whether action choices are distinguishable from terminal outcomes in the committed baseline artifacts.
- **SC-005**: Running the analysis twice on the same artifact set produces identical report content.
- **SC-006**: The analysis completes without mutating any existing campaign artifacts.

## Assumptions

- The committed `artifacts/campaigns/paper-baseline-reproduction` tree is the primary source of truth.
- The analysis will use trace files, matrix summaries, and policy summaries already present in the repository.
- If multiple collapse causes are plausible, the report should present the plausible causes rather than force a single root cause.
- High drop ratio, identical policy signatures, and weak scenario differentiation are treated as signals to explain, not as proof of simulator defects.

## Production Constraints

- [x] Performance budgets identified
- [x] Artifact handling rules identified
- [x] Security and secret-hygiene constraints identified
- [x] CI quality gate impact identified

## Public Interfaces Affected

- [ ] Environment reset/step
- [ ] Policy interface
- [ ] Task model
- [ ] Topology interface
- [ ] Runtime model interface
- [ ] Evaluation metric interface
- [ ] Config schema
- [x] Artifact schema

## Config / Schema Impact

- [x] Required config fields identified
- [x] Validation rules identified
- [x] Backward-compatibility impact identified

## Artifact Impact

- [x] Raw metrics
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

- [x] Spec matched by plan
- [x] Tests identified
- [x] Assumptions documented
- [x] Configs validated or updated
- [x] Paper-to-code mapping updated
- [x] Artifacts handled per lifecycle rules
- [x] Review and merge gate satisfied

