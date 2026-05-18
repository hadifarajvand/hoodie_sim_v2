from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import argparse
import json
from typing import Any

from .config import (
    CampaignConfig,
    READINESS_MANUAL_APPROVAL_APPROVED,
    READINESS_MANUAL_APPROVAL_PENDING,
    READINESS_MANUAL_APPROVAL_REJECTED,
)
from .readiness import CampaignReadinessProbe, ReadinessProbeResult, run_campaign_readiness_probe
from .report import CampaignReport, build_campaign_reports, collect_prior_feature_gates_verified, write_campaign_report
from .trainer import DDQNTrainer, EvaluationSummary, PilotTrainingResult, run_campaign_evaluation, run_pilot_training


DEFAULT_OUTPUT_DIR = Path("artifacts/analysis/full-training-reproduction-campaign")
DEFAULT_CHECKPOINT_DIR = Path("artifacts/checkpoints/full-training-reproduction-campaign")


@dataclass(slots=True)
class CampaignExecutionResult:
    config: CampaignConfig
    readiness_result: ReadinessProbeResult
    pilot_result: PilotTrainingResult | None
    evaluation_summary: EvaluationSummary | None
    readiness_report: CampaignReport
    training_report: CampaignReport
    checkpoint_path: Path | None
    full_campaign_block_reason: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "config": self.config.to_dict(),
            "readiness_result": self.readiness_result.to_dict(),
            "pilot_result": self.pilot_result.to_dict() if self.pilot_result is not None else None,
            "evaluation_summary": self.evaluation_summary.to_dict() if self.evaluation_summary is not None else None,
            "readiness_report": self.readiness_report.to_dict(),
            "training_report": self.training_report.to_dict(),
            "checkpoint_path": str(self.checkpoint_path) if self.checkpoint_path is not None else None,
            "full_campaign_block_reason": self.full_campaign_block_reason,
        }


def _checkpoint_metadata_path(config: CampaignConfig, stage: str) -> Path:
    return DEFAULT_CHECKPOINT_DIR / f"{stage}-checkpoint-metadata.json"


def _write_checkpoint_metadata(result: PilotTrainingResult, *, config: CampaignConfig, stage: str) -> Path:
    metadata_path = _checkpoint_metadata_path(config, stage)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(json.dumps(result.checkpoint_metadata.to_dict(), indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    return metadata_path


def _evaluation_summary_from_payload(payload: dict[str, Any]) -> EvaluationSummary:
    return EvaluationSummary(
        evaluation_episode_count=int(payload["evaluation_episode_count"]),
        mean_reward=float(payload["mean_reward"]),
        completed_task_count=int(payload["completed_task_count"]),
        dropped_task_count=int(payload["dropped_task_count"]),
        terminal_transition_count=int(payload["terminal_transition_count"]),
        reward_bearing_transition_count=int(payload["reward_bearing_transition_count"]),
        trace_bank_disjoint=bool(payload["trace_bank_disjoint"]),
        trace_bank_ids=dict(payload["trace_bank_ids"]),
        trace_ids=list(payload["trace_ids"]),
        evaluation_on_training_traces=bool(payload["evaluation_on_training_traces"]),
        candidate_reproduction_supported=bool(payload["candidate_reproduction_supported"]),
    )


def _build_blocked_result(config: CampaignConfig, readiness_result: ReadinessProbeResult, reason: str) -> CampaignExecutionResult:
    prior_feature_gates_verified = collect_prior_feature_gates_verified()
    empty_pilot = PilotTrainingResult(
        stage=readiness_result.campaign_stage,
        episodes_requested=0,
        episodes_completed=0,
        optimizer_step_count=0,
        target_sync_count=0,
        replay_size=0,
        loss_value=0.0,
        loss_is_finite=True,
        legal_action_only=True,
        delayed_reward_contract_preserved=True,
        pending_at_horizon_preserved=True,
        checkpoint_schema_valid=True,
        train_eval_trace_banks_disjoint=True,
        full_campaign_executed=False,
        full_campaign_block_reason=reason,
        evaluation_summary={
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
        checkpoint_metadata=DDQNTrainer(config)._checkpoint_metadata(stage=readiness_result.campaign_stage, replay_size=0),
    )
    readiness_report, training_report = build_campaign_reports(
        config=config,
        readiness_result=readiness_result,
        prior_feature_gates_verified=prior_feature_gates_verified,
        pilot_result=empty_pilot,
        evaluation_summary=None,
        final_verdict="readiness_blocked_terminal_exposure",
        campaign_stage=readiness_result.campaign_stage,
    )
    return CampaignExecutionResult(
        config=config,
        readiness_result=readiness_result,
        pilot_result=None,
        evaluation_summary=None,
        readiness_report=readiness_report,
        training_report=training_report,
        checkpoint_path=None,
        full_campaign_block_reason=reason,
    )


def run_campaign(
    config: CampaignConfig | None = None,
    *,
    stage: str = "readiness_probe",
    episodes: int | None = None,
    enable_full_campaign: bool | None = None,
) -> CampaignExecutionResult:
    campaign_config = config or CampaignConfig()
    if enable_full_campaign is not None:
        campaign_config.full_campaign_enabled = bool(enable_full_campaign)
    readiness_result = CampaignReadinessProbe(campaign_config).run()
    prior_feature_gates_verified = collect_prior_feature_gates_verified()

    if readiness_result.gate_status != "pilot-ready" or readiness_result.readiness_manual_approval_status != READINESS_MANUAL_APPROVAL_APPROVED:
        return _build_blocked_result(campaign_config, readiness_result, readiness_result.readiness_block_reason or "readiness probe blocked the campaign")

    if stage == "readiness_probe":
        readiness_report, training_report = build_campaign_reports(
            config=campaign_config,
            readiness_result=readiness_result,
            prior_feature_gates_verified=prior_feature_gates_verified,
            pilot_result=None,
            evaluation_summary=None,
            final_verdict="pilot_training_passed",
            campaign_stage="readiness_probe",
        )
        return CampaignExecutionResult(
            config=campaign_config,
            readiness_result=readiness_result,
            pilot_result=None,
            evaluation_summary=None,
            readiness_report=readiness_report,
            training_report=training_report,
            checkpoint_path=None,
            full_campaign_block_reason="pilot training not requested",
        )

    if stage == "pilot_training":
        trainer = DDQNTrainer(campaign_config)
        pilot_episodes = episodes or campaign_config.pilot_budget.primary_episodes
        if pilot_episodes not in {campaign_config.pilot_budget.primary_episodes, campaign_config.pilot_budget.follow_up_episodes}:
            raise ValueError("Pilot training episodes must be 10 or 25.")
        pilot_result = trainer.run_pilot(episodes=pilot_episodes, episode_length=campaign_config.pilot_episode_length)
        checkpoint_path = _write_checkpoint_metadata(pilot_result, config=campaign_config, stage="pilot_training") if pilot_result.checkpoint_schema_valid else None
        evaluation_summary = _evaluation_summary_from_payload(pilot_result.evaluation_summary)
        readiness_report, training_report = build_campaign_reports(
            config=campaign_config,
            readiness_result=readiness_result,
            prior_feature_gates_verified=prior_feature_gates_verified,
            pilot_result=pilot_result,
            evaluation_summary=evaluation_summary,
            final_verdict="pilot_training_passed",
            campaign_stage="pilot_training",
        )
        return CampaignExecutionResult(
            config=campaign_config,
            readiness_result=readiness_result,
            pilot_result=pilot_result,
            evaluation_summary=evaluation_summary,
            readiness_report=readiness_report,
            training_report=training_report,
            checkpoint_path=checkpoint_path,
            full_campaign_block_reason=None,
        )

    if stage in {"full_training_candidate", "final_reproduction_campaign"}:
        trainer = DDQNTrainer(campaign_config)
        pilot_result = trainer.run_pilot(episodes=campaign_config.pilot_budget.primary_episodes, episode_length=campaign_config.pilot_episode_length)
        if not pilot_result.loss_is_finite or not pilot_result.legal_action_only or not pilot_result.checkpoint_schema_valid:
            evaluation_summary = _evaluation_summary_from_payload(pilot_result.evaluation_summary)
            readiness_report, training_report = build_campaign_reports(
                config=campaign_config,
                readiness_result=readiness_result,
                prior_feature_gates_verified=prior_feature_gates_verified,
                pilot_result=pilot_result,
                evaluation_summary=evaluation_summary,
                final_verdict="pilot_training_failed",
                campaign_stage="pilot_training",
            )
            return CampaignExecutionResult(
                config=campaign_config,
                readiness_result=readiness_result,
                pilot_result=pilot_result,
                evaluation_summary=evaluation_summary,
                readiness_report=readiness_report,
                training_report=training_report,
                checkpoint_path=None,
                full_campaign_block_reason="pilot success criteria not met",
            )
        if not campaign_config.full_campaign_enabled:
            evaluation_summary = _evaluation_summary_from_payload(pilot_result.evaluation_summary)
            readiness_report, training_report = build_campaign_reports(
                config=campaign_config,
                readiness_result=readiness_result,
                prior_feature_gates_verified=prior_feature_gates_verified,
                pilot_result=pilot_result,
                evaluation_summary=evaluation_summary,
                final_verdict="pilot_training_passed",
                campaign_stage="pilot_training",
            )
            return CampaignExecutionResult(
                config=campaign_config,
                readiness_result=readiness_result,
                pilot_result=pilot_result,
                evaluation_summary=evaluation_summary,
                readiness_report=readiness_report,
                training_report=training_report,
                checkpoint_path=None,
                full_campaign_block_reason="full campaign command/flag not explicitly enabled",
            )
        full_episodes = episodes or campaign_config.full_campaign_budget
        candidate_result = trainer.run_full_candidate(
            episodes=full_episodes,
            episode_length=campaign_config.full_campaign_episode_length,
            enable_full_campaign=campaign_config.full_campaign_enabled,
            readiness_result=readiness_result,
            pilot_result=pilot_result,
        )
        evaluation_summary = _evaluation_summary_from_payload(candidate_result.evaluation_summary)
        checkpoint_path = _write_checkpoint_metadata(candidate_result, config=campaign_config, stage="full_training_candidate") if candidate_result.checkpoint_schema_valid else None
        final_verdict = "full_training_completed_no_reproduction_claim"
        if evaluation_summary.candidate_reproduction_supported:
            final_verdict = "full_training_completed_candidate_reproduction"
        readiness_report, training_report = build_campaign_reports(
            config=campaign_config,
            readiness_result=readiness_result,
            prior_feature_gates_verified=prior_feature_gates_verified,
            pilot_result=candidate_result,
            evaluation_summary=evaluation_summary,
            final_verdict=final_verdict,
            campaign_stage="full_training_candidate",
        )
        return CampaignExecutionResult(
            config=campaign_config,
            readiness_result=readiness_result,
            pilot_result=candidate_result,
            evaluation_summary=evaluation_summary,
            readiness_report=readiness_report,
            training_report=training_report,
            checkpoint_path=checkpoint_path,
            full_campaign_block_reason=None,
        )

    raise ValueError(f"Unsupported stage: {stage}")


def generate_campaign_artifacts(
    config: CampaignConfig | None = None,
    *,
    stage: str = "readiness_probe",
    episodes: int | None = None,
    enable_full_campaign: bool | None = None,
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
) -> CampaignExecutionResult:
    result = run_campaign(config, stage=stage, episodes=episodes, enable_full_campaign=enable_full_campaign)
    readiness_output = Path(output_dir)
    readiness_output.mkdir(parents=True, exist_ok=True)
    write_campaign_report(result.readiness_report, readiness_output, kind="readiness")
    write_campaign_report(result.training_report, readiness_output, kind="training")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m src.analysis.full_training_reproduction_campaign")
    parser.add_argument("--stage", default="readiness_probe", choices=["readiness_probe", "pilot_training", "full_training_candidate", "final_reproduction_campaign"])
    parser.add_argument("--episodes", type=int, default=None)
    parser.add_argument("--enable-full-campaign", action="store_true")
    parser.add_argument("--manual-approval-status", default=READINESS_MANUAL_APPROVAL_PENDING, choices=[READINESS_MANUAL_APPROVAL_PENDING, READINESS_MANUAL_APPROVAL_APPROVED, READINESS_MANUAL_APPROVAL_REJECTED])
    args = parser.parse_args(argv)
    config = CampaignConfig(readiness_manual_approval_status=args.manual_approval_status, full_campaign_enabled=args.enable_full_campaign)
    result = generate_campaign_artifacts(config, stage=args.stage, episodes=args.episodes, enable_full_campaign=args.enable_full_campaign)
    print(json.dumps(result.to_dict(), indent=2, sort_keys=True, ensure_ascii=False))
    return 0
