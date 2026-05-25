# Quickstart: Feature 056

## Run implementation validation

```bash
python3 -m unittest \
  tests.unit.test_target_update_replay_validation_schema \
  tests.unit.test_target_update_replay_validation_metrics \
  tests.unit.test_target_update_replay_validation_behavior_equivalence \
  tests.integration.test_target_update_replay_validation \
  tests.integration.test_target_update_replay_validation_report \
  tests.integration.test_target_update_replay_validation_scope_guard

python3 -m src.analysis.target_update_replay_training_validation
```

## Inspect report

```bash
python3 - <<'PY'
import json
p = 'artifacts/analysis/target-update-replay-training-validation/target-update-replay-validation-report.json'
d = json.load(open(p))
print('feature_055_smoke_verified =', d.get('feature_055_smoke_verified'))
print('replay_insertion_validated =', d.get('replay_insertion_validated'))
print('replay_sampling_validated =', d.get('replay_sampling_validated'))
print('optimizer_step_counter_validated =', d.get('optimizer_step_counter_validated'))
print('target_update_contract_validated =', d.get('target_update_contract_validated'))
print('target_sync_before_threshold_blocked =', d.get('target_sync_before_threshold_blocked'))
print('target_sync_at_threshold_validated =', d.get('target_sync_at_threshold_validated'))
print('remaining_blockers =', d.get('remaining_blockers'))
print('final_verdict =', d.get('final_verdict'))
print('recommended_next_feature =', d.get('recommended_next_feature'))
PY
```

## Expected passing result

```text
final_verdict = target_update_replay_validation_passed
recommended_next_feature = Feature 057 — Paper-Default Pilot Training Run
remaining_blockers = []
```
