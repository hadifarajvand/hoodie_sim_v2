from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch

from decision_makers.dummies import AllLocal
from environment import Environment
from environment.paper_horizon import (
    PAPER_ACTION_SLOTS,
    PAPER_DRAIN_SLOTS,
    PAPER_TOTAL_SLOTS,
    build_run_horizon_report,
    slot_phase,
)
from phase1_tracing import TraceRecorder
from training.orchestrate_model11 import orchestrate


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True))


def _build_smoke_environment(seed: int, trace_recorder: TraceRecorder) -> Environment:
    np.random.seed(seed)
    torch.manual_seed(seed)
    return Environment(
        static_frequency=False,
        number_of_servers=2,
        private_cpu_capacities=[1, 1],
        public_cpu_capacities=[1, 1],
        connection_matrix=[[0, 1], [1, 0]],
        cloud_computational_capacity=1,
        episode_time=PAPER_ACTION_SLOTS,
        task_arrive_probabilities=[1.0, 1.0],
        task_size_mins=[1, 1],
        task_size_maxs=[1, 1],
        task_size_distributions=["constant", "constant"],
        timeout_delay_mins=[10, 10],
        timeout_delay_maxs=[10, 10],
        timeout_delay_distributions=["constant", "constant"],
        priotiry_mins=[1, 1],
        priotiry_maxs=[1, 1],
        priotiry_distributions=["constant", "constant"],
        computational_density_mins=[1, 1],
        computational_density_maxs=[1, 1],
        computational_density_distributions=["constant", "constant"],
        drop_penalty_mins=[1, 1],
        drop_penalty_maxs=[1, 1],
        drop_penalty_distributions=["constant", "constant"],
        paper_state_window=4,
        vertical_offloading_rate=1.0,
        trace_recorder=trace_recorder,
    )


def _run_episode(env: Environment, agents: list[AllLocal], trace_recorder: TraceRecorder, episode_id: int) -> None:
    env.episode_id = episode_id
    observations, done, _ = env.reset()
    local_observations, public_queues = observations
    accumulated_rewards: list[float] = []
    for _ in range(PAPER_TOTAL_SLOTS):
        step_time = env.current_time
        current_phase = slot_phase(step_time)
        trace_recorder.note_run_horizon_trace(
            episode_id=episode_id,
            time=step_time,
            slot_phase=current_phase,
            paper_action_slot=current_phase == "action",
            paper_drain_slot=current_phase == "drain",
            task_generation_allowed=current_phase == "action",
            decision_allowed=current_phase == "action",
        )
        actions = np.zeros(env.number_of_servers, dtype=int)
        if current_phase == "action":
            for agent_id in range(env.number_of_servers):
                paper_state = env.get_paper_state(agent_id)
                if paper_state["x_n_t"] == 1 and paper_state["task_id"] is not None:
                    trace_recorder.note_pending_transition(
                        task_id=int(paper_state["task_id"]),
                        episode_id=episode_id,
                        source_agent=agent_id,
                        arrival_time=int(env.tasks[agent_id].arrival_time),
                        decision_time=step_time,
                        state_at_decision=np.asarray(local_observations[agent_id], dtype=np.float32).copy(),
                        lstm_state_at_decision=np.asarray(public_queues[agent_id], dtype=np.float32).copy(),
                        action_at_decision=0,
                        selected_target_node=agent_id,
                        raw_action_id=0,
                        first_stage_decision="local",
                        destination_type="local",
                        destination_node_id=agent_id,
                        immediate_next_state_after_action=np.asarray(local_observations[agent_id], dtype=np.float32).copy(),
                        immediate_next_lstm_state_after_action=np.asarray(public_queues[agent_id], dtype=np.float32).copy(),
                        created_by_policy="AllLocal",
                        replay_pairing_status="pending",
                    )
                    trace_recorder.note_action(
                        episode_id=episode_id,
                        time=step_time,
                        agent_id=agent_id,
                        x_n_t=1,
                        observation_shape=np.shape(local_observations[agent_id]),
                        selected_action=0,
                        target_node=agent_id,
                        reward_received=0.0,
                        first_stage_decision="local",
                        destination_node_id=agent_id,
                        destination_type="local",
                        is_valid=True,
                        adjacency_allowed=True,
                        cloud_target=False,
                        d_n_1=1,
                        d_nk_2={},
                        paper_destination_nodes=(),
                        paper_d_nk_2=(),
                        dm2_timing="not_applicable",
                        requires_separate_dm2_at_offloading_queue_exit=False,
                        paper_u_n_t=int(env.last_paper_queue_arrivals[agent_id]),
                        dm2_pending=False,
                    )
        observations, rewards, done, info = env.step(actions)
        accumulated_rewards.extend(float(value) for value in np.asarray(rewards).reshape(-1))
        local_observations, public_queues = observations
        trace_recorder.resolve_delayed_reward_candidates(episode_id)
        if done:
            break
    trace_recorder.finalize_episode(
        episode_id,
        total_reward=float(sum(accumulated_rewards)),
        mean_reward=float(sum(accumulated_rewards) / len(accumulated_rewards)) if accumulated_rewards else 0.0,
    )


def run_paper_smoke(
    output_dir: str | Path,
    seed: int = 7,
    agents: int = 2,
    episodes: int = 1,
    trace_level: str = "full",
    orchestrate_training: bool = False,
    algorithm: str = "dqn",
    train_lstm: bool = False,
) -> dict[str, object]:
    if agents != 2:
        raise ValueError("paper smoke contract currently supports exactly 2 agents")
    if episodes != 1:
        raise ValueError("paper smoke contract currently supports exactly 1 episode")
    if trace_level != "full":
        raise ValueError("paper smoke contract requires trace_level='full'")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    trace_dir = output_dir / "trace"
    trace_dir.mkdir(parents=True, exist_ok=True)
    trace_recorder = TraceRecorder(trace_level=trace_level)
    env = _build_smoke_environment(seed, trace_recorder)
    policy_agents = [AllLocal() for _ in range(env.number_of_servers)]
    for episode_id in range(episodes):
        _run_episode(env, policy_agents, trace_recorder, episode_id)

    trace_recorder.export(trace_dir)
    horizon_report = build_run_horizon_report(trace_dir)
    _write_json(trace_dir / "run_horizon_report.json", horizon_report)
    if not horizon_report.get("horizon_contract_passed"):
        raise ValueError("paper horizon contract failed during smoke execution")

    orchestration_status = "skipped"
    orchestration_manifest_path = None
    if orchestrate_training:
        orchestration_dir = output_dir / "orchestration"
        result = orchestrate(
            trace_dir=trace_dir,
            output_dir=orchestration_dir,
            algorithm=algorithm,
            epochs=1,
            batch_size=1,
            checkpoint_every=1,
            seed=seed,
            train_lstm=train_lstm,
        )
        orchestration_status = "passed"
        orchestration_manifest_path = str(orchestration_dir / "model11_orchestration_manifest.json")
        if not result["manifest"].get("paper_claims_made") is False:
            raise ValueError("paper claims were made during orchestration")

    generated_artifacts = sorted(
        [
            str(path.relative_to(output_dir))
            for path in output_dir.rglob("*")
            if path.is_file()
        ]
    )
    smoke_report = {
        "model": "Model 13 — Paper-Run Smoke Execution Contract",
        "status": "passed",
        "paper_claims_made": False,
        "official_reproduction_claimed": False,
        "simulation_scale": "tiny_smoke_only",
        "episodes": episodes,
        "agents": agents,
        "seed": seed,
        "action_slots": PAPER_ACTION_SLOTS,
        "drain_slots": PAPER_DRAIN_SLOTS,
        "total_slots": PAPER_TOTAL_SLOTS,
        "trace_dir": str(trace_dir),
        "run_horizon_report_path": str(trace_dir / "run_horizon_report.json"),
        "horizon_contract_passed": bool(horizon_report.get("horizon_contract_passed")),
        "orchestration_requested": bool(orchestrate_training),
        "orchestration_status": orchestration_status,
        "orchestration_manifest_path": orchestration_manifest_path,
        "generated_artifacts": generated_artifacts,
        "large_artifacts_created": False,
        "full_pytest_executed": False,
        "cleanup_performed": False,
        "git_add_dot_used": False,
    }
    _write_json(output_dir / "paper_smoke_execution_report.json", smoke_report)
    return smoke_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--agents", type=int, default=2)
    parser.add_argument("--episodes", type=int, default=1)
    parser.add_argument("--trace-level", choices=("full", "summary"), default="full")
    parser.add_argument("--orchestrate", action="store_true")
    parser.add_argument("--algorithm", choices=("dqn", "ddqn", "dueling_dqn"), default="dqn")
    parser.add_argument("--train-lstm", action="store_true")
    args = parser.parse_args()
    run_paper_smoke(
        output_dir=args.output_dir,
        seed=args.seed,
        agents=args.agents,
        episodes=args.episodes,
        trace_level=args.trace_level,
        orchestrate_training=args.orchestrate,
        algorithm=args.algorithm,
        train_lstm=args.train_lstm,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
