# Baseline Rebuild Sensitivity Audit

## Metadata
- **feature_id**: 022-baseline-rebuild-sensitivity-audit
- **generated_by**: baseline_rebuild_sensitivity_audit
- **deterministic**: True
- **source_refs**: ['specs/022-baseline-rebuild-sensitivity-audit/spec.md', 'specs/022-baseline-rebuild-sensitivity-audit/plan.md', 'specs/022-baseline-rebuild-sensitivity-audit/research.md', 'src/evaluation/matrix_runner.py', 'src/evaluation/matrix_config.py', 'src/evaluation/policy_registry.py', 'src/evaluation/scenario_registry.py', 'src/environment/gym_adapter.py']

## Source Gate Status
- **passed**: True
- **differential_audit**: valid=True details=['valid']
- **repair_summary**: valid=True details=['valid']
- **controlled_sweeps**: valid=True details=['valid']
- **fairness_rebuild**: valid=True details=['valid']

## Sensitivity Dimensions
- **seeds**: [7, 11, 13]
- **scenarios**: ['paper_default', 'moderate', 'heavy']
- **episode_lengths**: [4, 6]
- **baseline_signature_fields**: ['completed_tasks', 'dropped_tasks', 'throughput', 'average_delay']

## Used Settings
- **seeds**: [7, 11, 13]
- **scenarios**: ['paper_default', 'moderate', 'heavy']
- **episode_lengths**: [4, 6]
- **supported_settings**: 18

## Fairness Controls
- **shared_environment_interface**: HoodieGymEnvironment via EvaluationMatrixRunner
- **identical_workload**: True
- **identical_topology**: True
- **identical_deadline_rules**: True
- **identical_reward_timing**: True
- **identical_metric_definitions**: True

## Included Baselines
- FLC
- VO
- HO
- RO
- BCO
- MLEO
- ADAPTIVE

## Reused Metrics
- completed_tasks
- dropped_tasks
- throughput
- average_delay

## Baseline Signatures
- seed=7 scenario=paper_default episode_length=4
  - FLC: completed=3::dropped=0::throughput=3::delay=2.0
  - VO: completed=1::dropped=0::throughput=1::delay=3.0
  - HO: completed=1::dropped=0::throughput=1::delay=2.0
  - RO: completed=2::dropped=0::throughput=2::delay=2.0
  - BCO: completed=3::dropped=0::throughput=3::delay=2.0
  - MLEO: completed=3::dropped=0::throughput=3::delay=2.0
  - ADAPTIVE: completed=1::dropped=0::throughput=1::delay=1.0
- seed=7 scenario=paper_default episode_length=6
  - FLC: completed=5::dropped=0::throughput=5::delay=3.0
  - VO: completed=3::dropped=0::throughput=3::delay=4.0
  - HO: completed=2::dropped=0::throughput=2::delay=3.0
  - RO: completed=4::dropped=0::throughput=4::delay=3.5
  - BCO: completed=5::dropped=0::throughput=5::delay=3.0
  - MLEO: completed=5::dropped=0::throughput=5::delay=3.0
  - ADAPTIVE: completed=2::dropped=0::throughput=2::delay=2.5
- seed=7 scenario=moderate episode_length=4
  - FLC: completed=3::dropped=0::throughput=3::delay=2.0
  - VO: completed=2::dropped=0::throughput=2::delay=2.5
  - HO: completed=2::dropped=0::throughput=2::delay=2.5
  - RO: completed=2::dropped=0::throughput=2::delay=2.0
  - BCO: completed=3::dropped=0::throughput=3::delay=2.0
  - MLEO: completed=3::dropped=0::throughput=3::delay=2.0
  - ADAPTIVE: completed=2::dropped=0::throughput=2::delay=2.0
- seed=7 scenario=moderate episode_length=6
  - FLC: completed=5::dropped=0::throughput=5::delay=3.0
  - VO: completed=4::dropped=0::throughput=4::delay=3.5
  - HO: completed=3::dropped=0::throughput=3::delay=3.3333333333333335
  - RO: completed=4::dropped=0::throughput=4::delay=3.25
  - BCO: completed=5::dropped=0::throughput=5::delay=3.0
  - MLEO: completed=5::dropped=0::throughput=5::delay=3.0
  - ADAPTIVE: completed=3::dropped=0::throughput=3::delay=3.0
- seed=7 scenario=heavy episode_length=4
  - FLC: completed=3::dropped=0::throughput=3::delay=2.0
  - VO: completed=1::dropped=0::throughput=1::delay=3.0
  - HO: completed=1::dropped=0::throughput=1::delay=2.0
  - RO: completed=2::dropped=0::throughput=2::delay=2.0
  - BCO: completed=3::dropped=0::throughput=3::delay=2.0
  - MLEO: completed=3::dropped=0::throughput=3::delay=2.0
  - ADAPTIVE: completed=1::dropped=0::throughput=1::delay=1.0
- seed=7 scenario=heavy episode_length=6
  - FLC: completed=5::dropped=0::throughput=5::delay=3.0
  - VO: completed=3::dropped=0::throughput=3::delay=4.0
  - HO: completed=2::dropped=0::throughput=2::delay=3.0
  - RO: completed=4::dropped=0::throughput=4::delay=3.5
  - BCO: completed=5::dropped=0::throughput=5::delay=3.0
  - MLEO: completed=5::dropped=0::throughput=5::delay=3.0
  - ADAPTIVE: completed=2::dropped=0::throughput=2::delay=2.5
- seed=11 scenario=paper_default episode_length=4
  - FLC: completed=3::dropped=0::throughput=3::delay=2.0
  - VO: completed=0::dropped=0::throughput=0::delay=0.0
  - HO: completed=1::dropped=0::throughput=1::delay=3.0
  - RO: completed=2::dropped=0::throughput=2::delay=2.5
  - BCO: completed=3::dropped=0::throughput=3::delay=2.0
  - MLEO: completed=3::dropped=0::throughput=3::delay=2.0
  - ADAPTIVE: completed=1::dropped=0::throughput=1::delay=1.0
- seed=11 scenario=paper_default episode_length=6
  - FLC: completed=4::dropped=0::throughput=4::delay=2.75
  - VO: completed=2::dropped=0::throughput=2::delay=4.5
  - HO: completed=1::dropped=0::throughput=1::delay=3.0
  - RO: completed=2::dropped=0::throughput=2::delay=2.5
  - BCO: completed=4::dropped=0::throughput=4::delay=2.75
  - MLEO: completed=4::dropped=0::throughput=4::delay=2.75
  - ADAPTIVE: completed=1::dropped=0::throughput=1::delay=1.0
- seed=11 scenario=moderate episode_length=4
  - FLC: completed=3::dropped=0::throughput=3::delay=2.0
  - VO: completed=1::dropped=0::throughput=1::delay=3.0
  - HO: completed=2::dropped=0::throughput=2::delay=2.5
  - RO: completed=2::dropped=0::throughput=2::delay=2.0
  - BCO: completed=3::dropped=0::throughput=3::delay=2.0
  - MLEO: completed=3::dropped=0::throughput=3::delay=2.0
  - ADAPTIVE: completed=2::dropped=0::throughput=2::delay=2.0
- seed=11 scenario=moderate episode_length=6
  - FLC: completed=5::dropped=0::throughput=5::delay=3.0
  - VO: completed=3::dropped=0::throughput=3::delay=4.0
  - HO: completed=2::dropped=0::throughput=2::delay=2.5
  - RO: completed=4::dropped=0::throughput=4::delay=3.5
  - BCO: completed=5::dropped=0::throughput=5::delay=3.0
  - MLEO: completed=5::dropped=0::throughput=5::delay=3.0
  - ADAPTIVE: completed=2::dropped=0::throughput=2::delay=2.0
- seed=11 scenario=heavy episode_length=4
  - FLC: completed=3::dropped=0::throughput=3::delay=2.0
  - VO: completed=0::dropped=0::throughput=0::delay=0.0
  - HO: completed=1::dropped=0::throughput=1::delay=3.0
  - RO: completed=2::dropped=0::throughput=2::delay=2.5
  - BCO: completed=3::dropped=0::throughput=3::delay=2.0
  - MLEO: completed=3::dropped=0::throughput=3::delay=2.0
  - ADAPTIVE: completed=1::dropped=0::throughput=1::delay=1.0
- seed=11 scenario=heavy episode_length=6
  - FLC: completed=4::dropped=0::throughput=4::delay=2.75
  - VO: completed=2::dropped=0::throughput=2::delay=4.5
  - HO: completed=1::dropped=0::throughput=1::delay=3.0
  - RO: completed=2::dropped=0::throughput=2::delay=2.5
  - BCO: completed=4::dropped=0::throughput=4::delay=2.75
  - MLEO: completed=4::dropped=0::throughput=4::delay=2.75
  - ADAPTIVE: completed=1::dropped=0::throughput=1::delay=1.0
- seed=13 scenario=paper_default episode_length=4
  - FLC: completed=2::dropped=0::throughput=2::delay=2.0
  - VO: completed=0::dropped=0::throughput=0::delay=0.0
  - HO: completed=1::dropped=0::throughput=1::delay=3.0
  - RO: completed=2::dropped=0::throughput=2::delay=3.0
  - BCO: completed=2::dropped=0::throughput=2::delay=2.0
  - MLEO: completed=2::dropped=0::throughput=2::delay=2.0
  - ADAPTIVE: completed=1::dropped=0::throughput=1::delay=1.0
- seed=13 scenario=paper_default episode_length=6
  - FLC: completed=4::dropped=0::throughput=4::delay=3.25
  - VO: completed=2::dropped=0::throughput=2::delay=4.5
  - HO: completed=1::dropped=0::throughput=1::delay=3.0
  - RO: completed=2::dropped=0::throughput=2::delay=3.0
  - BCO: completed=4::dropped=0::throughput=4::delay=3.25
  - MLEO: completed=4::dropped=0::throughput=4::delay=3.25
  - ADAPTIVE: completed=1::dropped=0::throughput=1::delay=1.0
- seed=13 scenario=moderate episode_length=4
  - FLC: completed=3::dropped=0::throughput=3::delay=2.0
  - VO: completed=1::dropped=0::throughput=1::delay=3.0
  - HO: completed=2::dropped=0::throughput=2::delay=2.5
  - RO: completed=2::dropped=0::throughput=2::delay=2.0
  - BCO: completed=3::dropped=0::throughput=3::delay=2.0
  - MLEO: completed=3::dropped=0::throughput=3::delay=2.0
  - ADAPTIVE: completed=2::dropped=0::throughput=2::delay=2.0
- seed=13 scenario=moderate episode_length=6
  - FLC: completed=5::dropped=0::throughput=5::delay=3.0
  - VO: completed=3::dropped=0::throughput=3::delay=4.0
  - HO: completed=2::dropped=0::throughput=2::delay=2.5
  - RO: completed=3::dropped=0::throughput=3::delay=3.0
  - BCO: completed=5::dropped=0::throughput=5::delay=3.0
  - MLEO: completed=5::dropped=0::throughput=5::delay=3.0
  - ADAPTIVE: completed=2::dropped=0::throughput=2::delay=2.0
- seed=13 scenario=heavy episode_length=4
  - FLC: completed=2::dropped=0::throughput=2::delay=2.0
  - VO: completed=0::dropped=0::throughput=0::delay=0.0
  - HO: completed=1::dropped=0::throughput=1::delay=3.0
  - RO: completed=2::dropped=0::throughput=2::delay=3.0
  - BCO: completed=2::dropped=0::throughput=2::delay=2.0
  - MLEO: completed=2::dropped=0::throughput=2::delay=2.0
  - ADAPTIVE: completed=1::dropped=0::throughput=1::delay=1.0
- seed=13 scenario=heavy episode_length=6
  - FLC: completed=4::dropped=0::throughput=4::delay=3.25
  - VO: completed=2::dropped=0::throughput=2::delay=4.5
  - HO: completed=1::dropped=0::throughput=1::delay=3.0
  - RO: completed=2::dropped=0::throughput=2::delay=3.0
  - BCO: completed=4::dropped=0::throughput=4::delay=3.25
  - MLEO: completed=4::dropped=0::throughput=4::delay=3.25
  - ADAPTIVE: completed=1::dropped=0::throughput=1::delay=1.0

## Collapse Stability Indicators
- seed=7 scenario=paper_default episode_length=4 status=robust_collapse_reduced support=full note=reduced collapse survived this setting and improved differentiation
- seed=7 scenario=paper_default episode_length=6 status=robust_collapse_reduced support=full note=reduced collapse survived this setting and improved differentiation
- seed=7 scenario=moderate episode_length=4 status=collapse_unchanged support=full note=baseline diversity remained materially unchanged
- seed=7 scenario=moderate episode_length=6 status=robust_collapse_reduced support=full note=reduced collapse survived this setting and improved differentiation
- seed=7 scenario=heavy episode_length=4 status=robust_collapse_reduced support=full note=reduced collapse survived this setting and improved differentiation
- seed=7 scenario=heavy episode_length=6 status=robust_collapse_reduced support=full note=reduced collapse survived this setting and improved differentiation
- seed=11 scenario=paper_default episode_length=4 status=robust_collapse_reduced support=full note=reduced collapse survived this setting and improved differentiation
- seed=11 scenario=paper_default episode_length=6 status=robust_collapse_reduced support=full note=reduced collapse survived this setting and improved differentiation
- seed=11 scenario=moderate episode_length=4 status=robust_collapse_reduced support=full note=reduced collapse survived this setting and improved differentiation
- seed=11 scenario=moderate episode_length=6 status=robust_collapse_reduced support=full note=reduced collapse survived this setting and improved differentiation
- seed=11 scenario=heavy episode_length=4 status=robust_collapse_reduced support=full note=reduced collapse survived this setting and improved differentiation
- seed=11 scenario=heavy episode_length=6 status=robust_collapse_reduced support=full note=reduced collapse survived this setting and improved differentiation
- seed=13 scenario=paper_default episode_length=4 status=robust_collapse_reduced support=full note=reduced collapse survived this setting and improved differentiation
- seed=13 scenario=paper_default episode_length=6 status=robust_collapse_reduced support=full note=reduced collapse survived this setting and improved differentiation
- seed=13 scenario=moderate episode_length=4 status=robust_collapse_reduced support=full note=reduced collapse survived this setting and improved differentiation
- seed=13 scenario=moderate episode_length=6 status=robust_collapse_reduced support=full note=reduced collapse survived this setting and improved differentiation
- seed=13 scenario=heavy episode_length=4 status=robust_collapse_reduced support=full note=reduced collapse survived this setting and improved differentiation
- seed=13 scenario=heavy episode_length=6 status=robust_collapse_reduced support=full note=reduced collapse survived this setting and improved differentiation

## Sensitivity Classification
- **status**: robust_collapse_reduced
- reduced collapse survived all supported settings and improved in at least one

## Limitations
- Diagnostic only.
- No baseline campaign-scale reproduction was run.
- Unsupported controls remain inconclusive rather than being fabricated.

## No Training Disclaimer
This audit does not add training, DRL, or neural-network code.

## No Policy Redesign Disclaimer
This audit does not redesign policies or introduce new baseline algorithms.

## No Metric Change Disclaimer
This audit does not change metric formulas.

## No Paper Validity Disclaimer
This audit is not a paper-validity or reproduction-completeness claim.

## Reproducibility
- **approved_interpreter**: /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python
- **fixed_seeds**: [7, 11, 13]
- **deterministic_ordering**: gates -> settings -> policy matrix -> signatures -> classification
- **run_count_per_value**: 1
- **output_dir**: artifacts/analysis/baseline-rebuild-sensitivity-audit

## Overall Status
robust_collapse_reduced
