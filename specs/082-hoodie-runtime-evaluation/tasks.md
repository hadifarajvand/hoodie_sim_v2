# Feature 082 Tasks — Policy Adapter Repair

## Task Group A — Confirm Failure
- Read aggregate_by_policy.csv
- Confirm HOODIE_PROPOSED == LOCAL_ONLY
- Confirm ORIGINAL_HOODIE_BASELINE == CLOUD_ONLY

## Task Group B — Inspect Adapters
- Inspect policies.py, runner.py, Feature 080 package
- Identify proxy/alias behavior

## Task Group C — Repair HOODIE_PROPOSED
- Connect to Feature 080 components
- Use hybrid local/horizontal/vertical candidates
- Add decision trace
- Ensure it differs from LOCAL_ONLY

## Task Group D — Repair ORIGINAL_HOODIE_BASELINE
- Remove fixed CLOUD_ONLY behavior
- Implement paper-aligned hybrid baseline adapter
- Add decision trace
- Ensure it differs from CLOUD_ONLY

## Task Group E — Add Tests
- Unit tests for HOODIE_PROPOSED and ORIGINAL_HOODIE_BASELINE identity
- Integration tests to ensure artifacts reflect differences
- Scope guard tests

## Task Group F — Artifact Regeneration
- raw_rows.json/csv
- aggregate_by_policy.json/csv
- ranking_by_metric.json/csv
- feature_082_runtime_evaluation_report.json/md
- execution_manifest.json

## Task Group G — Report & Manifest
- Add identity-proof section
- Document compatibility-limitation if any
- Include claim boundary and scope proof

## Task Group H — Final Validation
- git diff --check
- Unit tests pass
- Integration tests pass
- Artifact write and validation pass
- Branch pushed