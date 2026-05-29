# Quickstart

```bash
python3 -m unittest \
  tests.unit.test_paper_traffic_queue_communication_fidelity_batch_schema \
  tests.unit.test_paper_traffic_queue_communication_fidelity_batch_metrics \
  tests.unit.test_paper_traffic_queue_communication_fidelity_batch_behavior_equivalence \
  tests.unit.test_paper_bernoulli_arrivals \
  tests.unit.test_paper_timeout_semantics \
  tests.unit.test_paper_link_delay \
  tests.unit.test_paper_pubsub_recovery \
  tests.integration.test_paper_traffic_queue_communication_fidelity_batch \
  tests.integration.test_paper_traffic_queue_communication_fidelity_batch_report \
  tests.integration.test_paper_traffic_queue_communication_fidelity_batch_scope_guard
python3 -m src.analysis.paper_traffic_queue_communication_fidelity_batch
```

