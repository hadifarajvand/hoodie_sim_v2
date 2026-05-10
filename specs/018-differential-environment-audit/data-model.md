# Data Model: Differential Environment Audit

## Entities

### ToyCase

- **Purpose**: Declarative, deterministic input scenario used for both the reference kernel and the current environment.
- **Fields**:
  - `case_id`: stable identifier
  - `scenario_type`: local compute, horizontal offload, vertical offload, timeout/drop, delayed reward timing, or deterministic ordering
  - `task`: deterministic toy task description
  - `action`: deterministic toy action description
  - `timeout_slot`: terminal boundary for timeout-oriented cases
  - `expected_comparison_context`: optional expected comparison notes
- **Validation Rules**:
  - Stable field ordering must be preserved in serialized reports.
  - The same case fixture must drive both sides of the audit.

### ReferenceLedgerSummary

- **Purpose**: Compact summary of the Feature 017 reference kernel’s observed lifecycle for one toy case.
- **Fields**:
  - `case_id`
  - `event_sequence`
  - `terminal_status`
  - `reward_timing`
- **Relationships**: One per toy case.
- **Validation Rules**:
  - Must be derived from the reference kernel’s deterministic ledger.

### EnvironmentLifecycleSummary

- **Purpose**: Compact summary of the current environment’s observed lifecycle for one toy case.
- **Fields**:
  - `case_id`
  - `event_sequence`
  - `terminal_status`
  - `reward_timing`
  - `observation_source`
- **Relationships**: One per toy case.
- **Validation Rules**:
  - Must be derived only from the public environment interface.
  - If exact hand-fed trace injection is unavailable, the summary may be partial and must be classified accordingly.

### ComparisonResult

- **Purpose**: Per-case comparison result that records how the two summaries relate.
- **Fields**:
  - `case_id`
  - `classification`
  - `finding_cause`
  - `reference_summary`
  - `environment_summary`
  - `notes`
- **Validation Rules**:
  - Classification must be one of the allowed comparison labels.
  - Finding cause must be one of the allowed root-cause labels.

### Finding

- **Purpose**: Structured explanation of a difference, gap, or match implication.
- **Fields**:
  - `finding_id`
  - `case_id`
  - `classification`
  - `cause`
  - `evidence`
  - `notes`
- **Validation Rules**:
  - Findings must distinguish assumptions, divergences, unsupported traces, and scope differences.

### AuditReport

- **Purpose**: Deterministic top-level artifact containing the full audit output.
- **Fields**:
  - `metadata`
  - `toy_cases`
  - `reference_summary`
  - `environment_summary`
  - `comparison_results`
  - `findings`
  - `assumptions`
  - `instrumentation_gaps`
  - `unsupported_cases`
  - `no_fix_disclaimer`
  - `reproducibility`
  - `overall_status`
- **Validation Rules**:
  - Output ordering must be deterministic.
  - The JSON schema must be stable enough for direct test assertions.

### ReproducibilityRecord

- **Purpose**: Metadata needed to reproduce the audit.
- **Fields**:
  - `feature_id`
  - `generated_by`
  - `deterministic`
  - `source_refs`
  - `output_paths`
  - `execution_environment`
- **Validation Rules**:
  - Must record the approved interpreter path.
  - Must record the source reference set used by the audit.

## State / Flow

1. Define toy cases as stable declarative fixtures.
2. Run each case through the reference kernel and current environment.
3. Collect lifecycle summaries.
4. Compare summaries and classify results.
5. Emit deterministic JSON and Markdown reports.

## Determinism Rules

- Case order must be fixed.
- Report section order must be fixed.
- Comparison labels must be stable for identical inputs.
- Unsupported or partial environment observations must never be silently normalized into matches.

