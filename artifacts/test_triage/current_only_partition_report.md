# Current-only partition report
- dirty-gate-only: 7
- actionable: 20

## Dirty gate only
- `tests.integration.test_bind_full_campaign_real_torch_trainer_scope_guard.BindFullCampaignRealTorchTrainerScopeGuardTests::test_dirty_and_staged_paths_are_only_feature_060b_paths` | `dirty_worktree_gate_only` | `` | ``
- `tests.integration.test_controlled_mechanistic_sweeps_final_diff.ControlledMechanisticSweepsFinalDiffTests::test_final_diff_stays_within_allowed_paths` | `dirty_worktree_gate_only` | `` | ``
- `tests.integration.test_controlled_mechanistic_sweeps_scope_guard.ControlledMechanisticSweepsScopeGuardTests::test_git_diff_does_not_touch_forbidden_paths` | `dirty_worktree_gate_only` | `` | ``
- `tests.integration.test_environment_lifecycle_final_diff.EnvironmentLifecycleFinalDiffIntegrationTest::test_no_forbidden_paths_changed` | `dirty_worktree_gate_only` | `` | ``
- `tests.integration.test_execution_time_contract_scope_guard.ExecutionTimeContractScopeGuardIntegrationTest::test_no_forbidden_paths_changed` | `dirty_worktree_gate_only` | `` | ``
- `tests.integration.test_mechanism_repair_scope_guard.MechanismRepairScopeGuardIntegrationTest::test_no_forbidden_paths_changed` | `dirty_worktree_gate_only` | `` | ``
- `tests.integration.test_transmission_delay_runtime_scope_guard.TransmissionDelayRuntimeScopeGuardIntegrationTests::test_no_forbidden_paths_changed` | `dirty_worktree_gate_only` | `` | ``

## Actionable
- `tests.integration.test_controlled_mechanistic_sweeps_flow.ControlledMechanisticSweepsFlowTests::test_tiny_sweeps_run_deterministically_and_write_artifacts` | `test_infrastructure_defect` | `` | ``
- `tests.integration.test_controlled_mechanistic_sweeps_flow.ControlledMechanisticSweepsFlowTests::test_unsupported_dimensions_remain_instrumentation_gaps` | `test_infrastructure_defect` | `` | ``
- `tests.integration.test_evaluation_runner.EvaluationRunnerTests::test_multiple_policies_share_the_same_runner` | `test_infrastructure_defect` | `` | ``
- `tests.integration.test_execution_time_flow.ExecutionTimeFlowTests::test_local_edge_and_cloud_execution_complete_in_expected_slots` | `test_infrastructure_defect` | `` | ``
- `tests.integration.test_offload_instrumentation_no_behavior_change.OffloadInstrumentationNoBehaviorChangeTest::test_instrumentation_does_not_change_rewards_or_metrics` | `test_infrastructure_defect` | `` | ``
- `tests.integration.test_passive_selected_action_trace_repair.PassiveSelectedActionTraceRepairIntegrationTest::test_decision_point_emits_selected_action_join_fields` | `test_infrastructure_defect` | `` | ``
- `tests.integration.test_transmission_delay_runtime_wiring.TransmissionDelayRuntimeWiringIntegrationTests::test_horizontal_metadata_recorded` | `test_infrastructure_defect` | `` | ``
- `tests.integration.test_transmission_delay_runtime_wiring.TransmissionDelayRuntimeWiringIntegrationTests::test_horizontal_transmission_delay_uses_task_size_and_RH` | `test_infrastructure_defect` | `` | ``
- `tests.integration.test_transmission_delay_runtime_wiring.TransmissionDelayRuntimeWiringIntegrationTests::test_local_path_has_no_transmission_metadata` | `test_infrastructure_defect` | `` | ``
- `tests.integration.test_transmission_delay_runtime_wiring.TransmissionDelayRuntimeWiringIntegrationTests::test_no_dependency_training_policy_campaign_drift` | `test_infrastructure_defect` | `` | ``
- `tests.integration.test_transmission_delay_runtime_wiring.TransmissionDelayRuntimeWiringIntegrationTests::test_no_feature_033_execution_contract_drift` | `test_infrastructure_defect` | `` | ``
- `tests.integration.test_transmission_delay_runtime_wiring.TransmissionDelayRuntimeWiringIntegrationTests::test_offload_admitted_at_documented_boundary` | `test_infrastructure_defect` | `` | ``
- `tests.integration.test_transmission_delay_runtime_wiring.TransmissionDelayRuntimeWiringIntegrationTests::test_offload_not_admitted_before_delay_boundary` | `test_infrastructure_defect` | `` | ``
- `tests.unit.test_baseline_registry_revalidation.BaselineRegistryRevalidationUnitTests::test_vertical_cloud_legality_does_not_require_cloud_in_figure7` | `test_infrastructure_defect` | `` | ``
- `tests.unit.test_evaluation_trace_bank_baseline_harness_behavior_equivalence.EvaluationTraceBankBaselineHarnessBehaviorEquivalenceTests::test_behavior_safety_fields_cover_all_forbidden_behaviors` | `test_infrastructure_defect` | `` | ``
- `tests.unit.test_full_paper_default_training_campaign_gate_behavior_equivalence.FullPaperDefaultTrainingCampaignGateBehaviorEquivalenceTests::test_safety_fields_cover_forbidden_feature_059_behaviors` | `test_infrastructure_defect` | `` | ``
- `tests.unit.test_gym_environment.GymEnvironmentTests::test_action_legality_under_topology` | `test_infrastructure_defect` | `` | ``
- `tests.unit.test_gym_environment.GymEnvironmentTests::test_horizontal_offload_path` | `test_infrastructure_defect` | `` | ``
- `tests.unit.test_gym_environment.GymEnvironmentTests::test_vertical_offload_does_not_require_cloud_in_topology` | `test_infrastructure_defect` | `` | ``
- `tests.unit.test_runtime_adoption_approved_assumption_registry.RuntimeAdoptionApprovedAssumptionRegistryUnitTests::test_approved_figure7_topology_keeps_vertical_cloud_offload_legal` | `test_infrastructure_defect` | `` | ``
