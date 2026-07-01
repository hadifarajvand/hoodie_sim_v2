from __future__ import annotations

import json
import math
from pathlib import Path

from src.analysis.full_training_reproduction_campaign.trainer import DDQNTrainer
from src.analysis.full_training_reproduction_campaign.config import CampaignConfig
from src.analysis.full_training_reproduction_campaign.replay import (
    legal_action_mask_to_tuple,
    ACTION_INDEX_TO_SEMANTICS_PAPER,
)
from src.evaluation.trace_protocol import build_deterministic_trace


def _compute_build_deterministic_trace_stats():
    traces = [build_deterministic_trace(f"check-{s}", s, 200) for s in range(3)]
    stats: dict[str, float] = {}
    all_sizes: list[int] = []
    all_densities: list[int] = []
    all_timeouts: list[int] = []
    all_cycles: list[float] = []
    all_agents: set[int] = set()
    all_deadlines: list[int] = []
    for t in traces:
        for b in t.tasks:
            all_sizes.append(b.size)
            all_densities.append(b.processing_density)
            all_timeouts.append(b.timeout_length)
            all_cycles.append(b.cycles_required)
            all_agents.add(b.source_agent_id)
            all_deadlines.append(b.absolute_deadline_slot)
    stats["min_size"] = min(all_sizes)
    stats["max_size"] = max(all_sizes)
    stats["min_density"] = min(all_densities)
    stats["max_density"] = max(all_densities)
    stats["min_timeout"] = min(all_timeouts)
    stats["max_timeout"] = max(all_timeouts)
    stats["min_cycles"] = min(all_cycles)
    stats["max_cycles"] = max(all_cycles)
    stats["unique_agents"] = len(all_agents)
    deadline_deltas = [d - b.arrival_slot for b, d in zip(traces[0].tasks, all_deadlines[:200])]
    stats["min_deadline_delta"] = min(deadline_deltas)
    stats["max_deadline_delta"] = max(deadline_deltas)
    return stats


class TestZeroCompletionRootCauseDiagnostic:
    """Evidence generation: zero-completion root cause in paper_default DDQN path."""

    def test_trace_param_size_mismatch(self):
        """Size should be 2-5 but trace uses 10-100."""
        s = _compute_build_deterministic_trace_stats()
        assert s["min_size"] >= 10, f"min_size={s['min_size']} should be >= 10 (bug: trace uses wrong range)"
        assert s["max_size"] <= 100, f"max_size={s['max_size']} should be <= 100"
        assert s["min_size"] < 5 or s["max_size"] > 6, (
            f"sizes {s['min_size']}-{s['max_size']} not in paper_default range 2-5"
        )

    def test_trace_param_density_mismatch(self):
        """Processing density should be ~0.297 but trace uses 1-5."""
        s = _compute_build_deterministic_trace_stats()
        assert s["min_density"] >= 1, f"min_density={s['min_density']}"
        assert s["max_density"] <= 5, f"max_density={s['max_density']}"
        assert s["min_density"] >= 1, (
            f"density {s['min_density']}-{s['max_density']} not ~0.297 (paper_default)"
        )

    def test_trace_param_timeout_mismatch(self):
        """Timeout should be 20 but trace uses 2-5."""
        s = _compute_build_deterministic_trace_stats()
        assert s["min_timeout"] >= 2, f"min_timeout={s['min_timeout']}"
        assert s["max_timeout"] <= 5, f"max_timeout={s['max_timeout']}"
        assert s["min_timeout"] < 10, (
            f"timeout {s['min_timeout']}-{s['max_timeout']} not 20 (paper_default)"
        )

    def test_trace_param_cycles_required_too_large(self):
        """Cycles required should be 0.594-1.485 but trace produces 10-500."""
        s = _compute_build_deterministic_trace_stats()
        assert s["min_cycles"] >= 10, f"min_cycles={s['min_cycles']}"
        assert s["max_cycles"] <= 500, f"max_cycles={s['max_cycles']}"
        assert s["min_cycles"] > 2 or s["max_cycles"] > 2, (
            f"cycles {s['min_cycles']}-{s['max_cycles']} is 10-1000x paper_default expected 0.594-1.485"
        )

    def test_trace_agent_concentration(self):
        """Only 3 agents generate tasks instead of all 20."""
        s = _compute_build_deterministic_trace_stats()
        assert s["unique_agents"] <= 3, f"unique_agents={s['unique_agents']}"

    def test_trace_deadline_too_short(self):
        """Deadline delta should be 19 (phi-1) but trace uses 2-5."""
        s = _compute_build_deterministic_trace_stats()
        assert s["min_deadline_delta"] >= 2
        assert s["max_deadline_delta"] <= 5
        assert s["max_deadline_delta"] < 15, (
            f"deadline delta {s['min_deadline_delta']}-{s['max_deadline_delta']} is "
            f"not 19 (paper_default phi=20 → arrival+phi-1)"
        )

    def test_paper_default_trainer_produces_zero_completions(self):
        """Verify the zero-completion symptom is reproducible with DDQNTrainer."""
        config = CampaignConfig.paper_default()
        trainer = DDQNTrainer(config)
        result = trainer._episode_rollout(
            episode_id=0,
            seed=config.seed_bundle.training_trace_generation_seed,
            episode_length=50,
            training=True,
        )
        assert result["transition_count"] > 0, "should generate at least one transition"
        assert result["completed_task_count"] == 0, (
            f"expected 0 completed, got {result['completed_task_count']} "
            f"(trace cycle inflation prevents completion)"
        )
        assert result["illegal_action_count"] == 0, (
            f"expected 0 illegal actions (all are 'local'), got {result['illegal_action_count']}"
        )

    def test_legal_mask_mapping_allows_only_local(self):
        """legal_action_mask_to_tuple with action_count=22 always returns all-False."""
        mask_6key = {
            "local": True, "compute_local": True,
            "horizontal": True, "offload_horizontal": True,
            "vertical": True, "offload_vertical": True,
        }
        result = legal_action_mask_to_tuple(mask_6key, action_count=22)
        assert len(result) == 22, f"expected 22, got {len(result)}"
        assert all(v is False for v in result), (
            f"expected all False (missing 'legal_action_mask' key), got {result}"
        )

    def test_paper_action_map_not_in_mask(self):
        """ACTION_INDEX_TO_SEMANTICS_PAPER outputs 'horizontal_N' which is not in the 6-key mask."""
        mask_keys = {"local", "compute_local", "horizontal", "offload_horizontal", "vertical", "offload_vertical"}
        for idx, sem in ACTION_INDEX_TO_SEMANTICS_PAPER.items():
            if idx == 0:
                assert sem == "local", f"index 0 should be 'local', got '{sem}'"
            elif idx == 21:
                assert sem == "cloud", f"index 21 should be 'cloud', got '{sem}'"
                assert sem not in mask_keys, f"'{sem}' should NOT be in the 6-key mask"
            else:
                assert sem.startswith("horizontal_"), f"index {idx} should be 'horizontal_N', got '{sem}'"
                assert sem not in mask_keys, f"'{sem}' should NOT be in the 6-key mask"

    def test_paper_default_trace_produces_wrong_cycles(self):
        """A single episode with paper_default config and trace produces zero completions."""
        config = CampaignConfig.paper_default()
        trainer = DDQNTrainer(config)
        episodes = 3
        total_completed = 0
        total_dropped = 0
        total_transitions = 0
        all_actions: dict[str, int] = {}
        for ep in range(episodes):
            r = trainer._episode_rollout(
                episode_id=ep,
                seed=config.seed_bundle.training_trace_generation_seed + ep,
                episode_length=200,
                training=True,
            )
            total_completed += r["completed_task_count"]
            total_dropped += r["dropped_task_count"]
            total_transitions += r["transition_count"]
        assert total_transitions > 0, "expected > 0 transitions"
        assert total_completed == 0, (
            f"expected 0 completed across {episodes} episodes, got {total_completed} "
            f"(dropped={total_dropped})"
        )
