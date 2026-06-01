from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from functools import lru_cache
from pathlib import Path
import json
from typing import Any

from .config import (
    BASE_PAPER_TARGET,
    DEFAULT_CHANGED_FILES,
    DEFAULT_OUTPUT_DIR,
    FEATURE_ID,
    FEATURE_NAME,
    READY_STATUS,
    REQUIRED_COMPONENT_IDS,
    SOURCE_OCR,
    SOURCE_PDF,
    validate_scope,
)
from .implementation_scan import scan_current_implementation
from .model import (
    HoodieProposedComponent,
    HoodieProposedFidelityReport,
    HoodieProposedRepairPlanEntry,
)
from .paper_extract import extract_paper_components, validate_paper_extraction


_IMPLEMENTED_COMPONENT_IDS = {"action_space"}


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _repair_plan_for(component: HoodieProposedComponent) -> HoodieProposedRepairPlanEntry | None:
    if component.status == "implemented" or component.status == "not_applicable":
        return None
    return HoodieProposedRepairPlanEntry(
        component_id=component.component_id,
        gap_type=component.gap,
        repair_action=component.required_repair,
        target_files=(
            "src/analysis/hoodie_proposed_fidelity/report.py",
            "src/analysis/hoodie_proposed_fidelity/model.py",
            "src/analysis/proposed_method_integration_readiness/report.py",
            "src/analysis/campaign_execution_engine/report.py",
            "src/analysis/result_aggregation_statistical_summary/aggregator.py",
            "src/analysis/distributed_multi_agent_hoodie_training/agent.py",
            "src/analysis/distributed_multi_agent_hoodie_training/coordinator.py",
            "src/analysis/distributed_multi_agent_hoodie_training/policy.py",
            "src/analysis/distributed_multi_agent_hoodie_training/replay.py",
        ),
        tests_needed=(
            "tests/unit/test_hoodie_proposed_fidelity_model.py",
            "tests/unit/test_hoodie_proposed_fidelity_paper_extract.py",
            "tests/unit/test_hoodie_proposed_fidelity_implementation_scan.py",
            "tests/unit/test_hoodie_proposed_fidelity_report.py",
        ),
    )


def _current_implementation_for(component_id: str) -> tuple[str, str, str, str]:
    observation = {item.component_id: item for item in scan_current_implementation()}[component_id]
    return (
        observation.current_implementation,
        observation.implementation_reference,
        observation.status,
        observation.gap,
    )


def build_paper_components() -> tuple[HoodieProposedComponent, ...]:
    validate_paper_extraction()
    components: list[HoodieProposedComponent] = []
    implementation_map = {item.component_id: item for item in scan_current_implementation()}
    for definition in extract_paper_components():
        observation = implementation_map[definition.component_id]
        components.append(
            HoodieProposedComponent(
                component_id=definition.component_id,
                component_name=definition.component_name,
                paper_definition=definition.paper_definition,
                paper_source=definition.paper_source,
                current_implementation=observation.current_implementation,
                implementation_reference=observation.implementation_reference,
                status=observation.status,
                gap=observation.gap,
                required_repair=observation.required_repair,
            )
        )
    return tuple(components)


def build_gap_summary(components: Sequence[HoodieProposedComponent]) -> tuple[str, ...]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for component in components:
        if component.status == "implemented":
            continue
        grouped[component.gap].append(component.component_id)
    summary: list[str] = []
    for gap_type in sorted(grouped):
        summary.append(f"{gap_type}: {', '.join(grouped[gap_type])}")
    return tuple(summary)


def build_repair_plan(components: Sequence[HoodieProposedComponent]) -> tuple[HoodieProposedRepairPlanEntry, ...]:
    entries: list[HoodieProposedRepairPlanEntry] = []
    for component in components:
        entry = _repair_plan_for(component)
        if entry is not None:
            entries.append(entry)
    return tuple(entries)


def build_validation_summary(components: Sequence[HoodieProposedComponent]) -> tuple[str, ...]:
    status_counts = defaultdict(int)
    for component in components:
        status_counts[component.status] += 1
    return (
        f"feature_id={FEATURE_ID}",
        f"source_pdf={SOURCE_PDF}",
        f"source_ocr={SOURCE_OCR}",
        f"component_count={len(components)}",
        f"implemented_count={status_counts['implemented']}",
        f"partial_count={status_counts['partial']}",
        f"missing_count={status_counts['missing']}",
        f"not_applicable_count={status_counts['not_applicable']}",
        "HOODIE_PROPOSED is the base-paper target.",
        "No evaluation is performed.",
        "No non-paper extension claim is made.",
        "No overclaim is made.",
    )


def build_claim_boundary() -> tuple[str, ...]:
    return (
        "No evaluation claim is made.",
        "No non-paper extension claim is made.",
        "No overclaim is made.",
        "HOODIE_PROPOSED is the base-paper target.",
    )


def build_feature_081_report(
    changed_files: Sequence[str] | None = None,
) -> HoodieProposedFidelityReport:
    checked_changed_files = tuple(validate_scope(DEFAULT_CHANGED_FILES if changed_files is None else changed_files))
    components = build_paper_components()
    repair_plan = build_repair_plan(components)
    gap_summary = build_gap_summary(components)
    validation_summary = build_validation_summary(components)
    report = HoodieProposedFidelityReport(
        feature_id=FEATURE_ID,
        status=READY_STATUS,
        passed=True,
        source_pdf=SOURCE_PDF,
        source_ocr=SOURCE_OCR,
        component_count=len(components),
        implemented_count=sum(1 for component in components if component.status == "implemented"),
        partial_count=sum(1 for component in components if component.status == "partial"),
        missing_count=sum(1 for component in components if component.status == "missing"),
        not_applicable_count=sum(1 for component in components if component.status == "not_applicable"),
        components=components,
        gap_summary=gap_summary,
        repair_plan=repair_plan,
        validation_summary=validation_summary,
        claim_boundary=build_claim_boundary(),
        scope_evidence=checked_changed_files,
    )
    return report


def render_feature_081_report(report: HoodieProposedFidelityReport) -> str:
    payload = report.to_dict()
    component_sections = []
    for component in payload["components"]:
        component_sections.append(
            "\n".join(
                [
                    f"### {component['component_id']}",
                    _json_dump(component).rstrip(),
                ]
            )
        )
    repair_sections = []
    for entry in payload["repair_plan"]:
        repair_sections.append(
            "\n".join(
                [
                    f"### {entry['component_id']}",
                    _json_dump(entry).rstrip(),
                ]
            )
        )
    return "\n".join(
        [
            "# Feature 081 HOODIE Proposed Method Fidelity Extraction Report",
            "",
            f"- feature_id: `{payload['feature_id']}`",
            f"- status: `{payload['status']}`",
            f"- passed: `{payload['passed']}`",
            f"- source_pdf: `{payload['source_pdf']}`",
            f"- source_ocr: `{payload['source_ocr']}`",
            f"- component_count: `{payload['component_count']}`",
            f"- implemented_count: `{payload['implemented_count']}`",
            f"- partial_count: `{payload['partial_count']}`",
            f"- missing_count: `{payload['missing_count']}`",
            f"- not_applicable_count: `{payload['not_applicable_count']}`",
            "",
            "## Claim Boundary",
            *[f"- {item}" for item in payload["claim_boundary"]],
            "",
            "## Scope Evidence",
            *[f"- {item}" for item in payload["scope_evidence"]],
            "",
            "## Validation Summary",
            *[f"- {item}" for item in payload["validation_summary"]],
            "",
            "## Fidelity Matrix",
            *component_sections,
            "",
            "## Gap Summary",
            *[f"- {item}" for item in payload["gap_summary"]],
            "",
            "## Repair Plan",
            *repair_sections,
            "",
        ]
    )


def write_feature_081_report(output_dir: Path | str = DEFAULT_OUTPUT_DIR) -> Path:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    report = build_feature_081_report()
    markdown_path = output_path / "feature-081-hoodie-proposed-method-fidelity-extraction-report.md"
    json_path = output_path / "feature-081-hoodie-proposed-method-fidelity-extraction-report.json"
    markdown_path.write_text(render_feature_081_report(report), encoding="utf-8")
    json_path.write_text(_json_dump(report.to_dict()), encoding="utf-8")
    return markdown_path
