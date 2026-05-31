from __future__ import annotations

from collections.abc import Sequence
from functools import lru_cache
from pathlib import Path
import json
from typing import Any

from src.analysis.baseline_policy_comparative_evaluation_readiness.report import build_feature_074_report
from src.analysis.proposed_method_integration_readiness.report import build_feature_075_report

from .config import DEFAULT_CHANGED_FILES, DEFAULT_OUTPUT_DIR, VALIDATION_COMMANDS, validate_scope
from .model import (
    CombinedComparativeReadinessReport,
    CombinedPolicyAggregate,
    CombinedPolicyRow,
    CombinedRegressionEvidence,
    REQUIRED_POLICY_IDS,
    REQUIRED_SCENARIO_IDS,
    aggregate_combined_rows,
)


FEATURE_076_STATUS_READY = "combined_baseline_proposed_comparative_readiness_ready"
FEATURE_076_STATUS_WITH_BLOCKERS = "combined_baseline_proposed_comparative_readiness_with_blockers"
FEATURE_076_RECOMMENDATION = "Feature 077 should only follow after combined comparative readiness is complete."


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


@lru_cache(maxsize=1)
def _feature_074_report():
    return build_feature_074_report()


@lru_cache(maxsize=1)
def _feature_075_report():
    return build_feature_075_report()


def normalize_feature_074_rows(feature_074_report) -> tuple[CombinedPolicyRow, ...]:
    rows: list[CombinedPolicyRow] = []
    for comparison in feature_074_report.scenario_comparisons:
        rows.append(
            CombinedPolicyRow(
                policy_id=comparison.policy_id,
                policy_family=comparison.policy_action_family,
                scenario_id=comparison.scenario_id,
                selected_action_id=comparison.selected_action_id,
                selected_action_family=comparison.selected_action_family,
                action_legality=comparison.action_legality,
                action_bound_terminal_status=comparison.action_bound_terminal_status,
                action_bound_reward_value=comparison.action_bound_reward_value,
                action_bound_metrics_derived=comparison.action_bound_metrics_derived,
                compatibility_mode_used=comparison.compatibility_mode_used,
                decision_trace_present=comparison.policy_decision_trace_present,
                completed_count=comparison.metrics.completed_count,
                dropped_timeout_count=comparison.metrics.dropped_timeout_count,
                dropped_unavailable_count=comparison.metrics.dropped_unavailable_count,
                deadline_violation_count=comparison.metrics.deadline_violation_count,
                illegal_action_rejection_count=comparison.metrics.illegal_action_rejection_count,
                average_delay=comparison.metrics.average_delay,
                average_reward=comparison.metrics.average_reward,
                source_feature="074",
                source_report_status=feature_074_report.status,
            )
        )
    return tuple(rows)


def normalize_feature_075_rows(feature_075_report) -> tuple[CombinedPolicyRow, ...]:
    rows: list[CombinedPolicyRow] = []
    for evaluation in feature_075_report.scenario_evaluations:
        rows.append(
            CombinedPolicyRow(
                policy_id=feature_075_report.proposed_method_descriptor.policy_id,
                policy_family=feature_075_report.proposed_method_descriptor.policy_family,
                scenario_id=evaluation.scenario_id,
                selected_action_id=evaluation.selected_action_id,
                selected_action_family=evaluation.selected_action_family,
                action_legality=evaluation.action_legality,
                action_bound_terminal_status=evaluation.action_bound_terminal_status,
                action_bound_reward_value=evaluation.action_bound_reward_value,
                action_bound_metrics_derived=evaluation.action_bound_metrics_derived,
                compatibility_mode_used=evaluation.compatibility_mode_used,
                decision_trace_present=evaluation.candidate_ranking_trace_present,
                completed_count=evaluation.metrics.completed_count,
                dropped_timeout_count=evaluation.metrics.dropped_timeout_count,
                dropped_unavailable_count=evaluation.metrics.dropped_unavailable_count,
                deadline_violation_count=evaluation.metrics.deadline_violation_count,
                illegal_action_rejection_count=evaluation.metrics.illegal_action_rejection_count,
                average_delay=evaluation.metrics.average_delay,
                average_reward=evaluation.metrics.average_reward,
                source_feature="075",
                source_report_status=feature_075_report.status,
            )
        )
    return tuple(rows)


def build_combined_rows() -> tuple[CombinedPolicyRow, ...]:
    feature_074_report = _feature_074_report()
    feature_075_report = _feature_075_report()
    if not feature_074_report.passed:
        raise ValueError("Feature 074 report must be passed before combined readiness can be built")
    if not feature_075_report.passed:
        raise ValueError("Feature 075 report must be passed before combined readiness can be built")
    baseline_rows = normalize_feature_074_rows(feature_074_report)
    proposed_rows = normalize_feature_075_rows(feature_075_report)
    rows = baseline_rows + proposed_rows
    validate_combined_matrix(rows)
    return rows


def build_combined_aggregates(rows: Sequence[CombinedPolicyRow]) -> tuple[CombinedPolicyAggregate, ...]:
    row_tuple = tuple(rows)
    aggregates = tuple(
        aggregate_combined_rows(tuple(row for row in row_tuple if row.policy_id == policy_id))
        for policy_id in REQUIRED_POLICY_IDS
    )
    return aggregates


def build_regression_evidence() -> tuple[CombinedRegressionEvidence, ...]:
    feature_074_report = _feature_074_report()
    feature_075_report = _feature_075_report()
    evidence_map = (
        ("068R", feature_074_report.feature_068r_regression_status, feature_074_report.status, "Feature 074 regression slice"),
        ("069", feature_074_report.feature_069_regression_status, feature_074_report.status, "Feature 074 regression slice"),
        ("070", feature_074_report.feature_070_regression_status, feature_074_report.status, "Feature 074 regression slice"),
        ("071", feature_074_report.feature_071_regression_status, feature_074_report.status, "Feature 074 regression slice"),
        ("072", feature_074_report.feature_072_regression_status, feature_074_report.status, "Feature 074 regression slice"),
        ("073", feature_074_report.feature_073_regression_status, feature_074_report.status, "Feature 074 regression slice"),
        ("074", feature_075_report.feature_074_regression_status, feature_075_report.status, "Feature 075 regression slice"),
        ("075", feature_075_report, feature_075_report.status, "Feature 075 regression slice"),
    )
    return tuple(
        CombinedRegressionEvidence(
            feature_id=feature_id,
            status=source_status,
            passed=getattr(status_obj, "passed"),
            command_hint=", ".join(getattr(status_obj, "validation_commands", VALIDATION_COMMANDS[12:14])),
            scope=scope,
        )
        for feature_id, status_obj, source_status, scope in evidence_map
    )


def validate_combined_matrix(rows: Sequence[CombinedPolicyRow]) -> None:
    row_tuple = tuple(rows)
    if len(row_tuple) != 49:
        raise ValueError("combined matrix must contain exactly 49 rows")
    row_keys = {(row.policy_id, row.scenario_id) for row in row_tuple}
    if len(row_keys) != len(row_tuple):
        raise ValueError("combined matrix must not contain duplicate policy/scenario rows")
    expected_keys = {
        (policy_id, scenario_id)
        for policy_id in REQUIRED_POLICY_IDS
        for scenario_id in REQUIRED_SCENARIO_IDS
    }
    if row_keys != expected_keys:
        raise ValueError("combined matrix must cover all required policy/scenario combinations")


def _compute_aggregates(rows: tuple[CombinedPolicyRow, ...]) -> tuple[CombinedPolicyAggregate, ...]:
    return tuple(
        aggregate_combined_rows(tuple(row for row in rows if row.policy_id == policy_id))
        for policy_id in REQUIRED_POLICY_IDS
    )


def _claim_boundary() -> tuple[str, ...]:
    return (
        "No training claim is made.",
        "No superiority claim is made.",
        "No final evaluation claim is made.",
        "No statistical significance claim is made.",
        "No full paper reproduction claim is made.",
        "Feature 074 rows are consumed as upstream readiness evidence.",
        "Feature 075 rows are consumed as upstream readiness evidence.",
        "Action-bound evidence is preserved in the normalized combined matrix.",
        "Compatibility mode is not used in the combined readiness layer.",
    )


def build_feature_076_report(
    changed_files: Sequence[str] | None = None,
    validation_commands: Sequence[str] | None = None,
) -> CombinedComparativeReadinessReport:
    checked_changed_files = tuple(validate_scope(DEFAULT_CHANGED_FILES if changed_files is None else changed_files))
    feature_074_report = _feature_074_report()
    feature_075_report = _feature_075_report()
    if not feature_074_report.passed:
        raise ValueError("Feature 074 report must be passed")
    if not feature_075_report.passed:
        raise ValueError("Feature 075 report must be passed")
    rows = build_combined_rows()
    aggregates = _compute_aggregates(rows)
    regression_evidence = build_regression_evidence()
    report = CombinedComparativeReadinessReport(
        feature_name="Feature 076 - Combined Baseline + Proposed Comparative Readiness",
        status=FEATURE_076_STATUS_READY,
        passed=True,
        rows=rows,
        aggregates=aggregates,
        regression_evidence=regression_evidence,
        required_policy_ids=REQUIRED_POLICY_IDS,
        required_scenario_ids=REQUIRED_SCENARIO_IDS,
        claim_boundary=_claim_boundary(),
        scope_evidence=(
            "Allowed scope: specs/076-combined-baseline-proposed-comparative-readiness/**",
            "Allowed scope: src/analysis/combined_baseline_proposed_comparative_readiness/**",
            "Allowed scope: tests/unit/test_combined_baseline_proposed_comparative_readiness_*.py",
            "Allowed scope: tests/integration/test_combined_baseline_proposed_comparative_readiness_*.py",
            "Forbidden scope: src/environment/**",
            "Forbidden scope: src/policies/**",
            "Forbidden scope: src/training/**",
            "Forbidden scope: src/agents/**",
            "Forbidden scope: artifacts/**",
            "Forbidden scope: resources/**",
            "Forbidden scope: Feature 077+ paths",
        ),
        source_features=("074", "075"),
    )
    return report


def render_feature_076_report(report: CombinedComparativeReadinessReport) -> str:
    payload = report.to_dict()
    feature_074_status = _feature_074_report().status
    feature_075_status = _feature_075_report().status
    row_sections = [
        "\n".join([f"### {row['policy_id']} / {row['scenario_id']}", _json_dump(row).rstrip()])
        for row in payload["rows"]
    ]
    aggregate_sections = [
        "\n".join([f"### {aggregate['policy_id']}", _json_dump(aggregate).rstrip()])
        for aggregate in payload["aggregates"]
    ]
    regression_sections = [
        "\n".join([f"### {evidence['feature_id']}", _json_dump(evidence).rstrip()])
        for evidence in payload["regression_evidence"]
    ]
    return "\n".join(
        [
            "# Feature 076 Combined Baseline + Proposed Comparative Readiness Report",
            "",
            f"- feature_name: `{payload['feature_name']}`",
            f"- status: `{payload['status']}`",
            f"- passed: `{payload['passed']}`",
            "",
            "## Source Features",
            *[f"- {source_feature}" for source_feature in payload["source_features"]],
            f"- Feature 074 source report status: `{feature_074_status}`",
            f"- Feature 075 source report status: `{feature_075_status}`",
            "",
            "## Required Policy / Method IDs",
            *[f"- {policy_id}" for policy_id in payload["required_policy_ids"]],
            "",
            "## Required Scenario IDs",
            *[f"- {scenario_id}" for scenario_id in payload["required_scenario_ids"]],
            "",
            f"- total_row_count: `{len(payload['rows'])}`",
            f"- aggregate_count: `{len(payload['aggregates'])}`",
            "",
            "## Claim Boundary",
            *payload["claim_boundary"],
            "",
            "## Scope Evidence",
            *payload["scope_evidence"],
            "",
            "## Combined Rows",
            *row_sections,
            "",
            "## Combined Aggregates",
            *aggregate_sections,
            "",
            "## Regression Evidence",
            *regression_sections,
            "",
            "## Comparative Scope",
            "Feature 074 rows are consumed.",
            "Feature 075 rows are consumed.",
            "Action-bound evidence is preserved.",
            "Compatibility mode is not used.",
            "No superiority claim is made.",
            "No final evaluation claim is made.",
            "No statistical significance claim is made.",
            "No full paper reproduction claim is made.",
            "",
        ]
    )


def write_feature_076_report(output_dir: Path | str = DEFAULT_OUTPUT_DIR) -> Path:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    report = build_feature_076_report()
    markdown_path = output_path / "feature-076-combined-baseline-proposed-comparative-readiness-report.md"
    json_path = output_path / "feature-076-combined-baseline-proposed-comparative-readiness-report.json"
    markdown_path.write_text(render_feature_076_report(report), encoding="utf-8")
    json_path.write_text(_json_dump(report.to_dict()), encoding="utf-8")
    return markdown_path
