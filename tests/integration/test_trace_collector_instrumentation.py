from __future__ import annotations

from typing import Any

from src.analysis.full_training_reproduction_campaign.config import CampaignConfig
from src.analysis.full_training_reproduction_campaign.trainer import DDQNTrainer
from src.analysis.trace_collector import TraceCollector, make_disabled_trace_collector, make_enabled_trace_collector


def test_trace_collector_disabled_by_default() -> None:
    """TraceCollector is disabled by default (factory)."""
    tc = make_disabled_trace_collector()
    assert not tc.enabled, "Disabled trace collector should have enabled=False"
    tc.record(0, 0, "test_event")
    assert tc.get_events() == [], "Disabled collector should not record events"


def test_trace_collector_enabled_records() -> None:
    """TraceCollector records events when enabled."""
    tc = make_enabled_trace_collector()
    assert tc.enabled, "Enabled trace collector should have enabled=True"
    tc.record(episode_id=1, slot=2, event_type="task_arrived", task_id="t1")
    events = tc.get_events()
    assert len(events) == 1, "Should have recorded exactly one event"
    assert events[0]["episode_id"] == 1
    assert events[0]["slot"] == 2
    assert events[0]["event_type"] == "task_arrived"
    assert events[0]["task_id"] == "t1"


def test_trace_collector_clear() -> None:
    """TraceCollector clear() removes all recorded events."""
    tc = make_enabled_trace_collector()
    tc.record(0, 0, "test")
    assert len(tc.get_events()) == 1
    tc.clear()
    assert tc.get_events() == []


def test_trace_collector_count_events_by_type() -> None:
    """TraceCollector count_events_by_type returns correct counts."""
    tc = make_enabled_trace_collector()
    tc.record(0, 0, "task_arrived")
    tc.record(0, 1, "task_arrived")
    tc.record(0, 2, "action_selected")
    counts = tc.count_events_by_type()
    assert counts["task_arrived"] == 2
    assert counts["action_selected"] == 1
    assert "reward_released" not in counts


def test_tracing_disabled_preserves_existing_behavior() -> None:
    """DDQNTrainer with no trace_collector (disabled) produces same results as before."""
    config = CampaignConfig.paper_default()
    trainer = DDQNTrainer(config, trace_collector=None)
    summary = trainer._episode_rollout(
        episode_id=0,
        seed=config.seed_bundle.training_trace_generation_seed,
        episode_length=50,
        training=True,
    )
    assert "transition_count" in summary
    assert "completed_task_count" in summary
    assert "dropped_task_count" in summary
    assert "pending_at_horizon_count" in summary
    # No trace events recorded
    assert trainer.trace_collector is None


def test_tracing_enabled_produces_events() -> None:
    """DDQNTrainer with enabled TraceCollector produces trace events."""
    config = CampaignConfig.paper_default()
    tracer = make_enabled_trace_collector()
    trainer = DDQNTrainer(config, trace_collector=tracer)
    summary = trainer._episode_rollout(
        episode_id=0,
        seed=config.seed_bundle.training_trace_generation_seed,
        episode_length=50,
        training=True,
    )
    events = tracer.get_events()
    assert len(events) > 0, "Should have recorded trace events"
    event_types = [e["event_type"] for e in events]
    assert "action_selected" in event_types, "Should record action_selected"
    # task_arrived may or may not be present depending on whether task arrived
    # queue_length_sampled should always be present since we sample each step
    assert "queue_length_sampled" in event_types, "Should record queue_length_sampled"


def test_tracing_behaviour_invariant() -> None:
    """Tracing enabled does not alter episode summary metrics."""
    config = CampaignConfig.paper_default()
    # Run without tracing
    trainer_no_trace = DDQNTrainer(config, trace_collector=None)
    summary_no_trace = trainer_no_trace._episode_rollout(
        episode_id=0,
        seed=123,
        episode_length=50,
        training=True,
    )
    # Run with tracing
    tracer = make_enabled_trace_collector()
    trainer_with_trace = DDQNTrainer(config, trace_collector=tracer)
    summary_with_trace = trainer_with_trace._episode_rollout(
        episode_id=0,
        seed=123,
        episode_length=50,
        training=True,
    )
    # Metrics should be identical
    assert summary_no_trace["transition_count"] == summary_with_trace["transition_count"]
    assert summary_no_trace["completed_task_count"] == summary_with_trace["completed_task_count"]
    assert summary_no_trace["dropped_task_count"] == summary_with_trace["dropped_task_count"]
    assert summary_no_trace["pending_at_horizon_count"] == summary_with_trace["pending_at_horizon_count"]
    assert summary_no_trace["illegal_action_count"] == summary_with_trace["illegal_action_count"]


def test_trace_collector_get_events_copy() -> None:
    """get_events returns a copy, not the internal list."""
    tc = make_enabled_trace_collector()
    tc.record(0, 0, "test")
    events = tc.get_events()
    events.append({"spam": "extra"})
    assert len(tc.get_events()) == 1, "Internal list should not be modified"


def test_bridge_deduplicates_lifecycle_events_across_steps() -> None:
    """Each lifecycle trace event is bridged exactly once; snapshot is sliced to new events only."""
    config = CampaignConfig.paper_default()
    tracer = make_enabled_trace_collector()
    trainer = DDQNTrainer(config, trace_collector=tracer)

    trainer._episode_rollout(
        episode_id=0,
        seed=42,
        episode_length=200,
        training=True,
    )

    events = tracer.get_events()
    event_types = [e["event_type"] for e in events]

    # Each action_selected should appear at most once per slot
    action_selected_count = event_types.count("action_selected")
    assert action_selected_count == 200, f"Expected exactly 200 action_selected events, got {action_selected_count}"

    # Lifecycle event counts should be O(200) not O(200²)
    # Bad: task_generated=61,497 (200 * 200 + inflation)
    # Good: task_generated should be O(λ * 200) where λ ≈ 1 per slot
    task_generated = event_types.count("task_generated")
    assert task_generated < 5000, f"task_generated={task_generated} suspiciously high, check deduplication"

    # Verify no single event_type is 200× the action_selected count
    for etype, count in tracer.count_events_by_type().items():
        if count > 0:
            ratio = count / max(action_selected_count, 1)
            assert ratio < 100, f"{etype}={count} is {ratio:.1f}× action_selected count, likely duplicate bridging"


def test_bridge_execution_started_mapped_to_service_started() -> None:
    """execution_started lifecycle events are bridged as service_started with original type preserved."""
    config = CampaignConfig.paper_default()
    tracer = make_enabled_trace_collector()
    trainer = DDQNTrainer(config, trace_collector=tracer)

    trainer._episode_rollout(
        episode_id=0,
        seed=42,
        episode_length=200,
        training=True,
    )

    events = tracer.get_events()
    service_started_events = [e for e in events if e["event_type"] == "service_started"]
    execution_started_as_source = [e for e in events if e.get("lifecycle_event_source") == "execution_started"]
    raw_execution_started = [e for e in events if e["event_type"] == "execution_started"]

    # service_started should exist (mapped from execution_started)
    assert len(service_started_events) > 0, "service_started events should be bridged"
    # Original execution_started should be in lifecycle_event_source
    assert len(execution_started_as_source) > 0, "execution_started should be preserved as lifecycle_event_source"
    # Raw execution_started should NOT appear as event_type
    assert len(raw_execution_started) == 0, "Raw execution_started should be remapped to service_started"


def test_bridged_lifecycle_event_count_is_deduplicated() -> None:
    """bridged_lifecycle_event_count should be close to total events, not inflated by cumulative snapshot."""
    from src.analysis.task_arrival_completion_timing_audit import run_task_arrival_completion_timing_audit

    tracer = make_enabled_trace_collector()
    report = run_task_arrival_completion_timing_audit(episodes=3, episode_length=200, trace_collector=tracer)

    bridge = report["bridge"]
    ti = report["trace_info"]

    bridged = bridge["bridged_lifecycle_event_count"]
    total_events = sum(ti["trace_event_counts"].values())

    # bridged_lifecycle_event_count counts events WITH lifecycle_event_source
    # total_events counts ALL events (lifecycle + trainer-level)
    # bridged should be less than total but in the same order of magnitude
    assert bridged > 0, "Should have bridged lifecycle events"
    assert bridged < total_events, "Bridget event count should be less than total (trainer events add more)"

    # Before fix: ~180,894 bridged for 3×200 slots → ~201× inflation
    # After fix: ~4,811 bridged for 3×200 slots → ~5.3× ratio (reasonable)
    assert bridged < 20000, f"bridged_lifecycle_event_count={bridged} too high for 3×200 slots"


def test_completion_accounting_mismatch_detected() -> None:
    """When execution_completed events exist but completed_task_count=0, mismatch is flagged."""
    from src.analysis.task_arrival_completion_timing_audit import run_task_arrival_completion_timing_audit

    tracer = make_enabled_trace_collector()
    report = run_task_arrival_completion_timing_audit(episodes=3, episode_length=200, trace_collector=tracer)

    bridge = report["bridge"]
    metrics = report["metrics"]

    has_execution_completed = bridge["execution_completed_count"] > 0
    has_zero_completion = metrics["completed_task_count"] == 0

    if has_execution_completed and has_zero_completion:
        assert bridge["completion_accounting_mismatch"] is True, \
            "completion_accounting_mismatch should be True when execution_completed>0 but completed_task_count=0"
