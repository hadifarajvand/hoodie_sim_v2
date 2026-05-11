from __future__ import annotations

OFFLOAD_LIFECYCLE_EVENTS: tuple[str, ...] = (
    "selected_action",
    "queued_public",
    "offloaded_cloud",
    "transmission_started",
    "transmission_completed",
    "execution_started",
    "execution_completed",
    "dropped_timeout",
    "reward_emitted",
)

