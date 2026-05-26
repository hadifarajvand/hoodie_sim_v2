# Quickstart: Feature 062

## Run implementation validation

```bash
python3 -m unittest \
  tests.unit.test_multi_seed_campaign_ablation_batch_schema \
  tests.unit.test_multi_seed_campaign_ablation_batch_metrics \
  tests.unit.test_multi_seed_campaign_ablation_batch_behavior_equivalence \
  tests.integration.test_multi_seed_campaign_ablation_batch \
  tests.integration.test_multi_seed_campaign_ablation_batch_report \
  tests.integration.test_multi_seed_campaign_ablation_batch_scope_guard

python3 -m src.analysis.multi_seed_campaign_ablation_batch
```

## Inspect report

```bash
python3 - <<'PY'
import json
p = 'artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-campaign-ablation-batch-report.json'
d = json.load(open(p))
print('feature_061_verified =', d.get('feature_061_verified'))
print('batch_items_covered =', d.get('batch_items_covered'))
print('multi_seed_gate_summary =', d.get('multi_seed_gate_summary'))
print('multi_seed_campaign_summary =', d.get('multi_seed_campaign_summary'))
print('multi_seed_aggregation_summary =', d.get('multi_seed_aggregation_summary'))
print('ablation_gate_summary =', d.get('ablation_gate_summary'))
print('ablation_execution_summary =', d.get('ablation_execution_summary'))
print('artifact_manifest_summary =', d.get('artifact_manifest_summary'))
print('safety_summary =', d.get('safety_summary'))
print('remaining_blockers =', d.get('remaining_blockers'))
print('final_verdict =', d.get('final_verdict'))
print('recommended_next_feature =', d.get('recommended_next_feature'))
PY
```

## Expected passing result

```text
final_verdict = multi_seed_campaign_ablation_batch_passed
recommended_next_feature = Feature 063 — Results Export, Reproducibility, and Final Documentation Batch
remaining_blockers = []
```

## Required git proof

```bash
git status --short
git diff --name-only main...HEAD
git diff --stat main...HEAD
git diff --cached --name-only
```
