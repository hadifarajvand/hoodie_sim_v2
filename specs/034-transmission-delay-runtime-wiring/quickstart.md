# Quickstart: Transmission Delay Runtime Wiring

## Approved Interpreter

Use the approved environment only:

```bash
/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python
```

## Implementation Target

The feature is scoped to runtime transmission delay wiring only. The expected code touchpoints are:

- `src/environment/gym_adapter.py`
- `src/environment/slot_engine.py`
- `src/environment/offloading_queue.py`
- `src/environment/link_rate_config.py` only if a helper gap is proven

## Validation Command

Run the targeted tests with the approved interpreter:

```bash
PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest \
  tests.unit.test_link_rate_conversion \
  tests.unit.test_link_rate_rounding_policy \
  tests.unit.test_slot_engine \
  tests.integration.test_execution_time_flow \
  tests.integration.test_transmission_delay_runtime_wiring \
  tests.integration.test_mechanism_repair_timeout_drop \
  tests.integration.test_execution_time_contract_scope_guard
```

## Expected Outcomes

- Horizontal delay uses payload size and `R_H = 30 Mbps`.
- Vertical delay uses payload size and `R_V = 10 Mbps`.
- Offloading admission occurs only at the documented slot boundary.
- Local execution remains free of transmission delay metadata.
- Timeout/drop behavior counts offload transit time.
- Reward remains terminal-only.

## Report Artifacts

Generate:

- `artifacts/analysis/transmission-delay-runtime-wiring/transmission-delay-runtime-report.json`
- `artifacts/analysis/transmission-delay-runtime-wiring/transmission-delay-runtime-report.md`

The report must distinguish:
- runtime components wired
- runtime components validated
- old fixed-one-slot behavior
- new delay contract
- tests added
- tests run
- no-drift flags
