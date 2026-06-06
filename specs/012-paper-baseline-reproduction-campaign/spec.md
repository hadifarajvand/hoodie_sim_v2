# Feature Specification: Paper Baseline Reproduction Campaign

**Feature Branch**: `012-paper-baseline-reproduction-campaign`  
**Created**: 2026-05-06  
**Status**: Draft  
**Input**: User description: "Execute reproducible multi-policy baseline campaigns across paper-backed traffic scenarios and generate audited campaign-level artifacts suitable for reproduction validation."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Run a full reproduction campaign (Priority: P1)

As a reviewer, I want to run a campaign across the implemented policies, scenarios, and seeds so I can reproduce the baseline comparison set in one place.

**Why this priority**: The campaign is the primary workflow. Without it, the matrix and bundle features remain isolated building blocks rather than a reproducible campaign.

**Independent Test**: Given a valid campaign configuration, the runner executes the approved policies and scenarios and produces campaign-level artifacts plus the underlying matrix and bundle outputs.

**Acceptance Scenarios**:

1. **Given** a campaign config with approved policies, scenarios, and seeds, **When** the campaign runs, **Then** it executes the shared matrix workflow and records campaign artifacts.
2. **Given** the same config and deterministic timestamp override, **When** the campaign runs twice, **Then** it produces identical campaign artifact payloads.

---

### User Story 2 - Audit campaign outputs (Priority: P2)

As a maintainer, I want grouped summaries and determinism checks so I can verify the campaign output set without inspecting raw execution details.

**Why this priority**: Campaign reproduction is only useful if the output set is auditable and deterministic.

**Independent Test**: Given campaign outputs, grouped summaries and determinism checks can be validated without re-running the full simulator.

**Acceptance Scenarios**:

1. **Given** campaign results, **When** the runner builds grouped summaries, **Then** it writes per-policy and per-scenario summaries with existing metrics only.
2. **Given** two campaign runs with the same deterministic override, **When** determinism is checked, **Then** the campaign artifacts match.

---

### User Story 3 - Package campaign reproduction outputs (Priority: P3)

As a reviewer, I want the campaign to reference the reproducibility bundle so I can inspect audit-ready outputs alongside campaign summaries.

**Why this priority**: The campaign must be aligned with the bundle packaging workflow to remain reviewable and reproducible.

**Independent Test**: Given campaign output directories, the campaign references or triggers the reproducibility bundle and records that reference in its artifacts.

**Acceptance Scenarios**:

1. **Given** a completed matrix output directory, **When** the campaign finalizes, **Then** it records the reproducibility bundle output location or reference.
2. **Given** missing or failed runs, **When** validation runs, **Then** the campaign reports discovered and expected run counts rather than hiding gaps.

### Edge Cases

- What happens when a campaign includes unsupported policy or scenario names?
- How does the campaign report missing or failed runs?
- What happens when the deterministic timestamp override is omitted?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST accept a campaign configuration containing campaign name, policy names, scenario names, seeds, output directory, episode-length override, deterministic timestamp override, and dependency-change note.
- **FR-002**: The campaign runner MUST execute the existing evaluation matrix workflow rather than reimplementing environment stepping.
- **FR-003**: The campaign MUST generate campaign artifacts including `campaign-manifest.json`, `campaign-summary.json`, `policy-summary.json`, `scenario-summary.json`, `determinism-check.json`, and `README.md`.
- **FR-004**: The campaign MUST reference or invoke the reproducibility bundle workflow after matrix outputs exist.
- **FR-005**: The campaign summary MUST aggregate existing matrix metrics only: average delay, drop ratio, throughput, completed tasks, dropped tasks, and total tasks.
- **FR-006**: The campaign MUST provide grouped summaries by policy name and by scenario name.
- **FR-007**: The campaign MUST support determinism verification by repeating the same configuration and comparing artifact payloads or hashes.
- **FR-008**: The campaign MUST reject unsupported policy and scenario names through the existing approved registries.
- **FR-009**: The campaign outputs MUST be deterministic when a deterministic timestamp override is supplied.
- **FR-010**: The campaign MUST record expected run count, discovered run count, and validation/determinism status when runs are missing or fail.

### Key Entities *(include if feature involves data)*

- **CampaignConfig**: The configuration for a single campaign, including the campaign name, inputs, output directory, and determinism settings.
- **CampaignRunResult**: The packaged result of a campaign execution, including matrix, bundle, and campaign artifact locations.
- **Campaign Manifest**: The campaign-level inventory and provenance record.
- **Campaign Summary**: The campaign-level aggregate metrics artifact.
- **Policy Summary**: The per-policy aggregate artifact.
- **Scenario Summary**: The per-scenario aggregate artifact.
- **Determinism Check**: The artifact that records repeated-run comparison results.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A valid campaign configuration can run all in-scope policies across all in-scope scenarios with fixed seeds.
- **SC-002**: 100% of campaign runs emit the required campaign artifacts.
- **SC-003**: Re-running the same campaign with the same deterministic override produces identical campaign artifact payloads.
- **SC-004**: Campaign outputs clearly report expected runs, discovered runs, and determinism status.
- **SC-005**: Reviewers can inspect policy, scenario, matrix, and bundle results without reading source code.

## Assumptions

- The matrix runner and reproducibility bundle workflows already exist and are available for the campaign to call.
- Existing policy registries remain the source of truth for approved policy names.
- Missing or failed runs are reported explicitly rather than being auto-suppressed.
- Campaign output directories are separate from the underlying matrix output and bundle output directories.
- No campaign-level plotting or statistical analysis is introduced.

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
- [x] Config schema
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
