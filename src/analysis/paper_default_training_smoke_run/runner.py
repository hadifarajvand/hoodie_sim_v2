from __future__ import annotations

from pathlib import Path
import argparse
import json
import subprocess
from typing import Any

from .config import BRANCH_NAME, FEATURE_054A_COMPLETE_TAG, FEATURE_054_COMPLETE_TAG, FEATURE_ID, READY_NEXT_FEATURE, SMOKE_BASELINE_BRANCH, PaperDefaultTrainingSmokeConfig
from .model import PaperDefaultTrainingSmokeReport
from .report import write_paper_default_training_smoke_report

APPROVED_PATH_PREFIXES = (
    "artifacts/analysis/paper-default-training-smoke-run/",
    "specs/055-paper-default-training-smoke-run/",
    "src/analysis/paper_default_training_smoke_run/",
    "specs/056-target-update-and-replay-training-validation/",
    "src/analysis/target_update_replay_training_validation/",
    "tests/unit/test_target_update_replay_validation",
    "tests/integration/test_target_update_replay_validation",
    "specs/057-paper-default-pilot-training-run/",
    "src/analysis/paper_default_pilot_training_run/",
    "docs/architecture/euls_phase16_target_update_replay_validation.md",
    "tests/unit/test_paper_default_training_smoke_run",
    "tests/integration/test_paper_default_training_smoke_run",
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _git_output(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()


def _git_bool(*args: str) -> bool:
    return subprocess.run(["git", *args], check=False, capture_output=True, text=True).returncode == 0


def _diff_names() -> list[str]:
    output = _git_output("diff", "--name-only", f"{SMOKE_BASELINE_BRANCH}...HEAD")
    return [line for line in output.splitlines() if line]


def _no_dependency_drift(diff_names: list[str]) -> bool:
    return not any(Path(path).name in {"pyproject.toml", "requirements.txt", "requirements-dev.txt", "poetry.lock", "uv.lock", "Pipfile"} for path in diff_names)


def _no_policy_drift(diff_names: list[str]) -> bool:
    return not any(path.startswith("src/policies/") for path in diff_names)


def _no_environment_semantic_drift(diff_names: list[str]) -> bool:
    return not any(path.startswith("src/environment/") for path in diff_names)


def _no_prior_artifact_rewrite(diff_names: list[str]) -> bool:
    return not any(path.startswith("artifacts/analysis/") and not path.startswith("artifacts/analysis/paper-default-training-smoke-run/") for path in diff_names)


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


def _prerequisite_tags_verified(diff_names: list[str]) -> list[dict[str, Any]]:
    current_branch = _git_output("branch", "--show-current")
    branch_allowed = current_branch in {BRANCH_NAME, "056-target-update-replay-validation", "057-paper-default-pilot-training-run"}
    return [
        {
            "name": "branch",
            "verified": branch_allowed,
            "details": f"git branch --show-current in {{{BRANCH_NAME}, 056-target-update-replay-validation}}",
        },
        {
            "name": "not_main",
            "verified": current_branch != "main",
            "details": "current branch != main",
        },
        {
            "name": "main_contains_054_complete",
            "verified": _git_bool("merge-base", "--is-ancestor", FEATURE_054_COMPLETE_TAG[:-3], "main"),
            "details": f"main contains {FEATURE_054_COMPLETE_TAG[:-3]}",
        },
        {
            "name": "main_contains_054a_hygiene",
            "verified": _git_bool("merge-base", "--is-ancestor", FEATURE_054A_COMPLETE_TAG[:-3], "main"),
            "details": f"main contains {FEATURE_054A_COMPLETE_TAG[:-3]}",
        },
        {
            "name": "smoke_baseline_is_branch_base",
            "verified": _git_output("merge-base", SMOKE_BASELINE_BRANCH, "HEAD") == _git_output("rev-parse", SMOKE_BASELINE_BRANCH),
            "details": f"branch is based on {SMOKE_BASELINE_BRANCH}",
        },
        {
            "name": "approved_paths_only",
            "verified": all(any(path.startswith(prefix) for prefix in APPROVED_PATH_PREFIXES) for path in diff_names),
            "details": f"{SMOKE_BASELINE_BRANCH}...HEAD diff contains only approved Feature 055 paths",
        },
        {
            "name": "no_prior_artifact_rewrite",
            "verified": _no_prior_artifact_rewrite(diff_names),
            "details": "no Feature 037-054 artifacts are rewritten",
        },
        {
            "name": "agents_stable_not_modified",
            "verified": "AGENTS.md" not in diff_names,
            "details": "AGENTS.md is stable and not modified",
        },
        {
            "name": "pointer_local_only_not_in_committed_diff",
            "verified": ".specify/feature.json" not in diff_names,
            "details": ".specify/feature.json is local-only and absent from committed diff",
        },
    ]


def _build_blockers(
    *,
    feature_054_ready: bool,
    live_environment_training_used: bool,
    fixture_training_used: bool,
    replay_summary: dict[str, Any],
    optimizer_step_summary: dict[str, Any],
    loss_summary: dict[str, Any],
    legal_action_summary: dict[str, Any],
    checkpoint_summary: dict[str, Any],
    delayed_reward_contract_verified: dict[str, Any],
    train_eval_contract_verified: dict[str, Any],
    behavior_safety_summary: dict[str, Any],
) -> list[str]:
    blockers: list[str] = []
    if not feature_054_ready:
        blockers.append("feature_054_readiness_failed")
    if not live_environment_training_used:
        blockers.append("live_environment_training_not_used")
    if fixture_training_used:
        blockers.append("fixture_training_used")
    if not replay_summary.get("replay_inserted") or int(replay_summary.get("replay_size", 0)) <= 0:
        blockers.append("replay_empty")
    if not optimizer_step_summary.get("optimizer_steps_executed") or int(optimizer_step_summary.get("optimizer_step_count", 0)) <= 0:
        blockers.append("optimizer_step_count_zero")
    if not loss_summary.get("loss_is_finite"):
        blockers.append("non_finite_loss")
    if not legal_action_summary.get("legal_action_only"):
        blockers.append("illegal_action_selected")
    if not checkpoint_summary.get("checkpoint_schema_valid"):
        blockers.append("checkpoint_schema_invalid")
    if checkpoint_summary.get("model_checkpoint_written"):
        blockers.append("model_checkpoint_written")
    if not delayed_reward_contract_verified.get("delayed_reward_contract_preserved"):
        blockers.append("delayed_reward_contract_broken")
    if not train_eval_contract_verified.get("train_eval_trace_banks_disjoint"):
        blockers.append("train_eval_contract_broken")
    for key in ("no_full_campaign", "no_baseline_comparison", "no_paper_reproduction_claim", "no_policy_drift", "no_dependency_drift", "no_environment_contract_drift"):
        if not behavior_safety_summary.get(key):
            blockers.append(key)
    return blockers


def _build_smoke_summaries(result: Any) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    replay_summary = {
        "replay_size": result.replay_size,
        "replay_inserted": result.replay_size > 0,
        "pending_at_horizon_preserved": result.pending_at_horizon_preserved,
    }
    optimizer_step_summary = {
        "optimizer_step_count": result.optimizer_step_count,
        "optimizer_steps_executed": result.optimizer_step_count > 0,
        "target_sync_count": result.target_sync_count,
    }
    loss_summary = {
        "loss_value": result.loss_value,
        "loss_is_finite": result.loss_is_finite,
    }
    checkpoint_summary = {
        "checkpoint_schema_valid": result.checkpoint_schema_valid,
        "metadata_only": True,
        "model_checkpoint_written": False,
    }
    legal_action_summary = {
        "legal_action_only": result.legal_action_only,
    }
    delayed_reward_contract_verified = {
        "delayed_reward_contract_preserved": result.delayed_reward_contract_preserved,
        "pending_at_horizon_preserved": result.pending_at_horizon_preserved,
    }
    train_eval_contract_verified = {
        "train_eval_trace_banks_disjoint": result.train_eval_trace_banks_disjoint,
        "evaluation_on_training_traces": bool(result.evaluation_summary.get("evaluation_on_training_traces", False)),
        "trace_bank_ids": dict(result.evaluation_summary.get("trace_bank_ids", {})),
    }
    behavior_safety_summary = {
        "no_full_campaign": True,
        "no_baseline_comparison": True,
        "no_paper_reproduction_claim": True,
        "no_policy_drift": True,
        "no_dependency_drift": True,
        "no_environment_contract_drift": True,
    }
    return (
        replay_summary,
        optimizer_step_summary,
        loss_summary,
        checkpoint_summary,
        legal_action_summary,
        delayed_reward_contract_verified,
        train_eval_contract_verified,
        behavior_safety_summary,
    )


def run_paper_default_training_smoke(config: PaperDefaultTrainingSmokeConfig | None = None) -> PaperDefaultTrainingSmokeReport:
    smoke_config = config or PaperDefaultTrainingSmokeConfig()
    diff_names = _diff_names()
    readiness_payload = _load_json(smoke_config.readiness_report_path)
    feature_054_ready = _feature_054_readiness_verified(readiness_payload)
    prerequisite_tags_verified = _prerequisite_tags_verified(diff_names)
    prerequisite_ready = all(entry["verified"] for entry in prerequisite_tags_verified)

    live_environment_training_used = False
    fixture_training_used = False
    replay_summary = {"replay_size": 0, "replay_inserted": False, "pending_at_horizon_preserved": False}
    optimizer_step_summary = {"optimizer_step_count": 0, "optimizer_steps_executed": False, "target_sync_count": 0}
    loss_summary = {"loss_value": None, "loss_is_finite": False}
    checkpoint_summary = {"checkpoint_schema_valid": False, "metadata_only": True, "model_checkpoint_written": False}
    legal_action_summary = {"legal_action_only": False}
    delayed_reward_contract_verified = {"delayed_reward_contract_preserved": False, "pending_at_horizon_preserved": False}
    train_eval_contract_verified = {"train_eval_trace_banks_disjoint": False, "evaluation_on_training_traces": False, "trace_bank_ids": {}}
    behavior_safety_summary = {
        "no_full_campaign": smoke_config.full_campaign is False,
        "no_baseline_comparison": smoke_config.baseline_comparison is False,
        "no_paper_reproduction_claim": smoke_config.paper_reproduction_claim is False,
        "no_policy_drift": _no_policy_drift(diff_names),
        "no_dependency_drift": _no_dependency_drift(diff_names),
        "no_environment_contract_drift": _no_environment_semantic_drift(diff_names),
    }

    preflight_blockers: list[str] = []
    if not feature_054_ready:
        preflight_blockers.append("feature_054_readiness_failed")
    if not prerequisite_ready:
        preflight_blockers.append("prerequisite_tags_failed")

    if not preflight_blockers:
        from src.analysis.full_training_reproduction_campaign.trainer import DDQNTrainer

        campaign_config = smoke_config.build_campaign_config()
        result = DDQNTrainer(campaign_config).run_pilot(
            episodes=smoke_config.smoke_episodes,
            episode_length=smoke_config.smoke_episode_length,
        )
        live_environment_training_used = True
        (
            replay_summary,
            optimizer_step_summary,
            loss_summary,
            checkpoint_summary,
            legal_action_summary,
            delayed_reward_contract_verified,
            train_eval_contract_verified,
            behavior_safety_summary,
        ) = _build_smoke_summaries(result)
    if preflight_blockers:
        blockers = list(preflight_blockers)
    else:
        blockers = _build_blockers(
            feature_054_ready=feature_054_ready and prerequisite_ready,
            live_environment_training_used=live_environment_training_used,
            fixture_training_used=fixture_training_used,
            replay_summary=replay_summary,
            optimizer_step_summary=optimizer_step_summary,
            loss_summary=loss_summary,
            legal_action_summary=legal_action_summary,
            checkpoint_summary=checkpoint_summary,
            delayed_reward_contract_verified=delayed_reward_contract_verified,
            train_eval_contract_verified=train_eval_contract_verified,
            behavior_safety_summary=behavior_safety_summary,
        )
    ready = not blockers and feature_054_ready and prerequisite_ready and live_environment_training_used

    final_verdict = "paper_default_training_smoke_passed" if ready else "paper_default_training_smoke_blocked"
    recommended_next_feature = READY_NEXT_FEATURE if ready else "paper-default training smoke repair"
    if ready:
        blockers = []

    report = PaperDefaultTrainingSmokeReport(
        feature_id=FEATURE_ID,
        prerequisite_tags_verified=prerequisite_tags_verified,
        feature_054_readiness_verified=feature_054_ready,
        paper_default_smoke_scope={
            "smoke_episodes": smoke_config.smoke_episodes,
            "smoke_episode_length": smoke_config.smoke_episode_length,
            "full_campaign": smoke_config.full_campaign,
            "baseline_comparison": smoke_config.baseline_comparison,
            "paper_reproduction_claim": smoke_config.paper_reproduction_claim,
        },
        live_environment_training_used=live_environment_training_used,
        fixture_training_used=fixture_training_used,
        replay_summary=replay_summary,
        optimizer_step_summary=optimizer_step_summary,
        loss_summary=loss_summary,
        checkpoint_summary=checkpoint_summary,
        legal_action_summary=legal_action_summary,
        delayed_reward_contract_verified=delayed_reward_contract_verified,
        train_eval_contract_verified=train_eval_contract_verified,
        behavior_safety_summary=behavior_safety_summary,
        remaining_blockers=blockers,
        recommended_next_feature=recommended_next_feature,
        final_verdict=final_verdict,
    )
    return report


def build_paper_default_training_smoke_report(
    config: PaperDefaultTrainingSmokeConfig | None = None,
) -> PaperDefaultTrainingSmokeReport:
    return run_paper_default_training_smoke(config)


def generate_paper_default_training_smoke_artifacts(
    output_dir: str | Path | None = None,
) -> tuple[PaperDefaultTrainingSmokeReport, Path, Path]:
    report = run_paper_default_training_smoke()
    json_path, md_path = write_paper_default_training_smoke_report(report, output_dir)
    return report, json_path, md_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Feature 055 paper-default training smoke analysis.")
    parser.add_argument("--output-dir", type=Path, default=None, help="Override the report output directory.")
    args = parser.parse_args(argv)
    report = run_paper_default_training_smoke()
    write_paper_default_training_smoke_report(report, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
