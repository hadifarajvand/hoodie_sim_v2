# Instrumentation Report Schema Contract

## Purpose

Define the analysis report written after a traced paper-default run.

## Required report fields

- `feature_id`
- `prerequisite_tags_verified`
- `prior_feature_gates_verified`
- `instrumentation_scope`
- `trace_event_schema`
- `trace_sources`
- `paper_default_runtime_verified`
- `behavior_equivalence_checks`
- `trace_coverage_summary`
- `lifecycle_trace_sample`
- `completion_diagnosis_readiness`
- `runtime_contracts_verified`
- `reward_timing_contract_verified`
- `pending_at_horizon_contract_verified`
- `no_training_started`
- `no_optimizer_step`
- `no_replay_training`
- `no_target_update_execution`
- `no_dependency_drift`
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

## Allowed final verdict values

- `passive_trace_instrumentation_ready`
- `passive_trace_instrumentation_incomplete`
- `behavior_drift_detected`
- `prerequisite_blocked`

## Contract notes

- The report MUST remain descriptive and diagnostic.
- The report MUST identify whether the trace is sufficient to support downstream lifecycle diagnosis.
- The report MUST preserve the paper-default runtime context and not imply any runtime repair.
