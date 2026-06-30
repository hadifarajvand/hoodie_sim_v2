from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
from statistics import mean
from typing import Any, Dict, Tuple

from src.analysis.full_training_reproduction_campaign.config import CampaignConfig
from src.analysis.full_training_reproduction_campaign.trainer import DDQNTrainer
from src.analysis.trace_collector import TraceCollector, make_enabled_trace_collector


def _config_hash(config: CampaignConfig) -> str:
    payload = json.dumps(config.to_dict(), sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def run_task_arrival_completion_timing_audit(
    episodes: int = 3,
    episode_length: int = 200,
    *,
    trace_collector: TraceCollector | None = None,
) -> Dict[str, Any]:
    config = CampaignConfig.paper_default()
    tracer = trace_collector or make_enabled_trace_collector()
    trainer = DDQNTrainer(config, trace_collector=tracer)
    config_hash = _config_hash(config)

    episode_summaries: list[dict[str, Any]] = []
    all_loss_values: list[float] = []
    total_transition_count = 0
    total_completed = 0
    total_dropped = 0
    total_pending_at_horizon = 0
    total_reward = 0.0
    reward_count = 0
    illegal_action_count = 0

    for ep_idx in range(episodes):
        summary = trainer._episode_rollout(
            episode_id=ep_idx,
            seed=config.seed_bundle.training_trace_generation_seed + ep_idx,
            episode_length=episode_length,
            training=True,
        )
        episode_summaries.append(summary)
        all_loss_values.extend(summary["loss_values"])
        total_transition_count += summary["transition_count"]
        total_completed += summary["completed_task_count"]
        total_dropped += summary["dropped_task_count"]
        total_pending_at_horizon += summary["pending_at_horizon_count"]
        illegal_action_count += summary["illegal_action_count"]

    # Read-only inspection of replay buffer transitions
    transitions = trainer.replay_buffer.as_list()

    arrival_slots: list[int] = []
    completion_or_drop_slots: list[int | None] = []
    terminal_reasons: list[str | None] = []
    action_indices: list[int] = []
    rewards_per_transition: list[float] = []
    per_episode_arrivals: list[list[int]] = [[] for _ in range(episodes)]
    per_episode_terminal_reasons: list[list[str | None]] = [[] for _ in range(episodes)]
    per_episode_actions: list[list[int]] = [[] for _ in range(episodes)]

    for t in transitions:
        if hasattr(t, "arrival_slot") and t.arrival_slot is not None:
            arrival_slots.append(t.arrival_slot)
            ep_id = t.episode_id if hasattr(t, "episode_id") else 0
            if 0 <= ep_id < episodes:
                per_episode_arrivals[ep_id].append(t.arrival_slot)
        if hasattr(t, "completion_or_drop_slot"):
            completion_or_drop_slots.append(t.completion_or_drop_slot)
        if hasattr(t, "terminal_reason"):
            terminal_reasons.append(t.terminal_reason)
            ep_id = t.episode_id if hasattr(t, "episode_id") else 0
            if 0 <= ep_id < episodes:
                per_episode_terminal_reasons[ep_id].append(t.terminal_reason)
        if hasattr(t, "action") and t.action is not None:
            action_indices.append(int(t.action))
            ep_id = t.episode_id if hasattr(t, "episode_id") else 0
            if 0 <= ep_id < episodes:
                per_episode_actions[ep_id].append(int(t.action))
        if t.reward_available:
            total_reward += float(t.reward)
            reward_count += 1

    loss_finite = all(math.isfinite(v) for v in all_loss_values) if all_loss_values else True
    no_nan = not any(math.isnan(v) for v in all_loss_values) if all_loss_values else True
    no_inf = not any(math.isinf(v) for v in all_loss_values) if all_loss_values else True
    legal_only = illegal_action_count == 0
    episodes_completed = len(episode_summaries)

    avg_reward = total_reward / reward_count if reward_count > 0 else 0.0

    # Build observability matrix
    has_arrival_slot = len(arrival_slots) > 0
    has_completion_or_drop_slot = any(s is not None for s in completion_or_drop_slots)
    has_terminal_reason = any(r is not None for r in terminal_reasons)
    has_action_idx = len(action_indices) > 0
    has_reward_events = reward_count > 0

    first_arrival_per_ep = [
        min(per_episode_arrivals[i]) if per_episode_arrivals[i] else None
        for i in range(episodes)
    ]

    firstcompletion_per_ep = []
    for i in range(episodes):
        comp_slots = []
        for j in range(len(per_episode_terminal_reasons[i])):
            reason = per_episode_terminal_reasons[i][j]
            if reason == "completed":
                if j < len(completion_or_drop_slots):
                    comp_slot = completion_or_drop_slots[j]
                    if comp_slot is not None:
                        comp_slots.append(comp_slot)
        firstcompletion_per_ep.append(min(comp_slots) if comp_slots else None)

    # Extract trace event counts if tracing was enabled
    trace_event_counts: dict[str, int] = {}
    first_service_start_slot: int | None = None
    queue_length_samples: list[dict[str, Any]] = []
    lifecycle_event_counts: dict[str, int] = {}
    service_started_observable = False
    lifecycle_events_absent = False
    
    if tracer is not None and tracer.enabled:
        trace_event_counts = tracer.count_events_by_type()
        # Check for service_started or execution_started events
        events = tracer.get_events()
        for event in events:
            event_type = event.get("event_type", "")
            if event_type in ["service_started", "execution_started"]:
                service_started_observable = True
                if first_service_start_slot is None or event["slot"] < first_service_start_slot:
                    first_service_start_slot = event["slot"]
            # Count lifecycle events by their source type
            if "lifecycle_event_source" in event:
                source_type = event["lifecycle_event_source"]
                lifecycle_event_counts[source_type] = lifecycle_event_counts.get(source_type, 0) + 1
            else:
                # Also count by event_type for non-lifecycle events
                if event_type:
                    lifecycle_event_counts[event_type] = lifecycle_event_counts.get(event_type, 0) + 1
        # Collect queue length samples
        for event in events:
            if event["event_type"] == "queue_length_sampled":
                queue_length_samples.append({
                    "episode_id": event["episode_id"],
                    "slot": event["slot"],
                    "ea_id": event.get("ea_id"),
                    "queue_length": event.get("queue_length"),
                })
        
        # Check if lifecycle events are absent even when trace is enabled
        has_lifecycle_events = any("lifecycle_event_source" in e for e in events)
        lifecycle_events_absent = not has_lifecycle_events and len(events) > 0

    observability_matrix = {
        "first_arrival_slot": {
            "observable": has_arrival_slot,
            "value": first_arrival_per_ep if has_arrival_slot else "not_observable_without_instrumenting_trainer",
        },
        "first_service_start_slot": {
            "observable": service_started_observable,
            "value": first_service_start_slot if service_started_observable else "not_observable_without_deeper_environment_instrumentation",
        },
        "first_completion_slot": {
            "observable": has_completion_or_drop_slot,
            "value": firstcompletion_per_ep if has_completion_or_drop_slot else "not_observable_without_instrumenting_trainer",
        },
        "action_distribution": {
            "observable": has_action_idx,
            "value": dict() if not has_action_idx else None,
        },
        "queue_lengths": {
            "observable": len(queue_length_samples) > 0,
            "value": f"{len(queue_length_samples)} samples recorded" if queue_length_samples else "not_observable_without_deeper_environment_instrumentation",
        },
        "reward_events": {
            "observable": has_reward_events,
            "value": {
                "count": reward_count,
                "total": total_reward,
                "average": avg_reward,
            },
        },
        "service_started_observable": {
            "observable": service_started_observable,
            "value": service_started_observable,
        },
    }

    # Compute action distribution
    if has_action_idx:
        action_counts: dict[int, int] = {}
        for a in action_indices:
            action_counts[a] = action_counts.get(a, 0) + 1
        observability_matrix["action_distribution"]["value"] = action_counts

    # Compute terminal_reason distribution
    terminal_reason_counts: dict[str, int] = {}
    for r in terminal_reasons:
        key = r if r is not None else "none"
        terminal_reason_counts[key] = terminal_reason_counts.get(key, 0) + 1

    # Compute arrival slot statistics
    arrival_stats = {}
    if arrival_slots:
        arrival_stats = {
            "min": min(arrival_slots),
            "max": max(arrival_slots),
            "mean": mean(arrival_slots),
            "count": len(arrival_slots),
        }

    # Inferred findings
    proven = []
    not_observable = []
    if not service_started_observable:
        not_observable.append("first_service_start_slot")
    if len(queue_length_samples) == 0:
        not_observable.append("queue_lengths_over_time")

    if has_arrival_slot and arrival_slots:
        proven.append(f"Task arrivals occur as early as slot {min(arrival_slots)} (mean {mean(arrival_slots):.1f})")
    if total_completed == 0 and total_dropped > 0:
        proven.append(f"{total_dropped} tasks were dropped but 0 completed — tasks arrive but cannot finish within {episode_length} slots")
    if total_completed == 0 and total_pending_at_horizon > 0:
        proven.append(f"{total_pending_at_horizon} tasks were pending at horizon — episode truncation prevents completion accounting")
    if has_reward_events and total_reward < 0:
        proven.append(f"All rewards are negative (total={total_reward:.1f}, avg={avg_reward:.2f}) — drop penalties dominate, no completion rewards")

    most_likely_hypothesis = ""
    if total_completed == 0 and total_dropped > 0 and has_arrival_slot and arrival_slots:
        service_time_or_horizon = (
            f"Tasks arrive (first at slot {min(arrival_slots)}) but are dropped (n={total_dropped}) "
            f"or pending (n={total_pending_at_horizon}) before completing. "
            f"Most likely: the bounded horizon of {episode_length} slots is too short for the "
            f"service time of tasks given the current action selection policy, OR the action "
            f"selection is not advancing task processing effectively."
        )
        most_likely_hypothesis = service_time_or_horizon
    elif total_completed == 0 and total_dropped == 0:
        most_likely_hypothesis = (
            f"No tasks were either completed or dropped in {episode_length} slots. "
            f"Tasks may still be in processing/pending at episode end."
        )

    # Verdict
    if total_completed == 0 and (has_arrival_slot or total_dropped > 0):
        verdict = "audit_needs_deeper_instrumentation"
        recommended_next_step = "minimal trainer instrumentation plan"
    elif total_completed > 0:
        verdict = "audit_explains_zero_completion"
        recommended_next_step = "bounded horizon extension plan"
    else:
        verdict = "audit_needs_deeper_instrumentation"
        recommended_next_step = "minimal trainer instrumentation plan"

    report: dict[str, Any] = {
        "diagnostic_type": "task_arrival_completion_timing_audit",
        "bounded_constraint": f"{episodes} episodes x {episode_length} slots",
        "config_summary": {
            "state_dim": config.state_dim,
            "action_count": config.action_count,
            "lookback_w": config.lookback_w,
            "learning_rate": config.learning_rate,
            "gamma": config.gamma,
            "batch_size": config.batch_size,
            "horizontal_data_rate_mbps": config.horizontal_data_rate_mbps,
            "vertical_data_rate_mbps": config.vertical_data_rate_mbps,
            "full_campaign_enabled": config.full_campaign_enabled,
            "config_hash": config_hash[:16],
        },
        "trace_info": {
            "trace_collector_enabled": tracer is not None and tracer.enabled,
            "trace_event_counts": trace_event_counts,
            "lifecycle_event_counts": lifecycle_event_counts,
            "first_service_start_slot": first_service_start_slot,
            "queue_length_samples": len(queue_length_samples),
            "service_started_observable": service_started_observable,
            "lifecycle_events_absent_even_when_trace_enabled": lifecycle_events_absent,
        },
        "observability_matrix": observability_matrix,
        "episode_summaries": [
            {
                "episode_id": i,
                "transition_count": s["transition_count"],
                "completed_task_count": s["completed_task_count"],
                "dropped_task_count": s["dropped_task_count"],
                "pending_at_horizon_count": s["pending_at_horizon_count"],
                "illegal_action_count": s["illegal_action_count"],
                "loss_count": len(s["loss_values"]),
            }
            for i, s in enumerate(episode_summaries)
        ],
        "metrics": {
            "episodes_completed": episodes_completed,
            "episode_length": episode_length,
            "total_transition_count": total_transition_count,
            "completed_task_count": total_completed,
            "dropped_task_count": total_dropped,
            "pending_at_horizon_count": total_pending_at_horizon,
            "illegal_action_count": illegal_action_count,
            "legal_action_only": legal_only,
            "reward_count": reward_count,
            "average_reward": avg_reward,
            "loss_count": len(all_loss_values),
            "loss_summary": {
                "all_finite": loss_finite,
                "no_nan": no_nan,
                "no_inf": no_inf,
            },
            "replay_size": len(transitions),
        },
        "inferred_findings": {
            "what_is_proven": proven,
            "what_is_not_observable": not_observable,
            "arrival_slot_statistics": arrival_stats,
            "terminal_reason_distribution": terminal_reason_counts,
            "most_likely_next_hypothesis": most_likely_hypothesis,
        },
        "verdict": verdict,
        "recommended_next_step": recommended_next_step,
    }

    return report


def write_artifacts(report: dict[str, Any]) -> tuple[Path, Path]:
    OUTPUT_DIR = Path(os.getenv("AUDIT_OUTPUT_DIR", "artifacts/analysis/task-arrival-completion-timing-audit"))
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUTPUT_DIR / "task-arrival-completion-timing-audit.json"
    md_path = OUTPUT_DIR / "task-arrival-completion-timing-audit.md"

    json_path.write_text(
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    m = report["metrics"]
    cfg = report["config_summary"]
    obs = report["observability_matrix"]
    findings = report["inferred_findings"]
    trace_info = report.get("trace_info", {})

    lines = [
        "# Task-Arrival Completion Timing Audit Evidence",
        "",
        f"- **Verdict**: `{report['verdict']}`",
        f"- **Constraint**: {report['bounded_constraint']}",
        "",
        "## Config Confirmation",
        "",
        f"- state_dim: `{cfg['state_dim']}`",
        f"- action_count: `{cfg['action_count']}`",
        f"- lookback_w: `{cfg['lookback_w']}`",
        f"- full_campaign_enabled: `{cfg['full_campaign_enabled']}`",
        f"- config_hash: `{cfg['config_hash']}`... (sha256 prefix)",
        "",
        "## Trace Info",
        "",
        f"- trace_collector_enabled: `{trace_info.get('trace_collector_enabled', False)}`",
        f"- trace_event_counts: `{trace_info.get('trace_event_counts', {})}`",
        f"- lifecycle_event_counts: `{trace_info.get('lifecycle_event_counts', {})}`",
        f"- first_service_start_slot: `{trace_info.get('first_service_start_slot', 'N/A')}`",
        f"- queue_length_samples: `{trace_info.get('queue_length_samples', 0)}`",
        f"- service_started_observable: `{trace_info.get('service_started_observable', False)}`",
        f"- lifecycle_events_absent_even_when_trace_enabled: `{trace_info.get('lifecycle_events_absent_even_when_trace_enabled', False)}`",
        "",
        "## Observability Matrix",
        "",
    ]
    for key, val in obs.items():
        observable = val.get("observable", False)
        lines.append(f"- {key}: `{'observable' if observable else 'NOT observable'}`")
    lines.append("")

    lines.extend([
        "## Metrics Summary",
        "",
        f"- episodes_completed: `{m['episodes_completed']}`",
 f"- episode_length: `{m['episode_length']}`",
        f"- total_transition_count: `{m['total_transition_count']}`",
        f"- completed_task_count: `{m['completed_task_count']}`",
        f"- dropped_task_count: `{m['dropped_task_count']}`",
        f"- pending_at_horizon_count: `{m['pending_at_horizon_count']}`",
        f"- illegal_action_count: `{m['illegal_action_count']}`",
        f"- legal_action_only: `{m['legal_action_only']}`",
        f"- reward_count: `{m['reward_count']}`",
        f"- average_reward: `{m['average_reward']:.6f}`",
        f"- loss_count: `{m['loss_count']}`",
        f"- replay_size: `{m['replay_size']}`",
        "",
        "## Inferred Findings",
        "",
        "### What is proven",
        "",
    ])
    for p in findings.get("what_is_proven", []):
        lines.append(f"- {p}")
    lines.append("")
    lines.extend([
        "### What is not observable",
        "",
    ])
    for n in findings.get("what_is_not_observable", []):
        lines.append(f"- {n}")
    lines.append("")
    lines.extend([
        "### Most likely next hypothesis",
        "",
        findings.get("most_likely_next_hypothesis", "N/A"),
        "",
        "## Recommended Next Step",
        "",
        report["recommended_next_step"],
        "",
    ])

    md_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, md_path


if __name__ == "__main__":
    report = run_task_arrival_completion_timing_audit()
    json_path, md_path = write_artifacts(report)
    print(f"JSON: {json_path}")
    print(f"MD:   {md_path}")
    print(f"Verdict: {report['verdict']}")
