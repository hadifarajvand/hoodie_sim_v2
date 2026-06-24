#!/usr/bin/env python3
"""
Validation script for paper-faithful HOODIE profile.

Fails loudly if any parameter deviates from paper Table 4 specification.
Use before running any paper-reproduction experiments.

Exit codes:
  0 = All checks passed (profile is paper-faithful)
  1 = At least one check failed (profile deviates from paper)
"""

import sys
import json
from pathlib import Path

from src.analysis.paper_faithful_profile.config import (
    build_paper_faithful_profile,
    PAPER_FAITHFUL_PROFILE_NAME,
    PAPER_N_EA,
    PAPER_T,
    PAPER_TASK_SIZE_MBITS_MIN,
    PAPER_TASK_SIZE_MBITS_MAX,
    PAPER_TASK_SIZE_MBITS_STEP,
    PAPER_PROCESSING_DENSITY_GCYCLES_PER_MBIT,
    PAPER_HORIZONTAL_LINK_RATE_MBPS,
    PAPER_VERTICAL_LINK_RATE_MBPS,
    PAPER_SLOT_DURATION_SECONDS,
    PAPER_TIMEOUT_SLOTS,
    PAPER_ARRIVAL_PROBABILITY,
    PAPER_DROP_PENALTY_C,
    PAPER_CPU_PRIVATE_GCYCLES_PER_SLOT,
    PAPER_CPU_PUBLIC_GCYCLES_PER_SLOT,
    PAPER_CPU_CLOUD_GCYCLES_PER_SLOT,
    PAPER_LEARNING_RATE,
    PAPER_GAMMA,
    PAPER_BATCH_SIZE,
    PAPER_REPLAY_MEMORY,
    PAPER_EPSILON_START,
    PAPER_EPSILON_END,
    PAPER_EPSILON_DECAY_EPISODES,
    PAPER_TARGET_UPDATE_FREQUENCY,
)
from src.environment.traffic_config import TrafficConfig
from src.environment.traffic_generator import TrafficGenerator


def validate_config() -> tuple[bool, list[str]]:
    """Validate paper-faithful configuration.

    Returns:
        (all_passed, error_messages)
    """
    errors = []

    # Build config (will raise if any field deviates from paper)
    try:
        cfg = build_paper_faithful_profile()
    except ValueError as e:
        errors.append(f"Config validation failed: {e}")
        return False, errors

    # Check all 24 paper parameters
    checks = [
        ("profile_name", cfg.profile_name, PAPER_FAITHFUL_PROFILE_NAME),
        ("num_agents", cfg.num_agents, PAPER_N_EA),
        ("episode_length", cfg.episode_length, PAPER_T),
        ("task_size_mbits_min", cfg.task_size_mbits_min, PAPER_TASK_SIZE_MBITS_MIN),
        ("task_size_mbits_max", cfg.task_size_mbits_max, PAPER_TASK_SIZE_MBITS_MAX),
        ("task_size_mbits_step", cfg.task_size_mbits_step, PAPER_TASK_SIZE_MBITS_STEP),
        ("processing_density", cfg.processing_density_gcycles_per_mbit, PAPER_PROCESSING_DENSITY_GCYCLES_PER_MBIT),
        ("horizontal_link_rate", cfg.horizontal_link_rate_mbps, PAPER_HORIZONTAL_LINK_RATE_MBPS),
        ("vertical_link_rate", cfg.vertical_link_rate_mbps, PAPER_VERTICAL_LINK_RATE_MBPS),
        ("slot_duration", cfg.slot_duration_seconds, PAPER_SLOT_DURATION_SECONDS),
        ("timeout_slots", cfg.timeout_slots, PAPER_TIMEOUT_SLOTS),
        ("arrival_probability", cfg.arrival_probability, PAPER_ARRIVAL_PROBABILITY),
        ("drop_penalty_c", cfg.drop_penalty_c, PAPER_DROP_PENALTY_C),
        ("cpu_private_gcycles_per_slot", cfg.cpu_private_gcycles_per_slot, PAPER_CPU_PRIVATE_GCYCLES_PER_SLOT),
        ("cpu_public_gcycles_per_slot", cfg.cpu_public_gcycles_per_slot, PAPER_CPU_PUBLIC_GCYCLES_PER_SLOT),
        ("cpu_cloud_gcycles_per_slot", cfg.cpu_cloud_gcycles_per_slot, PAPER_CPU_CLOUD_GCYCLES_PER_SLOT),
        ("learning_rate", cfg.learning_rate, PAPER_LEARNING_RATE),
        ("gamma", cfg.gamma, PAPER_GAMMA),
        ("batch_size", cfg.batch_size, PAPER_BATCH_SIZE),
        ("replay_memory", cfg.replay_memory, PAPER_REPLAY_MEMORY),
        ("epsilon_start", cfg.epsilon_start, PAPER_EPSILON_START),
        ("epsilon_end", cfg.epsilon_end, PAPER_EPSILON_END),
        ("epsilon_decay_episodes", cfg.epsilon_decay_episodes, PAPER_EPSILON_DECAY_EPISODES),
        ("target_update_frequency", cfg.target_update_frequency, PAPER_TARGET_UPDATE_FREQUENCY),
    ]

    for param_name, actual, expected in checks:
        if isinstance(actual, float):
            if abs(actual - expected) > 1e-6:
                errors.append(f"❌ {param_name}: {actual} != {expected}")
            else:
                print(f"✅ {param_name}: {actual}")
        else:
            if actual != expected:
                errors.append(f"❌ {param_name}: {actual} != {expected}")
            else:
                print(f"✅ {param_name}: {actual}")

    return len(errors) == 0, errors


def validate_trace_generation() -> tuple[bool, list[str]]:
    """Validate that traces can be generated with paper parameters."""
    errors = []

    cfg = build_paper_faithful_profile()
    traffic_config = TrafficConfig(
        scenario_name="paper_default",
        number_of_agents=cfg.num_agents,
        episode_length=cfg.episode_length,
        arrival_probability=cfg.arrival_probability,
        slot_duration_seconds=cfg.slot_duration_seconds,
        timeout_slots=cfg.timeout_slots,
        task_size_mbits_min=cfg.task_size_mbits_min,
        task_size_mbits_max=cfg.task_size_mbits_max,
        task_size_mbits_step=cfg.task_size_mbits_step,
        processing_density_gcycles_per_mbit=cfg.processing_density_gcycles_per_mbit,
    )

    try:
        trace = TrafficGenerator.generate(traffic_config, seed=42)
        print(f"✅ Trace generation: {len(trace.records)} tasks generated")

        # Verify task sizes are in paper range
        task_sizes = [t.size for t in trace.records]
        min_size = min(task_sizes) if task_sizes else 0
        max_size = max(task_sizes) if task_sizes else 0

        if task_sizes:
            if min_size < cfg.task_size_mbits_min - 0.01:
                errors.append(f"❌ Task size too small: {min_size} < {cfg.task_size_mbits_min}")
            elif max_size > cfg.task_size_mbits_max + 0.01:
                errors.append(f"❌ Task size too large: {max_size} > {cfg.task_size_mbits_max}")
            else:
                print(f"✅ Task size range: [{min_size:.2f}, {max_size:.2f}] within [{cfg.task_size_mbits_min}, {cfg.task_size_mbits_max}]")

        # Verify processing densities
        densities = [t.processing_density for t in trace.records]
        if densities:
            density_set = set(densities)
            if len(density_set) == 1 and abs(list(density_set)[0] - cfg.processing_density_gcycles_per_mbit) < 1e-6:
                print(f"✅ Processing density: {list(density_set)[0]}")
            elif all(abs(d - cfg.processing_density_gcycles_per_mbit) < 1e-6 for d in densities):
                print(f"✅ Processing density: uniform at {cfg.processing_density_gcycles_per_mbit}")
            else:
                errors.append(f"❌ Processing density mismatch: expected {cfg.processing_density_gcycles_per_mbit}")

    except Exception as e:
        errors.append(f"❌ Trace generation failed: {e}")

    return len(errors) == 0, errors


def validate_generated_task_samples() -> tuple[bool, list[str]]:
    """Generate and validate sample task parameters."""
    errors = []
    cfg = build_paper_faithful_profile()

    # Generate expected task sizes
    expected_sizes = []
    current = cfg.task_size_mbits_min
    while current <= cfg.task_size_mbits_max + 1e-6:
        expected_sizes.append(round(current, 10))
        current += cfg.task_size_mbits_step

    print(f"\n✅ Expected task sizes ({len(expected_sizes)} total):")
    print(f"   Range: [{expected_sizes[0]}, {expected_sizes[-1]}] Mbits")
    print(f"   Step: {cfg.task_size_mbits_step}")
    print(f"   Count: {len(expected_sizes)}")

    # Verify step size
    if abs(cfg.task_size_mbits_step - 0.1) > 1e-6:
        errors.append(f"❌ Task size step {cfg.task_size_mbits_step} != 0.1")
    else:
        print(f"✅ Task size step: 0.1 (correct)")

    return len(errors) == 0, errors


def main() -> int:
    """Run all validations."""
    print("\n" + "="*80)
    print("PAPER-FAITHFUL PROFILE VALIDATION")
    print("="*80 + "\n")

    print("[1/3] Validating configuration parameters...")
    config_ok, config_errors = validate_config()

    print("\n[2/3] Validating trace generation...")
    trace_ok, trace_errors = validate_trace_generation()

    print("\n[3/3] Validating task parameter samples...")
    sample_ok, sample_errors = validate_generated_task_samples()

    all_errors = config_errors + trace_errors + sample_errors

    print("\n" + "="*80)
    if not all_errors:
        print("✅ ALL CHECKS PASSED")
        print("Paper-faithful profile is valid for reproduction.")
        print("="*80 + "\n")
        return 0
    else:
        print("❌ VALIDATION FAILED")
        print("\nErrors:")
        for error in all_errors:
            print(f"  {error}")
        print("="*80 + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
