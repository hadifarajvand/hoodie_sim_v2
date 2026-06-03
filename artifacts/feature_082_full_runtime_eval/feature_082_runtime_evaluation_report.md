# Feature 082 HOODIE Runtime Evaluation Artifact Bundle

- output_dir: `artifacts/feature_082_full_runtime_eval`
- raw_row_count: `7560`
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
- `feature_082_runtime_evaluation_report.json`
- `feature_082_runtime_evaluation_report.md`
- `execution_manifest.json`

## Compatibility-Mode Policies
- HOODIE_PROPOSED
- ORIGINAL_HOODIE_BASELINE

# Feature 082 HOODIE Runtime Evaluation Report

- status: `hoodie_runtime_evaluation_ready`
- passed: `True`
- readiness_level: `mostly_implemented`
- raw_rows: 7560
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
- Feature 082 does not redesign Feature 080 internals.

## Scope Proof
- no ranking method beyond metric-by-metric deterministic ranking
- no baseline evaluation drift into Feature 080 internals
- no DCQ logic
- no thesis method
- HOODIE_PROPOSED remains the Feature 080 base-paper proposed method only

## Compatibility-Mode Policies
- HOODIE_PROPOSED
- ORIGINAL_HOODIE_BASELINE

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

## Metric Coverage
- completion_rate: completed_count / total_task_count
- timeout_drop_rate: dropped_timeout_count / total_task_count
- unavailable_drop_rate: dropped_unavailable_count / total_task_count
- deadline_violation_rate: deadline_violation_count / total_task_count
- average_delay: mean(completion_time - arrival_time) for completed tasks
- average_reward: mean(reward) across task outcomes
- total_reward: sum(reward) across task outcomes
- throughput: completed_count / total_task_count
- queue_stability_score: 1 / (1 + average_queue_length + positive_queue_growth)
- illegal_action_rejection_count: count of illegal candidate rejection events

## Metric Rankings
### average_delay
- 1. CLOUD_ONLY = 5.04384133611691
- 2. ORIGINAL_HOODIE_BASELINE = 5.04384133611691
- 3. HOODIE_PROPOSED = 5.186582809224318
- 4. LOCAL_ONLY = 5.186582809224318
- 5. RANDOM_POLICY = 5.325239146431199
### average_reward
- 1. CLOUD_ONLY = -6.777777777777778
- 2. ORIGINAL_HOODIE_BASELINE = -6.777777777777778
- 3. HOODIE_PROPOSED = -7.051587301587301
- 4. LOCAL_ONLY = -7.051587301587301
- 5. RANDOM_POLICY = -8.833994708994709
### completion_rate
- 1. CLOUD_ONLY = 0.9503968253968254
- 2. ORIGINAL_HOODIE_BASELINE = 0.9503968253968254
- 3. HOODIE_PROPOSED = 0.9464285714285714
- 4. LOCAL_ONLY = 0.9464285714285714
- 5. RANDOM_POLICY = 0.8988095238095238
### deadline_violation_rate
- 1. CLOUD_ONLY = 0.10317460317460317
- 2. ORIGINAL_HOODIE_BASELINE = 0.10317460317460317
- 3. HOODIE_PROPOSED = 0.12301587301587301
- 4. LOCAL_ONLY = 0.12301587301587301
- 5. RANDOM_POLICY = 0.13293650793650794
### illegal_action_rejection_count
- 1. CLOUD_ONLY = 0.0
- 2. ORIGINAL_HOODIE_BASELINE = 0.0
- 3. HOODIE_PROPOSED = 0.0
- 4. LOCAL_ONLY = 0.0
- 5. RANDOM_POLICY = 69.0
### queue_stability_score
- 1. CLOUD_ONLY = 0.23214285714285715
- 2. ORIGINAL_HOODIE_BASELINE = 0.23214285714285715
- 3. HOODIE_PROPOSED = 0.23214285714285715
- 4. LOCAL_ONLY = 0.23214285714285715
- 5. RANDOM_POLICY = 0.23214285714285715
### throughput
- 1. CLOUD_ONLY = 0.9503968253968254
- 2. ORIGINAL_HOODIE_BASELINE = 0.9503968253968254
- 3. HOODIE_PROPOSED = 0.9464285714285714
- 4. LOCAL_ONLY = 0.9464285714285714
- 5. RANDOM_POLICY = 0.8988095238095238
### timeout_drop_rate
- 1. CLOUD_ONLY = 0.0496031746031746
- 2. ORIGINAL_HOODIE_BASELINE = 0.0496031746031746
- 3. HOODIE_PROPOSED = 0.05357142857142857
- 4. LOCAL_ONLY = 0.05357142857142857
- 5. RANDOM_POLICY = 0.05555555555555555
### total_reward
- 1. CLOUD_ONLY = -10248.0
- 2. ORIGINAL_HOODIE_BASELINE = -10248.0
- 3. HOODIE_PROPOSED = -10662.0
- 4. LOCAL_ONLY = -10662.0
- 5. RANDOM_POLICY = -13357.0
### unavailable_drop_rate
- 1. CLOUD_ONLY = 0.0
- 2. ORIGINAL_HOODIE_BASELINE = 0.0
- 3. HOODIE_PROPOSED = 0.0
- 4. LOCAL_ONLY = 0.0
- 5. RANDOM_POLICY = 0.04563492063492063

## Remaining Gaps
- HOODIE_PROPOSED and ORIGINAL_HOODIE_BASELINE are represented through deterministic compatibility adapters because Feature 080 source internals are not modified by Feature 082.

## Manifest
- `execution_manifest.json`
