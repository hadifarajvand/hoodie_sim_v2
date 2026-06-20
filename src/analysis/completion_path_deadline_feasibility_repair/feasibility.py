from __future__ import annotations

from collections import Counter, defaultdict
from math import ceil
from typing import Any

from src.environment.compute_config import ComputeConfig
from src.environment.link_rate_config import LinkRateConfig, compute_transmission_delay, mbits_to_bits

from .config import RECORD_SAMPLE_LIMIT, SAMPLED_COMPLETION_PATH_MAX_TASK_DECISIONS
from .model import FeasibilityEstimate


def _task_key(task: dict[str, Any]) -> str:
    return f"{task.get('trace_id')}:{task.get('episode_id')}:{task.get('task_id')}"


def estimate_task_action_feasibility(task: dict[str, Any]) -> dict[str, Any]:
    compute_config = ComputeConfig()
    link_rate_config = LinkRateConfig()
    task_size = float(task.get("task_size", task.get("size", 0.0)) or 0.0)
    processing_density = float(task.get("processing_density", 0.0) or 0.0)
    required_cycles = task_size * processing_density
    timeout_length = int(task.get("timeout_length", 0) or 0)
    local_estimated_execution_slots = ceil(required_cycles / compute_config.cpu_capacity_per_slot_agent) if required_cycles else 0
    horizontal_transmission_slots = compute_transmission_delay(
        mbits_to_bits(task_size),
        link_rate_config.horizontal_data_rate_bps,
        slot_duration_seconds=link_rate_config.slot_duration_seconds,
        rounding_policy=link_rate_config.rounding_policy,
    ).delay_slots
    vertical_transmission_slots = compute_transmission_delay(
        mbits_to_bits(task_size),
        link_rate_config.vertical_data_rate_bps,
        slot_duration_seconds=link_rate_config.slot_duration_seconds,
        rounding_policy=link_rate_config.rounding_policy,
    ).delay_slots
    horizontal_estimated_execution_slots = ceil(required_cycles / compute_config.cpu_capacity_per_slot_edge) if required_cycles else 0
    vertical_estimated_execution_slots = ceil(required_cycles / compute_config.cpu_capacity_per_slot_cloud) if required_cycles else 0
    horizontal_estimated_total_slots = horizontal_transmission_slots + horizontal_estimated_execution_slots
    vertical_estimated_total_slots = vertical_transmission_slots + vertical_estimated_execution_slots
    local_slack = timeout_length - local_estimated_execution_slots
    horizontal_slack = timeout_length - horizontal_estimated_total_slots
    vertical_slack = timeout_length - vertical_estimated_total_slots
    estimate = FeasibilityEstimate(
        local_estimated_execution_slots=int(local_estimated_execution_slots),
        horizontal_estimated_transmission_slots=int(horizontal_transmission_slots),
        horizontal_estimated_execution_slots=int(horizontal_estimated_execution_slots),
        horizontal_estimated_total_slots=int(horizontal_estimated_total_slots),
        vertical_estimated_transmission_slots=int(vertical_transmission_slots),
        vertical_estimated_execution_slots=int(vertical_estimated_execution_slots),
        vertical_estimated_total_slots=int(vertical_estimated_total_slots),
        deadline_slack_for_local=int(local_slack),
        deadline_slack_for_horizontal=int(horizontal_slack),
        deadline_slack_for_vertical=int(vertical_slack),
        local_feasible_before_deadline=local_slack >= 0,
        horizontal_feasible_before_deadline=horizontal_slack >= 0,
        vertical_feasible_before_deadline=vertical_slack >= 0,
        estimate_source="compute_config+link_rate_config+task_metadata",
        estimate_confidence="high",
        missing_fields=[],
    ).to_dict()
    return estimate | {
        "trace_id": task.get("trace_id"),
        "episode_id": task.get("episode_id"),
        "task_id": task.get("task_id"),
        "arrival_slot": task.get("arrival_slot"),
        "absolute_deadline_slot": task.get("absolute_deadline_slot"),
        "timeout_length": timeout_length,
        "task_size": task_size,
        "processing_density": processing_density,
        "required_cycles_gcycles": required_cycles,
        "selected_action": task.get("selected_action"),
        "legal_action_mask": dict(task.get("legal_action_mask", {})),
        "source_agent_id": task.get("source_agent_id"),
        "queue_load_at_decision": int(task.get("queue_load", 0) or 0),
    }


def build_task_feasibility_summary(task_records: dict[str, dict[str, Any]], *, record_sample_limit: int = RECORD_SAMPLE_LIMIT) -> dict[str, Any]:
    records_by_task_key: dict[str, dict[str, Any]] = {}
    feasible_by_action = Counter({"local": 0, "horizontal": 0, "vertical": 0})
    infeasible_by_action = Counter({"local": 0, "horizontal": 0, "vertical": 0})
    selected_action_feasible_count = 0
    selected_action_infeasible_count = 0
    all_actions_infeasible = 0
    local_ratios: list[float] = []
    horizontal_ratios: list[float] = []
    vertical_ratios: list[float] = []
    sample_records: list[dict[str, Any]] = []

    for key, record in task_records.items():
        estimate = estimate_task_action_feasibility(record)
        records_by_task_key[key] = estimate
        if len(sample_records) < record_sample_limit:
            sample_records.append(dict(estimate))
        local_ratios.append(1.0 if estimate["local_feasible_before_deadline"] else 0.0)
        horizontal_ratios.append(1.0 if estimate["horizontal_feasible_before_deadline"] else 0.0)
        vertical_ratios.append(1.0 if estimate["vertical_feasible_before_deadline"] else 0.0)
        selected_action = str(estimate.get("selected_action") or "")
        selected_feasible = bool(
            {
                "local": estimate["local_feasible_before_deadline"],
                "compute_local": estimate["local_feasible_before_deadline"],
                "horizontal": estimate["horizontal_feasible_before_deadline"],
                "offload_horizontal": estimate["horizontal_feasible_before_deadline"],
                "vertical": estimate["vertical_feasible_before_deadline"],
                "offload_vertical": estimate["vertical_feasible_before_deadline"],
            }.get(selected_action, False)
        )
        if selected_feasible:
            selected_action_feasible_count += 1
        else:
            selected_action_infeasible_count += 1
        if not any(
            (
                estimate["local_feasible_before_deadline"],
                estimate["horizontal_feasible_before_deadline"],
                estimate["vertical_feasible_before_deadline"],
            )
        ):
            all_actions_infeasible += 1
        if estimate["local_feasible_before_deadline"]:
            feasible_by_action["local"] += 1
        else:
            infeasible_by_action["local"] += 1
        if estimate["horizontal_feasible_before_deadline"]:
            feasible_by_action["horizontal"] += 1
        else:
            infeasible_by_action["horizontal"] += 1
        if estimate["vertical_feasible_before_deadline"]:
            feasible_by_action["vertical"] += 1
        else:
            infeasible_by_action["vertical"] += 1

    total_task_count = len(task_records)
    summary = {
        "total_task_count": total_task_count,
        "local_feasible_task_count": int(feasible_by_action["local"]),
        "horizontal_feasible_task_count": int(feasible_by_action["horizontal"]),
        "vertical_feasible_task_count": int(feasible_by_action["vertical"]),
        "all_actions_infeasible_task_count": int(all_actions_infeasible),
        "selected_action_feasible_task_count": int(selected_action_feasible_count),
        "selected_action_infeasible_task_count": int(selected_action_infeasible_count),
        "local_feasible_ratio": float(sum(local_ratios) / max(len(local_ratios), 1)),
        "horizontal_feasible_ratio": float(sum(horizontal_ratios) / max(len(horizontal_ratios), 1)),
        "vertical_feasible_ratio": float(sum(vertical_ratios) / max(len(vertical_ratios), 1)),
        "sample_records": sample_records,
        "records_by_task_key": records_by_task_key,
        "all_actions_infeasible": all_actions_infeasible == total_task_count and total_task_count > 0,
        "estimate_source": "compute_config+link_rate_config+task_metadata",
        "estimate_confidence": "high",
        "missing_fields": [],
    }
    summary["feasible_task_count_by_action"] = {
        "local": int(feasible_by_action["local"]),
        "horizontal": int(feasible_by_action["horizontal"]),
        "vertical": int(feasible_by_action["vertical"]),
    }
    summary["infeasible_task_count_by_action"] = {
        "local": int(infeasible_by_action["local"]),
        "horizontal": int(infeasible_by_action["horizontal"]),
        "vertical": int(infeasible_by_action["vertical"]),
    }
    summary["feasible_task_ratio"] = (
        float(summary["local_feasible_task_count"] + summary["horizontal_feasible_task_count"] + summary["vertical_feasible_task_count"]) / max(total_task_count * 3, 1)
    )
    return summary


def build_action_path_feasibility(task_feasibility_summary: dict[str, Any]) -> dict[str, Any]:
    total_task_count = int(task_feasibility_summary["total_task_count"])
    feasible_by_action = dict(task_feasibility_summary["feasible_task_count_by_action"])
    infeasible_by_action = dict(task_feasibility_summary["infeasible_task_count_by_action"])
    return {
        "total_task_count": total_task_count,
        "feasible_task_count_by_action": feasible_by_action,
        "infeasible_task_count_by_action": infeasible_by_action,
        "local_feasible_ratio": float(task_feasibility_summary["local_feasible_ratio"]),
        "horizontal_feasible_ratio": float(task_feasibility_summary["horizontal_feasible_ratio"]),
        "vertical_feasible_ratio": float(task_feasibility_summary["vertical_feasible_ratio"]),
        "all_actions_infeasible": bool(task_feasibility_summary["all_actions_infeasible"]),
        "sample_records": list(task_feasibility_summary["sample_records"]),
    }


def build_completion_path_probe(evaluation_result: dict[str, Any], *, max_task_decisions_to_analyze: int = SAMPLED_COMPLETION_PATH_MAX_TASK_DECISIONS) -> dict[str, Any]:
    decision_count = int(evaluation_result.get("evaluation_decision_count", 0))
    task_records = list(evaluation_result.get("task_records", {}).values())
    sampled_records = task_records[:max_task_decisions_to_analyze]
    return {
        "sampled_completion_path_probe": {
            "evaluation_episode_count": int(evaluation_result.get("evaluation_episode_count", 0)),
            "max_task_decisions_to_analyze": max_task_decisions_to_analyze,
            "analyzed_decision_count": len(sampled_records),
            "purpose": "fast feasibility inspection",
            "sample_records": sampled_records[:25],
        },
        "full_evaluation_probe": {
            "evaluation_episode_count": int(evaluation_result.get("evaluation_episode_count", 0)),
            "episode_length": int(evaluation_result.get("episode_length", 0)),
            "expected_max_decision_slots": int(evaluation_result.get("evaluation_episode_count", 0)) * int(evaluation_result.get("episode_length", 0)),
            "observed_decision_count": decision_count,
            "purpose": "paper-aligned evaluation coverage check",
        },
    }


def build_evaluation_coverage_classification(completion_path_probe: dict[str, Any]) -> dict[str, Any]:
    full_probe = completion_path_probe["full_evaluation_probe"]
    observed = int(full_probe["observed_decision_count"])
    evaluation_episode_count = int(full_probe["evaluation_episode_count"])
    expected = int(full_probe["expected_max_decision_slots"])
    if observed == expected:
        evaluation_mode = "full_step_evaluation"
        one_decision_per_episode_observed = False
        full_step_decision_coverage_unavailable = False
    elif observed == evaluation_episode_count:
        evaluation_mode = "full_episode_single_task_evaluation"
        one_decision_per_episode_observed = True
        full_step_decision_coverage_unavailable = True
    else:
        evaluation_mode = "sampled_task_decision_evaluation"
        one_decision_per_episode_observed = False
        full_step_decision_coverage_unavailable = observed < expected
    return {
        "evaluation_mode": evaluation_mode,
        "sampled_completion_path_probe": completion_path_probe["sampled_completion_path_probe"],
        "full_evaluation_probe": full_probe,
        "observed_decision_count": observed,
        "one_decision_per_episode_observed": one_decision_per_episode_observed,
        "full_step_decision_coverage_unavailable": full_step_decision_coverage_unavailable,
        "expected_max_decision_slots": expected,
        "evaluation_episode_count": evaluation_episode_count,
    }
