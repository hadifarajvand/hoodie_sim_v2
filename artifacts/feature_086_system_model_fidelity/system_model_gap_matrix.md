# Feature 086 System Model Gap Matrix

| mechanism_id | status | required_fix_or_claim_boundary |
| --- | --- | --- |
| three_tier_topology | approximate_documented | Document the deterministic topology abstraction; no new simulator topology is claimed. |
| edge_agent_set_cloud_node | approximate_documented | Treat the active policy set and scenario contexts as the evidence boundary, not as a full distributed runtime simulator. |
| horizontal_connectivity_legality | approximate_documented | The legality model is documented through candidate/action legality checks. |
| vertical_ea_cloud_path | approximate_documented | The cloud path is evidenced by scenario traces, not by a separate cloud simulator service. |
| task_model | approximate_documented | The task model is reconstructed through deterministic scenario fixtures and runtime rows. |
| workload_arrival_representation | approximate_documented | Document the deterministic workload approximation; do not claim stochastic arrival fidelity. |
| private_queue_behavior | approximate_documented | This is an evidence-layer queue approximation, not a claim that the full FIFO queue simulator exists. |
| offloading_queue_behavior | approximate_documented | The evidence is candidate-based, not a full queue-simulation replay. |
| public_cloud_queue_behavior | approximate_documented | The cloud queue is an audit abstraction and not a dedicated runtime queue class. |
| local_execution_delay | approximate_documented | Local delay is evidenced in runtime rows, not by a standalone physical simulator. |
| horizontal_transmission_delay | exact | No additional repair required for the evidence layer. |
| vertical_transmission_delay | exact | No additional repair required for the evidence layer. |
| remote_cloud_execution_delay | approximate_documented | The remote compute term is evidence-backed, not a separate cloud runtime service. |
| waiting_time_completion_time | approximate_documented | Completion timing is represented in the audit layer, not as a full event simulator. |
| timeout_drop_unavailability_behavior | approximate_documented | The audit tracks these outcomes explicitly; it does not claim a full event-level simulator. |
| hybrid_action_model | exact | No repair required; the hybrid action contract is already active. |
| two_stage_decision_boundary | approximate_documented | Document the single-stage runtime approximation instead of pretending the training-stage boundary is reproduced. |
| hoodie_claim_boundary | exact | No thesis/DCQ/custom-method claim is allowed. |
| official_paper_baselines | exact | No legacy active labels remain in the 086 outputs. |
| mleo_min_total_latency | exact | No repair required for the evidence layer; keep the numeric proof. |
| reward_cost_boundary | approximate_documented | Do not claim a trained end-to-end reward model; keep the boundary conservative. |
| output_metrics_readiness | exact | Do not promote repository diagnostics to paper headline metrics. |
