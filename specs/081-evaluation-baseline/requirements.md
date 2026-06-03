# Feature 081 Requirements — HOODIE Evaluation & Baseline Benchmarking

## Purpose
Feature 081 defines a deterministic evaluation and benchmarking framework for comparing the base-paper HOODIE proposed method implemented in Feature 080 against explicit baseline policies.

This feature is evaluation-only. It must not redesign the Feature 080 method, introduce the user's thesis method, introduce DCQ, or modify the internal HOODIE proposed-method implementation.

## Methods Under Evaluation

### M1 — HOODIE_PROPOSED
- Source: `src/analysis/hoodie_proposed_method/` from Feature 080.
- Meaning: the proposed method from the base HOODIE paper only.
- Required behavior: use the Feature 080 package as the tested proposed method.
- Forbidden behavior: do not mutate or extend Feature 080 internals inside Feature 081.

### M2 — ORIGINAL_HOODIE_BASELINE
- Purpose: represent the base-paper HOODIE baseline behavior available in the current simulator stack.
- Decision behavior: use existing baseline/runtime components already present in the repository where available.
- Required output: action decision, execution outcome, and metric row.
- Constraint: if the repository does not contain a full original-HOODIE runtime baseline, represent this method honestly as a baseline adapter around the available paper-aligned baseline components and report any gap.

### M3 — RANDOM_POLICY
- Decision behavior: choose uniformly from valid candidate actions for the current scenario context.
- Valid actions may include local execution, legal horizontal offload, and legal vertical cloud offload where available.
- Must reject illegal actions rather than silently accepting them.
- Randomness must be seed-controlled and reproducible.

### M4 — LOCAL_ONLY
- Decision behavior: always execute locally/private queue when a task exists.
- No horizontal offloading.
- No vertical cloud offloading.
- If local execution is unavailable, mark unavailable drop according to the metric contract.

### M5 — CLOUD_ONLY
- Decision behavior: always use vertical cloud offloading when a task exists and cloud is available.
- No local execution.
- No horizontal edge-to-edge offloading.
- If cloud is unavailable or illegal, mark unavailable drop according to the metric contract.

## Scenario Requirements

Feature 081 must define and later implement deterministic scenario contexts covering:

### S1 — light_load_no_deadline_pressure
- Low task arrival rate.
- Relaxed deadlines.
- Expected behavior: most valid methods should complete most tasks.

### S2 — tight_deadline_pressure
- Moderate or high task arrival rate.
- Tight deadlines.
- Expected behavior: exposes delay/drop behavior.

### S3 — legal_horizontal_offload
- At least one legal edge-to-edge destination exists.
- Expected behavior: horizontal offload candidates are valid.

### S4 — illegal_horizontal_destination_attempt
- At least one invalid horizontal destination exists.
- Expected behavior: invalid action rejection is counted.

### S5 — cloud_vertical_fallback
- Cloud is available as vertical fallback.
- Expected behavior: cloud-only and proposed methods can use vertical route.

### S6 — timeout_drop_case
- Task characteristics force timeout under at least one policy.
- Expected behavior: timeout drops are counted.

### S7 — mixed_local_horizontal_cloud_candidates
- Local, horizontal, and vertical candidates all exist.
- Expected behavior: policy differences become visible.

## Workload Dimensions

Each scenario should support:
- workload level: low, medium, high
- deadline pressure: relaxed, moderate, tight
- topology mode: `paper_figure_7`
- runtime mode: `paper`
- seed-controlled reproducibility

## Metric Requirements

Each evaluation row must expose at least:

- `policy`
- `scenario`
- `workload`
- `deadline_pressure`
- `seed`
- `completed_count`
- `dropped_timeout_count`
- `dropped_unavailable_count`
- `deadline_violation_count`
- `illegal_action_rejection_count`
- `average_delay`
- `average_reward`
- `total_reward`
- `completion_rate`
- `timeout_drop_rate`
- `unavailable_drop_rate`
- `deadline_violation_rate`
- `throughput`
- `queue_stability_score`
- `compatibility_mode_used`

## Metric Formulas

### Completion Rate
`completion_rate = completed_count / total_task_count`

### Timeout Drop Rate
`timeout_drop_rate = dropped_timeout_count / total_task_count`

### Unavailable Drop Rate
`unavailable_drop_rate = dropped_unavailable_count / total_task_count`

### Deadline Violation Rate
`deadline_violation_rate = deadline_violation_count / total_task_count`

### Average Delay
`average_delay = sum(completion_time - arrival_time for completed tasks) / completed_count`

If no task completes, average delay must be represented as `None`, `NaN`, or an explicit null-compatible value according to existing project conventions.

### Throughput
`throughput = completed_count / scenario_duration`

### Queue Stability Score
Use a deterministic score derived from queue growth and/or queue length, for example:

`queue_stability_score = 1 / (1 + average_queue_length + positive_queue_growth)`

The implementation must document the exact formula used and keep it deterministic.

## Ranking Requirements

Ranking must be metric-by-metric first, not a single hidden overall score.

### Higher-is-better metrics
- completion_rate
- throughput
- queue_stability_score
- average_reward
- total_reward

### Lower-is-better metrics
- average_delay
- timeout_drop_rate
- unavailable_drop_rate
- deadline_violation_rate
- illegal_action_rejection_count

### Tie-breaking
If two policies have equal metric value:
1. prefer lower average_delay if relevant and available
2. prefer lower deadline_violation_rate
3. prefer lower timeout_drop_rate
4. use deterministic policy name ordering as final tie-break

## Report Requirements

The report must include:
- policy coverage table
- scenario coverage table
- metric coverage table
- per-metric ranking tables
- per-scenario comparison tables
- aggregate summary table
- validation summary
- claim boundary
- scope proof

## Claim Boundary
Feature 081 may claim:
- deterministic benchmarking framework exists
- baseline policies are represented according to this spec
- metrics and rankings are computed by explicit formulas

Feature 081 must not claim:
- full empirical reproduction of the HOODIE paper
- statistical superiority unless statistical tests are implemented and reported
- thesis/DCQ method comparison
- custom queue redesign
- trained DRL performance reproduction beyond what the implemented package actually supports
