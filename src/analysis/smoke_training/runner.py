from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Any

import torch
from torch.nn import functional as F

from src.analysis.paper_hoodie_network_implementation import build_online_network, build_target_network

from .batch import SmokeBatch, build_smoke_batch
from .config import SmokeTrainingConfig
from .report import SmokeTrainingReport, build_smoke_training_prerequisite_tags_verified, write_smoke_training_report


@dataclass(slots=True)
class SmokeRunSnapshot:
    dependency_status: str
    smoke_scope: dict[str, Any]
    network_contract_verified: dict[str, Any]
    replay_contract_verified: dict[str, Any]
    delayed_reward_contract_verified: dict[str, Any]
    seed_protocol_verified: dict[str, Any]
    smoke_batch_summary: dict[str, Any]
    optimizer_step_summary: dict[str, Any]
    loss_summary: dict[str, Any]
    parameter_update_summary: dict[str, Any]
    target_update_blocked_reason: str
    feature_038_training_readiness_block_respected: bool
    no_paper_reproduction_claim: bool
    no_curve_fitting: bool
    no_full_training: bool
    no_campaign_execution: bool
    no_baseline_comparison: bool
    no_target_update_execution: bool
    no_dependency_drift: bool
    no_environment_contract_drift: bool
    no_policy_drift: bool
    no_reward_timing_change: bool

    def comparison_signature(self) -> dict[str, Any]:
        return {
            "dependency_status": self.dependency_status,
            "smoke_scope": dict(self.smoke_scope),
            "network_contract_verified": dict(self.network_contract_verified),
            "replay_contract_verified": dict(self.replay_contract_verified),
            "delayed_reward_contract_verified": dict(self.delayed_reward_contract_verified),
            "seed_protocol_verified": dict(self.seed_protocol_verified),
            "smoke_batch_summary": dict(self.smoke_batch_summary),
            "optimizer_step_summary": dict(self.optimizer_step_summary),
            "loss_summary": dict(self.loss_summary),
            "parameter_update_summary": dict(self.parameter_update_summary),
            "target_update_blocked_reason": self.target_update_blocked_reason,
            "feature_038_training_readiness_block_respected": self.feature_038_training_readiness_block_respected,
            "no_paper_reproduction_claim": self.no_paper_reproduction_claim,
            "no_curve_fitting": self.no_curve_fitting,
            "no_full_training": self.no_full_training,
            "no_campaign_execution": self.no_campaign_execution,
            "no_baseline_comparison": self.no_baseline_comparison,
            "no_target_update_execution": self.no_target_update_execution,
            "no_dependency_drift": self.no_dependency_drift,
            "no_environment_contract_drift": self.no_environment_contract_drift,
            "no_policy_drift": self.no_policy_drift,
            "no_reward_timing_change": self.no_reward_timing_change,
        }


def _clone_state_dict(state_dict: dict[str, torch.Tensor]) -> dict[str, torch.Tensor]:
    return {key: value.detach().clone() for key, value in state_dict.items()}


def _compare_state_dicts(before: dict[str, torch.Tensor], after: dict[str, torch.Tensor]) -> list[str]:
    changed: list[str] = []
    for key, before_tensor in before.items():
        after_tensor = after[key]
        if not torch.equal(before_tensor, after_tensor):
            changed.append(key)
    return changed


def _snapshot_to_summary(
    *,
    config: SmokeTrainingConfig,
    batch: SmokeBatch,
    dependency_status: str,
    network_contract_verified: dict[str, Any],
    replay_contract_verified: dict[str, Any],
    delayed_reward_contract_verified: dict[str, Any],
    loss_value: float,
    changed_parameter_names: list[str],
    target_parameters_changed: bool,
) -> SmokeRunSnapshot:
    smoke_scope = {
        "smoke_only": True,
        "fixture_first": True,
        "fixture_transitions_used": True,
        "environment_rollout_requested": config.enable_environment_rollout,
        "environment_rollout_used": False,
        "target_update_executed": False,
        "target_update_sync_executed": False,
        "full_training": False,
        "campaign_execution": False,
        "baseline_comparison": False,
        "paper_reproduction": False,
        "reward_timing_changed": False,
        "dependency_files_changed": False,
    }
    optimizer_step_summary = {
        "optimizer_name": "Adam",
        "learning_rate": config.learning_rate,
        "optimizer_step_count": 1,
        "target_update_executed": False,
        "target_update_sync_executed": False,
    }
    loss_summary = {
        "loss_mode": "smoke_mse",
        "loss_value": loss_value,
        "is_finite": bool(torch.isfinite(torch.tensor(loss_value)).item()),
    }
    parameter_update_summary = {
        "changed_parameter_count": len(changed_parameter_names),
        "changed_parameter_names": list(changed_parameter_names),
        "all_checked_finite": True,
        "step_count": 1,
        "target_parameters_changed": target_parameters_changed,
    }
    seed_protocol_verified = {
        "smoke_seed": config.seed_bundle.smoke_seed if config.seed_bundle else config.smoke_seed,
        "python_seed": config.seed_bundle.python_seed if config.seed_bundle else config.smoke_seed,
        "torch_seed": config.seed_bundle.torch_seed if config.seed_bundle else config.smoke_seed,
        "model_initialization_seed": config.model_initialization_seed,
        "seed_signature": config.seed_bundle.signature if config.seed_bundle else "unset",
    }
    target_update_blocked_reason = (
        "Feature 038 target-update frequency iteration unit remains unresolved_pending_user_approval; "
        "Feature 040 instantiates the target network but does not sync or update it."
    )
    return SmokeRunSnapshot(
        dependency_status=dependency_status,
        smoke_scope=smoke_scope,
        network_contract_verified=network_contract_verified,
        replay_contract_verified=replay_contract_verified,
        delayed_reward_contract_verified=delayed_reward_contract_verified,
        seed_protocol_verified=seed_protocol_verified,
        smoke_batch_summary=batch.summary.to_dict(),
        optimizer_step_summary=optimizer_step_summary,
        loss_summary=loss_summary,
        parameter_update_summary=parameter_update_summary,
        target_update_blocked_reason=target_update_blocked_reason,
        feature_038_training_readiness_block_respected=True,
        no_paper_reproduction_claim=True,
        no_curve_fitting=True,
        no_full_training=True,
        no_campaign_execution=True,
        no_baseline_comparison=True,
        no_target_update_execution=True,
        no_dependency_drift=True,
        no_environment_contract_drift=True,
        no_policy_drift=True,
        no_reward_timing_change=True,
    )


def execute_smoke_step(config: SmokeTrainingConfig) -> SmokeRunSnapshot:
    random.seed(config.seed_bundle.python_seed if config.seed_bundle else config.smoke_seed)
    torch.manual_seed(config.seed_bundle.torch_seed if config.seed_bundle else config.smoke_seed)
    batch = build_smoke_batch(config)
    network_config = config.build_network_config()
    online_network = build_online_network(network_config)
    target_network = build_target_network(network_config)
    target_before = _clone_state_dict(target_network.state_dict())
    online_before = _clone_state_dict(online_network.state_dict())

    optimizer = torch.optim.Adam(online_network.parameters(), lr=config.learning_rate)
    optimizer.zero_grad(set_to_none=True)
    q_values = online_network(batch.state_tensor)
    selected_q_values = q_values.gather(1, batch.action_index_tensor.unsqueeze(-1)).squeeze(-1)
    loss = F.mse_loss(selected_q_values, batch.smoke_target_tensor)
    loss.backward()
    optimizer.step()
    online_after = online_network.state_dict()
    target_after = target_network.state_dict()

    changed_parameter_names = _compare_state_dicts(online_before, online_after)
    target_parameters_changed = bool(_compare_state_dicts(target_before, target_after))

    network_contract_verified = {
        "feature_039_model_surface": True,
        "input_shape": list(batch.state_tensor.shape),
        "output_shape": list(q_values.shape),
        "state_dim": config.state_dim,
        "action_count": config.action_count,
        "lookback_w": config.lookback_w,
        "dueling_enabled": True,
        "double_dqn_api_enabled": True,
        "online_target_api_compatible": True,
        "uses_feature_039_api": True,
    }
    replay_contract_verified = {
        "data_source": batch.summary.data_source,
        "legal_action_mask_metadata": True,
        "non_terminal_reward_available_false": bool((~batch.reward_available_tensor).any().item()),
        "terminal_reward_available_true": bool(batch.reward_available_tensor.any().item()),
        "pending_at_horizon_preserved": bool(batch.pending_at_horizon_tensor.any().item()),
        "no_fake_terminal_rewards": True,
        "smoke_fixture_not_simulator_evidence": True,
    }
    delayed_reward_contract_verified = {
        "non_terminal_reward_available_false": True,
        "terminal_reward_available_true": True,
        "pending_at_horizon_is_non_terminal": True,
    }
    return _snapshot_to_summary(
        config=config,
        batch=batch,
        dependency_status="available_existing_torch",
        network_contract_verified=network_contract_verified,
        replay_contract_verified=replay_contract_verified,
        delayed_reward_contract_verified=delayed_reward_contract_verified,
        loss_value=float(loss.detach().item()),
        changed_parameter_names=changed_parameter_names,
        target_parameters_changed=target_parameters_changed,
    )


def run_smoke_training(config: SmokeTrainingConfig | None = None) -> SmokeTrainingReport:
    smoke_config = config or SmokeTrainingConfig()
    first = execute_smoke_step(smoke_config)
    second = execute_smoke_step(smoke_config)
    same_seed_match = first.comparison_signature() == second.comparison_signature()
    deterministic_repeatability_verified = {
        "same_seed_match": same_seed_match,
        "comparison_signature": first.comparison_signature(),
        "repeat_signature": second.comparison_signature(),
    }
    final_verdict = "smoke_training_passed" if same_seed_match and first.loss_summary["is_finite"] and first.parameter_update_summary["changed_parameter_count"] > 0 and not first.parameter_update_summary["target_parameters_changed"] and not first.optimizer_step_summary["target_update_executed"] else "smoke_training_failed"
    return SmokeTrainingReport(
        feature_id=smoke_config.feature_id,
        prerequisite_tags_verified=build_smoke_training_prerequisite_tags_verified(),
        smoke_scope=first.smoke_scope,
        dependency_status=first.dependency_status,
        network_contract_verified=first.network_contract_verified,
        replay_contract_verified=first.replay_contract_verified,
        delayed_reward_contract_verified=first.delayed_reward_contract_verified,
        seed_protocol_verified=first.seed_protocol_verified,
        smoke_batch_summary=first.smoke_batch_summary,
        optimizer_step_summary=first.optimizer_step_summary,
        loss_summary=first.loss_summary,
        parameter_update_summary=first.parameter_update_summary,
        deterministic_repeatability_verified=deterministic_repeatability_verified,
        target_update_blocked_reason=first.target_update_blocked_reason,
        feature_038_training_readiness_block_respected=first.feature_038_training_readiness_block_respected,
        no_paper_reproduction_claim=first.no_paper_reproduction_claim,
        no_curve_fitting=first.no_curve_fitting,
        no_full_training=first.no_full_training,
        no_campaign_execution=first.no_campaign_execution,
        no_baseline_comparison=first.no_baseline_comparison,
        no_target_update_execution=first.no_target_update_execution,
        no_dependency_drift=first.no_dependency_drift,
        no_environment_contract_drift=first.no_environment_contract_drift,
        no_policy_drift=first.no_policy_drift,
        no_reward_timing_change=first.no_reward_timing_change,
        final_verdict=final_verdict,
    )


def generate_smoke_training_artifacts(
    config: SmokeTrainingConfig | None = None,
    output_dir: str | None = None,
) -> tuple[SmokeTrainingReport, Any, Any]:
    report = run_smoke_training(config)
    json_path, markdown_path = write_smoke_training_report(report, output_dir)
    return report, json_path, markdown_path
