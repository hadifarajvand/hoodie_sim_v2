# HOODIE paper mechanism map

| Mechanism | Status | Confidence | Gap |
|---|---|---|---|
| network_topology | matched_with_documented_approximation | medium | exact adjacency matrix G not numerically recovered (image-only Fig.7) |
| number_of_agents | matched | high | none |
| edge_nodes | matched_with_documented_approximation | medium | M count not numerically fixed |
| cloud_node | matched | high | none |
| horizontal_offload_path | matched_with_documented_approximation | medium | exact one-hop sentence not OCR-recovered |
| vertical_offload_path | matched | high | none |
| local_execution_path | matched | high | none |
| task_arrival | matched_with_documented_approximation | medium | P swept in paper; calibrated here |
| task_size | matched_with_documented_approximation | medium | exact size set calibrated |
| processing_density | matched_with_documented_approximation | medium | exact density set calibrated |
| deadline_timeout | matched | high | none |
| queueing_model | matched_with_documented_approximation | medium | exact paper citation indirect |
| transmission_model | implemented_but_unverified | medium | exact R_H/R_V not numerically fixed |
| execution_model | matched | high | none |
| reward_function | matched_with_documented_approximation | high | Phi_n approximated as (completion-arrival+1) |
| state_representation | matched_with_documented_approximation | medium | exact paper feature vector not enumerated |
| action_space | matched | high | none |
| drl_algorithm | matched_with_documented_approximation | medium | LSTM/dueling depth not fully verified vs 3x1024+1x20 |
| replay_target_optimizer | matched_with_documented_approximation | medium | N_R/N_copy not asserted equal to paper |
| training_schedule | matched_with_documented_approximation | high | 5000 intentionally not executed (bounded smoke) |
| evaluation_schedule | matched | high | none |
| baselines | matched_with_documented_approximation | medium | exact paper baseline names not enumerated |
| metrics | matched | high | none |
| figures | matched_with_documented_approximation | medium | P-sweep figure not reproduced (single calibrated P) |
| seed_reproducibility | matched | high | none |
| energy_cost | not_applicable | high | energy/cost not in reward Eq.20 |
