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
