# Quickstart: Exposure Matrix Paper Mechanism Rerun with Outcome Evidence

1. Confirm the feature pointer is set to `specs/053-exposure-matrix-paper-mechanism-rerun-with-outcome-evidence`.
2. Run the Feature 053 analysis through the approved interpreter.
3. Generate the JSON and Markdown rerun reports under `artifacts/analysis/exposure-matrix-paper-mechanism-rerun-with-outcome-evidence/`.
4. Validate the report against the Feature 053 unit and integration tests.
5. Confirm the report routes to the correct verdict:
   - `paper_mechanism_alignment_ready_for_training_contract`
   - `observation_vector_alignment_blocked`
   - `formula_unit_alignment_blocked`
   - `exposure_matrix_alignment_blocked`
   - `selected_action_outcome_alignment_blocked`
   - `behavior_drift_detected`
   - `prerequisite_blocked`

Validation notes:
- Prior Features 048, 049, 050, 051, and 052 must be verified through committed JSON report artifacts only.
- Do not use dirty-worktree-sensitive prior-feature report builders.
- Do not regenerate prior feature artifacts.

Expected outputs:
- `artifacts/analysis/exposure-matrix-paper-mechanism-rerun-with-outcome-evidence/exposure-matrix-paper-mechanism-rerun-report.json`
- `artifacts/analysis/exposure-matrix-paper-mechanism-rerun-with-outcome-evidence/exposure-matrix-paper-mechanism-rerun-report.md`
