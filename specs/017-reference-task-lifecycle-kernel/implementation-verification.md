# Implementation Verification: Reference Task Lifecycle Kernel

Feature: 017-reference-task-lifecycle-kernel
Date: 2026-05-29
Branch: 017-reference-task-lifecycle-kernel
Status: pending final Codex implementation report

## Purpose

This note defines the evidence required before Feature 017 is treated as complete. The feature is a reference-only task lifecycle oracle for single-task cases. It is not a simulator repair and it is not a paper reproduction claim.

## Required checks

- Verify exact local-compute ledger ordering.
- Verify exact horizontal-offload ledger ordering.
- Verify exact vertical-offload ledger ordering.
- Verify timeout and drop ledger ordering.
- Verify reward emission happens only after a terminal event.
- Verify repeated runs with identical inputs produce identical ledgers.
- Verify same-slot or tie ordering is deterministic.
- Verify unsupported actions fail explicitly.
- Verify the reference package remains isolated from runtime, policy, training, metric, campaign, artifact, and dependency code.

## Required command

Run the targeted unit and integration tests for the reference lifecycle kernel. If the approved local interpreter is unavailable in the execution environment, record the exact replacement interpreter.

## Final implementation report

The final report must list files changed, commands run, test results, isolation-audit result, and unresolved risks.

## Current evidence

Pending final implementation report.
