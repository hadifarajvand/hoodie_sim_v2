from __future__ import annotations

from dataclasses import replace
from typing import Any, Callable

from src.evaluation.runner import EvaluationRunner

from .schemas import DecisionRecord as CanonicalDecisionRecord
from .schemas import TaskRecord as CanonicalTaskRecord

_INSTALLED = False
_ORIGINAL_RUN: Callable[..., dict[str, object]] | None = None
_RECORDS: dict[str, dict[str, Any]] = {}


def _record_key(run_id: object, task_id: object) -> str:
    return f"{run_id}:{task_id}"


def _expanded_legal_mask(record: dict[str, Any]) -> dict[str, bool]:
    raw = record.get("legal_action_mask", {})
    mask = (
        {str(key): bool(value) for key, value in raw.items()}
        if isinstance(raw, dict)
        else {}
    )
    observation = record.get("decision_observation", {})
    if isinstance(observation, dict):
        topology = observation.get("topology", ())
        if isinstance(topology, (list, tuple, set)) and (
            mask.get("horizontal") or mask.get("offload_horizontal")
        ):
            for destination in topology:
                mask[f"horizontal_{destination}"] = True
    if mask.get("vertical") or mask.get("offload_vertical"):
        mask["cloud"] = True
    if mask.get("compute_local"):
        mask["local"] = True
    return mask


def _run_with_record_registry(
    self: EvaluationRunner, *args: Any, **kwargs: Any
) -> dict[str, object]:
    if _ORIGINAL_RUN is None:  # pragma: no cover
        raise RuntimeError("evaluation record patch is not installed")
    _RECORDS.clear()
    result = _ORIGINAL_RUN(self, *args, **kwargs)
    per_trace = result.get("per_trace", [])
    if isinstance(per_trace, list):
        for trace in per_trace:
            if not isinstance(trace, dict):
                continue
            run_id = trace.get("trace_id", "")
            raw_records = trace.get("raw_records", [])
            if not isinstance(raw_records, list):
                continue
            for record in raw_records:
                if isinstance(record, dict) and record.get("task_id") is not None:
                    _RECORDS[_record_key(run_id, record["task_id"])] = dict(record)
    return result


def enriched_task_record(*args: Any, **kwargs: Any) -> CanonicalTaskRecord:
    record = CanonicalTaskRecord(*args, **kwargs)
    evidence = _RECORDS.get(_record_key(record.run_id, record.task_id))
    if evidence is None:
        return record

    observation = evidence.get("decision_observation", {})
    observation = observation if isinstance(observation, dict) else {}
    workload = dict(record.workload)
    if observation.get("size") is not None:
        workload["task_size_mbits"] = float(observation["size"])
    if observation.get("processing_density") is not None:
        workload["processing_density_gcycles_per_mbit"] = float(
            observation["processing_density"]
        )
    source_agent = evidence.get("source_agent_id")
    decision_slot = evidence.get("decision_slot")
    deadline = observation.get("absolute_deadline_slot", record.deadline)
    owner = (
        f"EA-{source_agent}"
        if source_agent is not None and record.policy == "HOODIE"
        else record.learner_owner
    )
    return replace(
        record,
        source_agent=(
            str(source_agent) if source_agent is not None else record.source_agent
        ),
        decision_slot=(
            int(decision_slot)
            if decision_slot is not None
            else record.decision_slot
        ),
        deadline=int(deadline) if deadline is not None else None,
        workload=workload,
        learner_owner=owner,
    )


def enriched_decision_record(
    *args: Any, **kwargs: Any
) -> CanonicalDecisionRecord:
    record = CanonicalDecisionRecord(*args, **kwargs)
    evidence = _RECORDS.pop(record.observation_ref, None)
    if evidence is None:
        return record

    observation = evidence.get("decision_observation", {})
    observation = observation if isinstance(observation, dict) else {}
    q_summary = observation.get("hoodie_q_value_summary", {})
    q_summary = (
        {str(key): float(value) for key, value in q_summary.items()}
        if isinstance(q_summary, dict)
        else {}
    )
    forecast = dict(record.forecast_fields)
    forecast.update(
        {
            "decision_slot": evidence.get("decision_slot"),
            "source_agent_id": evidence.get("source_agent_id"),
            "queue_load": observation.get("queue_load"),
            "history_length": observation.get("history_length"),
        }
    )
    metadata = dict(record.policy_metadata)
    metadata.update(
        {
            "source_agent_id": evidence.get("source_agent_id"),
            "resolved_destination": evidence.get("resolved_destination"),
        }
    )
    return replace(
        record,
        legal_action_mask=_expanded_legal_mask(evidence),
        forecast_fields=forecast,
        q_value_summary=q_summary,
        policy_metadata=metadata,
    )


def install_evaluation_record_patch() -> None:
    global _INSTALLED
    global _ORIGINAL_RUN
    if _INSTALLED:
        return

    from . import production_patch

    _ORIGINAL_RUN = EvaluationRunner.run
    EvaluationRunner.run = _run_with_record_registry  # type: ignore[method-assign]
    production_patch.TaskRecord = enriched_task_record  # type: ignore[assignment]
    production_patch.DecisionRecord = enriched_decision_record  # type: ignore[assignment]
    _INSTALLED = True
