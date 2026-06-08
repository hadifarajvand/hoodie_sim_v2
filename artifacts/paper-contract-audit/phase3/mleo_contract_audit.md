# MLEO Candidate Latency Audit

## What was fixed
- MLEO is now a real candidate-wise latency scorer instead of a `RuleBased` proxy or a hard failure.
- For each arriving task, the estimator evaluates the legal action space from `Matchmaker` and emits one trace row per legal candidate.
- The selected candidate is the legal action with minimum estimated total latency.

## Exact estimator fields
- Identity: `episode_id`, `time`, `task_id`, `source_agent`, `raw_action_id`, `first_stage_decision`, `destination_type`, `destination_node_id`, `is_legal_candidate`, `is_selected`
- Task fields: `input_data_size`, `remaining_size`, `processing_density`, `required_cpu_cycles`, `arrival_time`, `absolute_deadline`, `timeout`
- Estimates: `private_wait_estimate`, `private_service_estimate`, `offloading_wait_estimate`, `transmission_estimate`, `public_wait_estimate`, `public_service_estimate`, `cloud_wait_estimate`, `cloud_service_estimate`, `total_estimated_latency`, `deadline_slack_estimate`, `estimated_deadline_violation`
- Diagnostics: `estimator_version`, `unavailable_fields_json`, `approximation_warnings_json`

## Approximated fields
- Public queue waiting/service estimates
- Cloud queue waiting/service estimates

## Approximation warnings
- `public_wait/public_service use deterministic active-queue estimate`
- `cloud_wait/cloud_service use deterministic active-queue estimate`

## Why this is candidate-wise now
- The estimator evaluates each legal candidate action from the existing topology-aware action model.
- The trace exports one row per candidate and marks exactly one row as selected for the arriving task.

## Why Figure 10 is still not automatically complete
- Delayed reward replay pairing is still not paper-grade.
- The official validation workflow for Figure 10 is not implemented in this phase.
- Candidate tracing is necessary, not sufficient, for paper-faithful evaluation.
