from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .policy_interface import PolicyContext


def _extract_observation_payload(observation: Mapping[str, object]) -> dict[str, object]:
    if not observation:
        return {}
    if any(isinstance(value, dict) for value in observation.values()) and all(
        isinstance(value, dict) for value in observation.values() if value is not None
    ):
        first_key = next(iter(observation))
        nested = observation.get(first_key)
        if isinstance(nested, dict):
            return dict(nested)
    return dict(observation)


def _coerce_tuple(value: object) -> tuple[object, ...] | None:
    if value is None:
        return None
    if isinstance(value, tuple):
        return value
    if isinstance(value, list):
        return tuple(value)
    return (value,)


@dataclass(frozen=True, slots=True)
class AdaptiveDecisionContext:
    agent_id: str | int | None
    current_slot: int | None
    task_id: int | str | None
    task_size: float | None
    processing_density: float | None
    cycles_required: float | None
    cycles_remaining: float | None
    timeout_length: int | None
    absolute_deadline_slot: int | None
    legal_action_mask: dict[str, bool]
    queue_load: float | int | None
    observed_arrival_probability: float | None
    arrivals_per_slot: tuple[int, ...] | None
    arrivals_per_agent: dict[str, int] | None
    latency_estimates: dict[str, float] | None
    balance_hint: dict[str, float] | None
    topology: object | None
    traffic_summary: dict[str, object] | None
    execution_summary: dict[str, object] | None
    observation: dict[str, object]


def build_adaptive_context(
    policy_context: PolicyContext,
    traffic_summary: Mapping[str, object] | None = None,
    execution_summary: Mapping[str, object] | None = None,
) -> AdaptiveDecisionContext:
    observation = _extract_observation_payload(policy_context.observation)
    legal_action_mask = dict(policy_context.legal_action_mask)
    nested_traffic = observation.get("traffic_summary")
    nested_execution = observation.get("execution_summary")
    traffic_payload = dict(traffic_summary or nested_traffic or {}) if (traffic_summary or nested_traffic) else None
    execution_payload = (
        dict(execution_summary or nested_execution or {}) if (execution_summary or nested_execution) else None
    )

    arrivals_per_slot = traffic_payload.get("arrivals_per_slot") if isinstance(traffic_payload, dict) else observation.get("arrivals_per_slot")
    arrivals_per_agent = traffic_payload.get("arrivals_per_agent") if isinstance(traffic_payload, dict) else observation.get("arrivals_per_agent")
    if arrivals_per_slot is None:
        arrivals_per_slot = observation.get("arrivals_per_slot")
    if arrivals_per_agent is None:
        arrivals_per_agent = observation.get("arrivals_per_agent")

    return AdaptiveDecisionContext(
        agent_id=observation.get("source_agent_id", observation.get("agent_id")),
        current_slot=observation.get("slot", observation.get("current_slot")),
        task_id=observation.get("task_id"),
        task_size=observation.get("size"),
        processing_density=observation.get("processing_density"),
        cycles_required=observation.get("cycles_required"),
        cycles_remaining=observation.get("cycles_remaining"),
        timeout_length=observation.get("timeout_length"),
        absolute_deadline_slot=observation.get("absolute_deadline_slot"),
        legal_action_mask=legal_action_mask,
        queue_load=observation.get("queue_load", observation.get("load_hint")),
        observed_arrival_probability=(
            traffic_payload.get("observed_arrival_probability") if isinstance(traffic_payload, dict) else observation.get("observed_arrival_probability")
        ),
        arrivals_per_slot=_coerce_tuple(arrivals_per_slot),
        arrivals_per_agent=dict(arrivals_per_agent) if isinstance(arrivals_per_agent, dict) else None,
        latency_estimates=dict(observation.get("latency_estimates", {})) if isinstance(observation.get("latency_estimates"), dict) else None,
        balance_hint=dict(observation.get("balance_hint", {})) if isinstance(observation.get("balance_hint"), dict) else None,
        topology=observation.get("topology"),
        traffic_summary=dict(traffic_payload) if isinstance(traffic_payload, dict) else None,
        execution_summary=dict(execution_payload) if isinstance(execution_payload, dict) else None,
        observation=observation,
    )
