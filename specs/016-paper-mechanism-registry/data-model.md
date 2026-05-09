# Data Model: Paper Mechanism Registry

## MechanismEvidence

### Purpose
Represents one OCR-derived paper evidence record for a mechanism claim.

### Fields
- `source_path`: Absolute or project-relative source path to the OCR file.
- `section_or_context`: Paper section name or local context label.
- `equation_or_table_reference`: Optional equation, table, or section reference when recoverable.
- `figure_reference`: Optional figure reference when relevant.
- `snippet_index`: Deterministic snippet number or character offset.
- `ocr_snippet`: Exact text snippet used as evidence.

### Validation Rules
- Must be present for every mechanism claim unless the mechanism is explicitly marked missing or ambiguous.
- Must not include synthesized or inferred numeric values.

## MechanismEntry

### Purpose
Represents one registry row for a paper mechanism category.

### Fields
- `mechanism_id`
- `mechanism_name`
- `category`
- `paper_status`
- `implementation_status`
- `assumption_risk`
- `paper_evidence` : array of `MechanismEvidence`
- `expected_mechanism_behavior`
- `current_project_mapping`
- `missing_details`
- `implementation_gaps`
- `validation_implications`
- `next_action`

### Validation Rules
- `paper_status` must be one of `documented`, `partially_documented`, `ambiguous`, `missing`.
- `implementation_status` must be one of `implemented`, `partially_implemented`, `assumption_backed`, `not_implemented`, `unknown`.
- `assumption_risk` must be one of `none`, `low`, `medium`, `high`, `blocking`.
- `next_action` must be one of `keep`, `inspect_source`, `recover_from_paper`, `document_assumption`, `requires_reference_kernel`, `requires_user_decision`.
- `current_project_mapping` must be labeled as project mapping, not paper evidence.

## MechanismRegistryReport

### Purpose
Top-level output containing the entire registry and summary findings.

### Fields
- `input_sources`
- `registry_version`
- `read_only`
- `behavior_changes`
- `mechanism_entries`
- `blocking_gaps`
- `high_risk_assumptions`
- `implementation_gap_summary`
- `next_recommended_feature`
- `passed`

### Validation Rules
- `read_only` must be `true`.
- `behavior_changes` must be `false`.
- Output order must be deterministic.
- The registry must include all 25 required mechanism categories.

## ProjectMapping

### Purpose
Represents a repository-side interpretation of where a mechanism may be reflected in the codebase.

### Fields
- `module_paths`
- `mapping_confidence`
- `notes`

### Validation Rules
- May be present only when confidently mapped.
- Must never be treated as paper evidence.
