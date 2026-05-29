# Quickstart

```bash
python3 -m unittest \
  tests.unit.test_distributed_multi_agent_hoodie_training_batch_schema \
  tests.unit.test_distributed_multi_agent_hoodie_training_batch_metrics \
  tests.unit.test_distributed_multi_agent_hoodie_training_batch_behavior_equivalence \
  tests.unit.test_distributed_agent_registry \
  tests.unit.test_distributed_agent_replay \
  tests.unit.test_distributed_epsilon_schedule \
  tests.unit.test_distributed_delayed_reward_assignment \
  tests.integration.test_distributed_multi_agent_hoodie_training_batch \
  tests.integration.test_distributed_multi_agent_hoodie_training_batch_report \
  tests.integration.test_distributed_multi_agent_hoodie_training_batch_scope_guard
python3 -m src.analysis.distributed_multi_agent_hoodie_training_batch
```

