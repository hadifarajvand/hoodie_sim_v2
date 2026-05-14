from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
from typing import Any


DEFAULT_OUTPUT_DIR = Path("artifacts/analysis/training-foundation-contract")
JSON_FILENAME = "training-foundation-contract-report.json"
MARKDOWN_FILENAME = "training-foundation-contract-report.md"


def _json_dump(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


@dataclass(slots=True)
class StateContract:
    version: str
    agent_key_field: str
    field_order: list[str]
    field_types: dict[str, str]
    normalization_rules: dict[str, Any]
    missing_value_encoding: dict[str, Any]
    history_buffer_policy: str
    lookback_w: int
    observable_only: bool
    diagnostics_excluded_from_model_input: bool
    no_privileged_future_information: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "agent_key_field": self.agent_key_field,
            "field_order": list(self.field_order),
            "field_types": dict(self.field_types),
            "normalization_rules": dict(self.normalization_rules),
            "missing_value_encoding": dict(self.missing_value_encoding),
            "history_buffer_policy": self.history_buffer_policy,
            "lookback_w": self.lookback_w,
            "observable_only": self.observable_only,
            "diagnostics_excluded_from_model_input": self.diagnostics_excluded_from_model_input,
            "no_privileged_future_information": self.no_privileged_future_information,
        }


@dataclass(slots=True)
class ActionIndexContract:
    version: str
    action_to_semantics: dict[int, str]
    horizontal_resolution_rule: str
    vertical_cloud_independent_rule: str
    illegal_action_behavior: str
    mask_surface: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "action_to_semantics": dict(self.action_to_semantics),
            "horizontal_resolution_rule": self.horizontal_resolution_rule,
            "vertical_cloud_independent_rule": self.vertical_cloud_independent_rule,
            "illegal_action_behavior": self.illegal_action_behavior,
            "mask_surface": self.mask_surface,
        }


@dataclass(slots=True)
class ReplayTransitionSchema:
    version: str
    fields: list[str]
    delayed_reward_policy: str
    pending_at_horizon_policy: str
    no_fake_terminal_samples: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "fields": list(self.fields),
            "delayed_reward_policy": self.delayed_reward_policy,
            "pending_at_horizon_policy": self.pending_at_horizon_policy,
            "no_fake_terminal_samples": self.no_fake_terminal_samples,
        }


@dataclass(slots=True)
class TargetUpdateFrequencyContract:
    update_frequency: int
    iteration_unit: str | None
    iteration_unit_status: str
    candidate_meanings: list[str]
    training_use_allowed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "update_frequency": self.update_frequency,
            "iteration_unit": self.iteration_unit,
            "iteration_unit_status": self.iteration_unit_status,
            "candidate_meanings": list(self.candidate_meanings),
            "training_use_allowed": self.training_use_allowed,
        }


@dataclass(slots=True)
class SeedProtocol:
    version: str
    training_trace_generation_seed: int
    evaluation_trace_generation_seed: int
    replay_sampling_seed: int
    model_initialization_seed: int
    action_exploration_seed: int
    python_seeded_now: bool
    numpy_seeded_now: bool
    torch_seed_future_required: bool
    recorded_in_artifacts: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "training_trace_generation_seed": self.training_trace_generation_seed,
            "evaluation_trace_generation_seed": self.evaluation_trace_generation_seed,
            "replay_sampling_seed": self.replay_sampling_seed,
            "model_initialization_seed": self.model_initialization_seed,
            "action_exploration_seed": self.action_exploration_seed,
            "python_seeded_now": self.python_seeded_now,
            "numpy_seeded_now": self.numpy_seeded_now,
            "torch_seed_future_required": self.torch_seed_future_required,
            "recorded_in_artifacts": self.recorded_in_artifacts,
        }


@dataclass(slots=True)
class TrainEvalSplitProtocol:
    version: str
    training_trace_ids: list[str]
    evaluation_trace_ids: list[str]
    fixed_evaluation_trace_bank: bool
    explicit_trace_ids: bool
    no_evaluation_on_training_traces: bool
    no_unfair_baseline_hoodie_trace_mismatch: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "training_trace_ids": list(self.training_trace_ids),
            "evaluation_trace_ids": list(self.evaluation_trace_ids),
            "fixed_evaluation_trace_bank": self.fixed_evaluation_trace_bank,
            "explicit_trace_ids": self.explicit_trace_ids,
            "no_evaluation_on_training_traces": self.no_evaluation_on_training_traces,
            "no_unfair_baseline_hoodie_trace_mismatch": self.no_unfair_baseline_hoodie_trace_mismatch,
        }


@dataclass(slots=True)
class CheckpointSchema:
    feature_id: str
    commit_sha: str
    config_path: str
    config_hash: str
    state_contract_version: str
    action_contract_version: str
    replay_schema_version: str
    seed_bundle: dict[str, Any]
    training_step_counters: dict[str, int]
    target_update_counter: int
    runtime_contract_refs: list[str]
    paper_default_parameter_refs: list[str]
    metadata_only: bool
    no_actual_model_checkpoint: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "commit_sha": self.commit_sha,
            "config_path": self.config_path,
            "config_hash": self.config_hash,
            "state_contract_version": self.state_contract_version,
            "action_contract_version": self.action_contract_version,
            "replay_schema_version": self.replay_schema_version,
            "seed_bundle": dict(self.seed_bundle),
            "training_step_counters": dict(self.training_step_counters),
            "target_update_counter": self.target_update_counter,
            "runtime_contract_refs": list(self.runtime_contract_refs),
            "paper_default_parameter_refs": list(self.paper_default_parameter_refs),
            "metadata_only": self.metadata_only,
            "no_actual_model_checkpoint": self.no_actual_model_checkpoint,
        }


@dataclass(slots=True)
class TerminalOutcomeExposureGate:
    generated_arrivals: int
    decisions_exposed: int
    finalized_terminal_tasks: int
    completed_tasks: int
    dropped_tasks: int
    pending_at_horizon: int
    terminal_transition_ratio: float
    reward_bearing_transition_ratio: float
    pending_transition_ratio: float
    threshold_status: str
    training_blocked: bool
    feature_037_sparse_terminal_issue_recorded: bool
    per_policy_smoke_statistics: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_arrivals": self.generated_arrivals,
            "decisions_exposed": self.decisions_exposed,
            "finalized_terminal_tasks": self.finalized_terminal_tasks,
            "completed_tasks": self.completed_tasks,
            "dropped_tasks": self.dropped_tasks,
            "pending_at_horizon": self.pending_at_horizon,
            "terminal_transition_ratio": self.terminal_transition_ratio,
            "reward_bearing_transition_ratio": self.reward_bearing_transition_ratio,
            "pending_transition_ratio": self.pending_transition_ratio,
            "threshold_status": self.threshold_status,
            "training_blocked": self.training_blocked,
            "feature_037_sparse_terminal_issue_recorded": self.feature_037_sparse_terminal_issue_recorded,
            "per_policy_smoke_statistics": list(self.per_policy_smoke_statistics),
        }


@dataclass(slots=True)
class TrainingFoundationReport:
    feature_id: str
    prerequisite_tags_verified: list[dict[str, Any]]
    state_contract: StateContract
    action_index_contract: ActionIndexContract
    replay_schema: ReplayTransitionSchema
    target_update_frequency_contract: TargetUpdateFrequencyContract
    seed_protocol: SeedProtocol
    train_eval_split_protocol: TrainEvalSplitProtocol
    checkpoint_schema: CheckpointSchema
    terminal_outcome_exposure_gate: TerminalOutcomeExposureGate
    runtime_contracts_verified: list[str]
    no_training_started: bool
    no_neural_network_change: bool
    no_dependency_drift: bool
    no_environment_contract_drift: bool
    no_reward_timing_change: bool
    no_policy_drift: bool
    no_curve_fitting: bool
    no_paper_reproduction_claim: bool
    final_verdict: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "prerequisite_tags_verified": list(self.prerequisite_tags_verified),
            "state_contract": self.state_contract.to_dict(),
            "action_index_contract": self.action_index_contract.to_dict(),
            "replay_schema": self.replay_schema.to_dict(),
            "target_update_frequency_contract": self.target_update_frequency_contract.to_dict(),
            "seed_protocol": self.seed_protocol.to_dict(),
            "train_eval_split_protocol": self.train_eval_split_protocol.to_dict(),
            "checkpoint_schema": self.checkpoint_schema.to_dict(),
            "terminal_outcome_exposure_gate": self.terminal_outcome_exposure_gate.to_dict(),
            "runtime_contracts_verified": list(self.runtime_contracts_verified),
            "no_training_started": self.no_training_started,
            "no_neural_network_change": self.no_neural_network_change,
            "no_dependency_drift": self.no_dependency_drift,
            "no_environment_contract_drift": self.no_environment_contract_drift,
            "no_reward_timing_change": self.no_reward_timing_change,
            "no_policy_drift": self.no_policy_drift,
            "no_curve_fitting": self.no_curve_fitting,
            "no_paper_reproduction_claim": self.no_paper_reproduction_claim,
            "final_verdict": self.final_verdict,
        }

    def to_json(self) -> str:
        return _json_dump(self.to_dict())

    def to_markdown(self) -> str:
        payload = self.to_dict()
        lines = [
            "# Training Foundation Contract Report",
            "",
            f"- feature_id: `{payload['feature_id']}`",
            f"- final_verdict: `{payload['final_verdict']}`",
            f"- no_training_started: `{payload['no_training_started']}`",
            f"- no_neural_network_change: `{payload['no_neural_network_change']}`",
            f"- no_dependency_drift: `{payload['no_dependency_drift']}`",
            f"- no_environment_contract_drift: `{payload['no_environment_contract_drift']}`",
            f"- no_reward_timing_change: `{payload['no_reward_timing_change']}`",
            f"- no_policy_drift: `{payload['no_policy_drift']}`",
            f"- no_curve_fitting: `{payload['no_curve_fitting']}`",
            f"- no_paper_reproduction_claim: `{payload['no_paper_reproduction_claim']}`",
            "",
            "## Terminal Outcome Exposure Gate",
        ]
        gate = payload["terminal_outcome_exposure_gate"]
        for key in [
            "generated_arrivals",
            "decisions_exposed",
            "finalized_terminal_tasks",
            "completed_tasks",
            "dropped_tasks",
            "pending_at_horizon",
            "terminal_transition_ratio",
            "reward_bearing_transition_ratio",
            "pending_transition_ratio",
            "threshold_status",
            "training_blocked",
            "feature_037_sparse_terminal_issue_recorded",
        ]:
            lines.append(f"- **{key}**: {gate[key]}")
        lines.append("")
        lines.append("## Prerequisite Tags Verified")
        for item in payload["prerequisite_tags_verified"]:
            lines.append(f"- `{item.get('tag', '')}` @ `{item.get('commit', '')}`")
        lines.append("")
        lines.append("## Runtime Contracts Verified")
        for item in payload["runtime_contracts_verified"]:
            lines.append(f"- {item}")
        lines.append("")
        return "\n".join(lines)

    def write(self, output_dir: Path | str | None = None) -> tuple[Path, Path]:
        target_dir = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR
        target_dir.mkdir(parents=True, exist_ok=True)
        json_path = target_dir / JSON_FILENAME
        md_path = target_dir / MARKDOWN_FILENAME
        json_path.write_text(self.to_json(), encoding="utf-8")
        md_path.write_text(self.to_markdown(), encoding="utf-8")
        return json_path, md_path


def _resolve_terminal_threshold_status(threshold_approved: bool) -> tuple[str, bool]:
    if not threshold_approved:
        return "pending_user_approval", True
    return "approved", False


def build_training_foundation_report(
    *,
    prerequisite_tags_verified: list[dict[str, Any]],
    state_contract: StateContract,
    action_index_contract: ActionIndexContract,
    replay_schema: ReplayTransitionSchema,
    target_update_frequency_contract: TargetUpdateFrequencyContract,
    seed_protocol: SeedProtocol,
    train_eval_split_protocol: TrainEvalSplitProtocol,
    checkpoint_schema: CheckpointSchema,
    generated_arrivals: int,
    decisions_exposed: int,
    finalized_terminal_tasks: int,
    completed_tasks: int,
    dropped_tasks: int,
    pending_at_horizon: int,
    per_policy_smoke_statistics: list[dict[str, Any]],
    runtime_contracts_verified: list[str],
    threshold_approved: bool = False,
    final_verdict: str | None = None,
) -> TrainingFoundationReport:
    threshold_status, training_blocked_by_threshold = _resolve_terminal_threshold_status(threshold_approved)
    terminal_transition_total = max(completed_tasks + dropped_tasks + pending_at_horizon, 0)
    terminal_transition_ratio = (completed_tasks + dropped_tasks) / terminal_transition_total if terminal_transition_total else 0.0
    reward_bearing_transition_ratio = (completed_tasks + dropped_tasks) / decisions_exposed if decisions_exposed else 0.0
    pending_transition_ratio = pending_at_horizon / terminal_transition_total if terminal_transition_total else 0.0
    training_blocked = training_blocked_by_threshold or finalized_terminal_tasks == 0 or reward_bearing_transition_ratio <= 0.0
    verdict = final_verdict or ("blocked_readiness" if training_blocked else "ready_for_training")
    return TrainingFoundationReport(
        feature_id="038-training-foundation-contract",
        prerequisite_tags_verified=prerequisite_tags_verified,
        state_contract=state_contract,
        action_index_contract=action_index_contract,
        replay_schema=replay_schema,
        target_update_frequency_contract=target_update_frequency_contract,
        seed_protocol=seed_protocol,
        train_eval_split_protocol=train_eval_split_protocol,
        checkpoint_schema=checkpoint_schema,
        terminal_outcome_exposure_gate=TerminalOutcomeExposureGate(
            generated_arrivals=generated_arrivals,
            decisions_exposed=decisions_exposed,
            finalized_terminal_tasks=finalized_terminal_tasks,
            completed_tasks=completed_tasks,
            dropped_tasks=dropped_tasks,
            pending_at_horizon=pending_at_horizon,
            terminal_transition_ratio=terminal_transition_ratio,
            reward_bearing_transition_ratio=reward_bearing_transition_ratio,
            pending_transition_ratio=pending_transition_ratio,
            threshold_status=threshold_status,
            training_blocked=training_blocked,
            feature_037_sparse_terminal_issue_recorded=True,
            per_policy_smoke_statistics=per_policy_smoke_statistics,
        ),
        runtime_contracts_verified=runtime_contracts_verified,
        no_training_started=True,
        no_neural_network_change=True,
        no_dependency_drift=True,
        no_environment_contract_drift=True,
        no_reward_timing_change=True,
        no_policy_drift=True,
        no_curve_fitting=True,
        no_paper_reproduction_claim=True,
        final_verdict=verdict,
    )


def write_training_foundation_report(
    report: TrainingFoundationReport,
    output_dir: Path | str | None = None,
) -> tuple[Path, Path]:
    return report.write(output_dir)
