from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import replace
from functools import lru_cache
from pathlib import Path
import json
from typing import Any
from types import SimpleNamespace

from src.analysis.baseline_policy_comparative_evaluation_readiness.report import (
    build_action_bound_outcome,
    _scenario_context as baseline_runtime_scenario_context,
)
from src.analysis.combined_baseline_proposed_comparative_readiness.report import build_feature_076_report
from src.analysis.proposed_method_integration_readiness.report import (
    PROPOSED_METHOD_POLICY_FAMILY,
    PROPOSED_METHOD_POLICY_ID,
    ScenarioReadinessProfile,
    _build_candidate as proposed_build_candidate,
    _candidate_context as proposed_candidate_context,
    _candidate_legal as proposed_candidate_legal,
    _candidate_ranking_trace as proposed_candidate_ranking_trace,
    _queue_or_load_value as proposed_queue_or_load_value,
    _reward_risk_value as proposed_reward_risk_value,
    _scenario_profile as proposed_scenario_profile,
    _selected_action_family as proposed_selected_action_family,
)
from src.evaluation.policy_registry import PolicyRegistry
from src.policies import PolicyContext, RandomOffloadingPolicy
from src.policies.common import action_family as runtime_action_family

from .config import (
    BLOCKED_STATUS,
    DEADLINE_PRESSURE_LEVELS,
    DEPENDENCY_FEATURES,
    DEFAULT_CHANGED_FILES,
    EXPECTED_ROW_COUNT_PER_SEED,
    FEATURE_ID,
    FEATURE_NAME,
    READY_STATUS,
    REQUIRED_POLICY_IDS,
    REQUIRED_SCENARIO_IDS,
    RUNTIME_MODE,
    SEED_IDS,
    SEED_SOURCE,
    SEED_VALUES,
    TOPOLOGY_MODE,
    WORKLOAD_LEVELS,
    validate_scope,
)
from .model import (
    CampaignExecutionGridCell,
    CampaignExecutionReport,
    CampaignExecutionResultRow,
    CampaignExecutionSeed,
)


_WORKLOAD_FACTORS: dict[str, float] = {
    "low": 0.85,
    "medium": 1.0,
    "high": 1.15,
}
_DEADLINE_FACTORS: dict[str, float] = {
    "relaxed": 0.85,
    "moderate": 1.0,
    "tight": 1.15,
}
_BASELINE_POLICY_IDS = tuple(policy_id for policy_id in REQUIRED_POLICY_IDS if policy_id != PROPOSED_METHOD_POLICY_ID)
_BASELINE_RUNTIME_PATH = "feature_074._scenario_context -> policy.choose_action -> build_action_bound_outcome"
_PROPOSED_RUNTIME_PATH = "feature_075._candidate_context -> candidate_ranking -> build_action_bound_outcome"
_BASELINE_SCENARIO_SOURCE = "feature_074.runtime_scenario_context"
_PROPOSED_SCENARIO_SOURCE = "feature_075.runtime_candidate_context"


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


@lru_cache(maxsize=1)
def _feature_076_report():
    return build_feature_076_report()


def build_execution_seed_plan() -> tuple[CampaignExecutionSeed, ...]:
    return tuple(
        CampaignExecutionSeed(seed_id=seed_id, seed_value=seed_value, source=SEED_SOURCE)
        for seed_id, seed_value in zip(SEED_IDS, SEED_VALUES, strict=True)
    )


def build_campaign_execution_grid(
    seed_plan: Sequence[CampaignExecutionSeed] | None = None,
) -> tuple[CampaignExecutionGridCell, ...]:
    seeds = tuple(seed_plan if seed_plan is not None else build_execution_seed_plan())
    grid: list[CampaignExecutionGridCell] = []
    for policy_id in REQUIRED_POLICY_IDS:
        for scenario_id in REQUIRED_SCENARIO_IDS:
            for seed in seeds:
                for workload_level in WORKLOAD_LEVELS:
                    for deadline_pressure_level in DEADLINE_PRESSURE_LEVELS:
                        grid.append(
                            CampaignExecutionGridCell(
                                policy_id=policy_id,
                                scenario_id=scenario_id,
                                seed_id=seed.seed_id,
                                workload_level=workload_level,
                                deadline_pressure_level=deadline_pressure_level,
                                topology_mode=TOPOLOGY_MODE,
                                runtime_mode=RUNTIME_MODE,
                            )
                        )
    return tuple(grid)


def _workload_factor(workload_level: str) -> float:
    return _WORKLOAD_FACTORS[workload_level]


def _deadline_factor(deadline_pressure_level: str) -> float:
    return _DEADLINE_FACTORS[deadline_pressure_level]


def _workload_modifier_state(workload_level: str) -> str:
    factor = _workload_factor(workload_level)
    return f"workload_level={workload_level};factor={factor:.2f};mode=paper"


def _deadline_modifier_state(deadline_pressure_level: str) -> str:
    factor = _deadline_factor(deadline_pressure_level)
    return f"deadline_pressure_level={deadline_pressure_level};factor={factor:.2f};mode=paper"


def _policy_source(policy_id: str, seed_value: int) -> str:
    if policy_id == PROPOSED_METHOD_POLICY_ID:
        return "Feature 075 HOODIE_PROPOSED runtime decision path"
    if policy_id == "RO":
        return f"RandomOffloadingPolicy(seed={seed_value})"
    return f"PolicyRegistry.resolve({policy_id})"


def _scenario_source(policy_id: str) -> str:
    return _PROPOSED_SCENARIO_SOURCE if policy_id == PROPOSED_METHOD_POLICY_ID else _BASELINE_SCENARIO_SOURCE


def _execution_runtime_path(policy_id: str) -> str:
    return _PROPOSED_RUNTIME_PATH if policy_id == PROPOSED_METHOD_POLICY_ID else _BASELINE_RUNTIME_PATH


def _scale_numeric_mapping(mapping: Mapping[str, object], factor: float) -> dict[str, float]:
    return {
        key: float(value) * factor
        for key, value in mapping.items()
        if isinstance(value, (int, float)) and not isinstance(value, bool)
    }


def _scale_mleo_candidates(
    value: object,
    workload_factor: float,
    deadline_factor: float,
) -> object:
    if isinstance(value, Mapping):
        scaled: dict[str, dict[str, object]] = {}
        for key, payload in value.items():
            if not isinstance(payload, Mapping):
                continue
            candidate = dict(payload)
            family = str(candidate.get("action_family") or key)
            factor = {
                "local": workload_factor,
                "horizontal": (workload_factor + deadline_factor) / 2.0,
                "vertical": deadline_factor,
            }.get(family, 1.0)
            if "total_delay" in candidate and isinstance(candidate["total_delay"], (int, float)):
                candidate["total_delay"] = float(candidate["total_delay"]) * factor
            scaled[str(key)] = candidate
        return scaled
    if isinstance(value, list):
        scaled_list: list[dict[str, object]] = []
        for payload in value:
            if not isinstance(payload, Mapping):
                continue
            candidate = dict(payload)
            family = str(candidate.get("action_family") or candidate.get("family") or candidate.get("placement_kind") or candidate.get("action_id") or "")
            factor = {
                "local": workload_factor,
                "horizontal": (workload_factor + deadline_factor) / 2.0,
                "vertical": deadline_factor,
            }.get(family, 1.0)
            if "total_delay" in candidate and isinstance(candidate["total_delay"], (int, float)):
                candidate["total_delay"] = float(candidate["total_delay"]) * factor
            scaled_list.append(candidate)
        return scaled_list
    return value


def _decorate_context(
    context: PolicyContext,
    *,
    policy_id: str,
    scenario_id: str,
    seed_id: str,
    seed_value: int,
    workload_level: str,
    deadline_pressure_level: str,
) -> PolicyContext:
    workload_factor = _workload_factor(workload_level)
    deadline_factor = _deadline_factor(deadline_pressure_level)
    observation = dict(context.observation)
    observation.update(
        {
            "campaign_feature_id": FEATURE_ID,
            "campaign_feature_name": FEATURE_NAME,
            "campaign_seed_id": seed_id,
            "campaign_seed_value": seed_value,
            "campaign_seed_source": SEED_SOURCE,
            "policy_id": policy_id,
            "scenario_id": scenario_id,
            "workload_level": workload_level,
            "deadline_pressure_level": deadline_pressure_level,
            "workload_modifier_state": _workload_modifier_state(workload_level),
            "deadline_modifier_state": _deadline_modifier_state(deadline_pressure_level),
            "execution_runtime_path_used": _execution_runtime_path(policy_id),
            "scenario_source": _scenario_source(policy_id),
            "policy_source": _policy_source(policy_id, seed_value),
        }
    )
    if isinstance(observation.get("queue_load_evidence"), Mapping):
        observation["queue_load_evidence"] = _scale_numeric_mapping(observation["queue_load_evidence"], workload_factor)
    if isinstance(observation.get("reward_risk_evidence"), Mapping):
        observation["reward_risk_evidence"] = _scale_numeric_mapping(observation["reward_risk_evidence"], deadline_factor)
    if isinstance(observation.get("deadline_slack_evidence"), Mapping):
        observation["deadline_slack_evidence"] = _scale_numeric_mapping(observation["deadline_slack_evidence"], deadline_factor)
    if isinstance(observation.get("balance_hint"), Mapping):
        balance_hint = dict(observation["balance_hint"])
        balance_hint["local"] = float(balance_hint.get("local", 0.0)) * workload_factor
        balance_hint["horizontal"] = float(balance_hint.get("horizontal", 0.0)) * ((workload_factor + deadline_factor) / 2.0)
        balance_hint["vertical"] = float(balance_hint.get("vertical", 0.0)) * deadline_factor
        observation["balance_hint"] = balance_hint
    if "mleo_delay_candidates" in observation:
        observation["mleo_delay_candidates"] = _scale_mleo_candidates(
            observation["mleo_delay_candidates"],
            workload_factor,
            deadline_factor,
        )
    if "mleo_placement_candidates" in observation:
        observation["mleo_placement_candidates"] = _scale_mleo_candidates(
            observation["mleo_placement_candidates"],
            workload_factor,
            deadline_factor,
        )
    if "placement_actions" in observation and isinstance(observation["placement_actions"], Mapping):
        observation["placement_actions"] = {
            key: value
            for key, value in observation["placement_actions"].items()
        }
    trace_history = tuple(context.trace_history) + (
        f"campaign_feature_id={FEATURE_ID}",
        f"policy_id={policy_id}",
        f"scenario_id={scenario_id}",
        f"seed_id={seed_id}",
        f"workload_level={workload_level}",
        f"deadline_pressure_level={deadline_pressure_level}",
    )
    return PolicyContext(observation=observation, legal_action_mask=dict(context.legal_action_mask), trace_history=trace_history)


def _resolve_policy(policy_id: str, seed_value: int):
    if policy_id == "RO":
        return RandomOffloadingPolicy(seed=seed_value)
    return PolicyRegistry.resolve(policy_id)


def _baseline_context(
    *,
    policy_id: str,
    scenario_id: str,
    seed_id: str,
    seed_value: int,
    workload_level: str,
    deadline_pressure_level: str,
) -> PolicyContext:
    context = baseline_runtime_scenario_context(policy_id, scenario_id)
    return _decorate_context(
        context,
        policy_id=policy_id,
        scenario_id=scenario_id,
        seed_id=seed_id,
        seed_value=seed_value,
        workload_level=workload_level,
        deadline_pressure_level=deadline_pressure_level,
    )


def _proposed_context(
    *,
    scenario_id: str,
    seed_id: str,
    seed_value: int,
    workload_level: str,
    deadline_pressure_level: str,
) -> tuple[ScenarioReadinessProfile, PolicyContext]:
    profile = proposed_scenario_profile(scenario_id)
    context = proposed_candidate_context(profile)
    decorated = _decorate_context(
        context,
        policy_id=PROPOSED_METHOD_POLICY_ID,
        scenario_id=scenario_id,
        seed_id=seed_id,
        seed_value=seed_value,
        workload_level=workload_level,
        deadline_pressure_level=deadline_pressure_level,
    )
    return profile, decorated


def _outcome_rates(
    *,
    completed_count: int,
    dropped_timeout_count: int,
    dropped_unavailable_count: int,
    deadline_violation_count: int,
) -> tuple[float, float, float, float]:
    denominator = completed_count + dropped_timeout_count + dropped_unavailable_count
    if denominator <= 0:
        denominator = 1
    return (
        completed_count / denominator,
        dropped_timeout_count / denominator,
        dropped_unavailable_count / denominator,
        deadline_violation_count / denominator,
    )


def _row_from_outcome(
    *,
    cell: CampaignExecutionGridCell,
    seed_value: int,
    outcome,
    runtime_path_used: str,
    scenario_source: str,
    policy_source: str,
    workload_modifier_state: str,
    deadline_modifier_state: str,
) -> CampaignExecutionResultRow:
    completed_count = int(outcome.metrics.completed_count)
    dropped_timeout_count = int(outcome.metrics.dropped_timeout_count)
    dropped_unavailable_count = int(outcome.metrics.dropped_unavailable_count)
    deadline_violation_count = int(outcome.metrics.deadline_violation_count)
    illegal_action_rejection_count = int(outcome.metrics.illegal_action_rejection_count)
    completion_rate, timeout_drop_rate, unavailable_drop_rate, deadline_violation_rate = _outcome_rates(
        completed_count=completed_count,
        dropped_timeout_count=dropped_timeout_count,
        dropped_unavailable_count=dropped_unavailable_count,
        deadline_violation_count=deadline_violation_count,
    )
    selected_action_family = outcome.selected_action_family
    if selected_action_family not in {"local", "horizontal", "vertical"}:
        raise ValueError("campaign execution rows must bind a mapped selected action")
    reward_value = float(outcome.reward_value if outcome.reward_value is not None else 0.0)
    delay_value = float(outcome.delay if outcome.delay is not None else 0.0)
    execution_provenance = (
        f"runtime_path={runtime_path_used};"
        f"scenario_source={scenario_source};"
        f"policy_source={policy_source};"
        f"workload_modifier_state={workload_modifier_state};"
        f"deadline_modifier_state={deadline_modifier_state};"
        f"seed_id={cell.seed_id};seed_value={seed_value};seed_source={SEED_SOURCE};"
        f"selected_action_id={outcome.selected_action_id};"
        f"selected_action_family={selected_action_family};"
        f"action_legality={outcome.action_legality};"
        f"terminal_status={outcome.terminal_status};"
        f"evidence_source={outcome.evidence_source}"
    )
    return CampaignExecutionResultRow(
        policy_id=cell.policy_id,
        scenario_id=cell.scenario_id,
        seed_id=cell.seed_id,
        workload_level=cell.workload_level,
        deadline_pressure_level=cell.deadline_pressure_level,
        topology_mode=cell.topology_mode,
        runtime_mode=cell.runtime_mode,
        selected_action_id=outcome.selected_action_id,
        selected_action_family=selected_action_family,
        action_legality=outcome.action_legality,
        terminal_status=outcome.terminal_status,
        completed_count=completed_count,
        dropped_timeout_count=dropped_timeout_count,
        dropped_unavailable_count=dropped_unavailable_count,
        deadline_violation_count=deadline_violation_count,
        illegal_action_rejection_count=illegal_action_rejection_count,
        average_delay=delay_value,
        average_reward=reward_value,
        total_reward=reward_value,
        completion_rate=float(completion_rate),
        timeout_drop_rate=float(timeout_drop_rate),
        unavailable_drop_rate=float(unavailable_drop_rate),
        deadline_violation_rate=float(deadline_violation_rate),
        compatibility_mode_used=False,
        execution_runtime_path_used=runtime_path_used,
        scenario_source=scenario_source,
        policy_source=policy_source,
        workload_modifier_state=workload_modifier_state,
        deadline_modifier_state=deadline_modifier_state,
        execution_provenance=execution_provenance,
    )


def _execute_baseline_cell(
    *,
    cell: CampaignExecutionGridCell,
    seed_value: int,
) -> CampaignExecutionResultRow:
    context = _baseline_context(
        policy_id=cell.policy_id,
        scenario_id=cell.scenario_id,
        seed_id=cell.seed_id,
        seed_value=seed_value,
        workload_level=cell.workload_level,
        deadline_pressure_level=cell.deadline_pressure_level,
    )
    policy = _resolve_policy(cell.policy_id, seed_value)
    selected_action = policy.choose_action(context)
    outcome = build_action_bound_outcome(cell.policy_id, cell.scenario_id, selected_action, context)
    return _row_from_outcome(
        cell=cell,
        seed_value=seed_value,
        outcome=outcome,
        runtime_path_used=_execution_runtime_path(cell.policy_id),
        scenario_source=_scenario_source(cell.policy_id),
        policy_source=_policy_source(cell.policy_id, seed_value),
        workload_modifier_state=_workload_modifier_state(cell.workload_level),
        deadline_modifier_state=_deadline_modifier_state(cell.deadline_pressure_level),
    )


def _execute_proposed_cell(
    *,
    cell: CampaignExecutionGridCell,
    seed_value: int,
) -> CampaignExecutionResultRow:
    profile, context = _proposed_context(
        scenario_id=cell.scenario_id,
        seed_id=cell.seed_id,
        seed_value=seed_value,
        workload_level=cell.workload_level,
        deadline_pressure_level=cell.deadline_pressure_level,
    )
    candidate_specs = (
        ("local", "local"),
        ("cloud", "vertical"),
        (profile.legal_horizontal_destination, "horizontal"),
        (profile.illegal_horizontal_destination, "horizontal"),
    )
    candidates = tuple(
        proposed_build_candidate(
            scenario_id=profile.scenario_id,
            action_id=action_id,
            family=family,
            legal=proposed_candidate_legal(family=family, action_id=action_id, profile=profile, context=context),
            profile=profile,
            context=context,
            selected=False,
        )
        for action_id, family in candidate_specs
    )
    selected_candidate = proposed_selected_action_family(profile, candidates)
    selected_candidate = replace(selected_candidate, selected=True)
    _ = proposed_candidate_ranking_trace(candidates, selected_candidate.action_id)
    _ = runtime_action_family(selected_candidate.action_id)
    outcome = build_action_bound_outcome(PROPOSED_METHOD_POLICY_ID, cell.scenario_id, selected_candidate.action_id, context)
    return _row_from_outcome(
        cell=cell,
        seed_value=seed_value,
        outcome=outcome,
        runtime_path_used=_execution_runtime_path(cell.policy_id),
        scenario_source=_scenario_source(cell.policy_id),
        policy_source=_policy_source(cell.policy_id, seed_value),
        workload_modifier_state=_workload_modifier_state(cell.workload_level),
        deadline_modifier_state=_deadline_modifier_state(cell.deadline_pressure_level),
    )


def build_campaign_execution_rows(
    *,
    seed_plan: Sequence[CampaignExecutionSeed] | None = None,
) -> tuple[CampaignExecutionResultRow, ...]:
    seeds = tuple(seed_plan if seed_plan is not None else build_execution_seed_plan())
    seed_values = {seed.seed_id: seed.seed_value for seed in seeds}
    rows: list[CampaignExecutionResultRow] = []
    for cell in build_campaign_execution_grid(seeds):
        seed_value = seed_values[cell.seed_id]
        if cell.policy_id == PROPOSED_METHOD_POLICY_ID:
            rows.append(_execute_proposed_cell(cell=cell, seed_value=seed_value))
        else:
            rows.append(_execute_baseline_cell(cell=cell, seed_value=seed_value))
    return tuple(rows)


def validate_execution_rows(rows: Sequence[CampaignExecutionResultRow], *, seed_count: int | None = None) -> None:
    row_tuple = tuple(rows)
    if seed_count is None:
        seed_count = len({row.seed_id for row in row_tuple})
    if seed_count <= 0:
        raise ValueError("seed_count must be positive")
    expected_row_count = EXPECTED_ROW_COUNT_PER_SEED * seed_count
    if len(row_tuple) != expected_row_count:
        raise ValueError("row count must match the campaign execution grid")
    expected_keys = {
        (policy_id, scenario_id, seed_id, workload_level, deadline_level)
        for policy_id in REQUIRED_POLICY_IDS
        for scenario_id in REQUIRED_SCENARIO_IDS
        for seed_id in SEED_IDS[:seed_count]
        for workload_level in WORKLOAD_LEVELS
        for deadline_level in DEADLINE_PRESSURE_LEVELS
    }
    actual_keys = {
        (row.policy_id, row.scenario_id, row.seed_id, row.workload_level, row.deadline_pressure_level)
        for row in row_tuple
    }
    if actual_keys != expected_keys:
        raise ValueError("rows must cover the complete execution grid exactly once")
    if any(row.compatibility_mode_used for row in row_tuple):
        raise ValueError("compatibility mode must be false for every execution row")
    if any(not row.selected_action_id for row in row_tuple):
        raise ValueError("every execution row must record a selected action")
    if any(row.action_legality == "unmapped" for row in row_tuple):
        raise ValueError("execution rows must be bound to mapped selected actions")
    if any(
        not row.execution_runtime_path_used
        or not row.scenario_source
        or not row.policy_source
        or not row.workload_modifier_state
        or not row.deadline_modifier_state
        or not row.execution_provenance
        for row in row_tuple
    ):
        raise ValueError("every execution row must carry runtime provenance evidence")
    if any(row.total_reward != row.average_reward for row in row_tuple):
        raise ValueError("total_reward must match average_reward for single-row execution cells")


def _claim_boundary() -> tuple[str, ...]:
    return (
        "No training claim is made.",
        "No superiority claim is made.",
        "No final evaluation claim is made.",
        "No statistical significance claim is made.",
        "No full paper reproduction claim is made.",
        "No statistical summary claim is made.",
        "No ranking claim is made.",
        "No winner claim is made.",
        "Feature 076 readiness rows are consumed only as dependency validation and compatibility proof.",
        "Feature 077 campaign dimensions are consumed as the execution contract.",
        "Runtime-backed policy or proposed-method execution is used for every campaign cell.",
        "No execution artifacts are committed by default.",
    )


def build_feature_078_report(
    *,
    seed_plan: Sequence[CampaignExecutionSeed] | None = None,
    changed_files: Sequence[str] | None = None,
) -> CampaignExecutionReport:
    checked_changed_files = tuple(validate_scope(DEFAULT_CHANGED_FILES if changed_files is None else changed_files))
    try:
        feature_076_report = _feature_076_report()
    except ValueError:
        feature_076_report = SimpleNamespace(passed=False)
    seeds = tuple(seed_plan if seed_plan is not None else build_execution_seed_plan())
    rows = build_campaign_execution_rows(seed_plan=seeds)
    validate_execution_rows(rows, seed_count=len(seeds))
    expected_row_count = EXPECTED_ROW_COUNT_PER_SEED * len(seeds)
    passed = bool(
        feature_076_report.passed
        and len(rows) == expected_row_count
        and all(not row.compatibility_mode_used for row in rows)
        and all(row.selected_action_id for row in rows)
        and all(row.action_legality != "unmapped" for row in rows)
        and all(row.execution_runtime_path_used for row in rows)
        and all(row.execution_provenance for row in rows)
    )
    status = READY_STATUS if passed else BLOCKED_STATUS
    validation_summary = (
        f"Feature 076 passed: {feature_076_report.passed}",
        "Feature 076 rows are used only for dependency validation and compatibility proof.",
        "Feature 077 campaign contract consumed from config constants.",
        "Runtime-backed execution path is used for every campaign cell.",
        f"Policy coverage: {len(REQUIRED_POLICY_IDS)}",
        f"Scenario coverage: {len(REQUIRED_SCENARIO_IDS)}",
        f"Seed count: {len(seeds)}",
        f"Workload levels: {', '.join(WORKLOAD_LEVELS)}",
        f"Deadline pressure levels: {', '.join(DEADLINE_PRESSURE_LEVELS)}",
        f"Topology mode: {TOPOLOGY_MODE}",
        f"Runtime mode: {RUNTIME_MODE}",
        f"Expected row count formula: {EXPECTED_ROW_COUNT_PER_SEED} * seed_count",
        "Runtime provenance fields are recorded for every execution row.",
        "No statistical summaries generated.",
        "No ranking generated.",
        "No winner declared.",
        "Compatibility mode remains false.",
    )
    scope_evidence = (
        "Allowed scope: src/analysis/campaign_execution_engine/**",
        "Allowed scope: tests/unit/test_campaign_execution_engine_*.py",
        "Allowed scope: tests/integration/test_campaign_execution_engine_*.py",
        "Forbidden scope: specs/**",
        "Forbidden scope: src/environment/**",
        "Forbidden scope: src/policies/**",
        "Forbidden scope: src/training/**",
        "Forbidden scope: src/agents/**",
        "Forbidden scope: artifacts/**",
        "Forbidden scope: resources/**",
    )
    report = CampaignExecutionReport(
        feature_id=FEATURE_ID,
        status=status,
        passed=passed,
        dependency_features=DEPENDENCY_FEATURES,
        seed_count=len(seeds),
        expected_row_count=expected_row_count,
        actual_row_count=len(rows),
        result_rows=rows,
        scope_evidence=scope_evidence,
        validation_summary=validation_summary,
        claim_boundary=_claim_boundary(),
    )
    return report


def render_feature_078_report(report: CampaignExecutionReport) -> str:
    payload = report.to_dict()
    row_preview = payload["result_rows"][:12]
    return "\n".join(
        [
            "# Feature 078 Campaign Execution Engine Report",
            "",
            f"- feature_id: `{payload['feature_id']}`",
            f"- status: `{payload['status']}`",
            f"- passed: `{payload['passed']}`",
            f"- dependency_features: {', '.join(payload['dependency_features'])}",
            f"- seed_count: `{payload['seed_count']}`",
            f"- expected_row_count: `{payload['expected_row_count']}`",
            f"- actual_row_count: `{payload['actual_row_count']}`",
            "",
            "## Campaign Dimensions",
            f"- policies: {', '.join(REQUIRED_POLICY_IDS)}",
            f"- scenarios: {', '.join(REQUIRED_SCENARIO_IDS)}",
            f"- workloads: {', '.join(WORKLOAD_LEVELS)}",
            f"- deadline pressures: {', '.join(DEADLINE_PRESSURE_LEVELS)}",
            f"- topology: {TOPOLOGY_MODE}",
            f"- runtime: {RUNTIME_MODE}",
            "",
            "## Scope Evidence",
            *[f"- {entry}" for entry in payload["scope_evidence"]],
            "",
            "## Validation Summary",
            *[f"- {entry}" for entry in payload["validation_summary"]],
            "",
            "## Claim Boundary",
            *[f"- {entry}" for entry in payload["claim_boundary"]],
            "",
            "## Execution Provenance Preview",
            *(
                f"- {row['policy_id']} / {row['scenario_id']} / {row['seed_id']} / {row['workload_level']} / {row['deadline_pressure_level']} "
                f"-> action={row['selected_action_id']} family={row['selected_action_family']} terminal={row['terminal_status']} "
                f"runtime_path={row['execution_runtime_path_used']} scenario_source={row['scenario_source']} "
                f"policy_source={row['policy_source']} workload={row['workload_modifier_state']} "
                f"deadline={row['deadline_modifier_state']}"
                for row in row_preview
            ),
            "",
            "## Notes",
            "- Raw execution rows are produced by runtime-backed policy or proposed-method execution.",
            "- No statistical summaries generated.",
            "- No ranking or winner declared.",
            "- No superiority, final evaluation, statistical significance, or full reproduction claim is made.",
        ]
    )


def write_feature_078_report(output_dir: str | Path, report: CampaignExecutionReport | None = None) -> Path:
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    output_path = target_dir / "campaign_execution_engine_report.md"
    output_path.write_text(render_feature_078_report(report or build_feature_078_report()), encoding="utf-8")
    return output_path
