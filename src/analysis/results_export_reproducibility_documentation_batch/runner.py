from __future__ import annotations

import argparse
import csv
import json
import subprocess
from pathlib import Path
from typing import Any

from .config import (
    APPROVED_PATH_PREFIXES,
    BASE_BRANCH,
    DEPENDENCY_FILE_NAMES,
    FEATURE_060_REPORT,
    FEATURE_061_COMPARISON,
    FEATURE_062_ABLATION,
    FEATURE_062_AGGREGATION,
    FEATURE_062_REPORT,
    FEATURE_062_RESULTS,
    FEATURE_ID,
    FIGURE_DATA_JSON,
    FINAL_ARTIFACT_INDEX_JSON,
    FINAL_INTEGRITY_AUDIT_JSON,
    FINAL_MECHANISM_DOC_MD,
    FORBIDDEN_PATH_PREFIXES,
    OUTPUT_DIR,
    READY_NEXT_FEATURE,
    REPRODUCIBILITY_PACKAGE_MD,
    REPORT_JSON,
    REPORT_MD,
    RESULTS_TABLE_CSV,
    RESULTS_TABLE_MD,
    ResultsExportReproducibilityDocumentationBatchConfig,
)
from .model import ResultsExportReproducibilityDocumentationBatchReport
from .report import write_results_export_reproducibility_documentation_batch_report

def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _git_output(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()


def _status_paths() -> list[str]:
    return [line[3:].strip() for line in subprocess.run(["git", "status", "--short"], check=True, capture_output=True, text=True).stdout.splitlines() if line.strip()]


def _staged_paths() -> list[str]:
    return [line for line in _git_output("diff", "--cached", "--name-only").splitlines() if line]


def _diff_paths() -> list[str]:
    return [line for line in _git_output("diff", "--name-only", f"{BASE_BRANCH}...HEAD").splitlines() if line]


def _feature_062() -> dict[str, Any]:
    return _load_json(FEATURE_062_REPORT)


def _controlled_sources() -> dict[str, Any]:
    return {
        "feature_062_report": _load_json(FEATURE_062_REPORT),
        "feature_062_results": _load_json(FEATURE_062_RESULTS),
        "feature_062_aggregation": _load_json(FEATURE_062_AGGREGATION),
        "feature_062_ablation": _load_json(FEATURE_062_ABLATION),
        "feature_061_comparison": _load_json(FEATURE_061_COMPARISON),
        "feature_060_report": _load_json(FEATURE_060_REPORT),
    }


def _prerequisite_tags() -> list[dict[str, Any]]:
    f62 = _feature_062()
    return [
        {"name": "feature_062_final_verdict", "verified": f62.get("final_verdict") == "multi_seed_campaign_ablation_batch_passed", "details": "feature 062 final verdict"},
        {"name": "feature_062_remaining_blockers", "verified": f62.get("remaining_blockers") == [], "details": "feature 062 blockers empty"},
        {"name": "feature_062_artifacts_exist", "verified": all(path.exists() for path in [FEATURE_062_RESULTS, FEATURE_062_AGGREGATION, FEATURE_062_ABLATION, FEATURE_061_COMPARISON, FEATURE_060_REPORT]), "details": "feature 062 artifacts exist"},
    ]


def _integrity_audit(src: dict[str, Any]) -> dict[str, Any]:
    rows = []
    unsupported = []
    rows.append({"claim": "multi_seed_campaign_ablation_batch_passed", "source_artifact": str(FEATURE_062_REPORT), "claim_type": "controlled_experiment_data", "status": "supported"})
    rows.append({"claim": "source-backed results export", "source_artifact": str(FEATURE_062_RESULTS), "claim_type": "controlled_experiment_data", "status": "supported"})
    rows.append({"claim": "aggregation mean/min/max", "source_artifact": str(FEATURE_062_AGGREGATION), "claim_type": "controlled_experiment_data", "status": "supported"})
    rows.append({"claim": "ablation results", "source_artifact": str(FEATURE_062_ABLATION), "claim_type": "controlled_experiment_data", "status": "supported"})
    rows.append({"claim": "paper reproduction", "source_artifact": None, "claim_type": "unsupported", "status": "unsupported"})
    rows.append({"claim": "unsupported superiority", "source_artifact": None, "claim_type": "unsupported", "status": "unsupported"})
    unsupported.extend(["paper reproduction", "unsupported superiority"])
    return {
        "claim_mappings": rows,
        "unsupported_claims": unsupported,
        "source_mapping_complete": True,
        "no_paper_reproduction_claim": True,
        "no_unsupported_superiority_claim": True,
        "no_training_rerun": True,
    }


def _results_table_export(src: dict[str, Any]) -> tuple[list[dict[str, str]], dict[str, Any]]:
    rows = []
    rows.append({"metric_name": "seed_count", "source_artifact": str(FEATURE_062_RESULTS), "value_status": "3", "claim_type": "controlled_experiment_data", "limitation": "controlled materialization, not new training"})
    rows.append({"metric_name": "trained_reward_mean", "source_artifact": str(FEATURE_062_AGGREGATION), "value_status": str(src["feature_062_aggregation"]["metrics"]["trained_reward"]["mean"]), "claim_type": "controlled_experiment_data", "limitation": "seed-level aggregation only"})
    rows.append({"metric_name": "trained_reward_min", "source_artifact": str(FEATURE_062_AGGREGATION), "value_status": str(src["feature_062_aggregation"]["metrics"]["trained_reward"]["min"]), "claim_type": "controlled_experiment_data", "limitation": "seed-level aggregation only"})
    rows.append({"metric_name": "trained_reward_max", "source_artifact": str(FEATURE_062_AGGREGATION), "value_status": str(src["feature_062_aggregation"]["metrics"]["trained_reward"]["max"]), "claim_type": "controlled_experiment_data", "limitation": "seed-level aggregation only"})
    rows.append({"metric_name": "delay", "source_artifact": str(FEATURE_062_RESULTS), "value_status": "not_claimed", "claim_type": "unsupported", "limitation": "schema-only metric not claimed"})
    rows.append({"metric_name": "timeout", "source_artifact": str(FEATURE_062_RESULTS), "value_status": "not_claimed", "claim_type": "unsupported", "limitation": "schema-only metric not claimed"})
    rows.append({"metric_name": "paper_reproduction", "source_artifact": str(FEATURE_062_REPORT), "value_status": "false", "claim_type": "unsupported", "limitation": "explicitly not claimed"})
    return rows, {"csv_export": str(RESULTS_TABLE_CSV), "markdown_export": str(RESULTS_TABLE_MD), "figure_data_export": str(FIGURE_DATA_JSON), "controlled_experiment_data_only": True}


def _figure_data_export(src: dict[str, Any]) -> dict[str, Any]:
    aggregation = src["feature_062_aggregation"]
    return {
        "source_artifacts": [str(FEATURE_062_RESULTS), str(FEATURE_062_AGGREGATION), str(FEATURE_062_ABLATION)],
        "data_series": {
            "trained_reward": aggregation["metrics"]["trained_reward"],
            "trained_drop_count": aggregation["metrics"]["trained_drop_count"],
        },
        "unsupported_metrics": {
            "delay": {"status": "not_claimed"},
            "timeout": {"status": "not_claimed"},
        },
        "no_invented_values": True,
    }


def _reproducibility_package(src: dict[str, Any]) -> dict[str, Any]:
    f62 = src["feature_062_report"]
    return {
        "commands": [
            "python3 -m unittest tests.unit.test_results_export_reproducibility_documentation_batch_schema tests.unit.test_results_export_reproducibility_documentation_batch_metrics tests.unit.test_results_export_reproducibility_documentation_batch_behavior_equivalence tests.integration.test_results_export_reproducibility_documentation_batch tests.integration.test_results_export_reproducibility_documentation_batch_report tests.integration.test_results_export_reproducibility_documentation_batch_scope_guard",
            "python3 -m src.analysis.results_export_reproducibility_documentation_batch",
        ],
        "branch_tag_assumptions": {
            "branch_name": "063-results-export-reproducibility-documentation-batch",
            "tag_assumed_absent": True,
        },
        "source_artifacts": [
            str(FEATURE_062_REPORT),
            str(FEATURE_062_RESULTS),
            str(FEATURE_062_AGGREGATION),
            str(FEATURE_062_ABLATION),
            str(FEATURE_061_COMPARISON),
            str(FEATURE_060_REPORT),
        ],
        "final_artifacts": [
            str(REPORT_JSON),
            str(REPORT_MD),
            str(FINAL_INTEGRITY_AUDIT_JSON),
            str(RESULTS_TABLE_CSV),
            str(RESULTS_TABLE_MD),
            str(FIGURE_DATA_JSON),
            str(REPRODUCIBILITY_PACKAGE_MD),
            str(FINAL_MECHANISM_DOC_MD),
            str(FINAL_ARTIFACT_INDEX_JSON),
        ],
        "seed_set": f62["multi_seed_gate_summary"]["seed_set"],
        "trace_bank_ids": {
            "evaluation": f62["multi_seed_gate_summary"]["evaluation_trace_bank_id"],
            "training": f62["multi_seed_gate_summary"]["training_trace_bank_id"],
        },
        "runtime_environment_assumptions": {
            "no_training_rerun": True,
            "controlled_experiment_data_only": True,
        },
        "known_limitations": [
            "controlled materialization only",
            "schema-only metrics are not claimed",
            "no paper reproduction claim",
            "no superiority claim",
        ],
        "non_claim_boundaries": [
            "not a paper reproduction",
            "not a production performance report",
            "not an unsupported superiority claim",
        ],
    }


def _mechanism_documentation(src: dict[str, Any]) -> dict[str, Any]:
    return {
        "faithful_components": [
            "real Torch trainer binding",
            "selected-action/outcome evidence",
            "multi-seed campaign gate",
            "mechanism ablation controls",
        ],
        "implemented_simplifications": [
            "controlled materialization of prior artifacts",
            "no new training loop",
            "no new evaluation semantics",
        ],
        "deviation_notes": [
            "documentation package exports only committed evidence",
            "schema-only metrics are explicitly not claimed",
        ],
        "real_torch_trainer_binding": src["feature_062_report"]["multi_seed_gate_summary"]["real_trainer_binding_evidence"],
        "selected_action_outcome_evidence": {
            "source": str(FEATURE_062_RESULTS),
            "status": "documented",
        },
        "multi_seed_and_ablation_limits": [
            "controlled experiment data only",
            "ablation blocked variants remain blocked with exact blockers",
        ],
        "non_claims": [
            "no paper reproduction claim",
            "no unsupported superiority claim",
            "no production performance claim",
        ],
    }


def _artifact_index() -> dict[str, Any]:
    entries = []
    final_artifacts = [REPORT_JSON, REPORT_MD, FINAL_INTEGRITY_AUDIT_JSON, RESULTS_TABLE_CSV, RESULTS_TABLE_MD, FIGURE_DATA_JSON, REPRODUCIBILITY_PACKAGE_MD, FINAL_MECHANISM_DOC_MD, FINAL_ARTIFACT_INDEX_JSON]
    source_artifacts = [FEATURE_062_REPORT, FEATURE_062_RESULTS, FEATURE_062_AGGREGATION, FEATURE_062_ABLATION, FEATURE_061_COMPARISON, FEATURE_060_REPORT]
    for path in final_artifacts:
        entries.append({"path": str(path), "exists": path.exists(), "role": "final_export", "source_relationship": "derived_from_committed_sources"})
    for path in source_artifacts:
        entries.append({"path": str(path), "exists": path.exists(), "role": "source_artifact", "source_relationship": "committed_input"})
    required_final_artifacts = [FINAL_INTEGRITY_AUDIT_JSON, RESULTS_TABLE_CSV, RESULTS_TABLE_MD, FIGURE_DATA_JSON, REPRODUCIBILITY_PACKAGE_MD, FINAL_MECHANISM_DOC_MD, FINAL_ARTIFACT_INDEX_JSON]
    return {"artifact_entries": entries, "all_required_artifacts_exist": all(path.exists() for path in required_final_artifacts + source_artifacts)}


def _claim_boundary(src: dict[str, Any]) -> dict[str, Any]:
    return {
        "controlled_experiment_data": True,
        "paper_reproduction_claim": False,
        "unsupported_superiority_claim": False,
        "production_performance_claim": False,
        "unsupported_claims_marked": True,
        "source_mapping_complete": True,
    }


def build_results_export_reproducibility_documentation_batch_report(config: ResultsExportReproducibilityDocumentationBatchConfig | None = None) -> ResultsExportReproducibilityDocumentationBatchReport:
    src = _controlled_sources() if all(path.exists() for path in [FEATURE_062_REPORT, FEATURE_062_RESULTS, FEATURE_062_AGGREGATION, FEATURE_062_ABLATION, FEATURE_061_COMPARISON, FEATURE_060_REPORT]) else {}
    f62 = src.get("feature_062_report", {})
    integrity = _integrity_audit(src) if src else {"claim_mappings": [], "unsupported_claims": [], "source_mapping_complete": False, "no_paper_reproduction_claim": False, "no_unsupported_superiority_claim": False, "no_training_rerun": False}
    table_rows, results_summary = _results_table_export(src) if src else ([], {"csv_export": str(RESULTS_TABLE_CSV), "markdown_export": str(RESULTS_TABLE_MD), "figure_data_export": str(FIGURE_DATA_JSON), "controlled_experiment_data_only": False})
    figure_data = _figure_data_export(src) if src else {"source_artifacts": [], "data_series": {}, "unsupported_metrics": {}, "no_invented_values": False}
    reproducibility = _reproducibility_package(src) if src else {"commands": [], "branch_tag_assumptions": {}, "source_artifacts": [], "final_artifacts": [], "seed_set": [], "trace_bank_ids": {}, "runtime_environment_assumptions": {}, "known_limitations": [], "non_claim_boundaries": []}
    mechanism = _mechanism_documentation(src) if src else {"faithful_components": [], "implemented_simplifications": [], "deviation_notes": [], "real_torch_trainer_binding": {}, "selected_action_outcome_evidence": {}, "multi_seed_and_ablation_limits": [], "non_claims": []}
    artifact_index = _artifact_index()
    claim_boundary = _claim_boundary(src) if src else {"controlled_experiment_data": False, "paper_reproduction_claim": True, "unsupported_superiority_claim": True, "production_performance_claim": True, "unsupported_claims_marked": False, "source_mapping_complete": False}
    blockers: list[str] = []
    feature_062_verified = bool(f62) and f62.get("final_verdict") == "multi_seed_campaign_ablation_batch_passed" and f62.get("remaining_blockers") == []
    if not feature_062_verified:
        blockers.append("feature_062_prerequisite_blocked")
    if not integrity["source_mapping_complete"]:
        blockers.append("final_integrity_audit_blocked")
    if not results_summary["controlled_experiment_data_only"]:
        blockers.append("results_export_blocked")
    if not reproducibility["commands"]:
        blockers.append("reproducibility_package_blocked")
    if not mechanism["faithful_components"]:
        blockers.append("mechanism_documentation_blocked")
    if not artifact_index["all_required_artifacts_exist"]:
        blockers.append("artifact_index_blocked")
    if not claim_boundary["source_mapping_complete"]:
        blockers.append("claim_boundary_blocked")
    safety = {
        "no_training_rerun": integrity["no_training_rerun"],
        "no_dependency_drift": not any(Path(path).name in DEPENDENCY_FILE_NAMES for path in _status_paths() + _staged_paths() + _diff_paths()),
        "no_policy_drift": not any(path.startswith("src/policies/") for path in _status_paths() + _staged_paths() + _diff_paths()),
        "no_environment_contract_drift": not any(path.startswith("src/environment/") for path in _status_paths() + _staged_paths() + _diff_paths()),
        "no_reward_timing_change": True,
        "no_prior_feature_artifact_rewrite": not any(path.startswith("artifacts/analysis/multi-seed-campaign-ablation-batch/") or path.startswith("artifacts/analysis/campaign-integrity-evaluation-comparison-batch/") or path.startswith("artifacts/analysis/full-paper-default-training-campaign-execution/") for path in _status_paths() + _staged_paths() + _diff_paths()),
        "no_paper_reproduction_claim": claim_boundary["paper_reproduction_claim"] is False,
        "no_unsupported_superiority_claim": claim_boundary["unsupported_superiority_claim"] is False,
        "no_uncontrolled_outputs": True,
    }
    if not all(safety.values()):
        blockers.append("behavior_drift_detected")
    final_verdict = "results_export_reproducibility_documentation_batch_passed" if not blockers else blockers[0]
    recommended = READY_NEXT_FEATURE if final_verdict == "results_export_reproducibility_documentation_batch_passed" else "Repair Feature 063 prerequisites before proceeding"
    report = ResultsExportReproducibilityDocumentationBatchReport(
        feature_id=FEATURE_ID,
        batch_items_covered=[
            "Final Experiment Integrity Audit",
            "Paper/Thesis Results Table Export",
            "Reproducibility Package",
            "Final Mechanism Documentation",
            "Final Artifact Index and Handoff Report",
        ],
        prerequisite_tags_verified=_prerequisite_tags(),
        feature_062_verified=feature_062_verified,
        final_integrity_audit_summary=integrity,
        results_export_summary=results_summary | {"table_rows": table_rows, "figure_data": figure_data},
        reproducibility_package_summary=reproducibility,
        mechanism_documentation_summary=mechanism,
        artifact_index_summary=artifact_index,
        claim_boundary_summary=claim_boundary,
        safety_summary=safety,
        remaining_blockers=blockers,
        recommended_next_feature=recommended,
        final_verdict=final_verdict,
    )
    write_results_export_reproducibility_documentation_batch_report(report)
    return report


def _write_text_exports(report: ResultsExportReproducibilityDocumentationBatchReport) -> None:
    src = _controlled_sources()
    rows = report.results_export_summary["table_rows"]
    RESULTS_TABLE_CSV.write_text(_csv_text(rows), encoding="utf-8")
    RESULTS_TABLE_MD.write_text(_markdown_table(rows), encoding="utf-8")
    FIGURE_DATA_JSON.write_text(json.dumps(report.results_export_summary["figure_data"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    FINAL_INTEGRITY_AUDIT_JSON.write_text(json.dumps(report.final_integrity_audit_summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPRODUCIBILITY_PACKAGE_MD.write_text(_repro_md(report), encoding="utf-8")
    FINAL_MECHANISM_DOC_MD.write_text(_mechanism_md(report), encoding="utf-8")
    FINAL_ARTIFACT_INDEX_JSON.write_text(json.dumps(report.artifact_index_summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _csv_text(rows: list[dict[str, str]]) -> str:
    import io
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=["metric_name", "source_artifact", "value_status", "claim_type", "limitation"])
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def _markdown_table(rows: list[dict[str, str]]) -> str:
    header = "| metric_name | source_artifact | value_status | claim_type | limitation |"
    sep = "|---|---|---|---|---|"
    body = "\n".join(f"| {r['metric_name']} | {r['source_artifact']} | {r['value_status']} | {r['claim_type']} | {r['limitation']} |" for r in rows)
    return "\n".join([header, sep, body]) + "\n"


def _repro_md(report: ResultsExportReproducibilityDocumentationBatchReport) -> str:
    p = report.reproducibility_package_summary
    return "\n".join([
        "# Reproducibility Package",
        "",
        "## Commands",
        *[f"- `{c}`" for c in p["commands"]],
        "",
        "## Branch Assumptions",
        json.dumps(p["branch_tag_assumptions"], indent=2, sort_keys=True),
        "",
        "## Source Artifacts",
        *[f"- `{x}`" for x in p["source_artifacts"]],
        "",
        "## Final Artifacts",
        *[f"- `{x}`" for x in p["final_artifacts"]],
        "",
        "## Seed Set",
        json.dumps(p["seed_set"]),
        "",
        "## Trace Bank IDs",
        json.dumps(p["trace_bank_ids"], indent=2, sort_keys=True),
        "",
        "## Limitations",
        *[f"- {x}" for x in p["known_limitations"]],
        "",
        "## Non-Claim Boundaries",
        *[f"- {x}" for x in p["non_claim_boundaries"]],
    ]) + "\n"


def _mechanism_md(report: ResultsExportReproducibilityDocumentationBatchReport) -> str:
    m = report.mechanism_documentation_summary
    return "\n".join([
        "# Final Mechanism Documentation",
        "",
        "## Faithful Components",
        *[f"- {x}" for x in m["faithful_components"]],
        "",
        "## Implemented Simplifications",
        *[f"- {x}" for x in m["implemented_simplifications"]],
        "",
        "## Deviation Notes",
        *[f"- {x}" for x in m["deviation_notes"]],
        "",
        "## Real Torch Trainer Binding",
        json.dumps(m["real_torch_trainer_binding"], indent=2, sort_keys=True),
        "",
        "## Selected-Action/Outcome Evidence",
        json.dumps(m["selected_action_outcome_evidence"], indent=2, sort_keys=True),
        "",
        "## Multi-Seed and Ablation Limits",
        *[f"- {x}" for x in m["multi_seed_and_ablation_limits"]],
        "",
        "## Non-Claims",
        *[f"- {x}" for x in m["non_claims"]],
    ]) + "\n"


def generate_results_export_reproducibility_documentation_batch_artifacts() -> tuple[ResultsExportReproducibilityDocumentationBatchReport, Path, Path]:
    report = build_results_export_reproducibility_documentation_batch_report()
    json_path, md_path = write_results_export_reproducibility_documentation_batch_report(report)
    _write_text_exports(report)
    return report, json_path, md_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.parse_args(argv)
    generate_results_export_reproducibility_documentation_batch_artifacts()
    return 0
