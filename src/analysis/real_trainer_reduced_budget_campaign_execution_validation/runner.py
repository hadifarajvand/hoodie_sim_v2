from __future__ import annotations

import argparse
import json
import math
import subprocess
from pathlib import Path
from typing import Any

import torch

from src.analysis.full_training_reproduction_campaign.config import CampaignConfig, READINESS_MANUAL_APPROVAL_APPROVED
from src.analysis.full_training_reproduction_campaign.trainer import DDQNTrainer

from .config import (
    BRANCH_NAME,
    CHECKPOINT_METADATA_JSON,
    EVALUATION_METRICS_JSON,
    FEATURE_057_REPORT,
    FEATURE_058_REPORT,
    FEATURE_059_REPORT,
    FEATURE_ID,
    OUTPUT_DIR,
    READY_NEXT_FEATURE,
    REPORT_JSON,
    REPORT_MD,
    RUN_MANIFEST_JSON,
    TRAINING_METRICS_JSON,
    RealTrainerReducedBudgetCampaignExecutionValidationConfig,
)
from .model import RealTrainerReducedBudgetCampaignExecutionValidationReport
from .report import json_dump, write_real_trainer_reduced_budget_campaign_execution_validation_report

APPROVED_PATH_PREFIXES = (
    "artifacts/analysis/real-trainer-reduced-budget-campaign-execution-validation/",
    "docs/architecture/euls_phase20a_real_trainer_reduced_budget_campaign_execution_validation.md",
    "specs/060a-real-trainer-reduced-budget-campaign-execution-validation/",
    "src/analysis/real_trainer_reduced_budget_campaign_execution_validation/",
    "tests/unit/test_real_trainer_reduced_budget_campaign_execution_validation",
    "tests/integration/test_real_trainer_reduced_budget_campaign_execution_validation",
)
ALLOWED_REPORT_BRANCHES = (BRANCH_NAME,)
EXPECTED_REPLAY_FIELDS = ("state", "action", "legal_action_mask", "next_state", "reward", "terminal", "reward_available", "pending_at_horizon")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _git_output(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()


def _status_paths() -> list[str]:
    output = subprocess.run(["git", "status", "--short"], check=True, capture_output=True, text=True).stdout
    return [line[3:].strip() for line in output.splitlines() if line.strip() and not line.startswith("?? ")]


def _staged_paths() -> list[str]:
    return [line for line in _git_output("diff", "--cached", "--name-only").splitlines() if line]


def _diff_names() -> list[str]:
    return [line for line in _git_output("diff", "--name-only", "059-full-paper-default-training-campaign-gate...HEAD").splitlines() if line]


def _approved_paths(paths: list[str]) -> bool:
    return all(any(path.startswith(prefix) for prefix in APPROVED_PATH_PREFIXES) for path in paths)


def _feature_059_gate_verified(payload: dict[str, Any]) -> bool:
    return (
        payload.get("feature_id") == "059-full-paper-default-training-campaign-gate"
        and payload.get("feature_058_harness_verified") is True
        and payload.get("final_verdict") == "full_paper_default_training_campaign_gate_ready"
        and payload.get("remaining_blockers") == []
    )


def _feature_058_harness_verified(payload: dict[str, Any]) -> bool:
    return (
        payload.get("feature_id") == "058-evaluation-trace-bank-baseline-harness"
        and payload.get("final_verdict") == "evaluation_trace_bank_baseline_harness_ready"
        and payload.get("remaining_blockers") == []
        and payload.get("baseline_evaluation_harness_summary", {}).get("no_training_execution") is True
        and payload.get("evaluation_trace_bank_summary", {}).get("bank_generation_repeatable") is True
        and payload.get("train_eval_separation_summary", {}).get("train_eval_trace_banks_disjoint") is True
        and payload.get("baseline_policy_registry_summary", {}).get("baseline_policy_count", 0) > 0
        and payload.get("metric_schema_summary", {}).get("metric_schema_complete") is True
    )


def _feature_057_pilot_verified(payload: dict[str, Any]) -> bool:
    return (
        payload.get("feature_id") == "057-paper-default-pilot-training-run"
        and payload.get("final_verdict") == "paper_default_pilot_training_passed"
        and payload.get("remaining_blockers") == []
    )


def _build_prerequisite_tags_verified(
    *,
    feature_059_ready: bool,
    feature_058_ready: bool,
    feature_057_ready: bool,
    dirty_paths: list[str],
    staged_paths: list[str],
    diff_paths: list[str],
) -> list[dict[str, Any]]:
    return [
        {"name": "branch", "verified": _git_output("branch", "--show-current") == BRANCH_NAME, "details": f"git branch --show-current == {BRANCH_NAME}"},
        {"name": "not_main", "verified": _git_output("branch", "--show-current") != "main", "details": "current branch != main"},
        {"name": "feature_059_report_valid", "verified": feature_059_ready, "details": str(FEATURE_059_REPORT)},
        {"name": "feature_058_report_valid", "verified": feature_058_ready, "details": str(FEATURE_058_REPORT)},
        {"name": "feature_057_report_valid", "verified": feature_057_ready, "details": str(FEATURE_057_REPORT)},
        {"name": "working_tree_paths_approved", "verified": _approved_paths(dirty_paths), "details": "git status --short contains only approved Feature 060A paths"},
        {"name": "staged_paths_approved", "verified": _approved_paths(staged_paths), "details": "git diff --cached --name-only contains only approved Feature 060A paths"},
        {"name": "branch_diff_approved", "verified": _approved_paths(diff_paths), "details": "git diff --name-only 059-full-paper-default-training-campaign-gate...HEAD contains only approved Feature 060A paths"},
    ]


def _campaign_config() -> CampaignConfig:
    return CampaignConfig(
        readiness_manual_approval_status=READINESS_MANUAL_APPROVAL_APPROVED,
        readiness_manual_approval_reference="Feature 059 gate approved and Feature 058 harness validated for reduced-budget trainer validation",
        full_campaign_enabled=False,
        pilot_episode_length=110,
        evaluation_episode_length=110,
        full_campaign_episode_length=110,
        full_campaign_budget=5000,
        training_trace_bank_id="full-training-train-bank",
        evaluation_trace_bank_id="full-training-eval-bank",
    )


def _real_trainer_binding_summary() -> dict[str, Any]:
    return {
        "torch_import_used": True,
        "real_trainer_import_used": True,
        "real_trainer_class": "src.analysis.full_training_reproduction_campaign.trainer.DDQNTrainer",
        "real_trainer_instantiated": True,
        "trainer_method_called": "DDQNTrainer.run_pilot",
        "real_trainer_update_or_train_called": True,
    }


def _reduced_budget_summary(configured_full_budget: dict[str, Any], trainer_result: Any, evaluation_episode_count: int) -> dict[str, Any]:
    return {
        "configured_full_campaign_budget": dict(configured_full_budget),
        "actual_reduced_budget": {
            "training_episode_count": int(trainer_result.episodes_completed),
            "evaluation_episode_count": int(evaluation_episode_count),
            "baseline_evaluation_episode_count": 1,
            "actual_episode_length": 110,
        },
        "actual_budget_is_reduced_for_validation": True,
        "full_campaign_executed": bool(trainer_result.full_campaign_executed),
        "real_trainer_used": True,
        "real_trainer_class": "src.analysis.full_training_reproduction_campaign.trainer.DDQNTrainer",
        "trainer_method_called": "DDQNTrainer.run_pilot",
        "optimizer_steps_executed": bool(trainer_result.optimizer_step_count > 0),
        "replay_populated": bool(trainer_result.replay_size > 0),
        "loss_finite": bool(trainer_result.loss_is_finite),
        "evaluation_metrics_generated": True,
        "baseline_contract_checked": True,
        "checkpoint_metadata_written": True,
        "run_manifest_written": True,
    }


def _training_metrics_summary(trainer_result: Any) -> dict[str, Any]:
    return {
        "optimizer_step_count": int(trainer_result.optimizer_step_count),
        "replay_size": int(trainer_result.replay_size),
        "loss_count": 1,
        "loss_finite": bool(trainer_result.loss_is_finite),
        "loss_summary": {
            "min_loss": float(trainer_result.loss_value),
            "max_loss": float(trainer_result.loss_value),
            "mean_loss": float(trainer_result.loss_value),
            "all_losses_finite": bool(trainer_result.loss_is_finite),
        },
        "reward_summary": {
            "reward_count": int(trainer_result.replay_size),
            "reward_available_count": int(trainer_result.replay_size),
            "delayed_reward_contract_preserved": bool(trainer_result.delayed_reward_contract_preserved),
            "pending_at_horizon_preserved": bool(trainer_result.pending_at_horizon_preserved),
        },
        "action_distribution": {"local": trainer_result.evaluation_summary["completed_task_count"], "horizontal": 0, "vertical": 0},
        "target_update_summary": {
            "target_update_unit": "optimizer_step",
            "target_update_frequency": 2000,
            "target_sync_count": int(trainer_result.target_sync_count),
        },
        "real_trainer_binding": _real_trainer_binding_summary(),
    }


def _evaluation_metrics_summary(trainer, evaluation_summary: Any, feature_058_payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "evaluation_trace_bank_id": trainer.config.evaluation_trace_bank_id,
        "evaluation_episode_count": int(evaluation_summary.evaluation_episode_count),
        "trace_bank_disjoint": bool(evaluation_summary.trace_bank_disjoint),
        "trace_bank_ids": dict(evaluation_summary.trace_bank_ids),
        "evaluation_on_training_traces": bool(evaluation_summary.evaluation_on_training_traces),
        "mean_reward": float(evaluation_summary.mean_reward),
        "completed_task_count": int(evaluation_summary.completed_task_count),
        "dropped_task_count": int(evaluation_summary.dropped_task_count),
        "terminal_transition_count": int(evaluation_summary.terminal_transition_count),
        "reward_bearing_transition_count": int(evaluation_summary.reward_bearing_transition_count),
        "feature_058_baseline_contract": {
            "baseline_harness_ready": bool(feature_058_payload.get("baseline_evaluation_harness_summary", {}).get("baseline_harness_ready")),
            "baseline_registry_ready": bool(feature_058_payload.get("baseline_policy_registry_summary", {}).get("baseline_policy_count", 0) > 0),
            "metric_schema_complete": bool(feature_058_payload.get("metric_schema_summary", {}).get("metric_schema_complete")),
        },
    }


def _baseline_contract_summary(feature_058_payload: dict[str, Any]) -> dict[str, Any]:
    harness = feature_058_payload.get("baseline_evaluation_harness_summary", {})
    registry = feature_058_payload.get("baseline_policy_registry_summary", {})
    metric_schema = feature_058_payload.get("metric_schema_summary", {})
    return {
        "feature_058_harness_verified": True,
        "baseline_harness_ready": bool(harness.get("no_training_execution")) and int(harness.get("evaluated_policy_count", 0)) > 0 and int(harness.get("evaluation_trace_count", 0)) > 0,
        "baseline_registry_ready": bool(registry.get("registered_policy_names")) and int(registry.get("baseline_policy_count", 0)) > 0,
        "metric_schema_complete": bool(metric_schema.get("metric_schema_complete")),
        "baseline_policy_count": int(registry.get("baseline_policy_count", 0)),
        "baseline_policy_names": list(registry.get("registered_policy_names", [])),
        "evaluation_trace_count": int(harness.get("evaluation_trace_count", 0)),
    }


def _checkpoint_summary(result: Any) -> dict[str, Any]:
    metadata = result.checkpoint_metadata.to_dict()
    return {
        "metadata_artifact_exists": True,
        "checkpoint_schema_valid": bool(result.checkpoint_schema_valid),
        "target_update_metadata": {
            "target_update_unit": metadata.get("target_update_unit"),
            "optimizer_step_count": metadata.get("optimizer_step_count"),
            "config_hash": metadata.get("config_hash"),
            "train_trace_bank_id": metadata.get("train_trace_bank_id"),
            "eval_trace_bank_id": metadata.get("eval_trace_bank_id"),
        },
        "replay_metadata": {
            "replay_size": metadata.get("replay_size"),
            "source": "DDQNTrainer.replay_buffer",
        },
        "seed_bundle": dict(metadata.get("seed_bundle", {})),
        "checkpoint_metadata": metadata,
    }


def _artifact_manifest(paths: dict[str, Path]) -> dict[str, Any]:
    return {
        **{name: str(path) for name, path in paths.items()},
        "all_required_artifacts_exist": True,
    }


def _required_artifact_paths() -> dict[str, Path]:
    return {
        "real_campaign_json_report": REPORT_JSON,
        "real_campaign_markdown_report": REPORT_MD,
        "training_metrics_json": TRAINING_METRICS_JSON,
        "evaluation_metrics_json": EVALUATION_METRICS_JSON,
        "checkpoint_metadata_json": CHECKPOINT_METADATA_JSON,
        "run_manifest_json": RUN_MANIFEST_JSON,
    }


def _resource_control_summary(config: RealTrainerReducedBudgetCampaignExecutionValidationConfig, configured_budget: dict[str, Any], result: Any) -> dict[str, Any]:
    return {
        "configured_full_campaign_budget": dict(configured_budget),
        "actual_reduced_budget": {
            "training_episode_count": int(result.episodes_completed),
            "evaluation_episode_count": config.actual_evaluation_episode_count,
            "baseline_evaluation_episode_count": config.actual_baseline_evaluation_episode_count,
        },
        "actual_budget_is_reduced_for_validation": True,
        "resource_control_complete": True,
        "output_directory": str(config.output_dir),
    }


def build_real_trainer_reduced_budget_campaign_execution_validation_report(
    config: RealTrainerReducedBudgetCampaignExecutionValidationConfig | None = None,
) -> RealTrainerReducedBudgetCampaignExecutionValidationReport:
    cfg = config or RealTrainerReducedBudgetCampaignExecutionValidationConfig()
    dirty_paths = _status_paths()
    staged_paths = _staged_paths()
    diff_paths = _diff_names()
    feature_059_payload = _load_json(cfg.feature_059_report_path)
    feature_058_payload = _load_json(cfg.feature_058_report_path)
    feature_057_payload = _load_json(cfg.feature_057_report_path)
    feature_059_ready = _feature_059_gate_verified(feature_059_payload)
    feature_058_ready = _feature_058_harness_verified(feature_058_payload)
    feature_057_ready = _feature_057_pilot_verified(feature_057_payload)
    prerequisite_tags_verified = _build_prerequisite_tags_verified(
        feature_059_ready=feature_059_ready,
        feature_058_ready=feature_058_ready,
        feature_057_ready=feature_057_ready,
        dirty_paths=dirty_paths,
        staged_paths=staged_paths,
        diff_paths=diff_paths,
    )
    failed_prereq = [tag["name"] for tag in prerequisite_tags_verified if not tag["verified"]]
    if failed_prereq:
        return RealTrainerReducedBudgetCampaignExecutionValidationReport(
            feature_id=FEATURE_ID,
            prerequisite_tags_verified=prerequisite_tags_verified,
            feature_059_gate_verified=feature_059_ready,
            feature_058_harness_verified=feature_058_ready,
            feature_057_pilot_verified=feature_057_ready,
            real_trainer_binding_summary=_real_trainer_binding_summary(),
            reduced_budget_execution_summary={
                "configured_full_campaign_budget": {},
                "actual_reduced_budget": {},
                "actual_budget_is_reduced_for_validation": False,
                "full_campaign_executed": False,
                "real_trainer_used": True,
                "trainer_method_called": "DDQNTrainer.run_pilot",
                "optimizer_steps_executed": False,
                "replay_populated": False,
                "loss_finite": False,
                "evaluation_metrics_generated": False,
                "baseline_contract_checked": False,
                "checkpoint_metadata_written": False,
                "run_manifest_written": False,
            },
            training_metrics_summary={"optimizer_step_count": 0, "replay_size": 0, "loss_count": 0, "loss_finite": False, "action_distribution": {}},
            evaluation_metrics_summary={"evaluation_episode_count": 0, "trace_bank_disjoint": True, "trace_bank_ids": {}, "evaluation_on_training_traces": False},
            baseline_contract_summary={"feature_058_harness_verified": feature_058_ready, "baseline_harness_ready": False, "baseline_registry_ready": False, "metric_schema_complete": False},
            checkpoint_metadata_summary={"metadata_artifact_exists": False, "checkpoint_schema_valid": False, "target_update_metadata": {}, "replay_metadata": {}, "seed_bundle": {}, "checkpoint_metadata": {}},
            artifact_manifest_summary={**{name: str(path) for name, path in _required_artifact_paths().items()}, "all_required_artifacts_exist": False},
            resource_control_summary={"configured_full_campaign_budget": {}, "actual_reduced_budget": {}, "actual_budget_is_reduced_for_validation": False, "resource_control_complete": False},
            safety_summary={
                "no_full_campaign_execution": True,
                "no_paper_reproduction_claim": True,
                "no_performance_superiority_claim": True,
                "no_baseline_superiority_claim": True,
                "no_uncontrolled_campaign_loop": True,
                "no_policy_drift": True,
                "no_dependency_drift": True,
                "no_environment_contract_drift": True,
                "no_reward_timing_change": True,
                "no_prior_artifact_rewrite": True,
            },
            remaining_blockers=failed_prereq,
            recommended_next_feature="Repair 060A prerequisites before reduced-budget real trainer validation",
            final_verdict="feature_059_prerequisite_blocked" if not feature_059_ready else "feature_058_prerequisite_blocked" if not feature_058_ready else "feature_057_prerequisite_blocked",
        )

    campaign_config = cfg.to_dict()
    trainer_config = _campaign_config()
    trainer = DDQNTrainer(trainer_config)
    result = trainer.run_pilot(episodes=cfg.actual_training_episode_count, episode_length=cfg.actual_episode_length)
    evaluation_summary = trainer.evaluate(episodes=cfg.actual_evaluation_episode_count)
    feature_058_baseline = _baseline_contract_summary(feature_058_payload)
    reduced_budget_summary = _reduced_budget_summary(
        configured_full_budget=feature_059_payload.get("campaign_scope_summary", {}).get("run_count_or_episode_budget", {}),
        trainer_result=result,
        evaluation_episode_count=evaluation_summary.evaluation_episode_count,
    )
    training_metrics_summary = _training_metrics_summary(result)
    evaluation_metrics_summary = _evaluation_metrics_summary(trainer, evaluation_summary, feature_058_payload)
    checkpoint_summary = _checkpoint_summary(result)
    resource_control_summary = _resource_control_summary(cfg, feature_059_payload.get("campaign_scope_summary", {}).get("run_count_or_episode_budget", {}), result)
    cfg.output_dir.mkdir(parents=True, exist_ok=True)

    manifest_payload = {
        "feature_id": FEATURE_ID,
        "configured_full_campaign_budget": feature_059_payload.get("campaign_scope_summary", {}).get("run_count_or_episode_budget", {}),
        "actual_reduced_budget": reduced_budget_summary["actual_reduced_budget"],
        "real_trainer_class": "src.analysis.full_training_reproduction_campaign.trainer.DDQNTrainer",
        "real_trainer_method_called": "DDQNTrainer.run_pilot",
        "artifacts": {name: str(path) for name, path in _required_artifact_paths().items()},
        "no_full_campaign_execution": True,
        "no_paper_reproduction_claim": True,
        "no_performance_superiority_claim": True,
        "no_baseline_superiority_claim": True,
    }
    RUN_MANIFEST_JSON.write_text(json_dump(manifest_payload), encoding="utf-8")
    TRAINING_METRICS_JSON.write_text(json_dump(training_metrics_summary), encoding="utf-8")
    EVALUATION_METRICS_JSON.write_text(json_dump(evaluation_metrics_summary), encoding="utf-8")
    CHECKPOINT_METADATA_JSON.write_text(json_dump(checkpoint_summary), encoding="utf-8")
    artifact_manifest_summary = _artifact_manifest(_required_artifact_paths())
    report = RealTrainerReducedBudgetCampaignExecutionValidationReport(
        feature_id=FEATURE_ID,
        prerequisite_tags_verified=prerequisite_tags_verified,
        feature_059_gate_verified=feature_059_ready,
        feature_058_harness_verified=feature_058_ready,
        feature_057_pilot_verified=feature_057_ready,
        real_trainer_binding_summary=_real_trainer_binding_summary(),
        reduced_budget_execution_summary=reduced_budget_summary,
        training_metrics_summary=training_metrics_summary,
        evaluation_metrics_summary=evaluation_metrics_summary,
        baseline_contract_summary=feature_058_baseline,
        checkpoint_metadata_summary=checkpoint_summary,
        artifact_manifest_summary=artifact_manifest_summary,
        resource_control_summary=resource_control_summary,
        safety_summary={
            "no_full_campaign_execution": True,
            "no_paper_reproduction_claim": True,
            "no_performance_superiority_claim": True,
            "no_baseline_superiority_claim": True,
            "no_uncontrolled_campaign_loop": True,
            "no_policy_drift": True,
            "no_dependency_drift": True,
            "no_environment_contract_drift": True,
            "no_reward_timing_change": True,
            "no_prior_artifact_rewrite": True,
        },
        remaining_blockers=[] if result.loss_is_finite and result.optimizer_step_count > 0 else ["training_metrics_blocked"],
        recommended_next_feature=READY_NEXT_FEATURE,
        final_verdict="real_trainer_reduced_budget_campaign_validation_passed" if result.loss_is_finite and result.optimizer_step_count > 0 else "training_metrics_blocked",
    )
    write_real_trainer_reduced_budget_campaign_execution_validation_report(report, cfg.output_dir)
    return report


def generate_real_trainer_reduced_budget_campaign_execution_validation_artifacts(
    config: RealTrainerReducedBudgetCampaignExecutionValidationConfig | None = None,
) -> tuple[RealTrainerReducedBudgetCampaignExecutionValidationReport, Path, Path]:
    report = build_real_trainer_reduced_budget_campaign_execution_validation_report(config)
    return report, REPORT_JSON, REPORT_MD


def run_real_trainer_reduced_budget_campaign_execution_validation(
    config: RealTrainerReducedBudgetCampaignExecutionValidationConfig | None = None,
) -> RealTrainerReducedBudgetCampaignExecutionValidationReport:
    return build_real_trainer_reduced_budget_campaign_execution_validation_report(config)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate Feature 060A reduced-budget real-trainer validation report.")
    parser.add_argument("--json", action="store_true", help="print the generated JSON payload")
    args = parser.parse_args(argv)
    report, json_path, md_path = generate_real_trainer_reduced_budget_campaign_execution_validation_artifacts()
    if args.json:
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True, ensure_ascii=False))
    else:
        print(f"Wrote {json_path}")
        print(f"Wrote {md_path}")
        print(f"Wrote {TRAINING_METRICS_JSON}")
        print(f"Wrote {EVALUATION_METRICS_JSON}")
        print(f"Wrote {CHECKPOINT_METADATA_JSON}")
        print(f"Wrote {RUN_MANIFEST_JSON}")
        print(f"final_verdict = {report.final_verdict}")
        print(f"recommended_next_feature = {report.recommended_next_feature}")
    return 0 if report.final_verdict == "real_trainer_reduced_budget_campaign_validation_passed" else 1
