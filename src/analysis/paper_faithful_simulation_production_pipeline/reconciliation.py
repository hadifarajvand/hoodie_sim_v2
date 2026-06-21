"""Horizon-aware reward/terminal reconciliation (Repair A).

Root cause of the Feature 072 reconciliation failure
----------------------------------------------------
The environment emits a ``reward_emitted`` trace event co-located with each
``task_completed`` / ``task_dropped`` terminal event (see
``src/environment/gym_adapter.py`` ``_record_outcome``). Tasks that are instead
*force-finalized at the episode horizon* are delivered to the evaluator via
``info["finalized_tasks"]`` and carry a ``terminal_outcome`` of ``completed`` or
``dropped`` but NO ``reward_emitted`` event, because the environment does not
emit a reward for a task it had to truncate at the horizon boundary.

The legacy canonical reconstruction (feature 067 ``repaired_terminal_evaluator``)
classifies those horizon-finalized tasks as reward-bearing and assigns them a
canonical reward (``-phi_private`` or ``-40``). The raw event stream does not
include them. Therefore::

    raw_event_reward_total  >  canonical_task_reward_total   (less negative)
    raw - canonical = + (sum of canonical reward of horizon-only tasks) > 0

The Feature 072 decision-time state injection shifted transition timing so that
~75-85 more tasks per campaign finalize exactly at the truncation boundary,
pushing the (always-present) delta above the ``1e-9`` tolerance for every policy
(observed deltas: 3000 / 3320 / 3400 ...).

Fix (analysis-only)
-------------------
A task is *canonical reward-bearing* iff the environment actually emitted a
reward for it, i.e. it has at least one ``reward_emitted`` event. Tasks that are
terminal only by horizon truncation (no reward event) are reclassified as
``reward_pending_at_horizon`` and excluded from the canonical reward/terminal
counts, so the canonical universe matches the environment's emitted-reward
universe. No reward value, policy, or environment semantic is changed.
"""

from __future__ import annotations

from typing import Any

REWARD_RECONCILIATION_TOLERANCE = 1e-9


def reward_bearing_task(record: dict[str, Any]) -> bool:
    """Return True iff the environment emitted a reward for this task.

    Authority is the raw ``reward_emitted`` evidence, not the reconstructed
    lifecycle outcome. This is what makes raw and canonical reconcile.
    """

    if int(record.get("raw_reward_event_count", 0)) > 0:
        return True
    # Some traces carry an explicit reward-availability flag from env.step.
    return bool(record.get("reward_available_from_step", False))


def horizon_aware_reconciliation(
    task_records: dict[str, Any],
    *,
    raw_event_reward_total: float | None = None,
    raw_reward_event_count: int | None = None,
    tolerance: float = REWARD_RECONCILIATION_TOLERANCE,
) -> dict[str, Any]:
    """Reconcile raw env-emitted reward against canonical per-task reward.

    Only tasks with an actual ``reward_emitted`` event contribute to the
    canonical reward/terminal universe. Horizon-truncated terminal tasks are
    counted separately as ``reward_pending_at_horizon``.
    """

    canonical_reward_total = 0.0
    canonical_reward_count = 0
    canonical_terminal_count = 0
    horizon_pending_count = 0
    completed_count = 0
    dropped_count = 0
    derived_raw_total = 0.0
    derived_raw_count = 0

    for record in task_records.values():
        derived_raw_total += float(record.get("raw_reward_total", 0.0))
        derived_raw_count += int(record.get("raw_reward_event_count", 0))
        outcome = str(record.get("terminal_outcome") or "unknown")
        if outcome not in {"completed", "dropped"}:
            continue
        if reward_bearing_task(record):
            canonical_terminal_count += 1
            canonical_reward_count += 1
            canonical_reward_total += float(record.get("canonical_reward", 0.0))
            if outcome == "completed":
                completed_count += 1
            else:
                dropped_count += 1
        else:
            # Terminal only via horizon truncation: env emitted no reward.
            horizon_pending_count += 1

    raw_total = float(raw_event_reward_total if raw_event_reward_total is not None else derived_raw_total)
    raw_count = int(raw_reward_event_count if raw_reward_event_count is not None else derived_raw_count)
    delta = raw_total - canonical_reward_total
    reward_reconciled = abs(delta) <= tolerance
    terminal_reconciled = raw_count == canonical_terminal_count

    return {
        "raw_event_reward_total": raw_total,
        "raw_reward_event_count": raw_count,
        "canonical_task_reward_total": canonical_reward_total,
        "canonical_reward_event_count": canonical_reward_count,
        "canonical_terminal_task_count": canonical_terminal_count,
        "completed_count": completed_count,
        "dropped_count": dropped_count,
        "reward_pending_at_horizon_count": horizon_pending_count,
        "raw_vs_canonical_reward_delta": delta,
        "reward_reconciled": reward_reconciled,
        "terminal_reconciled": terminal_reconciled,
        "reward_reconciliation_tolerance": tolerance,
        "terminal_event_coverage_ratio": (
            float(raw_count) / canonical_terminal_count if canonical_terminal_count else 0.0
        ),
    }
