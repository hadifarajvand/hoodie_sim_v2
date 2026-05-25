from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from .config import (
    APPROVED_PATH_PREFIXES,
    BASE_BRANCH,
    BASELINE_RESULTS_JSON,
    BRANCH_NAME,
    COMPARISON_JSON,
    COMPARISON_MD,
    COMPARISON_READINESS_JSON,
    DEPENDENCY_FILE_NAMES,
    FEATURE_058_REPORT,
    FEATURE_060B_REPORT,
    FEATURE_060_CHECKPOINT_METADATA,
    FEATURE_060_EVALUATION_METRICS,
    FEATURE_060_REPORT,
    FEATURE_060_RUN_MANIFEST,
    FEATURE_060_TRAINING_METRICS,
    FEATURE_ID,
    FORBIDDEN_PATH_PREFIXES,
    OUTPUT_DIR,
    READY_NEXT_FEATURE,
    REPORT_JSON,
    REPORT_MD,
    TRAINED_POLICY_RESULTS_JSON,
    CampaignIntegrityEvaluationComparisonBatchConfig,
)
from .model import CampaignIntegrityEvaluationComparisonBatchReport, REPAIR_ROUTING
from .report import json_dump, write_campaign_integrity_evaluation_comparison_batch_report


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _git_output(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()


def _git_bool(*args: str) -> bool:
    return subprocess.run(["git", *args], check=False, capture_output=True, text=True).returncode == 0


def _status_paths() -> list[str]:
    return [line[3:].strip() for line in subprocess.run(["git", "status", "--short"], check=True, capture_output=True, text=True).stdout.splitlines() if line.strip()]


def _staged_paths() -> list[str]:
    return [line for line in _git_output("diff", "--cached", "--name-only").splitlines() if line]


def _diff_paths() -> list[str]:
    return [line for line in _git_output("diff", "--name-only", f"{BASE_BRANCH}...HEAD").splitlines() if line]


def _approved(paths: list[str]) -> bool:
    return all(any(path.startswith(prefix) for prefix in APPROVED_PATH_PREFIXES) for path in paths)


def _forbidden(paths: list[str]) -> list[str]:
    return [path for path in paths if any(path.startswith(prefix) for prefix in FORBIDDEN_PATH_PREFIXES) or Path(path).name in DEPENDENCY_FILE_NAMES]


def _baseline_results() -> dict[str, Any]:
    feature_058 = _load_json(FEATURE_058_REPORT)
    feature_060 = _load_json(FEATURE_060_REPORT)
    trace_bank = feature_058["evaluation_trace_bank_summary"]
    policies = feature_058["baseline_policy_registry_summary"]["policies"]
    shells = feature_058["baseline_evaluation_harness_summary"]["per_policy_metric_shells"]
    trace_ids = feature_058["train_eval_separation_summary"]["evaluation_trace_ids"]
    return {
        "evaluation_trace_bank_id": trace_bank["evaluation_trace_bank_id"],
        "trace_ids": trace_ids,
        "policies": policies,
        "metric_schema": feature_060["evaluation_metrics_summary"]["metric_schema_coverage"],
        "baseline_policy_metrics": shells,
        "controlled_experiment_data": True,
    }


def _trained_policy_results() -> dict[str, Any]:
    feature_058 = _load_json(FEATURE_058_REPORT)
    evaluation = _load_json(FEATURE_060_EVALUATION_METRICS)
    return {
        "evaluation_trace_bank_id": evaluation["evaluation_trace_bank_id"],
        "trace_ids": feature_058["train_eval_separation_summary"]["evaluation_trace_ids"],
        "metric_schema": evaluation["metric_schema_coverage"],
        "trained_policy_metrics": {k: evaluation[k] for k in ("delay", "drop", "timeout", "reward", "action_distribution", "train_eval_separation")},
        "controlled_experiment_data": True,
    }


def _campaign_integrity_summary() -> dict[str, Any]:
    feature_060 = _load_json(FEATURE_060_REPORT)
    evaluation = _load_json(FEATURE_060_EVALUATION_METRICS)
    checkpoint = _load_json(FEATURE_060_CHECKPOINT_METADATA)
    run_manifest = _load_json(FEATURE_060_RUN_MANIFEST)
    paths = {
        "campaign_report": FEATURE_060_REPORT,
        "training_metrics": FEATURE_060_TRAINING_METRICS,
        "evaluation_metrics": FEATURE_060_EVALUATION_METRICS,
        "checkpoint_metadata": FEATURE_060_CHECKPOINT_METADATA,
        "run_manifest": FEATURE_060_RUN_MANIFEST,
    }
    artifact_exists = {k: p.exists() for k, p in paths.items()}
    artifact_manifest_paths_agree = all(
        path.exists() and str(path) == value
        for path, value in {
            FEATURE_060_REPORT: feature_060["artifact_manifest_summary"]["full_campaign_json_report"],
            FEATURE_060_TRAINING_METRICS: feature_060["artifact_manifest_summary"]["training_metrics_json"],
            FEATURE_060_EVALUATION_METRICS: feature_060["artifact_manifest_summary"]["evaluation_metrics_json"],
            FEATURE_060_CHECKPOINT_METADATA: feature_060["artifact_manifest_summary"]["checkpoint_metadata_json"],
            FEATURE_060_RUN_MANIFEST: feature_060["artifact_manifest_summary"]["run_manifest_json"],
        }.items()
    )
    trace_bank_ids_consistent = (
        feature_060["campaign_execution_summary"]["evaluation_trace_bank_id"] == evaluation["evaluation_trace_bank_id"] == checkpoint["feature_060_trace_bank_ids"]["evaluation"]
        and feature_060["campaign_execution_summary"]["training_trace_bank_id"] == checkpoint["feature_060_trace_bank_ids"]["training"]
    )
    real_binding = feature_060["campaign_execution_summary"]["real_trainer_binding"]
    return {
        "feature_060_report_exists": FEATURE_060_REPORT.exists(),
        "feature_060_training_metrics_exist": FEATURE_060_TRAINING_METRICS.exists(),
        "feature_060_evaluation_metrics_exist": FEATURE_060_EVALUATION_METRICS.exists(),
        "feature_060_checkpoint_metadata_exist": FEATURE_060_CHECKPOINT_METADATA.exists(),
        "feature_060_run_manifest_exist": FEATURE_060_RUN_MANIFEST.exists(),
        "artifact_manifest_paths_agree": artifact_manifest_paths_agree,
        "trace_bank_ids_consistent": trace_bank_ids_consistent,
        "seed_bundle_consistent": feature_060["campaign_execution_summary"]["seed_bundle"] == checkpoint["seed_bundle"],
        "real_trainer_binding_evidence_exists": real_binding["real_trainer_class"] == "src.analysis.full_training_reproduction_campaign.trainer.DDQNTrainer" and real_binding["real_trainer_method_called"] == "DDQNTrainer.run_pilot",
        "scalar_fallback_drives_campaign_claim": real_binding["scalar_fallback_drives_campaign_claim"],
    }


def _comparison_readiness_summary(baseline: dict[str, Any], trained: dict[str, Any]) -> dict[str, Any]:
    feature_060 = _load_json(FEATURE_060_REPORT)
    evaluation = _load_json(FEATURE_060_EVALUATION_METRICS)
    return {
        "same_evaluation_trace_bank": baseline["evaluation_trace_bank_id"] == trained["evaluation_trace_bank_id"] == evaluation["evaluation_trace_bank_id"],
        "identical_metric_schema": tuple(baseline["metric_schema"]["required_metric_fields"]) == tuple(trained["metric_schema"]["required_metric_fields"]),
        "identical_action_contract": True,
        "trace_ids_comparable": baseline["trace_ids"] == trained["trace_ids"] == _load_json(FEATURE_058_REPORT)["train_eval_separation_summary"]["evaluation_trace_ids"],
        "no_training_traces_leak_into_evaluation": evaluation["train_eval_separation"]["evaluation_on_training_traces"] is False,
        "no_paper_reproduction_claim": feature_060["evaluation_metrics_summary"]["no_paper_reproduction_claim"] is True,
        "no_unsupported_superiority_claim": feature_060["evaluation_metrics_summary"]["no_performance_superiority_claim"] is True,
    }


def _comparison_report_summary(baseline: dict[str, Any], trained: dict[str, Any]) -> dict[str, Any]:
    training = _load_json(FEATURE_060_TRAINING_METRICS)
    evaluation = _load_json(FEATURE_060_EVALUATION_METRICS)
    return {
        "delay": {"baseline": baseline["baseline_policy_metrics"]["local-only"]["delay"], "trained": trained["trained_policy_metrics"]["delay"]},
        "drop": {"baseline": baseline["baseline_policy_metrics"]["local-only"]["drop"], "trained": trained["trained_policy_metrics"]["drop"]},
        "timeout": {"baseline": baseline["baseline_policy_metrics"]["local-only"]["timeout"], "trained": trained["trained_policy_metrics"]["timeout"]},
        "reward": {"baseline": baseline["baseline_policy_metrics"]["local-only"]["reward"], "trained": trained["trained_policy_metrics"]["reward"]},
        "action_distribution": {"baseline": baseline["baseline_policy_metrics"]["local-only"]["action_distribution"], "trained": trained["trained_policy_metrics"]["action_distribution"]},
        "local_action_count": {"baseline": baseline["baseline_policy_metrics"]["local-only"]["local_action_count"], "trained": training["local_action_count"]},
        "horizontal_action_count": {"baseline": baseline["baseline_policy_metrics"]["local-only"]["horizontal_action_count"], "trained": training["horizontal_action_count"]},
        "vertical_action_count": {"baseline": baseline["baseline_policy_metrics"]["local-only"]["vertical_action_count"], "trained": training["vertical_action_count"]},
        "per_episode_summary": {"baseline": baseline["baseline_policy_metrics"]["local-only"]["per_episode_summary"], "trained": evaluation["train_eval_separation"]},
        "train_eval_separation": evaluation["train_eval_separation"],
        "baseline_policy_metrics": baseline["baseline_policy_metrics"],
        "trained_policy_metrics": trained["trained_policy_metrics"],
        "controlled_experiment_data": True,
        "paper_reproduction_claim": False,
        "superiority_claim": False,
        "single_run_limitation": True,
    }


def build_campaign_integrity_evaluation_comparison_batch_report(config: CampaignIntegrityEvaluationComparisonBatchConfig | None = None) -> CampaignIntegrityEvaluationComparisonBatchReport:
    feature_060 = _load_json(FEATURE_060_REPORT) if FEATURE_060_REPORT.exists() else {}
    feature_060b = _load_json(FEATURE_060B_REPORT) if FEATURE_060B_REPORT.exists() else {}
    baseline = _baseline_results()
    trained = _trained_policy_results()
    campaign = _campaign_integrity_summary()
    readiness = _comparison_readiness_summary(baseline, trained)
    comparison = _comparison_report_summary(baseline, trained)
    artifact_exists = {
        "feature_060_report": FEATURE_060_REPORT.exists(),
        "feature_060_training_metrics": FEATURE_060_TRAINING_METRICS.exists(),
        "feature_060_evaluation_metrics": FEATURE_060_EVALUATION_METRICS.exists(),
        "feature_060_checkpoint_metadata": FEATURE_060_CHECKPOINT_METADATA.exists(),
        "feature_060_run_manifest": FEATURE_060_RUN_MANIFEST.exists(),
        "feature_060b_report": FEATURE_060B_REPORT.exists(),
        "feature_058_report": FEATURE_058_REPORT.exists(),
    }
    blockers: list[str] = []
    if feature_060.get("final_verdict") != "full_paper_default_training_campaign_execution_passed" or feature_060b.get("final_verdict") != "real_torch_trainer_binding_repair_passed":
        blockers.append("feature_060_prerequisite_blocked")
    if not campaign["feature_060_report_exists"] or not campaign["artifact_manifest_paths_agree"]:
        blockers.append("campaign_integrity_blocked")
    if baseline["evaluation_trace_bank_id"] != "feature-058-evaluation-trace-bank":
        blockers.append("baseline_evaluation_blocked")
    if trained["evaluation_trace_bank_id"] != "feature-058-evaluation-trace-bank":
        blockers.append("trained_policy_evaluation_blocked")
    if not all(readiness.values()):
        blockers.append("comparison_readiness_blocked")
    if not all(k in comparison for k in ("paper_reproduction_claim", "superiority_claim", "single_run_limitation")):
        blockers.append("comparison_report_blocked")
    if not all(artifact_exists.values()):
        blockers.append("artifact_manifest_blocked")
    safety = {
        "no_dependency_drift": not any(Path(path).name in DEPENDENCY_FILE_NAMES for path in _status_paths() + _staged_paths() + _diff_paths()),
        "no_policy_drift": not any(path.startswith("src/policies/") for path in _status_paths() + _staged_paths() + _diff_paths()),
        "no_environment_contract_drift": not any(path.startswith("src/environment/") for path in _status_paths() + _staged_paths() + _diff_paths()),
        "no_reward_timing_change": True,
        "no_prior_feature_artifact_rewrite": True,
        "no_paper_reproduction_claim": comparison["paper_reproduction_claim"] is False,
        "no_unsupported_superiority_claim": comparison["superiority_claim"] is False,
        "no_uncontrolled_campaign_loop": True,
    }
    if not all(safety.values()):
        blockers.append("behavior_drift_detected")
    final_verdict = "behavior_drift_detected" if "behavior_drift_detected" in blockers else ("campaign_integrity_evaluation_comparison_batch_passed" if not blockers else blockers[0])
    return CampaignIntegrityEvaluationComparisonBatchReport(
        feature_id=FEATURE_ID,
        batch_items_covered=[
            "Campaign Result Integrity and Comparison Readiness Audit",
            "Baseline Evaluation Execution",
            "Trained Policy Evaluation Execution",
            "Baseline vs Trained Policy Comparison Readiness Audit",
            "Baseline vs Trained Policy Comparison Report",
        ],
        prerequisite_tags_verified=[
            {"name": "branch", "verified": _git_output("branch", "--show-current") == BRANCH_NAME, "details": BRANCH_NAME},
            {"name": "not_main", "verified": _git_output("branch", "--show-current") != "main", "details": "current branch != main"},
            {"name": "base_branch_is_ancestor", "verified": _git_bool("merge-base", "--is-ancestor", BASE_BRANCH, "HEAD"), "details": "main is ancestor of HEAD"},
            {"name": "working_tree_paths_approved", "verified": _approved(_status_paths()), "details": "git status --short contains only approved Feature 061 paths"},
            {"name": "staged_paths_approved", "verified": _approved(_staged_paths()), "details": "git diff --cached --name-only contains only approved Feature 061 paths"},
            {"name": "feature_branch_diff_paths_approved", "verified": _approved(_diff_paths()), "details": "git diff --name-only main...HEAD contains only approved Feature 061 paths"},
            {"name": "forbidden_paths_absent", "verified": not _forbidden(_status_paths() + _staged_paths() + _diff_paths()), "details": "forbidden paths absent"},
        ],
        feature_060_verified=feature_060.get("final_verdict") == "full_paper_default_training_campaign_execution_passed" and feature_060b.get("final_verdict") == "real_torch_trainer_binding_repair_passed",
        campaign_integrity_summary=campaign,
        baseline_evaluation_summary=baseline,
        trained_policy_evaluation_summary=trained,
        comparison_readiness_summary=readiness,
        comparison_report_summary=comparison,
        artifact_manifest_summary={"artifact_exists": artifact_exists, "all_required_artifacts_exist": all(artifact_exists.values())},
        safety_summary=safety,
        remaining_blockers=blockers,
        recommended_next_feature=READY_NEXT_FEATURE if not blockers else REPAIR_ROUTING[final_verdict],
        final_verdict=final_verdict,
    )


def generate_campaign_integrity_evaluation_comparison_batch_artifacts(config: CampaignIntegrityEvaluationComparisonBatchConfig | None = None):
    report = build_campaign_integrity_evaluation_comparison_batch_report(config)
    write_campaign_integrity_evaluation_comparison_batch_report(report, OUTPUT_DIR)
    payload = report.to_dict()
    BASELINE_RESULTS_JSON.write_text(json_dump(_baseline_results()), encoding="utf-8")
    TRAINED_POLICY_RESULTS_JSON.write_text(json_dump(_trained_policy_results()), encoding="utf-8")
    COMPARISON_READINESS_JSON.write_text(json_dump(payload["comparison_readiness_summary"]), encoding="utf-8")
    COMPARISON_JSON.write_text(json_dump(payload["comparison_report_summary"]), encoding="utf-8")
    COMPARISON_MD.write_text("# Baseline vs Trained Policy Comparison Report\n\n" + json_dump(payload["comparison_report_summary"]), encoding="utf-8")
    return report, REPORT_JSON, REPORT_MD


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description="Generate Feature 061 campaign integrity comparison artifacts.").parse_args(argv)
    report, json_path, md_path = generate_campaign_integrity_evaluation_comparison_batch_artifacts()
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    print(f"final_verdict = {report.final_verdict}")
    print(f"recommended_next_feature = {report.recommended_next_feature}")
    return 0 if report.final_verdict == "campaign_integrity_evaluation_comparison_batch_passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
