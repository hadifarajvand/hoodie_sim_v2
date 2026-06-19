from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from .config import (
    BASE_BRANCH_NAME,
    COMPARATIVE_METRICS_TABLE_JSON,
    COMPARISON_READINESS_JSON,
    FEATURE_ID,
    FIGURE_MANIFEST_JSON,
    FINAL_FINDINGS_MD,
    INTEGRITY_AUDIT_JSON,
    OUTPUT_DIR,
    READY_NEXT_STEP,
    REQUIRED_FIGURES,
    THESIS_TABLES_MD,
    UnifiedCampaignAnalysisConfig,
)
from .figures import generate_figures
from .model import UnifiedCampaignAnalysisReport
from .report import json_dump, write_unified_campaign_analysis_report

APPROVED_PATH_PREFIXES = (
    "artifacts/analysis/unified-campaign-result-analysis-figures-findings/",
    "docs/architecture/euls_phase21_unified_campaign_result_analysis_figures_findings.md",
    "specs/062-unified-campaign-result-analysis-figures-findings/",
    "src/analysis/unified_campaign_result_analysis_figures_findings/",
    "tests/unit/test_unified_campaign_result_analysis_figures_findings",
    "tests/integration/test_unified_campaign_result_analysis_figures_findings",
)
FORBIDDEN_PATH_PREFIXES = (
    "src/environment/",
    "src/dal/",
    "src/policies/",
    "src/environment/replay_hash.py",
    "src/analysis/full_training_reproduction_campaign/",
    "src/analysis/full_paper_default_training_campaign_execution/",
    "src/analysis/evaluation_trace_bank_baseline_harness/",
    "src/analysis/full_paper_default_training_campaign_gate/",
    "src/analysis/real_trainer_reduced_budget_campaign_execution_validation/",
    "requirements",
    "pyproject.toml",
    "poetry.lock",
    "uv.lock",
    "AGENTS.md",
    ".specify/feature.json",
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _git_output(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def _status_paths() -> list[str]:
    lines = _git_output("status", "--short", "--untracked-files=no").splitlines()
    return [line[3:].strip() for line in lines if line.strip()]


def _diff_names(base_ref: str = BASE_BRANCH_NAME) -> list[str]:
    output = _git_output("diff", "--name-only", f"{base_ref}...HEAD")
    return [line.strip() for line in output.splitlines() if line.strip()]


def _staged_paths() -> list[str]:
    output = _git_output("diff", "--cached", "--name-only")
    return [line.strip() for line in output.splitlines() if line.strip()]


def _paths_approved(paths: list[str]) -> bool:
    if any(path.startswith(FORBIDDEN_PATH_PREFIXES) for path in paths):
        return False
    return all(path.startswith(APPROVED_PATH_PREFIXES) for path in paths)


def _feature_060_artifacts(config: UnifiedCampaignAnalysisConfig) -> dict[str, dict[str, Any]]:
    return {
        "report": _load_json(config.feature_060_report_path),
        "training": _load_json(config.feature_060_training_path),
        "evaluation": _load_json(config.feature_060_evaluation_path),
        "baseline": _load_json(config.feature_060_baseline_path),
        "checkpoint": _load_json(config.feature_060_checkpoint_path),
        "manifest": _load_json(config.feature_060_manifest_path),
    }


def _verify_feature_060(artifacts: dict[str, dict[str, Any]]) -> dict[str, Any]:
    report = artifacts["report"]
    training = artifacts["training"]
    baseline = artifacts["baseline"]
    campaign = report.get("campaign_execution_summary", {})
    safety = report.get("safety_summary", {})
    dist = training.get("action_distribution", {})
    replay_size = int(training.get("replay_size", -1))
    action_total = sum(int(dist.get(key, 0)) for key in ("local", "horizontal", "vertical", "invalid_or_noop_action_count"))
    checks = {
        "final_verdict_passed": report.get("final_verdict") == "full_paper_default_training_campaign_execution_passed",
        "remaining_blockers_empty": report.get("remaining_blockers") == [],
        "full_campaign_executed": campaign.get("full_campaign_executed") is True,
        "training_episode_count": campaign.get("actual_training_episode_count") == 1000,
        "evaluation_episode_count": campaign.get("actual_evaluation_episode_count") == 100,
        "baseline_evaluation_episode_count": campaign.get("actual_baseline_evaluation_episode_count") == 100,
        "replay_size": replay_size == 110000,
        "training_action_accounting_reconciled": action_total == replay_size and training.get("action_accounting_reconciled") is True,
        "baseline_metrics_real_execution": baseline.get("baseline_metrics_real_execution") is True,
        "baseline_metric_shell_only_absent": "metric_shell_only" not in json.dumps(baseline),
        "no_paper_reproduction_claim": safety.get("no_paper_reproduction_claim") is True,
        "no_performance_superiority_claim": safety.get("no_performance_superiority_claim") is True,
        "no_baseline_superiority_claim": safety.get("no_baseline_superiority_claim") is True and baseline.get("no_baseline_superiority_claim") is True,
    }
    failed = [name for name, passed in checks.items() if not passed]
    return {
        "verified": not failed,
        "checks": checks,
        "failed_checks": failed,
        "source_artifacts": {
            "report": str(UnifiedCampaignAnalysisConfig().feature_060_report_path),
            "training": str(UnifiedCampaignAnalysisConfig().feature_060_training_path),
            "evaluation": str(UnifiedCampaignAnalysisConfig().feature_060_evaluation_path),
            "baseline": str(UnifiedCampaignAnalysisConfig().feature_060_baseline_path),
            "checkpoint": str(UnifiedCampaignAnalysisConfig().feature_060_checkpoint_path),
            "manifest": str(UnifiedCampaignAnalysisConfig().feature_060_manifest_path),
        },
    }


def _training_summary(training: dict[str, Any]) -> dict[str, Any]:
    return {
        "replay_size": training.get("replay_size"),
        "optimizer_step_count": training.get("optimizer_step_count"),
        "loss_finite": training.get("loss_finite"),
        "action_distribution": training.get("action_distribution", {}),
        "action_accounting_reconciled": training.get("action_accounting_reconciled"),
        "reward_summary": training.get("reward_summary", {}),
    }


def _evaluation_summary(evaluation: dict[str, Any]) -> dict[str, Any]:
    return {
        "evaluation_episode_count": evaluation.get("evaluation_episode_count"),
        "evaluation_trace_bank_id": evaluation.get("evaluation_trace_bank_id"),
        "metric_schema_coverage": evaluation.get("metric_schema_coverage", {}),
        "action_distribution": evaluation.get("action_distribution", {}),
        "no_performance_superiority_claim": evaluation.get("no_performance_superiority_claim"),
    }


def _baseline_summary(baseline: dict[str, Any]) -> dict[str, Any]:
    return {
        "actual_baseline_evaluation_episode_count": baseline.get("actual_baseline_evaluation_episode_count"),
        "baseline_metrics_real_execution": baseline.get("baseline_metrics_real_execution"),
        "baseline_policy_names": baseline.get("baseline_policy_names", []),
        "evaluated_policy_count": baseline.get("evaluated_policy_count"),
        "no_baseline_superiority_claim": baseline.get("no_baseline_superiority_claim"),
        "per_policy_episode_counts": {
            name: metrics.get("episode_count")
            for name, metrics in baseline.get("per_policy_metrics", {}).items()
        },
    }


def _comparison_readiness(verified: bool, artifacts: dict[str, dict[str, Any]]) -> dict[str, Any]:
    baseline = artifacts["baseline"]
    per_policy = baseline.get("per_policy_metrics", {})
    return {
        "comparison_ready": verified,
        "comparison_scope": "comparison readiness only; performance superiority not claimed",
        "descriptive_comparisons_available": [
            "training_action_distribution",
            "baseline_policy_action_distribution",
            "budget_integrity",
            "metric_availability",
            "artifact_completeness",
        ],
        "baseline_policy_count": len(per_policy),
        "performance_claim": False,
        "performance_superiority_claim_made": False,
        "paper_reproduction_claim_made": False,
        "baseline_superiority_claim_made": False,
    }


def _comparative_metrics_table(artifacts: dict[str, dict[str, Any]]) -> dict[str, Any]:
    report = artifacts["report"]
    training = artifacts["training"]
    baseline = artifacts["baseline"]
    campaign = report.get("campaign_execution_summary", {})
    rows: list[dict[str, Any]] = [
        {"metric": "training_episode_count", "value": campaign.get("actual_training_episode_count"), "claim": "integrity"},
        {"metric": "evaluation_episode_count", "value": campaign.get("actual_evaluation_episode_count"), "claim": "integrity"},
        {"metric": "baseline_evaluation_episode_count", "value": campaign.get("actual_baseline_evaluation_episode_count"), "claim": "integrity"},
        {"metric": "replay_size", "value": training.get("replay_size"), "claim": "integrity"},
        {"metric": "optimizer_step_count", "value": training.get("optimizer_step_count"), "claim": "execution evidence"},
    ]
    for name, metrics in baseline.get("per_policy_metrics", {}).items():
        rows.append(
            {
                "metric": f"baseline_{name}_episode_count",
                "value": metrics.get("episode_count"),
                "claim": "baseline execution evidence, not superiority",
            }
        )
    return {
        "rows": rows,
        "performance_claim": False,
        "notes": "Descriptive table for thesis/report use; no paper reproduction or superiority claim.",
    }


def _claim_safety(verified: bool, report: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    safety = report.get("safety_summary", {})
    return {
        "claim_safety_passed": verified,
        "paper_reproduction_claim_made": safety.get("no_paper_reproduction_claim") is not True,
        "performance_superiority_claim_made": safety.get("no_performance_superiority_claim") is not True,
        "baseline_superiority_claim_made": safety.get("no_baseline_superiority_claim") is not True or baseline.get("no_baseline_superiority_claim") is not True,
        "allowed_claim": "comparison readiness only; performance superiority not claimed",
    }


def _write_tables_and_findings(
    *,
    output_dir: Path,
    table: dict[str, Any],
    report: UnifiedCampaignAnalysisReport,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / COMPARATIVE_METRICS_TABLE_JSON.name).write_text(json_dump(table), encoding="utf-8")
    table_lines = [
        "# Thesis Result Tables",
        "",
        "| Metric | Value | Claim Boundary |",
        "| --- | ---: | --- |",
    ]
    for row in table["rows"]:
        table_lines.append(f"| {row['metric']} | {row['value']} | {row['claim']} |")
    table_lines.extend(["", "No paper reproduction, performance superiority, or baseline superiority claim is made."])
    (output_dir / THESIS_TABLES_MD.name).write_text("\n".join(table_lines) + "\n", encoding="utf-8")

    findings_lines = [
        "# Final Experimental Findings",
        "",
        "Feature 062 audited the already generated Feature 060 full-campaign artifacts.",
        "The findings are descriptive and comparison-ready; they do not claim HOODIE paper reproduction or superiority.",
        "",
        f"- final_verdict: `{report.final_verdict}`",
        f"- integrity_audit_passed: `{report.integrity_audit_result.get('passed')}`",
        f"- comparison_ready: `{report.comparison_readiness.get('comparison_ready')}`",
        f"- figures_generated: `{report.figure_manifest.get('figures_generated')}`",
        "",
        "Recommended next step is external review of these artifacts.",
    ]
    (output_dir / FINAL_FINDINGS_MD.name).write_text("\n".join(findings_lines) + "\n", encoding="utf-8")
    return {
        "comparative_metrics_table": str(output_dir / COMPARATIVE_METRICS_TABLE_JSON.name),
        "thesis_result_tables": str(output_dir / THESIS_TABLES_MD.name),
        "final_findings": str(output_dir / FINAL_FINDINGS_MD.name),
    }


def _scope_guard_blockers() -> list[str]:
    paths = _status_paths() + _staged_paths() + _diff_names()
    return ["scope_drift_detected"] if paths and not _paths_approved(paths) else []


def build_unified_campaign_analysis_report(
    config: UnifiedCampaignAnalysisConfig | None = None,
    *,
    generate_output_figures: bool = True,
) -> UnifiedCampaignAnalysisReport:
    cfg = config or UnifiedCampaignAnalysisConfig()
    missing = [
        str(path)
        for path in (
            cfg.feature_060_report_path,
            cfg.feature_060_training_path,
            cfg.feature_060_evaluation_path,
            cfg.feature_060_baseline_path,
            cfg.feature_060_checkpoint_path,
            cfg.feature_060_manifest_path,
        )
        if not path.exists()
    ]
    if missing:
        prerequisite = {"verified": False, "missing_artifacts": missing, "checks": {}}
        blockers = ["feature_060_artifacts_missing"]
        return UnifiedCampaignAnalysisReport(
            feature_id=FEATURE_ID,
            feature_060_prerequisite_verification=prerequisite,
            integrity_audit_result={"passed": False, "blockers": blockers},
            training_metrics_summary={},
            evaluation_metrics_summary={},
            baseline_evaluation_summary={},
            comparison_readiness={"comparison_ready": False, "performance_claim": False},
            result_tables_summary={},
            figure_manifest={"figures_generated": False, "figure_files": []},
            claim_safety_review={
                "claim_safety_passed": False,
                "paper_reproduction_claim_made": False,
                "performance_superiority_claim_made": False,
                "baseline_superiority_claim_made": False,
            },
            remaining_blockers=blockers,
            recommended_next_step="Repair Feature 060 artifact inputs",
            final_verdict="feature_060_prerequisite_blocked",
        )
    artifacts = _feature_060_artifacts(cfg)
    prerequisite = _verify_feature_060(artifacts)
    scope_blockers = _scope_guard_blockers()
    blockers = list(prerequisite["failed_checks"]) + scope_blockers
    integrity = {
        "passed": not blockers,
        "feature_060_verified": prerequisite["verified"],
        "scope_guard_passed": not scope_blockers,
        "blockers": blockers,
    }
    claim_safety = _claim_safety(not blockers, artifacts["report"], artifacts["baseline"])
    figures = (
        generate_figures(
            figures_dir=cfg.figures_dir,
            training=artifacts["training"],
            baseline=artifacts["baseline"],
            campaign_summary=artifacts["report"].get("campaign_execution_summary", {}),
        )
        if generate_output_figures and not blockers
        else {"figures_generated": False, "figure_files": []}
    )
    if not blockers and set(REQUIRED_FIGURES) - set(figures.get("figure_files", [])):
        blockers.append("figures_missing")
    final_verdict = "unified_campaign_result_analysis_ready" if not blockers else "result_integrity_blocked"
    if scope_blockers:
        final_verdict = "scope_drift_detected"
    if blockers and any(name.startswith("no_") or "claim" in name for name in blockers):
        final_verdict = "claim_safety_blocked"
    report = UnifiedCampaignAnalysisReport(
        feature_id=FEATURE_ID,
        feature_060_prerequisite_verification=prerequisite,
        integrity_audit_result=integrity,
        training_metrics_summary=_training_summary(artifacts["training"]),
        evaluation_metrics_summary=_evaluation_summary(artifacts["evaluation"]),
        baseline_evaluation_summary=_baseline_summary(artifacts["baseline"]),
        comparison_readiness=_comparison_readiness(not blockers, artifacts),
        result_tables_summary={},
        figure_manifest=figures,
        claim_safety_review=claim_safety,
        remaining_blockers=blockers,
        recommended_next_step=READY_NEXT_STEP if not blockers else "Repair unified campaign analysis blockers",
        final_verdict=final_verdict,
    )
    table = _comparative_metrics_table(artifacts)
    table_paths = _write_tables_and_findings(output_dir=cfg.output_dir, table=table, report=report) if not blockers else {}
    return UnifiedCampaignAnalysisReport(
        **{
            **report.to_dict(),
            "result_tables_summary": {
                "tables_generated": not blockers,
                "table_paths": table_paths,
                "performance_claim": False,
            },
        }
    )


def run_unified_campaign_analysis(config: UnifiedCampaignAnalysisConfig | None = None) -> UnifiedCampaignAnalysisReport:
    cfg = config or UnifiedCampaignAnalysisConfig()
    cfg.output_dir.mkdir(parents=True, exist_ok=True)
    report = build_unified_campaign_analysis_report(cfg)
    payload = report.to_dict()
    write_unified_campaign_analysis_report(report, cfg.output_dir)
    (cfg.output_dir / INTEGRITY_AUDIT_JSON.name).write_text(json_dump(payload["integrity_audit_result"]), encoding="utf-8")
    (cfg.output_dir / COMPARISON_READINESS_JSON.name).write_text(json_dump(payload["comparison_readiness"]), encoding="utf-8")
    (cfg.output_dir / FIGURE_MANIFEST_JSON.name).write_text(json_dump(payload["figure_manifest"]), encoding="utf-8")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Feature 062 unified campaign analysis artifacts")
    parser.add_argument("--json", action="store_true", help="print JSON report to stdout")
    args = parser.parse_args(argv)
    report = run_unified_campaign_analysis()
    if args.json:
        print(json_dump(report.to_dict()), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
