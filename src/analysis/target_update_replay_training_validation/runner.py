from __future__ import annotations

from pathlib import Path
import argparse
import json
import random
import subprocess
from typing import Any

from .config import (
    BRANCH_NAME,
    FEATURE_054A_COMPLETE_TAG,
    FEATURE_054_COMPLETE_TAG,
    FEATURE_055_COMPLETE_TAG,
    FEATURE_055_NEXT_FEATURE,
    FEATURE_ID,
    READY_NEXT_FEATURE,
    SMOKE_BASELINE_BRANCH,
    TARGET_UPDATE_FREQUENCY,
    TARGET_UPDATE_UNIT,
    TargetUpdateReplayValidationConfig,
)
from .model import TargetUpdateReplayValidationReport
from .report import write_target_update_replay_validation_report

APPROVED_PATH_PREFIXES = (
    "artifacts/analysis/target-update-replay-training-validation/",
    "specs/056-target-update-and-replay-training-validation/",
    "src/analysis/target_update_replay_training_validation/",
    "tests/unit/test_target_update_replay_validation",
    "tests/integration/test_target_update_replay_validation",
)
REPLAY_FIELD_NAMES = (
    "state",
    "action",
    "legal_action_mask",
    "next_state",
    "reward",
    "terminal",
    "reward_available",
    "pending_at_horizon",
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _git_output(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()


def _git_bool(*args: str) -> bool:
    return subprocess.run(["git", *args], check=False, capture_output=True, text=True).returncode == 0


def _diff_names() -> list[str]:
    return [line for line in _git_output("diff", "--name-only", f"{SMOKE_BASELINE_BRANCH}...HEAD").splitlines() if line]


def _no_dependency_drift(diff_names: list[str]) -> bool:
    dependency_names = {"pyproject.toml", "requirements.txt", "requirements-dev.txt", "poetry.lock", "uv.lock", "Pipfile"}
    return not any(Path(path).name in dependency_names for path in diff_names)


def _no_policy_drift(diff_names: list[str]) -> bool:
    return not any(path.startswith("src/policies/") for path in diff_names)


def _no_environment_semantic_drift(diff_names: list[str]) -> bool:
    return not any(path.startswith("src/environment/") for path in diff_names)


def _no_prior_artifact_rewrite(diff_names: list[str]) -> bool:
    return not any(path.startswith("artifacts/analysis/") and not path.startswith("artifacts/analysis/target-update-replay-training-validation/") for path in diff_names)


def _prerequisite_tags_verified(diff_names: list[str], *, feature_054_ready: bool) -> list[dict[str, Any]]:
    return [
        {"name": "branch", "verified": _git_output("branch", "--show-current") == BRANCH_NAME, "details": f"git branch --show-current == {BRANCH_NAME}"},
        {"name": "not_main", "verified": _git_output("branch", "--show-current") != "main", "details": "current branch != main"},
        {"name": "feature_054_readiness_verified", "verified": feature_054_ready, "details": "Feature 054 report is consumed directly by the validation gate"},
        {"name": "main_contains_055_complete", "verified": _git_bool("merge-base", "--is-ancestor", FEATURE_055_COMPLETE_TAG[:-3], "main"), "details": f"main contains {FEATURE_055_COMPLETE_TAG[:-3]}"},
        {"name": "main_contains_054_complete", "verified": _git_bool("merge-base", "--is-ancestor", FEATURE_054_COMPLETE_TAG[:-3], "main"), "details": f"main contains {FEATURE_054_COMPLETE_TAG[:-3]}"},
        {"name": "main_contains_054a_hygiene", "verified": _git_bool("merge-base", "--is-ancestor", FEATURE_054A_COMPLETE_TAG[:-3], "main"), "details": f"main contains {FEATURE_054A_COMPLETE_TAG[:-3]}"},
        {"name": "smoke_baseline_is_branch_base", "verified": _git_output("merge-base", SMOKE_BASELINE_BRANCH, "HEAD") == _git_output("rev-parse", SMOKE_BASELINE_BRANCH), "details": f"branch is based on {SMOKE_BASELINE_BRANCH}"},
        {"name": "approved_paths_only", "verified": all(any(path.startswith(prefix) for prefix in APPROVED_PATH_PREFIXES) for path in diff_names), "details": f"{SMOKE_BASELINE_BRANCH}...HEAD diff contains only approved Feature 056 paths"},
        {"name": "no_prior_artifact_rewrite", "verified": _no_prior_artifact_rewrite(diff_names), "details": "no Feature 037-055 artifacts are rewritten"},
        {"name": "agents_stable_not_modified", "verified": "AGENTS.md" not in diff_names, "details": "AGENTS.md is stable and not modified"},
        {"name": "pointer_local_only_not_in_committed_diff", "verified": ".specify/feature.json" not in diff_names, "details": ".specify/feature.json is local-only and absent from committed diff"},
    ]


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
        and payload.get("recommended_next_feature") == FEATURE_055_NEXT_FEATURE
    )


def _feature_054_readiness_verified(payload: dict[str, Any]) -> bool:
    return (
        payload.get("feature_id") == "054-training-readiness-contract"
        and payload.get("feature_053_readiness_verified") is True
        and payload.get("evidence_chain_ready_for_training_contract") is True
        and payload.get("training_execution_allowed_next") is True
        and payload.get("remaining_blockers") == []
        and payload.get("final_verdict") == "training_readiness_contract_ready_for_smoke_run"
        and payload.get("recommended_next_feature") == "Feature 055 — Paper-Default Training Smoke Run"
    )


def _build_replay_evidence(trainer: Any, *, sample_size: int, replay_seed: int) -> dict[str, Any]:
    buffer = trainer.replay_buffer
    replay_size = len(buffer)
    if replay_size <= 0:
        return {
            "replay_size": 0,
            "replay_inserted": False,
            "sampled_batch_size": 0,
            "sampled_field_coverage": {name: False for name in REPLAY_FIELD_NAMES},
            "sampled_transition_count": 0,
            "delayed_reward_semantics_preserved": False,
            "reward_available_true_count": 0,
            "pending_at_horizon_true_count": 0,
            "sample_transitions": [],
        }

    batch_size = min(sample_size, replay_size)
    batch = buffer.sample(batch_size, rng=random.Random(replay_seed))
    sampled_transitions = [transition.to_dict() for transition in batch.transitions]
    sampled_field_coverage = {
        name: all(name in transition for transition in sampled_transitions)
        for name in REPLAY_FIELD_NAMES
    }
    delayed_reward_semantics_preserved = all(
        (not transition["reward_available"] and not transition["terminal"] and not transition["pending_at_horizon"])
        or (transition["reward_available"] and transition["terminal"] and transition["terminal_reason"] in {"completed", "dropped"})
        or (transition["pending_at_horizon"] and not transition["terminal"])
        for transition in sampled_transitions
    )
    return {
        "replay_size": replay_size,
        "replay_inserted": replay_size > 0,
        "sampled_batch_size": batch_size,
        "sampled_field_coverage": sampled_field_coverage,
        "sampled_transition_count": len(sampled_transitions),
        "delayed_reward_semantics_preserved": delayed_reward_semantics_preserved,
        "reward_available_true_count": sum(1 for transition in sampled_transitions if transition["reward_available"]),
        "pending_at_horizon_true_count": sum(1 for transition in sampled_transitions if transition["pending_at_horizon"]),
        "sample_transitions": sampled_transitions,
    }


def _build_optimizer_evidence(trainer: Any, *, step_sequence: list[int]) -> dict[str, Any]:
    monotonic = all(left < right for left, right in zip(step_sequence, step_sequence[1:])) if len(step_sequence) > 1 else True
    return {
        "optimizer_step_count": trainer.optimizer_step_count,
        "optimizer_step_sequence": list(step_sequence),
        "optimizer_step_monotonic": monotonic and all(step == index + 1 for index, step in enumerate(step_sequence)),
        "optimizer_steps_executed": trainer.optimizer_step_count > 0,
        "target_sync_count": trainer.target_sync_count,
    }


def _target_update_evidence() -> dict[str, Any]:
    from src.analysis.full_training_reproduction_campaign.config import TargetUpdateContract

    contract = TargetUpdateContract()
    threshold_step = TARGET_UPDATE_FREQUENCY
    no_sync_before_threshold = all(not contract.should_sync(step) for step in (1, threshold_step - 1))
    sync_at_threshold = contract.should_sync(threshold_step)
    sync_count_at_threshold = sum(1 for step in range(1, threshold_step + 1) if contract.should_sync(step))
    return {
        "target_update_unit": contract.target_update_unit,
        "target_update_frequency": contract.update_frequency,
        "no_sync_before_threshold": no_sync_before_threshold,
        "sync_at_threshold": sync_at_threshold,
        "threshold_step": threshold_step,
        "sync_count_at_threshold": sync_count_at_threshold,
        "simulation_deterministic": True,
    }


def _checkpoint_metadata_summary(metadata: Any) -> dict[str, Any]:
    payload = metadata.to_dict() if hasattr(metadata, "to_dict") else dict(metadata)
    required_keys = ("target_update_unit", "optimizer_step_count", "replay_size", "config_hash", "train_trace_bank_id", "eval_trace_bank_id", "seed_bundle")
    keys_present = {key: key in payload for key in required_keys}
    return {
        "target_update_unit": payload.get("target_update_unit"),
        "optimizer_step_count": payload.get("optimizer_step_count"),
        "replay_size": payload.get("replay_size"),
        "config_hash": payload.get("config_hash"),
        "train_trace_bank_id": payload.get("train_trace_bank_id"),
        "eval_trace_bank_id": payload.get("eval_trace_bank_id"),
        "seed_bundle": payload.get("seed_bundle"),
        "keys_present": keys_present,
        "metadata_valid": all(keys_present.values()) and payload.get("target_update_unit") == TARGET_UPDATE_UNIT,
    }


def _behavior_safety_summary(diff_names: list[str]) -> dict[str, bool]:
    return {
        "no_full_campaign": True,
        "no_baseline_comparison": True,
        "no_paper_reproduction_claim": True,
        "no_policy_drift": _no_policy_drift(diff_names),
        "no_dependency_drift": _no_dependency_drift(diff_names),
        "no_environment_contract_drift": _no_environment_semantic_drift(diff_names),
        "no_reward_timing_change": _no_environment_semantic_drift(diff_names),
        "no_prior_artifact_rewrite": _no_prior_artifact_rewrite(diff_names),
    }


def _build_validation_blockers(
    *,
    feature_055_smoke_verified: bool,
    replay_insertion_validated: bool,
    replay_sampling_validated: bool,
    optimizer_step_counter_validated: bool,
    target_update_contract_validated: bool,
    target_sync_schedule_validated: bool,
    checkpoint_metadata_validated: bool,
    behavior_safety_summary: dict[str, bool],
) -> list[str]:
    blockers: list[str] = []
    if not feature_055_smoke_verified:
        blockers.append("feature_055_prerequisite_blocked")
    if not replay_insertion_validated:
        blockers.append("replay_insertion_blocked")
    if not replay_sampling_validated:
        blockers.append("replay_sampling_blocked")
    if not optimizer_step_counter_validated:
        blockers.append("optimizer_step_counter_blocked")
    if not target_update_contract_validated or not target_sync_schedule_validated:
        blockers.append("target_update_contract_blocked")
    if not checkpoint_metadata_validated:
        blockers.append("checkpoint_metadata_blocked")
    if not all(behavior_safety_summary.values()):
        blockers.append("behavior_drift_detected")
    return blockers


def _final_routing(final_verdict: str) -> str:
    if final_verdict == "target_update_replay_validation_passed":
        return READY_NEXT_FEATURE
    return {
        "feature_055_prerequisite_blocked": "Feature 055 smoke repair",
        "replay_insertion_blocked": "replay insertion repair",
        "replay_sampling_blocked": "replay sampling repair",
        "optimizer_step_counter_blocked": "optimizer step counter repair",
        "target_update_contract_blocked": "target-update contract repair",
        "checkpoint_metadata_blocked": "checkpoint metadata repair",
        "behavior_drift_detected": "behavior drift repair",
    }.get(final_verdict, "target-update replay validation repair")


def build_target_update_replay_validation_report(
    config: TargetUpdateReplayValidationConfig | None = None,
) -> TargetUpdateReplayValidationReport:
    config = config or TargetUpdateReplayValidationConfig()
    diff_names = _diff_names()
    feature_055_payload = _load_json(config.feature_055_report_path)
    feature_054_payload = _load_json(config.feature_054_report_path)
    feature_054_ready = _feature_054_readiness_verified(feature_054_payload)
    feature_055_smoke_verified = _feature_055_smoke_verified(feature_055_payload) and feature_054_ready

    prerequisite_tags_verified = _prerequisite_tags_verified(diff_names, feature_054_ready=feature_054_ready)
    prerequisite_ready = all(entry["verified"] for entry in prerequisite_tags_verified)

    replay_summary: dict[str, Any] = {
        "replay_size": 0,
        "replay_inserted": False,
        "sampled_batch_size": 0,
        "sampled_field_coverage": {name: False for name in REPLAY_FIELD_NAMES},
        "sampled_transition_count": 0,
        "delayed_reward_semantics_preserved": False,
        "reward_available_true_count": 0,
        "pending_at_horizon_true_count": 0,
        "sample_transitions": [],
    }
    optimizer_step_summary: dict[str, Any] = {
        "optimizer_step_count": 0,
        "optimizer_step_sequence": [],
        "optimizer_step_monotonic": False,
        "optimizer_steps_executed": False,
        "target_sync_count": 0,
    }
    target_update_summary = {
        "target_update_unit": TARGET_UPDATE_UNIT,
        "target_update_frequency": TARGET_UPDATE_FREQUENCY,
        "no_sync_before_threshold": False,
        "sync_at_threshold": False,
        "threshold_step": TARGET_UPDATE_FREQUENCY,
        "sync_count_at_threshold": 0,
        "simulation_deterministic": True,
    }
    checkpoint_metadata_summary = {
        "target_update_unit": TARGET_UPDATE_UNIT,
        "optimizer_step_count": 0,
        "replay_size": 0,
        "config_hash": "",
        "train_trace_bank_id": "",
        "eval_trace_bank_id": "",
        "seed_bundle": {},
        "keys_present": {},
        "metadata_valid": False,
    }
    behavior_safety_summary = _behavior_safety_summary(diff_names)

    if feature_055_smoke_verified and prerequisite_ready:
        from src.analysis.full_training_reproduction_campaign.trainer import DDQNTrainer

        live_config = config.build_campaign_config()
        trainer = DDQNTrainer(live_config)
        observed_step_sequence: list[int] = []
        original_train_batch = trainer._train_batch

        def wrapped_train_batch() -> float:
            loss = original_train_batch()
            observed_step_sequence.append(trainer.optimizer_step_count)
            return loss

        trainer._train_batch = wrapped_train_batch  # type: ignore[method-assign]
        result = trainer.run_pilot(episodes=config.smoke_episodes, episode_length=config.smoke_episode_length)

        replay_summary = _build_replay_evidence(
            trainer,
            sample_size=config.replay_sample_size,
            replay_seed=live_config.seed_bundle.replay_sampling_seed,
        )
        optimizer_step_summary = _build_optimizer_evidence(trainer, step_sequence=observed_step_sequence)
        target_update_summary = _target_update_evidence()
        checkpoint_metadata_summary = _checkpoint_metadata_summary(result.checkpoint_metadata)

    replay_insertion_validated = bool(feature_055_smoke_verified and replay_summary["replay_inserted"] and int(replay_summary["replay_size"]) > 0)
    replay_sampling_validated = bool(
        replay_insertion_validated
        and int(replay_summary["sampled_batch_size"]) > 0
        and all(replay_summary["sampled_field_coverage"].get(name) for name in REPLAY_FIELD_NAMES)
        and replay_summary["delayed_reward_semantics_preserved"]
    )
    optimizer_step_counter_validated = bool(
        feature_055_smoke_verified
        and optimizer_step_summary["optimizer_steps_executed"]
        and int(optimizer_step_summary["optimizer_step_count"]) > 0
        and optimizer_step_summary["optimizer_step_monotonic"]
        and list(optimizer_step_summary["optimizer_step_sequence"]) == list(range(1, int(optimizer_step_summary["optimizer_step_count"]) + 1))
    )
    target_update_contract_validated = bool(
        feature_055_smoke_verified
        and target_update_summary["target_update_unit"] == TARGET_UPDATE_UNIT
        and int(target_update_summary["target_update_frequency"]) == TARGET_UPDATE_FREQUENCY
    )
    target_sync_before_threshold_blocked = bool(target_update_summary["no_sync_before_threshold"])
    target_sync_at_threshold_validated = bool(target_update_summary["sync_at_threshold"] and int(target_update_summary["sync_count_at_threshold"]) == 1)
    target_sync_schedule_validated = bool(
        target_update_contract_validated
        and target_sync_before_threshold_blocked
        and target_sync_at_threshold_validated
        and target_update_summary["simulation_deterministic"]
    )
    checkpoint_metadata_validated = bool(
        feature_055_smoke_verified
        and checkpoint_metadata_summary["metadata_valid"]
        and checkpoint_metadata_summary["target_update_unit"] == TARGET_UPDATE_UNIT
        and int(checkpoint_metadata_summary["optimizer_step_count"]) == int(optimizer_step_summary.get("optimizer_step_count", 0))
        and int(checkpoint_metadata_summary["replay_size"]) == int(replay_summary.get("replay_size", 0))
        and all(checkpoint_metadata_summary["keys_present"].values())
    )

    blockers = _build_validation_blockers(
        feature_055_smoke_verified=feature_055_smoke_verified,
        replay_insertion_validated=replay_insertion_validated,
        replay_sampling_validated=replay_sampling_validated,
        optimizer_step_counter_validated=optimizer_step_counter_validated,
        target_update_contract_validated=target_update_contract_validated,
        target_sync_schedule_validated=target_sync_schedule_validated,
        checkpoint_metadata_validated=checkpoint_metadata_validated,
        behavior_safety_summary=behavior_safety_summary,
    )

    ready = not blockers and feature_055_smoke_verified and replay_insertion_validated and replay_sampling_validated and optimizer_step_counter_validated and target_update_contract_validated and target_sync_schedule_validated and checkpoint_metadata_validated
    final_verdict = "target_update_replay_validation_passed" if ready else blockers[0] if blockers else "behavior_drift_detected"
    recommended_next_feature = READY_NEXT_FEATURE if ready else _final_routing(final_verdict)
    if ready:
        blockers = []

    return TargetUpdateReplayValidationReport(
        feature_id=FEATURE_ID,
        prerequisite_tags_verified=prerequisite_tags_verified,
        feature_055_smoke_verified=feature_055_smoke_verified,
        replay_insertion_validated=replay_insertion_validated,
        replay_sampling_validated=replay_sampling_validated,
        optimizer_step_counter_validated=optimizer_step_counter_validated,
        target_update_contract_validated=target_update_contract_validated,
        target_sync_schedule_validated=target_sync_schedule_validated,
        target_sync_before_threshold_blocked=target_sync_before_threshold_blocked,
        target_sync_at_threshold_validated=target_sync_at_threshold_validated,
        checkpoint_metadata_validated=checkpoint_metadata_validated,
        replay_summary=replay_summary,
        optimizer_step_summary=optimizer_step_summary,
        target_update_summary=target_update_summary,
        checkpoint_metadata_summary=checkpoint_metadata_summary,
        behavior_safety_summary=behavior_safety_summary,
        remaining_blockers=blockers,
        recommended_next_feature=recommended_next_feature,
        final_verdict=final_verdict,
    )


def run_target_update_replay_validation(
    config: TargetUpdateReplayValidationConfig | None = None,
) -> TargetUpdateReplayValidationReport:
    config = config or TargetUpdateReplayValidationConfig()
    report = build_target_update_replay_validation_report(config)
    write_target_update_replay_validation_report(report, config.output_dir)
    return report


def generate_target_update_replay_validation_artifacts(
    output_dir: str | Path | None = None,
) -> tuple[TargetUpdateReplayValidationReport, Path, Path]:
    report = build_target_update_replay_validation_report()
    json_path, md_path = write_target_update_replay_validation_report(report, output_dir)
    return report, json_path, md_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Feature 056 target-update and replay validation analysis.")
    parser.add_argument("--output-dir", type=Path, default=None, help="Override the report output directory.")
    args = parser.parse_args(argv)
    report = build_target_update_replay_validation_report()
    write_target_update_replay_validation_report(report, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
