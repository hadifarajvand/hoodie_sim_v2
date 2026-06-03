# Tasks — Feature 083 HOODIE Paper Baseline Fidelity

## Task Group A — Paper Extraction
- [ ] Read HOODIE paper evaluation section.
- [ ] Extract baseline names, reported metrics, and behavior.

## Task Group B — Spec Kit Update
- [ ] Remove ORIGINAL_HOODIE_BASELINE
- [ ] Add new baselines: RO, FLC, VO, HO, BCO, MQO
- [ ] Update spec.md, plan.md, tasks.md
- [ ] Add Paper Baseline Extraction Requirements section
- [ ] Update readiness levels

## Task Group C — Adapter Implementation
- [ ] Implement each paper baseline adapter
- [ ] Connect HOODIE to Feature 080 proposed method
- [ ] Ensure adapters produce distinct metrics
- [ ] Add decision traces

## Task Group D — Artifact Regeneration
- [ ] Generate raw_rows.json/csv
- [ ] Generate aggregate_by_policy.json/csv
- [ ] Generate ranking_by_metric.json/csv
- [ ] Generate feature_083_runtime_evaluation_report.json/md
- [ ] Generate execution_manifest.json

## Task Group E — Testing
- [ ] Unit test each adapter
- [ ] Integration tests for artifact generation
- [ ] Verify HOODIE != each baseline in at least one core metric
- [ ] Validate report and manifest