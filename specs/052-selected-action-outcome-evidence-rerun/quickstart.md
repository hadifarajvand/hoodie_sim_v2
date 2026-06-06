# Quickstart: Selected-Action Outcome Evidence Rerun

1. Confirm the feature pointer is set to `specs/052-selected-action-outcome-evidence-rerun`.
2. Run the Feature 052 analysis command through the approved interpreter.
3. Generate the JSON and Markdown rerun reports under `artifacts/analysis/selected-action-outcome-evidence-rerun/`.
4. Validate the report against the Feature 052 unit and integration tests.
5. Confirm the report routes to the correct unblock assessment:
   - `selected_action_outcome_evidence_ready_for_feature_049_rerun`
   - `selected_action_family_evidence_still_incomplete`
   - `selected_action_to_task_join_still_incomplete`
   - `per_action_outcome_join_still_incomplete`
   - `exposure_matrix_internal_consistency_failed`
   - `behavior_drift_detected`
   - `prerequisite_blocked`

Validation notes:
- Prior Features 048, 049, 050, and 051 must be verified through committed JSON report artifacts only.
- Do not use dirty-worktree-sensitive prior-feature report builders.
- Do not regenerate prior feature artifacts.

Expected outputs:
- `artifacts/analysis/selected-action-outcome-evidence-rerun/selected-action-outcome-evidence-rerun-report.json`
- `artifacts/analysis/selected-action-outcome-evidence-rerun/selected-action-outcome-evidence-rerun-report.md`
