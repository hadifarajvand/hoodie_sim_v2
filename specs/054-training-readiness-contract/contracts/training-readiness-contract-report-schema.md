# Report Schema Contract: Training Readiness Contract

The report must be machine-readable and must include the following top-level fields:

```json
{
  "feature_id": "054-training-readiness-contract",
  "prerequisite_tags_verified": [],
  "prior_feature_gates_verified": [],
  "feature_053_readiness_verified": false,
  "evidence_chain_ready_for_training_contract": false,
  "paper_default_config_locked": false,
  "observation_contract_locked": false,
  "action_contract_locked": false,
  "legality_contract_locked": false,
  "reward_contract_locked": false,
  "timeout_contract_locked": false,
  "capacity_contract_locked": false,
  "transmission_contract_locked": false,
  "queue_contract_locked": false,
  "metric_contract_locked": false,
  "seed_contract_locked": false,
  "artifact_contract_locked": false,
  "behavior_equivalence_summary": {},
  "behavior_equivalence_passed": false,
  "training_execution_allowed_next": false,
  "remaining_blockers": [],
  "recommended_next_feature": "",
  "no_training_started": true,
  "no_optimizer_step": true,
  "no_replay_training": true,
  "no_target_update_execution": true,
  "no_checkpoint_written": true,
  "no_campaign_run": true,
  "no_policy_drift": true,
  "no_runtime_semantic_changes": true,
  "no_dependency_drift": true,
  "no_prior_artifact_rewrite": true,
  "no_paper_reproduction_claim": true,
  "final_verdict": ""
}
```

Contract expectations:

- `feature_053_readiness_verified` must be true only when the Feature 053 report proves readiness for the training contract.
- `evidence_chain_ready_for_training_contract` must be true only when the committed Feature 048 through 053 reports are present and internally consistent.
- Each contract lock field must be a boolean.
- `training_execution_allowed_next` must be true only when the evidence chain is ready, all contract locks are true, behavior equivalence passes, no drift is detected, no prior artifacts are rewritten, and no training has already started.
- `remaining_blockers` must explain the exact blocking family when training is not allowed next.
- `recommended_next_feature` must point to Feature 055 only when the contract is fully satisfied.
- `final_verdict` must be consistent with the lock bundle, the evidence chain gate, and the next-feature routing.
- `behavior_equivalence_passed` must equal `behavior_equivalence_summary.passed`.

Allowed final verdict values:

- `training_readiness_contract_ready_for_smoke_run`
- `evidence_chain_prerequisite_blocked`
- `paper_default_config_contract_blocked`
- `observation_contract_blocked`
- `action_or_legality_contract_blocked`
- `reward_timeout_capacity_contract_blocked`
- `metric_or_artifact_contract_blocked`
- `behavior_drift_detected`

Contract failure conditions:

- The contract fails if `feature_053_readiness_verified` is false.
- The contract fails if any lock field is missing.
- The contract fails if `training_execution_allowed_next` is true while any contract is unlocked.
- The contract fails if `remaining_blockers` is empty while training execution is not allowed next.
- The contract fails if `final_verdict` claims smoke-run readiness while `training_execution_allowed_next` is false.
- The contract fails if `recommended_next_feature` routes to Feature 055 while required evidence is unavailable.
- The contract fails if `behavior_equivalence_passed` contradicts `behavior_equivalence_summary.passed`.
