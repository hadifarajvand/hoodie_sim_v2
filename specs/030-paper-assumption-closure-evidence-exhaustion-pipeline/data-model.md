# Data Model: Paper Assumption Closure and Evidence Exhaustion Pipeline

## EvidenceItem
- **Purpose**: Represents one paper-related uncovered, assumption-backed, or unresolved topic.
- **Fields**:
  - `item_id`: Stable identifier for the evidence item.
  - `domain`: One of `topology`, `connectivity`, `compute capacity`, `link/data rate`, `timeout/deadline`, `reward aggregation`, `equation formatting`, `runtime assumption`, `other`.
  - `title`: Short human-readable label.
  - `description`: What the item represents.
  - `status`: Final status from the approved vocabulary.
  - `confidence`: `high`, `medium`, `low`, or `invalid`.
  - `runtime_approval_required`: Boolean flag for assumption-backed items.

## EvidenceRecord
- **Purpose**: Captures how a specific item was sourced and interpreted.
- **Fields**:
  - `source_type`: OCR, registry, JSON artifact, table extraction, equation extraction, visual PDF inspection, cross-artifact consistency check, or manual review.
  - `source_reference`: File path, page, offset, table, or equation reference.
  - `raw_evidence`: Original excerpt or structured snippet.
  - `normalized_finding`: Canonical interpretation.
  - `confidence`: Evidence strength.
  - `contradiction_notes`: Optional contradiction details.

## ReportSummary
- **Purpose**: Compact aggregate of the final evidence inventory.
- **Fields**:
  - `total_items`
  - `by_status`
  - `by_confidence`
  - `manual_review_count`
  - `approval_required_count`
  - `unrecoverable_count`

## ReportArtifact
- **Purpose**: Generated JSON and Markdown outputs.
- **Fields**:
  - `feature_id`
  - `schema_version`
  - `source_gates`
  - `inventory_summary`
  - `items`
  - `recovered_items`
  - `partially_recovered_items`
  - `contradicted_items`
  - `assumption_backed_items`
  - `unrecoverable_after_evidence_exhaustion_items`
  - `out_of_scope_items`
  - `manual_review_required_items`
  - `runtime_dependency_decisions`
  - `no_training_or_policy_drift`
  - `no_dependency_drift`
  - `final_verdict`

## Relationships
- Each `EvidenceItem` has one final status and may have multiple `EvidenceRecord` entries.
- A `ReportArtifact` contains an ordered inventory of `EvidenceItem` entries and derived summary counts.

## Validation Rules
- Each item must resolve to exactly one final status.
- Manual Figure 7 review must store confidence per edge, not just for the whole graph.
- Report structure must remain deterministic for identical inputs.

