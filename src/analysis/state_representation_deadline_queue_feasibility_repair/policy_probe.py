from __future__ import annotations

from collections import Counter
from contextlib import contextmanager
from dataclasses import dataclass, field
import math
from typing import Any

from src.analysis.evaluation_instrumentation_reward_state_diagnostic.instrumented_evaluator import (
    _LoggingPolicyProxy,
    _TrainingActionLogger,
    _build_action_counts_from_records,
    _build_replay_window_action_distribution,
    _build_training_reward_summary,
    _episode_seed,
    _temporary_policy,
    action_order,
    build_fixed_policy_suite,
    normalize_action_name,
)
from src.analysis.full_training_reproduction_campaign.config import CampaignConfig
from src.analysis.full_training_reproduction_campaign.trainer import DDQNTrainer
from src.analysis.terminal_lifecycle_accounting_50_100_comparison.repaired_terminal_evaluator import (
    build_policy_effect_after_terminal_repair,
    evaluate_policy_on_trace_bank_terminal_repaired,
)

from .config import CHECKPOINT_BUDGETS, EVALUATION_EPISODE_COUNT, EPISODE_LENGTH, NEW_STATE_REPRESENTATION_PROFILE
from .state_profile_adapter import build_profiled_campaign_config, patched_terminal_evaluator_state_profile


@dataclass(slots=True)
class StateRepresentationTrainingSession:
    config: Any
    state_representation_profile: str = NEW_STATE_REPRESENTATION_PROFILE
    campaign_config: CampaignConfig = field(init=False)
    trainer: DDQNTrainer = field(init=False)
    training_episode_count: int = field(init=False, default=0)
    cumulative_training_action_distribution: Counter[str] = field(init=False)
    cumulative_reward_total: float = field(init=False, default=0.0)
    cumulative_reward_count: int = field(init=False, default=0)
    cumulative_pending_at_horizon_count: int = field(init=False, default=0)
    loss_values: list[float] = field(init=False, default_factory=list)
    _training_logger: _TrainingActionLogger = field(init=False)
    _policy_proxy: _LoggingPolicyProxy = field(init=False)

    def __post_init__(self) -> None:
        self.campaign_config = build_profiled_campaign_config(state_representation_profile=self.state_representation_profile)
        self.trainer = DDQNTrainer(self.campaign_config)
        self.training_episode_count = 0
        self.cumulative_training_action_distribution = Counter({action: 0 for action in action_order()})
        self.cumulative_reward_total = 0.0
        self.cumulative_reward_count = 0
        self.cumulative_pending_at_horizon_count = 0
        self.loss_values = []
        self._training_logger = _TrainingActionLogger()
        self._policy_proxy = _LoggingPolicyProxy(self.trainer.policy, self._training_logger)

    def train_to_budget(self, target_budget: int) -> dict[str, Any]:
        if target_budget < self.training_episode_count:
            raise ValueError("target_budget cannot move backwards")
        while self.training_episode_count < target_budget:
            episode_id = self.training_episode_count
            seed = _episode_seed(self.campaign_config, episode_id)
            before_replay_size = len(self.trainer.replay_buffer)
            self._training_logger.begin_episode(episode_id=episode_id, seed=seed)
            self._policy_proxy.begin_episode()
            with _temporary_policy(self.trainer, self._policy_proxy):
                rollout_summary = self.trainer._episode_rollout(  # noqa: SLF001
                    episode_id=episode_id,
                    seed=seed,
                    episode_length=self.config.episode_length,
                    training=True,
                )
            action_records = self._training_logger.snapshot()
            new_transitions = self.trainer.replay_buffer.as_list()[before_replay_size:]
            episode_action_distribution = _build_action_counts_from_records(action_records)
            self.cumulative_training_action_distribution.update(episode_action_distribution)
            reward_summary = _build_training_reward_summary(new_transitions)
            self.cumulative_reward_total += float(reward_summary["total_reward"])
            self.cumulative_reward_count += int(reward_summary["reward_count"])
            self.cumulative_pending_at_horizon_count += int(reward_summary["pending_at_horizon_count"])
            self.loss_values.extend(float(loss) for loss in rollout_summary["loss_values"])
            self.training_episode_count += 1
        replay_window_action_distribution = _build_replay_window_action_distribution(self.trainer.replay_buffer.as_list())
        return {
            "training_budget": int(target_budget),
            "state_representation_profile": self.state_representation_profile,
            "cumulative_training_episode_count": self.training_episode_count,
            "optimizer_step_count": self.trainer.optimizer_step_count,
            "replay_size": len(self.trainer.replay_buffer),
            "loss_count": len(self.loss_values),
            "loss_value": self.loss_values[-1] if self.loss_values else 0.0,
            "loss_is_finite": bool(math.isfinite(self.loss_values[-1])) if self.loss_values else True,
            "replay_window_action_distribution": replay_window_action_distribution,
            "cumulative_training_action_distribution": dict(self.cumulative_training_action_distribution),
            "cumulative_reward_total": self.cumulative_reward_total,
            "cumulative_reward_count": self.cumulative_reward_count,
            "cumulative_pending_at_horizon_count": self.cumulative_pending_at_horizon_count,
        }

    def candidate_policy_result(self, *, checkpoint_budget: int) -> dict[str, Any]:
        with patched_terminal_evaluator_state_profile(self.campaign_config.state_representation_profile):
            return evaluate_policy_on_trace_bank_terminal_repaired(
                trainer=self.trainer,
                policy_name=f"candidate_policy_at_{checkpoint_budget}",
                policy_fn=lambda state_tensor, legal_action_mask, context: self.trainer.policy.choose_action(state_tensor, legal_action_mask),
                evaluation_episode_count=self.config.evaluation_episode_count,
                episode_length=self.config.episode_length,
                seed_base=self.campaign_config.seed_bundle.evaluation_trace_generation_seed,
                checkpoint_budget=checkpoint_budget,
                policy_kind="candidate",
                evaluation_trace_bank_id=self.campaign_config.evaluation_trace_bank_id,
                record_sample_limit=self.config.record_sample_limit,
            )

    def fixed_policy_results(self) -> dict[str, dict[str, Any]]:
        fixed_suite = build_fixed_policy_suite(self.campaign_config.seed_bundle.evaluation_trace_generation_seed)
        results: dict[str, dict[str, Any]] = {}
        with patched_terminal_evaluator_state_profile(self.campaign_config.state_representation_profile):
            for policy_name, policy_fn in fixed_suite.items():
                results[policy_name] = evaluate_policy_on_trace_bank_terminal_repaired(
                    trainer=self.trainer,
                    policy_name=policy_name,
                    policy_fn=policy_fn,
                    evaluation_episode_count=self.config.evaluation_episode_count,
                    episode_length=self.config.episode_length,
                    seed_base=self.campaign_config.seed_bundle.evaluation_trace_generation_seed,
                    checkpoint_budget=100,
                    policy_kind="fixed",
                    evaluation_trace_bank_id=self.campaign_config.evaluation_trace_bank_id,
                    record_sample_limit=self.config.record_sample_limit,
                )
        return results


def build_state_representation_policy_effect_comparison(
    *,
    session: StateRepresentationTrainingSession,
    checkpoint_results: list[dict[str, Any]],
    record_sample_limit: int,
) -> dict[str, Any]:
    with patched_terminal_evaluator_state_profile(session.campaign_config.state_representation_profile):
        comparison = build_policy_effect_after_terminal_repair(
            trainer=session.trainer,
            checkpoint_results=checkpoint_results,
            fixed_policy_seed=session.campaign_config.seed_bundle.evaluation_trace_generation_seed,
            evaluation_episode_count=session.config.evaluation_episode_count,
            episode_length=session.config.episode_length,
            evaluation_trace_bank_id=session.campaign_config.evaluation_trace_bank_id,
        )
    return comparison
