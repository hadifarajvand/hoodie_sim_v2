# Baseline Fairness Rebuild

## Metadata
- **feature_id**: 021-baseline-fairness-rebuild
- **generated_by**: baseline_fairness_rebuild
- **deterministic**: True
- **source_refs**: ['specs/021-baseline-fairness-rebuild/spec.md', 'specs/021-baseline-fairness-rebuild/plan.md', 'specs/021-baseline-fairness-rebuild/research.md', 'src/evaluation/matrix_runner.py', 'src/evaluation/policy_registry.py', 'src/evaluation/scenario_registry.py', 'src/environment/gym_adapter.py']

## Source Gate Status
- **passed**: True
- **differential_audit**: valid=True details=['valid']
- **repair_summary**: valid=True details=['valid']
- **controlled_sweeps**: valid=True details=['valid']

## Baseline Policies Included
- FLC
- VO
- HO
- RO
- BCO
- MLEO
- ADAPTIVE

## Scenarios And Traces
- paper_default trace=paper_default-7 seed=7
- moderate trace=moderate-7 seed=7

## Fairness Controls
- **shared_environment_interface**: HoodieGymEnvironment via EvaluationMatrixRunner
- **identical_workload**: True
- **identical_topology**: True
- **identical_deadline_rules**: True
- **identical_reward_timing**: True
- **identical_metric_definitions**: True

## Metrics Reused
- completed_tasks
- dropped_tasks
- throughput
- average_delay
- drop_ratio

## Collapse Indicators
- FLC / paper_default: completed=3|dropped=0|throughput=3
- FLC / moderate: completed=3|dropped=0|throughput=3
- VO / paper_default: completed=0|dropped=0|throughput=0
- VO / moderate: completed=0|dropped=0|throughput=0
- HO / paper_default: completed=2|dropped=0|throughput=2
- HO / moderate: completed=2|dropped=0|throughput=2
- RO / paper_default: completed=4|dropped=0|throughput=4
- RO / moderate: completed=4|dropped=0|throughput=4
- BCO / paper_default: completed=3|dropped=0|throughput=3
- BCO / moderate: completed=3|dropped=0|throughput=3
- MLEO / paper_default: completed=3|dropped=0|throughput=3
- MLEO / moderate: completed=3|dropped=0|throughput=3
- ADAPTIVE / paper_default: completed=3|dropped=0|throughput=3
- ADAPTIVE / moderate: completed=3|dropped=0|throughput=3

## Anti-Collapse Assessment
- **status**: collapse_reduced
- baseline signatures differentiated

## Unchanged Collapse Explanation
Persistent collapse remains a valid mechanism property when policy signatures do not differentiate materially.

## Limitations
- Diagnostic only.
- No baseline campaign-scale reproduction was run.
- No policy redesign or training foundation work is implied.

## No Training Disclaimer
This report does not add training or claim training-driven improvement.

## No Policy Redesign Disclaimer
This report does not redesign policies or claim that policy redesign is required.

## No Paper Validity Disclaimer
This report is not a paper-validity or reproduction-completeness claim.

## Reproducibility Details
- **approved_interpreter**: /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python
- **fixed_seeds**: [7]
- **run_count_per_value**: 1
- **trace_order**: policy -> scenario -> seed
- **output_dir**: artifacts/analysis/baseline-fairness-rebuild

## Overall Status
collapse_reduced
