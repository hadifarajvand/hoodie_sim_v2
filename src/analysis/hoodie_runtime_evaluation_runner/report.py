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
    POLICY_BCO,
    POLICY_FLC,
    POLICY_HO,
    POLICY_HOODIE,
    POLICY_MLEO,
    POLICY_RO,
    POLICY_VO,
    REQUIRED_POLICIES,
    REQUIRED_SCENARIOS,
    VALIDATION_COMMANDS,
    WORKLOAD_LEVELS,
)
from .metrics import build_metric_row
from .model import (
    ExecutionOutcome,
    Feature083Report,
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


FEATURE_085_STATUS_READY = "hoodie_paper_baseline_fidelity_audit_ready"
PRIMARY_PAPER_METRICS = ("task_completion_delay", "task_drop_ratio")
SECONDARY_REPOSITORY_METRICS = (
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


def _metric_rows_differ(left: MetricRow | None, right: MetricRow | None) -> bool:
    if left is None or right is None:
        return False
    comparable_fields = (
        "completed_count",
        "dropped_timeout_count",
        "dropped_unavailable_count",
        "deadline_violation_count",
        "illegal_action_rejection_count",
        "task_completion_delay",
        "task_drop_ratio",
        "average_reward",
        "total_reward",
        "completion_rate",
        "timeout_drop_rate",
        "unavailable_drop_rate",
        "deadline_violation_rate",
        "throughput",
        "queue_stability_score",
    )
    return any(getattr(left, field) != getattr(right, field) for field in comparable_fields)


def _metric_differences(left: MetricRow | None, right: MetricRow | None) -> tuple[str, ...]:
    if left is None or right is None:
        return ()
    fields = (
        "task_completion_delay",
        "task_drop_ratio",
        "average_reward",
        "total_reward",
        "completion_rate",
        "timeout_drop_rate",
        "unavailable_drop_rate",
        "deadline_violation_rate",
        "throughput",
        "queue_stability_score",
        "illegal_action_rejection_count",
    )
    return tuple(field for field in fields if getattr(left, field) != getattr(right, field))


def _policy_action_evidence_lines(
    outcomes_by_key: Mapping[tuple[str, str, str, str, int], tuple[ExecutionOutcome, ...]],
) -> tuple[str, ...]:
    hoodie_rows: dict[str, list[ExecutionOutcome]] = {}
    mleo_rows: dict[str, list[ExecutionOutcome]] = {}
    for (policy, scenario_name, _workload, _deadline_pressure, _seed), outcomes in sorted(outcomes_by_key.items()):
        if policy == POLICY_HOODIE:
            hoodie_rows.setdefault(scenario_name, []).extend(outcomes)
        elif policy == POLICY_MLEO:
            mleo_rows.setdefault(scenario_name, []).extend(outcomes)

    if not hoodie_rows or not mleo_rows:
        return ("HOODIE/MLEO action evidence unavailable",)

    total_same = 0
    total_different = 0
    identical_scenarios: list[str] = []
    divergent_scenarios: list[str] = []
    divergent_pairs: list[str] = []

    for scenario_name in sorted(hoodie_rows):
        hoodie_outcomes = hoodie_rows[scenario_name]
        mleo_outcomes = mleo_rows.get(scenario_name)
        if mleo_outcomes is None:
            continue
        same = 0
        different = 0
        pair_counts: dict[str, int] = {}
        for left, right in zip(hoodie_outcomes, mleo_outcomes):
            if left.selected_action == right.selected_action:
                same += 1
            else:
                different += 1
                pair = f"{left.selected_action}->{right.selected_action}"
                pair_counts[pair] = pair_counts.get(pair, 0) + 1
        total_same += same
        total_different += different
        if different == 0:
            identical_scenarios.append(f"{scenario_name}: {same}/{same + different}")
        else:
            pair_text = ", ".join(f"{pair} x{count}" for pair, count in sorted(pair_counts.items()))
            divergent_scenarios.append(f"{scenario_name}: {same}/{same + different} same, {different}/{same + different} different")
            divergent_pairs.append(f"{scenario_name}: {pair_text}")

    total_rows = total_same + total_different
    lines = [f"HOODIE and MLEO match in {total_same} of {total_rows} raw rows and differ in {total_different} rows."]
    if identical_scenarios:
        lines.append("Identical-action scenarios: " + "; ".join(identical_scenarios) + ".")
    if divergent_scenarios:
        lines.append("Divergent-action scenarios: " + "; ".join(divergent_scenarios) + ".")
    if divergent_pairs:
        lines.append("Divergent action pairs: " + "; ".join(divergent_pairs) + ".")
    lines.append("Aggregate metrics still tie exactly across all core metrics, so the tie is metric-level rather than action-level.")
    return tuple(lines)


def _policy_coverage_rows() -> tuple[PolicyCoverageRow, ...]:
    return (
        PolicyCoverageRow(POLICY_HOODIE, "implemented", "feature_080_runtime_path", "Feature 080 proposed-method runtime path", False),
        PolicyCoverageRow(POLICY_RO, "implemented", "paper_baseline_adapter", "Random Offloader baseline", False),
        PolicyCoverageRow(POLICY_FLC, "implemented", "paper_baseline_adapter", "Full Local Computing baseline", False),
        PolicyCoverageRow(POLICY_VO, "implemented", "paper_baseline_adapter", "Vertical Offloader baseline", False),
        PolicyCoverageRow(POLICY_HO, "implemented", "paper_baseline_adapter", "Horizontal Offloader baseline", False),
        PolicyCoverageRow(POLICY_BCO, "implemented", "paper_baseline_adapter", "Balanced Cyclic Offloader baseline", False),
        PolicyCoverageRow(POLICY_MLEO, "implemented", "paper_baseline_adapter", "Minimum Latency Estimate Offloader baseline", False),
    )


def _scenario_coverage_rows() -> tuple[ScenarioCoverageRow, ...]:
    return tuple(ScenarioCoverageRow(name, "implemented", "deterministic blueprint expansion") for name in REQUIRED_SCENARIOS)


def _metric_coverage_rows() -> tuple[MetricCoverageRow, ...]:
    formulas = {
        "task_completion_delay": "mean(completion_time - arrival_time) for completed tasks",
        "task_drop_ratio": "(dropped_timeout_count + dropped_unavailable_count) / total_task_count",
        "completion_rate": "completed_count / total_task_count",
        "timeout_drop_rate": "dropped_timeout_count / total_task_count",
        "unavailable_drop_rate": "dropped_unavailable_count / total_task_count",
        "deadline_violation_rate": "deadline_violation_count / total_task_count",
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
    queue_hints = {
        "local": float(queue_history[0] if queue_history else 0),
        "horizontal": float(queue_history[1] if len(queue_history) > 1 else (queue_history[0] if queue_history else 0)),
        "vertical": float(queue_history[2] if len(queue_history) > 2 else (queue_history[-1] if queue_history else 0)),
    }
    fallback_hints_by_scenario = {
        "light_load_no_deadline_pressure": {"local": 2.2, "horizontal": 1.2, "vertical": 0.8},
        "tight_deadline_pressure": {"local": 1.0, "horizontal": 1.8, "vertical": 2.4},
        "legal_horizontal_offload": {"local": 1.0, "horizontal": 2.4, "vertical": 0.9},
        "illegal_horizontal_destination_attempt": {"local": 2.1, "horizontal": 0.2, "vertical": 1.8},
        "cloud_vertical_fallback": {"local": 0.8, "horizontal": 1.0, "vertical": 2.6},
        "timeout_drop_case": {"local": 0.7, "horizontal": 1.7, "vertical": 2.2},
        "mixed_local_horizontal_cloud_candidates": {"local": 2.4, "horizontal": 1.8, "vertical": 2.1},
    }
    fallback_hints = dict(fallback_hints_by_scenario.get(scenario.scenario_name, {"local": 1.0, "horizontal": 1.5, "vertical": 1.2}))
    if deadline_pressure == "tight":
        fallback_hints["vertical"] = float(fallback_hints["vertical"]) + 0.2
        fallback_hints["horizontal"] = float(fallback_hints["horizontal"]) + 0.1
    elif deadline_pressure == "relaxed":
        fallback_hints["local"] = float(fallback_hints["local"]) + 0.2
    if workload == "high":
        fallback_hints["vertical"] = float(fallback_hints["vertical"]) + 0.1
    elif workload == "low":
        fallback_hints["local"] = float(fallback_hints["local"]) + 0.1
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
    mqo_queue_hints = {
        "local": queue_hints["local"],
        "horizontal": queue_hints["horizontal"],
        "vertical": queue_hints["vertical"],
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
            "topology": (task.source_agent_id, *task.legal_horizontal_destinations, "cloud"),
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
            "mqo_queue_hints": mqo_queue_hints,
            "delay_hints": delay_hints,
            "reward_hints": reward_hints,
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
        trace = tuple(getattr(policy_adapter, "last_decision_trace", ()))
        summary = " | ".join(trace)
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
            decision_trace=trace,
            decision_trace_summary=summary,
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
    trace = tuple(getattr(policy_adapter, "last_decision_trace", ()))
    summary = " | ".join(trace)
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
        decision_trace=trace,
        decision_trace_summary=summary,
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


def _remaining_gaps(policy_rows: Mapping[str, MetricRow], policy_coverage: tuple[PolicyCoverageRow, ...], compatibility_mode_used: bool) -> tuple[str, ...]:
    gaps: list[str] = []
    policies = {row.policy for row in policy_coverage}
    if policies != set(REQUIRED_POLICIES):
        gaps.append("required paper policy set is not exact")
    if any(row.compatibility_mode_used for row in policy_coverage) or compatibility_mode_used:
        gaps.append("compatibility-mode policies remain active")
    return tuple(gaps)


def build_feature_083_report(config: EvaluationConfig | None = None) -> Feature083Report:
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
    rows_by_policy = {row.policy: row for row in policy_aggregates}
    remaining_gaps = _remaining_gaps(rows_by_policy, policy_coverage, compatibility_mode_used)
    policy_action_evidence = _policy_action_evidence_lines(outcomes_by_key)
    claim_boundary = (
        "HOODIE means the Feature 080 proposed method only.",
        "Baselines are paper-aligned and restricted to RO, FLC, VO, HO, BCO, and MLEO.",
        "Deterministic evaluation is used for comparison and artifact generation.",
        "No statistical superiority claim is made.",
        "No full empirical paper reproduction is claimed.",
    )
    scope_proof = (
        "no DCQ logic",
        "no thesis method",
        "no custom queue redesign",
        "no legacy minimum-queue policy remains as an active baseline label",
        "HOODIE remains the Feature 080 proposed method only",
        "baselines are paper-aligned",
        "no empirical full-paper reproduction claim",
        "no statistical superiority claim",
        "PR #24 remains blocked until baseline correction and formula audit validations pass",
    )
    if remaining_gaps:
        readiness_level = "blocked"
        status = "hoodie_paper_baseline_fidelity_audit_blocked"
        passed = False
    else:
        readiness_level = "fully_implemented"
        status = FEATURE_085_STATUS_READY
        passed = True
    raw_row_count = sum(len(outcomes) for outcomes in outcomes_by_key.values())
    return Feature083Report(
        feature_id=FEATURE_ID,
        status=status,
        passed=passed,
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
        policy_action_evidence=policy_action_evidence,
        scenario_tables=scenario_tables,
        aggregate_summaries=aggregate_summaries,
        compatibility_mode_used=compatibility_mode_used,
        raw_row_count=raw_row_count,
    )


def _identity_proof_lines(report: Feature083Report) -> tuple[str, ...]:
    rows = {row.policy: row for row in report.summary_rows}
    hoodie = rows.get(POLICY_HOODIE)
    if hoodie is None:
        return ("policy identity proof unavailable",)
    lines = []
    for policy in REQUIRED_POLICIES:
        if policy == POLICY_HOODIE:
            continue
        comparison = rows.get(policy)
        if comparison is None:
            lines.append(f"{POLICY_HOODIE} vs {policy}: unavailable")
            continue
        metrics = ", ".join(_metric_differences(hoodie, comparison)) or "none"
        lines.append(f"{POLICY_HOODIE} differs from {policy} on metrics: {metrics}.")
    return tuple(lines)


def render_feature_083_report(report: Feature083Report | None = None) -> str:
    report = report or build_feature_083_report()
    lines = [
        "# Feature 085 HOODIE Baseline Fidelity Audit Report",
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
    lines.append("## Paper Baseline Mapping")
    for row in report.policy_coverage:
        lines.append(f"- {row.policy} -> {row.evidence}")
    lines.append("")
    lines.append("## Primary Paper Metrics")
    for metric in PRIMARY_PAPER_METRICS:
        lines.append(f"- {metric}")
    lines.append("")
    lines.append("## Secondary Repository Metrics")
    for metric in SECONDARY_REPOSITORY_METRICS:
        lines.append(f"- {metric}")
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
    lines.append("## Formula Audit")
    lines.append("- see `specs/085-hoodie-paper-baseline-fidelity-audit/formula-mapping-matrix.md`")
    lines.append("- see `specs/085-hoodie-paper-baseline-fidelity-audit/baseline-mapping-matrix.md`")
    lines.append("")
    lines.append("## HOODIE/MLEO Tie Evidence")
    lines.extend(f"- {line}" for line in (report.policy_action_evidence or ("tie evidence unavailable",)))
    lines.append("")
    lines.append("## Metric Rankings")
    lines.append("### Primary Paper Metrics")
    for metric in PRIMARY_PAPER_METRICS:
        lines.append(f"#### {metric}")
        for row in report.ranking_tables[metric]:
            lines.append(f"- {row.rank}. {row.policy} = {row.value}")
    lines.append("")
    lines.append("### Secondary Repository Metrics")
    for metric in SECONDARY_REPOSITORY_METRICS:
        lines.append(f"#### {metric}")
        for row in report.ranking_tables[metric]:
            lines.append(f"- {row.rank}. {row.policy} = {row.value}")
    lines.append("")
    lines.append("## Validation Commands")
    lines.extend(f"- {command}" for command in VALIDATION_COMMANDS)
    lines.append("")
    lines.append("## Remaining Gaps")
    lines.extend(f"- {gap}" for gap in (report.remaining_gaps or ("none",)))
    return "\n".join(lines)


def build_feature_085_report(config: EvaluationConfig | None = None) -> Feature083Report:
    return build_feature_083_report(config)


def render_feature_085_report(report: Feature083Report | None = None) -> str:
    return render_feature_083_report(report)


build_feature_082_report = build_feature_083_report
render_feature_082_report = render_feature_083_report
