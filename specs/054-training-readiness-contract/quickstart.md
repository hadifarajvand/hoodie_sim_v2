# Quickstart: Training Readiness Contract

1. Confirm the feature pointer is set to `specs/054-training-readiness-contract`.
2. Run the Feature 054 analysis through the approved interpreter.
3. Generate the JSON and Markdown readiness reports under `artifacts/analysis/training-readiness-contract/`.
4. Validate the report against the Feature 054 unit and integration tests.
5. Confirm the report routes to the correct verdict:
   - `training_readiness_contract_ready_for_smoke_run`
   - `evidence_chain_prerequisite_blocked`
   - `paper_default_config_contract_blocked`
   - `observation_contract_blocked`
   - `action_or_legality_contract_blocked`
   - `reward_timeout_capacity_contract_blocked`
   - `metric_or_artifact_contract_blocked`
   - `behavior_drift_detected`

Validation notes:
- Prior Features 048, 049, 050, 051, 052, and 053 must be verified through committed JSON report artifacts only.
- Do not use dirty-worktree-sensitive prior-feature report builders.
- Do not regenerate prior feature artifacts.

Expected outputs:
- `artifacts/analysis/training-readiness-contract/training-readiness-contract-report.json`
- `artifacts/analysis/training-readiness-contract/training-readiness-contract-report.md`
