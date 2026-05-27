# Feature 065 — Paper-Faithful State and Action Space Batch

## Batch rule

This feature batches the paper-faithful observation and action-space repair into one implementation feature. Splitting this would be useless churn because the state tensor, LSTM input, destination action mapping, and legal mask must evolve together.

Covered items:

1. Full paper state vector
2. Private/offloading waiting times
3. Public queue length vector
4. `W × (N+1)` load history matrix
5. LSTM forecast input based on node active queues
6. Destination-specific action space
7. Legal action masking for exact Edge-Agent and Cloud destinations

## Purpose

Repair the current simplified HOODIE action/state surface. The current implementation has a three-action family interface (`local`, `horizontal`, `vertical`) and a three-dimensional replay state. That is not paper-faithful enough. Feature 065 must introduce a paper-faithful state/action contract while preserving the existing safe pipeline and not rerunning training.

## Required prior inputs

- `artifacts/analysis/final-review-release-gate-batch/final-review-release-gate-batch-report.json`
- `resources/papers/hoodie/recovered/user-approved-assumption-registry.json`
- Existing topology implementation under `src/environment/topology.py`
- Existing queue/runtime implementation under `src/environment/`
- Existing Torch network/training surface under `src/analysis/paper_hoodie_network_implementation/` and `src/analysis/full_training_reproduction_campaign/`

## Scope

Allowed implementation paths:

- `specs/065-paper-faithful-state-action-space-batch/`
- `src/analysis/paper_faithful_state_action_space_batch/`
- `src/environment/paper_state.py`
- `src/environment/paper_action_space.py`
- `src/environment/paper_load_history.py`
- `src/environment/paper_lstm_forecast.py`
- `tests/unit/test_paper_faithful_state_action_space_batch_schema.py`
- `tests/unit/test_paper_faithful_state_action_space_batch_metrics.py`
- `tests/unit/test_paper_faithful_state_action_space_batch_behavior_equivalence.py`
- `tests/unit/test_paper_state_vector.py`
- `tests/unit/test_paper_action_space.py`
- `tests/unit/test_paper_load_history.py`
- `tests/integration/test_paper_faithful_state_action_space_batch.py`
- `tests/integration/test_paper_faithful_state_action_space_batch_report.py`
- `tests/integration/test_paper_faithful_state_action_space_batch_scope_guard.py`
- `artifacts/analysis/paper-faithful-state-action-space-batch/`

Forbidden paths:

- `.specify/feature.json`
- `AGENTS.md`
- `.gitignore`
- dependency files
- prior Feature 037–064 artifacts
- checkpoint binaries
- new campaign outputs
- release tags

Forbidden behavior:

- no training rerun
- no evaluation campaign rerun
- no optimizer steps
- no replay mutation from a campaign run
- no dependency installation
- no dependency-file changes
- no prior artifact rewrite
- no paper reproduction claim
- no unsupported superiority claim

## Paper-faithful state contract

The implementation must expose a state-building contract that contains at least:

- `task_size_mbits`
- `private_waiting_time_slots`
- `offloading_waiting_time_slots`
- `public_queue_lengths_by_destination`
- `load_history_matrix`
- `forecast_input_matrix`
- `active_queue_counts_by_node`
- `source_agent_id`
- `legal_destination_ids`
- `paper_state_version`

The paper-load matrix must be shaped:

```text
W × (N + 1)
```

where:

- `W = lookback window`, default `10`
- `N = number of Edge Agents`, default `20`
- `N + 1` includes the Cloud node

The implementation must not fake this with a three-dimensional state vector. The old compact state may remain for backward compatibility only if clearly labeled `legacy_compact_state` and not used as the paper-faithful state.

## Waiting-time requirements

Private and offloading waiting times must be explicit values derived from queue/task lifecycle state. They may be computed using deterministic queue-head age approximations if the existing queue type does not yet expose exact waiting time, but the approximation must be named and reported.

Required fields:

- `private_waiting_time_slots`
- `offloading_waiting_time_slots`
- `waiting_time_source`
- `waiting_time_exactness`

## Public queue vector requirements

The state must include a vector that represents public-queue load seen by or relevant to the source Edge Agent.

Required fields:

- `public_queue_lengths_by_destination`
- `public_queue_vector_length`
- `public_queue_destination_order`
- `public_queue_source_scope`

The vector must not collapse all public queues into one scalar.

## Load-history and LSTM forecast input requirements

The feature must implement a load-history recorder that samples active queue counts per node every slot.

Required fields:

- `load_history_matrix`
- `load_history_shape`
- `load_history_node_order`
- `load_history_window_w`
- `forecast_input_matrix`
- `forecast_input_shape`
- `forecast_input_source = active_queue_counts_by_node`

The LSTM forecast input does not need to train a forecasting model in this feature. It must expose the correct matrix that the next training feature can feed to the LSTM. If a forecast output is provided, it must be marked as structural/contract-only unless computed by a real model.

## Destination-specific action-space contract

The feature must replace the paper-facing action contract from three action families to destination-specific action IDs.

Minimum required action semantics:

```text
0 = local/self compute
1..N = exact horizontal destination Edge Agent IDs
N+1 = Cloud destination
```

For `N = 20`, the paper-faithful action count is `22` only if the encoding includes a reserved invalid/noop action. Otherwise it is `21` actions: `local + 20 edge destinations + cloud`. The implementation must choose one encoding, document it, and enforce it consistently.

Self-horizontal destinations must be illegal. Legal horizontal destinations must come from the recovered topology adjacency. Cloud must be legal for vertical offloading unless explicitly disabled by configuration.

Required action fields:

- `paper_action_count`
- `action_index_to_destination`
- `destination_to_action_index`
- `local_action_index`
- `cloud_action_index`
- `horizontal_action_indices`
- `invalid_action_indices`
- `action_encoding_version`

## Legal action mask requirements

The legal mask must be destination-specific, not family-specific.

Required behavior:

- local action is legal for pending tasks
- exact neighboring Edge Agent destinations are legal for horizontal offloading
- non-neighbor Edge Agent destinations are illegal
- self Edge Agent destination is illegal as horizontal destination
- Cloud destination is legal for vertical offloading
- mask length equals `paper_action_count`
- every legal action maps to a deterministic destination
- every illegal action has a reason

Required fields:

- `legal_action_mask`
- `legal_action_reasons`
- `illegal_action_reasons`
- `source_agent_id`
- `topology_source`
- `mask_encoding_version`

## Compatibility requirements

Existing environment behavior must not be silently broken. The feature may add new paper-facing modules and adapters, but it must not force the existing training campaign to use the new action space yet. Training migration belongs to Feature 066.

Feature 065 must produce a migration report that states:

- current training remains legacy-compatible
- paper-faithful state/action contract exists
- Feature 066 must bind distributed multi-agent training to this contract

## Required output artifacts

- `artifacts/analysis/paper-faithful-state-action-space-batch/paper-faithful-state-action-space-batch-report.json`
- `artifacts/analysis/paper-faithful-state-action-space-batch/paper-faithful-state-action-space-batch-report.md`
- `artifacts/analysis/paper-faithful-state-action-space-batch/paper-state-contract.json`
- `artifacts/analysis/paper-faithful-state-action-space-batch/paper-action-space-contract.json`
- `artifacts/analysis/paper-faithful-state-action-space-batch/paper-legal-mask-contract.json`
- `artifacts/analysis/paper-faithful-state-action-space-batch/paper-load-history-contract.json`
- `artifacts/analysis/paper-faithful-state-action-space-batch/migration-readiness-for-feature-066.json`

## Required report fields

- `feature_id`
- `batch_items_covered`
- `feature_064_verified`
- `paper_state_contract_summary`
- `waiting_time_summary`
- `public_queue_vector_summary`
- `load_history_summary`
- `forecast_input_summary`
- `destination_action_space_summary`
- `legal_mask_summary`
- `compatibility_summary`
- `safety_summary`
- `remaining_blockers`
- `recommended_next_feature`
- `final_verdict`

## Passing verdict

Passing requires:

- Feature 064 final verdict is `final_review_release_gate_batch_passed`
- paper state vector contract exists and is not three-dimensional legacy state
- private/offloading waiting times are explicit
- public queue vector exists and is not scalar-collapsed
- load-history matrix is `W × (N+1)`
- LSTM forecast input matrix is derived from active queue counts
- destination-specific action mapping exists
- legal mask is destination-specific and topology-backed
- existing legacy behavior is not broken
- no training/evaluation campaign is rerun
- no prior artifacts are rewritten

If all gates pass:

```text
final_verdict = paper_faithful_state_action_space_batch_passed
recommended_next_feature = Feature 066 — Distributed Multi-Agent HOODIE Training Batch
remaining_blockers = []
```

Allowed blocked verdicts:

- `feature_064_prerequisite_blocked`
- `paper_state_contract_blocked`
- `waiting_time_contract_blocked`
- `public_queue_vector_blocked`
- `load_history_contract_blocked`
- `forecast_input_contract_blocked`
- `destination_action_space_blocked`
- `legal_mask_contract_blocked`
- `compatibility_blocked`
- `behavior_drift_detected`
