from __future__ import annotations

import math
import json
from collections import deque
from pathlib import Path

from src.analysis.full_training_reproduction_campaign.trainer import (
    DDQNTrainer,
    CampaignPolicy,
    _build_environment,
    _ensure_valid_action,
)
from src.analysis.full_training_reproduction_campaign.config import CampaignConfig
from src.analysis.full_training_reproduction_campaign.replay import (
    build_state_window,
    build_state_window_tensor,
    semantics_to_action_index,
    legal_action_mask_to_tuple,
    ReplayTransition,
)
from src.environment.compute_config import ComputeConfig
from src.environment.topology import TopologyGraph


def diagnose_trace_episode(config: CampaignConfig, *, episode_id: int, episode_length: int, seed: int, output_dir: Path) -> dict:
    env = _build_environment(config, episode_length=episode_length, seed=seed, trace_enabled=False)
    env.reset(seed=seed)

    slot = 0
    total_generated = sum(len(blueprints) for blueprints in env._pending_arrivals.values())
    tasks_loaded = 0
    tasks_admitted = 0
    tasks_completed_execution = 0
    tasks_finalized_completed = 0
    tasks_finalized_dropped = 0
    tasks_pending_at_horizon = 0
    tasks_dequeued_execution = 0
    reward_sum = 0.0

    per_task_trace: dict[int, dict] = {}
    queue_depth_over_time: dict[int, dict[str, int]] = {}
    action_distribution: dict[str, int] = {}

    while True:
        current_task = env.current_task
        slot_before = env.current_slot

        if current_task is not None:
            tasks_loaded += 1
            tid = current_task.task_id
            obs = env.observe_flat(current_task)
            legal_mask = obs.get("legal_action_mask", {})

            action = next(
                (act for act in ["local", "cloud", "horizontal"] if legal_mask.get(act, False)),
                "none",
            )
            if action not in action_distribution:
                action_distribution[action] = 0
            action_distribution[action] += 1
        else:
            action = None

        next_observation, reward, terminated, truncated, info = env.step(action)

        finalized_tasks = info.get("finalized_tasks", [])

        for ft in finalized_tasks:
            ftid = ft.get("task_id")
            outcome = ft.get("terminal_outcome")
            if outcome == "completed":
                tasks_finalized_completed += 1
            elif outcome == "dropped":
                tasks_finalized_dropped += 1
            per_task_trace[ftid] = {
                "finalized_outcome": outcome,
                "finalized_at_slot": slot_before,
                "completion_slot": ft.get("completion_slot"),
            }

        if finalized_tasks:
            reward_sum += float(reward) if not (isinstance(reward, float) and math.isnan(reward)) else 0.0

        private_q_depths = {k: len(v.tasks) for k, v in env._private_queues.items() if v.tasks}
        public_q_depths = {f"{k[1]}@{k[0]}": len(v.tasks) for k, v in env._public_queues.items() if v.tasks}
        offload_q_depths = {f"{k[0]}->{k[1]}": len(v.tasks) for k, v in env._offloading_queues.items() if v.tasks}
        queue_depth_over_time[slot_before] = {
            "private_total": sum(private_q_depths.values()),
            "public_total": sum(public_q_depths.values()),
            "offload_total": sum(offload_q_depths.values()),
            "queue_load": env.queue_load,
            "pending_arrivals_remaining": sum(len(b) for b in env._pending_arrivals.values()),
        }

        if truncated:
            tasks_pending_at_horizon = sum(
                len(queue.tasks) for queue in env._private_queues.values()
            ) + sum(len(queue.tasks) for queue in env._public_queues.values())
            break

        slot += 1

    return {
        "episode_id": episode_id,
        "episode_length": episode_length,
        "total_generated": total_generated,
        "tasks_loaded": tasks_loaded,
        "tasks_admitted": tasks_admitted,
        "tasks_completed_execution": tasks_completed_execution,
        "tasks_dequeued_execution": tasks_dequeued_execution,
        "tasks_finalized_completed": tasks_finalized_completed,
        "tasks_finalized_dropped": tasks_finalized_dropped,
        "tasks_pending_at_horizon": tasks_pending_at_horizon,
        "reward_sum": reward_sum,
        "action_distribution": action_distribution,
        "queue_depth_over_time": queue_depth_over_time,
        "per_task_trace": per_task_trace,
    }


def diagnose_trainer_episode(config: CampaignConfig, *, episode_id: int, episode_length: int, seed: int, trainer: DDQNTrainer, training: bool = False) -> dict:
    env = _build_environment(config, episode_length=episode_length, seed=seed, trace_enabled=False)
    env.reset(seed=seed)

    state_builder = trainer.state_builder
    history = trainer._initial_history(episode_length=episode_length)

    slot = 0
    transition_count = 0
    completed_count = 0
    dropped_count = 0
    terminal_count = 0
    reward_bearing_count = 0
    pending_horizon_count = 0
    illegal_count = 0
    per_finalized: dict[str, str] = {}
    action_dist: dict[str, int] = {}
    loss_values: list[float] = []
    reward_sum = 0.0
    queue_depth_over_time: dict[int, dict] = {}
    task_arrival_time: dict[int, int] = {}
    task_finalization: dict[int, dict] = {}

    while True:
        current_task = env.current_task
        if current_task is not None:
            observation = env.observe_flat(current_task)
            legal_mask = observation.get("legal_action_mask", {})
            action = "local"
            if not _ensure_valid_action(action, legal_mask):
                illegal_count += 1
            action_index = semantics_to_action_index(action)
            if action not in action_dist:
                action_dist[action] = 0
            action_dist[action] += 1
            task_arrival_time[current_task.task_id] = current_task.arrival_slot
        else:
            observation = env.observe_flat()
            action = None
            action_index = -1

        next_observation, reward, terminated, truncated, info = env.step(action)

        next_current_task = env.current_task
        next_feature = trainer._compute_state_vector(next_observation, env)
        history.append(next_feature)
        next_state_window = build_state_window(history, state_dim=config.state_dim)

        finalized_tasks = info.get("finalized_tasks", [])
        reward_available = bool(finalized_tasks)
        terminal_reason = finalized_tasks[0].get("terminal_outcome") if finalized_tasks else None
        terminal_flag = bool(finalized_tasks)
        reward_value = float(reward) if reward_available and not (isinstance(reward, float) and math.isnan(reward)) else 0.0

        if reward_available:
            terminal_count += 1
            reward_bearing_count += 1
            reward_sum += reward_value
            for ft in finalized_tasks:
                ftid = str(ft.get("task_id", ""))
                if ftid:
                    per_finalized[ftid] = ft.get("terminal_outcome", "")
                    task_finalization[ft.get("task_id")] = {
                        "outcome": ft.get("terminal_outcome"),
                        "completion_slot": ft.get("completion_slot"),
                        "finalized_at_slot": env.current_slot,
                    }

        if truncated and (env.current_task is not None or info.get("queue_load", 0) > 0):
            pending_horizon_count += 1
            terminal_reason = "pending_at_horizon"

        if current_task is not None:
            transition = ReplayTransition(
                state=build_state_window(history, state_dim=config.state_dim),
                action=action_index,
                legal_action_mask=legal_action_mask_to_tuple(
                    observation.get("legal_action_mask", {}), action_count=config.action_count
                ),
                next_state=next_state_window,
                reward=reward_value,
                reward_available=reward_available,
                terminal=terminal_flag,
                terminal_reason=terminal_reason,
                pending_at_horizon=bool(
                    truncated and not reward_available
                    and (env.current_task is not None or info.get("queue_load", 0) > 0)
                ),
                arrival_slot=int(getattr(current_task, "arrival_slot", 0)),
                completion_or_drop_slot=int(finalized_tasks[0].get("completion_slot"))
                if finalized_tasks and finalized_tasks[0].get("completion_slot") is not None
                else None,
                agent_id=int(getattr(current_task, "source_agent_id", 0)),
                episode_id=episode_id,
                step_id=transition_count,
                state_dim=config.state_dim,
                action_count=config.action_count,
            )
            trainer.replay_buffer.add(transition)
            transition_count += 1

        queue_depth_over_time[env.current_slot] = {
            "private": sum(len(q.tasks) for q in env._private_queues.values()),
            "public": sum(len(q.tasks) for q in env._public_queues.values()),
            "offload": sum(len(q.tasks) for q in env._offloading_queues.values()),
            "pending": sum(len(b) for b in env._pending_arrivals.values()),
        }

        if terminated or truncated:
            break

        slot += 1

    completed_count = sum(1 for o in per_finalized.values() if o == "completed")
    dropped_count = sum(1 for o in per_finalized.values() if o == "dropped")

    return {
        "episode_id": episode_id,
        "transition_count": transition_count,
        "completed_count": completed_count,
        "dropped_count": dropped_count,
        "terminal_count": terminal_count,
        "reward_bearing_count": reward_bearing_count,
        "pending_horizon_count": pending_horizon_count,
        "illegal_count": illegal_count,
        "reward_sum": reward_sum,
        "action_distribution": action_dist,
        "per_finalized": per_finalized,
        "task_arrival_time": task_arrival_time,
        "task_finalization": task_finalization,
        "queue_depth_over_time": queue_depth_over_time,
    }


def run_full_diagnostic(config: CampaignConfig, *, output_dir: Path, episodes: int = 3, episode_length: int = 200):
    output_dir.mkdir(parents=True, exist_ok=True)

    config = CampaignConfig.paper_default()

    trainer = DDQNTrainer(config)

    results = []
    combined_metrics = {
        "total_transitions": 0,
        "total_completed": 0,
        "total_dropped": 0,
        "total_terminal": 0,
        "total_reward_bearing": 0,
        "total_pending_horizon": 0,
        "total_illegal": 0,
        "total_reward": 0.0,
        "all_actions": {},
    }

    for ep in range(episodes):
        seed_val = config.seed_bundle.training_trace_generation_seed + ep
        result = diagnose_trainer_episode(
            config,
            episode_id=ep,
            episode_length=episode_length,
            seed=seed_val,
            trainer=trainer,
            training=True,
        )
        results.append(result)

        combined_metrics["total_transitions"] += result["transition_count"]
        combined_metrics["total_completed"] += result["completed_count"]
        combined_metrics["total_dropped"] += result["dropped_count"]
        combined_metrics["total_terminal"] += result["terminal_count"]
        combined_metrics["total_reward_bearing"] += result["reward_bearing_count"]
        combined_metrics["total_pending_horizon"] += result["pending_horizon_count"]
        combined_metrics["total_illegal"] += result["illegal_count"]
        combined_metrics["total_reward"] += result["reward_sum"]
        for act, cnt in result["action_distribution"].items():
            combined_metrics["all_actions"][act] = combined_metrics["all_actions"].get(act, 0) + cnt

        ep_path = output_dir / f"episode_{ep}_detail.json"
        with open(ep_path, "w") as f:
            json.dump(result, f, indent=2, default=str)

    report = {
        "config": {
            "feature_id": config.feature_id,
            "action_count": config.action_count,
            "state_dim": config.state_dim,
            "episode_length": episode_length,
            "episodes": episodes,
            "pilot_episode_length": config.pilot_episode_length,
            "evaluation_episode_length": config.evaluation_episode_length,
        },
        "combined": combined_metrics,
        "by_episode": [
            {
                "episode": r["episode_id"],
                "transitions": r["transition_count"],
                "completed": r["completed_count"],
                "dropped": r["dropped_count"],
                "terminal": r["terminal_count"],
                "reward_sum": r["reward_sum"],
            }
            for r in results
        ],
    }

    report_path = output_dir / "zero_completion_root_cause_diagnostic.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    return report


if __name__ == "__main__":
    config = CampaignConfig.paper_default()
    output_dir = Path("artifacts/diagnostics")
    report = run_full_diagnostic(config, output_dir=output_dir, episodes=3, episode_length=200)
    print(json.dumps(report, indent=2))
