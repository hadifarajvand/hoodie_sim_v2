# Data Model: User-Approved Assumption Patch Registry

## AssumptionRegistryEntry
- **Purpose**: Stores one candidate item and its user-approved assumption state.
- **Fields**:
  - `item_id`: Stable identifier for the unresolved paper-gap item.
  - `paper_status`: Feature 030 paper classification, preserved verbatim.
  - `paper_confidence`: Paper evidence confidence from Feature 030.
  - `assumption_status`: `proposed`, `approved`, `rejected`, or `blocked_no_assumption`.
  - `proposed_value`: Suggested assumption value or rule, or empty when blocked.
  - `value_type`: Value category such as numeric, categorical, structural, or rule.
  - `runtime_use_allowed`: Boolean gate for downstream use.
  - `approval_required`: Boolean indicating whether a user decision is still needed.
  - `approval_source`: Where the approval or proposal came from.
  - `rationale`: Why the item is blocked or why the assumption is reasonable.
  - `scientific_risk`: What could be invalidated if the assumption is wrong.
  - `affected_runtime_components`: Which runtime areas would consume the assumption if approved.
  - `validation_plan`: How the assumption would be checked later.
  - `no_paper_recovery_claim`: Must always be `true`.

## AssumptionPatchReport
- **Purpose**: Deterministic audit artifact that summarizes all registry entries.
- **Fields**:
  - `feature_id`
  - `schema_version`
  - `source_gates`
  - `registry_path`
  - `item_count`
  - `status_counts`
  - `runtime_usable_items`
  - `proposed_items`
  - `blocked_items`
  - `rejected_items`
  - `entries`
  - `no_paper_recovery_claims`
  - `no_runtime_behavior_change`
  - `no_training_or_policy_drift`
  - `no_dependency_drift`
  - `final_verdict`

## Relationships
- One report contains many registry entries.
- Each entry maps to exactly one Feature 030 item.
- Approved entries may later be consumed by runtime-config features, but only if a later approved implementation explicitly does so.

## Validation Rules
- Every in-scope candidate must appear exactly once.
- `runtime_use_allowed` can be true only when `assumption_status = approved`.
- `no_paper_recovery_claim` must always be true.
- The registry must preserve the original `paper_status` unchanged.
