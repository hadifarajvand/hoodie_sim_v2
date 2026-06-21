# Paper component alignment audit (Feature 080)

| Paper component | Repository implementation | Status | Evidence | Gap | Proposed repair |
|---|---|---|---|---|---|
| topology | src/environment/, structured_paper_topology_linkrate_registry | implemented_but_unverified | src/environment/environment.py | node/link counts not cross-checked to a specific paper figure | map to paper topology table |
| agents / mobile devices / nodes | src/agents/, src/environment | implemented_but_unverified | src/agents/ | agent count vs paper unverified | document agent cardinality |
| edge servers | src/environment | implemented_but_unverified | src/environment/environment.py | edge capacity profile not paper-matched | record edge CPU profile |
| cloud server | public_cloud_queue_capacity_sharing | implemented_with_approximation | src/analysis/public_cloud_queue_capacity_sharing/ | cloud sharing approximated | document approximation |
| task generation | src/environment | implemented_but_unverified | src/environment/gym_adapter.py | arrival process not matched to paper | document arrival model |
| task size | deadline_timeout_feasible_workload_calibration | implemented_with_approximation | src/analysis/deadline_timeout_feasible_workload_calibration/ | size distribution calibrated, not paper-exact | tag calibration_profile |
| processing density | deadline_timeout_feasible_workload_calibration | implemented_with_approximation | src/analysis/deadline_timeout_feasible_workload_calibration/ | density calibrated | tag calibration_profile |
| deadline / timeout | completion_path_deadline_feasibility_repair | implemented_with_approximation | src/analysis/completion_path_deadline_feasibility_repair/feasibility.py | deadline envelope calibrated in F069 | document calibrated envelope |
| transmission rate | link_rate_transmission_delay_contract | implemented_but_unverified | src/analysis/link_rate_transmission_delay_contract/ | link rates unverified vs paper | document link-rate registry |
| execution capacity | computation_delay_cpu_unit_validation | implemented_but_unverified | src/analysis/computation_delay_cpu_unit_validation/ | cpu unit unverified | document cpu unit |
| local action | src/environment, gym_adapter | implemented_but_unverified | src/environment/gym_adapter.py | verified legal, not paper-cross-checked | keep |
| horizontal action | src/environment, gym_adapter | implemented_but_unverified | src/environment/gym_adapter.py | as above | keep |
| vertical action | src/environment, gym_adapter | implemented_but_unverified | src/environment/gym_adapter.py | as above | keep |
| queueing behavior | public_cloud_queue_capacity_sharing | implemented_but_unverified | src/environment/runtime_model.py | service discipline unverified | document discipline |
| transmission/execution latency | transmission_delay_runtime_wiring | implemented_but_unverified | src/analysis/transmission_delay_runtime_wiring/ | latency model unverified | document latency model |
| reward function | src/environment/reward_timing.py | implemented_but_unverified | src/environment/reward_timing.py:116 | phi_private + drop_penalty=40; matches canonical recompute | keep; do not modify |
| terminal event lifecycle | terminal_lifecycle_accounting_50_100_comparison | broken | src/analysis/terminal_lifecycle_accounting_50_100_comparison/repaired_terminal_evaluator.py | horizon-finalized tasks counted as reward-bearing without reward_emitted event (Feature 072 blocker) | Repair A: horizon-aware reconciliation |
| policy / DRL algorithm | src/training, DDQNTrainer | implemented_but_unverified | src/training/ | DDQN present; convergence not established | keep |
| state representation | state_profile_decision_time_integration_recovery | implemented_but_unverified | src/analysis/state_profile_decision_time_integration_recovery/state_features.py | legacy(3)+new(30) profiles; decision-time injection in place | keep; verify dims |
| training workflow | full_training_reproduction_campaign | implemented_but_unverified | src/analysis/full_training_reproduction_campaign/trainer.py | lightweight only validated | keep budget<=100 |
| evaluation workflow | repaired_terminal_evaluator | broken | src/analysis/terminal_lifecycle_accounting_50_100_comparison/repaired_terminal_evaluator.py | reconciliation fails post state-injection | Repair A |
| baseline policies | baseline_* modules | implemented_but_unverified | src/analysis/baseline_policy_comparative_evaluation_readiness/ | fixed local/horizontal/vertical/random present | validate schema |
| metrics | paper_faithful_simulation_production_pipeline/schema.py | implemented_but_unverified | src/analysis/paper_faithful_simulation_production_pipeline/schema.py | unified schema defined (Feature 080) | use across policies |
| figures | unified_campaign_result_analysis_figures_findings | implemented_but_unverified | src/analysis/unified_campaign_result_analysis_figures_findings/ | matplotlib only | keep |
| artifact pipeline | this feature | implemented_but_unverified | artifacts/analysis/paper-faithful-simulation-production-pipeline/ | single run dir | keep |
