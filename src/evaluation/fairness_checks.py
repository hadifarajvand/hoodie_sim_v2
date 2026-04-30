from __future__ import annotations

from .config import EvaluationConfig
from .trace_protocol import EvaluationTrace, trace_signature


def assert_fair_evaluation(
    policy_a: str,
    policy_b: str,
    trace_a: EvaluationTrace,
    trace_b: EvaluationTrace,
    config_a: EvaluationConfig,
    config_b: EvaluationConfig,
) -> None:
    if trace_signature(trace_a) != trace_signature(trace_b):
        raise ValueError(
            f"Trace mismatch between {policy_a} and {policy_b}: "
            f"{trace_signature(trace_a)} != {trace_signature(trace_b)}"
        )
    fair_config_a = {
        "seed": config_a.seed,
        "episode_count": config_a.episode_count,
        "episode_length": config_a.episode_length,
        "trace_mode": config_a.trace_mode,
    }
    fair_config_b = {
        "seed": config_b.seed,
        "episode_count": config_b.episode_count,
        "episode_length": config_b.episode_length,
        "trace_mode": config_b.trace_mode,
    }
    if fair_config_a != fair_config_b:
        raise ValueError(
            f"Evaluation condition mismatch between {policy_a} and {policy_b}: "
            f"{fair_config_a} != {fair_config_b}"
        )
