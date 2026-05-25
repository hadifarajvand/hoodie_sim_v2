# Data Model: Feature 058

## EvaluationTraceBankBaselineHarnessReport

Represents the complete evaluation trace-bank and baseline harness readiness result.

Fields:

- `feature_id`: constant `058-evaluation-trace-bank-baseline-harness`
- `prerequisite_tags_verified`: prerequisite gate checks
- `feature_057_pilot_verified`: boolean
- `evaluation_trace_bank_summary`: deterministic evaluation bank evidence
- `train_eval_separation_summary`: train/eval disjointness evidence
- `baseline_policy_registry_summary`: registered baseline policy definitions
- `baseline_evaluation_harness_summary`: baseline dry-run/evaluation evidence
- `metric_schema_summary`: metric schema coverage evidence
- `determinism_summary`: repeatability evidence
- `behavior_safety_summary`: no-training/no-drift evidence
- `remaining_blockers`: exact blocker list
- `recommended_next_feature`: next routed feature
- `final_verdict`: final status

## EvaluationTraceBankSummary

Expected evidence:

- evaluation trace bank ID
- evaluation trace count
- deterministic seed bundle
- trace identity/hash list or deterministic signature
- bank generation is repeatable

## TrainEvalSeparationSummary

Expected evidence:

- training trace bank ID
- evaluation trace bank ID
- disjoint trace IDs
- no evaluation-on-training traces

## BaselinePolicyRegistrySummary

Expected evidence:

- registered baseline policy names
- baseline policy count
- action contract compatibility
- no learned-policy checkpoint dependency

## BaselineEvaluationHarnessSummary

Expected evidence:

- registered policies can be evaluated on evaluation traces
- evaluation produces per-policy metric shells
- evaluation does not train, mutate replay, run optimizer, or write model checkpoints

## MetricSchemaSummary

Required metric families:

- delay
- drop
- timeout
- reward
- action distribution
- local action count
- horizontal action count
- vertical action count
- per-episode summary

## BehaviorSafetySummary

Must prove:

- no training execution
- no optimizer execution
- no replay mutation
- no checkpoint binary written
- no full campaign
- no paper reproduction claim
- no performance claim
- no policy drift
- no dependency drift
- no environment contract drift
- no reward timing change
- no prior artifact rewrite
