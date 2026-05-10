# Data Model: Mechanism Repair

## Entities

### Confirmed Divergence
- **Purpose**: Represents a committed audit finding that is eligible for repair.
- **Fields**:
  - `case_id`: Stable identifier from the Feature 018 audit.
  - `classification`: Expected to be `divergence` for the repaired case.
  - `cause`: Expected to be `likely_environment_bug`.
  - `reference_terminal_status`: Reference terminal result for the case.
  - `environment_terminal_status`: Observed environment terminal result.
  - `evidence`: Human-readable evidence string from the audit.

### Repair Target
- **Purpose**: The exact behavior allowed to change in this feature.
- **Fields**:
  - `name`: `timeout/drop terminal accounting`
  - `scope`: Public environment adapter boundary
  - `allowed_effect`: Change terminal accounting so timeout/drop finalization is reflected correctly

### Regression Test Case
- **Purpose**: Reproduces the divergence before repair and verifies the fix after repair.
- **Fields**:
  - `scenario_name`: Timeout/drop public `step` lifecycle
  - `initial_state`: Minimal environment setup needed for the case
  - `expected_terminal_outcome`: `dropped` or project-equivalent drop status
  - `expected_reward_timing`: Reward emitted only at terminal finalization

### Non-Repair Finding
- **Purpose**: A Feature 018 audit result that remains outside repair scope.
- **Fields**:
  - `case_id`
  - `classification`
  - `cause`
  - `status`: unrepaired

### Repair Summary
- **Purpose**: Optional artifact summarizing the exact divergence fixed and remaining unrepaired findings.
- **Fields**:
  - `repaired_case_id`
  - `repaired_behavior`
  - `regression_tests`
  - `remaining_findings`
  - `audit_regeneration_status`

## Relationships

- A `Confirmed Divergence` maps to one `Repair Target`.
- One `Regression Test Case` must exist for the confirmed repaired divergence.
- `Non-Repair Finding` entries are preserved in the regenerated audit and the repair summary.

## Validation Rules

- The repaired case must be the only confirmed repair target unless a new audit artifact proves another divergence.
- Regression tests must verify both terminal outcome and delayed reward behavior.
- Metrics remain unchanged unless a metric bug is separately proven, which is not part of this feature.
