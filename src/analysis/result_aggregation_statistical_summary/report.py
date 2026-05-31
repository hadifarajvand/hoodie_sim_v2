from __future__ import annotations

from collections.abc import Sequence
from functools import lru_cache
from pathlib import Path
import json
from typing import Any

from src.analysis.campaign_execution_engine.report import build_feature_078_report

from .aggregator import (
    build_comparative_aggregates,
    build_policy_aggregates,
    verify_all_policies_and_metrics,
)
from .config import (
    BLOCKED_STATUS,
    DEFAULT_CHANGED_FILES,
    DEPENDENCY_FEATURES,
    FEATURE_ID,
    FEATURE_NAME,
    READY_STATUS,
    REQUIRED_METRIC_NAMES,
    REQUIRED_POLICY_IDS,
    REQUIRED_SCENARIO_IDS,
    SUMMARY_FIELD_NAMES,
    validate_scope,
)
from .model import AggregationReport


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


@lru_cache(maxsize=1)
def _feature_078_report():
    return build_feature_078_report()


def _claim_boundary() -> tuple[str, ...]:
    return (
        "No training claim is made.",
        "No ranking claim is made.",
        "No winner claim is made.",
        "No superiority claim is made.",
        "No final evaluation claim is made.",
        "No statistical significance claim is made.",
        "Feature 078 raw execution rows are consumed as the aggregation substrate.",
        "No runtime execution occurs in Feature 079.",
        "No execution cells are recomputed in Feature 079.",
    )


def _validation_summary(
    *,
    source_status: str,
    source_passed: bool,
    row_count: int,
    policy_aggregate_count: int,
    comparative_aggregate_count: int,
) -> tuple[str, ...]:
    return (
        f"Feature 078 status: {source_status}",
        f"Feature 078 passed: {source_passed}",
        f"Feature 078 row count: {row_count}",
        f"Policy coverage: {policy_aggregate_count} policies",
        f"Comparative aggregate count: {comparative_aggregate_count}",
        f"Metrics summarized: {', '.join(REQUIRED_METRIC_NAMES)}",
        f"Summary fields: {', '.join(SUMMARY_FIELD_NAMES)}",
        "CI95 fields are populated deterministically from row summaries.",
        "No runtime execution occurs.",
        "No ranking output is produced.",
        "No winner declaration is produced.",
    )


def build_feature_079_report(
    *,
    changed_files: Sequence[str] | None = None,
) -> AggregationReport:
    checked_changed_files = tuple(validate_scope(DEFAULT_CHANGED_FILES if changed_files is None else changed_files))
    feature_078 = _feature_078_report()
    if feature_078.status != "campaign_execution_engine_ready" or not feature_078.passed:
        raise ValueError("Feature 078 must be ready and passed before aggregation")
    rows = feature_078.result_rows
    if not rows:
        raise ValueError("Feature 078 must provide raw execution rows")
    policy_aggregates = build_policy_aggregates(rows)
    comparative_aggregates = build_comparative_aggregates(rows)
    verify_all_policies_and_metrics(policy_aggregates, comparative_aggregates)
    passed = bool(
        feature_078.passed
        and feature_078.status == "campaign_execution_engine_ready"
        and len(rows) > 0
        and len(policy_aggregates) == len(REQUIRED_POLICY_IDS)
        and len(comparative_aggregates) > 0
        and all(summary.count > 0 for aggregate in policy_aggregates for summary in aggregate.metric_summaries)
        and all(summary.ci95_low <= summary.mean <= summary.ci95_high for aggregate in policy_aggregates for summary in aggregate.metric_summaries)
        and all(aggregate.policy_aggregates for aggregate in comparative_aggregates)
    )
    status = READY_STATUS if passed else BLOCKED_STATUS
    return AggregationReport(
        feature_id=FEATURE_ID,
        status=status,
        passed=passed,
        dependency_features=DEPENDENCY_FEATURES,
        policy_aggregates=policy_aggregates,
        comparative_aggregates=comparative_aggregates,
        validation_summary=_validation_summary(
            source_status=feature_078.status,
            source_passed=feature_078.passed,
            row_count=len(rows),
            policy_aggregate_count=len(policy_aggregates),
            comparative_aggregate_count=len(comparative_aggregates),
        ),
        claim_boundary=_claim_boundary(),
    )


def render_feature_079_report(report: AggregationReport) -> str:
    payload = report.to_dict()
    policy_sections = [
        "\n".join(
            [
                f"### {aggregate['policy_id']}",
                _json_dump(aggregate).rstrip(),
            ]
        )
        for aggregate in payload["policy_aggregates"]
    ]
    comparative_sections = [
        "\n".join(
            [
                f"### {aggregate['grouping_type']} / {aggregate['grouping_key']}",
                _json_dump(aggregate).rstrip(),
            ]
        )
        for aggregate in payload["comparative_aggregates"]
    ]
    return "\n".join(
        [
            "# Feature 079 Result Aggregation Statistical Summary Report",
            "",
            f"- feature_id: `{payload['feature_id']}`",
            f"- status: `{payload['status']}`",
            f"- passed: `{payload['passed']}`",
            f"- dependency_features: {', '.join(payload['dependency_features'])}",
            f"- required_policies: {', '.join(REQUIRED_POLICY_IDS)}",
            f"- required_scenarios: {', '.join(REQUIRED_SCENARIO_IDS)}",
            f"- required_metrics: {', '.join(REQUIRED_METRIC_NAMES)}",
            f"- summary_fields: {', '.join(SUMMARY_FIELD_NAMES)}",
            "",
            "## Validation Summary",
            *[f"- {entry}" for entry in payload["validation_summary"]],
            "",
            "## Claim Boundary",
            *[f"- {entry}" for entry in payload["claim_boundary"]],
            "",
            "## Policy Aggregates",
            *policy_sections,
            "",
            "## Comparative Aggregates",
            *comparative_sections,
            "",
            "## Notes",
            "- Feature 078 raw execution rows are consumed as input.",
            "- No runtime execution occurs in Feature 079.",
            "- No ranking or winner declaration is produced.",
            "- No superiority, final evaluation, or statistical significance claim is made.",
        ]
    )


def write_feature_079_report(output_dir: str | Path, report: AggregationReport | None = None) -> Path:
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    output_path = target_dir / "result_aggregation_statistical_summary_report.md"
    output_path.write_text(render_feature_079_report(report or build_feature_079_report()), encoding="utf-8")
    return output_path
