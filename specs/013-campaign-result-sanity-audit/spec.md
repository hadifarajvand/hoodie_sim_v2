# Feature Specification: Campaign Result Sanity Audit

**Feature Branch**: `[013-campaign-result-sanity-audit]`  
**Created**: 2026-05-07  
**Status**: Draft  
**Input**: User description: "Campaign Result Sanity Audit"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Inspect Campaign Artifacts (Priority: P1)

As a reviewer, I want to inspect campaign artifacts for obvious quality problems so I can determine whether the baseline reproduction results are trustworthy.

**Why this priority**: Artifact inspection is the core value of the audit. Without it, no anomaly review is possible.

**Independent Test**: Given a completed campaign artifact directory, an audit report can be generated that lists the available artifacts and summarizes their contents without changing any files.

**Acceptance Scenarios**:

1. **Given** a campaign artifact directory exists, **When** the audit is run, **Then** the report lists the campaign, matrix, bundle, and trace artifacts that were found.
2. **Given** the artifacts are present but suspicious, **When** the audit is run, **Then** the report still completes and marks the suspicious conditions as anomalies rather than failing silently.

---

### User Story 2 - Explain Anomalies (Priority: P2)

As a reviewer, I want the audit to explain unusual drop ratios, weak scenario separation, and near-identical policy outcomes so I can understand whether the campaign results are structurally sound.

**Why this priority**: The primary problem is not mere presence of artifacts, but that the results appear implausibly similar and under-differentiated.

**Independent Test**: Given the baseline campaign artifacts, the audit report identifies and categorizes anomaly signals for drop ratio, policy separation, and scenario separation.

**Acceptance Scenarios**:

1. **Given** the campaign results show a high drop ratio, **When** the audit runs, **Then** it flags the drop ratio as anomalous and reports it clearly.
2. **Given** multiple policies produce nearly identical outcomes, **When** the audit runs, **Then** it highlights the similarity and notes the affected baselines.

---

### User Story 3 - Check Accounting Consistency (Priority: P3)

As a reviewer, I want the audit to detect missing finalization or accounting inconsistencies so I can tell whether the campaign totals are internally consistent.

**Why this priority**: Even if results look plausible, broken accounting can invalidate the campaign. This is a later-stage forensic check.

**Independent Test**: Given campaign totals and per-run summaries, the audit reports whether totals reconcile and whether any missing-finalization indicators are present.

**Acceptance Scenarios**:

1. **Given** the campaign totals do not match the per-run summaries, **When** the audit runs, **Then** it reports an accounting inconsistency.
2. **Given** the audit detects missing finalization signals, **When** the audit runs, **Then** it records the issue in the report with affected artifacts.

---

### Edge Cases

- What happens when campaign artifacts are incomplete or partially missing?
- How does the audit report behave when anomaly signals are present but no single root cause is obvious?
- What happens when the same suspicious pattern appears across multiple policies and scenarios?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The audit MUST inspect completed campaign artifacts without modifying any artifact files.
- **FR-002**: The audit MUST report which campaign-level, matrix-level, bundle-level, and trace-level artifacts were found and which were missing.
- **FR-003**: The audit MUST identify anomalous aggregate outcomes, including unusually high drop ratios.
- **FR-004**: The audit MUST identify weak differentiation across scenarios when scenario-level outcomes are too similar to distinguish meaningfully.
- **FR-005**: The audit MUST identify weak differentiation across policies when multiple baselines produce near-identical results.
- **FR-006**: The audit MUST check for consistency between campaign summaries and the underlying matrix summaries.
- **FR-007**: The audit MUST report missing-finalization or accounting inconsistencies when totals or run counts do not reconcile.
- **FR-008**: The audit MUST produce a deterministic report for the same input artifacts.
- **FR-009**: The audit MUST preserve the existing simulator, policy, and metric behavior unchanged.
- **FR-010**: The audit MUST not require new runtime dependencies or external services.

### Key Entities *(include if feature involves data)*

- **Campaign Artifact Set**: The collection of campaign, matrix, bundle, and trace outputs produced by a completed baseline run.
- **Anomaly Report**: A read-only forensic summary of suspicious patterns, consistency checks, and missing artifacts.
- **Accounting Check**: A reconciliation summary that compares campaign-level totals against underlying per-run outputs.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A complete audit report is produced for 100% of valid completed baseline artifact sets.
- **SC-002**: At least 3 distinct anomaly categories are reported when the input artifacts exhibit high drop ratios, weak scenario differentiation, and near-identical policy outcomes.
- **SC-003**: The audit reports missing artifacts or accounting inconsistencies in every case where the underlying files do not reconcile.
- **SC-004**: Re-running the audit on the same artifact set produces identical report content.
- **SC-005**: The audit completes without changing any artifact files.

## Assumptions

- The audit is read-only and must never mutate campaign outputs.
- Existing campaign artifacts are treated as the source of truth for forensic inspection.
- High drop ratio, weak scenario differentiation, and near-identical policy outcomes are treated as anomaly signals to be explained, not corrected.
- If the audit cannot infer a single root cause, it should report multiple plausible anomaly signals rather than forcing a false conclusion.

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

