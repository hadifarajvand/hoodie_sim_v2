# Quickstart: Feature 063

## Run implementation validation

```bash
python3 -m unittest \
  tests.unit.test_results_export_reproducibility_documentation_batch_schema \
  tests.unit.test_results_export_reproducibility_documentation_batch_metrics \
  tests.unit.test_results_export_reproducibility_documentation_batch_behavior_equivalence \
  tests.integration.test_results_export_reproducibility_documentation_batch \
  tests.integration.test_results_export_reproducibility_documentation_batch_report \
  tests.integration.test_results_export_reproducibility_documentation_batch_scope_guard

python3 -m src.analysis.results_export_reproducibility_documentation_batch
```

## Inspect report

```bash
python3 - <<'PY'
import json
p = 'artifacts/analysis/results-export-reproducibility-documentation-batch/results-export-reproducibility-documentation-batch-report.json'
d = json.load(open(p))
print('feature_062_verified =', d.get('feature_062_verified'))
print('batch_items_covered =', d.get('batch_items_covered'))
print('final_integrity_audit_summary =', d.get('final_integrity_audit_summary'))
print('results_export_summary =', d.get('results_export_summary'))
print('reproducibility_package_summary =', d.get('reproducibility_package_summary'))
print('mechanism_documentation_summary =', d.get('mechanism_documentation_summary'))
print('artifact_index_summary =', d.get('artifact_index_summary'))
print('claim_boundary_summary =', d.get('claim_boundary_summary'))
print('safety_summary =', d.get('safety_summary'))
print('remaining_blockers =', d.get('remaining_blockers'))
print('final_verdict =', d.get('final_verdict'))
print('recommended_next_feature =', d.get('recommended_next_feature'))
PY
```

## Expected passing result

```text
final_verdict = results_export_reproducibility_documentation_batch_passed
recommended_next_feature = Feature 064 — Final Review and Release Gate
remaining_blockers = []
```

## Required git proof

```bash
git status --short
git diff --name-only main...HEAD
git diff --stat main...HEAD
git diff --cached --name-only
```
