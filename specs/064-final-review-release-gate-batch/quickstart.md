# Quickstart: Feature 064

## Run implementation validation

```bash
python3 -m unittest \
  tests.unit.test_final_review_release_gate_batch_schema \
  tests.unit.test_final_review_release_gate_batch_metrics \
  tests.unit.test_final_review_release_gate_batch_behavior_equivalence \
  tests.integration.test_final_review_release_gate_batch \
  tests.integration.test_final_review_release_gate_batch_report \
  tests.integration.test_final_review_release_gate_batch_scope_guard

python3 -m src.analysis.final_review_release_gate_batch
```

## Inspect report

```bash
python3 - <<'PY'
import json
p = 'artifacts/analysis/final-review-release-gate-batch/final-review-release-gate-batch-report.json'
d = json.load(open(p))
print('feature_063_verified =', d.get('feature_063_verified'))
print('batch_items_covered =', d.get('batch_items_covered'))
print('repository_state_audit_summary =', d.get('repository_state_audit_summary'))
print('artifact_completeness_summary =', d.get('artifact_completeness_summary'))
print('claim_boundary_review_summary =', d.get('claim_boundary_review_summary'))
print('release_tag_readiness_summary =', d.get('release_tag_readiness_summary'))
print('handoff_summary =', d.get('handoff_summary'))
print('safety_summary =', d.get('safety_summary'))
print('remaining_blockers =', d.get('remaining_blockers'))
print('final_verdict =', d.get('final_verdict'))
print('recommended_next_feature =', d.get('recommended_next_feature'))
PY
```

## Expected passing result

```text
final_verdict = final_review_release_gate_batch_passed
recommended_next_feature = Release tag creation or thesis/paper writing workflow
remaining_blockers = []
```

## Required git proof

```bash
git status --short
git diff --name-only main...HEAD
git diff --stat main...HEAD
git diff --cached --name-only
```
