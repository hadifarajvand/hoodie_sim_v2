from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RewardComputation:
    reward_timing_convention: str
    delay: int | None
    reward: float
    drop_penalty: float | None
    reward_reason: str


def compute_delayed_reward(
    *,
    final_status: str,
    arrival_time: int | None,
    completion_time: int | None,
    drop_penalty: float,
    reward_timing_convention: str = "completion_minus_arrival",
) -> RewardComputation:
    if final_status == "completed" and arrival_time is not None and completion_time is not None:
        delay = max(0, completion_time - arrival_time)
        return RewardComputation(
            reward_timing_convention=reward_timing_convention,
            delay=delay,
            reward=float(-delay),
            drop_penalty=None,
            reward_reason="completed",
        )
    if final_status in {"dropped", "timeout"}:
        return RewardComputation(
            reward_timing_convention=reward_timing_convention,
            delay=None,
            reward=float(-drop_penalty),
            drop_penalty=float(drop_penalty),
            reward_reason=final_status,
        )
    return RewardComputation(
        reward_timing_convention=reward_timing_convention,
        delay=None,
        reward=0.0,
        drop_penalty=None,
        reward_reason=final_status,
    )
