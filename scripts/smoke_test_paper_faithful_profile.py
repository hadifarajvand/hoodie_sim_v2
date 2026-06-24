#!/usr/bin/env python3
"""
Smoke test: Paper-faithful HOODIE baseline.

Tests whether the paper-faithful configuration (task_size [2-5], density 0.297)
produces mixed action distributions instead of collapse.

Runs 10 and 50 episode training, captures action distributions.
Does NOT run full 5000-episode Option B.
"""

import sys
import json
import csv
from pathlib import Path
from typing import Any

from src.analysis.paper_faithful_profile.config import build_paper_faithful_profile
from src.analysis.paper_faithful_profile.calibration import patched_paper_faithful_environment
from src.analysis.per_EA_distributed_baseline.config import DistributedBaselineConfig
from src.analysis.per_EA_distributed_baseline.distributed_trainer import DistributedTrainer


def run_smoke_test_paper_faithful() -> dict[str, Any]:
    """Run smoke test with paper-faithful parameters."""

    output_dir = Path("artifacts/analysis/paper-faithful-profile-smoke")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Build config
    cfg = DistributedBaselineConfig()
    profile = build_paper_faithful_profile()

    results = {
        "test_type": "smoke_test_paper_faithful",
        "date": "2026-06-24",
        "profile_validation": profile.to_dict(),
        "episodes": [],
    }

    print("\n" + "="*80)
    print("SMOKE TEST: PAPER-FAITHFUL PROFILE")
    print("="*80 + "\n")

    print(f"Configuration:")
    print(f"  Profile: {profile.profile_name}")
    print(f"  Task size: [{profile.task_size_mbits_min}, {profile.task_size_mbits_max}] Mbits (step={profile.task_size_mbits_step})")
    print(f"  Processing density: {profile.processing_density_gcycles_per_mbit} Gcycles/Mbit")
    print(f"  Epsilon: {profile.epsilon_start} → {profile.epsilon_end} over {profile.epsilon_decay_episodes} episodes")
    print()

    # Run smoke test with paper-faithful environment
    with patched_paper_faithful_environment(profile, output_dir / "traces"):
        trainer = DistributedTrainer(
            cfg,
            epsilon_decay_episodes=cfg.smoke_epsilon_decay_episodes,
        )

        for target_episodes in [10, 50]:
            print(f"Training to {target_episodes} episodes...")

            while trainer.episode_count < target_episodes:
                episode_result = trainer.train_episode(trainer.episode_count)
                trainer.episode_count += 1

            # Evaluate at this checkpoint
            print(f"  Evaluating at {target_episodes} episodes...")
            eval_results = trainer.evaluate(
                episode_count=trainer.episode_count,
                num_episodes=10,
            )

            action_distribution = eval_results.get("evaluation_action_distribution", {})
            action_counts = {
                "local": action_distribution.get(0, 0),
                "horizontal": action_distribution.get(1, 0),
                "vertical": action_distribution.get(2, 0),
            }
            total_decisions = sum(action_counts.values())

            if total_decisions > 0:
                distribution = {k: v / total_decisions for k, v in action_counts.items()}
            else:
                distribution = {k: 0.0 for k in action_counts.keys()}

            episode_result = {
                "episode_count": trainer.episode_count,
                "evaluation_episodes": 10,
                "action_counts": action_counts,
                "action_distribution": distribution,
                "avg_reward": eval_results.get("evaluation_avg_reward", 0.0),
                "drop_ratio": eval_results.get("evaluation_drop_ratio", 0.0),
            }

            results["episodes"].append(episode_result)

            print(f"  Actions: {distribution['local']:.1%} local, {distribution['horizontal']:.1%} horizontal, {distribution['vertical']:.1%} vertical")
            print(f"  Collapse check: {'❌ COLLAPSED' if max(distribution.values()) >= 0.99 else '✅ MIXED'}")
            print()

    # Save results
    with open(output_dir / "action_distribution_smoke.json", "w") as f:
        json.dump(results, f, indent=2)

    # Generate CSV for easy viewing
    with open(output_dir / "action_distribution_smoke.csv", "w") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["episode_count", "local", "horizontal", "vertical", "collapsed", "avg_reward"],
        )
        writer.writeheader()
        for ep in results["episodes"]:
            dist = ep["action_distribution"]
            writer.writerow({
                "episode_count": ep["episode_count"],
                "local": f"{dist['local']:.4f}",
                "horizontal": f"{dist['horizontal']:.4f}",
                "vertical": f"{dist['vertical']:.4f}",
                "collapsed": "YES" if max(dist.values()) >= 0.99 else "NO",
                "avg_reward": f"{ep['avg_reward']:.4f}",
            })

    print("="*80)
    print(f"Smoke test complete. Results saved to {output_dir}/")
    print("="*80 + "\n")

    return results


def main() -> int:
    """Run smoke test."""
    try:
        results = run_smoke_test_paper_faithful()

        # Check for collapse
        all_collapsed = all(max(ep["action_distribution"].values()) >= 0.99 for ep in results["episodes"])

        if all_collapsed:
            print("\n⚠️  WARNING: All evaluations still show collapse!")
            print("Even with paper-faithful parameters [2-5] Mbits and density 0.297.")
            print("\nThis suggests the root cause is NOT parameter scaling alone.")
            print("Possible causes:")
            print("  1. Missing epsilon exploration")
            print("  2. State vector misses critical features")
            print("  3. Reward formula is asymmetric")
            print("  4. Q-value estimates have high variance")
            return 1
        else:
            print("\n✅ SUCCESS: Mixed action distributions appear with paper-faithful parameters!")
            print("Parameter scaling was the root cause. Full Option B can now be rerun.")
            return 0

    except Exception as e:
        print(f"\n❌ Smoke test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
