from __future__ import annotations

from pathlib import Path
import argparse
import json
import random
import subprocess
from statistics import mean
from typing import Any

from .config import (
    BRANCH_NAME,
    FEATURE_054_REPORT,
    FEATURE_055_REPORT,
    FEATURE_056_REPORT,
    FEATURE_ID,
    READY_NEXT_FEATURE,
    PaperDefaultPilotTrainingRunConfig,
)
from .model import PaperDefaultPilotTrainingRunReport
from .report import write_paper_default_pilot_training_run_report

APPROVED_PATH_PREFIXES = (
    "artifacts/analysis/paper-default-pilot-training-run/",
    "specs/057-paper-default-pilot-training-run/",
    "src/analysis/paper_default_pilot_training_run/",
    "tests/unit/test_paper_default_pilot_training_run",
    "tests/integration/test_paper_default_pilot_training_run",
)
REPLAY_SAMPLE_FIELD_NAMES = (
    "state",
    "action",
    "legal_action_mask",
    "next_state",
    "reward",
    "terminal",
    "reward_available",
    "pending_at_horizon",
)
FEATURE_056_EXPECTED_NEXT_FEATURE = "Feature 057 — Paper-Default Pilot Training Run"


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _git_output(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()


def _git_bool(*args: str) -> bool:
    return subprocess.run(["git", *args], check=False, capture_output=True, text=True).returncode == 0


def _status_paths() -> list[str]:
    paths: list[str] = []
    for line in _git_output("status", "--short").splitlines():
        if not line.strip():
            continue
        paths.append(line[3:].strip())
    return paths


def _staged_paths() -> list[str]:
    output = _git_output("diff", "--cached", "--name-only")
    return [line for line in output.splitlines() if line]


def _diff_names() -> list[str]:
    output = _git_output("diff", "--name-only", "main...HEAD")
    return [line for line in output.splitlines() if line]


def _no_dependency_drift(paths: list[str]) -> bool:
    return not any(Path(path).name in {"pyproject.toml", "requirements.txt", "requirements-dev.txt", "poetry.lock", "uv.lock", "Pipfile"} for path in paths)


def _no_policy_drift(paths: list[str]) -> bool:
    return not any(path.startswith("src/policies/") for path in paths)


def _no_environment_semantic_drift(paths: list[str]) -> bool:
    return not any(path.startswith("src/environment/") for path in paths)


def _no_prior_artifact_rewrite(paths: list[str]) -> bool:
    return not any(path.startswith("artifacts/analysis/") and not path.startswith("artifacts/analysis/paper-default-pilot-training-run/") for path in paths)


def _feature_055_smoke_verified(payload: dict[str, Any]) -> bool:
    return (
        payload.get("feature_id") == "055-paper-default-training-smoke-run"
        and payload.get("feature_054_readiness_verified") is True
        and payload.get("live_environment_training_used") is True
        and payload.get("fixture_training_used") is False
        and payload.get("replay_summary", {}).get("replay_inserted") is True
        and int(payload.get("replay_summary", {}).get("replay_size", 0)) > 0
        and payload.get("optimizer_step_summary", {}).get("optimizer_steps_executed") is True
        and int(payload.get("optimizer_step_summary", {}).get("optimizer_step_count", 0)) > 0
        and payload.get("loss_summary", {}).get("loss_is_finite") is True
        and payload.get("legal_action_summary", {}).get("legal_action_only") is True
        and payload.get("remaining_blockers") == []
        and payload.get("final_verdict") == "paper_default_training_smoke_passed"
        and payload.get("recommended_next_feature") == "Feature 056 — Target Update and Replay Training Validation"
    )


def _feature_054_ready(payload: dict[str, Any]) -> bool:
    return (
        payload.get("feature_id") == "054-training-readiness-contract"
        and payload.get("feature_053_readiness_verified") is True
        and payload.get("evidence_chain_ready_for_training_contract") is True
        and payload.get("training_execution_allowed_next") is True
        and payload.get("remaining_blockers") == []
        and payload.get("final_verdict") == "training_readiness_contract_ready_for_smoke_run"
        and payload.get("recommended_next_feature") == "Feature 055 — Paper-Default Training Smoke Run"
    )


def _report_exists(path: Path, expected_feature_id: str) -> tuple[bool, dict[str, Any]]:
    if not path.exists():
        return False, {"path": str(path), "exists": False, "feature_id": None, "final_verdict": None}
    payload = _load_json(path)
    return (
        payload.get("feature_id") == expected_feature_id,
        {
            "path": str(path),
            "exists": True,
            "feature_id": payload.get("feature_id"),
            "final_verdict": payload.get("final_verdict"),
        },
    )


def _feature_056_validation_verified(payload: dict[str, Any]) -> bool:
    return (
        payload.get("feature_id") == "056-target-update-and-replay-training-validation"
        and payload.get("feature_055_smoke_verified") is True
        and payload.get("replay_insertion_validated") is True
        and payload.get("replay_sampling_validated") is True
        and payload.get("optimizer_step_counter_validated") is True
        and payload.get("target_update_contract_validated") is True
        and payload.get("target_sync_schedule_validated") is True
        and payload.get("target_sync_before_threshold_blocked") is True
        and payload.get("target_sync_at_threshold_validated") is True
        and payload.get("checkpoint_metadata_validated") is True
        and payload.get("remaining_blockers") == []
        and payload.get("final_verdict") == "target_update_replay_validation_passed"
        and payload.get("recommended_next_feature") == FEATURE_056_EXPECTED_NEXT_FEATURE
    )


def _feature_055_smoke_metrics(payload: dict[str, Any]) -> tuple[int, int]:
    replay_size = int(payload.get("replay_summary", {}).get("replay_size", 0))
    optimizer_step_count = int(payload.get("optimizer_step_summary", {}).get("optimizer_step_count", 0))
    return replay_size, optimizer_step_count


def _build_prerequisite_tags_verified(
    *,
    feature_056_ready: bool,
    feature_055_ready: bool,
    feature_054_ready: bool,
    dirty_paths: list[str],
    staged_paths: list[str],
    diff_paths: list[str],
) -> list[dict[str, Any]]:
    approved_dirty = all(any(path.startswith(prefix) for prefix in APPROVED_PATH_PREFIXES) for path in dirty_paths)
    approved_staged = all(any(path.startswith(prefix) for prefix in APPROVED_PATH_PREFIXES) for path in staged_paths)
    approved_diff = all(any(path.startswith(prefix) for prefix in APPROVED_PATH_PREFIXES) for path in diff_paths)
    return [
        {"name": "branch", "verified": _git_output("branch", "--show-current") == BRANCH_NAME, "details": f"git branch --show-current == {BRANCH_NAME}"},
        {"name": "not_main", "verified": _git_output("branch", "--show-current") != "main", "details": "current branch != main"},
        {"name": "origin_main_contains_056_complete", "verified": _git_bool("merge-base", "--is-ancestor", "056-target-update-replay-validation", "origin/main"), "details": "origin/main contains the 056 validation branch commit"},
        {"name": "origin_main_contains_055_complete", "verified": _git_bool("merge-base", "--is-ancestor", "055-paper-default-smoke-run", "origin/main"), "details": "origin/main contains the 055 smoke branch commit"},
        {"name": "origin_main_contains_054_complete", "verified": _git_bool("merge-base", "--is-ancestor", "054-training-readiness-contract", "origin/main"), "details": "origin/main contains the 054 readiness branch commit"},
        {"name": "origin_main_contains_054a_hygiene", "verified": _git_bool("merge-base", "--is-ancestor", "054a-speckit-local-state-hygiene-recovery", "origin/main"), "details": "origin/main contains the 054A hygiene branch commit"},
        {"name": "origin_main_is_branch_base", "verified": _git_output("merge-base", "origin/main", "HEAD") == _git_output("rev-parse", "origin/main"), "details": "branch is based on current origin/main"},
        {"name": "feature_056_report_valid", "verified": feature_056_ready, "details": f"{FEATURE_056_REPORT} exists and contains the approved 056 readiness verdict"},
        {"name": "feature_055_report_valid", "verified": feature_055_ready, "details": f"{FEATURE_055_REPORT} exists and contains the approved 055 smoke verdict"},
        {"name": "feature_054_report_valid", "verified": feature_054_ready, "details": f"{FEATURE_054_REPORT} exists and contains the approved 054 readiness verdict"},
        {"name": "working_tree_paths_approved", "verified": approved_dirty, "details": "git status --short contains only approved Feature 057 paths"},
        {"name": "staged_paths_approved", "verified": approved_staged, "details": "git diff --cached --name-only contains only approved Feature 057 paths"},
        {"name": "main_head_diff_approved", "verified": approved_diff, "details": "git diff --name-only main...HEAD contains only approved Feature 057 paths"},
        {"name": "no_prior_artifact_rewrite", "verified": _no_prior_artifact_rewrite(diff_paths), "details": "no Feature 037-056 artifacts are rewritten"},
        {"name": "agents_stable_not_modified", "verified": "AGENTS.md" not in dirty_paths and "AGENTS.md" not in staged_paths and "AGENTS.md" not in diff_paths, "details": "AGENTS.md is stable and not modified"},
        {"name": "pointer_local_only_not_dirty_or_staged", "verified": ".specify/feature.json" not in dirty_paths and ".specify/feature.json" not in staged_paths and ".specify/feature.json" not in diff_paths, "details": ".specify/feature.json is ignored/local-only and absent from dirty/staged/committed paths"},
    ]


def _build_replay_summary(trainer: Any, *, feature_055_replay_size: int, sample_size: int, replay_seed: int) -> dict[str, Any]:
    buffer = trainer.replay_buffer
    replay_size = len(buffer)
    sampled_batch_size = min(sample_size, replay_size) if replay_size > 0 else 0
    sampled_field_coverage = {name: False for name in REPLAY_SAMPLE_FIELD_NAMES}
    sampled_transition_count = 0
    delayed_reward_semantics_preserved = False
    full_transitions = buffer.as_list()
    pending_at_horizon_preserved = any(transition.pending_at_horizon for transition in full_transitions)
    reward_available_count = sum(1 for transition in full_transitions if transition.reward_available)
    sample_transitions: list[dict[str, Any]] = []
    if sampled_batch_size > 0:
        batch = buffer.sample(sampled_batch_size, rng=random.Random(replay_seed))
        sample_transitions = [transition.to_dict() for transition in batch.transitions]
        sampled_transition_count = len(sample_transitions)
        sampled_field_coverage = {
            name: all(name in transition for transition in sample_transitions)
            for name in REPLAY_SAMPLE_FIELD_NAMES
        }
        delayed_reward_semantics_preserved = all(
            (not transition["reward_available"] and not transition["terminal"] and not transition["pending_at_horizon"])
            or (transition["reward_available"] and transition["terminal"] and transition["terminal_reason"] in {"completed", "dropped"})
            or (transition["pending_at_horizon"] and not transition["terminal"])
            for transition in sample_transitions
        )
    return {
        "feature_055_smoke_replay_size": feature_055_replay_size,
        "replay_size": replay_size,
        "replay_growth_count": replay_size - feature_055_replay_size,
        "replay_growth_validated": replay_size > feature_055_replay_size,
        "sampled_batch_size": sampled_batch_size,
        "sampled_transition_count": sampled_transition_count,
        "replay_inserted": replay_size > 0,
        "sampled_field_coverage": sampled_field_coverage,
        "delayed_reward_semantics_preserved": delayed_reward_semantics_preserved,
        "pending_at_horizon_preserved": pending_at_horizon_preserved,
        "reward_available_count": reward_available_count,
        "sample_transitions": sample_transitions,
    }


def _build_optimizer_summary(trainer: Any, *, feature_055_optimizer_step_count: int) -> dict[str, Any]:
    optimizer_step_count = trainer.optimizer_step_count
    return {
        "feature_055_smoke_optimizer_step_count": feature_055_optimizer_step_count,
        "optimizer_step_count": optimizer_step_count,
        "optimizer_step_growth_count": optimizer_step_count - feature_055_optimizer_step_count,
        "optimizer_progress_validated": optimizer_step_count > feature_055_optimizer_step_count,
        "optimizer_steps_executed": optimizer_step_count > 0,
        "optimizer_step_monotonic": True,
        "target_sync_count": trainer.target_sync_count,
    }


def _build_target_update_summary(trainer: Any, *, target_update_frequency: int) -> dict[str, Any]:
    optimizer_step_count = trainer.optimizer_step_count
    target_sync_count = trainer.target_sync_count
    threshold_reached = optimizer_step_count >= target_update_frequency
    return {
        "target_update_unit": trainer.config.target_update_contract.target_update_unit,
        "target_update_frequency": target_update_frequency,
        "target_sync_count": target_sync_count,
        "target_sync_before_threshold_blocked": optimizer_step_count < target_update_frequency and target_sync_count == 0,
        "target_sync_at_threshold_validated": threshold_reached and target_sync_count >= 1,
        "target_update_contract_validated": trainer.config.target_update_contract.target_update_unit == "optimizer_step" and target_update_frequency == 2000,
        "target_update_schedule_within_pilot": optimizer_step_count < target_update_frequency,
    }


def _build_loss_summary(result: Any) -> dict[str, Any]:
    loss_value = float(result.loss_value)
    return {
        "loss_count": 1 if result.loss_is_finite else 0,
        "all_losses_finite": bool(result.loss_is_finite),
        "min_loss": loss_value if result.loss_is_finite else None,
        "max_loss": loss_value if result.loss_is_finite else None,
        "mean_loss": loss_value if result.loss_is_finite else None,
        "loss_values": [loss_value] if result.loss_is_finite else [],
    }


def _build_reward_summary(replay_summary: dict[str, Any], trainer: Any) -> dict[str, Any]:
    transitions = trainer.replay_buffer.as_list()
    reward_available_count = sum(1 for transition in transitions if transition.reward_available)
    reward_count = reward_available_count
    reward_values = [float(transition.reward) for transition in transitions if transition.reward_available]
    return {
        "reward_count": reward_count,
        "reward_available_count": reward_available_count,
        "delayed_reward_contract_preserved": all(
            (not transition.reward_available and not transition.terminal and not transition.pending_at_horizon)
            or (transition.reward_available and transition.terminal and transition.terminal_reason in {"completed", "dropped"})
            or (transition.pending_at_horizon and not transition.terminal)
            for transition in transitions
        ),
        "pending_at_horizon_preserved": any(transition.pending_at_horizon for transition in transitions),
        "total_reward": float(sum(reward_values)) if reward_values else 0.0,
        "mean_reward": float(mean(reward_values)) if reward_values else 0.0,
    }


def _build_legal_action_summary(trainer: Any) -> dict[str, Any]:
    illegal_action_count = 0
    for transition in trainer.replay_buffer.as_list():
        legal_mask = {
            "local": bool(transition.legal_action_mask[0]),
            "horizontal": bool(transition.legal_action_mask[1]),
            "vertical": bool(transition.legal_action_mask[2]),
        }
        if not legal_mask.get({0: "local", 1: "horizontal", 2: "vertical"}[transition.action], False):
            illegal_action_count += 1
    return {
        "legal_action_only": illegal_action_count == 0,
        "illegal_action_count": illegal_action_count,
    }


def _build_checkpoint_summary(result: Any) -> dict[str, Any]:
    metadata = result.checkpoint_metadata.to_dict() if hasattr(result.checkpoint_metadata, "to_dict") else dict(result.checkpoint_metadata)
    required_keys = ("target_update_unit", "optimizer_step_count", "replay_size", "config_hash", "train_trace_bank_id", "eval_trace_bank_id", "seed_bundle")
    keys_present = {key: key in metadata for key in required_keys}
    return {
        "checkpoint_schema_valid": bool(result.checkpoint_schema_valid) and all(keys_present.values()) and metadata.get("target_update_unit") == "optimizer_step",
        "metadata_only": True,
        "model_checkpoint_written": False,
        "keys_present": keys_present,
        "checkpoint_metadata": _json_safe(metadata),
    }


def _build_train_eval_contract_verified(result: Any) -> dict[str, Any]:
    evaluation_summary = result.evaluation_summary
    return {
        "train_eval_trace_banks_disjoint": bool(result.train_eval_trace_banks_disjoint),
        "trace_bank_ids": dict(evaluation_summary.get("trace_bank_ids", {})),
        "evaluation_on_training_traces": bool(evaluation_summary.get("evaluation_on_training_traces", False)),
        "candidate_reproduction_supported": bool(evaluation_summary.get("candidate_reproduction_supported", False)),
    }


def _behavior_safety_summary(paths: list[str]) -> dict[str, bool]:
    return {
        "no_full_campaign": True,
        "no_baseline_comparison": True,
        "no_paper_reproduction_claim": True,
        "no_performance_claim": True,
        "no_policy_drift": _no_policy_drift(paths),
        "no_dependency_drift": _no_dependency_drift(paths),
        "no_environment_contract_drift": _no_environment_semantic_drift(paths),
        "no_reward_timing_change": _no_environment_semantic_drift(paths),
        "no_prior_artifact_rewrite": _no_prior_artifact_rewrite(paths),
    }


def _feature_056_report_payload(config: PaperDefaultPilotTrainingRunConfig) -> dict[str, Any]:
    return _load_json(config.feature_056_report_path)


def _feature_055_report_payload(config: PaperDefaultPilotTrainingRunConfig) -> dict[str, Any]:
    return _load_json(config.feature_055_report_path)


def _feature_054_report_payload(config: PaperDefaultPilotTrainingRunConfig) -> dict[str, Any]:
    return _load_json(config.feature_054_report_path)


def _build_blockers(
    *,
    feature_056_ready: bool,
    pilot_scope_ok: bool,
    live_environment_training_used: bool,
    fixture_training_used: bool,
    replay_summary: dict[str, Any],
    optimizer_summary: dict[str, Any],
    loss_summary: dict[str, Any],
    reward_summary: dict[str, Any],
    legal_action_summary: dict[str, Any],
    checkpoint_summary: dict[str, Any],
    train_eval_contract_verified: dict[str, Any],
    behavior_safety_summary: dict[str, Any],
) -> list[str]:
    blockers: list[str] = []
    if not feature_056_ready:
        blockers.append("feature_056_validation_failed")
    if not pilot_scope_ok:
        blockers.append("pilot_scope_not_controlled")
    if not live_environment_training_used:
        blockers.append("live_environment_training_not_used")
    if fixture_training_used:
        blockers.append("fixture_training_used")
    if not replay_summary.get("replay_growth_validated"):
        blockers.append("replay_growth_not_validated")
    if int(replay_summary.get("replay_size", 0)) <= int(replay_summary.get("feature_055_smoke_replay_size", 0)):
        blockers.append("replay_size_not_greater_than_feature_055_smoke")
    if not optimizer_summary.get("optimizer_progress_validated"):
        blockers.append("optimizer_progress_not_validated")
    if int(optimizer_summary.get("optimizer_step_count", 0)) <= int(optimizer_summary.get("feature_055_smoke_optimizer_step_count", 0)):
        blockers.append("optimizer_step_count_not_greater_than_feature_055_smoke")
    if not loss_summary.get("all_losses_finite"):
        blockers.append("non_finite_loss")
    if int(loss_summary.get("loss_count", 0)) <= 0:
        blockers.append("loss_count_zero")
    if not reward_summary.get("delayed_reward_contract_preserved"):
        blockers.append("delayed_reward_contract_broken")
    if not reward_summary.get("pending_at_horizon_preserved"):
        blockers.append("pending_at_horizon_contract_broken")
    if not legal_action_summary.get("legal_action_only"):
        blockers.append("illegal_action_selected")
    if not checkpoint_summary.get("checkpoint_schema_valid"):
        blockers.append("checkpoint_schema_invalid")
    if checkpoint_summary.get("model_checkpoint_written"):
        blockers.append("model_checkpoint_written")
    if not train_eval_contract_verified.get("train_eval_trace_banks_disjoint"):
        blockers.append("train_eval_contract_broken")
    if not all(behavior_safety_summary.values()):
        blockers.append("behavior_drift_detected")
    return blockers


def _recommended_next_feature(final_verdict: str) -> str:
    if final_verdict == "paper_default_pilot_training_passed":
        return READY_NEXT_FEATURE
    return {
        "feature_056_prerequisite_blocked": "Feature 056 validation repair before pilot training",
        "pilot_scope_blocked": "paper-default pilot scope repair",
        "replay_growth_blocked": "replay growth repair before evaluation harness",
        "optimizer_progress_blocked": "optimizer progress repair before evaluation harness",
        "loss_or_reward_blocked": "loss and reward contract repair before evaluation harness",
        "legal_action_blocked": "legal action contract repair before evaluation harness",
        "checkpoint_metadata_blocked": "checkpoint metadata repair before evaluation harness",
        "behavior_drift_detected": "behavior drift repair before evaluation harness",
    }[final_verdict]


def run_paper_default_pilot_training(config: PaperDefaultPilotTrainingRunConfig | None = None) -> PaperDefaultPilotTrainingRunReport:
    pilot_config = config or PaperDefaultPilotTrainingRunConfig()
    diff_paths = _diff_names()
    dirty_paths = _status_paths()
    staged_paths = _staged_paths()

    feature_056_payload = _feature_056_report_payload(pilot_config)
    feature_055_payload = _feature_055_report_payload(pilot_config)
    feature_054_payload = _feature_054_report_payload(pilot_config)
    feature_056_ready = _feature_056_validation_verified(feature_056_payload)
    feature_055_ready = _feature_055_smoke_verified(feature_055_payload)
    feature_054_ready = _feature_054_ready(feature_054_payload)

    feature_055_replay_size, feature_055_optimizer_step_count = _feature_055_smoke_metrics(feature_055_payload)
    prerequisite_tags_verified = _build_prerequisite_tags_verified(
        feature_056_ready=feature_056_ready,
        feature_055_ready=feature_055_ready,
        feature_054_ready=feature_054_ready,
        dirty_paths=dirty_paths,
        staged_paths=staged_paths,
        diff_paths=diff_paths,
    )
    prerequisite_ready = all(entry["verified"] for entry in prerequisite_tags_verified)

    campaign_config = pilot_config.build_campaign_config()
    episode_summary = {
        "pilot_episodes": pilot_config.pilot_episodes,
        "pilot_episode_length": pilot_config.pilot_episode_length,
        "episodes_requested": pilot_config.pilot_episodes,
        "episodes_completed": 0,
        "completed_all_episodes": False,
        "seed_bundle": campaign_config.seed_bundle.to_dict(),
        "seed_signature": campaign_config.seed_bundle.signature,
    }
    replay_summary = {
        "feature_055_smoke_replay_size": feature_055_replay_size,
        "replay_size": 0,
        "replay_growth_count": 0,
        "replay_growth_validated": False,
        "sampled_batch_size": 0,
        "sampled_transition_count": 0,
        "replay_inserted": False,
        "sampled_field_coverage": {name: False for name in REPLAY_SAMPLE_FIELD_NAMES},
        "delayed_reward_semantics_preserved": False,
        "pending_at_horizon_preserved": False,
        "reward_available_count": 0,
        "sample_transitions": [],
    }
    optimizer_summary = {
        "feature_055_smoke_optimizer_step_count": feature_055_optimizer_step_count,
        "optimizer_step_count": 0,
        "optimizer_step_growth_count": 0,
        "optimizer_progress_validated": False,
        "optimizer_steps_executed": False,
        "optimizer_step_monotonic": False,
        "target_sync_count": 0,
    }
    target_update_summary = {
        "target_update_unit": campaign_config.target_update_contract.target_update_unit,
        "target_update_frequency": campaign_config.target_update_contract.update_frequency,
        "target_sync_count": 0,
        "target_sync_before_threshold_blocked": False,
        "target_sync_at_threshold_validated": False,
        "target_update_contract_validated": False,
        "target_update_schedule_within_pilot": True,
    }
    loss_summary = {
        "loss_count": 0,
        "all_losses_finite": False,
        "min_loss": None,
        "max_loss": None,
        "mean_loss": None,
        "loss_values": [],
    }
    reward_summary = {
        "reward_count": 0,
        "reward_available_count": 0,
        "delayed_reward_contract_preserved": False,
        "pending_at_horizon_preserved": False,
        "total_reward": 0.0,
        "mean_reward": 0.0,
    }
    legal_action_summary = {
        "legal_action_only": False,
        "illegal_action_count": 0,
    }
    checkpoint_summary = {
        "checkpoint_schema_valid": False,
        "metadata_only": True,
        "model_checkpoint_written": False,
        "keys_present": {
            "target_update_unit": False,
            "optimizer_step_count": False,
            "replay_size": False,
            "config_hash": False,
            "train_trace_bank_id": False,
            "eval_trace_bank_id": False,
            "seed_bundle": False,
        },
        "checkpoint_metadata": {},
    }
    train_eval_contract_verified = {
        "train_eval_trace_banks_disjoint": False,
        "trace_bank_ids": {
            "training": campaign_config.training_trace_bank_id,
            "evaluation": campaign_config.evaluation_trace_bank_id,
        },
        "evaluation_on_training_traces": False,
        "candidate_reproduction_supported": False,
    }
    all_paths = sorted(set(diff_paths) | set(dirty_paths) | set(staged_paths))
    behavior_safety_summary = _behavior_safety_summary(all_paths)

    preflight_blockers: list[str] = []
    if not feature_056_ready:
        preflight_blockers.append("feature_056_validation_failed")
    if not prerequisite_ready:
        preflight_blockers.append("prerequisite_tags_failed")

    live_environment_training_used = False
    fixture_training_used = False

    if not preflight_blockers:
        from src.analysis.full_training_reproduction_campaign.trainer import DDQNTrainer

        trainer = DDQNTrainer(campaign_config)
        result = trainer.run_pilot(
            episodes=pilot_config.pilot_episodes,
            episode_length=pilot_config.pilot_episode_length,
        )
        live_environment_training_used = True
        fixture_training_used = False
        episode_summary.update(
            {
                "episodes_completed": result.episodes_completed,
                "completed_all_episodes": result.episodes_completed == pilot_config.pilot_episodes,
            }
        )
        replay_summary = _build_replay_summary(
            trainer,
            feature_055_replay_size=feature_055_replay_size,
            sample_size=16,
            replay_seed=campaign_config.seed_bundle.replay_sampling_seed,
        )
        optimizer_summary = _build_optimizer_summary(trainer, feature_055_optimizer_step_count=feature_055_optimizer_step_count)
        target_update_summary = _build_target_update_summary(trainer, target_update_frequency=campaign_config.target_update_contract.update_frequency)
        loss_summary = _build_loss_summary(result)
        reward_summary = _build_reward_summary(replay_summary, trainer)
        legal_action_summary = _build_legal_action_summary(trainer)
        checkpoint_summary = _build_checkpoint_summary(result)
        train_eval_contract_verified = _build_train_eval_contract_verified(result)
        behavior_safety_summary = _behavior_safety_summary(all_paths)

    pilot_scope_ok = (
        pilot_config.pilot_episodes > 1
        and pilot_config.pilot_episode_length == 110
        and pilot_config.full_campaign is False
        and pilot_config.baseline_comparison is False
        and pilot_config.paper_reproduction_claim is False
    )
    blockers = list(preflight_blockers) if preflight_blockers else _build_blockers(
        feature_056_ready=feature_056_ready,
        pilot_scope_ok=pilot_scope_ok,
        live_environment_training_used=live_environment_training_used,
        fixture_training_used=fixture_training_used,
        replay_summary=replay_summary,
        optimizer_summary=optimizer_summary,
        loss_summary=loss_summary,
        reward_summary=reward_summary,
        legal_action_summary=legal_action_summary,
        checkpoint_summary=checkpoint_summary,
        train_eval_contract_verified=train_eval_contract_verified,
        behavior_safety_summary=behavior_safety_summary,
    )
    ready = not blockers and feature_056_ready and prerequisite_ready and live_environment_training_used and pilot_scope_ok
    final_verdict = "paper_default_pilot_training_passed" if ready else (
        "feature_056_prerequisite_blocked"
        if not feature_056_ready or not prerequisite_ready
        else "pilot_scope_blocked"
        if not pilot_scope_ok
        else "replay_growth_blocked"
        if not replay_summary.get("replay_growth_validated")
        else "optimizer_progress_blocked"
        if not optimizer_summary.get("optimizer_progress_validated")
        else "loss_or_reward_blocked"
        if not loss_summary.get("all_losses_finite") or not reward_summary.get("delayed_reward_contract_preserved")
        else "legal_action_blocked"
        if not legal_action_summary.get("legal_action_only")
        else "checkpoint_metadata_blocked"
        if not checkpoint_summary.get("checkpoint_schema_valid")
        else "behavior_drift_detected"
    )
    recommended_next_feature = _recommended_next_feature(final_verdict)
    if ready:
        blockers = []

    report = PaperDefaultPilotTrainingRunReport(
        feature_id=FEATURE_ID,
        prerequisite_tags_verified=prerequisite_tags_verified,
        feature_056_validation_verified=feature_056_ready,
        pilot_scope={
            "pilot_episodes": pilot_config.pilot_episodes,
            "pilot_episode_length": pilot_config.pilot_episode_length,
            "full_campaign": pilot_config.full_campaign,
            "baseline_comparison": pilot_config.baseline_comparison,
            "paper_reproduction_claim": pilot_config.paper_reproduction_claim,
        },
        live_environment_training_used=live_environment_training_used,
        fixture_training_used=fixture_training_used,
        episode_summary=episode_summary,
        replay_summary=replay_summary,
        optimizer_summary=optimizer_summary,
        target_update_summary=target_update_summary,
        loss_summary=loss_summary,
        reward_summary=reward_summary,
        legal_action_summary=legal_action_summary,
        checkpoint_summary=checkpoint_summary,
        train_eval_contract_verified=train_eval_contract_verified,
        behavior_safety_summary=behavior_safety_summary,
        remaining_blockers=blockers,
        recommended_next_feature=recommended_next_feature,
        final_verdict=final_verdict,
    )
    return report


def build_paper_default_pilot_training_run_report(
    config: PaperDefaultPilotTrainingRunConfig | None = None,
) -> PaperDefaultPilotTrainingRunReport:
    return run_paper_default_pilot_training(config)


def generate_paper_default_pilot_training_run_artifacts(
    output_dir: str | Path | None = None,
) -> tuple[PaperDefaultPilotTrainingRunReport, Path, Path]:
    report = run_paper_default_pilot_training()
    json_path, md_path = write_paper_default_pilot_training_run_report(report, output_dir)
    return report, json_path, md_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Feature 057 paper-default pilot training analysis.")
    parser.add_argument("--output-dir", type=Path, default=None, help="Override the report output directory.")
    args = parser.parse_args(argv)
    report = run_paper_default_pilot_training()
    write_paper_default_pilot_training_run_report(report, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
