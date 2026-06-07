# Phase 2 Two-Stage Action Model

This phase makes the HOODIE offloading decision explicit in code.

## What It Implements

- First-stage decision `d_n^(1)(t)`: `local` or `offload`
- Second-stage destination decision `d_{n,k}^{(2)}(t)`: one legal destination when offloading
- Local, horizontal edge, and vertical cloud action types
- Topology-aware legality checks for horizontal offloading
- Rejection of invalid raw actions and invalid explicit route choices
- Action trace fields for the two-stage decision contract

## Paper Mapping

- `TwoStageAction.first_stage_decision` maps to `d_n^(1)(t)`
- `TwoStageAction.d_n_1` stores the compact first-stage indicator:
  - `0` for local
  - `1` for offload
- `TwoStageAction.d_nk_2` stores the sparse second-stage destination choice
  - empty for local
  - one active destination for offload

## Action Semantics

- `local`
  - stays on the source node's private path
  - no offloading destination is active
- `horizontal_edge`
  - offloads to a neighboring edge node
  - adjacency must be allowed by the topology matrix
- `vertical_cloud`
  - offloads to the cloud node
  - cloud is a distinct legal destination, not a self-route

## Topology Contract

- `environment/action_model.py` wraps the adjacency matrix in `TopologyAdapter`
- `environment/matchmaker.py` builds per-node action spaces from that topology
- `environment/environment.py` loads the topology from the existing connection matrix in `hyperparameters/hyperparameters.json`
- Cloud node id is `number_of_servers`

## Compatibility Layer

- Legacy raw action ids are still supported
- Raw action id `0` remains the local action
- Horizontal destinations occupy the middle action slots
- The final action is the cloud destination
- Invalid raw ids are rejected with a clear `ValueError`

## What This Phase Does Not Change

- queue service formulas
- offloading queue formulas
- public CPU sharing
- reward calculation
- LSTM or training
- action-space learning
- figure generation

## Files Involved

- `environment/action_model.py`
- `environment/matchmaker.py`
- `environment/environment.py`
- `phase1_tracing.py`
- `main.py`
- `tests/test_phase2_action_model.py`

## Running The Tests

```bash
./.venvmac/bin/python -m unittest tests.test_phase1_task_properties -v
./.venvmac/bin/python -m unittest tests.test_phase1_tracing -v
./.venvmac/bin/python -m unittest tests.test_phase2_action_model -v
./.venvmac/bin/python -m unittest tests.test_phase2_mechanisms -v
./.venvmac/bin/python main.py --epochs 1 --log_folder /private/tmp/phase2-action-model-smoke/logs
```

