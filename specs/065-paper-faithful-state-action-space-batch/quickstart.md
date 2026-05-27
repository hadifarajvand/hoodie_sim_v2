# Quickstart: Feature 065

## Run implementation validation

```bash
python3 -m unittest \
  tests.unit.test_paper_faithful_state_action_space_batch_schema \
  tests.unit.test_paper_faithful_state_action_space_batch_metrics \
  tests.unit.test_paper_faithful_state_action_space_batch_behavior_equivalence \
  tests.unit.test_paper_state_vector \
  tests.unit.test_paper_action_space \
  tests.unit.test_paper_load_history \
  tests.integration.test_paper_faithful_state_action_space_batch \
  tests.integration.test_paper_faithful_state_action_space_batch_report \
  tests.integration.test_paper_faithful_state_action_space_batch_scope_guard

python3 -m src.analysis.paper_faithful_state_action_space_batch
```

## Inspect report

```bash
python3 - <<'PY'
import json
p = 'artifacts/analysis/paper-faithful-state-action-space-batch/paper-faithful-state-action-space-batch-report.json'
d = json.load(open(p))
print('feature_064_verified =', d.get('feature_064_verified'))
print('paper_state_contract_summary =', d.get('paper_state_contract_summary'))
print('waiting_time_summary =', d.get('waiting_time_summary'))
print('public_queue_vector_summary =', d.get('public_queue_vector_summary'))
print('load_history_summary =', d.get('load_history_summary'))
print('forecast_input_summary =', d.get('forecast_input_summary'))
print('destination_action_space_summary =', d.get('destination_action_space_summary'))
print('legal_mask_summary =', d.get('legal_mask_summary'))
print('compatibility_summary =', d.get('compatibility_summary'))
print('safety_summary =', d.get('safety_summary'))
print('remaining_blockers =', d.get('remaining_blockers'))
print('final_verdict =', d.get('final_verdict'))
print('recommended_next_feature =', d.get('recommended_next_feature'))
PY
```

## Expected passing result

```text
final_verdict = paper_faithful_state_action_space_batch_passed
recommended_next_feature = Feature 066 — Distributed Multi-Agent HOODIE Training Batch
remaining_blockers = []
```

## Required git proof

```bash
git status --short
git diff --name-only main...HEAD
git diff --stat main...HEAD
git diff --cached --name-only
```
