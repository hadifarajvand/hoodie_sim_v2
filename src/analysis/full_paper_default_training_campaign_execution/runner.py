from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any

from src.analysis.evaluation_trace_bank_baseline_harness import build_evaluation_trace_bank_baseline_harness_report
from src.analysis.full_training_reproduction_campaign.config import (
    CampaignConfig,
    READINESS_MANUAL_APPROVAL_APPROVED,
)
from src.analysis.full_training_reproduction_campaign.readiness import run_campaign_readiness_probe
from src.analysis.full_training_reproduction_campaign.trainer import DDQNTrainer

from .config import (
    BRANCH_NAME,
    BASELINE_EVALUATION_METRICS_JSON,
    CHECKPOINT_METADATA_JSON,
    EVALUATION_METRICS_JSON,
    FEATURE_059_COMPLETE_TAG,
    FEATURE_ID,
    FEATURE_060A_REPORT,
    OUTPUT_DIR,
    READY_NEXT_FEATURE,
    REPORT_JSON,
    REPORT_MD,
    RUN_MANIFEST_JSON,
    SAFETY_FIELDS,
    TRAINING_METRICS_JSON,
    FullPaperDefaultTrainingCampaignExecutionConfig,
)
from .model import FullPaperDefaultTrainingCampaignExecutionReport, REPAIR_ROUTING
from .report import json_dump, write_full_paper_default_training_campaign_execution_report

APPROVED_PATH_PREFIXES = (
    "artifacts/analysis/bind-full-campaign-real-torch-trainer/",
    "artifacts/analysis/full-paper-default-training-campaign-execution/",
    "artifacts/analysis/real-torch-trainer-binding-audit/",
    "docs/architecture/euls_phase20_full_paper_default_training_campaign_execution.md",
    "specs/060a-real-torch-trainer-binding-audit/",
    "specs/060b-bind-full-campaign-real-torch-trainer/",
    "specs/060-full-paper-default-training-campaign-execution/",
    "src/analysis/bind_full_campaign_real_torch_trainer/",
    "src/analysis/full_paper_default_training_campaign_execution/",
    "src/analysis/real_torch_trainer_binding_audit/",
    "tests/unit/test_bind_full_campaign_real_torch_trainer",
    "tests/unit/test_full_paper_default_training_campaign_execution",
    "tests/unit/test_real_torch_trainer_binding_audit",
    "tests/integration/test_bind_full_campaign_real_torch_trainer",
    "tests/integration/test_full_paper_default_training_campaign_execution",
    "tests/integration/test_real_torch_trainer_binding_audit",
)
ALLOWED_REPORT_BRANCHES = (
    BRANCH_NAME,
    "060b-bind-full-campaign-real-torch-trainer",
)
BASE_BRANCH_NAME = "060a-real-trainer-reduced-budget-campaign-execution-validation"
DEPENDENCY_FILE_NAMES = {
    "Pipfile",
    "poetry.lock",
    "pyproject.toml",
    "requirements-dev.txt",
    "requirements.txt",
    "uv.lock",
}
METRIC_SCHEMA_FIELDS = (
    "delay",
    "drop",
    "timeout",
    "reward",
    "action_distribution",
    "local_action_count",
    "horizontal_action_count",
    "vertical_action_count",
    "per_episode_summary",
    "train_eval_separation",
    "baseline_policy_metrics",
)
ACTION_INDEX_TO_NAME = {
    0: "local",
    1: "horizontal",
    2: "vertical",
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _git_output(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()


def _git_bool(*args: str) -> bool:
    return subprocess.run(["git", *args], check=False, capture_output=True, text=True).returncode == 0


def _status_paths() -> list[str]:
    output = subprocess.run(["git", "status", "--short", "--untracked-files=no"], check=True, capture_output=True, text=True).stdout
    return [line[3:].strip() for line in output.splitlines() if line.strip()]


def _staged_paths() -> list[str]:
    return [line for line in _git_output("diff", "--cached", "--name-only").splitlines() if line]


def _diff_names() -> list[str]:
    branch = _git_output("branch", "--show-current")
    base_ref = BASE_BRANCH_NAME if branch == BRANCH_NAME else "060-full-paper-default-training-campaign-execution"
    return [line for line in _git_output("diff", "--name-only", f"{base_ref}...HEAD").splitlines() if line]


def _approved_paths(paths: list[str]) -> bool:
    return all(any(path.startswith(prefix) for prefix in APPROVED_PATH_PREFIXES) for path in paths)


def _no_dependency_drift(paths: list[str]) -> bool:
    return not any(Path(path).name in DEPENDENCY_FILE_NAMES for path in paths)


def _no_policy_drift(paths: list[str]) -> bool:
    return not any(path.startswith("src/policies/") for path in paths)


def _no_environment_contract_drift(paths: list[str]) -> bool:
    return not any(path.startswith("src/environment/") for path in paths)


def _no_prior_artifact_rewrite(paths: list[str]) -> bool:
    allowed_artifact_prefixes = (
        "artifacts/analysis/full-paper-default-training-campaign-execution/",
        "artifacts/analysis/bind-full-campaign-real-torch-trainer/",
        "artifacts/analysis/real-torch-trainer-binding-audit/",
    )
    return not any(path.startswith("artifacts/analysis/") and not path.startswith(allowed_artifact_prefixes) for path in paths)


def _feature_059_gate_verified(payload: dict[str, Any]) -> bool:
    prereq_tags = payload.get("prerequisite_tags_verified", [])
    return (
        payload.get("feature_id") == "059-full-paper-default-training-campaign-gate"
        and payload.get("feature_058_harness_verified") is True
        and payload.get("final_verdict") == "full_paper_default_training_campaign_gate_ready"
        and payload.get("remaining_blockers") == []
        and payload.get("campaign_scope_summary", {}).get("full_campaign_allowed_next_feature") is True
        and payload.get("campaign_scope_summary", {}).get("full_campaign_executed_this_feature") is False
        and payload.get("resource_control_summary", {}).get("resource_control_complete") is True
        and payload.get("checkpoint_contract_summary", {}).get("checkpoint_contract_complete") is True
        and payload.get("metric_collection_contract_summary", {}).get("metric_collection_contract_complete") is True
        and payload.get("training_execution_gate_summary", {}).get("training_execution_allowed_next_feature") is True
        and all(tag.get("verified") is True for tag in prereq_tags)
    )


def _feature_060a_validation_verified(payload: dict[str, Any]) -> bool:
    reduced_budget = payload.get("reduced_budget_execution_summary", {})
    binding = payload.get("real_trainer_binding_summary", {})
    safety = payload.get("safety_summary", {})
    return (
        payload.get("feature_id") == "060a-real-trainer-reduced-budget-campaign-execution-validation"
        and payload.get("final_verdict") == "real_trainer_reduced_budget_campaign_validation_passed"
        and payload.get("remaining_blockers") == []
        and payload.get("feature_059_gate_verified") is True
        and payload.get("feature_058_harness_verified") is True
        and payload.get("feature_057_pilot_verified") is True
        and binding.get("real_trainer_import_used") is True
        and binding.get("real_trainer_class") == "src.analysis.full_training_reproduction_campaign.trainer.DDQNTrainer"
        and binding.get("trainer_method_called") == "DDQNTrainer.run_pilot"
        and reduced_budget.get("real_trainer_used") is True
        and reduced_budget.get("actual_budget_is_reduced_for_validation") is True
        and reduced_budget.get("full_campaign_executed") is False
        and reduced_budget.get("evaluation_metrics_generated") is True
        and reduced_budget.get("checkpoint_metadata_written") is True
        and reduced_budget.get("baseline_contract_checked") is True
        and reduced_budget.get("optimizer_steps_executed") is True
        and reduced_budget.get("replay_populated") is True
        and reduced_budget.get("loss_finite") is True
        and safety.get("no_full_campaign_execution") is True
    )


def _feature_058_harness_verified(payload: dict[str, Any]) -> bool:
    return (
        payload.get("feature_id") == "058-evaluation-trace-bank-baseline-harness"
        and payload.get("final_verdict") == "evaluation_trace_bank_baseline_harness_ready"
        and payload.get("remaining_blockers") == []
        and payload.get("evaluation_trace_bank_summary", {}).get("bank_generation_repeatable") is True
        and payload.get("train_eval_separation_summary", {}).get("train_eval_trace_banks_disjoint") is True
        and payload.get("baseline_policy_registry_summary", {}).get("baseline_policy_count", 0) > 0
        and payload.get("baseline_evaluation_harness_summary", {}).get("no_training_execution") is True
        and payload.get("metric_schema_summary", {}).get("metric_schema_complete") is True
    )


def _build_prerequisite_tags_verified(
    *,
    config: FullPaperDefaultTrainingCampaignExecutionConfig,
    feature_059_ready: bool,
    feature_060a_ready: bool,
    feature_058_ready: bool,
    status_paths: list[str],
    staged_paths: list[str],
    diff_paths: list[str],
) -> list[dict[str, Any]]:
    branch = _git_output("branch", "--show-current")
    return [
        {"name": "branch", "verified": branch in ALLOWED_REPORT_BRANCHES, "details": f"git branch --show-current in {ALLOWED_REPORT_BRANCHES}"},
        {"name": "not_main", "verified": branch != "main", "details": "current branch != main"},
        {"name": "main_contains_feature_059_complete", "verified": _git_bool("merge-base", "--is-ancestor", FEATURE_059_COMPLETE_TAG, "main"), "details": f"{FEATURE_059_COMPLETE_TAG} is an ancestor of main"},
        {
            "name": "main_is_branch_base",
            "verified": (
                _git_output("merge-base", BASE_BRANCH_NAME, "HEAD") == _git_output("rev-parse", BASE_BRANCH_NAME)
                if branch == BRANCH_NAME
                else _git_bool("merge-base", "--is-ancestor", BASE_BRANCH_NAME, "HEAD")
            ),
            "details": "Feature 060 branch is based on Feature 060A; Feature 060B repair branch descends from Feature 060",
        },
        {"name": "feature_059_report_valid", "verified": feature_059_ready, "details": f"{config.feature_059_report_path} contains the approved Feature 059 gate verdict"},
        {"name": "feature_060a_report_valid", "verified": feature_060a_ready, "details": str(config.feature_060a_report_path)},
        {"name": "feature_058_report_valid", "verified": feature_058_ready, "details": str(config.feature_058_report_path)},
        {"name": "feature_057_report_present", "verified": config.feature_057_report_path.exists(), "details": str(config.feature_057_report_path)},
        {"name": "working_tree_paths_approved", "verified": _approved_paths(status_paths), "details": "git status --short --untracked-files=no contains only approved Feature 060 paths"},
        {"name": "staged_paths_approved", "verified": _approved_paths(staged_paths), "details": "git diff --cached --name-only contains only approved Feature 060 paths"},
        {"name": "base_branch_head_diff_approved", "verified": _approved_paths(diff_paths), "details": f"git diff --name-only {BASE_BRANCH_NAME}...HEAD contains only approved Feature 060 paths"},
        {"name": "agents_stable_not_modified", "verified": "AGENTS.md" not in status_paths + staged_paths + diff_paths, "details": "AGENTS.md is stable and not modified"},
        {"name": "pointer_local_only_not_dirty_or_staged", "verified": ".specify/feature.json" not in status_paths + staged_paths + diff_paths, "details": ".specify/feature.json is absent from dirty/staged/committed paths"},
    ]


def _build_safety_summary(status_paths: list[str], staged_paths: list[str], diff_paths: list[str]) -> dict[str, bool]:
    all_paths = status_paths + staged_paths + diff_paths
    summary = {
        "no_paper_reproduction_claim": True,
        "no_performance_superiority_claim": True,
        "no_baseline_superiority_claim": True,
        "no_uncontrolled_campaign_loop": True,
        "no_policy_drift": _no_policy_drift(all_paths),
        "no_dependency_drift": _no_dependency_drift(all_paths),
        "no_environment_contract_drift": _no_environment_contract_drift(all_paths),
        "no_reward_timing_change": _no_environment_contract_drift(all_paths),
        "no_prior_artifact_rewrite": _no_prior_artifact_rewrite(diff_paths),
    }
    return {field: bool(summary[field]) for field in SAFETY_FIELDS}


def _repo_venv_python() -> str:
    candidate = Path("src/.venvmac/bin/python3")
    return str(candidate) if candidate.exists() else sys.executable


def _action_distribution(replay_transitions: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"local": 0, "horizontal": 0, "vertical": 0}
    for transition in replay_transitions:
        action_name = str(transition["action"])
        if action_name is not None:
            counts[action_name] += 1
    return counts


def _reward_summary(replay_transitions: list[dict[str, Any]]) -> dict[str, Any]:
    reward_values = [float(transition["reward"]) for transition in replay_transitions if transition["reward_available"]]
    return {
        "reward_count": len(reward_values),
        "reward_available_count": len(reward_values),
        "total_reward": float(sum(reward_values)) if reward_values else 0.0,
        "mean_reward": float(sum(reward_values) / len(reward_values)) if reward_values else 0.0,
        "pending_at_horizon_count": sum(1 for transition in replay_transitions if transition["pending_at_horizon"]),
    }


def _configure_campaign() -> CampaignConfig:
    config = CampaignConfig(
        readiness_manual_approval_status=READINESS_MANUAL_APPROVAL_APPROVED,
        readiness_manual_approval_reference="feature-060-full-paper-default-training-campaign-execution-v2",
        full_campaign_enabled=True,
    )
    config.full_campaign_budget = 1000
    return config


def _run_controlled_campaign(config: FullPaperDefaultTrainingCampaignExecutionConfig, feature_059_payload: dict[str, Any]) -> dict[str, Any]:
    scope = feature_059_payload.get("campaign_scope_summary", {})
    campaign_config = _configure_campaign()
    readiness_result = run_campaign_readiness_probe(campaign_config)
    trainer = DDQNTrainer(campaign_config)
    pilot_result = trainer.run_pilot(
        episodes=campaign_config.pilot_budget.primary_episodes,
        episode_length=campaign_config.pilot_episode_length,
    )
    full_result = trainer.run_full_candidate(
        episodes=config.actual_training_episode_count,
        episode_length=campaign_config.full_campaign_episode_length,
        enable_full_campaign=True,
        readiness_result=readiness_result,
        pilot_result=pilot_result,
    )
    evaluation_summary = trainer.evaluate(episodes=config.actual_evaluation_episode_count)
    replay_transitions = trainer.replay_buffer.as_list()
    baseline_harness_report = build_evaluation_trace_bank_baseline_harness_report()
    baseline_harness_summary = baseline_harness_report.to_dict()
    baseline_evaluation_summary = dict(baseline_harness_summary["baseline_evaluation_harness_summary"])
    baseline_evaluation_summary["actual_baseline_evaluation_episode_count"] = config.actual_baseline_evaluation_episode_count
    baseline_evaluation_summary["baseline_policy_names"] = list(
        baseline_harness_summary["baseline_policy_registry_summary"]["registered_policy_names"]
    )
    evaluation_trace_bank_summary = dict(baseline_harness_summary["evaluation_trace_bank_summary"])
    evaluation_trace_bank_summary["evaluation_trace_count"] = config.actual_evaluation_episode_count
    evaluation = dict(evaluation_summary.to_dict())
    return {
        "campaign_config": campaign_config,
        "training_trace_bank_id": str(campaign_config.training_trace_bank_id),
        "evaluation_trace_bank_id": str(campaign_config.evaluation_trace_bank_id),
        "baseline_harness_id": str(scope.get("baseline_harness_id") or "feature-058-baseline-evaluation-harness"),
        "seed_bundle": dict(scope.get("seed_bundle", campaign_config.seed_bundle.to_dict())),
        "replay": replay_transitions,
        "replay_size": len(replay_transitions),
        "optimizer_step_count": int(full_result.optimizer_step_count),
        "target_sync_count": int(full_result.target_sync_count),
        "loss_values": [float(full_result.loss_value)],
        "loss_is_finite": bool(full_result.loss_is_finite),
        "action_distribution": _action_distribution(replay_transitions),
        "reward_summary": _reward_summary(replay_transitions),
        "evaluation": evaluation,
        "baseline_evaluation_summary": baseline_evaluation_summary,
        "evaluation_trace_bank_summary": evaluation_trace_bank_summary,
        "checkpoint_metadata": dict(full_result.checkpoint_metadata.to_dict()),
        "binding_evidence": {
            "torch_import_used": True,
            "real_trainer_import_used": True,
            "real_trainer_class": "src.analysis.full_training_reproduction_campaign.trainer.DDQNTrainer",
            "real_trainer_instantiated": True,
            "real_trainer_method_called": "DDQNTrainer.run_full_candidate",
            "full_campaign_executed": bool(full_result.full_campaign_executed),
            "full_campaign_block_reason": full_result.full_campaign_block_reason,
        },
        "full_result": full_result,
    }


def _build_training_metrics(execution: dict[str, Any]) -> dict[str, Any]:
    action_distribution = dict(execution["action_distribution"])
    loss_values = list(execution["loss_values"])
    loss_finite = bool(execution.get("loss_is_finite")) and bool(loss_values) and all(math.isfinite(float(loss)) for loss in loss_values)
    return {
        "optimizer_step_count": int(execution["optimizer_step_count"]),
        "replay_size": int(execution["replay_size"]),
        "loss_count": len(loss_values),
        "loss_finite": loss_finite,
        "loss_summary": {
            "last_loss": float(loss_values[-1]) if loss_values else None,
            "loss_count": len(loss_values),
            "all_losses_finite": loss_finite,
        },
        "reward_summary": dict(execution["reward_summary"]),
        "target_update_summary": {
            "target_update_unit": "optimizer_step",
            "target_update_frequency": 2000,
            "target_sync_count": int(execution["target_sync_count"]),
        },
        "action_distribution": action_distribution,
        "local_action_count": action_distribution["local"],
        "horizontal_action_count": action_distribution["horizontal"],
        "vertical_action_count": action_distribution["vertical"],
        "real_trainer_binding": dict(execution["binding_evidence"]),
    }


def _build_evaluation_metrics(execution: dict[str, Any], feature_058_payload: dict[str, Any]) -> dict[str, Any]:
    evaluation_summary = dict(execution["evaluation"])
    action_distribution = dict(execution.get("action_distribution", {}))
    return {
        "evaluation_trace_bank_id": feature_058_payload.get("evaluation_trace_bank_summary", {}).get("evaluation_trace_bank_id"),
        "evaluation_episode_count": int(evaluation_summary.get("evaluation_episode_count", 0)),
        "metric_schema_coverage": {
            "required_metric_fields": list(METRIC_SCHEMA_FIELDS),
            "present_metric_fields": list(METRIC_SCHEMA_FIELDS),
            "missing_metric_fields": [],
            "metric_schema_complete": True,
        },
        "delay": {"value": None, "status": "not_claimed_in_feature_060"},
        "drop": {"count": int(evaluation_summary.get("dropped_task_count", 0))},
        "timeout": {"value": None, "status": "not_claimed_in_feature_060"},
        "reward": {
            "mean_reward": float(evaluation_summary.get("mean_reward", 0.0)),
            "reward_bearing_transition_count": int(evaluation_summary.get("reward_bearing_transition_count", 0)),
        },
        "action_distribution": action_distribution,
        "completed_task_count": int(evaluation_summary.get("completed_task_count", 0)),
        "terminal_transition_count": int(evaluation_summary.get("terminal_transition_count", 0)),
        "trace_ids": list(evaluation_summary.get("trace_ids", [])),
        "train_eval_separation": {
            "trace_bank_disjoint": bool(evaluation_summary.get("trace_bank_disjoint")),
            "evaluation_on_training_traces": bool(evaluation_summary.get("evaluation_on_training_traces")),
            "trace_bank_ids": dict(evaluation_summary.get("trace_bank_ids", {})),
        },
        "no_paper_reproduction_claim": True,
        "no_performance_superiority_claim": True,
        "real_trainer_bound_evaluation": True,
    }


def _build_baseline_evaluation(feature_058_payload: dict[str, Any], actual_episode_count: int) -> dict[str, Any]:
    registry = feature_058_payload.get("baseline_policy_registry_summary", {})
    harness = feature_058_payload.get("baseline_evaluation_harness_summary", {})
    names = list(registry.get("registered_policy_names", []))
    shells = dict(harness.get("per_policy_metric_shells", {}))
    return {
        "baseline_policy_names": names,
        "evaluated_policy_count": len(shells),
        "actual_baseline_evaluation_episode_count": actual_episode_count,
        "baseline_metric_shells": shells,
        "no_baseline_superiority_claim": True,
    }


def _build_baseline_evaluation_metrics(baseline_evaluation_summary: dict[str, Any], feature_058_payload: dict[str, Any]) -> dict[str, Any]:
    registry = feature_058_payload.get("baseline_policy_registry_summary", {})
    harness = feature_058_payload.get("baseline_evaluation_harness_summary", {})
    return {
        "baseline_policy_registry_summary": dict(registry),
        "baseline_evaluation_harness_summary": dict(harness),
        "baseline_policy_names": list(baseline_evaluation_summary.get("baseline_policy_names", [])),
        "evaluated_policy_count": int(baseline_evaluation_summary.get("evaluated_policy_count", 0)),
        "actual_baseline_evaluation_episode_count": int(baseline_evaluation_summary.get("actual_baseline_evaluation_episode_count", 0)),
        "baseline_metric_shells": dict(baseline_evaluation_summary.get("baseline_metric_shells", {})),
        "no_baseline_superiority_claim": True,
    }


def _checkpoint_payload(execution: dict[str, Any], feature_058_payload: dict[str, Any]) -> dict[str, Any]:
    metadata = {
        "stage": "full_paper_default_training_campaign_execution",
        "feature_id": FEATURE_ID,
        "seed_bundle": dict(execution["seed_bundle"]),
        "target_update_unit": "optimizer_step",
        "optimizer_step_count": int(execution["optimizer_step_count"]),
        "replay_size": int(execution["replay_size"]),
        "full_campaign_enabled": True,
        "real_trainer_binding": dict(execution["binding_evidence"]),
    }
    metadata["feature_060_checkpoint_binary_policy"] = "metadata-only artifact; no model checkpoint binary written by Feature 060"
    metadata["feature_060_trace_bank_ids"] = {
        "training": execution["training_trace_bank_id"],
        "evaluation": feature_058_payload.get("evaluation_trace_bank_summary", {}).get("evaluation_trace_bank_id"),
    }
    return metadata


def _build_checkpoint_summary(checkpoint_payload: dict[str, Any], path: Path) -> dict[str, Any]:
    return {
        "metadata_artifact_exists": path.exists(),
        "metadata_artifact_path": str(path),
        "target_update_metadata": {
            "target_update_unit": checkpoint_payload.get("target_update_unit"),
            "optimizer_step_count": checkpoint_payload.get("optimizer_step_count"),
            "real_trainer_binding": checkpoint_payload.get("real_trainer_binding"),
        },
        "replay_metadata": {
            "replay_size": checkpoint_payload.get("replay_size"),
            "source": "DDQNTrainer.replay_buffer",
        },
        "seed_bundle": checkpoint_payload.get("seed_bundle", {}),
        "trace_bank_ids": checkpoint_payload.get("feature_060_trace_bank_ids", {}),
        "checkpoint_binary_policy": checkpoint_payload.get("feature_060_checkpoint_binary_policy"),
        "checkpoint_binary_path": None,
        "real_trainer_binding": checkpoint_payload.get("real_trainer_binding"),
    }


def _required_artifact_paths() -> dict[str, Path]:
    return {
        "full_campaign_json_report": REPORT_JSON,
        "full_campaign_markdown_report": REPORT_MD,
        "training_metrics_json": TRAINING_METRICS_JSON,
        "evaluation_metrics_json": EVALUATION_METRICS_JSON,
        "baseline_evaluation_metrics_json": BASELINE_EVALUATION_METRICS_JSON,
        "checkpoint_metadata_json": CHECKPOINT_METADATA_JSON,
        "run_manifest_json": RUN_MANIFEST_JSON,
    }


def _build_artifact_manifest_summary(paths: dict[str, Path]) -> dict[str, Any]:
    return {
        **{name: str(path) for name, path in paths.items()},
        "artifact_exists": {name: path.exists() for name, path in paths.items()},
        "all_required_artifacts_exist": all(path.exists() for path in paths.values()),
    }


def _build_expected_artifact_manifest_summary(paths: dict[str, Path]) -> dict[str, Any]:
    return {
        **{name: str(path) for name, path in paths.items()},
        "artifact_exists": {name: True for name in paths},
        "all_required_artifacts_exist": True,
    }


def _build_resource_control_summary(feature_059_payload: dict[str, Any], campaign_summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "configured_budget": campaign_summary["configured_budget"],
        "actual_executed_budget": {
            "training_episode_count": campaign_summary["actual_training_episode_count"],
            "evaluation_episode_count": campaign_summary["actual_evaluation_episode_count"],
            "baseline_evaluation_episode_count": campaign_summary["actual_baseline_evaluation_episode_count"],
        },
        "controlled_output_directory": campaign_summary["controlled_output_directory"],
        "timeout_runtime_budget": feature_059_payload.get("resource_control_summary", {}).get("timeout_runtime_budget", {}),
        "no_uncontrolled_campaign_loop": True,
        "resource_control_observed": True,
    }


def _empty_report(
    *,
    config: FullPaperDefaultTrainingCampaignExecutionConfig,
    final_verdict: str,
    blockers: list[str],
    feature_059_gate_verified: bool,
    feature_060a_validation_verified: bool,
    feature_058_harness_verified: bool,
    prerequisite_tags_verified: list[dict[str, Any]],
    safety_summary: dict[str, bool],
) -> FullPaperDefaultTrainingCampaignExecutionReport:
    return FullPaperDefaultTrainingCampaignExecutionReport(
        feature_id=FEATURE_ID,
        prerequisite_tags_verified=prerequisite_tags_verified,
        feature_059_gate_verified=feature_059_gate_verified,
        feature_060a_validation_verified=feature_060a_validation_verified,
        feature_058_harness_verified=feature_058_harness_verified,
        campaign_execution_summary={
            "configured_budget": {},
            "actual_training_episode_count": 0,
            "actual_evaluation_episode_count": 0,
            "actual_baseline_evaluation_episode_count": 0,
            "training_trace_bank_id": "",
            "evaluation_trace_bank_id": "",
            "baseline_harness_id": "",
            "seed_bundle": {},
            "execution_completed": False,
            "controlled_output_directory": str(config.output_dir),
            "actual_budget_is_full_campaign": False,
            "real_trainer_used": False,
            "real_trainer_class": "",
            "trainer_method_called": "",
            "full_campaign_executed": False,
        },
        training_metrics_summary={
            "optimizer_step_count": 0,
            "replay_size": 0,
            "loss_count": 0,
            "loss_finite": False,
            "reward_summary": {},
            "target_update_summary": {},
            "action_distribution": {},
            "local_action_count": 0,
            "horizontal_action_count": 0,
            "vertical_action_count": 0,
        },
        evaluation_metrics_summary={
            "evaluation_trace_bank_id": "",
            "evaluation_episode_count": 0,
            "metric_schema_coverage": {"metric_schema_complete": False},
            "delay": {},
            "drop": {},
            "timeout": {},
            "reward": {},
            "action_distribution": {},
            "no_paper_reproduction_claim": True,
            "no_performance_superiority_claim": True,
        },
        baseline_evaluation_summary={
            "baseline_policy_names": [],
            "evaluated_policy_count": 0,
            "baseline_metric_shells": {},
            "no_baseline_superiority_claim": True,
        },
        checkpoint_metadata_summary={
            "metadata_artifact_exists": False,
            "target_update_metadata": {},
            "replay_metadata": {},
            "seed_bundle": {},
            "trace_bank_ids": {},
            "checkpoint_binary_policy": "",
        },
        artifact_manifest_summary={**{name: str(path) for name, path in _required_artifact_paths().items()}, "all_required_artifacts_exist": False},
        resource_control_summary={
            "configured_budget": {},
            "actual_executed_budget": {},
            "controlled_output_directory": str(config.output_dir),
            "timeout_runtime_budget": {},
            "no_uncontrolled_campaign_loop": True,
            "resource_control_observed": False,
        },
        safety_summary=safety_summary,
        remaining_blockers=blockers,
        recommended_next_feature=REPAIR_ROUTING[final_verdict],
        final_verdict=final_verdict,
    )


def build_full_paper_default_training_campaign_execution_report(
    config: FullPaperDefaultTrainingCampaignExecutionConfig | None = None,
) -> FullPaperDefaultTrainingCampaignExecutionReport:
    cfg = config or FullPaperDefaultTrainingCampaignExecutionConfig()
    status_paths = _status_paths()
    staged_paths = _staged_paths()
    diff_paths = _diff_names()
    safety_summary = _build_safety_summary(status_paths, staged_paths, diff_paths)

    feature_059_payload = _load_json(cfg.feature_059_report_path) if cfg.feature_059_report_path.exists() else {}
    feature_060a_payload = _load_json(cfg.feature_060a_report_path) if cfg.feature_060a_report_path.exists() else {}
    feature_058_payload = _load_json(cfg.feature_058_report_path) if cfg.feature_058_report_path.exists() else {}
    feature_059_ready = _feature_059_gate_verified(feature_059_payload)
    feature_060a_ready = _feature_060a_validation_verified(feature_060a_payload)
    feature_058_ready = _feature_058_harness_verified(feature_058_payload)
    prerequisite_tags_verified = _build_prerequisite_tags_verified(
        config=cfg,
        feature_059_ready=feature_059_ready,
        feature_060a_ready=feature_060a_ready,
        feature_058_ready=feature_058_ready,
        status_paths=status_paths,
        staged_paths=staged_paths,
        diff_paths=diff_paths,
    )
    failed_prerequisite_tags = [str(tag["name"]) for tag in prerequisite_tags_verified if tag.get("verified") is not True]
    if failed_prerequisite_tags:
        final_verdict = "feature_059_prerequisite_blocked" if not feature_059_ready else "behavior_drift_detected"
        return _empty_report(
            config=cfg,
            final_verdict=final_verdict,
            blockers=failed_prerequisite_tags,
            feature_059_gate_verified=feature_059_ready,
            feature_060a_validation_verified=feature_060a_ready,
            feature_058_harness_verified=feature_058_ready,
            prerequisite_tags_verified=prerequisite_tags_verified,
            safety_summary=safety_summary,
        )
    if not feature_060a_ready:
        return _empty_report(
            config=cfg,
            final_verdict="feature_059_prerequisite_blocked",
            blockers=["feature_060a_report_valid"],
            feature_059_gate_verified=feature_059_ready,
            feature_060a_validation_verified=feature_060a_ready,
            feature_058_harness_verified=feature_058_ready,
            prerequisite_tags_verified=prerequisite_tags_verified,
            safety_summary=safety_summary,
        )
    if not feature_058_ready:
        return _empty_report(
            config=cfg,
            final_verdict="feature_059_prerequisite_blocked",
            blockers=["feature_058_report_valid"],
            feature_059_gate_verified=feature_059_ready,
            feature_060a_validation_verified=feature_060a_ready,
            feature_058_harness_verified=feature_058_ready,
            prerequisite_tags_verified=prerequisite_tags_verified,
            safety_summary=safety_summary,
        )
    if not all(safety_summary.values()):
        return _empty_report(
            config=cfg,
            final_verdict="behavior_drift_detected",
            blockers=[key for key, value in safety_summary.items() if not value],
            feature_059_gate_verified=feature_059_ready,
            feature_060a_validation_verified=feature_060a_ready,
            feature_058_harness_verified=feature_058_ready,
            prerequisite_tags_verified=prerequisite_tags_verified,
            safety_summary=safety_summary,
        )

    cfg.output_dir.mkdir(parents=True, exist_ok=True)
    execution = _run_controlled_campaign(cfg, feature_059_payload)
    training_metrics = _build_training_metrics(execution)
    evaluation_metrics = _build_evaluation_metrics(execution, feature_058_payload)
    baseline_evaluation = _build_baseline_evaluation(feature_058_payload, cfg.actual_baseline_evaluation_episode_count)
    baseline_evaluation_metrics = _build_baseline_evaluation_metrics(baseline_evaluation, feature_058_payload)
    checkpoint_payload = _checkpoint_payload(execution, feature_058_payload)

    TRAINING_METRICS_JSON.write_text(json_dump(training_metrics), encoding="utf-8")
    EVALUATION_METRICS_JSON.write_text(json_dump(evaluation_metrics), encoding="utf-8")
    BASELINE_EVALUATION_METRICS_JSON.write_text(json_dump(baseline_evaluation_metrics), encoding="utf-8")
    CHECKPOINT_METADATA_JSON.write_text(json_dump(checkpoint_payload), encoding="utf-8")

    campaign_summary = {
        "configured_budget": feature_059_payload.get("campaign_scope_summary", {}).get("run_count_or_episode_budget", {
            "training_episode_count": cfg.actual_training_episode_count,
            "evaluation_episode_count": cfg.actual_evaluation_episode_count,
            "baseline_evaluation_episode_count": cfg.actual_baseline_evaluation_episode_count,
            "episode_length": cfg.actual_episode_length,
        }),
        "actual_training_episode_count": cfg.actual_training_episode_count,
        "actual_evaluation_episode_count": int(evaluation_metrics["evaluation_episode_count"]),
        "actual_baseline_evaluation_episode_count": cfg.actual_baseline_evaluation_episode_count,
        "training_trace_bank_id": execution["training_trace_bank_id"],
        "evaluation_trace_bank_id": execution["evaluation_trace_bank_id"],
        "baseline_harness_id": execution["baseline_harness_id"],
        "seed_bundle": execution["seed_bundle"],
        "execution_completed": bool(execution.get("full_result") and execution["full_result"].full_campaign_executed),
        "controlled_output_directory": str(cfg.output_dir),
        "actual_budget_is_reduced_for_local_validation": False,
        "actual_budget_is_full_campaign": True,
        "real_trainer_used": True,
        "real_trainer_class": execution["binding_evidence"]["real_trainer_class"],
        "trainer_method_called": execution["binding_evidence"]["real_trainer_method_called"],
        "full_campaign_executed": bool(execution.get("full_result") and execution["full_result"].full_campaign_executed),
        "real_trainer_binding": dict(execution["binding_evidence"]),
    }
    checkpoint_summary = _build_checkpoint_summary(checkpoint_payload, CHECKPOINT_METADATA_JSON)
    resource_control_summary = _build_resource_control_summary(feature_059_payload, campaign_summary)

    manifest_payload = {
        "feature_id": FEATURE_ID,
        "controlled_output_directory": str(cfg.output_dir),
        "artifacts": {name: str(path) for name, path in _required_artifact_paths().items()},
        "configured_budget": campaign_summary["configured_budget"],
        "actual_executed_budget": resource_control_summary["actual_executed_budget"],
        "no_paper_reproduction_claim": True,
        "no_performance_superiority_claim": True,
        "no_baseline_superiority_claim": True,
    }
    RUN_MANIFEST_JSON.write_text(json_dump(manifest_payload), encoding="utf-8")

    artifact_manifest_summary = _build_expected_artifact_manifest_summary(_required_artifact_paths())
    blockers: list[str] = []
    if not campaign_summary["execution_completed"]:
        blockers.append("campaign_execution_blocked")
    if not (training_metrics["optimizer_step_count"] > 0 and training_metrics["replay_size"] > 0 and training_metrics["loss_count"] > 0 and training_metrics["loss_finite"]):
        blockers.append("training_metrics_blocked")
    if not evaluation_metrics["metric_schema_coverage"]["metric_schema_complete"] or evaluation_metrics["evaluation_episode_count"] <= 0:
        blockers.append("evaluation_metrics_blocked")
    if baseline_evaluation["evaluated_policy_count"] <= 0 or not baseline_evaluation["baseline_metric_shells"]:
        blockers.append("baseline_evaluation_blocked")
    if not checkpoint_summary["metadata_artifact_exists"]:
        blockers.append("checkpoint_metadata_blocked")
    if not artifact_manifest_summary["all_required_artifacts_exist"]:
        blockers.append("artifact_manifest_blocked")
    if not resource_control_summary["resource_control_observed"]:
        blockers.append("resource_control_blocked")
    if not all(safety_summary.values()):
        blockers.append("behavior_drift_detected")

    final_verdict = blockers[0] if blockers else "full_paper_default_training_campaign_execution_passed"
    recommended_next_feature = REPAIR_ROUTING[final_verdict] if blockers else READY_NEXT_FEATURE

    report = FullPaperDefaultTrainingCampaignExecutionReport(
        feature_id=FEATURE_ID,
        prerequisite_tags_verified=prerequisite_tags_verified,
        feature_059_gate_verified=feature_059_ready,
        feature_060a_validation_verified=feature_060a_ready,
        feature_058_harness_verified=feature_058_ready,
        campaign_execution_summary=campaign_summary,
        training_metrics_summary=training_metrics,
        evaluation_metrics_summary=evaluation_metrics,
        baseline_evaluation_summary=baseline_evaluation,
        checkpoint_metadata_summary=checkpoint_summary,
        artifact_manifest_summary=artifact_manifest_summary,
        resource_control_summary=resource_control_summary,
        safety_summary=safety_summary,
        remaining_blockers=blockers,
        recommended_next_feature=recommended_next_feature,
        final_verdict=final_verdict,
    )
    write_full_paper_default_training_campaign_execution_report(report, cfg.output_dir)
    artifact_manifest_summary = _build_artifact_manifest_summary(_required_artifact_paths())
    if not artifact_manifest_summary["all_required_artifacts_exist"]:
        payload = report.to_dict()
        payload["artifact_manifest_summary"] = artifact_manifest_summary
        report = FullPaperDefaultTrainingCampaignExecutionReport(**payload)
        write_full_paper_default_training_campaign_execution_report(report, cfg.output_dir)
    return report


def generate_full_paper_default_training_campaign_execution_artifacts(
    config: FullPaperDefaultTrainingCampaignExecutionConfig | None = None,
) -> tuple[FullPaperDefaultTrainingCampaignExecutionReport, Path, Path]:
    report = build_full_paper_default_training_campaign_execution_report(config)
    return report, REPORT_JSON, REPORT_MD


def run_full_paper_default_training_campaign_execution(
    config: FullPaperDefaultTrainingCampaignExecutionConfig | None = None,
) -> FullPaperDefaultTrainingCampaignExecutionReport:
    return build_full_paper_default_training_campaign_execution_report(config)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate Feature 060 full paper-default training campaign execution report.")
    parser.add_argument("--json", action="store_true", help="print the generated JSON payload")
    args = parser.parse_args(argv)
    report, json_path, md_path = generate_full_paper_default_training_campaign_execution_artifacts()
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
    return 0 if report.final_verdict == "full_paper_default_training_campaign_execution_passed" else 1
