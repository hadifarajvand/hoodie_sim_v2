# Feature Specification: Reward Emission and Evaluation Metric Aggregation Repair

**Feature Branch**: `066-reward-emission-evaluation-metric-aggregation-repair`
**Created**: 2026-06-20
**Status**: Spec Kit created; implementation in progress

## Dependency

Feature 066 depends on the validated Feature 065 diagnostic branch `065-evaluation-instrumentation-reward-state-diagnostic`.

Feature 065 established that canonical task-level rewards were recoverable, but raw evaluation reward events needed a repair to reconcile event-level evidence with canonical task metrics.

## Goal

Repair the evaluation aggregation path so raw reward events, terminal events, and canonical task-level rewards reconcile from real evaluation stepping evidence.

Feature 066 answers this question:

Can the repository recover raw evaluation reward events from `env.step()` evidence and reconcile them with canonical task outcomes without changing reward semantics?

## Required Behaviors

- Recover raw reward events from evaluation stepping evidence.
- Attach terminal events and reward events to task identity.
- Reconcile raw event reward totals against canonical task rewards.
- Preserve staged budgets `[100, 150, 200, 500]`.
- Preserve reward semantics, environment semantics, policy semantics, DAL behavior, and replay behavior.

## Out of Scope

- 5000-episode training.
- Reward redesign.
- Environment redesign.
- Policy redesign.
- Replay redesign.
- Baseline superiority claims.
- Paper reproduction claims.

## Claim Boundary

Feature 066 may claim reward emission and evaluation metric aggregation repair readiness only. It must not claim superiority or full reproduction.
