# Quickstart: Public/Cloud Queue Capacity Sharing Contract

## Approved Interpreter

Use the approved environment only:

```bash
/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python
```

## Implementation Target

This feature is scoped to public/cloud capacity sharing only. Expected touchpoints are:

- `src/environment/gym_adapter.py`
- `src/environment/public_queue.py` if queue grouping helpers are needed
- `src/environment/compute_config.py` only if capacity lookup helpers are needed

## Validation Command

Run the targeted tests with the approved interpreter:

```bash
PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest \
  tests.unit.test_public_cloud_capacity_sharing \
  tests.integration.test_public_cloud_capacity_sharing_flow \
  tests.integration.test_execution_time_flow \
  tests.integration.test_transmission_delay_runtime_wiring \
  tests.integration.test_public_cloud_capacity_sharing_report \
  tests.integration.test_public_cloud_capacity_sharing_scope_guard
```

## Expected Outcomes

- One public queue can consume the full edge capacity for its host.
- Multiple public queues sharing the same host split edge capacity evenly.
- Different edge hosts do not share capacity with each other.
- Cloud queues share the global cloud capacity evenly.
- Local/private behavior, transmission delay, and reward timing remain unchanged.

## Report Artifacts

Generate:

- `artifacts/analysis/public-cloud-queue-capacity-sharing/public-cloud-capacity-sharing-report.json`
- `artifacts/analysis/public-cloud-queue-capacity-sharing/public-cloud-capacity-sharing-report.md`

The report must distinguish:
- runtime components wired
- runtime components validated
- old invalid behavior
- new capacity-sharing contract
- tests added
- tests run
- no-drift flags
