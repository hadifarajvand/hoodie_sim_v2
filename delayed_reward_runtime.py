from __future__ import annotations

import json
from typing import Any

import numpy as np


def process_delayed_reward_events(agents: list[Any], trace_recorder: Any, delayed_reward_events: list[dict[str, Any]]) -> dict[str, int]:
    replay_inserted_count = 0
    paired_count = 0
    unresolved_count = 0
    for event in delayed_reward_events:
        pending = event.get("pending_transition")
        source_agent = event.get("source_agent")
        replay_inserted = False
        if pending is not None and source_agent is not None and 0 <= int(source_agent) < len(agents):
            paired_count += 1
            agent = agents[int(source_agent)]
            if bool(getattr(agent, "supports_replay", False)):
                agent.store_transitions(
                    state=np.asarray(json.loads(pending.state_at_decision_json), dtype=np.float32),
                    lstm_state=np.asarray(json.loads(pending.lstm_state_at_decision_json), dtype=np.float32),
                    action=int(pending.action_at_decision),
                    reward=float(event["reward"]),
                    new_state=np.asarray(json.loads(pending.immediate_next_state_after_action_json), dtype=np.float32),
                    new_lstm_state=np.asarray(json.loads(pending.immediate_next_lstm_state_after_action_json), dtype=np.float32),
                    done=event["final_status"] in {"completed", "dropped"},
                )
                replay_inserted = True
                replay_inserted_count += 1
        else:
            unresolved_count += 1
        trace_recorder.note_delayed_reward_event(
            task_id=int(event["task_id"]),
            episode_id=event["episode_id"],
            source_agent=int(source_agent) if source_agent is not None else -1,
            decision_time=int(event["decision_time"]),
            final_status=event["final_status"],
            completion_time=event["completion_time"],
            drop_time=event["drop_time"],
            delay=event["delay"],
            reward=float(event["reward"]),
            drop_penalty=event["drop_penalty"],
            reward_reason=event["reward_reason"],
            paired_transition_found=bool(event["paired_transition_found"]),
            replay_inserted=replay_inserted,
            replay_pairing_status="paired_replay_inserted" if replay_inserted else event["replay_pairing_status"],
            reward_timing_convention=event["reward_timing_convention"],
        )
    return {
        "replay_inserted_count": replay_inserted_count,
        "paired_count": paired_count,
        "unresolved_count": unresolved_count,
    }
