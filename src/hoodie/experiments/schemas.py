from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class TaskRecord:
    campaign_id: str
    panel_id: str
    job_id: str
    run_id: str
    policy: str
    variant: str | None
    seed: int
    trace_hash: str
    task_id: str
    source_agent: str
    arrival_slot: int
    workload: dict[str, object]
    deadline: int | None
    decision_slot: int
    selected_action: str
    destination: str
    completion_or_drop_slot: int | None
    outcome: str
    queue_delay: float | None
    transmission_delay: float | None
    service_delay: float | None
    end_to_end_delay: float | None
    reward: float
    learner_owner: str
    config_hash: str
    source_hash: str
    checkpoint_hash: str

@dataclass(frozen=True, slots=True)
class DecisionRecord:
    observation_ref: str
    legal_action_mask: dict[str, bool]
    selected_action: str
    exploration: bool
    forecast_fields: dict[str, object]
    q_value_summary: dict[str, float]
    policy_metadata: dict[str, object]

@dataclass(frozen=True, slots=True)
class TransitionRecord:
    owner: str
    originating_decision: str
    delayed_reward: float
    next_state: str
    terminal: bool
    assignment_slot: int
    uniqueness_id: str

@dataclass(frozen=True, slots=True)
class TrainingHistoryRecord:
    episode_or_step: int
    loss: float
    epsilon: float
    replay_size: int
    target_update_count: int
    checkpoint_id: str

@dataclass(frozen=True, slots=True)
class AggregateRecord:
    offered_tasks: int
    completed_tasks: int
    dropped_tasks: int
    completion_ratio: float
    drop_ratio: float
    average_delay: float
    component_delays: dict[str, float]
    action_distribution: dict[str, int]
    reward_aggregates: dict[str, float]
    confidence_interval: tuple[float, float]
    seed_count: int
    denominator_contract: str
