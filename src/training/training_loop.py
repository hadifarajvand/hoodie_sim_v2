from __future__ import annotations

from dataclasses import dataclass, field

from src.agents.hoodie_agent import HoodieAgent
from src.config.training_config import TrainingConfig
from src.environment.environment import apply_policy_action, finalize_task_runtime_state_with_parameters
from src.environment.slot_engine import SlotEngine
from src.environment.topology import TopologyGraph
from src.evaluation.runner import EvaluationRunner
from src.evaluation.trace_protocol import EvaluationTrace
from src.policies.policy_interface import PolicyContext

from .delayed_reward_training import DelayedRewardTraining
from .training_logging import TrainingLogger


@dataclass(slots=True)
class TrainingEpisodeSummary:
    episode_index: int
    trace_id: str
    transitions_recorded: int
    replay_buffer_size: int


@dataclass(slots=True)
class TrainingLoop:
    policy: HoodieAgent
    config: TrainingConfig
    topology: TopologyGraph | None = None
    logger: TrainingLogger = field(default_factory=TrainingLogger)
    delayed_reward: DelayedRewardTraining = field(default_factory=DelayedRewardTraining)

    def __post_init__(self) -> None:
        self.policy.replay_buffer.capacity = self.config.replay_buffer_capacity

    def _evaluation_runner(self) -> EvaluationRunner:
        return EvaluationRunner(
            policy=self.policy,
            config=self.config.to_evaluation_config(),
            topology=self.topology,
        )

    def _trace_for_episode(self, episode_index: int) -> EvaluationTrace:
        return self._evaluation_runner()._trace_for_episode(episode_index)

    def _run_episode(self, trace: EvaluationTrace, runner: EvaluationRunner) -> TrainingEpisodeSummary:
        engine = SlotEngine(current_slot=0, trace_metadata=trace.metadata)
        transitions_recorded = 0
        for blueprint in trace.tasks:
            task = blueprint.build()
            legal_action_mask = runner._legal_action_mask(task)
            observation = runner._build_observation(task, legal_action_mask)
            policy_context = PolicyContext(
                observation=observation,
                legal_action_mask=legal_action_mask,
                trace_history=(trace.trace_id,),
            )
            action = self.policy.choose_action(policy_context)
            apply_policy_action(task, policy_context, action, resolved_destination=runner._resolved_destination(task, action))
            engine.run_slot([task])
            finalize_task_runtime_state_with_parameters(task, task.completion_slot or task.arrival_slot, engine.runtime_parameters)

            state = dict(policy_context.observation)
            next_state = {
                "task_id": task.task_id,
                "terminal_outcome": task.terminal_outcome,
                "reward_emitted": task.reward_emitted,
            }
            self.delayed_reward.stage_transition(
                task=task,
                state=state,
                action=action,
                next_state=next_state,
                done=bool(task.reward_emitted),
            )
            ready_transition = self.delayed_reward.consume_ready_transition(task)
            if ready_transition is not None:
                self.policy.record_transition(
                    ready_transition.state,
                    ready_transition.action,
                    ready_transition.reward,
                    ready_transition.next_state,
                    ready_transition.done,
                )
                self.policy.learn_from_replay(self.config.batch_size, self.config.learning_rate)
                transitions_recorded += 1

        return TrainingEpisodeSummary(
            episode_index=int(trace.trace_id.rsplit("-", 1)[-1]) if "-" in trace.trace_id else 0,
            trace_id=trace.trace_id,
            transitions_recorded=transitions_recorded,
            replay_buffer_size=len(self.policy.replay_buffer),
        )

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
