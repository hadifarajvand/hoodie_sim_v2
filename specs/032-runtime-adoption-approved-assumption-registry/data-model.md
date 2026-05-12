# Data Model: Runtime Adoption of Approved Assumption Registry

## ApprovedAssumptionSnapshot

- **Purpose**: Represents the Feature 031 registry/report data consumed by Feature 032.
- **Fields**:
  - `item_id`
  - `assumption_status`
  - `runtime_use_allowed`
  - `approval_source`
  - `proposed_value`
  - `no_paper_recovery_claim`
  - `runtime_patch_applied`

## RuntimeAdoptionContract

- **Purpose**: Represents a runtime-facing adoption rule or configuration binding.
- **Fields**:
  - `contract_name`
  - `source_assumption_id`
  - `runtime_component`
  - `adopted_value`
  - `validation_rule`
  - `provenance`

## TopologyLegalityContract

- **Purpose**: Captures the runtime adjacency and legality rules used by the action mask.
- **Fields**:
  - `node_order`
  - `adjacency_matrix`
  - `neighbor_only_horizontal`
  - `forbid_self_offload`
  - `forbid_non_neighbor_horizontal`
  - `vertical_action_independent`

## TimeoutContract

- **Purpose**: Captures the runtime timeout and drop behavior contract.
- **Fields**:
  - `timeout_slots`
  - `slot_duration_seconds`
  - `timeout_seconds`
  - `drop_validation`
  - `reward_timing_validation`

## AggregationContract

- **Purpose**: Captures the shared reward aggregation helper semantics.
- **Fields**:
  - `agent_level_reduction`
  - `cross_agent_reduction`
  - `exclude_no_task_slots`
  - `exclude_nan_slots`
  - `exclude_omitted_slots`
  - `no_direct_slot_average`

## AdoptionReport

- **Purpose**: Auditable summary of which approved assumptions were consumed and which runtime components changed.
- **Fields**:
  - `feature_id`
  - `consumed_assumption_ids`
  - `runtime_components_changed`
  - `runtime_components_validated`
  - `tests_run`
  - `no_paper_recovery_claims`
  - `no_dependency_drift`
  - `no_training_or_policy_drift`
  - `no_reward_timing_change`
  - `no_campaign_rerun`
  - `final_verdict`

## Relationships

- One adoption report summarizes many adoption contracts.
- One approved assumption snapshot may feed more than one runtime contract.
- Topology, timeout, link-rate, compute, and aggregation contracts are independent but must remain provenance-linked to Feature 031.

## Validation Rules

- Approved assumptions must stay labeled as approved assumptions.
- Runtime adoption must not relabel assumptions as paper-recovered facts.
- Aggregation must sum per-agent terminal rewards before cross-agent arithmetic mean.
- Topology legality must keep vertical/cloud legality separate from horizontal adjacency.

