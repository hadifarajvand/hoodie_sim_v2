# Feature Specification: Baseline Revalidation After Runtime Repair

**Feature Branch**: `037-baseline-revalidation-after-runtime-repair`  
**Created**: 2026-05-13  
**Status**: Draft  
**Input**: User description: "Feature 037 — Baseline Revalidation After Runtime Repair"

## Clarifications

### Session 2026-05-13

- Q: Which baseline policies are in scope for revalidation? → A: FLC, VO, HO, RO, BCO, MLEO, and ADAPTIVE.
- Q: Must every policy run through `HoodieGymEnvironment` without shortcuts or legal-mask bypasses? → A: Yes. Every policy must use `HoodieGymEnvironment` and must not bypass `legal_action_mask`.
- Q: Which scenario and seed set should be used for baseline revalidation? → A: Use the repaired paper-default runtime configuration unless an existing smaller smoke scenario is already used by the matrix runner for deterministic validation; if a smaller smoke scenario is used, label it as smoke revalidation, not paper-scale reproduction. Use deterministic seeds, with `0`, `1`, and `2` as the minimal set and `0` through `4` preferred when runtime cost allows.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Baseline Interface Revalidation (Priority: P1)

As a simulator maintainer, I need the existing baseline policies to run through the repaired environment interface so that I can confirm they still execute under the approved runtime contracts.

**Why this priority**: If the baselines do not run cleanly through the shared environment, the repaired runtime cannot be trusted for downstream evaluation.

**Independent Test**: Run each baseline policy through the same environment entry points with deterministic seeds and confirm each policy completes an evaluation episode without bypassing the shared action validation path.

**Acceptance Scenarios**:

1. **Given** the repaired runtime contracts are active, **When** FLC, VO, HO, RO, BCO, MLEO, and ADAPTIVE each run on the paper-default scenario, **Then** each policy completes through the same environment interface.
2. **Given** a baseline proposes an action, **When** the environment validates it, **Then** the action is accepted only if it is legal under the shared mask.

---

### User Story 2 - Deterministic Baseline Revalidation (Priority: P2)

As a simulator maintainer, I need revalidation artifacts to be deterministic for fixed seeds so that the baseline sanity results can be compared and audited reliably.

**Why this priority**: Determinism is required to distinguish runtime stability from incidental variation.

**Independent Test**: Re-run each deterministic baseline with the same seed and confirm the resulting artifacts and metrics are identical across repeated runs; confirm the seed-controlled baseline remains reproducible.

**Acceptance Scenarios**:

1. **Given** a fixed seed and a deterministic baseline policy, **When** the revalidation is run twice, **Then** the artifact contents and metric outputs are identical.
2. **Given** RO is run under seed control, **When** the same seed is reused, **Then** the baseline result remains reproducible.

---

### User Story 3 - Baseline Sanity Reporting (Priority: P3)

As a simulator maintainer, I need a report that summarizes post-repair baseline sanity results so that I can verify the baselines ran without claiming paper reproduction.

**Why this priority**: Reporting is the audit surface that proves the baselines were revalidated under the repaired runtime.

**Independent Test**: Produce a report that lists the revalidated policies, scenarios, seeds, environment contract checks, legal-action verification, and deterministic reproducibility results without any paper-curve matching claim.

**Acceptance Scenarios**:

1. **Given** the baseline revalidation is complete, **When** the report is generated, **Then** it explicitly labels the results as post-runtime-repair sanity results, not paper reproduction.
2. **Given** the report is reviewed, **When** the summary is inspected, **Then** it shows which policies ran, which contracts were verified, and whether the artifacts were deterministic.

### Edge Cases

- A baseline must not be allowed to bypass the legal action mask even if it previously relied on a shortcut path.
- A deterministic baseline must produce the same artifact contents when rerun with the same seed.
- RO must remain seed-controlled and reproducible, even though its action choices may differ from deterministic policies.
- The report must not imply the paper has been reproduced merely because the baselines run successfully.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST revalidate the seven in-scope baseline policies: FLC, VO, HO, RO, BCO, MLEO, and ADAPTIVE.
- **FR-002**: The system MUST run all in-scope baselines through the same `HoodieGymEnvironment` interface used by the repaired runtime.
- **FR-003**: The system MUST use deterministic seeds for baseline revalidation runs.
- **FR-004**: The system MUST use the repaired paper-default runtime configuration, including the approved traffic and resource settings already established by Features 032–036.
- **FR-005**: The system MUST verify that each baseline emits only legal actions under the shared action validation path.
- **FR-006**: The system MUST verify that no baseline bypasses the legal action mask.
- **FR-007**: The system MUST verify that fixed-seed runs for deterministic baselines produce deterministic revalidation artifacts.
- **FR-008**: The system MUST verify that RO remains reproducible when run with the same seed.
- **FR-009**: The system MUST use the repaired paper-default runtime configuration, unless an existing smaller smoke scenario is already used by the matrix runner for deterministic validation; any smaller run MUST be labeled as smoke revalidation, not paper-scale reproduction.
- **FR-010**: The system MUST capture revalidation metrics using the existing evaluation schema without reshaping metrics to resemble paper curves.
- **FR-011**: The system MUST generate a baseline revalidation report that clearly labels the output as post-runtime-repair sanity results, not paper reproduction.
- **FR-012**: The system MUST include the prerequisite runtime contracts verified by Features 032, 033, 034, 035, and 036 in the revalidation report.
- **FR-013**: The system MUST refuse any claim of paper reproduction success based solely on baseline execution.
- **FR-014**: The system MUST avoid changes to baseline policy logic, training behavior, or environment semantics beyond the repaired runtime contracts already approved.
- **FR-015**: The system MUST avoid rewriting paper registries or introducing dependency, topology, CPU-capacity, transmission-delay, capacity-sharing, timeout, or reward-equation drift.

### Key Entities *(include if data involved)*

- **Baseline Policy**: One of the in-scope policies being revalidated against the repaired environment.
- **Revalidation Run**: A seeded evaluation pass that produces comparable metrics and artifacts for a baseline policy.
- **Revalidation Report**: The summary artifact that records policies, scenarios, seeds, contract checks, and reproducibility results.
- **Legal Action Mask**: The environment-provided legality constraint that filters permitted baseline actions.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All seven in-scope baseline policies complete at least one evaluation run through the same environment interface.
- **SC-002**: 100% of actions taken during revalidation are accepted only when they are legal under the shared action mask.
- **SC-003**: Deterministic baselines produce identical revalidation artifacts across repeated runs with the same seed.
- **SC-004**: RO produces reproducible results for the same seed in repeated runs.
- **SC-005**: The revalidation report records all required contracts, seeds, policy names, and artifact paths with no paper-reproduction claim.

## Assumptions

- The repaired runtime contracts from Features 032–036 are already established and remain the baseline for this feature.
- Existing baseline policies are revalidated without changing their internal logic.
- The evaluation metrics schema already exists and can be reused for sanity reporting.
- Any new report artifact will be explicitly framed as post-runtime-repair baseline sanity output, not evidence of paper reproduction.
- The minimal deterministic seed set is `0`, `1`, and `2`; `0` through `4` may be used when runtime cost allows.
- Old artifacts may be used only as drift references; they are not ground truth after runtime repair.

## Production Constraints

- [x] Performance budgets identified
- [x] Artifact handling rules identified
- [x] Security and secret-hygiene constraints identified
- [x] CI quality gate impact identified

## Public Interfaces Affected

- [x] Environment reset/step
- [x] Policy interface
- [x] Evaluation metric interface
- [x] Artifact schema
- [ ] Task model
- [ ] Topology interface
- [ ] Runtime model interface
- [x] Config schema

## Config / Schema Impact

- [x] Required config fields identified
- [x] Validation rules identified
- [x] Backward-compatibility impact identified

## Artifact Impact

- [x] Raw metrics
- [x] Reports
- [x] Validation summaries
- [x] Debug traces
- [ ] Plots
- [ ] Checkpoints

## Security Considerations

- [x] Secrets / tokens / credentials reviewed
- [x] Remote code execution reviewed
- [x] External references documented

## Definition of Done

- [x] Spec matched by plan
- [ ] Tests identified
- [x] Assumptions documented
- [x] Configs validated or updated
- [x] Paper-to-code mapping updated
- [x] Artifacts handled per lifecycle rules
- [x] Review and merge gate satisfied
