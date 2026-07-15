from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
import json
from typing import Any


@dataclass(frozen=True, slots=True)
class TaskRecord:
    campaign_id: str
    run_id: str
    policy: str
    seed: int
    trace_hash: str
    task_id: str
    source_agent: str
    arrival_slot: int
    decision_slot: int
    selected_action: str
    destination: str
    completion_or_drop_slot: int | None
    outcome: str
    end_to_end_delay: float | None
    queue_delay: float | None
    transmission_delay: float | None
    service_delay: float | None
    reward: float
    learner_owner: str
    checkpoint_hash: str
    configuration_hash: str


@dataclass(frozen=True, slots=True)
class PairedMetrics:
    offered_tasks: int
    completed_tasks: int
    dropped_tasks: int
    completion_ratio: float
    drop_ratio: float
    average_end_to_end_delay: float
    action_distribution: dict[str, int]
    per_agent_metrics: dict[str, dict[str, float]]
    aggregate_reward: float


def hash_payload(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256(encoded).hexdigest()


def validate_fairness(reference: dict[str, Any], candidate: dict[str, Any]) -> None:
    keys = ("trace_hash", "offered_tasks", "task_ids", "topology_hash", "physical_configuration", "horizon", "seed_set", "metric_denominator", "warmup_handling", "checkpoint_selection_rule")
    mismatches = {key for key in keys if reference.get(key) != candidate.get(key)}
    if mismatches:
        raise ValueError(f"Fairness violation: {sorted(mismatches)}")


def paired_metric_summary(records: list[TaskRecord]) -> PairedMetrics:
    offered = len(records)
    completed = sum(1 for record in records if record.outcome == "completed")
    dropped = sum(1 for record in records if record.outcome == "dropped")
    delays = [record.end_to_end_delay for record in records if record.end_to_end_delay is not None]
    distribution: dict[str, int] = {}
    per_agent: dict[str, dict[str, float]] = {}
    reward = 0.0
    for record in records:
        distribution[record.selected_action] = distribution.get(record.selected_action, 0) + 1
        reward += float(record.reward)
        stats = per_agent.setdefault(record.source_agent, {"tasks": 0.0, "completed": 0.0, "dropped": 0.0})
        stats["tasks"] += 1
        if record.outcome == "completed":
            stats["completed"] += 1
        if record.outcome == "dropped":
            stats["dropped"] += 1
    completion_ratio = completed / offered if offered else 0.0
    drop_ratio = dropped / offered if offered else 0.0
    average_delay = sum(delays) / len(delays) if delays else 0.0
    return PairedMetrics(offered, completed, dropped, completion_ratio, drop_ratio, average_delay, distribution, per_agent, reward)

