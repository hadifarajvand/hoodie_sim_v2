# Report Schema Contract: Exposure Matrix Rerun and Paper Mechanism Alignment

The report must be machine-readable and must include the following top-level fields:

```json
{
  "feature_id": "049-exposure-matrix-paper-mechanism-alignment",
  "prerequisite_tags_verified": [],
  "prior_feature_gates_verified": [],
  "legality_evidence_verified": {},
  "exposure_matrix_rerun_summary": {},
  "legal_vs_selected_action_matrix": [],
  "per_strategy_seed_matrix": [],
  "per_action_outcome_matrix": {},
  "selected_illegal_action_summary": {},
  "observation_vector_audit": {},
  "paper_formula_unit_audit": {},
  "runtime_semantic_drift_check": {},
  "training_readiness_decision": {},
  "recommended_next_feature": "",
  "no_runtime_repair_performed": true,
  "no_training_started": true,
  "no_optimizer_step": true,
  "no_replay_training": true,
  "no_target_update_execution": true,
  "no_dependency_drift": true,
  "no_policy_drift": true,
  "no_reward_timing_change": true,
  "no_timeout_contract_drift": true,
  "no_capacity_contract_drift": true,
  "no_transmission_contract_drift": true,
  "no_action_legality_drift": true,
  "no_action_selection_drift": true,
  "no_curve_fitting": true,
  "no_simulator_output_tuning": true,
  "no_paper_reproduction_claim": true,
  "final_verdict": ""
}
```

Contract expectations:

- `legality_evidence_verified` must record that Feature 048 evidence was used and whether it was sufficient.
- `exposure_matrix_rerun_summary` must summarize rerun completeness, exposure bias, and rerun status by strategy/seed/action.
- `legal_vs_selected_action_matrix` must compare legal availability with selected actions and outcomes.
- `observation_vector_audit` must report presence/missing status for paper HOODIE observation inputs.
- `paper_formula_unit_audit` must report pass/fail status for the required timing and terminal-state formulas.
- `runtime_semantic_drift_check` must report whether the current simulator contract contradicts the paper mechanism.
- `training_readiness_decision` must explain why the final verdict does or does not permit the next training-contract bundle.
- `recommended_next_feature` must align with the final verdict and never recommend training when a blocking gap exists.

Allowed final verdict values:

- `paper_mechanism_alignment_ready_for_training_contract`
- `observation_vector_gap_blocks_training`
- `formula_unit_gap_blocks_training`
- `exposure_bias_blocks_training`
- `runtime_semantic_contradiction_requires_repair`
- `insufficient_legality_or_trace_evidence`
- `prerequisite_blocked`
