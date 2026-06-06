# Feature Specification: Paper Assumption Closure and Evidence Exhaustion Pipeline

**Feature Branch**: `030-paper-assumption-closure-evidence-exhaustion-pipeline`  
**Created**: 2026-05-11  
**Status**: Draft  
**Input**: User description: "Paper Assumption Closure and Evidence Exhaustion Pipeline"


## Clarifications

### Session 2026-05-11
- Q: Inventory source scope → A: Include every artifact named in the feature plus any prior feature reports that contain assumption-backed, unrecoverable, or partially recovered paper items.
- Q: Final status vocabulary → A: Use only `recovered`, `partially_recovered`, `contradicted`, `assumption_backed_requires_user_approval`, `unrecoverable_after_evidence_exhaustion`, and `out_of_scope`.
- Q: Evidence confidence policy → A: Use `high`, `medium`, `low`, and `invalid`; `low` and `invalid` block runtime use unless later explicitly approved.
- Q: Figure 7 manual recovery policy → A: Ambiguous Figure 7 edges are `unrecoverable_after_evidence_exhaustion`; only defensible edges may be recovered with per-edge confidence.
- Q: Output schema → A: Use a single top-level `items` array plus a compact `summary` block.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Exhaust Paper Gaps (Priority: P1)

As a reproduction maintainer, I want every remaining paper-related uncovered item to be inventoried, searched, inspected, and classified so that no future DRL work relies on fabricated or vaguely justified values.

**Why this priority**: This is the core gate for scientific integrity. If uncovered items remain unclassified, later reward, topology, or capacity work can silently drift into invention.

**Independent Test**: The pipeline can be run on the current evidence set and produces a complete item-by-item inventory with a final classification for each item.

**Acceptance Scenarios**:

1. **Given** the HOODIE OCR, recovered registries, and prior analysis artifacts, **When** the evidence-exhaustion pipeline runs, **Then** each known paper-related uncovered item appears in the report with a classification.
2. **Given** a paper item that is still noisy or partially recovered, **When** the pipeline completes, **Then** the report records the raw evidence, the normalized interpretation, and the confidence or recovery status without claiming full recovery if the evidence does not support it.

### User Story 2 - Distinguish Evidence From Assumption (Priority: P2)

As a reproduction maintainer, I want the report to separate recovered, partially recovered, contradicted, assumption-backed, unrecoverable, and out-of-scope items so that approval is required before any assumption-backed value is used at runtime.

**Why this priority**: The next planning steps depend on knowing which values are paper-backed and which still need user approval. A false “recovered” label would invalidate the reproduction.

**Independent Test**: The report can be reviewed independently and each item’s status is explicit, with assumption-backed items clearly marked as requiring approval before use.

**Acceptance Scenarios**:

1. **Given** an item such as a topology edge or CPU capacity that is not fully recoverable, **When** it is classified, **Then** the report states whether it is assumption-backed or unrecoverable and explains why.
2. **Given** an item that is explicitly outside the feature’s scope, **When** the pipeline classifies it, **Then** the report labels it out-of-scope rather than mixing it with paper gaps.

### User Story 3 - Produce Audit-Ready Evidence (Priority: P3)

As a reviewer, I want a deterministic report artifact that summarizes evidence coverage and final classifications so I can decide whether future runtime use is safe.

**Why this priority**: The output is only useful if it is auditable, repeatable, and suitable for review before implementation planning.

**Independent Test**: The pipeline produces the same structured report artifact on repeated runs from the same source inputs.

**Acceptance Scenarios**:

1. **Given** the same source inputs and recovered registries, **When** the pipeline is rerun, **Then** the generated report preserves the same classifications and evidence references.
2. **Given** the report artifact, **When** a reviewer inspects it, **Then** they can identify unresolved risks, required approvals, and evidence exhaustion rationale without reading implementation code.

### Edge Cases

- What happens when OCR yields a noisy equation fragment that cannot be normalized without guessing?
- How does the pipeline treat items that appear in prior artifacts but are not supported by direct paper evidence?
- What happens when the same unresolved item appears in multiple prior reports with conflicting labels?
- How does the pipeline classify items that are recoverable only by manual visual inspection of the paper PDF rather than OCR text?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST inventory every known paper-related uncovered item from the supplied paper OCR, recovered registries, prior analysis artifacts, and any prior feature reports that contain assumption-backed, unrecoverable, or partially recovered paper items.
- **FR-002**: The system MUST classify each inventoried item as recovered, partially_recovered, contradicted, assumption_backed_requires_user_approval, unrecoverable_after_evidence_exhaustion, or out_of_scope.
- **FR-003**: The system MUST record source evidence for each recovered or partially_recovered item, including the source type and the relevant location or offset when available.
- **FR-004**: The system MUST distinguish automatic OCR or registry recovery from manual visual recovery.
- **FR-005**: The system MUST identify whether each assumption_backed_requires_user_approval item requires explicit user approval before runtime use.
- **FR-006**: The system MUST record an evidence-exhaustion rationale for each unrecoverable_after_evidence_exhaustion item.
- **FR-007**: The system MUST preserve source wording when a paper term is ambiguous, noisy, or terminology-specific, instead of silently renaming it.
- **FR-008**: The system MUST treat the following known categories as in-scope for evidence exhaustion: topology adjacency, legal horizontal destinations, edge-cloud connectivity, EA private CPU capacities, EA public CPU capacities, cloud CPU capacity, cloud data-rate constants beyond vertical rate, numeric timeout or deadline values, multi-agent reward reduction order, and noisy public delay-cost equation formatting.
- **FR-009**: The system MUST treat runtime behavior changes as out of scope for this feature unless a later approved implementation feature explicitly uses the recovered evidence.
- **FR-010**: The system MUST generate an auditable report artifact that is deterministic for the same inputs.

### Key Entities *(include if data involved)*

- **Evidence Item**: A paper-related topic or value that may be recovered, partially recovered, assumption-backed, unrecoverable, or out-of-scope.
- **Evidence Record**: A structured entry containing source references, raw evidence, normalized interpretation, confidence, and classification.
- **Assumption Item**: A value that is not paper-backed but may be carried forward only with explicit approval.
- **Unrecoverable Item**: A value for which evidence exhaustion failed to produce a reliable recovery.
- **Report Artifact**: The generated JSON and Markdown outputs summarizing coverage and final classifications.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of known paper-related uncovered items are listed in the report with a final classification.
- **SC-002**: 100% of recovered or partially_recovered items include source references and confidence or recovery status.
- **SC-003**: 100% of assumption_backed_requires_user_approval items explicitly state whether user approval is required before runtime use.
- **SC-004**: 100% of unrecoverable_after_evidence_exhaustion items include an evidence-exhaustion rationale.
- **SC-005**: Re-running the pipeline on unchanged inputs produces identical classifications and report structure.

## Recovery Policy

- Confidence labels are `high`, `medium`, `low`, and `invalid`.
- `high` and `medium` values may be reported, but only `high` values may be used in runtime decisions without extra approval.
- `low` and `invalid` values are report-only until later explicit approval.
- `invalid` guesses must be rejected.
- Manual Figure 7 recovery may only record per-edge confidence. Ambiguous edges are `unrecoverable_after_evidence_exhaustion` and must not be encoded as topology facts.

## Report Schema

The `assumption-closure-report.json` artifact MUST use this shape:

- `summary`: compact totals and counts by status and confidence
- `items`: array of item records, each containing:
  - `item_id`
  - `domain`
  - `status`
  - `confidence`
  - `source_methods`
  - `source_evidence`
  - `normalized_finding`
  - `runtime_approval_required`
  - `evidence_exhaustion_rationale`
  - `manual_visual_recovery`

Each item record MUST preserve per-edge confidence where topology is manually inspected.

## Assumptions

- The feature focuses on evidence exhaustion and classification, not runtime behavior changes.
- Prior analysis artifacts are treated as valid inputs for classification, but not as substitutes for paper evidence.
- Manual visual inspection of the paper PDF is allowed only for recovery classification and documentation, not for inventing values.
- Any value that cannot be justified from paper or artifact evidence remains unrecoverable or assumption-backed.
- Runtime use of assumption-backed items requires explicit approval in a later implementation feature or review step.

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

- Required evidence fields are identified for the closure report.
- Final classification values are constrained to the approved evidence states.
- Backward-compatibility impact is limited to adding a new analysis artifact and optional recovered-item registry.

## Artifact Impact

- [x] Raw metrics
- [ ] Plots
- [x] Reports
- [ ] Checkpoints
- [x] Debug traces
- [x] Validation summaries

## Security Considerations

- Secrets / tokens / credentials reviewed: not applicable to this feature.
- Remote code execution reviewed: no executable runtime changes are intended.
- External references documented: paper OCR, recovered registries, and prior analysis artifacts are the only sources.

## Definition of Done

- [x] Spec matched by plan
- [x] Tests identified
- [x] Assumptions documented
- [x] Configs validated or updated
- [x] Paper-to-code mapping updated
- [x] Artifacts handled per lifecycle rules
- [x] Review and merge gate satisfied
