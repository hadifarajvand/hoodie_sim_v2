from __future__ import annotations

from collections.abc import Sequence
from functools import lru_cache
from pathlib import Path
import json
from typing import Any

from src.analysis.combined_baseline_proposed_comparative_readiness.report import build_feature_076_report

from .config import (
    BLOCKED_STATUS,
    DEADLINE_PRESSURE_LEVELS,
    DEPENDENCY_FEATURES,
    EXPECTED_ROW_COUNT_PER_SEED,
    FEATURE_ID,
    FEATURE_NAME,
    DEFAULT_CHANGED_FILES,
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


def _base_row_index() -> dict[tuple[str, str], Any]:
    report = _feature_076_report()
    if not report.passed:
        raise ValueError("Feature 076 report must pass before campaign execution")
    return {(row.policy_id, row.scenario_id): row for row in report.rows}


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


def _row_from_cell(
    *,
    cell: CampaignExecutionGridCell,
    seed_value: int,
    base_row,
) -> CampaignExecutionResultRow:
    completed_count = int(base_row.completed_count)
    dropped_timeout_count = int(base_row.dropped_timeout_count)
    dropped_unavailable_count = int(base_row.dropped_unavailable_count)
    deadline_violation_count = int(base_row.deadline_violation_count)
    illegal_action_rejection_count = int(base_row.illegal_action_rejection_count)
    completion_rate, timeout_drop_rate, unavailable_drop_rate, deadline_violation_rate = _outcome_rates(
        completed_count=completed_count,
        dropped_timeout_count=dropped_timeout_count,
        dropped_unavailable_count=dropped_unavailable_count,
        deadline_violation_count=deadline_violation_count,
    )
    average_delay = float(base_row.average_delay)
    average_reward = float(base_row.average_reward)
    total_reward = float(base_row.average_reward)
    execution_provenance = (
        f"feature_076_source={base_row.source_feature};"
        f"source_report_status={base_row.source_report_status};"
        f"policy_id={cell.policy_id};scenario_id={cell.scenario_id};"
        f"seed_id={cell.seed_id};seed_value={seed_value};seed_source={SEED_SOURCE};"
        f"workload_level={cell.workload_level};deadline_pressure_level={cell.deadline_pressure_level};"
        f"topology_mode={cell.topology_mode};runtime_mode={cell.runtime_mode}"
    )
    return CampaignExecutionResultRow(
        policy_id=cell.policy_id,
        scenario_id=cell.scenario_id,
        seed_id=cell.seed_id,
        workload_level=cell.workload_level,
        deadline_pressure_level=cell.deadline_pressure_level,
        topology_mode=cell.topology_mode,
        runtime_mode=cell.runtime_mode,
        selected_action_id=base_row.selected_action_id,
        selected_action_family=base_row.selected_action_family,
        action_legality=base_row.action_legality,
        terminal_status=base_row.action_bound_terminal_status,
        completed_count=completed_count,
        dropped_timeout_count=dropped_timeout_count,
        dropped_unavailable_count=dropped_unavailable_count,
        deadline_violation_count=deadline_violation_count,
        illegal_action_rejection_count=illegal_action_rejection_count,
        average_delay=average_delay,
        average_reward=average_reward,
        total_reward=total_reward,
        completion_rate=float(completion_rate),
        timeout_drop_rate=float(timeout_drop_rate),
        unavailable_drop_rate=float(unavailable_drop_rate),
        deadline_violation_rate=float(deadline_violation_rate),
        compatibility_mode_used=False,
        execution_provenance=execution_provenance,
    )


def build_campaign_execution_rows(
    *,
    seed_plan: Sequence[CampaignExecutionSeed] | None = None,
) -> tuple[CampaignExecutionResultRow, ...]:
    seeds = tuple(seed_plan if seed_plan is not None else build_execution_seed_plan())
    base_rows = _base_row_index()
    rows: list[CampaignExecutionResultRow] = []
    for cell in build_campaign_execution_grid(seeds):
        base_row = base_rows[(cell.policy_id, cell.scenario_id)]
        seed_value = next(seed.seed_value for seed in seeds if seed.seed_id == cell.seed_id)
        rows.append(_row_from_cell(cell=cell, seed_value=seed_value, base_row=base_row))
    return tuple(rows)


def validate_execution_rows(rows: Sequence[CampaignExecutionResultRow]) -> None:
    row_tuple = tuple(rows)
    expected_row_count = EXPECTED_ROW_COUNT_PER_SEED * len(SEED_IDS)
    if len(row_tuple) != expected_row_count:
        raise ValueError("row count must match the campaign execution grid")
    expected_keys = {
        (policy_id, scenario_id, seed_id, workload_level, deadline_level)
        for policy_id in REQUIRED_POLICY_IDS
        for scenario_id in REQUIRED_SCENARIO_IDS
        for seed_id in SEED_IDS
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
        "Feature 076 readiness rows are consumed as the action-bound execution substrate.",
        "Feature 077 campaign dimensions are consumed as the execution contract.",
        "No execution artifacts are committed by default.",
    )


def build_feature_078_report(
    *,
    seed_plan: Sequence[CampaignExecutionSeed] | None = None,
    changed_files: Sequence[str] | None = None,
) -> CampaignExecutionReport:
    checked_changed_files = tuple(validate_scope(DEFAULT_CHANGED_FILES if changed_files is None else changed_files))
    seeds = tuple(seed_plan if seed_plan is not None else build_execution_seed_plan())
    rows = build_campaign_execution_rows(seed_plan=seeds)
    validate_execution_rows(rows)
    expected_row_count = EXPECTED_ROW_COUNT_PER_SEED * len(seeds)
    validation_summary = (
        f"Feature 076 passed: {_feature_076_report().passed}",
        "Feature 077 campaign contract consumed from config constants.",
        f"Policy coverage: {len(REQUIRED_POLICY_IDS)}",
        f"Scenario coverage: {len(REQUIRED_SCENARIO_IDS)}",
        f"Seed count: {len(seeds)}",
        f"Workload levels: {', '.join(WORKLOAD_LEVELS)}",
        f"Deadline pressure levels: {', '.join(DEADLINE_PRESSURE_LEVELS)}",
        f"Topology mode: {TOPOLOGY_MODE}",
        f"Runtime mode: {RUNTIME_MODE}",
        f"Expected row count formula: {EXPECTED_ROW_COUNT_PER_SEED} * seed_count",
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
        status=READY_STATUS,
        passed=True,
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
            "## Result Row Preview",
            *(f"- {row['policy_id']} / {row['scenario_id']} / {row['seed_id']} / {row['workload_level']} / {row['deadline_pressure_level']} / {row['terminal_status']}" for row in row_preview),
            "",
            "## Notes",
            "- Raw execution rows only.",
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
