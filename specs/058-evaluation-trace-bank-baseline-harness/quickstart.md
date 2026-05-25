# Quickstart: Feature 058

## Run implementation validation

```bash
python3 -m unittest \
  tests.unit.test_evaluation_trace_bank_baseline_harness_schema \
  tests.unit.test_evaluation_trace_bank_baseline_harness_metrics \
  tests.unit.test_evaluation_trace_bank_baseline_harness_behavior_equivalence \
  tests.integration.test_evaluation_trace_bank_baseline_harness \
  tests.integration.test_evaluation_trace_bank_baseline_harness_report \
  tests.integration.test_evaluation_trace_bank_baseline_harness_scope_guard

python3 -m src.analysis.evaluation_trace_bank_baseline_harness
```

## Inspect report

```bash
python3 - <<'PY'
import json
p = 'artifacts/analysis/evaluation-trace-bank-baseline-harness/evaluation-trace-bank-baseline-harness-report.json'
d = json.load(open(p))
print('feature_057_pilot_verified =', d.get('feature_057_pilot_verified'))
print('evaluation_trace_bank_summary =', d.get('evaluation_trace_bank_summary'))
print('train_eval_separation_summary =', d.get('train_eval_separation_summary'))
print('baseline_policy_registry_summary =', d.get('baseline_policy_registry_summary'))
print('baseline_evaluation_harness_summary =', d.get('baseline_evaluation_harness_summary'))
print('metric_schema_summary =', d.get('metric_schema_summary'))
print('determinism_summary =', d.get('determinism_summary'))
print('behavior_safety_summary =', d.get('behavior_safety_summary'))
print('remaining_blockers =', d.get('remaining_blockers'))
print('final_verdict =', d.get('final_verdict'))
print('recommended_next_feature =', d.get('recommended_next_feature'))
PY
```

## Expected passing result

```text
final_verdict = evaluation_trace_bank_baseline_harness_ready
recommended_next_feature = Feature 059 — Full Paper-Default Training Campaign Gate
remaining_blockers = []
```
