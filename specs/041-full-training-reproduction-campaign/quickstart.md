# Quickstart: Full Training/Reproduction Campaign

## Purpose

Run the Feature 041 readiness, pilot, and regression validation gate before any expensive full-campaign execution.

## Prerequisites

- Use the approved interpreter: `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python`
- Ensure the active feature pointer resolves to `specs/041-full-training-reproduction-campaign`
- Do not add or change dependency files

## Validation Command

Run the full validation gate:

```bash
PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest \
  tests.unit.test_full_training_campaign_config \
  tests.unit.test_full_training_replay_contract \
  tests.integration.test_campaign_readiness_gate \
  tests.integration.test_full_training_candidate_gate \
  tests.integration.test_full_training_pilot \
  tests.integration.test_full_training_report \
  tests.integration.test_full_training_scope_guard \
  tests.unit.test_smoke_training_contract \
  tests.integration.test_smoke_training_report \
  tests.integration.test_smoke_training_determinism \
  tests.unit.test_paper_hoodie_network_config \
  tests.unit.test_paper_hoodie_network_shapes \
  tests.integration.test_paper_hoodie_network_report \
  tests.unit.test_training_foundation_contract \
  tests.integration.test_training_foundation_contract_report \
  tests.integration.test_training_readiness_gate \
  tests.unit.test_execution_model \
  tests.unit.test_task_compute_state \
  tests.unit.test_deadline_expiration \
  tests.unit.test_link_rate_config \
  tests.unit.test_link_rate_transmission_delay \
  tests.unit.test_public_cloud_capacity_sharing \
  tests.unit.test_reproducibility_bundle \
  tests.unit.test_runtime_adoption_approved_assumption_registry \
  tests.integration.test_execution_time_contract_report \
  tests.integration.test_execution_time_flow \
  tests.integration.test_transmission_delay_runtime_report \
  tests.integration.test_transmission_delay_runtime_wiring \
  tests.integration.test_public_cloud_capacity_sharing_report \
  tests.integration.test_public_cloud_capacity_sharing_flow \
  tests.integration.test_deadline_timeout_off_by_one_report \
  tests.integration.test_reproducibility_bundle_flow
```

## Campaign Commands

Run the readiness probe:

```bash
PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m src.analysis.full_training_reproduction_campaign --stage readiness_probe
```

Run the bounded pilot stage:

```bash
PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m src.analysis.full_training_reproduction_campaign --stage pilot_training --episodes 10
```

Run the gated full campaign candidate only after readiness and pilot gates pass:

```bash
PYTHONPATH=/Users/hadi/Documents/GitHub/hoodie_sim_v2 /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m src.analysis.full_training_reproduction_campaign --stage full_training_candidate --episodes 5000 --enable-full-campaign
```

Warning: the full campaign remains blocked unless the readiness probe passes, the pilot stage passes, and the explicit full-campaign flag or command is supplied.

## Expected Artifacts

- `artifacts/analysis/full-training-reproduction-campaign/campaign-readiness-report.json`
- `artifacts/analysis/full-training-reproduction-campaign/campaign-readiness-report.md`
- `artifacts/analysis/full-training-reproduction-campaign/training-campaign-report.json`
- `artifacts/analysis/full-training-reproduction-campaign/training-campaign-report.md`

## Campaign Contract Expectations

- Readiness probe runs before any pilot or full campaign stage
- Pilot stage starts at 10 episodes
- Optional second pilot stage uses 25 episodes only if the first pilot passes cleanly
- Full 5000-episode campaign is configurable but only executable behind explicit command or flag
- Replay comes from live `HoodieGymEnvironment` rollouts only
- Train and eval traces stay disjoint
- Delayed rewards remain tied only to completion or drop
- Pending-at-horizon transitions remain non-terminal
- No automatic paper reproduction claim

## Notes

- Feature 037 is reference-only baseline context for now.
- The target-update unit is `optimizer_step` and must remain an explicit campaign assumption.
