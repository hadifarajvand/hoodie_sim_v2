# Feature Specification: 009-paper-backed-evaluation-matrix

**Feature Branch**: `009-paper-backed-evaluation-matrix`  
**Created**: 2026-05-06  
**Status**: Draft  
**Input**: User description: "Paper-Backed Evaluation Matrix"

## Clarifications

### Session 2026-05-06

- Q: Does this train HOODIE? → A: No. This feature only evaluates implemented policies.
- Q: Does this reproduce paper plots? → A: No. It creates auditable JSON/CSV result artifacts only.
- Q: Does this alter metric formulas? → A: No. Use existing evaluation metrics only.
- Q: Does each policy get a special environment path? → A: No. Every policy must use the same HoodieGymEnvironment reset/step loop.
- Q: Are unsupported policies/scenarios allowed as aliases? → A: No. Reject unsupported names explicitly.
- Q: Is parallel execution required? → A: No. Deterministic serial execution first.
- Q: Should this use pandas, matplotlib, or external trackers? → A: No. Stdlib only.
- Q: What is the minimum complete version? → A: A config, policy/scenario registry, serial matrix runner, JSON/CSV artifacts, deterministic tests, and docs.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Reproducible Matrix Runs (Priority: P1)

As a simulation user, I want a single runner to execute each implemented policy across each paper-backed traffic scenario and seed so that I can compare results under a shared environment boundary.

**Why this priority**: This is the core value of the feature; without reproducible matrix execution there is no auditable comparison across policies or scenarios.

**Independent Test**: Run the matrix twice with the same configuration and confirm the same policy/scenario/seed combinations produce the same traces and metric records.

**Acceptance Scenarios**:

1. **Given** an approved policy list, scenario list, and seed list, **When** the matrix runner executes, **Then** it produces one result record per policy × scenario × seed combination.
2. **Given** the same matrix configuration and seeds, **When** the matrix runner is run again, **Then** it produces identical run ordering and identical per-run metadata.

---

### User Story 2 - Auditable Metric Artifacts (Priority: P1)

As a simulation user, I want machine-readable result artifacts for each run and aggregate summary outputs so that I can audit the evaluation without relying on manual inspection.

**Why this priority**: Reproducibility is not useful unless results can be inspected and traced after the run completes.

**Independent Test**: Execute a small matrix and verify the runner writes per-run records and an aggregate summary that can be reloaded without ambiguity.

**Acceptance Scenarios**:

1. **Given** a completed matrix run, **When** the output directory is inspected, **Then** it contains machine-readable per-run records and an aggregate summary.
2. **Given** a run record, **When** it is reloaded later, **Then** it preserves the policy, scenario, seed, trace identifier, and config metadata used for the run.

---

### User Story 3 - Strict Scope Enforcement (Priority: P2)

As a simulation maintainer, I want unsupported policy or scenario names rejected so that the matrix stays paper-backed and does not silently expand its scope.

**Why this priority**: The feature must remain bounded to implemented policies and paper-backed traffic scenarios only.

**Independent Test**: Attempt to run the matrix with an unsupported policy or scenario name and verify the request is rejected before any simulation begins.

**Acceptance Scenarios**:

1. **Given** an unknown policy name, **When** the matrix runner validates the configuration, **Then** it rejects the request.
2. **Given** an unknown scenario name, **When** the matrix runner validates the configuration, **Then** it rejects the request.

### Edge Cases

- What happens when the policy list is empty?
- How does the runner behave when the same seed appears more than once?
- What happens when the output directory already contains earlier matrix artifacts?
- How should the runner record configuration values when optional overrides are omitted?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide an evaluation matrix configuration that includes policy names, scenario names, seeds, an optional episode-length override, an output directory, and references to already-supported runtime or compute configuration values.
- **FR-002**: The system MUST provide a policy lookup mechanism limited to implemented policies only.
- **FR-003**: The system MUST provide a scenario lookup mechanism limited to the paper-backed traffic scenarios only.
- **FR-004**: For every policy, scenario, and seed combination, the system MUST generate traffic using the existing traffic generation feature, run through the shared environment reset/step boundary, and collect the existing evaluation metrics.
- **FR-005**: The system MUST write machine-readable per-run result artifacts and, if feasible with standard library support, an aggregate CSV summary.
- **FR-006**: The system MUST include reproducibility metadata for each run record, including policy, scenario, seed, trace identifier, configuration values, and a dependency-change note.
- **FR-007**: The system MUST not change evaluation metric formulas.
- **FR-008**: The matrix runner MUST be deterministic for the same configuration and seed inputs.
- **FR-009**: The system MUST reject unsupported policy names and unsupported scenario names before execution begins.
- **FR-010**: The system MUST not introduce new traffic models, policy-specific environment paths, or lifecycle ownership changes.

### Key Entities *(include if feature involves data)*

- **Evaluation Matrix Config**: The set of policies, scenarios, seeds, output location, and shared runtime/compute configuration references used to define a matrix run.
- **Matrix Run Record**: One auditable result entry for a single policy/scenario/seed combination.
- **Aggregate Summary**: A roll-up of the run records for the full matrix.
- **Policy Registry**: The approved set of policy names that may be executed by the matrix runner.
- **Scenario Registry**: The approved set of paper-backed traffic scenarios that may be executed by the matrix runner.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Running the same matrix configuration twice with the same seeds produces identical run ordering and identical per-run metadata in 100% of tested cases.
- **SC-002**: The matrix runner can execute every approved policy across every approved traffic scenario without requiring a special environment mode in 100% of tested combinations.
- **SC-003**: The matrix runner produces machine-readable per-run artifacts for 100% of completed policy/scenario/seed combinations.
- **SC-004**: Unsupported policy or scenario names are rejected before execution in 100% of validation tests.
- **SC-005**: No dependency files are changed for this feature.

## Assumptions

- The matrix runner is a reproducible evaluation tool, not a training or optimization tool.
- Only policies already implemented in the repository may be included in the matrix.
- Only the paper-backed traffic scenarios already recovered for the repository may be included in the matrix.
- If a commit or ref identifier is unavailable from the local environment, it may be omitted from artifacts rather than invented.
- The runner executes serially first; parallel execution is explicitly out of scope for this feature.
- Standard library output formats are sufficient for this feature; external trackers and plotting libraries are not required.

## Production Constraints

- No new dependencies are added.
- No stochastic or learned decision model is introduced.
- The environment lifecycle owner remains unchanged.
- Policy selection remains external to the environment boundary.

## Public Interfaces Affected

- Evaluation runner interface
- Policy registry
- Traffic scenario selection
- Output artifact schema

## Config / Schema Impact

- Evaluation matrix configuration fields must be validated before execution.
- Unsupported names must fail fast.
- Optional overrides must remain backward compatible.

## Artifact Impact

- Raw metrics
- Validation summaries
- Reports
- Debug traces
- Aggregated CSV summaries

## Security Considerations

- No secrets, tokens, or credentials are introduced.
- No remote execution surfaces are added.
- Output artifacts must remain local and reproducible.

## Definition of Done

- Spec matched by plan
- Tests identified
- Assumptions documented
- Configs validated or updated
- Paper-to-code mapping updated
- Artifacts handled per lifecycle rules
- Review and merge gate satisfied
