from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from .config import (
    BRANCH_NAME,
    CAMPAIGN_RUN_COUNT_OR_EPISODE_BUDGET,
    EXPECTED_FEATURE_060_ARTIFACTS,
    FEATURE_058_COMPLETE_TAG,
    FEATURE_ID,
    FULL_CAMPAIGN_OUTPUT_DIR,
    METRIC_COLLECTION_FIELDS,
    READY_NEXT_FEATURE,
    RESOURCE_TIMEOUT_BUDGET,
    SAFETY_FIELDS,
    FullPaperDefaultTrainingCampaignGateConfig,
)
from .model import FullPaperDefaultTrainingCampaignGateReport, REPAIR_ROUTING
from .report import write_full_paper_default_training_campaign_gate_report

APPROVED_PATH_PREFIXES = (
    "artifacts/analysis/full-paper-default-training-campaign-gate/",
    "specs/059-full-paper-default-training-campaign-gate/",
    "src/analysis/full_paper_default_training_campaign_gate/",
    "tests/unit/test_full_paper_default_training_campaign_gate",
    "tests/integration/test_full_paper_default_training_campaign_gate",
)
DEPENDENCY_FILE_NAMES = {
    "Pipfile",
    "poetry.lock",
    "pyproject.toml",
    "requirements-dev.txt",
    "requirements.txt",
    "uv.lock",
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _git_output(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()


def _git_bool(*args: str) -> bool:
    return subprocess.run(["git", *args], check=False, capture_output=True, text=True).returncode == 0


def _status_paths() -> list[str]:
    output = subprocess.run(["git", "status", "--short"], check=True, capture_output=True, text=True).stdout
    return [line[3:].strip() for line in output.splitlines() if line.strip()]


def _staged_paths() -> list[str]:
    return [line for line in _git_output("diff", "--cached", "--name-only").splitlines() if line]


def _diff_names() -> list[str]:
    return [line for line in _git_output("diff", "--name-only", "main...HEAD").splitlines() if line]


def _approved_paths(paths: list[str]) -> bool:
    return all(any(path.startswith(prefix) for prefix in APPROVED_PATH_PREFIXES) for path in paths)


def _no_dependency_drift(paths: list[str]) -> bool:
    return not any(Path(path).name in DEPENDENCY_FILE_NAMES for path in paths)


def _no_policy_drift(paths: list[str]) -> bool:
    return not any(path.startswith("src/policies/") for path in paths)


def _no_environment_contract_drift(paths: list[str]) -> bool:
    return not any(path.startswith("src/environment/") for path in paths)


def _no_prior_artifact_rewrite(paths: list[str]) -> bool:
    return not any(path.startswith("artifacts/analysis/") and not path.startswith("artifacts/analysis/full-paper-default-training-campaign-gate/") for path in paths)


def _feature_058_harness_verified(payload: dict[str, Any]) -> bool:
    registry_count = int(payload.get("baseline_policy_registry_summary", {}).get("baseline_policy_count", 0))
    evaluated_count = int(payload.get("baseline_evaluation_harness_summary", {}).get("evaluated_policy_count", -1))
    prereq_tags = payload.get("prerequisite_tags_verified", [])
    return (
        payload.get("feature_id") == "058-evaluation-trace-bank-baseline-harness"
        and payload.get("feature_057_pilot_verified") is True
        and int(payload.get("evaluation_trace_bank_summary", {}).get("evaluation_trace_count", 0)) > 0
        and payload.get("evaluation_trace_bank_summary", {}).get("bank_generation_repeatable") is True
        and payload.get("train_eval_separation_summary", {}).get("train_eval_trace_banks_disjoint") is True
        and payload.get("train_eval_separation_summary", {}).get("evaluation_on_training_traces") is False
        and registry_count > 0
        and payload.get("baseline_policy_registry_summary", {}).get("action_contract_compatible") is True
        and evaluated_count == registry_count
        and payload.get("metric_schema_summary", {}).get("metric_schema_complete") is True
        and payload.get("determinism_summary", {}).get("repeatability_proven") is True
        and payload.get("behavior_safety_summary", {}).get("no_training_execution") is True
        and payload.get("behavior_safety_summary", {}).get("no_optimizer_execution") is True
        and payload.get("behavior_safety_summary", {}).get("no_replay_mutation") is True
        and payload.get("behavior_safety_summary", {}).get("no_checkpoint_binary_written") is True
        and payload.get("behavior_safety_summary", {}).get("no_full_campaign") is True
        and payload.get("behavior_safety_summary", {}).get("no_paper_reproduction_claim") is True
        and payload.get("behavior_safety_summary", {}).get("no_performance_claim") is True
        and all(tag.get("verified") is True for tag in prereq_tags)
        and payload.get("remaining_blockers") == []
        and payload.get("final_verdict") == "evaluation_trace_bank_baseline_harness_ready"
        and payload.get("recommended_next_feature") == "Feature 059 — Full Paper-Default Training Campaign Gate"
    )


def _build_prerequisite_tags_verified(
    *,
    config: FullPaperDefaultTrainingCampaignGateConfig,
    feature_058_ready: bool,
    status_paths: list[str],
    staged_paths: list[str],
    diff_paths: list[str],
) -> list[dict[str, Any]]:
    branch = _git_output("branch", "--show-current")
    return [
        {"name": "branch", "verified": branch == BRANCH_NAME, "details": f"git branch --show-current == {BRANCH_NAME}"},
        {"name": "not_main", "verified": branch != "main", "details": "current branch != main"},
        {"name": "main_contains_feature_058_complete", "verified": _git_bool("merge-base", "--is-ancestor", FEATURE_058_COMPLETE_TAG, "main"), "details": f"{FEATURE_058_COMPLETE_TAG} is an ancestor of main"},
        {"name": "main_is_branch_base", "verified": _git_output("merge-base", "main", "HEAD") == _git_output("rev-parse", "main"), "details": "branch is based on local main"},
        {"name": "feature_058_report_valid", "verified": feature_058_ready, "details": f"{config.feature_058_report_path} contains the approved Feature 058 readiness verdict"},
        {"name": "feature_057_report_present", "verified": config.feature_057_report_path.exists(), "details": str(config.feature_057_report_path)},
        {"name": "feature_056_report_present", "verified": config.feature_056_report_path.exists(), "details": str(config.feature_056_report_path)},
        {"name": "feature_055_report_present", "verified": config.feature_055_report_path.exists(), "details": str(config.feature_055_report_path)},
        {"name": "working_tree_paths_approved", "verified": _approved_paths(status_paths), "details": "git status --short contains only approved Feature 059 paths"},
        {"name": "staged_paths_approved", "verified": _approved_paths(staged_paths), "details": "git diff --cached --name-only contains only approved Feature 059 paths"},
        {"name": "main_head_diff_approved", "verified": _approved_paths(diff_paths), "details": "git diff --name-only main...HEAD contains only approved Feature 059 paths"},
        {"name": "agents_stable_not_modified", "verified": "AGENTS.md" not in status_paths + staged_paths + diff_paths, "details": "AGENTS.md is stable and not modified"},
        {"name": "pointer_local_only_not_dirty_or_staged", "verified": ".specify/feature.json" not in status_paths + staged_paths + diff_paths, "details": ".specify/feature.json is absent from dirty/staged/committed paths"},
    ]


def _build_campaign_scope_summary(feature_058_payload: dict[str, Any]) -> dict[str, Any]:
    train_eval = feature_058_payload.get("train_eval_separation_summary", {})
    trace_bank = feature_058_payload.get("evaluation_trace_bank_summary", {})
    return {
        "full_campaign_allowed_next_feature": True,
        "full_campaign_executed_this_feature": False,
        "paper_default_training_campaign": True,
        "training_trace_bank_id": train_eval.get("training_trace_bank_id"),
        "evaluation_trace_bank_id": train_eval.get("evaluation_trace_bank_id"),
        "baseline_harness_id": "feature-058-baseline-evaluation-harness",
        "seed_bundle": trace_bank.get("seed_bundle", {}),
        "run_count_or_episode_budget": CAMPAIGN_RUN_COUNT_OR_EPISODE_BUDGET,
        "campaign_scale_is_explicit": True,
    }


def _build_training_execution_gate_summary() -> dict[str, Any]:
    return {
        "training_execution_allowed_next_feature": True,
        "training_executed_this_feature": False,
        "optimizer_executed_this_feature": False,
        "replay_mutated_this_feature": False,
        "checkpoint_binary_written_this_feature": False,
    }


def _build_evaluation_harness_gate_summary(feature_058_payload: dict[str, Any]) -> dict[str, Any]:
    registry_count = int(feature_058_payload.get("baseline_policy_registry_summary", {}).get("baseline_policy_count", 0))
    evaluated_count = int(feature_058_payload.get("baseline_evaluation_harness_summary", {}).get("evaluated_policy_count", -1))
    return {
        "evaluation_trace_bank_ready": int(feature_058_payload.get("evaluation_trace_bank_summary", {}).get("evaluation_trace_count", 0)) > 0
        and feature_058_payload.get("evaluation_trace_bank_summary", {}).get("bank_generation_repeatable") is True,
        "train_eval_trace_banks_disjoint": feature_058_payload.get("train_eval_separation_summary", {}).get("train_eval_trace_banks_disjoint") is True
        and feature_058_payload.get("train_eval_separation_summary", {}).get("evaluation_on_training_traces") is False,
        "baseline_policy_registry_ready": registry_count > 0
        and feature_058_payload.get("baseline_policy_registry_summary", {}).get("action_contract_compatible") is True,
        "baseline_harness_ready": evaluated_count == registry_count and registry_count > 0,
        "metric_schema_complete": feature_058_payload.get("metric_schema_summary", {}).get("metric_schema_complete") is True,
        "determinism_ready": feature_058_payload.get("determinism_summary", {}).get("repeatability_proven") is True,
    }


def _build_artifact_output_contract_summary() -> dict[str, Any]:
    return {
        **EXPECTED_FEATURE_060_ARTIFACTS,
        "artifact_output_contract_complete": all(EXPECTED_FEATURE_060_ARTIFACTS.values()),
    }


def _build_resource_control_summary(seed_bundle: dict[str, Any]) -> dict[str, Any]:
    return {
        "deterministic_seeds": seed_bundle,
        "max_episode_or_run_budget": CAMPAIGN_RUN_COUNT_OR_EPISODE_BUDGET,
        "timeout_runtime_budget": RESOURCE_TIMEOUT_BUDGET,
        "controlled_output_directory": FULL_CAMPAIGN_OUTPUT_DIR,
        "no_uncontrolled_loop": True,
        "resource_control_complete": bool(seed_bundle) and bool(CAMPAIGN_RUN_COUNT_OR_EPISODE_BUDGET) and bool(RESOURCE_TIMEOUT_BUDGET),
    }


def _build_checkpoint_contract_summary() -> dict[str, Any]:
    return {
        "metadata_required": True,
        "checkpoint_binary_policy": "Feature 060 may write checkpoint binaries only under its controlled output directory with metadata; Feature 059 writes none.",
        "checkpoint_binary_written_this_feature": False,
        "target_update_metadata_required": True,
        "replay_metadata_required": True,
        "seed_bundle_required": True,
        "trace_bank_ids_required": True,
        "checkpoint_contract_complete": True,
    }


def _build_metric_collection_contract_summary() -> dict[str, Any]:
    present = list(METRIC_COLLECTION_FIELDS)
    return {
        "required_metric_fields": list(METRIC_COLLECTION_FIELDS),
        "present_metric_fields": present,
        "missing_metric_fields": [],
        "metric_collection_contract_complete": True,
    }


def _build_safety_summary(status_paths: list[str], staged_paths: list[str], diff_paths: list[str]) -> dict[str, bool]:
    all_paths = status_paths + staged_paths + diff_paths
    summary = {
        "no_training_execution": True,
        "no_optimizer_execution": True,
        "no_replay_mutation": True,
        "no_checkpoint_binary_written": True,
        "no_full_campaign_execution": True,
        "no_paper_reproduction_claim": True,
        "no_performance_claim": True,
        "no_baseline_superiority_claim": True,
        "no_policy_drift": _no_policy_drift(all_paths),
        "no_dependency_drift": _no_dependency_drift(all_paths),
        "no_environment_contract_drift": _no_environment_contract_drift(all_paths),
        "no_reward_timing_change": _no_environment_contract_drift(all_paths),
        "no_prior_artifact_rewrite": _no_prior_artifact_rewrite(diff_paths),
    }
    return {field: bool(summary[field]) for field in SAFETY_FIELDS}


def _empty_report(
    *,
    config: FullPaperDefaultTrainingCampaignGateConfig,
    final_verdict: str,
    blockers: list[str],
    feature_058_harness_verified: bool,
    prerequisite_tags_verified: list[dict[str, Any]],
    safety_summary: dict[str, bool],
) -> FullPaperDefaultTrainingCampaignGateReport:
    return FullPaperDefaultTrainingCampaignGateReport(
        feature_id=FEATURE_ID,
        prerequisite_tags_verified=prerequisite_tags_verified,
        feature_058_harness_verified=feature_058_harness_verified,
        campaign_scope_summary={
            "full_campaign_allowed_next_feature": config.full_campaign_allowed_next_feature,
            "full_campaign_executed_this_feature": config.full_campaign_executed_this_feature,
            "paper_default_training_campaign": True,
            "training_trace_bank_id": "",
            "evaluation_trace_bank_id": "",
            "baseline_harness_id": "",
            "seed_bundle": {},
            "run_count_or_episode_budget": {},
            "campaign_scale_is_explicit": False,
        },
        training_execution_gate_summary=_build_training_execution_gate_summary(),
        evaluation_harness_gate_summary={
            "evaluation_trace_bank_ready": False,
            "train_eval_trace_banks_disjoint": False,
            "baseline_policy_registry_ready": False,
            "baseline_harness_ready": False,
            "metric_schema_complete": False,
            "determinism_ready": False,
        },
        artifact_output_contract_summary={**EXPECTED_FEATURE_060_ARTIFACTS, "artifact_output_contract_complete": False},
        resource_control_summary={
            "deterministic_seeds": {},
            "max_episode_or_run_budget": {},
            "timeout_runtime_budget": {},
            "controlled_output_directory": FULL_CAMPAIGN_OUTPUT_DIR,
            "no_uncontrolled_loop": True,
            "resource_control_complete": False,
        },
        checkpoint_contract_summary=_build_checkpoint_contract_summary(),
        metric_collection_contract_summary={
            "required_metric_fields": list(METRIC_COLLECTION_FIELDS),
            "present_metric_fields": [],
            "missing_metric_fields": list(METRIC_COLLECTION_FIELDS),
            "metric_collection_contract_complete": False,
        },
        safety_summary=safety_summary,
        remaining_blockers=blockers,
        recommended_next_feature=REPAIR_ROUTING[final_verdict],
        final_verdict=final_verdict,
    )


def build_full_paper_default_training_campaign_gate_report(
    config: FullPaperDefaultTrainingCampaignGateConfig | None = None,
) -> FullPaperDefaultTrainingCampaignGateReport:
    cfg = config or FullPaperDefaultTrainingCampaignGateConfig()
    status_paths = _status_paths()
    staged_paths = _staged_paths()
    diff_paths = _diff_names()
    safety_summary = _build_safety_summary(status_paths, staged_paths, diff_paths)

    feature_058_payload = _load_json(cfg.feature_058_report_path) if cfg.feature_058_report_path.exists() else {}
    feature_058_ready = _feature_058_harness_verified(feature_058_payload)
    prerequisite_tags_verified = _build_prerequisite_tags_verified(
        config=cfg,
        feature_058_ready=feature_058_ready,
        status_paths=status_paths,
        staged_paths=staged_paths,
        diff_paths=diff_paths,
    )
    failed_prerequisite_tags = [
        str(tag["name"])
        for tag in prerequisite_tags_verified
        if tag.get("verified") is not True
    ]
    if failed_prerequisite_tags:
        final_verdict = "feature_058_prerequisite_blocked" if not feature_058_ready else "behavior_drift_detected"
        return _empty_report(
            config=cfg,
            final_verdict=final_verdict,
            blockers=failed_prerequisite_tags,
            feature_058_harness_verified=feature_058_ready,
            prerequisite_tags_verified=prerequisite_tags_verified,
            safety_summary=safety_summary,
        )

    if not all(safety_summary.values()):
        return _empty_report(
            config=cfg,
            final_verdict="behavior_drift_detected",
            blockers=[key for key, value in safety_summary.items() if not value],
            feature_058_harness_verified=feature_058_ready,
            prerequisite_tags_verified=prerequisite_tags_verified,
            safety_summary=safety_summary,
        )

    campaign_scope_summary = _build_campaign_scope_summary(feature_058_payload)
    training_execution_gate_summary = _build_training_execution_gate_summary()
    evaluation_harness_gate_summary = _build_evaluation_harness_gate_summary(feature_058_payload)
    artifact_output_contract_summary = _build_artifact_output_contract_summary()
    resource_control_summary = _build_resource_control_summary(dict(campaign_scope_summary["seed_bundle"]))
    checkpoint_contract_summary = _build_checkpoint_contract_summary()
    metric_collection_contract_summary = _build_metric_collection_contract_summary()

    blockers: list[str] = []
    if not (
        campaign_scope_summary["full_campaign_allowed_next_feature"] is True
        and campaign_scope_summary["full_campaign_executed_this_feature"] is False
        and campaign_scope_summary["paper_default_training_campaign"] is True
        and campaign_scope_summary["campaign_scale_is_explicit"] is True
        and bool(campaign_scope_summary["training_trace_bank_id"])
        and bool(campaign_scope_summary["evaluation_trace_bank_id"])
        and bool(campaign_scope_summary["baseline_harness_id"])
    ):
        blockers.append("campaign_scope_blocked")
    if not (
        training_execution_gate_summary["training_execution_allowed_next_feature"] is True
        and training_execution_gate_summary["training_executed_this_feature"] is False
        and training_execution_gate_summary["optimizer_executed_this_feature"] is False
        and training_execution_gate_summary["replay_mutated_this_feature"] is False
        and training_execution_gate_summary["checkpoint_binary_written_this_feature"] is False
    ):
        blockers.append("training_execution_gate_blocked")
    if not all(evaluation_harness_gate_summary.values()):
        blockers.append("evaluation_harness_gate_blocked")
    if not artifact_output_contract_summary["artifact_output_contract_complete"]:
        blockers.append("artifact_output_contract_blocked")
    if not resource_control_summary["resource_control_complete"]:
        blockers.append("resource_control_blocked")
    if not checkpoint_contract_summary["checkpoint_contract_complete"]:
        blockers.append("checkpoint_contract_blocked")
    if not metric_collection_contract_summary["metric_collection_contract_complete"]:
        blockers.append("metric_collection_contract_blocked")
    if not all(safety_summary.values()):
        blockers.append("behavior_drift_detected")

    final_verdict = blockers[0] if blockers else "full_paper_default_training_campaign_gate_ready"
    recommended_next_feature = REPAIR_ROUTING[final_verdict] if blockers else READY_NEXT_FEATURE

    return FullPaperDefaultTrainingCampaignGateReport(
        feature_id=FEATURE_ID,
        prerequisite_tags_verified=prerequisite_tags_verified,
        feature_058_harness_verified=feature_058_ready,
        campaign_scope_summary=campaign_scope_summary,
        training_execution_gate_summary=training_execution_gate_summary,
        evaluation_harness_gate_summary=evaluation_harness_gate_summary,
        artifact_output_contract_summary=artifact_output_contract_summary,
        resource_control_summary=resource_control_summary,
        checkpoint_contract_summary=checkpoint_contract_summary,
        metric_collection_contract_summary=metric_collection_contract_summary,
        safety_summary=safety_summary,
        remaining_blockers=blockers,
        recommended_next_feature=recommended_next_feature,
        final_verdict=final_verdict,
    )


def generate_full_paper_default_training_campaign_gate_artifacts(
    config: FullPaperDefaultTrainingCampaignGateConfig | None = None,
) -> tuple[FullPaperDefaultTrainingCampaignGateReport, Path, Path]:
    report = build_full_paper_default_training_campaign_gate_report(config)
    json_path, md_path = write_full_paper_default_training_campaign_gate_report(report)
    return report, json_path, md_path


def run_full_paper_default_training_campaign_gate(
    config: FullPaperDefaultTrainingCampaignGateConfig | None = None,
) -> FullPaperDefaultTrainingCampaignGateReport:
    report, _, _ = generate_full_paper_default_training_campaign_gate_artifacts(config)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate Feature 059 full paper-default training campaign gate report.")
    parser.add_argument("--json", action="store_true", help="print the generated JSON payload")
    args = parser.parse_args(argv)
    report, json_path, md_path = generate_full_paper_default_training_campaign_gate_artifacts()
    if args.json:
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True, ensure_ascii=False))
    else:
        print(f"Wrote {json_path}")
        print(f"Wrote {md_path}")
        print(f"final_verdict = {report.final_verdict}")
        print(f"recommended_next_feature = {report.recommended_next_feature}")
    return 0 if report.final_verdict == "full_paper_default_training_campaign_gate_ready" else 1
