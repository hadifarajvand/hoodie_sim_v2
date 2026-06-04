# Feature Specification: HOODIE Baseline Fidelity Audit and Formula Mapping

**Feature Branch**: `[085-hoodie-paper-baseline-fidelity-audit]`  
**Created**: 2026-06-04  
**Status**: Draft  
**Input**: User description: "Repair HOODIE paper baseline fidelity and prepare full audit Spec Kit."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Correct Baseline Naming (Priority: P1)

As a maintainer, I want the audit outputs to use the correct baseline name `MLEO` instead of the legacy `MQO` label so that the paper-aligned comparison set is accurate.

**Why this priority**: The current audit is invalid if a baseline is mislabeled. This is the most immediate correctness issue.

**Independent Test**: Run the audit artifact generator and inspect the policy coverage, aggregate tables, and ranking tables to confirm `MLEO` appears and `MQO` does not appear in active outputs.

**Acceptance Scenarios**:

1. **Given** a regenerated audit artifact bundle, **When** the policy table is inspected, **Then** the active policy set contains `HOODIE, RO, FLC, VO, HO, BCO, MLEO`.
2. **Given** the same artifact bundle, **When** the report is rendered, **Then** no active policy row or ranking row uses `MQO` as the canonical baseline label.

---

### User Story 2 - Formula-to-Code Audit (Priority: P1)

As a reviewer, I want a formal formula-to-code mapping matrix so I can verify which paper equations, figures, and algorithms are implemented, where they live in code, and what still needs repair.

**Why this priority**: The baseline rename is only useful if the formulas tied to the report are traceable and auditable.

**Independent Test**: Open the matrix and verify every required formula row is present with a paper reference, meaning, expected simulation behavior, code location, status, and required fix.

**Acceptance Scenarios**:

1. **Given** the formula mapping matrix, **When** I scan the rows for `task_completion_delay`, `task_drop_ratio`, reward calculation, and offload delay, **Then** each row has an explicit code location and audit status.
2. **Given** the same matrix, **When** I scan the rows for DQN, DDQN, Dueling, and LSTM interfaces, **Then** each one is mapped to code and marked with an explicit audit outcome.

---

### User Story 3 - Merge Gate Protection (Priority: P2)

As a release manager, I want the audit to block any merge of PR #24 until the baseline correction and formula audit are complete so that stale baseline labels do not get merged back into the repository.

**Why this priority**: The wrong baseline label would undermine the audit and every downstream report if it is merged prematurely.

**Independent Test**: Verify the validation rules fail when `MQO` appears in active outputs or when the formula matrix is incomplete, and verify the merge gate remains closed until the audit passes.

**Acceptance Scenarios**:

1. **Given** an incomplete audit bundle, **When** validation runs, **Then** the merge gate remains blocked.
2. **Given** a complete audit bundle, **When** validation runs, **Then** the merge gate may open and no stale `MQO` label is present in active outputs.

---

### Edge Cases

- A legacy compatibility alias exists in code, but the generated report and artifacts must still show `MLEO` as the canonical baseline.
- Historical artifacts may still contain `MQO`; the audit must distinguish historical output from current canonical output.
- The formula matrix may reference multiple code locations for one equation when runtime and learning paths both contribute.
- Missing formula fields must be flagged explicitly rather than silently inferred.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The audit MUST replace the active runtime baseline label `MQO` with `MLEO` in generated evaluation artifacts, policy definitions, and reported metric tables.
- **FR-002**: The audit MUST ensure the active policy set is exactly `HOODIE, RO, FLC, VO, HO, BCO, MLEO`.
- **FR-003**: The audit MUST prevent `MQO` from appearing as an active policy label in final artifacts or report coverage.
- **FR-004**: The audit MUST generate a baseline-mapping matrix that documents canonical baseline names, legacy labels, code locations, and audit status.
- **FR-005**: The audit MUST generate a formula-to-code mapping matrix with columns for paper equation/figure/algorithm, meaning, expected simulation behavior, code location, status, and required fix.
- **FR-006**: The formula-to-code matrix MUST include `task_completion_delay`, `task_drop_ratio`, reward calculation, vertical offload delay, horizontal offload delay, DQN interface, DDQN interface, Dueling interface, and LSTM interface.
- **FR-007**: The audit MUST update validation rules so that generated artifacts fail if `MQO` is present in active coverage or if any required formula mapping row is missing.
- **FR-008**: The audit MUST document the code locations that implement the Feature 080 proposed method path used by `HOODIE`.
- **FR-009**: The audit MUST explicitly state the claim boundary that no statistical superiority claim and no full empirical paper reproduction claim are being made.
- **FR-010**: The audit MUST block completion if PR #24 would merge before baseline correction and formula audit validation passes.
- **FR-011**: The audit MUST regenerate artifact outputs and reported metric tables so that they consistently use the canonical baseline label `MLEO`.

### Key Entities

- **Baseline Policy**: A canonical policy label used in audit outputs and validation rules.
- **Legacy Label**: A retired or compatibility label that may exist in code history but must not appear as an active audit policy.
- **Formula Mapping Row**: A paper-to-code trace record describing what a formula means, how it is simulated, where it lives in code, and whether it needs repair.
- **Audit Artifact Bundle**: The generated raw rows, aggregate tables, rankings, report, manifest, and mapping matrices.
- **Validation Gate**: A rule set that fails when stale labels or incomplete mappings are present.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of active policy references in generated audit artifacts use `MLEO` instead of `MQO`.
- **SC-002**: The final artifact bundle contains the full active policy set `HOODIE, RO, FLC, VO, HO, BCO, MLEO` and no other active baseline labels.
- **SC-003**: The formula-to-code matrix includes every required formula row and each row has a code location and status.
- **SC-004**: Validation fails when `MQO` is reintroduced into active policy coverage or when the formula matrix is incomplete.
- **SC-005**: A reviewer can trace each primary paper formula to a code location without consulting unstructured notes.

## Assumptions

- `MLEO` is the canonical paper baseline name for the minimum-latency / minimum-latency-estimate offloading behavior already present in the repository.
- `MQO` may remain as a legacy alias in internal code paths only if audit outputs never expose it.
- The audit is deterministic and uses the existing repository evaluation pipeline rather than a new simulator.
- The work is limited to baseline fidelity, formula traceability, and audit gating; it does not introduce DCQ, a thesis method, or a queue redesign.

## Production Constraints

- [x] Performance budgets identified
- [x] Artifact handling rules identified
- [x] Security and secret-hygiene constraints identified
- [x] CI quality gate impact identified

## Public Interfaces Affected

- [x] Policy interface
- [x] Runtime model interface
- [x] Evaluation metric interface
- [x] Artifact schema
- [x] Config schema

## Config / Schema Impact

- [x] Required config fields identified
- [x] Validation rules identified
- [x] Backward-compatibility impact identified

## Artifact Impact

- [x] Raw metrics
- [x] Reports
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
