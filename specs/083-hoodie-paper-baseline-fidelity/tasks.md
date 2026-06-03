# Tasks — Feature 083 HOODIE Paper Baseline Fidelity

## Task Group A — Paper Extraction
- [x] Read HOODIE paper evaluation section.
- [x] Extract baseline names, reported metrics, and behavior.

## Task Group B — Spec Kit Update
- [x] Remove ORIGINAL_HOODIE_BASELINE
- [x] Add new baselines: RO, FLC, VO, HO, BCO, MQO
- [x] Update spec.md, plan.md, tasks.md
- [x] Add Paper Baseline Extraction Requirements section
- [x] Update readiness levels

## Task Group C — Adapter Implementation
- [x] Implement each paper baseline adapter
- [x] Connect HOODIE to Feature 080 proposed method
- [x] Ensure adapters produce distinct metrics
- [x] Add decision traces

## Task Group D — Artifact Regeneration
- [x] Generate raw_rows.json/csv
- [x] Generate aggregate_by_policy.json/csv
- [x] Generate ranking_by_metric.json/csv
- [x] Generate feature_083_runtime_evaluation_report.json/md
- [x] Generate execution_manifest.json

## Task Group E — Testing
- [x] Unit test each adapter
- [x] Integration tests for artifact generation
- [x] Verify HOODIE != each baseline in at least one core metric
- [x] Validate report and manifest
