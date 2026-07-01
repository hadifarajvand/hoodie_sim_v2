from __future__ import annotations

import json
import math
from pathlib import Path

from src.analysis.full_training_reproduction_campaign.trainer import DDQNTrainer
from src.analysis.full_training_reproduction_campaign.config import CampaignConfig
from src.analysis.full_training_reproduction_campaign.replay import (
    legal_action_mask_to_tuple,
    ACTION_INDEX_TO_SEMANTICS_PAPER,
    SEMANTICS_TO_ACTION_INDEX_PAPER,
)
from src.evaluation.trace_protocol import build_deterministic_trace


def _compute_build_deterministic_trace_stats():
    traces = [build_deterministic_trace(f"check-{s}", s, 200) for s in range(3)]
    stats: dict[str, float] = {}
    all_sizes: list[float] = []
    all_densities: list[float] = []
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

    def test_trace_param_size_paper_aligned(self):
        """Size should be 2.0-5.0 after repair."""
        s = _compute_build_deterministic_trace_stats()
        assert s["min_size"] >= 2.0, f"min_size={s['min_size']} should be >= 2.0"
        assert s["max_size"] <= 5.0, f"max_size={s['max_size']} should be <= 5.0"

    def test_trace_param_density_paper_aligned(self):
        """Processing density should be 0.297 after repair."""
        s = _compute_build_deterministic_trace_stats()
        assert s["min_density"] == 0.297, f"min_density={s['min_density']} should be 0.297"
        assert s["max_density"] == 0.297, f"max_density={s['max_density']} should be 0.297"

    def test_trace_param_timeout_paper_aligned(self):
        """Timeout should be 20 after repair."""
        s = _compute_build_deterministic_trace_stats()
        assert s["min_timeout"] == 20, f"min_timeout={s['min_timeout']} should be 20"
        assert s["max_timeout"] == 20, f"max_timeout={s['max_timeout']} should be 20"

    def test_trace_param_cycles_paper_aligned(self):
        """Cycles required should be 0.594-1.485 after repair."""
        s = _compute_build_deterministic_trace_stats()
        assert s["min_cycles"] >= 0.594, f"min_cycles={s['min_cycles']} should be >= 0.594"
        assert s["max_cycles"] <= 1.485, f"max_cycles={s['max_cycles']} should be <= 1.485"

    def test_trace_agent_distribution(self):
        """Agents should cover full 1-20 range after repair."""
        s = _compute_build_deterministic_trace_stats()
        assert s["unique_agents"] >= 20, f"unique_agents={s['unique_agents']} should be 20"

    def test_trace_deadline_paper_aligned(self):
        """Deadline delta should be 19 (phi-1=20-1) after repair."""
        s = _compute_build_deterministic_trace_stats()
        assert s["min_deadline_delta"] == 19, f"min_deadline_delta={s['min_deadline_delta']} should be 19"
        assert s["max_deadline_delta"] == 19, f"max_deadline_delta={s['max_deadline_delta']} should be 19"

    def test_paper_default_trainer_produces_completions(self):
        """After repair, trainer should produce at least one completed task."""
        config = CampaignConfig.paper_default()
        trainer = DDQNTrainer(config)
        result = trainer._episode_rollout(
            episode_id=0,
            seed=config.seed_bundle.training_trace_generation_seed,
            episode_length=200,
            training=True,
        )
        assert result["transition_count"] > 0, "should generate at least one transition"
        assert result["completed_task_count"] > 0, (
            f"expected > 0 completed, got {result['completed_task_count']} "
            f"(trace repair makes tasks structurally feasible)"
        )
        assert result["illegal_action_count"] == 0, (
            f"expected 0 illegal actions, got {result['illegal_action_count']}"
        )

    def test_legal_mask_mapping_22_action(self):
        """legal_action_mask_to_tuple with action_count=22 must not return all-False for valid mask."""
        mask_6key = {
            "local": True, "compute_local": True,
            "horizontal": True, "offload_horizontal": True,
            "vertical": True, "offload_vertical": True,
        }
        result = legal_action_mask_to_tuple(mask_6key, action_count=22)
        assert len(result) == 22, f"expected 22, got {len(result)}"
        assert result[0] is True, "local should be legal"
        assert result[21] is True, "cloud should be legal"
        assert any(result[1:21]), "at least one horizontal should be legal"
        assert not all(v is False for v in result), "should NOT be all-False"

    def test_legal_mask_local_only(self):
        """When only local is legal, only index 0 is True."""
        mask_local_only = {"local": True}
        result = legal_action_mask_to_tuple(mask_local_only, action_count=22)
        assert result[0] is True, "local should be legal"
        assert all(v is False for v in result[1:]), "non-local should be illegal"

    def test_legal_mask_3_action_backward_compat(self):
        """3-action path preserves backward compatibility."""
        mask = {"local": True, "horizontal": True, "vertical": True}
        result = legal_action_mask_to_tuple(mask, action_count=3)
        assert result == (True, True, True), f"expected (True, True, True), got {result}"

        mask2 = {"local": True, "horizontal": False, "vertical": False}
        result2 = legal_action_mask_to_tuple(mask2, action_count=3)
        assert result2 == (True, False, False), f"expected (True, False, False), got {result2}"

    def test_paper_action_semantics_convertible(self):
        """Paper action semantics can round-trip through semantics_to_action_index."""
        for sem, idx in SEMANTICS_TO_ACTION_INDEX_PAPER.items():
            from src.analysis.full_training_reproduction_campaign.replay import semantics_to_action_index as stai
            recovered = stai(sem)
            assert recovered == idx, f"semantics '{sem}' → {recovered}, expected {idx}"

    def test_paper_default_trace_produces_completions_bounded(self):
        """3x200 episodes with paper_default should produce completions after repair."""
        config = CampaignConfig.paper_default()
        trainer = DDQNTrainer(config)
        episodes = 3
        total_completed = 0
        total_dropped = 0
        total_transitions = 0
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
        assert total_completed > 0, (
            f"expected > 0 completed across {episodes} episodes, got {total_completed} "
            f"(dropped={total_dropped})"
        )
