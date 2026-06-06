# Feature Specification: Structured Paper Topology and Link-Rate Registry

**Feature Branch**: `[025-structured-paper-topology-linkrate-registry]`  
**Created**: 2026-05-10  
**Status**: Draft  
**Input**: User description: "Feature 025 — Structured Paper Topology and Link-Rate Registry."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Recover Paper Topology Evidence (Priority: P1)

A maintainer wants a frozen, structured topology registry that captures only what the HOODIE paper and its OCR/PDF evidence can support, so later work can reference a stable source instead of re-reading the paper manually.

**Why this priority**: Topology is the foundation for all later parameter recovery. If it is not structured and evidence-backed, downstream registries cannot be trusted.

**Independent Test**: Can be independently verified by inspecting the frozen topology registry and confirming either the full Figure 7 topology is recovered with cited sources for every edge and adjacency, or the entire topology artifact is marked unrecoverable with no fabricated edges.

**Acceptance Scenarios**:

1. **Given** the HOODIE paper resources are available, **When** topology evidence is recovered, **Then** the registry records Figure 7, the N=20 edge-agent structure, and any recoverable adjacency/connectivity facts with provenance only if the full Figure 7 topology can be reconstructed without gaps.
2. **Given** any Figure 7 topology detail cannot be supported by paper evidence, **When** the registry is produced, **Then** the topology artifact is marked unrecoverable rather than partially recovered or inferred.

### User Story 2 - Recover Parameter Registry With Provenance (Priority: P2)

A maintainer wants a frozen parameter registry that captures paper-backed link-rate, CPU-capacity, and scenario parameters with evidence for each value, so the project can reuse structured values without inventing missing ones.

**Why this priority**: Link rates and CPU/scenario parameters are needed for reproducible paper recovery, but they must remain evidence-bound and may depend on how much topology could be recovered.

**Independent Test**: Can be independently verified by inspecting the frozen parameter registry and confirming each value includes a source reference, recovery status, and any caveat needed to show it was not fabricated.

**Acceptance Scenarios**:

1. **Given** paper/OCR/PDF evidence contains a parameter value, **When** the registry is produced, **Then** the value is stored with provenance and marked recovered.
2. **Given** paper/OCR/PDF evidence does not support a parameter value, **When** the registry is produced, **Then** the value is explicitly marked unrecoverable or partially recovered.

### User Story 3 - Produce Frozen Recovery Reports (Priority: P3)

A maintainer wants deterministic report artifacts that summarize what was recovered, what could not be recovered, and why, so the recovery process is auditable and repeatable.

**Why this priority**: The registry artifacts are only useful if the recovery outcome is also summarized in a stable analysis report.

**Independent Test**: Can be independently verified by regenerating the report artifacts and confirming deterministic JSON ordering, schema versioning, and evidence fields are present for every recovered item.

**Acceptance Scenarios**:

1. **Given** the recovery has been run, **When** the report artifacts are written, **Then** both JSON and Markdown reports exist and summarize recovered, partially recovered, and unrecoverable items.
2. **Given** the same source evidence is used again, **When** the recovery artifacts are regenerated, **Then** the outputs remain deterministic and preserve the same evidence-backed conclusions.

### Edge Cases

- What happens when Figure 7 topology edges cannot be reliably recovered? The artifact must mark them unrecoverable rather than inventing edges.
- How are partially legible values handled? The artifact must preserve the legible portion, record the limitation, and mark the item partially recovered if appropriate for parameter values, but not for the Figure 7 topology artifact.
- What happens when an expected value appears in multiple sources with minor formatting differences? The registry must record the canonical recovered value and cite the source evidence used.
- What happens when no paper evidence supports a claimed CPU or link-rate value? The registry must leave it unrecoverable.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST produce a frozen structured topology registry for the HOODIE paper only when the full Figure 7 topology can be recovered without gaps; otherwise the topology artifact MUST be marked unrecoverable.
- **FR-002**: The system MUST not invent topology edges, adjacency entries, connectivity statements, link-rate values, CPU capacities, or scenario parameters when paper evidence is missing or ambiguous.
- **FR-003**: The system MUST produce a frozen structured parameter registry covering paper-backed horizontal data-rate values, vertical data-rate values, CPU capacities for EA private/public/cloud processing when recoverable, and scenario parameters required for paper-level experiments.
- **FR-004**: The system MUST attach source evidence to every recovered registry item and MUST record a recovery status for each item, including recovered, partially_recovered, or unrecoverable.
- **FR-005**: The system MUST preserve deterministic JSON ordering in the frozen registry artifacts.
- **FR-006**: The system MUST write the frozen topology registry to `resources/papers/hoodie/recovered/topology-g.json` and the frozen parameter registry to `resources/papers/hoodie/recovered/paper-parameter-registry.json`.
- **FR-007**: The system MUST write an analysis report to `artifacts/analysis/structured-paper-topology-linkrate-registry/topology-recovery-report.json` and `artifacts/analysis/structured-paper-topology-linkrate-registry/topology-recovery-report.md`.
- **FR-008**: The system MUST explicitly mark items as unrecoverable or partially recovered when the paper/OCR/PDF resources do not support a reliable reconstruction, except that the topology artifact MUST not be partially recovered if Figure 7 cannot be fully reconstructed.
- **FR-009**: The system MUST preserve read-only paper recovery behavior and MUST not mutate simulator behavior, environment behavior, policy behavior, metric behavior, training behavior, or campaign artifacts.
- **FR-010**: The system MUST provide provenance or evidence metadata for every recovered value so later features can trace each registry entry back to paper sources.

### Key Entities *(include if feature involves data)*

- **Topology Registry**: A frozen structured record of paper-backed topology facts, adjacency, and connectivity evidence.
- **Parameter Registry**: A frozen structured record of paper-backed link-rate, CPU-capacity, and scenario parameters with provenance.
- **Recovery Item**: A single recovered, partially recovered, or unrecoverable fact with evidence, status, and canonical value if available.
- **Evidence Source**: A paper, OCR, or PDF reference used to support a recovered item.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The repository contains the frozen topology registry and parameter registry artifacts at the required paths after recovery.
- **SC-002**: 100% of recovered registry items include provenance or evidence metadata and a recovery status.
- **SC-003**: 100% of unsupported items are explicitly marked unrecoverable or partially recovered rather than inferred.
- **SC-004**: A reviewer can determine within 2 minutes which paper-backed topology and parameter facts were recovered and which remain missing.
- **SC-005**: Regenerating the artifacts with the same source evidence produces deterministic JSON output ordering and the same recovery conclusions.

## Assumptions

- The HOODIE paper, OCR, and related PDF resources are the only acceptable sources of truth for this feature.
- Some topology edges, rates, or scenario parameters may not be recoverable with sufficient confidence.
- When evidence is insufficient, explicit unrecoverable classification is preferable to conjecture.
- The feature is diagnostic and archival only; it does not authorize simulator or paper-validity changes.

## Production Constraints

- [x] Performance budgets identified
- [x] Artifact handling rules identified
- [x] Security and secret-hygiene constraints identified
- [x] CI quality gate impact identified

## Public Interfaces Affected

- [ ] Environment reset/step
- [ ] Policy interface
- [ ] Task model
- [x] Topology interface
- [x] Runtime model interface
- [ ] Evaluation metric interface
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
- [ ] Debug traces
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
