from __future__ import annotations

from collections import defaultdict
from functools import lru_cache
from math import isnan
from pathlib import Path
import json
from typing import Any, Sequence

from src.analysis.controlled_evaluation_batch_readiness.report import build_feature_073_report
from src.analysis.end_to_end_hoodie_golden_trace_validation.report import build_feature_072_report
from src.analysis.full_hoodie_mechanism_fidelity_batch.report import build_feature_069_report
from src.analysis.runtime_paper_faithful_semantics_alignment.report import build_feature_071_report
from src.analysis.topology_timeout_reward_fidelity.report import build_feature_070_report
from src.evaluation.policy_registry import PolicyRegistry
from src.policies import (
    BalancedCooperationOffloadingPolicy,
    FullLocalComputingPolicy,
    HorizontalOffloadingPolicy,
    MinimumLatencyEstimateOffloadingPolicy,
    PolicyContext,
    RandomOffloadingPolicy,
    VerticalOffloadingPolicy,
)
from src.policies.common import action_family as runtime_action_family

from .config import DEFAULT_CHANGED_FILES, DEFAULT_OUTPUT_DIR, VALIDATION_COMMANDS, validate_scope
from .model import (
    BaselineComparativeReadinessReport,
    BaselinePolicyComparativeRegressionEvidence,
    BaselinePolicyDescriptor,
    PolicyAggregateComparison,
    PolicyScenarioComparison,
    REQUIRED_POLICY_IDS,
    REQUIRED_SCENARIO_IDS,
    aggregate_policy_rows,
)


FEATURE_074_STATUS_READY = "baseline_policy_comparative_evaluation_readiness_ready"
FEATURE_074_STATUS_WITH_BLOCKERS = "baseline_policy_comparative_evaluation_readiness_with_blockers"
FEATURE_074_RECOMMENDATION = "Feature 075 - Proposed Deadline-Aware Method Integration Readiness"


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


@lru_cache(maxsize=1)
def _feature_073_report():
    return build_feature_073_report()


@lru_cache(maxsize=1)
def _feature_070_report():
    return build_feature_070_report()


@lru_cache(maxsize=1)
def _feature_071_report():
    return build_feature_071_report()


@lru_cache(maxsize=1)
def _feature_072_report():
    return build_feature_072_report()


def _feature_069_regression() -> BaselinePolicyComparativeRegressionEvidence:
    report = build_feature_069_report()
    return BaselinePolicyComparativeRegressionEvidence(
        name="Feature 069 regression",
        passed=report.passed,
        summary="Feature 069 full HOODIE mechanism fidelity batch remains green and continues to serve as prerequisite evidence.",
        validation_commands=report.validation_commands,
    )


def _feature_068r_regression() -> BaselinePolicyComparativeRegressionEvidence:
    report = build_feature_069_report()
    evidence = report.feature_068r_regression_status
    return BaselinePolicyComparativeRegressionEvidence(
        name="Feature 068R regression",
        passed=evidence.passed,
        summary="Feature 068R baseline policy fidelity remains green and continues to cover the required policy registry contract.",
        validation_commands=evidence.validation_commands,
    )


def _feature_070_regression() -> BaselinePolicyComparativeRegressionEvidence:
    report = _feature_070_report()
    return BaselinePolicyComparativeRegressionEvidence(
        name="Feature 070 regression",
        passed=report.passed and report.status == "blocker_resolution_readiness_with_runtime_divergence",
        summary="Feature 070 topology, timeout/drop, and reward evidence remains green with runtime divergence still explicit.",
        validation_commands=(VALIDATION_COMMANDS[2],),
    )


def _feature_071_regression() -> BaselinePolicyComparativeRegressionEvidence:
    report = _feature_071_report()
    return BaselinePolicyComparativeRegressionEvidence(
        name="Feature 071 regression",
        passed=report.passed and report.status == "runtime_paper_faithful_semantics_alignment_ready",
        summary="Feature 071 runtime helper alignment remains green with paper mode default and explicit compatibility mode only.",
        validation_commands=tuple(VALIDATION_COMMANDS[3:5]),
    )


def _feature_072_regression() -> BaselinePolicyComparativeRegressionEvidence:
    report = _feature_072_report()
    return BaselinePolicyComparativeRegressionEvidence(
        name="Feature 072 regression",
        passed=report.passed and report.status == "end_to_end_golden_trace_validation_ready",
        summary="Feature 072 deterministic golden trace validation remains green and is consumed as prerequisite evidence.",
        validation_commands=tuple(VALIDATION_COMMANDS[5:7]),
    )


def _feature_073_regression() -> BaselinePolicyComparativeRegressionEvidence:
    report = _feature_073_report()
    return BaselinePolicyComparativeRegressionEvidence(
        name="Feature 073 regression",
        passed=report.passed and report.status == "controlled_evaluation_batch_readiness_ready",
        summary="Feature 073 controlled evaluation batch readiness remains green and provides the scenario universe for Feature 074.",
        validation_commands=tuple(VALIDATION_COMMANDS[7:9]),
    )


def _policy_family_label(policy_id: str) -> str:
    return {
        "FLC": "fixed-local / local-first family",
        "VO": "vertical-offload family",
        "HO": "horizontal-offload family",
        "RO": "random-offload family",
        "BCO": "balanced-cloud-offload family",
        "MLEO": "minimum-latency-estimation-offload family",
    }[policy_id]


def _expected_policy_type(policy_id: str):
    return {
        "FLC": FullLocalComputingPolicy,
        "VO": VerticalOffloadingPolicy,
        "HO": HorizontalOffloadingPolicy,
        "RO": RandomOffloadingPolicy,
        "BCO": BalancedCooperationOffloadingPolicy,
        "MLEO": MinimumLatencyEstimateOffloadingPolicy,
    }[policy_id]


def _copy_metrics(metrics):
    return type(metrics)(**metrics.to_dict())


def _scenario_task_metrics() -> dict[str, Any]:
    feature_073 = _feature_073_report()
    return {scenario.scenario_id: scenario.actual_metrics for scenario in feature_073.scenarios}


def _scenario_context(policy_id: str, scenario_id: str) -> PolicyContext:
    source_agent_id = "1"
    horizontal_destinations = ("6", "11", "16")
    if scenario_id == "illegal_horizontal_destination_attempt":
        horizontal_destinations = ("2", "6", "11", "16")

    legal_action_mask = {
        "local": True,
        "compute_local": True,
        "horizontal": True,
        "offload_horizontal": True,
        "vertical": True,
        "offload_vertical": True,
        "cloud": True,
        "6": True,
        "11": True,
        "16": True,
        "2": scenario_id != "illegal_horizontal_destination_attempt",
    }
    observation = {
        "scenario_id": scenario_id,
        "source_agent_id": source_agent_id,
        "local_action": "local",
        "cloud_action": "cloud",
        "horizontal_destinations": horizontal_destinations,
        "edge_agent_ids": horizontal_destinations,
        "placement_actions": {
            "local": "local",
            "vertical": "cloud",
            "horizontal": horizontal_destinations,
        },
        "fallback_hints": {"local": 1.0, "horizontal": 2.0, "vertical": 3.0},
        "balance_hint": {"local": 1.0, "horizontal": 2.0, "vertical": 3.0},
        "mleo_delay_candidates": {
            "local": {"total_delay": 3.0},
            "horizontal": {"total_delay": 4.0},
            "vertical": {"total_delay": 5.0},
        },
        "mleo_placement_candidates": [
            {"action_id": "local", "action_family": "local", "total_delay": 3.0},
            {"action_id": "cloud", "action_family": "vertical", "total_delay": 5.0},
            {"action_id": "6", "action_family": "horizontal", "total_delay": 4.0},
        ],
        "policy_id": policy_id,
    }
    return PolicyContext(observation=observation, legal_action_mask=legal_action_mask, trace_history=(policy_id, scenario_id))


def build_required_policy_descriptors() -> tuple[BaselinePolicyDescriptor, ...]:
    descriptors: list[BaselinePolicyDescriptor] = []
    for policy_id in REQUIRED_POLICY_IDS:
        try:
            policy = PolicyRegistry.resolve(policy_id)
        except Exception:
            descriptors.append(
                BaselinePolicyDescriptor(
                    policy_id=policy_id,
                    policy_family=_policy_family_label(policy_id),
                    registry_key=policy_id,
                    available=False,
                    decision_trace_supported=False,
                )
            )
            continue
        expected_type = _expected_policy_type(policy_id)
        available = isinstance(policy, expected_type)
        descriptors.append(
            BaselinePolicyDescriptor(
                policy_id=policy_id,
                policy_family=_policy_family_label(policy_id),
                registry_key=policy_id,
                available=available,
                decision_trace_supported=available and hasattr(policy, "choose_action"),
            )
        )
    return tuple(descriptors)


def build_policy_scenario_comparisons() -> tuple[PolicyScenarioComparison, ...]:
    feature_073 = _feature_073_report()
    scenario_metrics = _scenario_task_metrics()
    descriptors = {descriptor.policy_id: descriptor for descriptor in build_required_policy_descriptors()}
    comparisons: list[PolicyScenarioComparison] = []
    for policy_id in REQUIRED_POLICY_IDS:
        descriptor = descriptors[policy_id]
        policy = None
        if descriptor.available:
            policy = PolicyRegistry.resolve(policy_id)
        for scenario_id in REQUIRED_SCENARIO_IDS:
            metrics = _copy_metrics(scenario_metrics[scenario_id])
            if descriptor.available and policy is not None:
                context = _scenario_context(policy_id, scenario_id)
                try:
                    chosen_action = policy.choose_action(context)
                except Exception:
                    chosen_action = None
                if chosen_action is None:
                    trace: tuple[str, ...] = ()
                    trace_present = False
                    passed = False
                else:
                    trace = (
                        f"policy_id={policy_id}",
                        f"scenario_id={scenario_id}",
                        f"chosen_action={chosen_action}",
                        f"chosen_action_family={runtime_action_family(chosen_action)}",
                    )
                    trace_present = True
                    passed = True
            else:
                trace = ()
                trace_present = False
                passed = False
            comparisons.append(
                PolicyScenarioComparison(
                    policy_id=policy_id,
                    scenario_id=scenario_id,
                    policy_action_family=_policy_family_label(policy_id),
                    policy_decision_trace_present=trace_present,
                    decision_trace=trace,
                    metrics=metrics,
                    compatibility_mode_used=False,
                    passed=passed,
                )
            )
    return tuple(comparisons)


def compute_policy_aggregate_metrics(
    policy_id: str,
    scenario_comparisons: Sequence[PolicyScenarioComparison],
) -> PolicyAggregateComparison:
    rows = tuple(scenario_comparisons)
    if not rows:
        raise ValueError("policy aggregates require at least one scenario comparison")
    if any(row.policy_id != policy_id for row in rows):
        raise ValueError("scenario comparisons must belong to the requested policy")
    return aggregate_policy_rows(rows)


def _feature_068r_regression_evidence() -> BaselinePolicyComparativeRegressionEvidence:
    return _feature_068r_regression()


def _feature_069_regression_evidence() -> BaselinePolicyComparativeRegressionEvidence:
    return _feature_069_regression()


def _feature_070_regression_evidence() -> BaselinePolicyComparativeRegressionEvidence:
    return _feature_070_regression()


def _feature_071_regression_evidence() -> BaselinePolicyComparativeRegressionEvidence:
    return _feature_071_regression()


def _feature_072_regression_evidence() -> BaselinePolicyComparativeRegressionEvidence:
    return _feature_072_regression()


def _feature_073_regression_evidence() -> BaselinePolicyComparativeRegressionEvidence:
    return _feature_073_regression()


def _claim_boundary() -> str:
    return (
        "No final evaluation claim is made. No performance superiority claim is made. No statistical significance claim "
        "is made. No full paper reproduction claim is made. This layer only proves baseline policy comparative evaluation "
        "readiness over the Feature 073 controlled scenarios using paper-mode default semantics. Feature 073 controlled "
        "scenarios are consumed as the comparison universe. Feature 072 report is consumed as prerequisite evidence. "
        "Baseline policies are not rewritten. Compatibility mode is excluded from the default comparison. Feature 075 "
        "is the next proposed deadline-aware method integration readiness step, not training."
    )


def build_feature_074_report(
    changed_files: Sequence[str] | None = None,
    validation_commands: Sequence[str] | None = None,
) -> BaselineComparativeReadinessReport:
    checked_changed_files = tuple(validate_scope(DEFAULT_CHANGED_FILES if changed_files is None else changed_files))
    descriptors = build_required_policy_descriptors()
    comparisons = build_policy_scenario_comparisons()
    aggregates = tuple(
        compute_policy_aggregate_metrics(policy_id, tuple(row for row in comparisons if row.policy_id == policy_id))
        for policy_id in REQUIRED_POLICY_IDS
    )
    feature_068r = _feature_068r_regression_evidence()
    feature_069 = _feature_069_regression_evidence()
    feature_070 = _feature_070_regression_evidence()
    feature_071 = _feature_071_regression_evidence()
    feature_072 = _feature_072_regression_evidence()
    feature_073 = _feature_073_regression_evidence()
    passed = bool(
        all(descriptor.available for descriptor in descriptors)
        and all(descriptor.decision_trace_supported for descriptor in descriptors)
        and all(comparison.passed for comparison in comparisons)
        and all(not aggregate.compatibility_mode_used for aggregate in aggregates)
        and feature_068r.passed
        and feature_069.passed
        and feature_070.passed
        and feature_071.passed
        and feature_072.passed
        and feature_073.passed
    )
    status = FEATURE_074_STATUS_READY if passed else FEATURE_074_STATUS_WITH_BLOCKERS
    regression_commands = tuple(validation_commands) if validation_commands is not None else tuple(VALIDATION_COMMANDS)
    return BaselineComparativeReadinessReport(
        feature_name="Feature 074 - Baseline Policy Comparative Evaluation Readiness",
        status=status,
        passed=passed,
        changed_files=checked_changed_files,
        policy_descriptors=descriptors,
        scenario_comparisons=comparisons,
        policy_aggregate_metrics=aggregates,
        feature_068r_regression_status=BaselinePolicyComparativeRegressionEvidence(
            name=feature_068r.name,
            passed=feature_068r.passed,
            summary=feature_068r.summary,
            validation_commands=feature_068r.validation_commands,
        ),
        feature_069_regression_status=BaselinePolicyComparativeRegressionEvidence(
            name=feature_069.name,
            passed=feature_069.passed,
            summary=feature_069.summary,
            validation_commands=feature_069.validation_commands,
        ),
        feature_070_regression_status=BaselinePolicyComparativeRegressionEvidence(
            name=feature_070.name,
            passed=feature_070.passed,
            summary=feature_070.summary,
            validation_commands=feature_070.validation_commands,
        ),
        feature_071_regression_status=BaselinePolicyComparativeRegressionEvidence(
            name=feature_071.name,
            passed=feature_071.passed,
            summary=feature_071.summary,
            validation_commands=feature_071.validation_commands,
        ),
        feature_072_regression_status=BaselinePolicyComparativeRegressionEvidence(
            name=feature_072.name,
            passed=feature_072.passed,
            summary=feature_072.summary,
            validation_commands=feature_072.validation_commands,
        ),
        feature_073_regression_status=BaselinePolicyComparativeRegressionEvidence(
            name=feature_073.name,
            passed=feature_073.passed,
            summary=feature_073.summary,
            validation_commands=feature_073.validation_commands or regression_commands[7:9],
        ),
        paper_claim_boundary=_claim_boundary(),
        recommended_next_feature=FEATURE_074_RECOMMENDATION,
    )


def render_feature_074_report(report: BaselineComparativeReadinessReport) -> str:
    payload = report.to_dict()
    descriptor_sections = [
        "\n".join(
            [
                f"### {descriptor['policy_id']}",
                _json_dump(descriptor).rstrip(),
            ]
        )
        for descriptor in payload["policy_descriptors"]
    ]
    scenario_sections = [
        "\n".join(
            [
                f"### {comparison['policy_id']} / {comparison['scenario_id']}",
                _json_dump(comparison).rstrip(),
            ]
        )
        for comparison in payload["scenario_comparisons"]
    ]
    aggregate_sections = [
        "\n".join(
            [
                f"### {aggregate['policy_id']}",
                _json_dump(aggregate).rstrip(),
            ]
        )
        for aggregate in payload["policy_aggregate_metrics"]
    ]
    regression_sections = []
    for name in (
        "feature_068r_regression_status",
        "feature_069_regression_status",
        "feature_070_regression_status",
        "feature_071_regression_status",
        "feature_072_regression_status",
        "feature_073_regression_status",
    ):
        regression_sections.append(f"### {payload[name]['name']}\n{_json_dump(payload[name]).rstrip()}")
    return "\n".join(
        [
            "# Feature 074 Baseline Policy Comparative Evaluation Readiness Report",
            "",
            f"- feature_name: `{payload['feature_name']}`",
            f"- status: `{payload['status']}`",
            f"- passed: `{payload['passed']}`",
            f"- recommended_next_feature: {payload['recommended_next_feature']}",
            "",
            "## Claim Boundary",
            payload["paper_claim_boundary"],
            "",
            "## Comparative Scope",
            "Feature 072 report is consumed as prerequisite evidence.",
            "Feature 073 controlled scenarios are consumed as the comparison universe.",
            "Baseline policies are not rewritten.",
            "Compatibility mode is excluded from the default comparison.",
            "Policy decision traces are produced from the registry and policy helpers.",
            "",
            "## Policy Descriptors",
            *descriptor_sections,
            "",
            "## Scenario Comparisons",
            *scenario_sections,
            "",
            "## Policy Aggregate Metrics",
            *aggregate_sections,
            "",
            "## Regression Evidence",
            *regression_sections,
            "",
        ]
    )


def write_feature_074_report(output_dir: Path | str = DEFAULT_OUTPUT_DIR) -> Path:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    report = build_feature_074_report()
    markdown_path = output_path / "feature-074-baseline-policy-comparative-evaluation-readiness-report.md"
    json_path = output_path / "feature-074-baseline-policy-comparative-evaluation-readiness-report.json"
    markdown_path.write_text(render_feature_074_report(report), encoding="utf-8")
    json_path.write_text(_json_dump(report.to_dict()), encoding="utf-8")
    return markdown_path
