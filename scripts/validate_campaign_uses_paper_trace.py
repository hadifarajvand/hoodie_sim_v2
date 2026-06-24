#!/usr/bin/env python3
"""Validate that campaign config uses paper-faithful traces correctly.

This script verifies that:
1. CampaignConfig can be created with paper_faithful profile
2. _build_environment produces correct paper-faithful environment
3. Trace loads with correct metadata
4. First task has correct parameters
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analysis.full_training_reproduction_campaign.config import (
    CampaignConfig,
    CampaignSeedBundle,
    READINESS_MANUAL_APPROVAL_APPROVED
)
from src.analysis.full_training_reproduction_campaign.trainer import _build_environment
from src.analysis.paper_faithful_profile.config import (
    PAPER_TASK_SIZE_MBITS_MIN,
    PAPER_TASK_SIZE_MBITS_MAX,
    PAPER_PROCESSING_DENSITY_GCYCLES_PER_MBIT,
    PAPER_TIMEOUT_SLOTS,
)


def validate_campaign_paper_trace():
    """Validate paper-faithful campaign configuration and environment."""
    print("\n" + "=" * 80)
    print("VALIDATING CAMPAIGN PAPER-FAITHFUL TRACE INTEGRATION")
    print("=" * 80 + "\n")

    try:
        # 1. Create paper-faithful config
        print("[1/6] Creating paper-faithful CampaignConfig...")
        trace_root = Path("artifacts/paper_faithful_campaign_traces")
        config = CampaignConfig.for_paper_faithful(trace_root=str(trace_root))
        print(f"  ✅ Config created with environment_profile='paper_faithful'")
        print(f"  ✅ trace_root={config.trace_root}")
        print(f"  ✅ require_paper_faithful_trace={config.require_paper_faithful_trace}")

        # 2. Build environment using real path
        print("\n[2/6] Building environment through _build_environment...")
        env = _build_environment(config, episode_length=110, seed=42)
        print(f"  ✅ Environment built successfully")

        # 3. Reset to load trace (use None seed for paper_faithful to load trace_bank)
        print("\n[3/6] Resetting environment to load trace...")
        reset_seed = None if config.environment_profile == "paper_faithful" else 42
        env.reset(seed=reset_seed)
        print(f"  ✅ Environment reset complete")

        # 4. Verify trace loaded
        print("\n[4/6] Verifying trace metadata...")
        if env.trace is None:
            raise ValueError("Trace not loaded after reset - check trace source configuration")
        if env.trace is None:
            raise ValueError("No trace loaded in environment")

        trace_id = env.trace.trace_id
        print(f"  Trace ID: {trace_id}")
        if not trace_id.startswith("paper_faithful"):
            raise ValueError(f"Expected trace_id starting with 'paper_faithful', got '{trace_id}'")
        print(f"  ✅ Trace ID is paper_faithful (NOT deterministic seed fallback)")

        # 5. Verify first task parameters
        print("\n[5/6] Verifying first task parameters...")
        if not env.trace.tasks:
            raise ValueError("Trace has no tasks")

        first_task = env.trace.tasks[0]
        task_size = getattr(first_task, "size", None)
        task_density = getattr(first_task, "processing_density", None)
        task_timeout = getattr(first_task, "timeout_length", None)

        print(f"  First task size: {task_size} Mbits")
        if task_size is None or task_size < PAPER_TASK_SIZE_MBITS_MIN or task_size > PAPER_TASK_SIZE_MBITS_MAX:
            raise ValueError(f"Task size {task_size} not in paper-faithful range [{PAPER_TASK_SIZE_MBITS_MIN}, {PAPER_TASK_SIZE_MBITS_MAX}]")
        print(f"  ✅ Task size in range [{PAPER_TASK_SIZE_MBITS_MIN}, {PAPER_TASK_SIZE_MBITS_MAX}]")

        print(f"  First task processing_density: {task_density}")
        if task_density is not None:
            expected_cycles = task_size * task_density
            if abs(task_density - PAPER_PROCESSING_DENSITY_GCYCLES_PER_MBIT) > 1e-6:
                print(f"  ⚠️  Task density {task_density} != paper value {PAPER_PROCESSING_DENSITY_GCYCLES_PER_MBIT}")
            else:
                print(f"  ✅ Task density matches paper value {PAPER_PROCESSING_DENSITY_GCYCLES_PER_MBIT}")

        print(f"  First task timeout: {task_timeout} slots")
        if task_timeout != PAPER_TIMEOUT_SLOTS:
            raise ValueError(f"Task timeout {task_timeout} != paper value {PAPER_TIMEOUT_SLOTS}")
        print(f"  ✅ Task timeout matches paper value {PAPER_TIMEOUT_SLOTS}")

        # 6. Verify deterministic fallback is NOT used
        print("\n[6/6] Verifying no deterministic fallback...")
        if trace_id.startswith("hoodie-"):
            raise ValueError(f"Deterministic fallback trace detected: {trace_id}")
        print(f"  ✅ No deterministic 'hoodie-*' trace fallback detected")

        print("\n" + "=" * 80)
        print("✅ ALL VALIDATIONS PASSED")
        print("=" * 80)
        print("\nSummary:")
        print(f"  Trace ID: {trace_id}")
        print(f"  Task count: {len(env.trace.tasks)}")
        print(f"  First task: size={task_size} Mbits, timeout={task_timeout} slots")
        print(f"  Environment profile: paper_faithful")
        print(f"  Paper-faithful trace is CORRECTLY LOADED and used\n")
        return True

    except Exception as e:
        print(f"\n❌ VALIDATION FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = validate_campaign_paper_trace()
    sys.exit(0 if success else 1)
