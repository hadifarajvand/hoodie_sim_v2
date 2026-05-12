# Data Model: User-Approved Assumption Patch Registry

## GovernanceDocsChange

- **Purpose**: Represents the narrow governance/docs reconciliation included in Feature 031.
- **Fields**:
  - `constitution_version`: The version number shown in both the sync report and footer.
  - `approved_interpreter_path`: The interpreter path that the governance docs must reference consistently.
  - `scope`: Must remain limited to patch-level governance cleanup.
  - `changed_files`: The documentation files intentionally updated by the reconciliation.
  - `runtime_adoption_allowed`: Must remain `false` for Feature 031.

## AssumptionRegistryEntry

- **Purpose**: Stores one candidate item and its user-approved assumption state.
- **Fields**:
  - `item_id`
  - `paper_status`
  - `paper_confidence`
  - `assumption_status`
  - `proposed_value`
  - `value_type`
  - `runtime_use_allowed`
  - `approval_required`
  - `approval_source`
  - `rationale`
  - `scientific_risk`
  - `affected_runtime_components`
  - `validation_plan`
  - `no_paper_recovery_claim`

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
- The governance/docs reconciliation is a separate document-level concern that must not alter the registry data model.
- Approved entries may later be consumed by runtime-config features, but only if a later approved feature explicitly does so.

## Validation Rules

- Every in-scope candidate must appear exactly once.
- `runtime_use_allowed` can be true only when `assumption_status = approved`.
- `no_paper_recovery_claim` must always be true.
- The registry must preserve the original `paper_status` unchanged.
- Governance docs must preserve version consistency between sync report and footer.

