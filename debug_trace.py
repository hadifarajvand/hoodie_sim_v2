#!/usr/bin/env python3
"""
Quick test to see what data is available from the trace collector and trainer.
"""

import sys
sys.path.insert(0, '/Users/hadi/Documents/GitHub/hoodie_sim_v2')

from src.analysis.full_training_reproduction_campaign.trainer import DDQNTrainer
from src.analysis.full_training_reproduction_campaign.config import CampaignConfig
from src.analysis.trace_collector import TraceCollector, make_enabled_trace_collector

def test_data_availability():
    config = CampaignConfig.paper_default()
    trace_collector = make_enabled_trace_collector()
    trainer = DDQNTrainer(config, trace_collector=trace_collector)
    
    # Run a tiny episode to see what we get
    summary = trainer._episode_rollout(
        episode_id=0,
        seed=config.seed_bundle.training_trace_generation_seed,
        episode_length=10,  # Very short for testing
        training=True,
    )
    
    print("=== Trainer Episode Summary ===")
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    print("\n=== Trace Collector Events ===")
    # Get all recorded events
    events = []
    for episode_id in trace_collector._storage.keys():
        for event in trace_collector._storage[episode_id]:
            events.append((episode_id, event))
    
    print(f"Total events recorded: {len(events)}")
    if events:
        print("Sample events:")
        for episode_id, event in events[:5]:  # First 5 events
            print(f"  Episode {episode_id}: {event}")
    
    # Check what's in finalized_tasks and lifecycle_trace_events from info
    # We'd need to modify the trainer to expose these, or access via trace
    
    # Let's see what the trace collector actually stores by event type
    event_types = {}
    for episode_id, event in events:
        etype = getattr(event, 'event_type', 'unknown')
        event_types[etype] = event_types.get(etype, 0) + 1
    
    print("\n=== Event Types ===")
    for etype, count in sorted(event_types.items()):
        print(f"  {etype}: {count}")

if __name__ == "__main__":
    test_data_availability()