# Feature 065 — Paper-Faithful State and Action Space Batch

## Batch rule

This feature batches the paper-faithful state and action-space repair items into one implementation feature.

Covered items:

1. Full paper state vector
2. Private/offloading waiting times
3. Public queue length vector
4. `W × (N+1)` load history matrix
5. LSTM forecast input based on node active queues
6. Destination-specific action space
7. Legal action masking for exact Edge-Agent/Cloud destinations

## Purpose

Replace the current simplified 3-dimensional state and 3-family action abstraction with a paper-faithful HOODIE state/action contract. The feature must expose exact destination choices and paper-derived state components while preserving the existing release-gated evidence chain and avoiding new training/reproduction claims.

## Required prior inputs

- `artifacts/analysis/final-review-release-gate-batch/final-review-release-gate-batch-report.json`
- `artifacts/analysis/results-export-reproducibility-documentation-batch/final-mechanism-documentation.md`
- `resources/papers/hoodie/recovered/user-approved-assumption-registry.json`
- `src/environment/gym_adapter.py`
- `src/environment/topology.py`
- `src/analysis/full_training_reproduction_campaign/replay.py`
- `src/analysis/paper_hoodie_network_implementation/network.py`

## Current known defect being repaired

The current replay state is only `state_dim = 3`, and the current action index set is only:

```text
0 = local
1 = horizontal
2 = vertical
```

That is not paper-faithful because the HOODIE paper uses richer state information and destination-specific offloading decisions. Current horizontal offloading also resolves to the first legal neighbor automatically, which means the agent does not actually learn the horizontal destination.

## Required output artifacts

- `artifacts/analysis/paper-state-action-space-batch/paper-state-action-space-batch-report.json`
- `artifacts/analysis/paper-state-action-space-batch/paper-state-action-space-batch-report.md`
- `artifacts/analysis/paper-state-action-space-batch/paper-state-vector-contract.json`
- `artifacts/analysis/paper-state-action-space-batch/paper-action-space-contract.json`
- `artifacts/analysis/paper-state-action-space-batch/paper-load-history-contract.json`
- `artifacts/analysis/paper-state-action-space-batch/paper-lstm-forecast-input-contract.json`
- `artifacts/analysis/paper-state-action-space-batch/legal-destination-mask-contract.json`

## Required report fields

- `feature_id`
- `batch_items_covered`
- `prerequisite_tags_verified`
- `feature_064_verified`
- `paper_state_vector_summary`
- `waiting_time_summary`
- `public_queue_vector_summary`
- `load_history_matrix_summary`
- `lstm_forecast_input_summary`
- `destination_action_space_summary`
- `legal_destination_mask_summary`
- `compatibility_summary`
- `safety_summary`
- `remaining_blockers`
- `recommended_next_feature`
- `final_verdict`

## Paper-faithful state vector contract

The implementation must expose a structured state for each decision point containing at least:

- current task size `eta_mbits`
- current task processing density / cycles requirement
- current task arrival slot
- current task absolute deadline or timeout residual
- private queue waiting time for the source Edge Agent
- offloading queue waiting time for the source Edge Agent
- public queue length vector for tasks owned/hosted across exact destination nodes
- load history matrix with shape `W × (N+1)` where `W = lookback_w`, `N = edge_agent_count`, and `+1` is Cloud
- legal destination mask aligned to exact destination action indices

The raw structured state can be dictionary-based, but the tensor adapter must flatten deterministically and report its exact `state_dim`.

## Waiting-time contract

Private and offloading waiting times must be measured from queue state, not guessed from global history length. Required fields:

- `private_waiting_time_slots`
- `offloading_waiting_time_slots`
- `private_queue_depth`
- `offloading_queue_depth`
- deterministic zero behavior when queues are empty

## Public queue length vector contract

Public queue length representation must distinguish exact node destinations. Required fields:

- `destination_node_ids`
- `public_queue_lengths_by_destination`
- `cloud_public_queue_length`
- vector order contract
- vector length equals `N + 1`

## Load-history matrix contract

The environment must maintain node active queue counts over the last `W` slots. Required fields:

- `lookback_w`
- `edge_agent_count`
- `node_ids_in_order`
- `matrix_shape = [W, N+1]`
- per-slot active queue count per Edge Agent and Cloud
- left-padding/initialization policy for the first slots

## LSTM forecast input contract

The LSTM input must use the load-history matrix, not the previous simplified 3-column replay state. Required fields:

- `forecast_input_shape = [lookback_w, edge_agent_count + 1]`
- `forecast_node_order`
- `forecast_source = node_active_queue_load_history`
- deterministic tensor conversion
- clear compatibility path for the existing `PaperHoodieDuelingNetwork`

This feature does not need to retrain the final campaign, but it must make the correct paper-faithful input path available and validated.

## Destination-specific action space contract

The action space must explicitly represent:

- local/self execution
- horizontal offload to each exact legal Edge Agent destination
- vertical offload to Cloud

The implementation must not collapse all horizontal destinations into one action. The action registry must include:

- action index
- action family: `local`, `horizontal`, `vertical`
- source node
- destination node
- destination kind: `self`, `edge_agent`, `cloud`
- legality flag source

## Legal destination mask contract

For each source Edge Agent, the legal mask must:

- permit local/self action
- permit only topology-backed horizontal destination actions
- permit Cloud vertical action
- reject non-neighbor horizontal destinations
- align one-to-one with destination-specific action indices

## Allowed final verdicts

- `paper_state_action_space_batch_passed`
- `feature_064_prerequisite_blocked`
- `paper_state_vector_blocked`
- `waiting_time_contract_blocked`
- `public_queue_vector_blocked`
- `load_history_matrix_blocked`
- `lstm_forecast_input_blocked`
- `destination_action_space_blocked`
- `legal_destination_mask_blocked`
- `compatibility_blocked`
- `behavior_drift_detected`

## Passing behavior

Passing requires:

- Feature 064 final verdict is `final_review_release_gate_batch_passed`
- all requested batch items are implemented or exposed through validated contracts
- no horizontal action is silently resolved to first neighbor without an action-specific destination
- structured state includes real waiting times, public queue vector, and load-history matrix
- legal destination mask rejects illegal exact destinations
- report has `remaining_blockers = []`
- no training campaign rerun
- no prior Feature 037–064 artifact rewrite
- no paper reproduction claim

## Routing

If all gates pass:

- `final_verdict = paper_state_action_space_batch_passed`
- `recommended_next_feature = Feature 066 — Distributed Multi-Agent HOODIE Training Batch`
- `remaining_blockers = []`

If any gate fails, blockers must name exact failed gates and route to repair, not Feature 066.

## Hard scope

Allowed:

- state/action contract models
- environment observation/action-space extension
- replay/tensor adapter extension
- network config compatibility extension
- validation artifacts and tests

Forbidden:

- full training campaign rerun
- release tag creation
- prior artifact rewrites
- dependency changes
- policy superiority claims
- paper reproduction claims
- changing reward timing semantics
- changing existing 064 release artifacts
