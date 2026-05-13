# Data Model: Baseline Revalidation After Runtime Repair

## Entities

### Baseline Policy

- **Purpose**: Represents one of the in-scope baseline policies being revalidated.
- **Attributes**:
  - `policy_name`
  - `policy_family`
  - `deterministic` flag
  - `seed_controlled` flag
- **Relationships**:
  - Participates in one or more `Revalidation Run` records.

### Revalidation Run

- **Purpose**: A single seeded evaluation pass for a baseline policy.
- **Attributes**:
  - `policy_name`
  - `scenario_name`
  - `seed`
  - `final_metrics`
  - `total_tasks`
  - `completed_tasks`
  - `dropped_tasks`
  - `drop_ratio`
  - `throughput`
  - `average_delay`
  - `runtime_contract_markers`
  - `artifact_paths`
  - `legal_action_mask_verified`
- **Validation Rules**:
  - Must use the shared `HoodieGymEnvironment`.
  - Must not bypass the legal action mask.
  - Must be reproducible for fixed seeds when the policy is deterministic.

### Revalidation Report

- **Purpose**: Summarizes the baseline sanity results after runtime repair.
- **Attributes**:
  - `feature_id`
  - `prerequisite_tags_verified`
  - `policies_revalidated`
  - `scenarios_revalidated`
  - `seeds_used`
  - `runtime_contracts_verified`
  - `environment_interface_verified`
  - `legal_action_mask_verified`
  - `metric_schema_verified`
  - `deterministic_reproducibility_verified`
  - `baseline_result_summary`
  - `artifact_paths`
  - `no_curve_fitting`
  - `no_paper_reproduction_claim`
  - `no_dependency_drift`
  - `no_training_or_policy_drift`
  - `no_environment_contract_drift`
  - `no_reward_timing_change`
  - `no_execution_time_contract_drift`
  - `no_transmission_delay_contract_drift`
  - `no_capacity_sharing_contract_drift`
  - `no_timeout_contract_drift`
  - `final_verdict`
- **Validation Rules**:
  - Must clearly label the result as post-runtime-repair sanity output.
  - Must not imply paper reproduction or curve matching.
  - Must include all prerequisite runtime tags from Features 032–036.

### Legal Action Mask

- **Purpose**: The environment-side legality filter that determines whether a proposed action may be taken.
- **Attributes**:
  - `allowed_actions`
  - `policy_context`
  - `scenario_name`
- **Validation Rules**:
  - All baseline actions must pass through this mask.
  - No baseline may bypass the mask.

## State Transitions

- `Revalidation Run`: created when a baseline is executed with a fixed seed; completed when metrics and artifacts are captured.
- `Revalidation Report`: created after one or more revalidation runs; finalized when all required fields and claim boundaries are present.

## Invariants

- Baselines are revalidated, not redesigned.
- Revalidation artifacts must remain deterministic for fixed seeds where the policy is deterministic.
- RO is seed-controlled and must reproduce its own action/result trace for the same seed.
- Old artifacts are drift references only, not correctness targets.
