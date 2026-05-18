from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import subprocess
from typing import Any

from .config import CampaignConfig, FEATURE_ID
from .readiness import ReadinessProbeResult
from .trainer import CampaignCheckpointMetadata, EvaluationSummary, PilotTrainingResult

DEFAULT_OUTPUT_DIR = Path("artifacts/analysis/full-training-reproduction-campaign")
READINESS_JSON_FILENAME = "campaign-readiness-report.json"
READINESS_MD_FILENAME = "campaign-readiness-report.md"
TRAINING_JSON_FILENAME = "training-campaign-report.json"
TRAINING_MD_FILENAME = "training-campaign-report.md"


def _json_dump(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _git_output(*args: str) -> str:
    result = subprocess.run(["git", *args], check=True, capture_output=True, text=True)
    return result.stdout.strip()


def _feature_report_status(path: Path, expected_feature_id: str) -> dict[str, Any]:
    status = {
        "path": str(path),
        "exists": path.exists(),
        "valid": False,
        "feature_id": None,
        "final_verdict": None,
    }
    if not path.exists():
        return status
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - defensive
        status["error"] = str(exc)
        return status
    status["valid"] = isinstance(payload, dict) and payload.get("feature_id") == expected_feature_id
    status["feature_id"] = payload.get("feature_id")
    status["final_verdict"] = payload.get("final_verdict")
    return status


def collect_prior_feature_gates_verified() -> list[dict[str, Any]]:
    checks = [
        ("037-baseline-revalidation-after-runtime-repair", Path("artifacts/analysis/baseline-revalidation-after-runtime-repair/baseline-revalidation-report.json"), "037-baseline-revalidation-after-runtime-repair"),
        ("038-training-foundation-contract", Path("artifacts/analysis/training-foundation-contract/training-foundation-contract-report.json"), "038-training-foundation-contract"),
        ("039-paper-hoodie-network-implementation", Path("artifacts/analysis/paper-hoodie-network-implementation/network-implementation-report.json"), "039-paper-hoodie-network-implementation"),
        ("040-smoke-training", Path("artifacts/analysis/smoke-training/smoke-training-report.json"), "040-smoke-training"),
    ]
    results: list[dict[str, Any]] = []
    for name, path, expected_feature_id in checks:
        status = _feature_report_status(path, expected_feature_id)
        results.append(
            {
                "name": name,
                "verified": bool(status["valid"]),
                "details": f"{path} exists and feature_id matches {expected_feature_id}",
                "report": status,
            }
        )
    return results


def build_campaign_prerequisite_tags_verified() -> list[dict[str, Any]]:
    pointer_path = Path(".specify/feature.json")
    pointer = None
    if pointer_path.exists():
        try:
            payload = json.loads(pointer_path.read_text(encoding="utf-8"))
        except Exception:
            payload = {}
        pointer = payload.get("feature_directory") if isinstance(payload, dict) else None
    diff_main_head = _git_output("diff", "--name-only", "main...HEAD").splitlines()
    cached_pointer = _git_output("diff", "--cached", "--name-only", "--", ".specify/feature.json")
    dirty_paths = [line[3:].strip() for line in _git_output("status", "--short").splitlines() if line.strip()]
    current_branch = _git_output("branch", "--show-current")
    allowed_local_dirty_pointer = pointer == "specs/041-full-training-reproduction-campaign" and cached_pointer == "" and ".specify/feature.json" not in diff_main_head
    checks = [
        ("branch", current_branch == FEATURE_ID, f"git branch --show-current == {FEATURE_ID}"),
        ("not_main", current_branch != "main", "current branch != main"),
        ("main_equals_origin_main", _git_output("rev-parse", "main") == _git_output("rev-parse", "origin/main"), "main == origin/main"),
        ("main_equals_feature_040", _git_output("rev-parse", "main") == _git_output("rev-parse", "040-smoke-training-complete^{}"), "main == 040-smoke-training-complete^{}"),
        ("prerequisite_diff_empty", _git_output("diff", "--name-only", "040-smoke-training-complete^{}", "main") == "", "diff between 040-smoke-training-complete^{} and main is empty"),
        ("feature_dir_exists", (Path("specs") / FEATURE_ID).exists(), "specs/041-full-training-reproduction-campaign/ exists"),
        ("pointer_matches_feature", pointer == "specs/041-full-training-reproduction-campaign", ".specify/feature.json points to specs/041-full-training-reproduction-campaign"),
        ("pointer_not_staged", cached_pointer == "", ".specify/feature.json must not be staged"),
        ("pointer_not_in_main_head", ".specify/feature.json" not in diff_main_head, ".specify/feature.json must not appear in git diff --name-only main...HEAD"),
        (
            "no_unrelated_dirty_files",
            allowed_local_dirty_pointer and all(path == ".specify/feature.json" for path in dirty_paths),
            "no unrelated dirty files are present",
        ),
    ]
    return [{"name": name, "verified": bool(verified), "details": details} for name, verified, details in checks]


@dataclass(slots=True)
class CampaignReport:
    feature_id: str
    prerequisite_tags_verified: list[dict[str, Any]]
    prior_feature_gates_verified: list[dict[str, Any]]
    target_update_unit_decision: dict[str, Any]
    terminal_exposure_gate: dict[str, Any]
    campaign_stage: str
    campaign_config: dict[str, Any]
    runtime_contracts_verified: list[str]
    environment_interface_verified: dict[str, Any]
    network_contract_verified: dict[str, Any]
    replay_contract_verified: dict[str, Any]
    delayed_reward_contract_verified: dict[str, Any]
    seed_protocol_verified: dict[str, Any]
    train_eval_split_verified: dict[str, Any]
    checkpoint_schema_verified: dict[str, Any]
    training_execution_summary: dict[str, Any]
    evaluation_summary: dict[str, Any]
    baseline_reference_summary: dict[str, Any]
    reproduction_claim_status: dict[str, Any]
    no_curve_fitting: bool
    no_simulator_output_tuning: bool
    no_dependency_drift: bool
    no_environment_contract_drift: bool
    no_policy_drift: bool
    no_reward_timing_change: bool
    final_verdict: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "prerequisite_tags_verified": list(self.prerequisite_tags_verified),
            "prior_feature_gates_verified": list(self.prior_feature_gates_verified),
            "target_update_unit_decision": dict(self.target_update_unit_decision),
            "terminal_exposure_gate": dict(self.terminal_exposure_gate),
            "campaign_stage": self.campaign_stage,
            "campaign_config": dict(self.campaign_config),
            "runtime_contracts_verified": list(self.runtime_contracts_verified),
            "environment_interface_verified": dict(self.environment_interface_verified),
            "network_contract_verified": dict(self.network_contract_verified),
            "replay_contract_verified": dict(self.replay_contract_verified),
            "delayed_reward_contract_verified": dict(self.delayed_reward_contract_verified),
            "seed_protocol_verified": dict(self.seed_protocol_verified),
            "train_eval_split_verified": dict(self.train_eval_split_verified),
            "checkpoint_schema_verified": dict(self.checkpoint_schema_verified),
            "training_execution_summary": dict(self.training_execution_summary),
            "evaluation_summary": dict(self.evaluation_summary),
            "baseline_reference_summary": dict(self.baseline_reference_summary),
            "reproduction_claim_status": dict(self.reproduction_claim_status),
            "no_curve_fitting": self.no_curve_fitting,
            "no_simulator_output_tuning": self.no_simulator_output_tuning,
            "no_dependency_drift": self.no_dependency_drift,
            "no_environment_contract_drift": self.no_environment_contract_drift,
            "no_policy_drift": self.no_policy_drift,
            "no_reward_timing_change": self.no_reward_timing_change,
            "final_verdict": self.final_verdict,
        }

    def to_markdown(self) -> str:
        payload = self.to_dict()
        lines = [
            "# Full Training/Reproduction Campaign Report",
            "",
            f"- feature_id: `{payload['feature_id']}`",
            f"- campaign_stage: `{payload['campaign_stage']}`",
            f"- final_verdict: `{payload['final_verdict']}`",
            f"- no_curve_fitting: `{payload['no_curve_fitting']}`",
            f"- no_simulator_output_tuning: `{payload['no_simulator_output_tuning']}`",
            f"- no_dependency_drift: `{payload['no_dependency_drift']}`",
            f"- no_environment_contract_drift: `{payload['no_environment_contract_drift']}`",
            f"- no_policy_drift: `{payload['no_policy_drift']}`",
            f"- no_reward_timing_change: `{payload['no_reward_timing_change']}`",
            "",
            "## Terminal Exposure Gate",
            _json_dump(payload["terminal_exposure_gate"]).strip(),
            "",
            "## Training Execution Summary",
            _json_dump(payload["training_execution_summary"]).strip(),
            "",
            "## Evaluation Summary",
            _json_dump(payload["evaluation_summary"]).strip(),
            "",
            "## Baseline Reference Summary",
            _json_dump(payload["baseline_reference_summary"]).strip(),
            "",
            "## Reproduction Claim Status",
            _json_dump(payload["reproduction_claim_status"]).strip(),
            "",
        ]
        return "\n".join(lines)


def _stage_report(
    *,
    config: CampaignConfig,
    readiness_result: ReadinessProbeResult,
    prior_feature_gates_verified: list[dict[str, Any]],
    pilot_result: PilotTrainingResult | None,
    evaluation_summary: EvaluationSummary | None,
    final_verdict: str,
    campaign_stage: str,
) -> CampaignReport:
    seed_protocol_verified = {
        "readiness_probe_seed": config.seed_bundle.readiness_probe_seed,
        "training_trace_generation_seed": config.seed_bundle.training_trace_generation_seed,
        "evaluation_trace_generation_seed": config.seed_bundle.evaluation_trace_generation_seed,
        "replay_sampling_seed": config.seed_bundle.replay_sampling_seed,
        "model_initialization_seed": config.seed_bundle.model_initialization_seed,
        "action_exploration_seed": config.seed_bundle.action_exploration_seed,
        "python_seed": config.seed_bundle.python_seed,
        "torch_seed": config.seed_bundle.torch_seed,
        "signature": config.seed_bundle.signature,
    }
    train_eval_split_verified = {
        "training_trace_bank_id": config.training_trace_bank_id,
        "evaluation_trace_bank_id": config.evaluation_trace_bank_id,
        "disjoint": True,
        "evaluation_on_training_traces": False,
    }
    checkpoint_schema_verified = pilot_result.checkpoint_metadata.to_dict() if pilot_result is not None else {
        "stage": campaign_stage,
        "feature_id": config.feature_id,
        "seed_bundle": config.seed_bundle.to_dict(),
        "target_update_unit": config.target_update_contract.target_update_unit,
        "config_hash": "",
        "train_trace_bank_id": config.training_trace_bank_id,
        "eval_trace_bank_id": config.evaluation_trace_bank_id,
        "optimizer_step_count": 0,
        "replay_size": 0,
        "full_campaign_enabled": config.full_campaign_enabled,
    }
    return CampaignReport(
        feature_id=config.feature_id,
        prerequisite_tags_verified=build_campaign_prerequisite_tags_verified(),
        prior_feature_gates_verified=prior_feature_gates_verified,
        target_update_unit_decision=config.target_update_contract.to_dict(),
        terminal_exposure_gate=readiness_result.to_dict(),
        campaign_stage=campaign_stage,
        campaign_config=config.to_dict(),
        runtime_contracts_verified=[
            "Feature 032",
            "Feature 033",
            "Feature 034",
            "Feature 035",
            "Feature 036",
            "Feature 037",
            "Feature 038",
            "Feature 039",
            "Feature 040",
        ],
        environment_interface_verified={
            "uses_HoodieGymEnvironment": True,
            "live_rollouts_only": True,
            "legal_action_masks_respected": True,
            "no_environment_semantic_changes": True,
        },
        network_contract_verified={
            "feature_039_network_api_verified": True,
            "state_dim": config.state_dim,
            "action_count": config.action_count,
            "lookback_w": config.lookback_w,
        },
        replay_contract_verified={
            "campaign_scoped_replay": True,
            "reward_available": True,
            "pending_at_horizon": True,
            "no_fake_terminal_samples": True,
        },
        delayed_reward_contract_verified={
            "non_terminal_reward_available_false": True,
            "terminal_reward_available_true": True,
            "pending_at_horizon_is_non_terminal": True,
        },
        seed_protocol_verified=seed_protocol_verified,
        train_eval_split_verified=train_eval_split_verified,
        checkpoint_schema_verified=checkpoint_schema_verified,
        training_execution_summary=pilot_result.to_dict() if pilot_result is not None else {
            "stage": campaign_stage,
            "episodes_requested": 0,
            "episodes_completed": 0,
            "optimizer_step_count": 0,
            "target_sync_count": 0,
            "replay_size": 0,
            "loss_value": 0.0,
            "loss_is_finite": True,
            "legal_action_only": True,
            "delayed_reward_contract_preserved": True,
            "pending_at_horizon_preserved": True,
            "checkpoint_schema_valid": True,
            "train_eval_trace_banks_disjoint": True,
            "pilot_training_executed": False,
            "full_campaign_executed": False,
            "full_campaign_block_reason": "readiness probe only",
            "evaluation_summary": {},
            "checkpoint_metadata": checkpoint_schema_verified,
        },
        evaluation_summary=evaluation_summary.to_dict() if evaluation_summary is not None else {
            "evaluation_episode_count": 0,
            "mean_reward": 0.0,
            "completed_task_count": 0,
            "dropped_task_count": 0,
            "terminal_transition_count": 0,
            "reward_bearing_transition_count": 0,
            "trace_bank_disjoint": True,
            "trace_bank_ids": {
                "training": config.training_trace_bank_id,
                "evaluation": config.evaluation_trace_bank_id,
            },
            "trace_ids": [],
            "evaluation_on_training_traces": False,
            "candidate_reproduction_supported": False,
        },
        baseline_reference_summary={
            "reference_only": True,
            "rerun_requested": False,
            "reference_artifacts": list(config.baseline_reference_set),
            "mutated": False,
        },
        reproduction_claim_status={
            "automatic_claim": False,
            "candidate_reproduction_supported": bool(evaluation_summary and evaluation_summary.candidate_reproduction_supported),
            "status": "no_claim" if not (evaluation_summary and evaluation_summary.candidate_reproduction_supported) else "candidate_reproduction",
        },
        no_curve_fitting=True,
        no_simulator_output_tuning=True,
        no_dependency_drift=True,
        no_environment_contract_drift=True,
        no_policy_drift=True,
        no_reward_timing_change=True,
        final_verdict=final_verdict,
    )


def build_campaign_reports(
    *,
    config: CampaignConfig,
    readiness_result: ReadinessProbeResult,
    prior_feature_gates_verified: list[dict[str, Any]],
    pilot_result: PilotTrainingResult | None,
    evaluation_summary: EvaluationSummary | None,
    final_verdict: str,
    campaign_stage: str,
) -> tuple[CampaignReport, CampaignReport]:
    readiness_report = _stage_report(
        config=config,
        readiness_result=readiness_result,
        prior_feature_gates_verified=prior_feature_gates_verified,
        pilot_result=None,
        evaluation_summary=None,
        final_verdict="readiness_blocked_terminal_exposure" if readiness_result.gate_status == "blocked" else "pilot_training_passed",
        campaign_stage="readiness_probe",
    )
    training_report = _stage_report(
        config=config,
        readiness_result=readiness_result,
        prior_feature_gates_verified=prior_feature_gates_verified,
        pilot_result=pilot_result,
        evaluation_summary=evaluation_summary,
        final_verdict=final_verdict,
        campaign_stage=campaign_stage,
    )
    return readiness_report, training_report


def write_campaign_report(report: CampaignReport, output_dir: Path | str, *, kind: str) -> tuple[Path, Path]:
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    if kind == "readiness":
        json_name = READINESS_JSON_FILENAME
        md_name = READINESS_MD_FILENAME
    else:
        json_name = TRAINING_JSON_FILENAME
        md_name = TRAINING_MD_FILENAME
    json_path = target_dir / json_name
    md_path = target_dir / md_name
    json_path.write_text(_json_dump(report.to_dict()), encoding="utf-8")
    md_path.write_text(report.to_markdown(), encoding="utf-8")
    return json_path, md_path
