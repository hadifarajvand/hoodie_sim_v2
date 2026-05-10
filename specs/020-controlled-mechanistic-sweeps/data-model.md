# Data Model: Controlled Mechanistic Sweeps

## Entities

### Sweep Definition
- **Purpose**: Describes one tiny deterministic parameter family to be swept.
- **Attributes**:
  - `name`: Stable sweep family name.
  - `parameter`: Controlled mechanism dimension.
  - `values`: Tiny ordered set of three values.
  - `fixed_seeds`: Seed list used for repeatability.
  - `expected_direction`: Qualitative monotonic expectation.
  - `control_source`: Public configuration or environment hook used, or `unsupported`.

### Fixed Input Set
- **Purpose**: Records the exact inputs used for a sweep run.
- **Attributes**:
  - `seed`
  - `parameter_value`
  - `trace_identifier`
  - `control_notes`

### Sweep Observation
- **Purpose**: Captures one observed outcome for one sweep input.
- **Attributes**:
  - `seed`
  - `parameter_value`
  - `observed_pressure_indicator`
  - `observed_outcome_summary`
  - `evidence_available`

### Monotonic Check
- **Purpose**: Evaluates the qualitative direction of the sweep results.
- **Attributes**:
  - `sweep_name`
  - `status`
  - `support_level`
  - `rationale`

### Sweep Report
- **Purpose**: The final JSON and Markdown summary artifact.
- **Attributes**:
  - `metadata`
  - `sweep_definitions`
  - `fixed_inputs`
  - `observations`
  - `monotonic_checks`
  - `warnings`
  - `instrumentation_gaps`
  - `limitations`
  - `no_campaign_rerun_disclaimer`
  - `no_paper_validity_disclaimer`
  - `reproducibility`
  - `overall_status`

## Relationships

- Each `Sweep Definition` has many `Fixed Input Set` entries.
- Each `Fixed Input Set` produces one or more `Sweep Observation` entries.
- Each `Monotonic Check` summarizes a single `Sweep Definition`.
- The `Sweep Report` aggregates all definitions, observations, checks, warnings, and limitations.

## Validation Rules

- Sweep values must remain tiny and deterministic.
- A sweep dimension without a public control source must be recorded as unsupported, inconclusive, or instrumentation_gap.
- The report must preserve fixed seeds and deterministic ordering.
- No report field may imply paper-validity or reproduction completeness.
