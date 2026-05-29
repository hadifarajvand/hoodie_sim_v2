# Quickstart

```bash
python3 -m unittest \
  tests.unit.test_paper_baseline_suite_batch_schema \
  tests.unit.test_paper_baseline_suite_batch_metrics \
  tests.unit.test_paper_baseline_suite_batch_behavior_equivalence \
  tests.unit.test_baseline_policy_legality \
  tests.unit.test_baseline_policy_registry \
  tests.unit.test_mleo_policy \
  tests.integration.test_paper_baseline_suite_batch \
  tests.integration.test_paper_baseline_suite_batch_report \
  tests.integration.test_paper_baseline_suite_batch_scope_guard
python3 -m src.analysis.paper_baseline_suite_batch
```

