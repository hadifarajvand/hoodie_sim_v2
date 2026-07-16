from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import torch

from src.agents.distributed_hoodie import DistributedHoodiePolicy
from src.agents.hoodie_agent import HoodieAgent
from src.environment.topology import TopologyGraph

from ..storage.checkpoints import hydrate_replay_snapshot, save_bounded_checkpoint


_INSTALLED = False
_ORIGINAL_POLICY_FROM_CHECKPOINT: Callable[..., Any] | None = None
_ORIGINAL_LOAD_INTERNAL_CHECKPOINT_STATE: Callable[..., Any] | None = None


def _agent_count(row: Any) -> int:
    values = row.topology_contract.get("agent_counts", [20])
    if isinstance(values, (list, tuple)):
        if len(values) != 1:
            raise ValueError("one checkpoint row must resolve to one agent count")
        return int(values[0])
    return int(values)


def _checkpoint_job_dir(checkpoint_state: dict[str, Any]) -> Path | None:
    record = checkpoint_state.get("checkpoint_record")
    if not isinstance(record, dict):
        return None
    raw = record.get("checkpoint_path")
    if not isinstance(raw, str) or not raw:
        return None
    checkpoint_path = Path(raw)
    # jobs/<job-id>/internal_checkpoints/<checkpoint-id>/checkpoint.pt
    try:
        return checkpoint_path.parents[2]
    except IndexError:
        return None


def load_internal_checkpoint_state(job_dir: Path) -> dict[str, Any] | None:
    """Load and hydrate the latest resumable checkpoint for training.

    The legacy training loop calls this function before constructing the policy.
    Hydrating here ensures external replay state is present when
    ``DistributedHoodiePolicy.from_state`` restores a schema-v3 checkpoint.
    """

    if _ORIGINAL_LOAD_INTERNAL_CHECKPOINT_STATE is None:
        raise RuntimeError("checkpoint storage patch is not installed")
    state = _ORIGINAL_LOAD_INTERNAL_CHECKPOINT_STATE(job_dir)
    if not isinstance(state, dict):
        return state
    if int(state.get("schema_version", 0)) >= 3 and bool(state.get("resume_capable")):
        return hydrate_replay_snapshot(Path(job_dir), state)
    return state


def _load_agent_from_compact_state(
    agent_state: dict[str, Any], *, device_name: str | None
) -> HoodieAgent:
    learner_state = agent_state.get("learner")
    if not isinstance(learner_state, dict):
        raise ValueError("compact checkpoint agent is missing learner state")
    action_order = tuple(str(value) for value in learner_state.get("action_order", ()))
    if not action_order:
        raise ValueError("compact checkpoint learner is missing action_order")
    agent = HoodieAgent.configured(
        seed=int(learner_state.get("seed", 0)),
        use_lstm=bool(agent_state.get("use_lstm", learner_state.get("use_lstm", True))),
        learning_rate=float(learner_state.get("learning_rate", 7e-7)),
        discount_factor=float(learner_state.get("gamma", 0.99)),
        batch_size=int(learner_state.get("batch_size", 64)),
        replay_capacity=int(learner_state.get("capacity", 10_000)),
        target_update_interval=int(learner_state.get("target_update_interval", 2_000)),
        device_name=device_name,
        hidden_dims=tuple(
            int(value)
            for value in learner_state.get("hidden_dims", (1024, 1024, 1024))
        ),
        lookback=int(learner_state.get("lookback", 10)),
        lstm_hidden=int(learner_state.get("lstm_hidden", 20)),
        action_order=action_order,
    )
    inner = agent.learner.learner
    online_state = learner_state.get("online_state_dict")
    if not isinstance(online_state, dict):
        raise ValueError("compact checkpoint learner is missing online_state_dict")
    inner.online_network.load_state_dict(online_state)
    target_state = learner_state.get("target_state_dict")
    inner.target_network.load_state_dict(
        target_state if isinstance(target_state, dict) else online_state
    )
    inner.target_network.eval()
    optimizer_state = learner_state.get("optimizer_state_dict")
    if isinstance(optimizer_state, dict):
        inner.optimizer.load_state_dict(optimizer_state)
        for optimizer_value in inner.optimizer.state.values():
            for key, value in optimizer_value.items():
                if isinstance(value, torch.Tensor):
                    optimizer_value[key] = value.to(inner.device)
    replay_state = learner_state.get("replay_buffer")
    if isinstance(replay_state, dict):
        inner.replay_buffer.load_state_dict(replay_state)
    rng_state = learner_state.get("rng_state")
    if rng_state is not None:
        inner.rng.setstate(rng_state)
    inner.training_steps = int(learner_state.get("training_steps", 0))
    inner.target_update_steps = int(learner_state.get("target_update_steps", 0))
    agent.exploration_epsilon = float(agent_state.get("exploration_epsilon", 0.0))
    agent.causal_history = [
        tuple(float(value) for value in row)
        for row in agent_state.get("causal_history", [])
    ]
    agent.history_builder.window_size = agent._history_limit()
    agent._trim_history()
    return agent


def _load_compact_policy(
    row: Any, checkpoint_state: dict[str, Any]
) -> DistributedHoodiePolicy:
    job_dir = _checkpoint_job_dir(checkpoint_state)
    if bool(checkpoint_state.get("resume_capable")):
        if job_dir is None:
            raise ValueError("resumable checkpoint is missing its job directory")
        hydrate_replay_snapshot(job_dir, checkpoint_state)
    policy_state = checkpoint_state.get("policy_state")
    if not isinstance(policy_state, dict):
        raise ValueError("checkpoint is missing policy_state")
    agents_payload = policy_state.get("agents")
    if not isinstance(agents_payload, dict) or not agents_payload:
        raise ValueError("checkpoint is missing distributed learner states")
    requested_device = None
    backend = str(row.physical_contract.get("backend", "")).strip()
    if backend and backend != "worker-selected":
        requested_device = backend
    agents = {
        str(agent_id): _load_agent_from_compact_state(
            agent_state, device_name=requested_device
        )
        for agent_id, agent_state in agents_payload.items()
        if isinstance(agent_state, dict)
    }
    if len(agents) != len(agents_payload):
        raise ValueError("checkpoint contains a non-dictionary learner state")
    policy = DistributedHoodiePolicy(agents=agents)
    topology = TopologyGraph.for_agent_count(_agent_count(row))
    policy.validate_topology(topology)
    policy.use_lstm = row.variant != "hoodie_no_lstm"
    return policy


def policy_from_checkpoint(row: Any, checkpoint_state: dict[str, Any] | None):
    if row.policy != "HOODIE":
        if _ORIGINAL_POLICY_FROM_CHECKPOINT is None:
            raise RuntimeError("checkpoint storage patch is not installed")
        return _ORIGINAL_POLICY_FROM_CHECKPOINT(row, checkpoint_state)
    if checkpoint_state is None:
        raise ValueError(f"HOODIE evaluation job {row.job_id} requires a checkpoint")
    schema = int(checkpoint_state.get("schema_version", 0))
    if schema < 3:
        if _ORIGINAL_POLICY_FROM_CHECKPOINT is None:
            raise RuntimeError("checkpoint storage patch is not installed")
        return _ORIGINAL_POLICY_FROM_CHECKPOINT(row, checkpoint_state)
    policy = _load_compact_policy(row, checkpoint_state)
    policy.exploration_epsilon = 0.0
    return policy


def bounded_checkpoint_policy(
    *,
    policy: DistributedHoodiePolicy,
    row: Any,
    job_dir: Path,
    source_commit: str,
    next_episode: int,
    episode_rewards: list[float],
    selection_value: float,
) -> str:
    from . import production_campaign as legacy
    from . import production_patch

    policy_state = policy.export_state()
    checkpoint_id = legacy._hash(
        {
            "job_id": row.job_id,
            "source": source_commit,
            "next_episode": next_episode,
            "policy_hash": production_patch._state_hash(policy_state),
        }
    )[:24]
    required_episodes = int(row.training_contract.get("training_episodes", next_episode))
    final = next_episode >= required_episodes
    agents_state = policy_state["agents"]
    online = {
        key: value["learner"]["online_state_dict"]
        for key, value in agents_state.items()
    }
    target = {
        key: value["learner"]["target_state_dict"]
        for key, value in agents_state.items()
    }
    optimizer = {
        key: value["learner"]["optimizer_state_dict"]
        for key, value in agents_state.items()
    }
    replay = {
        key: value["learner"]["replay_buffer"]
        for key, value in agents_state.items()
    }
    checkpoint_state = {
        "schema_version": 3,
        "checkpoint_id": checkpoint_id,
        "next_episode": next_episode,
        "episode_rewards": list(episode_rewards),
        "policy_state": policy_state,
        "backend_type": policy_state["backend_type"],
        "device_string": policy_state["device_string"],
    }
    result = save_bounded_checkpoint(
        job_dir=job_dir,
        checkpoint_id=checkpoint_id,
        checkpoint_state=checkpoint_state,
        final=final,
        metadata={
            "checkpoint_id": checkpoint_id,
            "training_job_id": row.job_id,
            "policy": row.policy,
            "variant": row.variant,
            "training_seed": int(row.seed or 0),
            "selected_episode": max(0, next_episode - 1),
            "selection_rule": "final_episode" if final else "latest_completed_episode",
            "selection_metric": "accumulated_reward",
            "selection_value": float(selection_value),
            "online_network_hash": production_patch._state_hash(online),
            "target_network_hash": production_patch._state_hash(target),
            "optimizer_state_hash": production_patch._state_hash(optimizer),
            "replay_state_hash": production_patch._state_hash(replay),
            "configuration_hash": row.config_hash,
            "topology_hash": legacy._hash(row.topology_contract),
            "workload_hash": legacy._hash(row.workload_contract),
            "source_contract_hash": row.source_contract_hash,
            "source_commit": source_commit,
        },
    )
    legacy._write_json(
        job_dir / "checkpoint_storage_status.json",
        {
            "checkpoint_id": checkpoint_id,
            "checkpoint_sha256": result["checkpoint_sha256"],
            "checkpoint_size_bytes": result["checkpoint_size_bytes"],
            "resume_capable": not final,
            "maximum_retained_checkpoints": 1,
            "replay_snapshot": result["replay_snapshot"],
        },
    )
    return checkpoint_id


def install_checkpoint_storage_patch() -> None:
    global _INSTALLED
    global _ORIGINAL_POLICY_FROM_CHECKPOINT
    global _ORIGINAL_LOAD_INTERNAL_CHECKPOINT_STATE
    if _INSTALLED:
        return
    from . import production_campaign
    from . import production_patch

    _ORIGINAL_POLICY_FROM_CHECKPOINT = production_patch._policy_from_checkpoint
    _ORIGINAL_LOAD_INTERNAL_CHECKPOINT_STATE = (
        production_campaign._load_internal_checkpoint_state
    )
    production_patch._policy_from_checkpoint = policy_from_checkpoint
    production_patch._checkpoint_policy = bounded_checkpoint_policy
    production_campaign._load_internal_checkpoint_state = load_internal_checkpoint_state
    _INSTALLED = True
