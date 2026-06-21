"""Paper mechanism -> repository implementation map."""

from __future__ import annotations

from typing import Any

# (mechanism, paper_expected, repo_current, implementation_status, gap, source, confidence, required_action)
_ROWS = [
    ("network_topology", "Multi-server CEC graph, 20 agents, adjacency Fig.7", "structured topology registry + env", "matched_with_documented_approximation", "exact adjacency matrix G not numerically recovered (image-only Fig.7)", "paper_pdf:Fig.7", "medium", "keep calibrated topology; document G gap"),
    ("number_of_agents", "N = 20 Edge Agents (EA)", "agent set in env/campaign", "matched", "none", "paper_pdf:Table4/text", "high", "keep"),
    ("edge_nodes", "ECs (M) with private/public queues", "edge node + private/public queues", "matched_with_documented_approximation", "M count not numerically fixed", "paper_pdf:notation", "medium", "document M"),
    ("cloud_node", "Single cloud, 30 GHz", "cloud queue capacity sharing module", "matched", "none", "paper_pdf:Table4", "high", "keep"),
    ("horizontal_offload_path", "One-hop horizontal to neighbor EA public queue", "runtime_model horizontal route", "matched_with_documented_approximation", "exact one-hop sentence not OCR-recovered", "paper_pdf:text", "medium", "keep"),
    ("vertical_offload_path", "Vertical to cloud", "runtime_model vertical route", "matched", "none", "paper_pdf:text", "high", "keep"),
    ("local_execution_path", "Local compute in private queue", "execution_helper local path", "matched", "none", "paper_pdf:text", "high", "keep"),
    ("task_arrival", "Bernoulli arrival prob P per slot (x_n(t))", "traffic_generator", "matched_with_documented_approximation", "P swept in paper; calibrated here", "paper_pdf:Algorithm1", "medium", "expose P in config"),
    ("task_size", "Set of task sizes H [bits]", "task size in trace_protocol", "matched_with_documented_approximation", "exact size set calibrated", "paper_pdf:notation", "medium", "tag calibration_profile"),
    ("processing_density", "rho_n(t) [CPU cycles/bit]", "task.py processing density", "matched_with_documented_approximation", "exact density set calibrated", "paper_pdf:notation", "medium", "tag calibration_profile"),
    ("deadline_timeout", "Timeout = 20 slots (2 sec)", "deadline_rules / absolute_deadline_slot", "matched", "none", "paper_pdf:Table4", "high", "keep"),
    ("queueing_model", "FIFO private/public queues, capacity shared among active public queues", "private/public/offloading queues", "matched_with_documented_approximation", "exact paper citation indirect", "paper_pdf:text", "medium", "keep"),
    ("transmission_model", "Horizontal R_H / vertical R_V data rates", "link_rate registry / transmission wiring", "implemented_but_unverified", "exact R_H/R_V not numerically fixed", "paper_pdf:notation", "medium", "document link rates"),
    ("execution_model", "Slot-based compute decrement using CPU freq / Delta", "runtime_model compute_service_delay", "matched", "none", "paper_pdf:Table4", "high", "keep"),
    ("reward_function", "r=-Phi_n(t) success, -C(=40) drop, NaN no-arrival (Eq.20)", "reward_timing.py", "matched_with_documented_approximation", "Phi_n approximated as (completion-arrival+1)", "paper_pdf:Eq20/Table4", "high", "keep; do not modify reward"),
    ("state_representation", "Per-agent observation incl. load, queues, task features", "deadline_queue_feasibility_v1 (state_dim=30)", "matched_with_documented_approximation", "exact paper feature vector not enumerated", "paper_pdf:text", "medium", "keep"),
    ("action_space", "Local / horizontal / vertical decisions (d1/d2)", "3-action legal-masked space", "matched", "none", "paper_pdf:Eq19", "high", "keep"),
    ("drl_algorithm", "Double + Dueling DQN with LSTM, eps-greedy", "DDQNTrainer", "matched_with_documented_approximation", "LSTM/dueling depth not fully verified vs 3x1024+1x20", "paper_pdf:Table4", "medium", "verify network shape later"),
    ("replay_target_optimizer", "Replay N_R=10000, batch 64, Adam, MSE, target copy N_copy", "trainer replay buffer + optimizer", "matched_with_documented_approximation", "N_R/N_copy not asserted equal to paper", "paper_pdf:Table4", "medium", "document"),
    ("training_schedule", "N_E=5000 episodes, T=110 slots", "staged budgets (<=300 here)", "matched_with_documented_approximation", "5000 intentionally not executed (bounded smoke)", "paper_pdf:Table4", "high", "full campaign config only"),
    ("evaluation_schedule", "Per-episode evaluation over traces", "evaluate_policy_on_trace_bank_terminal_repaired", "matched", "none", "existing_repo", "high", "keep"),
    ("baselines", "Several baseline offloading methods", "fixed local/horizontal/vertical + random legal", "matched_with_documented_approximation", "exact paper baseline names not enumerated", "paper_pdf:abstract", "medium", "document missing named baselines"),
    ("metrics", "Drop rate, average processing delay, throughput, reward", "paper-compatible metric schema", "matched", "none", "paper_pdf:text", "high", "keep"),
    ("figures", "Reward/drop/delay vs P; topology", "matplotlib figures", "matched_with_documented_approximation", "P-sweep figure not reproduced (single calibrated P)", "paper_pdf:figures", "medium", "keep"),
    ("seed_reproducibility", "Deterministic seeds per episode", "seed bundle in campaign config", "matched", "none", "existing_repo", "high", "keep"),
    ("energy_cost", "Not a primary metric in base reward (delay+drop focus)", "not modeled", "not_applicable", "energy/cost not in reward Eq.20", "paper_pdf:Eq20", "high", "report energy_metric_status=not_implemented"),
]

_FIELDS = ("mechanism", "paper_expected", "repo_current", "implementation_status", "gap", "source", "confidence", "required_action")


def build_mechanism_map() -> dict[str, Any]:
    rows = [dict(zip(_FIELDS, r)) for r in _ROWS]
    from collections import Counter

    status_counts = Counter(r["implementation_status"] for r in rows)
    return {
        "mechanism_count": len(rows),
        "status_counts": dict(status_counts),
        "rows": rows,
        "paper_mechanism_map_completed": True,
    }
