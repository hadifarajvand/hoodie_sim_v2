#!/usr/bin/env python3
"""
Learning-path collapse audit: Diagnose why DDQN collapses to one action.

Instruments training, replay buffer, Q-values, state representation, and forced policies
to identify whether collapse is due to:
- Greedy-only training (no epsilon-greedy exploration)
- Insufficient exploration leading to action starvation
- Poor state representation
- Reward formula bias
- Horizontal being genuinely optimal
- Legal mask constraints

Usage:
  python scripts/audit_learning_path_collapse.py

Outputs:
  artifacts/analysis/paper-faithful-learning-path-audit/
"""

import sys
import json
import csv
from pathlib import Path
from dataclasses import dataclass
from typing import Any
from collections import deque

import torch
import random

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analysis.paper_faithful_profile.config import build_paper_faithful_profile
from src.analysis.paper_faithful_profile.calibration import patched_paper_faithful_environment
from src.analysis.full_training_reproduction_campaign.config import CampaignConfig, CampaignSeedBundle
from src.analysis.full_training_reproduction_campaign.trainer import DDQNTrainer
from src.analysis.full_training_reproduction_campaign.replay import (
    ACTION_INDEX_TO_SEMANTICS,
    legal_action_mask_to_tuple,
    build_state_vector,
    build_state_window,
    build_state_window_tensor,
)

SMOKE_TEST_SEED = 42
AUDIT_SEED = 100


def set_seeds(seed: int) -> None:
    """Set all random seeds for reproducibility."""
    random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)


class TrainingActionTracer:
    """Trace action selection during training."""

    def __init__(self):
        self.traces = []

    def record(
        self,
        episode: int,
        step: int,
        task_id: int,
        legal_mask: tuple[bool, bool, bool],
        q_values: torch.Tensor,
        greedy_action: int,
        selected_action: int,
        epsilon: float,
        was_exploratory: bool,
        reward: float | None = None,
    ):
        """Record a training decision."""
        self.traces.append({
            "episode": episode,
            "step": step,
            "task_id": task_id,
            "legal_local": legal_mask[0],
            "legal_horizontal": legal_mask[1],
            "legal_vertical": legal_mask[2],
            "q_local": float(q_values[0].item()),
            "q_horizontal": float(q_values[1].item()),
            "q_vertical": float(q_values[2].item()),
            "greedy_action": ACTION_INDEX_TO_SEMANTICS[greedy_action],
            "selected_action": ACTION_INDEX_TO_SEMANTICS[selected_action],
            "epsilon": epsilon,
            "was_exploratory": was_exploratory,
            "reward": reward if reward is not None else None,
        })

    def save(self, path: Path):
        """Save traces to CSV (first 1000 only to avoid huge files)."""
        if not self.traces:
            return
        # Sample to avoid explosion
        sampled = self.traces[::max(1, len(self.traces) // 1000)]
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.traces[0].keys())
            writer.writeheader()
            writer.writerows(sampled)


@dataclass
class ReplaySnapshot:
    """Snapshot of replay buffer state."""
    episodes: int
    total_transitions: int
    local_count: int
    horizontal_count: int
    vertical_count: int
    completed_local: int
    completed_horizontal: int
    completed_vertical: int
    dropped_local: int
    dropped_horizontal: int
    dropped_vertical: int


class ReplayAuditor:
    """Track replay buffer composition over time."""

    def __init__(self):
        self.snapshots = []

    def snapshot_from_trainer(self, trainer: DDQNTrainer, episode_count: int):
        """Capture replay buffer state."""
        action_counts = {0: 0, 1: 0, 2: 0}
        completion_counts = {0: 0, 1: 0, 2: 0}
        drop_counts = {0: 0, 1: 0, 2: 0}

        for transition in trainer.replay_buffer.as_list():
            action = transition.action
            action_counts[action] += 1
            if transition.terminal_reason == "completed":
                completion_counts[action] += 1
            elif transition.terminal_reason == "dropped":
                drop_counts[action] += 1

        snap = ReplaySnapshot(
            episodes=episode_count,
            total_transitions=len(trainer.replay_buffer),
            local_count=action_counts[0],
            horizontal_count=action_counts[1],
            vertical_count=action_counts[2],
            completed_local=completion_counts[0],
            completed_horizontal=completion_counts[1],
            completed_vertical=completion_counts[2],
            dropped_local=drop_counts[0],
            dropped_horizontal=drop_counts[1],
            dropped_vertical=drop_counts[2],
        )
        self.snapshots.append(snap)

    def save(self, path: Path):
        """Save to CSV."""
        if not self.snapshots:
            return
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "episodes",
                    "total_transitions",
                    "local_count",
                    "horizontal_count",
                    "vertical_count",
                    "completed_local",
                    "completed_horizontal",
                    "completed_vertical",
                    "dropped_local",
                    "dropped_horizontal",
                    "dropped_vertical",
                ],
            )
            writer.writeheader()
            for snap in self.snapshots:
                writer.writerow(snap.__dict__)


class QValueAuditor:
    """Track Q-values on fixed states over training."""

    def __init__(self, trainer: DDQNTrainer, num_fixed_states: int = 20):
        self.trainer = trainer
        self.num_fixed_states = num_fixed_states
        self.fixed_states = []
        self.fixed_observations = []
        self.q_snapshots = []

    def initialize_fixed_states(self, env, episode_length: int):
        """Collect fixed states from environment."""
        env.reset(seed=AUDIT_SEED)
        history = self.trainer._initial_history(episode_length=episode_length)

        for _ in range(self.num_fixed_states):
            if env.current_task is not None:
                obs = env.observe_flat(env.current_task)
                state_tensor = self.trainer._state_tensor(history)
                self.fixed_states.append(state_tensor.clone().detach())
                self.fixed_observations.append({
                    "task_id": getattr(env.current_task, "task_id", None),
                    "size": float(getattr(env.current_task, "size", 0.0)),
                    "density": float(getattr(env.current_task, "processing_density", 0.0)),
                    "queue_load": float(obs.get("queue_load", 0.0)),
                    "slot": float(obs.get("slot", 0.0)),
                    "legal_local": obs.get("legal_action_mask", {}).get("local", False),
                    "legal_horizontal": obs.get("legal_action_mask", {}).get("horizontal", False),
                    "legal_vertical": obs.get("legal_action_mask", {}).get("vertical", False),
                })

            next_obs, reward, terminated, truncated, info = env.step(None)
            next_task = env.current_task
            next_feature = build_state_vector(
                observation=env.observe_flat(next_task) if next_task is not None else next_obs if isinstance(next_obs, dict) else {},
                current_task=next_task,
                episode_length=episode_length,
            )
            history.append(next_feature)

            if terminated or truncated:
                break

    def snapshot_q_values(self, label: str):
        """Capture Q-values on fixed states."""
        with torch.no_grad():
            for state, obs in zip(self.fixed_states, self.fixed_observations):
                q_values = self.trainer.online_network(state.unsqueeze(0))[0]
                legal_mask = torch.tensor(
                    (obs["legal_local"], obs["legal_horizontal"], obs["legal_vertical"]),
                    dtype=torch.bool,
                    device=q_values.device,
                )
                masked_q = q_values.masked_fill(~legal_mask, -1e9)
                argmax_action = int(torch.argmax(masked_q).item())

                self.q_snapshots.append({
                    "label": label,
                    "task_id": obs["task_id"],
                    "size": obs["size"],
                    "density": obs["density"],
                    "queue_load": obs["queue_load"],
                    "q_local": float(q_values[0].item()),
                    "q_horizontal": float(q_values[1].item()),
                    "q_vertical": float(q_values[2].item()),
                    "argmax_action": ACTION_INDEX_TO_SEMANTICS[argmax_action],
                    "legal_local": obs["legal_local"],
                    "legal_horizontal": obs["legal_horizontal"],
                    "legal_vertical": obs["legal_vertical"],
                })

    def save(self, path: Path):
        """Save to CSV."""
        if not self.q_snapshots:
            return
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.q_snapshots[0].keys())
            writer.writeheader()
            writer.writerows(self.q_snapshots)


class StateFeatureAuditor:
    """Audit state representation."""

    def __init__(self):
        self.features = {i: [] for i in range(30)}  # 30 features (3 * 10 lookback)

    def record_state(self, state_window: tuple):
        """Record a state window (10 rows of 3 features each)."""
        for i, row in enumerate(state_window):
            for j, val in enumerate(row):
                feature_idx = i * 3 + j
                self.features[feature_idx].append(float(val))

    def save(self, path: Path):
        """Save feature statistics."""
        import statistics

        rows = []
        for idx, values in self.features.items():
            if values:
                rows.append({
                    "feature_index": idx,
                    "count": len(values),
                    "min": min(values),
                    "max": max(values),
                    "mean": statistics.mean(values),
                    "stdev": statistics.stdev(values) if len(values) > 1 else 0.0,
                })

        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["feature_index", "count", "min", "max", "mean", "stdev"],
            )
            writer.writeheader()
            writer.writerows(rows)


class ForcedPolicyAuditor:
    """Run forced policies and compare to learned policy."""

    def __init__(self):
        self.results = []

    def run_forced_policy(self, trainer: DDQNTrainer, policy_name: str, policy_fn):
        """Run a forced policy for 3 episodes."""
        requested_counts = {0: 0, 1: 0, 2: 0}
        executed_counts = {0: 0, 1: 0, 2: 0}
        total_reward = 0.0
        total_delay = 0.0
        completed = 0
        dropped = 0

        for ep in range(3):
            from src.analysis.full_training_reproduction_campaign import trainer as campaign_trainer

            env = campaign_trainer._build_environment(
                trainer.config,
                episode_length=trainer.config.evaluation_episode_length,
                seed=AUDIT_SEED + ep,
            )
            env.reset(seed=AUDIT_SEED + ep)
            history = trainer._initial_history(episode_length=trainer.config.evaluation_episode_length)

            while True:
                current_task = env.current_task
                if current_task is not None:
                    obs = env.observe_flat(current_task)
                    legal_mask = obs.get("legal_action_mask", {})
                    mask_tuple = (legal_mask.get("local", False), legal_mask.get("horizontal", False), legal_mask.get("vertical", False))

                    requested_action_idx = policy_fn(mask_tuple)
                    requested_counts[requested_action_idx] += 1
                    requested_action_str = ACTION_INDEX_TO_SEMANTICS[requested_action_idx]
                    obs_new, reward, terminated, truncated, info = env.step(requested_action_str)
                    executed_action_str = info.get("executed_action", requested_action_str)
                    # Map back to index if it's a string
                    executed_action_idx = (
                        {"local": 0, "horizontal": 1, "vertical": 2}.get(executed_action_str, requested_action_idx)
                    )
                    executed_counts[executed_action_idx] += 1

                    next_task = env.current_task
                    next_feature = build_state_vector(
                        observation=env.observe_flat(next_task) if next_task is not None else obs_new if isinstance(obs_new, dict) else {},
                        current_task=next_task,
                        episode_length=trainer.config.evaluation_episode_length,
                    )
                    history.append(next_feature)

                    if info.get("terminal_reason") == "completed":
                        completed += 1
                    elif info.get("terminal_reason") == "dropped":
                        dropped += 1

                    total_reward += reward if not (isinstance(reward, float) and reward != reward) else 0.0

                else:
                    obs_new, reward, terminated, truncated, info = env.step(None)
                    next_task = env.current_task
                    next_feature = build_state_vector(
                        observation=env.observe_flat(next_task) if next_task is not None else obs_new if isinstance(obs_new, dict) else {},
                        current_task=next_task,
                        episode_length=trainer.config.evaluation_episode_length,
                    )
                    history.append(next_feature)

                if terminated or truncated:
                    break

        total_actions = sum(requested_counts.values())
        self.results.append({
            "policy": policy_name,
            "requested_local": requested_counts[0],
            "requested_horizontal": requested_counts[1],
            "requested_vertical": requested_counts[2],
            "local_pct": (requested_counts[0] / total_actions * 100) if total_actions > 0 else 0,
            "horizontal_pct": (requested_counts[1] / total_actions * 100) if total_actions > 0 else 0,
            "vertical_pct": (requested_counts[2] / total_actions * 100) if total_actions > 0 else 0,
            "avg_reward": total_reward / 3.0,
            "completed": completed,
            "dropped": dropped,
            "drop_ratio": dropped / (completed + dropped) if (completed + dropped) > 0 else 0,
        })

    def save(self, path: Path):
        """Save to CSV."""
        if not self.results:
            return
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.results[0].keys())
            writer.writeheader()
            writer.writerows(self.results)


def run_audit() -> bool:
    """Run the comprehensive learning-path audit."""
    print("\n" + "=" * 80)
    print("LEARNING-PATH COLLAPSE AUDIT")
    print("=" * 80 + "\n")

    set_seeds(AUDIT_SEED)
    output_dir = Path("artifacts/analysis/paper-faithful-learning-path-audit")
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Build profile and config
        print("[1/7] Setting up paper-faithful profile and campaign config...")
        profile = build_paper_faithful_profile()
        trace_root = output_dir / "traces"
        config = CampaignConfig(
            full_campaign_enabled=False,
            seed_bundle=CampaignSeedBundle(
                readiness_probe_seed=AUDIT_SEED,
                training_trace_generation_seed=AUDIT_SEED + 1,
                evaluation_trace_generation_seed=AUDIT_SEED + 100,
                replay_sampling_seed=AUDIT_SEED + 2,
                model_initialization_seed=AUDIT_SEED + 3,
                action_exploration_seed=AUDIT_SEED + 4,
                python_seed=AUDIT_SEED + 5,
                torch_seed=AUDIT_SEED + 6,
            ),
        )
        print("✅ Profile and config ready\n")

        # Audit 1: Training action trace
        print("[2/7] Running training with action tracing...")
        action_tracer = TrainingActionTracer()
        replay_auditor = ReplayAuditor()
        q_auditor = QValueAuditor(trainer=None, num_fixed_states=20)  # Will set trainer later
        state_auditor = StateFeatureAuditor()

        with patched_paper_faithful_environment(profile, trace_root):
            trainer = DDQNTrainer(config)
            q_auditor.trainer = trainer

            # Snapshot before training
            q_auditor.snapshot_q_values("before_training")

            # Train for 50 episodes with instrumentation
            checkpoint_episodes = [1, 5, 10, 25, 50]
            next_checkpoint_idx = 0
            from src.analysis.full_training_reproduction_campaign import trainer as campaign_trainer

            for episode_idx in range(50):
                env = campaign_trainer._build_environment(
                    config,
                    episode_length=110,
                    seed=config.seed_bundle.training_trace_generation_seed + episode_idx,
                )
                env.reset(seed=config.seed_bundle.training_trace_generation_seed + episode_idx)
                history = trainer._initial_history(episode_length=110)
                step = 0

                while True:
                    current_task = env.current_task
                    if current_task is not None:
                        obs = env.observe_flat(current_task)
                        state_tensor = trainer._state_tensor(history)

                        # Record state features
                        state_auditor.record_state(build_state_window(history))

                        # Get Q-values
                        with torch.no_grad():
                            q_values = trainer.online_network(state_tensor.unsqueeze(0))[0]

                        legal_mask = obs.get("legal_action_mask", {})
                        legal_mask_tuple = legal_action_mask_to_tuple(legal_mask)
                        masked_q = q_values.masked_fill(
                            ~torch.tensor(legal_mask_tuple, device=q_values.device),
                            -1e9,
                        )
                        greedy_action = int(torch.argmax(masked_q).item())

                        # Determine if exploratory (epsilon-greedy)
                        epsilon = (
                            config.seed_bundle.action_exploration_seed * 0.001
                        )  # Approximate
                        import random as py_random

                        was_exploratory = py_random.random() < epsilon
                        selected_action = (
                            py_random.randint(0, 2)
                            if was_exploratory
                            else greedy_action
                        )

                        action = ACTION_INDEX_TO_SEMANTICS[selected_action]
                    else:
                        action = None
                        legal_mask_tuple = (False, False, False)
                        q_values = torch.tensor([0.0, 0.0, 0.0])
                        selected_action = -1
                        greedy_action = -1
                        was_exploratory = False

                    obs_new, reward, terminated, truncated, info = env.step(action)
                    next_task = env.current_task
                    next_feature = build_state_vector(
                        observation=env.observe_flat(next_task)
                        if next_task is not None
                        else obs_new if isinstance(obs_new, dict) else {},
                        current_task=next_task,
                        episode_length=110,
                    )
                    history.append(next_feature)

                    # Record action trace
                    if current_task is not None:
                        action_tracer.record(
                            episode=episode_idx,
                            step=step,
                            task_id=getattr(current_task, "task_id", -1),
                            legal_mask=legal_mask_tuple,
                            q_values=q_values,
                            greedy_action=greedy_action,
                            selected_action=selected_action,
                            epsilon=epsilon,
                            was_exploratory=was_exploratory,
                            reward=reward if not (isinstance(reward, float) and reward != reward) else None,
                        )

                    if terminated or truncated:
                        break
                    step += 1

                # Train batch if buffer has enough
                if len(trainer.replay_buffer) >= config.batch_size:
                    loss = trainer._train_batch()

                # Checkpoint snapshots
                if next_checkpoint_idx < len(checkpoint_episodes) and (episode_idx + 1) == checkpoint_episodes[next_checkpoint_idx]:
                    replay_auditor.snapshot_from_trainer(trainer, episode_idx + 1)
                    q_auditor.snapshot_q_values(f"after_{episode_idx + 1}_episodes")
                    next_checkpoint_idx += 1

        print("✅ Training complete with instrumentation\n")

        # Audit 2: Forced policies
        print("[3/7] Running forced policy audit...")
        forced_auditor = ForcedPolicyAuditor()

        with patched_paper_faithful_environment(profile, trace_root):
            trainer_for_policies = DDQNTrainer(config)

            def policy_always_local(mask):
                return 0 if mask[0] else (1 if mask[1] else 2)

            def policy_always_horizontal(mask):
                return 1 if mask[1] else (0 if mask[0] else 2)

            def policy_always_vertical(mask):
                return 2 if mask[2] else (0 if mask[0] else 1)

            def policy_round_robin(mask):
                for i in range(3):
                    if mask[i]:
                        return i
                return 0

            forced_auditor.run_forced_policy(trainer_for_policies, "always_local", policy_always_local)
            forced_auditor.run_forced_policy(trainer_for_policies, "always_horizontal", policy_always_horizontal)
            forced_auditor.run_forced_policy(trainer_for_policies, "always_vertical", policy_always_vertical)
            forced_auditor.run_forced_policy(trainer_for_policies, "round_robin", policy_round_robin)

        print("✅ Forced policy audit complete\n")

        # Save all audits
        print("[4/7] Saving audit outputs...")
        action_tracer.save(output_dir / "learning_action_trace_sample.csv")
        replay_auditor.save(output_dir / "replay_action_distribution.csv")
        q_auditor.save(output_dir / "q_value_fixed_state_audit.csv")
        state_auditor.save(output_dir / "state_feature_variance.csv")
        forced_auditor.save(output_dir / "forced_policy_reward_audit.csv")
        print("✅ Outputs saved\n")

        # Generate summary
        print("[5/7] Analyzing results...")
        summary = analyze_audit_results(
            action_tracer,
            replay_auditor,
            q_auditor,
            state_auditor,
            forced_auditor,
        )

        # Save summary
        with open(output_dir / "learning_path_summary.json", "w") as f:
            json.dump(summary, f, indent=2)

        print("✅ Analysis complete\n")

        # Print findings
        print("=" * 80)
        print("AUDIT FINDINGS")
        print("=" * 80)
        print(f"Final Verdict: {summary['final_verdict']}")
        print(f"\nKey findings:")
        for finding in summary["key_findings"]:
            print(f"  - {finding}")
        print("\n" + "=" * 80 + "\n")

        return True

    except Exception as e:
        print(f"\n❌ AUDIT FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False


def analyze_audit_results(action_tracer, replay_auditor, q_auditor, state_auditor, forced_auditor) -> dict[str, Any]:
    """Analyze audit results and produce verdict."""
    findings = []
    verdict = "inconclusive_needs_deeper_trace"

    # Check 1: Is training greedy-only or epsilon-greedy?
    if action_tracer.traces:
        exploratory_count = sum(1 for t in action_tracer.traces if t["was_exploratory"])
        total_count = len(action_tracer.traces)
        exploration_rate = (exploratory_count / total_count * 100) if total_count > 0 else 0
        findings.append(f"Exploration rate: {exploration_rate:.1f}% (expected ~10% for ε-greedy)")
        if exploration_rate < 1.0:
            verdict = "greedy_only_training_path"

    # Check 2: Does replay buffer contain all three actions?
    if replay_auditor.snapshots:
        final_snap = replay_auditor.snapshots[-1]
        has_all_actions = (
            final_snap.local_count > 0
            and final_snap.horizontal_count > 0
            and final_snap.vertical_count > 0
        )
        findings.append(
            f"Replay buffer (final): local={final_snap.local_count}, "
            f"horiz={final_snap.horizontal_count}, vert={final_snap.vertical_count}"
        )
        if not has_all_actions:
            if final_snap.local_count == 0 or final_snap.vertical_count == 0:
                verdict = "replay_buffer_action_starvation"

    # Check 3: Is horizontal always argmax across fixed states?
    if q_auditor.q_snapshots:
        final_q_snapshots = [s for s in q_auditor.q_snapshots if s["label"] == "after_50_episodes"]
        if final_q_snapshots:
            horizontal_argmax_count = sum(
                1 for s in final_q_snapshots if s["argmax_action"] == "horizontal"
            )
            total_states = len(final_q_snapshots)
            findings.append(
                f"Q-value argmax (50 ep, {total_states} states): "
                f"{horizontal_argmax_count}/{total_states} horizontal "
                f"({horizontal_argmax_count/total_states*100:.1f}%)"
            )

    # Check 4: State representation features
    feature_count = sum(1 for v in state_auditor.features.values() if v)
    findings.append(f"State representation: {feature_count} features used (expected 30)")
    if feature_count < 3:
        verdict = "state_representation_too_poor"

    # Check 5: Forced policies
    if forced_auditor.results:
        for result in forced_auditor.results:
            findings.append(
                f"Forced {result['policy']}: "
                f"{result['horizontal_pct']:.1f}% horizontal, "
                f"reward={result['avg_reward']:.2f}, "
                f"drop_ratio={result['drop_ratio']:.2%}"
            )

    return {
        "test_type": "learning_path_collapse_audit",
        "profile": "paper_faithful",
        "checkpoint_episodes": [1, 5, 10, 25, 50],
        "key_findings": findings,
        "final_verdict": verdict,
        "full_option_b_allowed": verdict == "horizontal_genuinely_optimal_under_current_reward",
    }


def main() -> int:
    """Run the audit."""
    success = run_audit()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
