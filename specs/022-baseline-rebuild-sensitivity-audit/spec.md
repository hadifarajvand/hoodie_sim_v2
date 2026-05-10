# Feature Specification: Baseline Rebuild Sensitivity Audit

**Feature Branch**: `[022-baseline-rebuild-sensitivity-audit]`  
**Created**: 2026-05-10  
**Status**: Draft  
**Input**: User description: "Feature 022 — Baseline Rebuild Sensitivity Audit"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Check Rebuild Robustness (Priority: P1)

A maintainer wants to know whether Feature 021’s `collapse_reduced` result is stable when the same rebuild is rerun under small, controlled variations. The maintainer needs a sensitivity audit that shows whether the rebuild signal is robust, fragile, worsened, or inconclusive without changing the meaning of the baseline comparison.

**Why this priority**: This is the core value of the audit. If the rebuild signal is not robust, the maintainer needs to know before treating it as a durable conclusion.

**Independent Test**: Can be fully tested by rerunning the sensitivity audit across a tiny set of seeds, scenarios, and supported episode lengths and checking that the audit reports a deterministic sensitivity classification.

**Acceptance Scenarios**:

1. **Given** the Feature 018, 019, 020, and 021 gate artifacts are present and internally consistent, **When** the audit runs, **Then** it produces a sensitivity report and states whether the Feature 021 conclusion is robust, fragile, worsened, or inconclusive.
2. **Given** a tiny controlled change in seed, scenario, or supported episode length, **When** the audit runs, **Then** the report identifies whether baseline signatures stay differentiated or collapse again.

### User Story 2 - Preserve Conservative Interpretation (Priority: P2)

A maintainer reviews a sensitivity audit and understands that an unstable or collapsed result is not automatically a bug, and that the audit does not prove paper-level reproduction validity. The report must preserve the possibility that collapse is a real mechanism property.

**Why this priority**: The audit must not overclaim. Fragility or instability is an important outcome and must be reported honestly.

**Independent Test**: Can be independently verified by checking that the report includes no-training, no-policy-redesign, no-metric-change, and no-paper-validity disclaimers, and that it does not force `collapse_reduced` as the only acceptable outcome.

**Acceptance Scenarios**:

1. **Given** an unstable or mixed sensitivity result, **When** the maintainer inspects the report, **Then** the audit classifies it as fragile or inconclusive rather than hiding the instability.
2. **Given** a sensitivity audit with unchanged or worsened collapse, **When** the maintainer inspects it, **Then** the report still records the outcome as valid and does not claim training, policy redesign, or paper-level success.

### Edge Cases

- What happens when the Feature 018/019/020/021 artifacts are missing or inconsistent? The audit must fail closed and report that the gate was not satisfied.
- How does the feature behave when a scenario or episode-length variation is not supported through current public interfaces? The audit must mark that dimension inconclusive rather than fabricating control.
- What happens when the sensitivity result is mixed across dimensions? The report must preserve the instability and classify the audit conservatively.

## Requirements *(mandatory)*

## Clarifications

### Session 2026-05-10

- Q: When should the audit call the result robust versus fragile? → A: `robust_collapse_reduced` only if the reduction survives all supported tiny variations; `fragile_collapse_reduced` if it survives some variations but fails or degrades under others.
- Q: Which artifacts should the sensitivity audit require before it runs? → A: Require the final committed artifacts from Features 018, 019, 020, and 021, including their summary/report outputs.
- Q: Which seed set should the audit use? → A: Use `7, 11, 13`.
- Q: Which scenario set and episode lengths should the audit use, and how should unsupported combinations be handled? → A: Use the supported scenario set `paper_default`, `moderate`, `heavy` when available; use episode lengths `4` and `6` only if supported; mark unsupported combinations inconclusive.
- Q: Which baselines and metrics should the audit use, and how should baseline signatures be computed? → A: Include all existing baseline policies from the current baseline evaluation framework, reuse the same metrics already used in Feature 021, and compute a compact signature from completed tasks, dropped tasks, throughput, and average delay.

### Functional Requirements

- **FR-001**: The system MUST gate the sensitivity audit on Feature 018, Feature 019, Feature 020, and Feature 021 artifacts being present and internally consistent.
- **FR-002**: The system MUST evaluate whether Feature 021’s rebuild conclusion remains robust, fragile, worsened, or inconclusive under small controlled variations.
- **FR-003**: The system MUST test sensitivity across a tiny fixed seed set, a tiny fixed scenario set, and supported tiny episode-length variations.
- **FR-004**: The system MUST reuse the existing baseline fairness rebuild result as the reference point for sensitivity comparison.
- **FR-005**: The system MUST preserve the possibility that persistent collapse is a mechanism property and MUST NOT automatically label instability as a bug.
- **FR-006**: The system MUST NOT redesign policies, change metric formulas, or change simulator behavior.
- **FR-007**: The system MUST produce deterministic sensitivity audit artifacts in JSON and Markdown form, with optional CSV only if already conventional and deterministic in the repository.
- **FR-008**: The system MUST include source gate status, sensitivity dimensions, seeds/scenarios/episode lengths used, included baselines, reused metrics, per-setting baseline signatures, collapse stability indicators, sensitivity classification, limitations, reproducibility details, and no-training/no-policy-redesign/no-metric-change/no-paper-validity disclaimers in the report.
- **FR-009**: The system MUST avoid campaign-scale reproduction, paper-curve fitting, dependency changes, and plotting.

### Key Entities *(include if feature involves data)*

- **Source Gate**: The set of prior feature artifacts required before the sensitivity audit is considered valid.
- **Sensitivity Dimension**: A small controlled variation used to test whether the Feature 021 rebuild conclusion is stable.
- **Baseline Signature**: A compact representation of baseline behavior used to compare differentiation across settings.
- **Sensitivity Audit Report**: The JSON and Markdown artifacts that summarize robustness, fragility, or collapse stability.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The sensitivity audit report can be generated deterministically from the same inputs with identical output on repeated runs.
- **SC-002**: The report classifies the sensitivity outcome as `robust_collapse_reduced`, `fragile_collapse_reduced`, `collapse_unchanged`, `collapse_worsened`, or `inconclusive` with no unclassified outcomes.
- **SC-003**: The audit report clearly identifies which seed, scenario, and episode-length settings were actually supported and which were marked inconclusive.
- **SC-004**: A reviewer can determine from the report whether the Feature 021 conclusion appears robust or fragile in under 2 minutes.
- **SC-005**: The report includes explicit limitations and no-training/no-policy-redesign/no-metric-change/no-paper-validity disclaimers.

## Assumptions

- The Feature 021 rebuild artifact is available and can be used as the reference point for sensitivity checks.
- Supported scenarios and episode lengths are limited to what the current public interfaces already expose.
- If sensitivity is unstable, that instability is reported directly rather than tuned away.
- The audit remains diagnostic and does not imply paper-level completeness or baseline superiority.

## Production Constraints

- [x] Performance budgets identified
- [x] Artifact handling rules identified
- [x] Security and secret-hygiene constraints identified
- [x] CI quality gate impact identified

## Public Interfaces Affected

- [x] Environment reset/step
- [x] Policy interface
- [ ] Task model
- [ ] Topology interface
- [x] Runtime model interface
- [x] Evaluation metric interface
- [x] Config schema
- [x] Artifact schema

## Config / Schema Impact

- [x] Required config fields identified
- [x] Validation rules identified
- [x] Backward-compatibility impact identified

## Artifact Impact

- [ ] Raw metrics
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
