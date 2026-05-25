# Quickstart: Feature 057

## Run implementation validation

```bash
python3 -m unittest \
  tests.unit.test_paper_default_pilot_training_run_schema \
  tests.unit.test_paper_default_pilot_training_run_metrics \
  tests.unit.test_paper_default_pilot_training_run_behavior_equivalence \
  tests.integration.test_paper_default_pilot_training_run \
  tests.integration.test_paper_default_pilot_training_run_report \
  tests.integration.test_paper_default_pilot_training_run_scope_guard

python3 -m src.analysis.paper_default_pilot_training_run
```

## Inspect report

```bash
python3 - <<'PY'
import json
p = 'artifacts/analysis/paper-default-pilot-training-run/paper-default-pilot-training-run-report.json'
d = json.load(open(p))
print('feature_056_validation_verified =', d.get('feature_056_validation_verified'))
print('live_environment_training_used =', d.get('live_environment_training_used'))
print('fixture_training_used =', d.get('fixture_training_used'))
print('episode_summary =', d.get('episode_summary'))
print('replay_summary =', d.get('replay_summary'))
print('optimizer_summary =', d.get('optimizer_summary'))
print('loss_summary =', d.get('loss_summary'))
print('reward_summary =', d.get('reward_summary'))
print('legal_action_summary =', d.get('legal_action_summary'))
print('checkpoint_summary =', d.get('checkpoint_summary'))
print('remaining_blockers =', d.get('remaining_blockers'))
print('final_verdict =', d.get('final_verdict'))
print('recommended_next_feature =', d.get('recommended_next_feature'))
PY
```

## Expected passing result

```text
final_verdict = paper_default_pilot_training_passed
recommended_next_feature = Feature 058 — Evaluation Trace Bank and Baseline Evaluation Harness
remaining_blockers = []
```
