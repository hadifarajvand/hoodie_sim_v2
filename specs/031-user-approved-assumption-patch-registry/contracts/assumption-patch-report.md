# Contract: User-Approved Assumption Patch Registry Report

## JSON Shape

The generated `assumption-patch-report.json` MUST contain:

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

## Registry Entry Shape

Each entry in `entries` MUST include:

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

## Final Verdict Values

- `registry_created_no_runtime_approved_assumptions`
- `registry_created_with_runtime_approved_assumptions`
- `blocked_missing_feature_030_source_gate`
- `blocked_invalid_assumption_registry`

## Determinism

The same inputs MUST produce the same registry ordering, same status counts, and same final verdict.
