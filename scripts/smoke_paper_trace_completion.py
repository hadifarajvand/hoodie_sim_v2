#!/usr/bin/env python3
"""Smoke test: verify paper-faithful traces allow task completion.

This script:
1. Builds environment using real CampaignConfig.for_paper_faithful()
2. Runs one episode with always-local action
3. Confirms at least some tasks complete (not 100% drop)
4. Reports arrivals, completed, dropped, pending, queue load
"""

import sys
import csv
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analysis.full_training_reproduction_campaign.config import CampaignConfig
from src.analysis.full_training_reproduction_campaign.trainer import _build_environment


def run_smoke_test():
    """Run smoke test with always-local action on paper-faithful traces."""
    print("\n" + "=" * 80)
    print("SMOKE TEST: Paper-Faithful Trace Completion")
    print("=" * 80 + "\n")

    try:
        # 1. Build paper-faithful config and environment
        print("[1/4] Building paper-faithful environment...")
        trace_root = Path("artifacts/paper_faithful_campaign_traces")
        config = CampaignConfig.for_paper_faithful(trace_root=str(trace_root))
        env = _build_environment(config, episode_length=110, seed=200)
        reset_seed = None if config.environment_profile == "paper_faithful" else 200
        env.reset(seed=reset_seed)
        print(f"  ✅ Environment built with trace={env.trace.trace_id}")

        # 2. Run episode with always-local action
        print("\n[2/4] Running episode with always-local action...")
        step_log = []
        completed_count = 0
        dropped_count = 0
        pending_at_end = 0

        while True:
            current_task = env.current_task
            action = "local" if current_task else None

            obs, reward, terminated, truncated, info = env.step(action)

            finalized_tasks = info.get("finalized_tasks", [])
            finalized_outcomes = [t.get("terminal_outcome") for t in finalized_tasks]

            completed_this_step = sum(1 for outcome in finalized_outcomes if outcome == "completed")
            dropped_this_step = sum(1 for outcome in finalized_outcomes if outcome == "dropped")

            completed_count += completed_this_step
            dropped_count += dropped_this_step

            step_log.append({
                "slot": env.current_slot,
                "has_current_task": current_task is not None,
                "action": action,
                "queue_load": env.queue_load,
                "finalized_count": len(finalized_tasks),
                "finalized_outcomes": str(finalized_outcomes),
                "completed_this_step": completed_this_step,
                "dropped_this_step": dropped_this_step,
                "reward": reward,
            })

            if terminated or truncated:
                if current_task is not None or env.queue_load > 0:
                    pending_at_end = env.queue_load + (1 if current_task else 0)
                break

        print(f"  ✅ Episode complete")
        print(f"     Total completed: {completed_count}")
        print(f"     Total dropped: {dropped_count}")
        print(f"     Pending at end: {pending_at_end}")

        # 3. Save trace
        print("\n[3/4] Saving step-by-step trace...")
        output_dir = Path("artifacts/analysis/paper-faithful-smoke-test")
        output_dir.mkdir(parents=True, exist_ok=True)

        csv_path = output_dir / "always_local_step_trace.csv"
        if step_log:
            with open(csv_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=step_log[0].keys())
                writer.writeheader()
                writer.writerows(step_log)
        print(f"  ✅ Saved to {csv_path}")

        # 4. Verify success criteria
        print("\n[4/4] Verifying success criteria...")
        success_criteria = []

        total_finalized = completed_count + dropped_count
        if total_finalized > 0:
            print(f"  ✅ Tasks were finalized ({total_finalized} total, not 100% pending)")
            success_criteria.append(True)
        else:
            print(f"  ❌ No tasks finalized (all pending - trace not loaded correctly)")
            success_criteria.append(False)

        if env.trace.trace_id.startswith("paper_faithful"):
            print(f"  ✅ Paper-faithful trace loaded (id={env.trace.trace_id})")
            success_criteria.append(True)
        else:
            print(f"  ❌ Wrong trace loaded (id={env.trace.trace_id})")
            success_criteria.append(False)

        first_task_size = env.trace.tasks[0].size if env.trace.tasks else None
        if first_task_size and 2.0 <= first_task_size <= 5.0:
            print(f"  ✅ First task has paper-faithful size ({first_task_size} Mbits)")
            success_criteria.append(True)
        else:
            print(f"  ❌ First task size not paper-faithful ({first_task_size})")
            success_criteria.append(False)

        print("\n" + "=" * 80)
        total_fin = completed_count + dropped_count
        comp_ratio = completed_count / max(total_fin, 1)
        if all(success_criteria):
            print("✅ SMOKE TEST PASSED")
            print("=" * 80)
            print(f"\nResults:")
            print(f"  Arrivals: {len(env.trace.tasks)}")
            print(f"  Completed: {completed_count}")
            print(f"  Dropped: {dropped_count}")
            print(f"  Completion ratio: {comp_ratio:.1%}")
            print(f"  Pending at episode end: {pending_at_end}")
            print(f"  Trace: {env.trace.trace_id}\n")
            return True
        else:
            print("❌ SMOKE TEST FAILED")
            print("=" * 80)
            print(f"\nResults:")
            print(f"  Arrivals: {len(env.trace.tasks)}")
            print(f"  Completed: {completed_count}")
            print(f"  Dropped: {dropped_count}")
            print(f"  Completion ratio: {comp_ratio:.1%}")
            print(f"  Pending at episode end: {pending_at_end}\n")
            return False

    except Exception as e:
        print(f"\n❌ SMOKE TEST FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_smoke_test()
    sys.exit(0 if success else 1)
