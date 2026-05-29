# Quickstart

```bash
python3 -m unittest \
  tests.unit.test_full_hoodie_mechanism_fidelity_batch_schema \
  tests.unit.test_full_hoodie_mechanism_fidelity_batch_metrics \
  tests.unit.test_full_hoodie_mechanism_fidelity_batch_behavior_equivalence \
  tests.unit.test_hoodie_neighbor_graph \
  tests.unit.test_hoodie_congestion_control \
  tests.unit.test_hoodie_reward_pipeline \
  tests.unit.test_hoodie_synchronization \
  tests.integration.test_full_hoodie_mechanism_fidelity_batch \
  tests.integration.test_full_hoodie_mechanism_fidelity_batch_report \
  tests.integration.test_full_hoodie_mechanism_fidelity_batch_scope_guard
python3 -m src.analysis.full_hoodie_mechanism_fidelity_batch
```

