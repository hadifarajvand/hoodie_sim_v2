# Quickstart: Paper-default Terminal Exposure Probe

## Purpose

Run the diagnostic probe that checks whether terminal exposure appears at the paper-default horizon `T = 110`.

## Prerequisites

- Use the approved interpreter: `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python`
- Ensure the active feature pointer resolves to `specs/042-paper-default-terminal-exposure-probe`
- Do not change runtime, dependency, or policy semantics

## Probe Command

Run the diagnostic probe:

```bash
PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m src.analysis.paper_default_terminal_exposure_probe
```

## Expected Artifacts

- `artifacts/analysis/paper-default-terminal-exposure-probe/terminal-exposure-report.json`
- `artifacts/analysis/paper-default-terminal-exposure-probe/terminal-exposure-report.md`

## Validation Command

```bash
PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest \
  tests.unit.test_paper_default_terminal_exposure_config \
  tests.unit.test_paper_default_terminal_exposure_schema \
  tests.integration.test_paper_default_terminal_exposure_probe \
  tests.integration.test_paper_default_terminal_exposure_report \
  tests.integration.test_paper_default_terminal_exposure_scope_guard \
  tests.unit.test_paper_hoodie_network_config \
  tests.unit.test_paper_hoodie_network_shapes \
  tests.integration.test_paper_hoodie_network_report \
  tests.integration.test_smoke_training_report \
  tests.integration.test_smoke_training_determinism \
  tests.unit.test_training_foundation_contract \
  tests.integration.test_training_foundation_contract_report \
  tests.integration.test_training_readiness_gate \
  tests.integration.test_execution_time_flow \
  tests.integration.test_transmission_delay_runtime_wiring \
  tests.integration.test_public_cloud_capacity_sharing_flow \
  tests.integration.test_deadline_timeout_off_by_one_audit
```

## Probe Expectations

- Probe uses `T = 110`, not `T = 20`
- Timeout remains `20 slots`
- Delayed rewards are emitted only on completion or drop
- Pending-at-horizon remains non-terminal
- Local, horizontal, and vertical action counts are separated
- Legal action masks are respected
- No training is performed
- Feature 041 remains readiness-blocked unless separately approved later
