from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.config.training_config import TrainingConfig
from src.environment.evaluation_gym_adapter import EvaluationHoodieGymEnvironment
from src.environment.runtime_model import SharedRuntimeParameters
from src.environment.topology import TopologyGraph
from src.evaluation.runner import EvaluationRunner
from src.evaluation.trace_protocol import EvaluationTrace
from src.policies.policy_interface import ReplayTrainablePolicy

from .delayed_reward_training import DelayedRewardTraining
from .event_smdp import AgentEventSMDPAccumulator, EventSMDPTransition
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
    """Shared training entry point with isolated HOODIE and ECHO semantics.

    Both policies consume the same materialized task trace and the same physical
    slot kernel.  Only ECHO uses the agent-specific event-epoch SMDP defined in
    the manuscript.  HOODIE retains the repository's legacy delayed task-reward
    transition path so the baseline is not contaminated by ECHO-only logic.
    """

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

    @property
    def _is_echo(self) -> bool:
        return self.config.policy_name.upper().startswith("ECHO")

    def _evaluation_runner(self) -> EvaluationRunner:
        return EvaluationRunner(
            policy=self.policy,
            config=self.config.to_evaluation_config(),
            topology=self.topology,
            runtime_parameters=self.runtime_parameters,
        )

    def _trace_for_episode(self, episode_index: int) -> EvaluationTrace:
        return self._evaluation_runner()._trace_for_episode(episode_index)

    def _build_environment(self, trace: EvaluationTrace) -> EvaluationHoodieGymEnvironment:
        runtime_parameters = self.runtime_parameters or SharedRuntimeParameters()
        return EvaluationHoodieGymEnvironment(
            episode_length=self.config.episode_length,
            topology=self.topology,
            runtime_parameters=runtime_parameters,
            compute_config=runtime_parameters.to_compute_config(),
            policy_name=self.config.policy_name,
            supplied_trace=trace,
        )

    def _record_smdp_transition(self, transition: EventSMDPTransition) -> None:
        self.policy.record_transition(
            transition.state,
            transition.action,
            transition.reward,
            transition.next_state,
            transition.done,
            delta_slots=transition.delta_slots,
        )
        self.policy.learn_from_replay(self.config.batch_size, self.config.learning_rate)

    def _run_echo_episode(self, trace: EvaluationTrace) -> TrainingEpisodeSummary:
        env = self._build_environment(trace)
        env.reset(seed=trace.seed)
        accumulator = AgentEventSMDPAccumulator(gamma=self.config.discount_factor)
        transitions_recorded = 0

        while True:
            _observation, _reward, terminated, truncated, info = env.step_slot(self.policy)

            # A new decision of EA n closes only that EA's previous interval.
            # Decision events are processed before end-of-slot resolutions, so
            # a task that resolves in this physical slot belongs to the interval
            # opened by the same-slot decision, exactly as Section III defines.
            for decision_event in info.get("decision_events", []):
                transition = accumulator.observe_decision(decision_event)
                if transition is not None:
                    self._record_smdp_transition(transition)
                    transitions_recorded += 1

            for resolution_event in info.get("task_resolution_events", []):
                accumulator.observe_resolution(resolution_event)

            if terminated or truncated:
                terminal_slot = self.config.episode_length
                for transition in accumulator.finalize_terminal(
                    terminal_slot=terminal_slot
                ):
                    self._record_smdp_transition(transition)
                    transitions_recorded += 1
                break

        return TrainingEpisodeSummary(
            episode_index=int(trace.trace_id.rsplit("-", 1)[-1])
            if "-" in trace.trace_id
            else 0,
            trace_id=trace.trace_id,
            transitions_recorded=transitions_recorded,
            replay_buffer_size=len(self.policy.replay_buffer),
        )

    def _run_hoodie_episode(self, trace: EvaluationTrace) -> TrainingEpisodeSummary:
        """Run the isolated legacy HOODIE delayed-reward learner.

        This branch intentionally does not use ERT ordering, deadline masking,
        minimum-lateness fallback, or ECHO interval rewards.  It is retained
        until the paper-reproduction audit freezes the exact HOODIE Bellman
        timing from the original source.
        """

        env = self._build_environment(trace)
        env.reset(seed=trace.seed)
        transitions_recorded = 0
        pending_decisions: dict[int, _PendingDecision] = {}

        while True:
            observation, _reward, terminated, truncated, info = env.step_slot(self.policy)

            for decision in info.get("decision_events", []):
                task_id = int(decision["task_id"])
                pending_decisions[task_id] = _PendingDecision(
                    task_id=task_id,
                    decision_slot=int(decision["decision_slot"]),
                    state=dict(decision["state"]),
                    action=str(decision["action"]),
                )

            for delivery in info.get("reward_delivery_events", []):
                task_id = int(delivery["task_id"])
                pending = pending_decisions.pop(task_id, None)
                if pending is None:
                    continue
                next_state = dict(observation)
                next_state["reward_delivery_event"] = dict(delivery)
                delta_slots = max(1, int(delivery.get("delta_slots", 1)))
                self.policy.record_transition(
                    pending.state,
                    pending.action,
                    float(delivery["reward"]),
                    next_state,
                    bool(terminated or truncated),
                    delta_slots=delta_slots,
                )
                self.policy.learn_from_replay(
                    self.config.batch_size,
                    self.config.learning_rate,
                )
                transitions_recorded += 1

            if terminated or truncated:
                if pending_decisions:
                    raise RuntimeError(
                        "unresolved HOODIE pending decisions at episode end: "
                        f"{sorted(pending_decisions)}"
                    )
                break

        return TrainingEpisodeSummary(
            episode_index=int(trace.trace_id.rsplit("-", 1)[-1])
            if "-" in trace.trace_id
            else 0,
            trace_id=trace.trace_id,
            transitions_recorded=transitions_recorded,
            replay_buffer_size=len(self.policy.replay_buffer),
        )

    def _run_episode(
        self,
        trace: EvaluationTrace,
        runner: EvaluationRunner | None = None,
    ) -> TrainingEpisodeSummary:
        del runner  # Compatibility with existing direct unit-test calls.
        if self._is_echo:
            return self._run_echo_episode(trace)
        return self._run_hoodie_episode(trace)

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
                and (episode_index + 1)
                % self.config.target_network_update_frequency
                == 0
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
