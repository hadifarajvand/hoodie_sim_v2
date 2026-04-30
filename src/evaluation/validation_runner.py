from __future__ import annotations

from dataclasses import dataclass, field, replace

from src.config.config_freeze import FrozenConfig
from src.evaluation.config import EvaluationConfig
from src.evaluation.fairness_checks import assert_fair_evaluation
from src.evaluation.runner import EvaluationRunner, PolicyProtocol
from src.evaluation.trace_protocol import EvaluationTrace, build_deterministic_trace
from src.environment.topology import TopologyGraph


@dataclass(slots=True)
class ValidationPolicyResult:
    policy_name: str
    trace_results: dict[str, object]


@dataclass(slots=True)
class ValidationRunResult:
    config_snapshot: str
    config_hash: str
    baseline_policy_name: str
    policy_order: tuple[str, ...]
    policy_results: list[ValidationPolicyResult] = field(default_factory=list)


@dataclass(slots=True)
class ValidationRunner:
    policies: dict[str, PolicyProtocol]
    config: EvaluationConfig
    topology: TopologyGraph | None = None
    config_freeze: FrozenConfig | None = None

    def __post_init__(self) -> None:
        if self.config_freeze is None:
            self.config_freeze = FrozenConfig(self.config)

    def _trace_for_policy(self, policy_name: str, episode_index: int) -> EvaluationTrace:
        trace_id = f"{self.config.trace_id}-{episode_index}"
        return build_deterministic_trace(trace_id, self.config.seed + episode_index, self.config.episode_length)

    def run(self) -> ValidationRunResult:
        assert self.config_freeze is not None
        self.config_freeze.ensure_unchanged()
        policy_results: list[ValidationPolicyResult] = []
        baseline_policy_name = next(iter(self.policies)) if self.policies else ""
        policy_order: tuple[str, ...] = tuple(self.policies.keys())
        for policy_name, policy in self.policies.items():
            policy_config = replace(self.config, policy_name=policy_name)
            runner = EvaluationRunner(policy=policy, config=policy_config, topology=self.topology)
            for episode_index in range(self.config.episode_count):
                trace = self._trace_for_policy(policy_name, episode_index)
                if policy_name != baseline_policy_name:
                    baseline_trace = self._trace_for_policy(baseline_policy_name, episode_index)
                    assert_fair_evaluation(
                        baseline_policy_name,
                        policy_name,
                        baseline_trace,
                        trace,
                        self.config,
                        self.config,
                    )
            run_output = runner.run()
            policy_results.append(ValidationPolicyResult(policy_name=policy_name, trace_results=run_output))
        return ValidationRunResult(
            config_snapshot=self.config_freeze.snapshot,
            config_hash=self.config_freeze.hash,
            baseline_policy_name=baseline_policy_name,
            policy_order=policy_order,
            policy_results=policy_results,
        )
