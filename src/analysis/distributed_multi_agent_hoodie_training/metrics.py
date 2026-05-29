from __future__ import annotations


def summarize_agent_counts(count: int) -> dict[str, int | bool]:
    return {
        "agent_count": count,
        "online_network_count": count,
        "target_network_count": count,
        "optimizer_count": count,
        "replay_buffer_count": count,
        "policy_count": count,
        "shared_network_instance_detected": False,
    }

