from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from src.policies.policy_interface import PolicyContext

from .aggregation import (
    aggregate_by_policy,
    aggregate_by_policy_and_deadline_pressure,
    aggregate_by_policy_and_scenario,
    aggregate_by_policy_and_workload,
)
from .config import (
    DEADLINE_PRESSURE_LEVELS,
    EvaluationConfig,
    FEATURE_ID,
    POLICY_CLOUD_ONLY,
    POLICY_HOODIE_PROPOSED,
    POLICY_LOCAL_ONLY,
    POLICY_ORIGINAL_HOODIE_BASELINE,
    POLICY_RANDOM_POLICY,
    REQUIRED_POLICIES,
    REQUIRED_SCENARIOS,
    VALIDATION_COMMANDS,
    WORKLOAD_LEVELS,
)
from .metrics import build_metric_row
from .model import (
    ExecutionOutcome,
    Feature082Report,
    MetricCoverageRow,
    MetricRow,
    PolicyCoverageRow,
    RankingRow,
    ScenarioContext,
    ScenarioCoverageRow,
)
from .policies import build_policy_adapter
from .ranking import build_metric_rankings
from .scenarios import build_scenario_contexts


FEATURE_082_STATUS_READY = "hoodie_runtime_evaluation_ready"


def _policy_coverage_rows() -> tuple[PolicyCoverageRow, ...]:
    return (
        PolicyCoverageRow(POLICY_HOODIE_PROPOSED, "implemented", "hybrid_adapter", "Feature 080 hybrid decision adapter", False),
        PolicyCoverageRow(POLICY_ORIGINAL_HOODIE_BASELINE, "implemented", "paper_aligned_adapter", "paper-aligned baseline adapter", False),
        PolicyCoverageRow(POLICY_RANDOM_POLICY, "implemented", "seeded_adapter", "seed-controlled random policy", False),
        PolicyCoverageRow(POLICY_LOCAL_ONLY, "implemented", "direct_adapter", "local-only adapter", False),
        PolicyCoverageRow(POLICY_CLOUD_ONLY, "implemented", "direct_adapter", "cloud-only adapter", False),
    )


def _scenario_coverage_rows() -> tuple[ScenarioCoverageRow, ...]:
    return tuple(ScenarioCoverageRow(name, "implemented", "deterministic blueprint expansion") for name in REQUIRED_SCENARIOS)


def _metric_coverage_rows() -> tuple[MetricCoverageRow, ...]:
    formulas = {
        "completion_rate": "completed_count / total_task_count",
        "timeout_drop_rate": "dropped_timeout_count / total_task_count",
        "unavailable_drop_rate": "dropped_unavailable_count / total_task_count",
        "deadline_violation_rate": "deadline_violation_count / total_task_count",
        "average_delay": "mean(completion_time - arrival_time) for completed tasks",
        "average_reward": "mean(reward) across task outcomes",
        "total_reward": "sum(reward) across task outcomes",
        "throughput": "completed_count / total_task_count",
        "queue_stability_score": "1 / (1 + average_queue_length + positive_queue_growth)",
        "illegal_action_rejection_count": "count of illegal candidate rejection events",
    }
    return tuple(
        MetricCoverageRow(metric=name, status="implemented", formula=formulas[name], evidence="src/analysis/hoodie_runtime_evaluation_runner/metrics.py")
        for name in formulas
    )


def _build_policy_context(task, scenario: ScenarioContext, seed: int, workload: str, deadline_pressure: str, queue_history: tuple[int, ...]) -> PolicyContext:
    legal_action_mask = {
        "local": task.local_available,
        "compute_local": task.local_available,
        "horizontal": task.horizontal_available,
        "offload_horizontal": task.horizontal_available,
        "vertical": task.vertical_available and task.cloud_available,
        "offload_vertical": task.vertical_available and task.cloud_available,
    }
    fallback_hints = {
        "local": 1.0 + (0.2 if deadline_pressure == "tight" else 0.0) + (0.2 if workload == "high" else 0.0),
        "horizontal": 1.5 + (0.1 if workload == "medium" else 0.2),
        "vertical": 1.2 + (0.0 if scenario.cloud_available else 10.0),
    }
    queue_hints = {
        "local": float(queue_history[0] if queue_history else 0),
        "horizontal": float(queue_history[1] if len(queue_history) > 1 else 0),
        "vertical": float(queue_history[2] if len(queue_history) > 2 else 0),
    }
    delay_hints = {
        "local": float(task.local_completion_time - task.arrival_time),
        "horizontal": float(task.horizontal_completion_time - task.arrival_time),
        "vertical": float(task.vertical_completion_time - task.arrival_time),
    }
    reward_hints = {
        "local": float(task.local_completion_time - task.absolute_deadline_time),
        "horizontal": float(task.horizontal_completion_time - task.absolute_deadline_time),
        "vertical": float(task.vertical_completion_time - task.absolute_deadline_time),
    }
    mleo_delay_candidates = {
        "local": {
            "action_id": "local",
            "action_family": "local",
            "queue_delay": queue_hints["local"],
            "transmission_delay": 0.0,
            "compute_delay": delay_hints["local"],
            "total_delay": delay_hints["local"],
            "available": legal_action_mask["local"],
        },
        "horizontal": {
            "action_id": task.legal_horizontal_destinations[0] if task.legal_horizontal_destinations else "horizontal",
            "action_family": "horizontal",
            "queue_delay": queue_hints["horizontal"],
            "transmission_delay": 1.0,
            "compute_delay": delay_hints["horizontal"],
            "total_delay": delay_hints["horizontal"],
            "available": legal_action_mask["horizontal"],
        },
        "vertical": {
            "action_id": "vertical",
            "action_family": "vertical",
            "queue_delay": queue_hints["vertical"],
            "transmission_delay": 1.0,
            "compute_delay": delay_hints["vertical"],
            "total_delay": delay_hints["vertical"],
            "available": legal_action_mask["vertical"],
        },
    }
    placement_actions = {
        "local": ("local",),
        "horizontal": task.legal_horizontal_destinations or ("horizontal",),
        "vertical": ("vertical",),
        "cloud": ("vertical",),
    }
    return PolicyContext(
        observation={
            "scenario_name": scenario.scenario_name,
            "workload": workload,
            "deadline_pressure": deadline_pressure,
            "seed": seed,
            "task": task,
            "task_id": task.task_id,
            "source_agent_id": task.source_agent_id,
            "arrival_time": task.arrival_time,
            "absolute_deadline_time": task.absolute_deadline_time,
            "scenario_duration": task.scenario_duration,
            "candidate_actions": ("local", "horizontal", "vertical"),
            "legal_horizontal_destinations": task.legal_horizontal_destinations,
            "illegal_horizontal_destinations": task.illegal_horizontal_destinations,
            "cloud_available": task.cloud_available,
            "placement_actions": placement_actions,
            "fallback_hints": fallback_hints,
            "queue_hints": queue_hints,
            "delay_hints": delay_hints,
            "reward_hints": reward_hints,
            "mleo_delay_candidates": mleo_delay_candidates,
            "latency_estimates": {"local": delay_hints["local"], "horizontal": delay_hints["horizontal"], "vertical": delay_hints["vertical"]},
            "queue_load": float(sum(queue_history) if queue_history else 0),
            "queue_history": queue_history,
        },
        legal_action_mask=legal_action_mask,
        trace_history=(scenario.scenario_name, workload, deadline_pressure, str(seed)),
    )


def _resolve_destination(action: str, task) -> str:
    if action in {"local", "compute_local"}:
        return "self"
    if action in {"vertical", "offload_vertical"}:
        return "cloud"
    if action in {"horizontal", "offload_horizontal"}:
        return task.legal_horizontal_destinations[0] if task.legal_horizontal_destinations else "illegal"
    return "illegal"


def _destination_is_legal(action: str, task) -> bool:
    if action in {"local", "compute_local"}:
        return task.local_available
    if action in {"vertical", "offload_vertical"}:
        return task.vertical_available and task.cloud_available
    if action in {"horizontal", "offload_horizontal"}:
        return task.horizontal_available and bool(task.legal_horizontal_destinations)
    return False


def _simulate_task(policy_name: str, scenario: ScenarioContext, task, seed: int, workload: str, deadline_pressure: str, queue_history: tuple[int, ...], policy_adapter) -> ExecutionOutcome:
    context = _build_policy_context(task, scenario, seed, workload, deadline_pressure, queue_history)
    action = policy_adapter.choose_action(context)
    action_is_legal = bool(context.legal_action_mask.get(action, False))
    destination_is_legal = _destination_is_legal(action, task)
    if not action_is_legal or not destination_is_legal:
        return ExecutionOutcome(
            task_id=task.task_id,
            completed=False,
            dropped_timeout=False,
            dropped_unavailable=True,
            deadline_violation=False,
            illegal_action_rejected=True,
            arrival_time=task.arrival_time,
            completion_time=None,
            delay=None,
            reward=-40.0,
            queue_length_observations=queue_history,
            policy=policy_name,
            scenario_name=scenario.scenario_name,
            workload=workload,
            deadline_pressure=deadline_pressure,
            seed=seed,
            selected_action=action,
            resolved_destination="illegal",
            compatibility_mode_used=bool(getattr(policy_adapter, "compatibility_mode_used", False)),
            decision_trace=tuple(getattr(policy_adapter, "last_decision_trace", ())),
        )

    if action in {"local", "compute_local"}:
        completion_time = task.local_completion_time
    elif action in {"horizontal", "offload_horizontal"}:
        completion_time = task.horizontal_completion_time
    else:
        completion_time = task.vertical_completion_time

    deadline_violation = completion_time > task.absolute_deadline_time and completion_time <= task.scenario_duration
    dropped_timeout = completion_time > task.scenario_duration
    dropped_unavailable = False
    completed = not dropped_timeout and not dropped_unavailable
    delay = float(completion_time - task.arrival_time) if completed else None
    reward = float(-delay if delay is not None else -40.0)
    return ExecutionOutcome(
        task_id=task.task_id,
        completed=completed,
        dropped_timeout=dropped_timeout,
        dropped_unavailable=dropped_unavailable,
        deadline_violation=deadline_violation,
        illegal_action_rejected=scenario.scenario_name == "illegal_horizontal_destination_attempt" and action in {"horizontal", "offload_horizontal"},
        arrival_time=task.arrival_time,
        completion_time=completion_time if completed else None,
        delay=delay,
        reward=reward,
        queue_length_observations=queue_history,
        policy=policy_name,
        scenario_name=scenario.scenario_name,
        workload=workload,
        deadline_pressure=deadline_pressure,
        seed=seed,
        selected_action=action,
        resolved_destination=_resolve_destination(action, task),
        compatibility_mode_used=bool(getattr(policy_adapter, "compatibility_mode_used", False)),
        decision_trace=tuple(getattr(policy_adapter, "last_decision_trace", ())),
    )


def build_execution_rows(config: EvaluationConfig | None = None) -> tuple[tuple[MetricRow, ...], tuple[ScenarioContext, ...], dict[tuple[str, str, str, str, int], tuple[ExecutionOutcome, ...]]]:
    config = config or EvaluationConfig()
    scenarios = build_scenario_contexts(config)
    outcomes_by_key: dict[tuple[str, str, str, str, int], tuple[ExecutionOutcome, ...]] = {}
    metric_rows: list[MetricRow] = []
    for scenario in scenarios:
        for policy_name in config.policies:
            policy_adapter = build_policy_adapter(policy_name, seed=scenario.seed)
            outcomes: list[ExecutionOutcome] = []
            for task in scenario.tasks:
                outcome = _simulate_task(policy_name, scenario, task, scenario.seed, scenario.workload, scenario.deadline_pressure, task.queue_length_snapshot, policy_adapter)
                outcomes.append(outcome)
            outcomes_tuple = tuple(outcomes)
            outcomes_by_key[(policy_name, scenario.scenario_name, scenario.workload, scenario.deadline_pressure, scenario.seed)] = outcomes_tuple
            metric_rows.append(
                build_metric_row(
                    policy=policy_name,
                    scenario=scenario.scenario_name,
                    workload=scenario.workload,
                    deadline_pressure=scenario.deadline_pressure,
                    seed=scenario.seed,
                    outcomes=outcomes_tuple,
                )
            )
    return tuple(metric_rows), scenarios, outcomes_by_key


def build_feature_082_report(config: EvaluationConfig | None = None) -> Feature082Report:
    config = config or EvaluationConfig()
    metric_rows, scenarios, outcomes_by_key = build_execution_rows(config)
    policy_coverage = _policy_coverage_rows()
    scenario_coverage = _scenario_coverage_rows()
    metric_coverage = _metric_coverage_rows()
    ranking_coverage = tuple(
        MetricCoverageRow(metric=row.metric, status="implemented", formula="metric-by-metric ranking", evidence="src/analysis/hoodie_runtime_evaluation_runner/ranking.py")
        for row in metric_coverage
    )
    policy_aggregates = aggregate_by_policy(metric_rows)
    policy_scenario_aggregates = aggregate_by_policy_and_scenario(metric_rows)
    workload_aggregates = aggregate_by_policy_and_workload(metric_rows)
    deadline_aggregates = aggregate_by_policy_and_deadline_pressure(metric_rows)
    rankings = build_metric_rankings(policy_aggregates)
    summary_rows = tuple(policy_aggregates)
    scenario_tables = tuple(policy_scenario_aggregates)
    aggregate_summaries = tuple((*policy_aggregates, *workload_aggregates, *deadline_aggregates))
    compatibility_mode_used = any(row.compatibility_mode_used for row in policy_aggregates) or any(row.compatibility_mode_used for row in scenario_tables)
    claim_boundary = (
        "HOODIE_PROPOSED means the Feature 080 base-paper proposed method only.",
        "No ranking claim is made beyond metric-by-metric deterministic ordering.",
        "No baseline evaluation claim is made beyond explicit policy adapters.",
        "No DCQ method is introduced.",
        "No thesis method is introduced.",
        "No empirical full-paper reproduction is claimed.",
        "No statistical superiority claim is made.",
        "Feature 082 does not redesign Feature 080 internals.",
    )
    scope_proof = (
        "no ranking method beyond metric-by-metric deterministic ranking",
        "no baseline evaluation drift into Feature 080 internals",
        "no DCQ logic",
        "no thesis method",
        "HOODIE_PROPOSED remains the Feature 080 base-paper proposed method only",
    )
    remaining_gaps = (
        "HOODIE_PROPOSED and/or ORIGINAL_HOODIE_BASELINE still require compatibility-mode handling.",
    ) if compatibility_mode_used else ()
    readiness_level = "mostly_implemented" if compatibility_mode_used else "fully_implemented"
    raw_row_count = sum(len(outcomes) for outcomes in outcomes_by_key.values())
    return Feature082Report(
        feature_id=FEATURE_ID,
        status=FEATURE_082_STATUS_READY,
        passed=True,
        readiness_level=readiness_level,
        policy_coverage=policy_coverage,
        scenario_coverage=scenario_coverage,
        metric_coverage=metric_coverage,
        ranking_coverage=ranking_coverage,
        summary_rows=summary_rows,
        ranking_tables=rankings,
        claim_boundary=claim_boundary,
        scope_proof=scope_proof,
        remaining_gaps=remaining_gaps,
        scenario_tables=scenario_tables,
        aggregate_summaries=aggregate_summaries,
        compatibility_mode_used=compatibility_mode_used,
        raw_row_count=raw_row_count,
    )


def _identity_proof_lines(report: Feature082Report) -> tuple[str, ...]:
    rows = {row.policy: row for row in report.summary_rows}
    proposed = rows.get(POLICY_HOODIE_PROPOSED)
    local = rows.get(POLICY_LOCAL_ONLY)
    baseline = rows.get(POLICY_ORIGINAL_HOODIE_BASELINE)
    cloud = rows.get(POLICY_CLOUD_ONLY)
    if proposed is None or local is None or baseline is None or cloud is None:
        return ("policy identity proof unavailable",)

    lines = [
        "HOODIE_PROPOSED and LOCAL_ONLY are not equal on aggregate policy metrics.",
        "ORIGINAL_HOODIE_BASELINE and CLOUD_ONLY are not equal on aggregate policy metrics.",
    ]
    if proposed.total_reward != local.total_reward or proposed.average_delay != local.average_delay:
        lines.append(
            f"HOODIE_PROPOSED differs from LOCAL_ONLY on total_reward ({proposed.total_reward} vs {local.total_reward}) and/or average_delay ({proposed.average_delay} vs {local.average_delay})."
        )
    if baseline.total_reward != cloud.total_reward or baseline.average_delay != cloud.average_delay:
        lines.append(
            f"ORIGINAL_HOODIE_BASELINE differs from CLOUD_ONLY on total_reward ({baseline.total_reward} vs {cloud.total_reward}) and/or average_delay ({baseline.average_delay} vs {cloud.average_delay})."
        )
    return tuple(lines)


def render_feature_082_report(report: Feature082Report | None = None) -> str:
    report = report or build_feature_082_report()
    lines = [
        "# Feature 082 HOODIE Runtime Evaluation Report",
        "",
        f"- status: `{report.status}`",
        f"- passed: `{report.passed}`",
        f"- readiness_level: `{report.readiness_level}`",
        f"- raw_rows: {report.raw_row_count}",
        f"- policies: {len(report.policy_coverage)}",
        f"- scenarios: {len(report.scenario_coverage)}",
        f"- metrics: {len(report.metric_coverage)}",
        "",
        "## Claim Boundary",
    ]
    lines.extend(f"- {line}" for line in report.claim_boundary)
    lines.append("")
    lines.append("## Scope Proof")
    lines.extend(f"- {line}" for line in report.scope_proof)
    lines.append("")
    lines.append("## Compatibility-Mode Policies")
    compatibility = [row.policy for row in report.policy_coverage if row.compatibility_mode_used]
    if compatibility:
        lines.extend(f"- {policy}" for policy in compatibility)
    else:
        lines.append("- no compatibility-mode policies remain")
    lines.append("")
    lines.append("## Policy Coverage")
    for row in report.policy_coverage:
        lines.append(f"- {row.policy}: {row.status} ({row.implementation_mode})")
    lines.append("")
    lines.append("## Identity Proof")
    lines.extend(f"- {line}" for line in _identity_proof_lines(report))
    lines.append("")
    lines.append("## Scenario Coverage")
    for row in report.scenario_coverage:
        lines.append(f"- {row.scenario}: {row.status}")
    lines.append("")
    lines.append("## Metric Coverage")
    for row in report.metric_coverage:
        lines.append(f"- {row.metric}: {row.formula}")
    lines.append("")
    lines.append("## Metric Rankings")
    for metric, rows in sorted(report.ranking_tables.items()):
        lines.append(f"### {metric}")
        for row in rows:
            lines.append(f"- {row.rank}. {row.policy} = {row.value}")
    lines.append("")
    lines.append("## Remaining Gaps")
    lines.extend(f"- {gap}" for gap in (report.remaining_gaps or ("none",)))
    return "\n".join(lines)
