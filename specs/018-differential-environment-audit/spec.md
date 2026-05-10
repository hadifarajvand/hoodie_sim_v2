# Feature Specification: Differential Environment Audit

**Feature Branch**: `018-differential-environment-audit`  
**Created**: 2026-05-10  
**Status**: Draft  
**Input**: User description: "Feature 018 — Differential Environment Audit"

## Clarifications

### Session 2026-05-10

- Q: Which environment interface is allowed for the audit? → A: Use the existing public `reset`/`step` lifecycle interface only; if exact hand-fed traces cannot be injected, classify the result as `instrumentation_gap` or `unsupported_by_environment_trace`.
- Q: How are toy cases represented? → A: Use a small declarative case fixture with stable fields so the audit inputs remain explicit, reproducible, and canonical.
- Q: What counts as identical enough when the environment lacks direct trace injection? → A: Treat inputs as identical if the same declarative toy-case fixture is used for both sides, even when the environment can only approximate the trace through its public interface.
- Q: What is the exact report schema and output location? → A: Use a fixed top-level audit object with per-case comparison records and write deterministic reports under `artifacts/analysis/differential-environment-audit/`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Deterministic differential audit report (Priority: P1)

As a maintainer, I want a diagnostic-only audit that compares identical toy lifecycle cases between the Feature 017 reference kernel and the current HoodieGymEnvironment so that lifecycle divergences are surfaced without altering either side.

**Why this priority**: The audit is only useful if it can compare the two behaviors on the same toy inputs and produce a deterministic report.

**Independent Test**: Run the audit on the required toy cases and verify that the JSON and Markdown outputs contain the reference summary, environment summary, and a comparison result for each case.

**Acceptance Scenarios**:

1. **Given** a one-task local compute toy case, **When** the audit runs against the reference kernel and the current environment, **Then** the report records both observed lifecycles and classifies the case result deterministically.
2. **Given** a one-task horizontal offload toy case, **When** the audit runs, **Then** the report includes the comparison outcome and preserves the original observations without normalizing divergences away.
3. **Given** a one-task vertical offload toy case, **When** the audit runs, **Then** the report is reproducible and does not modify either execution target.

---

### User Story 2 - Classified divergence reporting (Priority: P2)

As a maintainer, I want each finding to be classified so that bugs, assumptions, instrumentation gaps, and scope differences are distinguished instead of collapsed into a single generic mismatch.

**Why this priority**: Without classification, the audit cannot separate likely environment bugs from expected scope differences or missing instrumentation.

**Independent Test**: Run the audit on timeout/drop, delayed reward timing, and deterministic event ordering toy cases, then verify each finding receives a deterministic comparison label and a secondary finding class.

**Acceptance Scenarios**:

1. **Given** a timeout/drop toy case, **When** the environment does not expose exact hand-fed trace support, **Then** the audit reports an unsupported trace or instrumentation gap rather than patching the environment.
2. **Given** a delayed reward timing toy case, **When** the environment and reference kernel differ, **Then** the report distinguishes a divergence from a paper assumption gap.
3. **Given** a deterministic event ordering toy case, **When** repeated runs are identical, **Then** the audit classifies the case as a match and keeps the report ordering stable.

---

### User Story 3 - Reproducible no-fix audit artifacts (Priority: P3)

As a maintainer, I want the audit outputs to be reproducible and explicitly non-remediating so that the report can be used as evidence without implying that the environment was repaired.

**Why this priority**: The feature must remain diagnostic only. A reproducible report is necessary for later review and for separating observation from correction.

**Independent Test**: Run the audit twice on the same toy inputs and verify that the JSON and Markdown artifacts are byte-stable or deterministically equivalent and include the no-fix disclaimer.

**Acceptance Scenarios**:

1. **Given** the same toy traces and actions, **When** the audit is rerun, **Then** the report order and classifications remain stable.
2. **Given** any finding in the audit report, **When** the report is reviewed, **Then** it clearly states that no fixes were applied to HoodieGymEnvironment, SlotEngine, or any simulator lifecycle path.

---

### Edge Cases

- What happens when the current environment cannot accept exact hand-fed traces or actions? The report must classify the result as an instrumentation gap or unsupported_by_environment_trace.
- What happens when the environment exposes a lifecycle observation that the reference kernel does not support? The report must classify the result as unsupported_by_reference_kernel.
- What happens when the observations are insufficient to determine a verdict? The report must classify the result as inconclusive.
- What happens when a toy case differs by design rather than by bug? The report must label it as expected_scope_difference and not convert it into a repair target.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST compare identical deterministic toy traces and actions between the Feature 017 reference kernel and the current HoodieGymEnvironment using the current public `reset`/`step` lifecycle interface only.
- **FR-002**: The system MUST generate a deterministic audit report in machine-readable form and a deterministic human-readable form.
- **FR-003**: The system MUST include audit metadata, input toy cases, reference ledger summaries, environment-observed lifecycle summaries, per-case comparison results, classified findings, assumptions versus divergences, unsupported observations, a no-fix disclaimer, reproducibility details, and deterministic output paths under `artifacts/analysis/differential-environment-audit/`.
- **FR-004**: The system MUST support the required toy cases: one-task local compute, one-task horizontal offload, one-task vertical offload, timeout/drop, delayed reward timing, and deterministic event ordering.
- **FR-005**: The system MUST classify each comparison result as one of `match`, `divergence`, `assumption_gap`, `unsupported_by_environment_trace`, `unsupported_by_reference_kernel`, or `inconclusive`.
- **FR-006**: The system MUST classify each finding as one of `likely_environment_bug`, `likely_reference_gap`, `paper_assumption_gap`, `instrumentation_gap`, `expected_scope_difference`, or `unresolved`.
- **FR-007**: The system MUST distinguish assumptions from divergences and MUST not normalize mismatches away.
- **FR-008**: The system MUST remain diagnostic only and MUST not modify HoodieGymEnvironment, SlotEngine, simulator lifecycle behavior, policies, baselines, metric formulas, campaign orchestration, or dependency state.
- **FR-009**: The system MUST treat inability to accept exact hand-fed traces or actions as an instrumentation gap or unsupported_by_environment_trace rather than attempting compatibility patches.
- **FR-010**: The system MUST preserve deterministic report ordering so repeated runs over the same toy cases produce the same comparison structure and labels.

### Key Entities *(include if feature involves data)*

- **Toy Case**: A deterministic input scenario used to drive both the reference kernel and the environment.
- **Reference Ledger Summary**: A compact description of the reference kernel’s observed lifecycle for one toy case.
- **Environment Lifecycle Summary**: A compact description of the current environment’s observed lifecycle for one toy case.
- **Comparison Finding**: A labeled result that records whether the two observations match or diverge and how that difference should be interpreted.
- **Audit Report**: The deterministic output artifact containing all cases, summaries, classifications, assumptions, and reproducibility details.
- **Reproducibility Record**: The metadata needed to rerun the audit and verify that the same inputs produce the same report structure.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The audit produces both JSON and Markdown reports for every required toy case in a single run.
- **SC-002**: Re-running the audit with the same toy cases and actions produces the same case order and classification order.
- **SC-003**: Every toy case in the report includes both a reference summary and an environment summary, or an explicit unsupported/instrumentation classification.
- **SC-004**: The report includes at least one classification entry for each of `match`, `divergence`, `assumption_gap`, `unsupported_by_environment_trace`, `unsupported_by_reference_kernel`, or `inconclusive` as applicable to the observed inputs.
- **SC-005**: The report explicitly states that no fixes were applied to HoodieGymEnvironment, SlotEngine, simulator lifecycle code, or any related policy/baseline/metric/campaign path.

## Assumptions

Any assumption that materially changes code, workflow, or repository state MUST be recorded and
presented for user approval before implementation depends on it.

- The reference kernel in `src/reference_model` is treated as the comparison baseline for toy lifecycle behavior.
- The current environment is exercised through its public `reset`/`step` lifecycle interface only; if exact hand-fed trace injection is unavailable, the report records an instrumentation gap or unsupported_by_environment_trace rather than forcing compatibility.
- The audit may classify differences caused by deliberate scope mismatch as expected scope differences instead of bugs.
- Output artifact locations and file names will be deterministic and confined to `artifacts/analysis/differential-environment-audit/`.

## Production Constraints

- [x] Performance budgets identified
- [x] Artifact handling rules identified
- [x] Security and secret-hygiene constraints identified
- [x] CI quality gate impact identified

## Public Interfaces Affected

- [ ] Environment reset/step
- [ ] Policy interface
- [x] Task model
- [x] Runtime model interface
- [ ] Evaluation metric interface
- [ ] Config schema
- [x] Artifact schema

## Config / Schema Impact

- [x] Required config fields identified
- [x] Validation rules identified
- [x] Backward-compatibility impact identified

## Artifact Impact

- [ ] Raw metrics
- [x] Reports
- [ ] Checkpoints
- [x] Debug traces
- [x] Validation summaries

## Security Considerations

- [x] Secrets / tokens / credentials reviewed
- [x] Remote code execution reviewed
- [x] External references documented

## Definition of Done

- [ ] Spec matched by plan
- [ ] Tests identified
- [ ] Assumptions documented
- [ ] Configs validated or updated
- [ ] Paper-to-code mapping updated
- [ ] Artifacts handled per lifecycle rules
- [ ] Review and merge gate satisfied
