# Feature 085 HOODIE Baseline Fidelity Audit Artifact Bundle

- output_dir: `artifacts/feature_085_full_audit`
- raw_row_count: `10584`
- policies: `7`
- scenarios: `7`
- metrics: `11`
- compatibility_mode_used: `False`

## Generated Files
- `raw_rows.json`
- `raw_rows.csv`
- `aggregate_by_policy.json`
- `aggregate_by_policy.csv`
- `ranking_by_metric.json`
- `ranking_by_metric.csv`
- `feature_085_audit_report.json`
- `feature_085_audit_report.md`
- `execution_manifest.json`

## Compatibility-Mode Policies
- no compatibility-mode policies remain

# Feature 085 HOODIE Baseline Fidelity Audit Report

- status: `hoodie_paper_baseline_fidelity_audit_ready`
- passed: `True`
- readiness_level: `fully_implemented`
- raw_rows: 10584
- policies: 7
- scenarios: 7
- metrics: 11

## Claim Boundary
- HOODIE means the Feature 080 proposed method only.
- Baselines are paper-aligned and restricted to RO, FLC, VO, HO, BCO, and MLEO.
- Deterministic evaluation is used for comparison and artifact generation.
- No statistical superiority claim is made.
- No full empirical paper reproduction is claimed.

## Scope Proof
- no DCQ logic
- no thesis method
- no custom queue redesign
- no legacy minimum-queue policy remains as an active baseline label
- HOODIE remains the Feature 080 proposed method only
- baselines are paper-aligned
- no empirical full-paper reproduction claim
- no statistical superiority claim
- PR #24 remains blocked until baseline correction and formula audit validations pass

## Compatibility-Mode Policies
- no compatibility-mode policies remain

## Policy Coverage
- HOODIE: implemented (feature_080_runtime_path)
- RO: implemented (paper_baseline_adapter)
- FLC: implemented (paper_baseline_adapter)
- VO: implemented (paper_baseline_adapter)
- HO: implemented (paper_baseline_adapter)
- BCO: implemented (paper_baseline_adapter)
- MLEO: implemented (paper_baseline_adapter)

## Paper Baseline Mapping
- HOODIE -> Feature 080 proposed-method runtime path
- RO -> Random Offloader baseline
- FLC -> Full Local Computing baseline
- VO -> Vertical Offloader baseline
- HO -> Horizontal Offloader baseline
- BCO -> Balanced Cyclic Offloader baseline
- MLEO -> Minimum Latency Estimate Offloader baseline

## Primary Paper Metrics
- task_completion_delay
- task_drop_ratio

## Secondary Repository Metrics
- completion_rate
- timeout_drop_rate
- unavailable_drop_rate
- deadline_violation_rate
- average_reward
- total_reward
- throughput
- queue_stability_score
- illegal_action_rejection_count

## Identity Proof
- HOODIE differs from RO on metrics: task_completion_delay, task_drop_ratio, average_reward, total_reward, completion_rate, timeout_drop_rate, unavailable_drop_rate, deadline_violation_rate, throughput, illegal_action_rejection_count.
- HOODIE differs from FLC on metrics: task_completion_delay, task_drop_ratio, average_reward, total_reward, completion_rate, timeout_drop_rate, deadline_violation_rate, throughput.
- HOODIE differs from VO on metrics: task_completion_delay, task_drop_ratio, average_reward, total_reward, completion_rate, timeout_drop_rate, deadline_violation_rate, throughput.
- HOODIE differs from HO on metrics: task_completion_delay, task_drop_ratio, average_reward, total_reward, completion_rate, timeout_drop_rate, unavailable_drop_rate, deadline_violation_rate, throughput, illegal_action_rejection_count.
- HOODIE differs from BCO on metrics: task_completion_delay, task_drop_ratio, average_reward, total_reward, completion_rate, timeout_drop_rate, unavailable_drop_rate, deadline_violation_rate, throughput, illegal_action_rejection_count.
- HOODIE differs from MLEO on metrics: none.

## Scenario Coverage
- light_load_no_deadline_pressure: implemented
- tight_deadline_pressure: implemented
- legal_horizontal_offload: implemented
- illegal_horizontal_destination_attempt: implemented
- cloud_vertical_fallback: implemented
- timeout_drop_case: implemented
- mixed_local_horizontal_cloud_candidates: implemented

## Metric Coverage
- task_completion_delay: mean(completion_time - arrival_time) for completed tasks
- task_drop_ratio: (dropped_timeout_count + dropped_unavailable_count) / total_task_count
- completion_rate: completed_count / total_task_count
- timeout_drop_rate: dropped_timeout_count / total_task_count
- unavailable_drop_rate: dropped_unavailable_count / total_task_count
- deadline_violation_rate: deadline_violation_count / total_task_count
- average_reward: mean(reward) across task outcomes
- total_reward: sum(reward) across task outcomes
- throughput: completed_count / total_task_count
- queue_stability_score: 1 / (1 + average_queue_length + positive_queue_growth)
- illegal_action_rejection_count: count of illegal candidate rejection events

## Formula Audit
- see `specs/085-hoodie-paper-baseline-fidelity-audit/formula-mapping-matrix.md`
- see `specs/085-hoodie-paper-baseline-fidelity-audit/baseline-mapping-matrix.md`

## Metric Rankings
### Primary Paper Metrics
#### task_completion_delay
- 1. HOODIE = 4.902286902286902
- 2. MLEO = 4.902286902286902
- 3. VO = 5.04384133611691
- 4. FLC = 5.186582809224318
- 5. BCO = 5.2967032967032965
- 6. RO = 5.325239146431199
- 7. HO = 5.834170854271357
#### task_drop_ratio
- 1. HOODIE = 0.04563492063492063
- 2. MLEO = 0.04563492063492063
- 3. VO = 0.0496031746031746
- 4. FLC = 0.05357142857142857
- 5. BCO = 0.09722222222222222
- 6. RO = 0.10119047619047619
- 7. HO = 0.21031746031746032

### Secondary Repository Metrics
#### completion_rate
- 1. HOODIE = 0.9543650793650794
- 2. MLEO = 0.9543650793650794
- 3. VO = 0.9503968253968254
- 4. FLC = 0.9464285714285714
- 5. BCO = 0.9027777777777778
- 6. RO = 0.8988095238095238
- 7. HO = 0.7896825396825397
#### timeout_drop_rate
- 1. HOODIE = 0.04563492063492063
- 2. MLEO = 0.04563492063492063
- 3. VO = 0.0496031746031746
- 4. FLC = 0.05357142857142857
- 5. BCO = 0.05555555555555555
- 6. RO = 0.05555555555555555
- 7. HO = 0.06746031746031746
#### unavailable_drop_rate
- 1. HOODIE = 0.0
- 2. MLEO = 0.0
- 3. VO = 0.0
- 4. FLC = 0.0
- 5. BCO = 0.041666666666666664
- 6. RO = 0.04563492063492063
- 7. HO = 0.14285714285714285
#### deadline_violation_rate
- 1. HOODIE = 0.08333333333333333
- 2. MLEO = 0.08333333333333333
- 3. VO = 0.10317460317460317
- 4. FLC = 0.12301587301587301
- 5. BCO = 0.13095238095238096
- 6. RO = 0.13293650793650794
- 7. HO = 0.17063492063492064
#### average_reward
- 1. HOODIE = -6.503968253968254
- 2. MLEO = -6.503968253968254
- 3. VO = -6.777777777777778
- 4. FLC = -7.051587301587301
- 5. BCO = -8.670634920634921
- 6. RO = -8.833994708994709
- 7. HO = -13.01984126984127
#### total_reward
- 1. HOODIE = -9834.0
- 2. MLEO = -9834.0
- 3. VO = -10248.0
- 4. FLC = -10662.0
- 5. BCO = -13110.0
- 6. RO = -13357.0
- 7. HO = -19686.0
#### throughput
- 1. HOODIE = 0.9543650793650794
- 2. MLEO = 0.9543650793650794
- 3. VO = 0.9503968253968254
- 4. FLC = 0.9464285714285714
- 5. BCO = 0.9027777777777778
- 6. RO = 0.8988095238095238
- 7. HO = 0.7896825396825397
#### queue_stability_score
- 1. HOODIE = 0.17937041032955262
- 2. MLEO = 0.17937041032955262
- 3. VO = 0.17937041032955262
- 4. FLC = 0.17937041032955262
- 5. BCO = 0.17937041032955262
- 6. RO = 0.17937041032955262
- 7. HO = 0.17937041032955262
#### illegal_action_rejection_count
- 1. HOODIE = 0.0
- 2. MLEO = 0.0
- 3. VO = 0.0
- 4. FLC = 0.0
- 5. BCO = 63.0
- 6. RO = 69.0
- 7. HO = 216.0

## Validation Commands
- git diff --check
- src/.venvmac/bin/python -m unittest discover tests/unit -p 'test_hoodie_runtime_evaluation_*.py'
- src/.venvmac/bin/python -m unittest discover tests/integration -p 'test_hoodie_runtime_evaluation_*.py'
- src/.venvmac/bin/python -m analysis.hoodie_runtime_evaluation_runner --validate-artifacts --artifact-dir artifacts/feature_085_full_audit

## Remaining Gaps
- none

## Manifest
- `execution_manifest.json`
