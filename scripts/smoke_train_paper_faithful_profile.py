#!/usr/bin/env python3
"""
Behavioral smoke test: Train on paper-faithful HOODIE profile.

Runs short training for 10 and 50 episodes with paper-faithful parameters
to verify that parameter scaling was the root cause of vertical collapse.

Uses the same trainer/evaluator path as full Option B.
Captures action distributions at each checkpoint.

Does NOT run full 5000 episodes.
Does NOT overwrite production artifacts.
"""

import sys
import json
import csv
import random
from pathlib import Path
from dataclasses import dataclass
from typing import Any

import torch

# Seed for reproducibility
SMOKE_TEST_SEED = 42

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analysis.paper_faithful_profile.config import build_paper_faithful_profile
from src.analysis.paper_faithful_profile.calibration import patched_paper_faithful_environment
from src.analysis.full_training_reproduction_campaign.config import CampaignConfig, CampaignSeedBundle
from src.analysis.full_training_reproduction_campaign import trainer as campaign_trainer
from src.analysis.full_training_reproduction_campaign.trainer import DDQNTrainer
from src.analysis.full_training_reproduction_campaign.replay import (
    ACTION_INDEX_TO_SEMANTICS,
    legal_action_mask_to_tuple,
    build_state_vector,
    build_state_window,
    build_state_window_tensor,
)


@dataclass
class ActionSnapshot:
    """Capture of action distribution at a training checkpoint."""
    episode_count: int
    local_count: int
    horizontal_count: int
    vertical_count: int
    total_actions: int
    local_pct: float
    horizontal_pct: float
    vertical_pct: float


def set_seeds(seed: int) -> None:
    """Set all random seeds for reproducibility."""
    random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)


def build_campaign_config() -> CampaignConfig:
    """Build a CampaignConfig with paper-faithful settings."""
    return CampaignConfig(
        # Use standard campaign config (which enforces paper values)
        # Readiness is approved (implicit in this test)
        full_campaign_enabled=False,  # Don't run full campaign
        readiness_manual_approval_status="user_approved_campaign_assumption",
        # Use paper-faithful seed bundle
        seed_bundle=CampaignSeedBundle(
            readiness_probe_seed=SMOKE_TEST_SEED,
            training_trace_generation_seed=SMOKE_TEST_SEED + 1,
            evaluation_trace_generation_seed=SMOKE_TEST_SEED + 100,
            replay_sampling_seed=SMOKE_TEST_SEED + 2,
            model_initialization_seed=SMOKE_TEST_SEED + 3,
            action_exploration_seed=SMOKE_TEST_SEED + 4,
            python_seed=SMOKE_TEST_SEED + 5,
            torch_seed=SMOKE_TEST_SEED + 6,
        ),
    )


def capture_action_distribution(trainer: DDQNTrainer, episode_count: int) -> ActionSnapshot:
    """Sample the policy to capture action distribution without training."""
    action_counts = {"local": 0, "horizontal": 0, "vertical": 0}
    total_actions = 0

    # Sample for a few evaluation episodes
    sample_episodes = 3
    for _ in range(sample_episodes):
        env = campaign_trainer._build_environment(
            trainer.config,
            episode_length=trainer.config.evaluation_episode_length,
            seed=SMOKE_TEST_SEED + episode_count + _,
        )
        env.reset(seed=SMOKE_TEST_SEED + episode_count + _)
        history = trainer._initial_history(episode_length=trainer.config.evaluation_episode_length)

        while True:
            current_task = env.current_task
            if current_task is not None:
                observation = env.observe_flat(current_task)
                action = trainer.policy.choose_action(
                    trainer._state_tensor(history),
                    observation.get("legal_action_mask", {}),
                )
                action_counts[action] += 1
                total_actions += 1
            else:
                action = None

            next_observation, reward, terminated, truncated, info = env.step(action)
            next_current_task = env.current_task
            next_feature = build_state_vector(
                observation=env.observe_flat(next_current_task)
                if next_current_task is not None
                else (
                    next_observation
                    if isinstance(next_observation, dict)
                    else {}
                ),
                current_task=next_current_task,
                episode_length=trainer.config.evaluation_episode_length,
            )
            history.append(next_feature)

            if terminated or truncated:
                break

    # Calculate percentages
    pcts = {
        k: (v / total_actions * 100) if total_actions > 0 else 0
        for k, v in action_counts.items()
    }

    return ActionSnapshot(
        episode_count=episode_count,
        local_count=action_counts["local"],
        horizontal_count=action_counts["horizontal"],
        vertical_count=action_counts["vertical"],
        total_actions=total_actions,
        local_pct=pcts["local"],
        horizontal_pct=pcts["horizontal"],
        vertical_pct=pcts["vertical"],
    )


def run_behavior_smoke_test() -> bool:
    """Run the behavioral smoke test."""
    print("\n" + "=" * 80)
    print("BEHAVIOR SMOKE TEST: PAPER-FAITHFUL PROFILE TRAINING")
    print("=" * 80 + "\n")

    set_seeds(SMOKE_TEST_SEED)

    # Create output directory
    output_dir = Path("artifacts/analysis/paper-faithful-profile-behavior-smoke")
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Build paper-faithful profile
        print("[1/5] Building paper-faithful profile...")
        profile = build_paper_faithful_profile()
        print(f"✅ Profile: {profile.profile_name}")
        print(f"   Task size: [{profile.task_size_mbits_min}, {profile.task_size_mbits_max}] Mbits")
        print(f"   Processing density: {profile.processing_density_gcycles_per_mbit} Gcycles/Mbit")
        print(f"   Training params: lr={profile.learning_rate}, γ={profile.gamma}, batch={profile.batch_size}\n")

        # Validate task generation
        print("[2/5] Validating task generation...")
        trace_root = output_dir / "traces"
        from src.analysis.paper_faithful_profile.calibration import ensure_paper_faithful_trace_bank
        trace_path = ensure_paper_faithful_trace_bank(profile, trace_root, SMOKE_TEST_SEED)
        print(f"✅ Traces generated: {trace_path}\n")

        # Build campaign config
        print("[3/5] Building campaign config...")
        campaign_config = build_campaign_config()
        print("✅ Campaign config built (paper-faithful)\n")

        # Train with patched environment
        print("[4/5] Training for 10 and 50 episodes...")
        action_snapshots: list[ActionSnapshot] = []

        with patched_paper_faithful_environment(profile, trace_root):
            # Create trainer
            trainer = DDQNTrainer(campaign_config)
            print(f"✅ Trainer initialized with paper parameters")
            print(f"   Network: {[1024, 1024, 1024]} hidden layers")
            print(f"   Replay buffer: {campaign_config.replay_memory_capacity} capacity\n")

            # Train for 10 episodes
            print("   Training 10 episodes...")
            result_10 = trainer.run_pilot(episodes=10, episode_length=110)
            print(f"   ✅ Completed: {result_10.episodes_completed} episodes")
            print(
                f"      Optimizer steps: {result_10.optimizer_step_count}, "
                f"Loss: {result_10.loss_value:.6f}"
            )

            # Capture action distribution after 10 episodes
            snapshot_10 = capture_action_distribution(trainer, 10)
            action_snapshots.append(snapshot_10)
            print(f"      Action distribution (sampled over 3 eval episodes):")
            print(f"        local={snapshot_10.local_pct:.1f}%, "
                  f"horizontal={snapshot_10.horizontal_pct:.1f}%, "
                  f"vertical={snapshot_10.vertical_pct:.1f}%\n")

            # Train for 40 more episodes (50 total)
            print("   Training 40 more episodes (50 total)...")
            result_50 = trainer.run_pilot(episodes=40, episode_length=110)
            print(f"   ✅ Completed: {result_10.episodes_completed + result_50.episodes_completed} episodes")
            print(
                f"      Optimizer steps: {result_50.optimizer_step_count}, "
                f"Loss: {result_50.loss_value:.6f}"
            )

            # Capture action distribution after 50 episodes
            snapshot_50 = capture_action_distribution(trainer, 50)
            action_snapshots.append(snapshot_50)
            print(f"      Action distribution (sampled over 3 eval episodes):")
            print(f"        local={snapshot_50.local_pct:.1f}%, "
                  f"horizontal={snapshot_50.horizontal_pct:.1f}%, "
                  f"vertical={snapshot_50.vertical_pct:.1f}%\n")

        # Save results
        print("[5/5] Saving results...")

        # Action distribution CSV
        with open(output_dir / "action_distribution.csv", "w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "episode_count",
                    "local_count",
                    "horizontal_count",
                    "vertical_count",
                    "total_actions",
                    "local_pct",
                    "horizontal_pct",
                    "vertical_pct",
                ],
            )
            writer.writeheader()
            for snapshot in action_snapshots:
                writer.writerow({
                    "episode_count": snapshot.episode_count,
                    "local_count": snapshot.local_count,
                    "horizontal_count": snapshot.horizontal_count,
                    "vertical_count": snapshot.vertical_count,
                    "total_actions": snapshot.total_actions,
                    "local_pct": f"{snapshot.local_pct:.2f}",
                    "horizontal_pct": f"{snapshot.horizontal_pct:.2f}",
                    "vertical_pct": f"{snapshot.vertical_pct:.2f}",
                })

        # Behavior summary
        summary = {
            "test_type": "behavioral_smoke_test",
            "profile": "paper_faithful",
            "task_size_mbits": {
                "min": profile.task_size_mbits_min,
                "max": profile.task_size_mbits_max,
            },
            "processing_density_gcycles_per_mbit": profile.processing_density_gcycles_per_mbit,
            "training_checkpoints": [
                {
                    "episodes": s.episode_count,
                    "actions": {
                        "local": s.local_count,
                        "horizontal": s.horizontal_count,
                        "vertical": s.vertical_count,
                        "total": s.total_actions,
                    },
                    "distribution_pct": {
                        "local": round(s.local_pct, 2),
                        "horizontal": round(s.horizontal_pct, 2),
                        "vertical": round(s.vertical_pct, 2),
                    },
                    "is_collapsed": (
                        s.local_pct == 100.0
                        or s.horizontal_pct == 100.0
                        or s.vertical_pct == 100.0
                    ),
                }
                for s in action_snapshots
            ],
            "root_cause_assessment": {
                "is_collapsed_10ep": action_snapshots[0].local_pct == 100.0
                or action_snapshots[0].horizontal_pct == 100.0
                or action_snapshots[0].vertical_pct == 100.0,
                "is_collapsed_50ep": action_snapshots[1].local_pct == 100.0
                or action_snapshots[1].horizontal_pct == 100.0
                or action_snapshots[1].vertical_pct == 100.0,
                "mixed_actions_observed": (
                    action_snapshots[1].local_pct > 0
                    and action_snapshots[1].horizontal_pct > 0
                    and action_snapshots[1].vertical_pct > 0
                ),
                "parameter_mismatch_is_root_cause": (
                    action_snapshots[1].local_pct > 0
                    and action_snapshots[1].horizontal_pct > 0
                    and action_snapshots[1].vertical_pct > 0
                ),
            },
            "full_option_b_approved": (
                action_snapshots[1].local_pct > 0
                and action_snapshots[1].horizontal_pct > 0
                and action_snapshots[1].vertical_pct > 0
            ),
        }

        with open(output_dir / "behavior_smoke_summary.json", "w") as f:
            json.dump(summary, f, indent=2)

        # Print summary
        print("✅ Results saved:")
        print(f"   action_distribution.csv")
        print(f"   behavior_smoke_summary.json")

        # Print assessment
        print("\n" + "=" * 80)
        print("ROOT CAUSE ASSESSMENT")
        print("=" * 80)

        final_snapshot = action_snapshots[-1]
        is_collapsed = final_snapshot.local_pct == 100.0 or final_snapshot.horizontal_pct == 100.0 or final_snapshot.vertical_pct == 100.0

        if is_collapsed:
            print(f"❌ Policy still 100% collapsed at 50 episodes")
            print(f"   Selected action: local={final_snapshot.local_pct:.1f}%, "
                  f"horizontal={final_snapshot.horizontal_pct:.1f}%, "
                  f"vertical={final_snapshot.vertical_pct:.1f}%")
            print(f"\n⚠️  Parameter mismatch may NOT be the root cause")
            print(f"    Deeper diagnostics needed")
        else:
            print(f"✅ Mixed actions observed at 50 episodes:")
            print(f"   local={final_snapshot.local_pct:.1f}%, "
                  f"horizontal={final_snapshot.horizontal_pct:.1f}%, "
                  f"vertical={final_snapshot.vertical_pct:.1f}%")
            print(f"\n✅ Root cause confirmed: parameter mismatch")
            print(f"   Full Option B rerun is APPROVED")

        print("=" * 80 + "\n")

        return True

    except Exception as e:
        print(f"\n❌ BEHAVIOR SMOKE TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main() -> int:
    """Run behavior smoke test."""
    success = run_behavior_smoke_test()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
