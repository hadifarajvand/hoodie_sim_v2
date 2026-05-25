# Quickstart: Feature 060B

## Run implementation validation

```bash
python3 -m unittest \
  tests.unit.test_bind_full_campaign_real_torch_trainer_schema \
  tests.unit.test_bind_full_campaign_real_torch_trainer_metrics \
  tests.unit.test_bind_full_campaign_real_torch_trainer_behavior_equivalence \
  tests.integration.test_bind_full_campaign_real_torch_trainer \
  tests.integration.test_bind_full_campaign_real_torch_trainer_report \
  tests.integration.test_bind_full_campaign_real_torch_trainer_scope_guard

python3 -m unittest \
  tests.unit.test_full_paper_default_training_campaign_execution_schema \
  tests.unit.test_full_paper_default_training_campaign_execution_metrics \
  tests.unit.test_full_paper_default_training_campaign_execution_behavior_equivalence \
  tests.integration.test_full_paper_default_training_campaign_execution \
  tests.integration.test_full_paper_default_training_campaign_execution_report \
  tests.integration.test_full_paper_default_training_campaign_execution_scope_guard

python3 -m src.analysis.full_paper_default_training_campaign_execution
python3 -m src.analysis.bind_full_campaign_real_torch_trainer
```

## Inspect repair report

```bash
python3 - <<'PY'
import json
p = 'artifacts/analysis/bind-full-campaign-real-torch-trainer/bind-full-campaign-real-torch-trainer-report.json'
d = json.load(open(p))
print('feature_060a_audit_verified =', d.get('feature_060a_audit_verified'))
print('torch_environment_summary =', d.get('torch_environment_summary'))
print('real_trainer_binding_summary =', d.get('real_trainer_binding_summary'))
print('feature_060_repair_summary =', d.get('feature_060_repair_summary'))
print('artifact_regeneration_summary =', d.get('artifact_regeneration_summary'))
print('remaining_blockers =', d.get('remaining_blockers'))
print('final_verdict =', d.get('final_verdict'))
print('recommended_next_feature =', d.get('recommended_next_feature'))
PY
```

## Expected passing result

```text
final_verdict = real_torch_trainer_binding_repair_passed
recommended_next_feature = Feature 061 — Campaign Result Integrity and Comparison Readiness Audit
remaining_blockers = []
```
