# Feature Specification: Paper Mechanism Registry

**Feature Branch**: `[016-paper-mechanism-registry]`  
**Created**: 2026-05-09  
**Status**: Draft  
**Input**: User description: "Paper Mechanism Registry"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Read the Mechanism Registry (Priority: P1)

As a reviewer, I want a read-only registry of the paper's mechanisms so I can see which mechanisms are documented by the paper, which are only partially documented, and which remain missing or ambiguous.

**Why this priority**: The registry is the feature's core deliverable. Without it, there is no source-of-truth view of the paper's mechanism claims and gaps.

**Independent Test**: Run the registry builder against the committed OCR sources and verify that every required mechanism category appears with a status, evidence, and gap summary.

**Acceptance Scenarios**:

1. **Given** the paper OCR source is available, **When** the registry is generated, **Then** it includes all required mechanism categories with status and OCR evidence or explicit missing markers.
2. **Given** a mechanism is not supported by explicit OCR evidence, **When** the registry is generated, **Then** the mechanism is marked missing, ambiguous, or assumption-backed rather than invented.

---

### User Story 2 - Trace Claims to Evidence (Priority: P2)

As a reviewer, I want every mechanism claim to point back to paper evidence so I can verify that the registry reflects the paper text rather than a guessed interpretation.

**Why this priority**: The registry is only useful if it preserves traceability to OCR snippets and section references.

**Independent Test**: Inspect the generated registry and confirm each mechanism entry contains OCR evidence metadata, including source path and deterministic snippet location.

**Acceptance Scenarios**:

1. **Given** a mechanism is documented in the paper, **When** the registry is generated, **Then** its entry includes OCR evidence and the relevant paper reference context.
2. **Given** a paper detail is ambiguous or incomplete, **When** the registry is generated, **Then** the gap is called out explicitly instead of being resolved silently.

---

### User Story 3 - Separate Paper Facts From Project Mapping (Priority: P3)

As a reviewer, I want the registry to distinguish paper facts from current project mapping so I can see what is established by the paper and what is only a project-side hypothesis.

**Why this priority**: The next features depend on a clear boundary between paper-documented mechanisms and implementation gaps.

**Independent Test**: Verify that each entry includes a current project mapping field and a next-action field that separates keep, inspect, recover, and assumption decisions.

**Acceptance Scenarios**:

1. **Given** a mechanism is mapped to a known project module, **When** the registry is generated, **Then** that mapping is labeled as project mapping and not as paper evidence.
2. **Given** learned HOODIE training mechanics are not supported by committed implementation evidence, **When** the registry is generated, **Then** they remain marked as unknown or not implemented.

---

### Edge Cases

- What happens when the OCR source is present but a mechanism category has no explicit section or equation reference?
- What happens when topology adjacency is discussed only conceptually and no structured topology artifact exists?
- What happens when training, LSTM, or reward-timing details are mentioned in the paper but no implementation artifact proves they exist in the repository?
- What happens when optional supporting analysis artifacts are missing?
- What happens when paper and repository terminology differ for the same mechanism?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The feature MUST generate a read-only registry of paper mechanisms without changing simulator behavior, environment lifecycle behavior, policy behavior, metric formulas, training behavior, or artifact contents.
- **FR-002**: The registry MUST include entries for all required mechanism categories: system topology, edge agents and cloud, action space, local computation, horizontal offloading, vertical offloading, private queue, public queue, task arrival process, task size distribution, processing density, CPU capacity, link data rates, transmission delay, computation delay, timeout and drop, reward definition, state representation, load forecasting or LSTM input, DQN/Double/Dueling/LSTM training, training episode protocol, validation episode protocol, baseline policy definitions, evaluation metrics, and figure result requirements.
- **FR-003**: Every mechanism entry MUST include mechanism identifier, category, paper status, implementation status, assumption risk, OCR evidence, expected mechanism behavior, current project mapping, missing details, implementation gaps, validation implications, and next action.
- **FR-004**: Every paper-derived mechanism claim MUST include OCR evidence from `resources/papers/hoodie/ocr/merged.tex` or be explicitly marked missing or ambiguous.
- **FR-005**: The registry MUST preserve deterministic evidence references, including source path, section or context, recoverable equation/table reference when present, figure reference when relevant, deterministic snippet index or character offset, and OCR snippet text.
- **FR-006**: The registry MUST distinguish paper-documented mechanisms from implementation gaps so paper facts cannot be mistaken for runtime guarantees.
- **FR-007**: The registry MUST mark topology adjacency as missing or blocking unless a structured topology artifact explicitly provides it.
- **FR-008**: The registry MUST mark learned HOODIE training mechanics as unknown, not implemented, or partially implemented unless committed evidence proves otherwise.
- **FR-009**: The registry MUST treat reward timing and delayed reward behavior as high-impact mechanism areas.
- **FR-010**: The registry MUST treat timeout and drop behavior as high-impact mechanism areas.
- **FR-011**: The registry MUST treat CPU and link-rate unit mapping as high-risk whenever paper units or conversions remain incomplete or assumption-backed.
- **FR-012**: The feature MUST read the committed OCR source as the source of truth and MAY use supporting OCR siblings or analysis artifacts only as secondary evidence, never as a substitute for paper text.
- **FR-013**: The feature MUST write `paper-mechanism-registry.json` and `paper-mechanism-registry.md` only to a caller-provided analysis output directory.
- **FR-014**: The registry output MUST include a read-only statement and MUST NOT claim paper reproduction validity.
- **FR-015**: The feature MUST be deterministic so repeated runs on the same inputs produce byte-identical outputs.
- **FR-016**: The feature MUST explicitly mark missing or ambiguous details rather than inventing unsupported mechanism semantics.

### Key Entities *(include if feature involves data)*

- **Mechanism Entry**: A single paper mechanism record with paper status, implementation status, evidence, risk, gaps, and next action.
- **Mechanism Evidence**: A deterministic OCR-derived evidence record tied to a source path and snippet location.
- **Registry Report**: The complete output document containing the inventory, mechanism entries, blocking gaps, and high-risk assumptions.
- **Project Mapping**: A current repository-side mapping for a mechanism, labeled as mapping rather than paper evidence.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The registry includes all 25 required mechanism categories in a single generated report.
- **SC-002**: Every mechanism entry contains at least one OCR evidence snippet or an explicit missing designation.
- **SC-003**: The report identifies topology adjacency as missing unless structured topology evidence is available.
- **SC-004**: The report flags learned HOODIE training mechanics as unknown, not implemented, or partially implemented unless committed evidence proves otherwise.
- **SC-005**: The report clearly separates paper-documented mechanisms from implementation gaps in every entry.
- **SC-006**: Repeated runs on unchanged inputs produce byte-identical JSON and Markdown outputs.
- **SC-007**: Existing paper and campaign artifacts remain unchanged after registry generation.
- **SC-008**: The registry states that it is read-only and does not validate paper reproduction.

## Assumptions

- The OCR file is the authoritative paper-text source for mechanism claims when it contains explicit evidence.
- If supporting OCR siblings or analysis artifacts disagree with the OCR text, the OCR text takes precedence for paper evidence.
- Missing or ambiguous details are better preserved as gaps than force-fit into false certainty.
- The registry is a precursor to later mechanism analysis, reference-kernel work, and differential auditing, not a substitute for them.

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
