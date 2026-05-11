# Contract: Assumption Closure Report

## JSON Shape

The generated `assumption-closure-report.json` MUST contain:

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

## Item Record Shape

Each entry in `items` MUST include:

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

## Final Verdict Values

- `all_items_closed_without_runtime_changes`
- `recovered_items_require_user_approval`
- `runtime_repair_required_from_recovered_evidence`
- `blocked_by_unrecoverable_core_evidence`

## Determinism

The same inputs MUST produce the same item ordering, same classification set, and same summary counts.

