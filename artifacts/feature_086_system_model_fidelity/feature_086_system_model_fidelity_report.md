# Feature 086 HOODIE System-Model Fidelity Gate Report

- feature_id: `086-mleo-latency-evidence-test`
- status: `system_model_fidelity_ready_for_output_comparison`
- passed: `True`
- verdict: `system_model_fidelity_ready_for_output_comparison`
- output_comparison_ready: `True`
- active_policy_count: `7`
- mechanism_count: `22`
- metric_count: `11`

## Active Policies
- HOODIE
- RO
- FLC
- VO
- HO
- BCO
- MLEO

## Invalid-Label Check
- Legacy active-label check passed: retired aliases are absent from the active 086 outputs.
- Historical references remain in prior feature documentation only.

## Verdict
- `system_model_fidelity_ready_for_output_comparison`

## Mechanism Coverage Summary
- exact: `7`
- approximate_documented: `15`
- blocking: `0`

## Mechanism Coverage
| mechanism_id | paper_expectation | simulator_behavior | code_location | test_artifact_evidence | status | required_fix_or_claim_boundary |
| --- | --- | --- | --- | --- | --- | --- |
| three_tier_topology | Task source / IoT layer, edge agents, and cloud are represented as a three-tier CEC topology. | The runtime layer uses deterministic topology profiles and scenario fixtures to represent the source, edge, and cloud tiers. | resources/papers/hoodie/ocr/merged.txt; src/analysis/hoodie_runtime_evaluation_runner/config.py; src/analysis/hoodie_runtime_evaluation_runner/scenarios.py | tests/unit/test_hoodie_runtime_evaluation_runner_scenarios.py; artifacts/feature_085_full_audit/raw_rows.json | approximate_documented | Document the deterministic topology abstraction; no new simulator topology is claimed. |
| edge_agent_set_cloud_node | Multiple edge agents plus one cloud node exist as active runtime participants. | The runtime policy set and scenario contexts model multiple edge agents plus a cloud destination. | src/analysis/hoodie_runtime_evaluation_runner/config.py; src/analysis/hoodie_runtime_evaluation_runner/model.py | tests/unit/test_hoodie_runtime_evaluation_runner_policies.py; artifacts/feature_085_full_audit/feature_085_audit_report.json | approximate_documented | Treat the active policy set and scenario contexts as the evidence boundary, not as a full distributed runtime simulator. |
| horizontal_connectivity_legality | Horizontal EA-to-EA destinations must be legal only when topology permits them. | The policy layer distinguishes legal horizontal destinations from illegal attempts and rejects invalid horizontal choices. | src/analysis/hoodie_runtime_evaluation_runner/policies.py; src/analysis/hoodie_runtime_evaluation_runner/scenarios.py | tests/unit/test_hoodie_runtime_evaluation_runner_policies.py::test_ho_prefers_horizontal_when_legal_destination_exists; tests/integration/test_hoodie_runtime_evaluation_runner_report.py | approximate_documented | The legality model is documented through candidate/action legality checks. |
| vertical_ea_cloud_path | Vertical offload reaches the cloud path and uses cloud-side execution capacity. | The runtime scenarios include cloud-vertical fallback and vertical offload decisions with cloud destinations. | src/analysis/hoodie_runtime_evaluation_runner/policies.py; src/analysis/hoodie_runtime_evaluation_runner/scenarios.py | tests/unit/test_hoodie_runtime_evaluation_runner_policies.py::test_vo_always_vertical; artifacts/feature_085_full_audit/raw_rows.json | approximate_documented | The cloud path is evidenced by scenario traces, not by a separate cloud simulator service. |
| task_model | Tasks carry ID, data size, CPU demand/processing density, and deadline/timeout semantics. | TaskBlueprint and scenario rows retain task_id, workload, deadline pressure, and arrival/completion timing fields. | src/analysis/hoodie_runtime_evaluation_runner/model.py; src/analysis/hoodie_runtime_evaluation_runner/scenarios.py | artifacts/feature_085_full_audit/raw_rows.json; tests/unit/test_hoodie_runtime_evaluation_runner_scenarios.py | approximate_documented | The task model is reconstructed through deterministic scenario fixtures and runtime rows. |
| workload_arrival_representation | Workload arrivals are represented over time or documented as deterministic approximations. | Scenario definitions encode workload and deadline-pressure profiles deterministically with seeds. | src/analysis/hoodie_runtime_evaluation_runner/config.py; src/analysis/hoodie_runtime_evaluation_runner/scenarios.py | tests/unit/test_hoodie_runtime_evaluation_runner_scenarios.py; artifacts/feature_085_full_audit/execution_manifest.json | approximate_documented | Document the deterministic workload approximation; do not claim stochastic arrival fidelity. |
| private_queue_behavior | Local/private queue behavior contributes waiting and completion time before local execution finishes. | Queue-length observations and delay traces are captured in the runtime rows, but the queue is represented through deterministic evidence rather than a standalone queue engine. | src/analysis/hoodie_runtime_evaluation_runner/model.py; src/analysis/hoodie_runtime_evaluation_runner/runner.py | artifacts/feature_085_full_audit/raw_rows.json; tests/unit/test_hoodie_runtime_evaluation_runner_metrics.py | approximate_documented | This is an evidence-layer queue approximation, not a claim that the full FIFO queue simulator exists. |
| offloading_queue_behavior | Offloaded tasks use offloading queues and transmission-time evidence before destination execution. | Horizontal and vertical candidate traces expose delay components and queue-length snapshots for offloaded actions. | src/policies/mleo.py; src/analysis/hoodie_runtime_evaluation_runner/policies.py; src/analysis/hoodie_runtime_evaluation_runner/model.py | tests/unit/test_mleo_latency_evidence.py; artifacts/feature_085_full_audit/raw_rows.json | approximate_documented | The evidence is candidate-based, not a full queue-simulation replay. |
| public_cloud_queue_behavior | Public/cloud queues receive vertically offloaded tasks and expose cloud-side waiting/execution behavior. | The cloud path appears in the runtime outcomes and scenario traces; public/cloud queue behavior is documented through output timing rather than a separate queue model. | src/analysis/hoodie_runtime_evaluation_runner/scenarios.py; src/analysis/hoodie_runtime_evaluation_runner/runner.py | artifacts/feature_085_full_audit/raw_rows.json; artifacts/feature_085_full_audit/feature_085_audit_report.md | approximate_documented | The cloud queue is an audit abstraction and not a dedicated runtime queue class. |
| local_execution_delay | Local execution delay contributes to completion time. | Local actions surface delay values and completion times in raw rows and aggregate metrics. | src/analysis/hoodie_runtime_evaluation_runner/model.py; src/analysis/hoodie_runtime_evaluation_runner/runner.py | artifacts/feature_085_full_audit/raw_rows.json; tests/unit/test_hoodie_runtime_evaluation_runner_artifacts.py | approximate_documented | Local delay is evidenced in runtime rows, not by a standalone physical simulator. |
| horizontal_transmission_delay | Horizontal offload delay includes transmission delay between edge agents. | MLEO candidate traces expose horizontal transmission_delay and total_delay components. | src/policies/mleo.py; src/analysis/hoodie_runtime_evaluation_runner/policies.py | tests/unit/test_mleo_latency_evidence.py::test_mleo_selects_minimum_total_delay_not_minimum_queue_length | exact | No additional repair required for the evidence layer. |
| vertical_transmission_delay | Vertical offload delay includes EA-to-cloud transmission delay. | Vertical candidates in the MLEO and policy traces expose transmission_delay and total_delay components. | src/policies/mleo.py; src/analysis/hoodie_runtime_evaluation_runner/policies.py | tests/unit/test_mleo_latency_evidence.py; artifacts/feature_085_full_audit/raw_rows.json | exact | No additional repair required for the evidence layer. |
| remote_cloud_execution_delay | Remote/cloud execution delay contributes to total delay for vertical offload. | Cloud-bearing candidates carry compute_delay and total_delay evidence in the MLEO trace and runtime rows. | src/policies/mleo.py; src/analysis/hoodie_runtime_evaluation_runner/policies.py; src/analysis/hoodie_runtime_evaluation_runner/model.py | tests/unit/test_mleo_latency_evidence.py; artifacts/feature_085_full_audit/raw_rows.json | approximate_documented | The remote compute term is evidence-backed, not a separate cloud runtime service. |
| waiting_time_completion_time | Waiting time and completion time are explicit parts of task latency accounting. | Runtime rows capture arrival_time, completion_time, delay, and queue_length_observations. | src/analysis/hoodie_runtime_evaluation_runner/model.py; src/analysis/hoodie_runtime_evaluation_runner/runner.py | artifacts/feature_085_full_audit/raw_rows.json; artifacts/feature_085_full_audit/aggregate_by_policy.csv | approximate_documented | Completion timing is represented in the audit layer, not as a full event simulator. |
| timeout_drop_unavailability_behavior | Timeout, drop, and unavailability are reflected in output outcomes. | Runtime rows and aggregate metrics include dropped_timeout, dropped_unavailable, and illegal_action_rejected flags. | src/analysis/hoodie_runtime_evaluation_runner/model.py; src/analysis/hoodie_runtime_evaluation_runner/metrics.py | artifacts/feature_085_full_audit/raw_rows.json; tests/unit/test_hoodie_runtime_evaluation_runner_metrics.py | approximate_documented | The audit tracks these outcomes explicitly; it does not claim a full event-level simulator. |
| hybrid_action_model | Local, horizontal, and vertical actions exist as a hybrid offloading action space. | Active policies expose local, horizontal, and vertical families and the runtime policy set is the paper set. | src/analysis/hoodie_runtime_evaluation_runner/policies.py; src/analysis/hoodie_runtime_evaluation_runner/config.py | tests/unit/test_hoodie_runtime_evaluation_runner_policies.py::test_required_policy_set_matches_feature_085 | exact | No repair required; the hybrid action contract is already active. |
| two_stage_decision_boundary | Local-vs-offload and destination selection are distinct or are clearly documented when collapsed. | The runtime policy adapters operate as a documented single-stage approximation over legal candidate actions. | src/analysis/hoodie_runtime_evaluation_runner/policies.py; src/policies/mleo.py | tests/unit/test_hoodie_runtime_evaluation_runner_policies.py; tests/unit/test_mleo_latency_evidence.py | approximate_documented | Document the single-stage runtime approximation instead of pretending the training-stage boundary is reproduced. |
| hoodie_claim_boundary | HOODIE remains the proposed method boundary and is not renamed or expanded into a thesis/DCQ method. | Feature 085/086 artifacts keep HOODIE as the proposed method boundary and do not introduce an alternate method claim. | specs/086-mleo-latency-evidence-test/spec.md; specs/086-mleo-latency-evidence-test/quickstart.md; src/analysis/hoodie_runtime_evaluation_runner/report.py | tests/integration/test_hoodie_runtime_evaluation_runner_report.py; artifacts/feature_085_full_audit/feature_085_audit_report.md | exact | No thesis/DCQ/custom-method claim is allowed. |
| official_paper_baselines | Only RO, FLC, VO, HO, BCO, and MLEO are active baselines. | The runtime evaluation policy registry exposes exactly the paper baselines plus HOODIE. | src/analysis/hoodie_runtime_evaluation_runner/config.py; src/analysis/hoodie_runtime_evaluation_runner/policies.py | tests/unit/test_hoodie_runtime_evaluation_runner_policies.py::test_required_policy_set_matches_feature_085 | exact | No legacy active labels remain in the 086 outputs. |
| mleo_min_total_latency | MLEO selects the legal candidate with minimum estimated total latency, not queue length only. | The candidate trace test proves MLEO chooses the minimum total_delay candidate when queue-length minimum is different. | src/policies/mleo.py; src/analysis/hoodie_runtime_evaluation_runner/policies.py | tests/unit/test_mleo_latency_evidence.py::test_mleo_selects_minimum_total_delay_not_minimum_queue_length | exact | No repair required for the evidence layer; keep the numeric proof. |
| reward_cost_boundary | Reward/cost equations remain inside the paper’s comparison boundary and are not overclaimed. | The runtime audit reports reward, delay, and drop outcomes with explicit claim-boundary text. | src/analysis/hoodie_runtime_evaluation_runner/metrics.py; src/analysis/hoodie_runtime_evaluation_runner/report.py; resources/papers/hoodie/ocr/merged.txt | tests/unit/test_hoodie_runtime_evaluation_runner_metrics.py; artifacts/feature_085_full_audit/feature_085_audit_report.md | approximate_documented | Do not claim a trained end-to-end reward model; keep the boundary conservative. |
| output_metrics_readiness | Metrics are classified so that paper-headline comparison and repository diagnostics are not conflated. | The metric readiness matrix classifies primary, secondary, and diagnostic metrics explicitly. | specs/086-mleo-latency-evidence-test/metric-readiness-matrix.md; src/analysis/hoodie_system_model_fidelity_gate/report.py | tests/unit/test_hoodie_system_model_fidelity_gate.py | exact | Do not promote repository diagnostics to paper headline metrics. |

## System Model Gap Matrix
| mechanism_id | paper_expectation | simulator_behavior | code_location | test_artifact_evidence | status | required_fix_or_claim_boundary |
| --- | --- | --- | --- | --- | --- | --- |
| three_tier_topology | Task source / IoT layer, edge agents, and cloud are represented as a three-tier CEC topology. | The runtime layer uses deterministic topology profiles and scenario fixtures to represent the source, edge, and cloud tiers. | resources/papers/hoodie/ocr/merged.txt; src/analysis/hoodie_runtime_evaluation_runner/config.py; src/analysis/hoodie_runtime_evaluation_runner/scenarios.py | tests/unit/test_hoodie_runtime_evaluation_runner_scenarios.py; artifacts/feature_085_full_audit/raw_rows.json | approximate_documented | Document the deterministic topology abstraction; no new simulator topology is claimed. |
| edge_agent_set_cloud_node | Multiple edge agents plus one cloud node exist as active runtime participants. | The runtime policy set and scenario contexts model multiple edge agents plus a cloud destination. | src/analysis/hoodie_runtime_evaluation_runner/config.py; src/analysis/hoodie_runtime_evaluation_runner/model.py | tests/unit/test_hoodie_runtime_evaluation_runner_policies.py; artifacts/feature_085_full_audit/feature_085_audit_report.json | approximate_documented | Treat the active policy set and scenario contexts as the evidence boundary, not as a full distributed runtime simulator. |
| horizontal_connectivity_legality | Horizontal EA-to-EA destinations must be legal only when topology permits them. | The policy layer distinguishes legal horizontal destinations from illegal attempts and rejects invalid horizontal choices. | src/analysis/hoodie_runtime_evaluation_runner/policies.py; src/analysis/hoodie_runtime_evaluation_runner/scenarios.py | tests/unit/test_hoodie_runtime_evaluation_runner_policies.py::test_ho_prefers_horizontal_when_legal_destination_exists; tests/integration/test_hoodie_runtime_evaluation_runner_report.py | approximate_documented | The legality model is documented through candidate/action legality checks. |
| vertical_ea_cloud_path | Vertical offload reaches the cloud path and uses cloud-side execution capacity. | The runtime scenarios include cloud-vertical fallback and vertical offload decisions with cloud destinations. | src/analysis/hoodie_runtime_evaluation_runner/policies.py; src/analysis/hoodie_runtime_evaluation_runner/scenarios.py | tests/unit/test_hoodie_runtime_evaluation_runner_policies.py::test_vo_always_vertical; artifacts/feature_085_full_audit/raw_rows.json | approximate_documented | The cloud path is evidenced by scenario traces, not by a separate cloud simulator service. |
| task_model | Tasks carry ID, data size, CPU demand/processing density, and deadline/timeout semantics. | TaskBlueprint and scenario rows retain task_id, workload, deadline pressure, and arrival/completion timing fields. | src/analysis/hoodie_runtime_evaluation_runner/model.py; src/analysis/hoodie_runtime_evaluation_runner/scenarios.py | artifacts/feature_085_full_audit/raw_rows.json; tests/unit/test_hoodie_runtime_evaluation_runner_scenarios.py | approximate_documented | The task model is reconstructed through deterministic scenario fixtures and runtime rows. |
| workload_arrival_representation | Workload arrivals are represented over time or documented as deterministic approximations. | Scenario definitions encode workload and deadline-pressure profiles deterministically with seeds. | src/analysis/hoodie_runtime_evaluation_runner/config.py; src/analysis/hoodie_runtime_evaluation_runner/scenarios.py | tests/unit/test_hoodie_runtime_evaluation_runner_scenarios.py; artifacts/feature_085_full_audit/execution_manifest.json | approximate_documented | Document the deterministic workload approximation; do not claim stochastic arrival fidelity. |
| private_queue_behavior | Local/private queue behavior contributes waiting and completion time before local execution finishes. | Queue-length observations and delay traces are captured in the runtime rows, but the queue is represented through deterministic evidence rather than a standalone queue engine. | src/analysis/hoodie_runtime_evaluation_runner/model.py; src/analysis/hoodie_runtime_evaluation_runner/runner.py | artifacts/feature_085_full_audit/raw_rows.json; tests/unit/test_hoodie_runtime_evaluation_runner_metrics.py | approximate_documented | This is an evidence-layer queue approximation, not a claim that the full FIFO queue simulator exists. |
| offloading_queue_behavior | Offloaded tasks use offloading queues and transmission-time evidence before destination execution. | Horizontal and vertical candidate traces expose delay components and queue-length snapshots for offloaded actions. | src/policies/mleo.py; src/analysis/hoodie_runtime_evaluation_runner/policies.py; src/analysis/hoodie_runtime_evaluation_runner/model.py | tests/unit/test_mleo_latency_evidence.py; artifacts/feature_085_full_audit/raw_rows.json | approximate_documented | The evidence is candidate-based, not a full queue-simulation replay. |
| public_cloud_queue_behavior | Public/cloud queues receive vertically offloaded tasks and expose cloud-side waiting/execution behavior. | The cloud path appears in the runtime outcomes and scenario traces; public/cloud queue behavior is documented through output timing rather than a separate queue model. | src/analysis/hoodie_runtime_evaluation_runner/scenarios.py; src/analysis/hoodie_runtime_evaluation_runner/runner.py | artifacts/feature_085_full_audit/raw_rows.json; artifacts/feature_085_full_audit/feature_085_audit_report.md | approximate_documented | The cloud queue is an audit abstraction and not a dedicated runtime queue class. |
| local_execution_delay | Local execution delay contributes to completion time. | Local actions surface delay values and completion times in raw rows and aggregate metrics. | src/analysis/hoodie_runtime_evaluation_runner/model.py; src/analysis/hoodie_runtime_evaluation_runner/runner.py | artifacts/feature_085_full_audit/raw_rows.json; tests/unit/test_hoodie_runtime_evaluation_runner_artifacts.py | approximate_documented | Local delay is evidenced in runtime rows, not by a standalone physical simulator. |
| horizontal_transmission_delay | Horizontal offload delay includes transmission delay between edge agents. | MLEO candidate traces expose horizontal transmission_delay and total_delay components. | src/policies/mleo.py; src/analysis/hoodie_runtime_evaluation_runner/policies.py | tests/unit/test_mleo_latency_evidence.py::test_mleo_selects_minimum_total_delay_not_minimum_queue_length | exact | No additional repair required for the evidence layer. |
| vertical_transmission_delay | Vertical offload delay includes EA-to-cloud transmission delay. | Vertical candidates in the MLEO and policy traces expose transmission_delay and total_delay components. | src/policies/mleo.py; src/analysis/hoodie_runtime_evaluation_runner/policies.py | tests/unit/test_mleo_latency_evidence.py; artifacts/feature_085_full_audit/raw_rows.json | exact | No additional repair required for the evidence layer. |
| remote_cloud_execution_delay | Remote/cloud execution delay contributes to total delay for vertical offload. | Cloud-bearing candidates carry compute_delay and total_delay evidence in the MLEO trace and runtime rows. | src/policies/mleo.py; src/analysis/hoodie_runtime_evaluation_runner/policies.py; src/analysis/hoodie_runtime_evaluation_runner/model.py | tests/unit/test_mleo_latency_evidence.py; artifacts/feature_085_full_audit/raw_rows.json | approximate_documented | The remote compute term is evidence-backed, not a separate cloud runtime service. |
| waiting_time_completion_time | Waiting time and completion time are explicit parts of task latency accounting. | Runtime rows capture arrival_time, completion_time, delay, and queue_length_observations. | src/analysis/hoodie_runtime_evaluation_runner/model.py; src/analysis/hoodie_runtime_evaluation_runner/runner.py | artifacts/feature_085_full_audit/raw_rows.json; artifacts/feature_085_full_audit/aggregate_by_policy.csv | approximate_documented | Completion timing is represented in the audit layer, not as a full event simulator. |
| timeout_drop_unavailability_behavior | Timeout, drop, and unavailability are reflected in output outcomes. | Runtime rows and aggregate metrics include dropped_timeout, dropped_unavailable, and illegal_action_rejected flags. | src/analysis/hoodie_runtime_evaluation_runner/model.py; src/analysis/hoodie_runtime_evaluation_runner/metrics.py | artifacts/feature_085_full_audit/raw_rows.json; tests/unit/test_hoodie_runtime_evaluation_runner_metrics.py | approximate_documented | The audit tracks these outcomes explicitly; it does not claim a full event-level simulator. |
| hybrid_action_model | Local, horizontal, and vertical actions exist as a hybrid offloading action space. | Active policies expose local, horizontal, and vertical families and the runtime policy set is the paper set. | src/analysis/hoodie_runtime_evaluation_runner/policies.py; src/analysis/hoodie_runtime_evaluation_runner/config.py | tests/unit/test_hoodie_runtime_evaluation_runner_policies.py::test_required_policy_set_matches_feature_085 | exact | No repair required; the hybrid action contract is already active. |
| two_stage_decision_boundary | Local-vs-offload and destination selection are distinct or are clearly documented when collapsed. | The runtime policy adapters operate as a documented single-stage approximation over legal candidate actions. | src/analysis/hoodie_runtime_evaluation_runner/policies.py; src/policies/mleo.py | tests/unit/test_hoodie_runtime_evaluation_runner_policies.py; tests/unit/test_mleo_latency_evidence.py | approximate_documented | Document the single-stage runtime approximation instead of pretending the training-stage boundary is reproduced. |
| hoodie_claim_boundary | HOODIE remains the proposed method boundary and is not renamed or expanded into a thesis/DCQ method. | Feature 085/086 artifacts keep HOODIE as the proposed method boundary and do not introduce an alternate method claim. | specs/086-mleo-latency-evidence-test/spec.md; specs/086-mleo-latency-evidence-test/quickstart.md; src/analysis/hoodie_runtime_evaluation_runner/report.py | tests/integration/test_hoodie_runtime_evaluation_runner_report.py; artifacts/feature_085_full_audit/feature_085_audit_report.md | exact | No thesis/DCQ/custom-method claim is allowed. |
| official_paper_baselines | Only RO, FLC, VO, HO, BCO, and MLEO are active baselines. | The runtime evaluation policy registry exposes exactly the paper baselines plus HOODIE. | src/analysis/hoodie_runtime_evaluation_runner/config.py; src/analysis/hoodie_runtime_evaluation_runner/policies.py | tests/unit/test_hoodie_runtime_evaluation_runner_policies.py::test_required_policy_set_matches_feature_085 | exact | No legacy active labels remain in the 086 outputs. |
| mleo_min_total_latency | MLEO selects the legal candidate with minimum estimated total latency, not queue length only. | The candidate trace test proves MLEO chooses the minimum total_delay candidate when queue-length minimum is different. | src/policies/mleo.py; src/analysis/hoodie_runtime_evaluation_runner/policies.py | tests/unit/test_mleo_latency_evidence.py::test_mleo_selects_minimum_total_delay_not_minimum_queue_length | exact | No repair required for the evidence layer; keep the numeric proof. |
| reward_cost_boundary | Reward/cost equations remain inside the paper’s comparison boundary and are not overclaimed. | The runtime audit reports reward, delay, and drop outcomes with explicit claim-boundary text. | src/analysis/hoodie_runtime_evaluation_runner/metrics.py; src/analysis/hoodie_runtime_evaluation_runner/report.py; resources/papers/hoodie/ocr/merged.txt | tests/unit/test_hoodie_runtime_evaluation_runner_metrics.py; artifacts/feature_085_full_audit/feature_085_audit_report.md | approximate_documented | Do not claim a trained end-to-end reward model; keep the boundary conservative. |
| output_metrics_readiness | Metrics are classified so that paper-headline comparison and repository diagnostics are not conflated. | The metric readiness matrix classifies primary, secondary, and diagnostic metrics explicitly. | specs/086-mleo-latency-evidence-test/metric-readiness-matrix.md; src/analysis/hoodie_system_model_fidelity_gate/report.py | tests/unit/test_hoodie_system_model_fidelity_gate.py | exact | Do not promote repository diagnostics to paper headline metrics. |

## Metric Readiness Summary
- paper_primary_metric: `task_completion_delay, task_drop_ratio`
- paper_secondary_or_derived_metric: `completion_rate`
- paper_secondary_or_repository_metric: `average_reward, total_reward, throughput`
- repository_diagnostic_metric: `timeout_drop_rate, unavailable_drop_rate, deadline_violation_rate, queue_stability_score, illegal_action_rejection_count`

## Metric Readiness Matrix
| metric | classification | paper_use | status | evidence |
| --- | --- | --- | --- | --- |
| task_completion_delay | paper_primary_metric | headline_paper-comparison metric | ready | paper OCR defines average delay / completion-delay comparison and runtime rows expose completion time and delay. |
| task_drop_ratio | paper_primary_metric | headline_paper-comparison metric | ready | paper OCR compares drop ratio and runtime rows expose timeout/drop/unavailability outcomes. |
| completion_rate | paper_secondary_or_derived_metric | derived reliability metric for supporting analysis | ready | Derived from completed and dropped rows in the runtime evaluation bundle. |
| timeout_drop_rate | repository_diagnostic_metric | runtime diagnostic; not a paper headline metric | diagnostic_only | Useful for simulator validation; do not present as a paper headline unless separately justified. |
| unavailable_drop_rate | repository_diagnostic_metric | runtime diagnostic; not a paper headline metric | diagnostic_only | Tracks availability failures as a simulator diagnostic. |
| deadline_violation_rate | repository_diagnostic_metric | runtime diagnostic; not a paper headline metric | diagnostic_only | Tracks deadline misses as a validation aid, not as a headline paper metric. |
| average_reward | paper_secondary_or_repository_metric | supporting optimization metric with an explicit claim boundary | ready_with_boundary | Reward output exists in runtime rows but the audit does not claim a full training-loop reproduction. |
| total_reward | paper_secondary_or_repository_metric | supporting optimization metric with an explicit claim boundary | ready_with_boundary | Aggregate reward is exposed for analysis and marked as a supporting metric only. |
| throughput | paper_secondary_or_repository_metric | supporting system-throughput metric with an explicit claim boundary | ready_with_boundary | Throughput is retained as a secondary comparison metric, not a headline one. |
| queue_stability_score | repository_diagnostic_metric | internal diagnostic only | diagnostic_only | Queue-stability score is an audit helper, not a paper metric. |
| illegal_action_rejection_count | repository_diagnostic_metric | legal-action diagnostic only | diagnostic_only | Counts illegal-action rejections to validate legality handling. |

## Scenario Mechanism Coverage Summary
- exact scenarios: `7`

## Scenario Mechanism Coverage
| scenario | workload | deadline_pressure | exercised_mechanisms | status | evidence |
| --- | --- | --- | --- | --- | --- |
| light_load_no_deadline_pressure | low | relaxed | ['local_execution_delay', 'hybrid_action_model', 'output_metrics_readiness'] | exact | Runtime rows include low-load local and offload decisions with completed-delay evidence. |
| tight_deadline_pressure | high | tight | ['timeout_drop_unavailability_behavior', 'mleo_min_total_latency', 'output_metrics_readiness'] | exact | This is the divergent HOODIE/MLEO scenario with explicit delay-vs-drop behavior. |
| legal_horizontal_offload | medium | moderate | ['horizontal_connectivity_legality', 'horizontal_transmission_delay', 'hybrid_action_model'] | exact | Horizontal offload is legal and exercised in runtime rows and policy tests. |
| illegal_horizontal_destination_attempt | medium | moderate | ['horizontal_connectivity_legality', 'timeout_drop_unavailability_behavior', 'hybrid_action_model'] | exact | Illegal horizontal destination attempts are rejected in policy traces. |
| cloud_vertical_fallback | high | tight | ['vertical_ea_cloud_path', 'vertical_transmission_delay', 'remote_cloud_execution_delay'] | exact | Cloud fallback exercises the vertical/cloud path and cloud delay components. |
| timeout_drop_case | high | tight | ['timeout_drop_unavailability_behavior', 'waiting_time_completion_time', 'mleo_min_total_latency'] | exact | Timeout/drop behavior is exercised and the HOODIE/MLEO divergence is documented here. |
| mixed_local_horizontal_cloud_candidates | medium | moderate | ['hybrid_action_model', 'two_stage_decision_boundary', 'official_paper_baselines'] | exact | Mixed candidate sets exercise local, horizontal, and vertical candidate selection. |

## HOODIE / MLEO Tie Evidence
- source_artifact_dir: `artifacts/feature_085_full_audit`
- matching_rows: `1080`
- differing_rows: `432`
- identical_scenarios: `cloud_vertical_fallback, illegal_horizontal_destination_attempt, legal_horizontal_offload, light_load_no_deadline_pressure, mixed_local_horizontal_cloud_candidates`
- divergent_scenarios: `tight_deadline_pressure, timeout_drop_case`
- divergent_action_counts: `{"tight_deadline_pressure": {"vertical->local": 216}, "timeout_drop_case": {"vertical->local": 216}}`

## Allowed Paper-Comparison Metrics
- task_completion_delay
- task_drop_ratio
- completion_rate
- average_reward
- total_reward
- throughput

## Repository Diagnostic Metrics
- timeout_drop_rate
- unavailable_drop_rate
- deadline_violation_rate
- queue_stability_score
- illegal_action_rejection_count

## Remaining Approximations
- three_tier_topology
- edge_agent_set_cloud_node
- horizontal_connectivity_legality
- vertical_ea_cloud_path
- task_model
- workload_arrival_representation
- private_queue_behavior
- offloading_queue_behavior
- public_cloud_queue_behavior
- local_execution_delay
- remote_cloud_execution_delay
- waiting_time_completion_time
- timeout_drop_unavailability_behavior
- two_stage_decision_boundary
- reward_cost_boundary

## Scope Proof
- Active policies are the paper set: HOODIE, RO, FLC, VO, HO, BCO, MLEO.
- No legacy active labels are exposed in the Feature 086 outputs.
- No thesis/DCQ/custom-method code is added.
- MLEO evidence remains a policy-evidence boundary, not a new proposed method.

## Claim Boundary
- HOODIE remains the Feature 080 proposed method boundary.
- No thesis method, DCQ method, or custom queue redesign is introduced.
- The audit documents interface-only DRL/LSTM/forecast boundaries where full training is not reproduced.
- No full empirical HOODIE reproduction claim is made.
