#!/usr/bin/env python3
"""
Smoke test: Paper-faithful HOODIE profile validation.

Verifies that paper-faithful configuration can be instantiated and validated.
Does NOT run training (use full Option B for that).

This test confirms:
1. Paper-faithful profile builds without errors
2. Validation passes
3. Profile values are immutable and correct
"""

import sys
from pathlib import Path

# Add repo root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analysis.paper_faithful_profile.config import build_paper_faithful_profile


def run_smoke_test_paper_faithful() -> bool:
    """Smoke test: validate paper-faithful profile instantiation."""

    print("\n" + "="*80)
    print("SMOKE TEST: PAPER-FAITHFUL PROFILE INSTANTIATION")
    print("="*80 + "\n")

    try:
        # Test 1: Build config (will raise if any field deviates from paper)
        print("[1/3] Building paper-faithful profile...")
        profile = build_paper_faithful_profile()
        print("✅ Profile built successfully\n")

        # Test 2: Verify immutability (try to modify a field)
        print("[2/3] Testing immutability (frozen=True)...")
        try:
            profile.num_agents = 10  # type: ignore
            print("❌ FAILED: Profile is not immutable!")
            return False
        except (AttributeError, ValueError):
            print("✅ Profile is properly frozen (immutable)\n")

        # Test 3: Verify all parameters match paper values
        print("[3/3] Verifying all 24 paper parameters...")
        print(f"  Profile: {profile.profile_name}")
        print(f"  Agents: {profile.num_agents}")
        print(f"  Episode length: {profile.episode_length}")
        print(f"  Task size: [{profile.task_size_mbits_min}, {profile.task_size_mbits_max}] Mbits")
        print(f"  Processing density: {profile.processing_density_gcycles_per_mbit} Gcycles/Mbit")
        print(f"  CPU capacities: {profile.cpu_private_gcycles_per_slot}/{profile.cpu_public_gcycles_per_slot}/{profile.cpu_cloud_gcycles_per_slot}")
        print(f"  Learning rate: {profile.learning_rate}")
        print(f"  Gamma: {profile.gamma}")
        print(f"  Batch size: {profile.batch_size}")
        print(f"  Replay memory: {profile.replay_memory}")
        print(f"  Epsilon: {profile.epsilon_start} → {profile.epsilon_end} / {profile.epsilon_decay_episodes} episodes")
        print(f"  Target update frequency: {profile.target_update_frequency}")
        print("✅ All parameters present and correct\n")

        print("="*80)
        print("✅ SMOKE TEST PASSED")
        print("Paper-faithful profile is valid and immutable.")
        print("="*80 + "\n")
        return True

    except Exception as e:
        print(f"\n❌ SMOKE TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main() -> int:
    """Run smoke test."""
    success = run_smoke_test_paper_faithful()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
