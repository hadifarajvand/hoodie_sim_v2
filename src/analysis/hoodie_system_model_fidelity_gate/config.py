from __future__ import annotations

from pathlib import Path


FEATURE_ID = "086-mleo-latency-evidence-test"
FEATURE_NAME = "HOODIE System-Model Fidelity Gate"

READY_STATUS = "system_model_fidelity_ready_for_output_comparison"
BLOCKED_STATUS = "system_model_fidelity_blocked"

DEFAULT_OUTPUT_DIR = Path("artifacts/feature_086_system_model_fidelity")
FEATURE_085_AUDIT_DIR = Path("artifacts/feature_085_full_audit")

ACTIVE_POLICIES = ("HOODIE", "RO", "FLC", "VO", "HO", "BCO", "MLEO")
INVALID_LABELS = ("MQO", "Minimum Queue Offloader", "ORIGINAL_HOODIE_BASELINE", "HOODIE_PROPOSED")

REQUIRED_METRICS = (
    "task_completion_delay",
    "task_drop_ratio",
    "completion_rate",
    "timeout_drop_rate",
    "unavailable_drop_rate",
    "deadline_violation_rate",
    "average_reward",
    "total_reward",
    "throughput",
    "queue_stability_score",
    "illegal_action_rejection_count",
)

PAPER_PRIMARY_METRICS = ("task_completion_delay", "task_drop_ratio")
PAPER_SECONDARY_OR_DERIVED_METRICS = ("completion_rate",)
PAPER_SECONDARY_OR_REPOSITORY_METRICS = ("average_reward", "total_reward", "throughput")
REPOSITORY_DIAGNOSTIC_METRICS = (
    "timeout_drop_rate",
    "unavailable_drop_rate",
    "deadline_violation_rate",
    "queue_stability_score",
    "illegal_action_rejection_count",
)

REQUIRED_MECHANISM_IDS = (
    "three_tier_topology",
    "edge_agent_set_cloud_node",
    "horizontal_connectivity_legality",
    "vertical_ea_cloud_path",
    "task_model",
    "workload_arrival_representation",
    "private_queue_behavior",
    "offloading_queue_behavior",
    "public_cloud_queue_behavior",
    "local_execution_delay",
    "horizontal_transmission_delay",
    "vertical_transmission_delay",
    "remote_cloud_execution_delay",
    "waiting_time_completion_time",
    "timeout_drop_unavailability_behavior",
    "hybrid_action_model",
    "two_stage_decision_boundary",
    "hoodie_claim_boundary",
    "official_paper_baselines",
    "mleo_min_total_latency",
    "reward_cost_boundary",
    "output_metrics_readiness",
)

