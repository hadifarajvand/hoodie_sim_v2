# Feature 081 HOODIE Evaluation & Baseline Benchmarking Artifact Bundle

- output_dir: `artifacts/feature_081_evaluation_baseline`
- raw_row_count: `2520`
- policies: `5`
- scenarios: `7`
- metrics: `10`
- compatibility_mode_used: `True`

## Generated Files
- `raw_rows.json`
- `raw_rows.csv`
- `aggregate_by_policy.json`
- `aggregate_by_policy.csv`
- `ranking_by_metric.json`
- `ranking_by_metric.csv`
- `execution_manifest.json`

## Compatibility-Mode Policies
- HOODIE_PROPOSED
- ORIGINAL_HOODIE_BASELINE

# Feature 081 HOODIE Evaluation & Baseline Benchmarking Report

- status: `hoodie_evaluation_runner_ready`
- passed: `True`
- readiness_level: `mostly_implemented`
- policies: 5
- scenarios: 7
- metrics: 10

## Claim Boundary
- HOODIE_PROPOSED means the Feature 080 base-paper proposed method only.
- No ranking claim is made beyond metric-by-metric deterministic ordering.
- No baseline evaluation claim is made beyond explicit policy adapters.
- No DCQ method is introduced.
- No thesis method is introduced.
- No empirical full-paper reproduction is claimed.
- No statistical superiority claim is made.
- Feature 081 does not redesign Feature 080 internals.

## Scope Proof
- no ranking method beyond metric-by-metric deterministic ranking
- no baseline evaluation drift into Feature 080 internals
- no DCQ logic
- no thesis method
- HOODIE_PROPOSED remains the Feature 080 base-paper proposed method only

## Policy Coverage
- HOODIE_PROPOSED: implemented (compatibility_adapter)
- ORIGINAL_HOODIE_BASELINE: implemented (compatibility_adapter)
- RANDOM_POLICY: implemented (seeded_adapter)
- LOCAL_ONLY: implemented (direct_adapter)
- CLOUD_ONLY: implemented (direct_adapter)

## Scenario Coverage
- light_load_no_deadline_pressure: implemented
- tight_deadline_pressure: implemented
- legal_horizontal_offload: implemented
- illegal_horizontal_destination_attempt: implemented
- cloud_vertical_fallback: implemented
- timeout_drop_case: implemented
- mixed_local_horizontal_cloud_candidates: implemented

## Metric Rankings
### average_delay
- 1. CLOUD_ONLY = 4.532258064516129
- 2. ORIGINAL_HOODIE_BASELINE = 4.532258064516129
- 3. HOODIE_PROPOSED = 4.82258064516129
- 4. LOCAL_ONLY = 4.82258064516129
- 5. RANDOM_POLICY = 5.403225806451613
### average_reward
- 1. CLOUD_ONLY = -7.748677248677249
- 2. ORIGINAL_HOODIE_BASELINE = -7.748677248677249
- 3. HOODIE_PROPOSED = -8.653439153439153
- 4. LOCAL_ONLY = -8.653439153439153
- 5. RANDOM_POLICY = -11.415343915343914
### completion_rate
- 1. CLOUD_ONLY = 0.8928571428571429
- 2. ORIGINAL_HOODIE_BASELINE = 0.8928571428571429
- 3. HOODIE_PROPOSED = 0.8690476190476191
- 4. LOCAL_ONLY = 0.8690476190476191
- 5. RANDOM_POLICY = 0.7976190476190477
### deadline_violation_rate
- 1. CLOUD_ONLY = 0.3333333333333333
- 2. ORIGINAL_HOODIE_BASELINE = 0.3333333333333333
- 3. HOODIE_PROPOSED = 0.40476190476190477
- 4. LOCAL_ONLY = 0.40476190476190477
- 5. RANDOM_POLICY = 0.4365079365079365
### illegal_action_rejection_count
- 1. CLOUD_ONLY = 18.0
- 2. ORIGINAL_HOODIE_BASELINE = 18.0
- 3. HOODIE_PROPOSED = 18.0
- 4. LOCAL_ONLY = 18.0
- 5. RANDOM_POLICY = 18.0
### queue_stability_score
- 1. CLOUD_ONLY = 0.24807256235827663
- 2. ORIGINAL_HOODIE_BASELINE = 0.24807256235827663
- 3. HOODIE_PROPOSED = 0.24807256235827663
- 4. LOCAL_ONLY = 0.24807256235827663
- 5. RANDOM_POLICY = 0.24807256235827663
### throughput
- 1. CLOUD_ONLY = 0.42896825396825394
- 2. ORIGINAL_HOODIE_BASELINE = 0.42896825396825394
- 3. HOODIE_PROPOSED = 0.41865079365079366
- 4. LOCAL_ONLY = 0.41865079365079366
- 5. RANDOM_POLICY = 0.3855820105820106
### timeout_drop_rate
- 1. CLOUD_ONLY = 0.10714285714285714
- 2. ORIGINAL_HOODIE_BASELINE = 0.10714285714285714
- 3. HOODIE_PROPOSED = 0.13095238095238096
- 4. LOCAL_ONLY = 0.13095238095238096
- 5. RANDOM_POLICY = 0.20238095238095238
### total_reward
- 1. CLOUD_ONLY = -4244.0
- 2. ORIGINAL_HOODIE_BASELINE = -4244.0
- 3. HOODIE_PROPOSED = -4788.0
- 4. LOCAL_ONLY = -4788.0
- 5. RANDOM_POLICY = -6260.0
### unavailable_drop_rate
- 1. CLOUD_ONLY = 0.0
- 2. ORIGINAL_HOODIE_BASELINE = 0.0
- 3. HOODIE_PROPOSED = 0.0
- 4. LOCAL_ONLY = 0.0
- 5. RANDOM_POLICY = 0.0

## Remaining Gaps
- HOODIE_PROPOSED and ORIGINAL_HOODIE_BASELINE are represented through deterministic compatibility adapters because Feature 080 source internals are not modified by Feature 081.
