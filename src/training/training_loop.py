from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.config.training_config import TrainingConfig
from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.runtime_model import SharedRuntimeParameters
from src.environment.topology import TopologyGraph
from src.evaluation.runner import EvaluationRunner
from src.evaluation.trace_protocol import EvaluationTrace
from src.policies.policy_interface import PolicyContext, ReplayTrainablePolicy

from .delayed_reward_training import DelayedRewardTraining
from .training_logging import TrainingLogger


@dataclass(slots=True)
class _PendingDecision:
    task_id: int
    decision_slot: int
    state: dict[str, Any]
    action: str


@dataclass(slots=True)
class TrainingEpisodeSummary:
    episode_index: int
    trace_id: str
    transitions_recorded: int
    replay_buffer_size: int


@dataclass(slots=True)
class TrainingLoop:
    policy: ReplayTrainablePolicy
    config: TrainingConfig
    topology: TopologyGraph | None = None
    runtime_parameters: SharedRuntimeParameters | None = None
    logger: TrainingLogger = field(default_factory=TrainingLogger)
    delayed_reward: DelayedRewardTraining = field(default_factory=DelayedRewardTraining)

    def __post_init__(self) -> None:
        self.policy.replay_buffer.capacity = self.config.replay_buffer_capacity
        if self.config.replay_seed is not None:
            self.policy.replay_buffer.reseed(self.config.replay_seed)

    def _evaluation_runner(self) -> EvaluationRunner:
        return EvaluationRunner(
            policy=self.policy,
            config=self.config.to_evaluation_config(),
            topology=self.topology,
            runtime_parameters=self.runtime_parameters,
        )

    def _trace_for_episode(self, episode_index: int) -> EvaluationTrace:
        return self._evaluation_runner()._trace_for_episode(episode_index)

    def _run_episode(self, trace: EvaluationTrace, runner: EvaluationRunner) -> TrainingEpisodeSummary:
        env = HoodieGymEnvironment(
            episode_length=self.config.episode_length,
            topology=self.topology,
            runtime_parameters=self.runtime_parameters or SharedRuntimeParameters(),
            policy_name=self.config.policy_name,
        )
        env.reset(seed=trace.seed)
        transitions_recorded = 0
        pending_decisions: dict[int, _PendingDecision] = {}
        while True:
            current_task = env.current_task
            if current_task is None:
                action = None
            else:
                observation = env.observe_flat(current_task)
                legal_action_mask = observation.get("legal_action_mask", {})
                policy_context = PolicyContext(
                    observation=observation,
                    legal_action_mask=legal_action_mask,
                    trace_history=(trace.trace_id,),
                )
                action = self.policy.choose_action(policy_context)
                pending_decisions[current_task.task_id] = _PendingDecision(
                    task_id=current_task.task_id,
                    decision_slot=int(current_task.decision_slot if current_task.decision_slot is not None else env.current_slot),
                    state=dict(policy_context.observation),
                    action=action,
                )

            _observation, _reward, terminated, truncated, info = env.step(action)
            delivery_events = info.get("reward_delivery_events", [])
            for delivery in delivery_events:
                task_id = int(delivery["task_id"])
                pending = pending_decisions.pop(task_id, None)
                if pending is None:
                    continue
                next_state = dict(_observation)
                next_state["reward_delivery_event"] = dict(delivery)
                delta_slots = max(1, int(delivery.get("delta_slots", 1)))
                self.policy.record_transition(
                    pending.state,
                    pending.action,
                    float(delivery["reward"]),
                    next_state,
                    True,
                    delta_slots=delta_slots,
                )
                self.policy.learn_from_replay(self.config.batch_size, self.config.learning_rate)
                transitions_recorded += 1
            if terminated:
                if pending_decisions:
                    raise RuntimeError(f"unresolved pending decisions at termination: {sorted(pending_decisions)}")
                break
            if truncated and env.current_task is None and env.queue_load == 0:
                if pending_decisions:
                    raise RuntimeError(f"unresolved pending decisions at truncation: {sorted(pending_decisions)}")
                break

        return TrainingEpisodeSummary(
            episode_index=int(trace.trace_id.rsplit("-", 1)[-1]) if "-" in trace.trace_id else 0,
            trace_id=trace.trace_id,
            transitions_recorded=transitions_recorded,
            replay_buffer_size=len(self.policy.replay_buffer),
        )

    def _reward_for_finalized_task(self, finalized: dict[str, Any]) -> float:
        terminal_outcome = finalized.get("terminal_outcome")
        if terminal_outcome == "dropped":
            return -float(self.delayed_reward.drop_penalty)
        arrival_slot = int(finalized.get("arrival_slot", 0))
        completion_slot = finalized.get("completion_slot")
        if terminal_outcome == "completed" and completion_slot is not None:
            return -float(int(completion_slot) - arrival_slot)
        return 0.0

    def run(self) -> list[TrainingEpisodeSummary]:
        summaries: list[TrainingEpisodeSummary] = []
        runner = self._evaluation_runner()
        for episode_index in range(self.config.episode_count):
            trace = runner._trace_for_episode(episode_index)
            summary = self._run_episode(trace, runner)
            summaries.append(summary)
            if (
                self.config.target_network_update_frequency > 0
                and (episode_index + 1) % self.config.target_network_update_frequency == 0
                and hasattr(self.policy.model, "dueling_dqn")
            ):
                self.policy.sync_target_network()
            self.logger.log_episode(
                config=self.config,
                seeds=self.config.seed_management,
                episode_index=episode_index,
                loss=None,
                replay_buffer_size=len(self.policy.replay_buffer),
            )
        return summaries
