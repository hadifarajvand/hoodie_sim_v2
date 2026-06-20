# Feature Specification: Terminal Lifecycle Accounting and 50/100 Comparison Repair

**Feature Branch**: `067-terminal-lifecycle-accounting-50-100-comparison`
**Created**: 2026-06-20
**Status**: Spec Kit created; implementation in progress

## Dependency

Feature 067 depends on the validated Feature 066 diagnostic branch and its reward reconciliation output.

## Goal

Separate lifecycle-only events from terminal-outcome events so canonical terminal task accounting is not inflated by duplicate lifecycle records, then compare the 50 and 100 episode checkpoints under the same staged training flow.

## Required Behaviors

- Train cumulatively to 50 and then 100 episodes.
- Evaluate both checkpoints on the same evaluation setup.
- Count terminal-outcome events once per task.
- Classify lifecycle-only events separately from terminal-outcome events.
- Compare 50 vs 100 on action distribution, terminal ratios, reward, and latency.

## Out of Scope

- 150/200/500 episode campaigns.
- 1000/2000/5000 episode campaigns.
- Reward redesign.
- Environment redesign.
- Policy redesign.

## Claim Boundary

Feature 067 may claim terminal lifecycle accounting repair readiness only. It must not claim superiority or paper reproduction.
