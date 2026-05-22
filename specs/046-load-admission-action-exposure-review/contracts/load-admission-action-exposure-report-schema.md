# Contract: Load Admission Action Exposure Report Schema

## Required top-level fields

- `feature_id`
- `prerequisite_tags_verified`
- `prior_feature_gates_verified`
- `trace_input_sources`
- `paper_default_runtime_verified`
- `load_pressure_summary`
- `admission_serialization_summary`
- `action_exposure_summary`
- `queue_pressure_summary`
- `offload_path_pressure_summary`
- `budget_comparison_summary`
- `per_strategy_summary`
- `per_action_summary`
- `per_queue_summary`
- `dominant_pressure_sources`
- `diagnosis`
- `recommended_next_feature`
- `no_runtime_repair_performed`
- `no_training_started`
- `no_optimizer_step`
- `no_replay_training`
- `no_target_update_execution`
- `no_dependency_drift`
- `no_environment_contract_drift`
- `no_policy_drift`
- `no_reward_timing_change`
- `no_timeout_contract_drift`
- `no_capacity_contract_drift`
- `no_transmission_contract_drift`
- `no_action_legality_drift`
- `no_curve_fitting`
- `no_simulator_output_tuning`
- `no_paper_reproduction_claim`
- `final_verdict`

## Metric contracts

### Load pressure summary

Must include:
- generated, admitted, terminal, completed, dropped, and pending counts
- generated/admitted/terminal rates per slot
- completion, drop, and pending rates

### Admission serialization summary

Must include:
- same-slot generated and admitted counts
- serialized backlog count
- serialization lag statistics
- delayed and expired task identifiers

### Action exposure summary

Must include:
- legal, selected, and unselected action counts by family
- exposure and selection ratios by action family
- action entropy
- per-action completion/drop/pending rates

### Queue pressure summary

Must include:
- private/public/cloud admissions and terminal counts
- per-queue completion/drop rates
- queue wait mean and max
- queue pressure index

### Offload-path pressure summary

Must include:
- transmission start/completion counts
- transmission delay mean and max
- transmission-to-admission lag
- execution-start-after-transmission lag
- offloaded completed/dropped/pending counts

### Budget comparison summary

Must include:
- representative task identifiers
- expected compute and transmission budget
- observed queue wait, execution progress, and task age
- deadline margin or overrun at terminal outcome

## Verdict discipline

- `final_verdict` must be one of:
  - `load_pressure_explains_completion_weakness`
  - `admission_serialization_explains_completion_weakness`
  - `action_exposure_explains_completion_weakness`
  - `queue_pressure_explains_completion_weakness`
  - `offload_path_pressure_explains_completion_weakness`
  - `mixed_load_action_pressure_explains_completion_weakness`
  - `diagnosis_inconclusive_requires_deeper_exposure_matrix`
  - `prerequisite_blocked`
- Runtime repair is invalid for this feature except as an evidence-backed runtime-fault contradiction explicitly named in the report.
- `recommended_next_feature` must not point to runtime repair.
- If action exposure is dominant, the recommendation must be `Feature 047 — Paper HOODIE Observation Vector`.
- If mixed load/action pressure is dominant, the recommendation must be `exposure-matrix review` before Feature 047.
- If load/admission pressure is dominant, the recommendation must be load/admission/action-exposure assumption review or `exposure-matrix review`.
- If queue pressure or offload-path pressure is dominant, the recommendation must be load/admission/action-exposure assumption review or `exposure-matrix review`.
- If evidence is inconclusive, the recommendation must be `exposure-matrix review`.
- The report must not use loose variants such as observation-vector, observation vector, pilot-policy review, or exposure matrix/pilot policy review.

## Traceability

- `trace_input_sources` must reference Feature 044 and Feature 045 artifacts.
- `paper_default_runtime_verified` must identify the paper-default configuration used for the review.
- The report must preserve evidence lineage from lifecycle reconstruction through per-strategy summaries.
- The report must preserve canonical next-feature terminology exactly as defined in the spec.
