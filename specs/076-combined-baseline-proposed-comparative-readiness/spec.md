# Feature Specification: Combined Baseline + Proposed Comparative Readiness

**Feature Branch**: `076-combined-baseline-proposed-comparative-readiness`  
**Created**: 2026-05-31  
**Status**: Implementation ready; Feature 077 Spec Kit merged into this branch

## Goal

Create a read-only comparative readiness layer that combines Feature 074 baseline action-bound comparison rows with Feature 075 proposed-method action-bound readiness rows into a single normalized 7-by-7 matrix.

This feature is for readiness only. It must not rank methods, claim superiority, claim final evaluation, or claim full HOODIE reproduction.

## Dependency Chain

Feature 076 depends on:

- Feature 074 `074-baseline-policy-comparative-evaluation-readiness`
- Feature 075 `075-proposed-integration-readiness`

Feature 076 must consume their report objects and normalize their rows. It must not recompute baseline policy logic or proposed-method scoring.

## Required Coverage

Required policy/method identifiers:

- `FLC`
- `VO`
- `HO`
- `RO`
- `BCO`
- `MLEO`
- `PROPOSED_DCQ`

Required scenario identifiers:

- `light_load_no_deadline_pressure`
- `tight_deadline_pressure`
- `legal_horizontal_offload`
- `illegal_horizontal_destination_attempt`
- `cloud_vertical_fallback`
- `timeout_drop_case`
- `mixed_local_horizontal_cloud_candidates`

The combined matrix must contain 49 action-bound rows.

## Required Output

The combined report must include:

- normalized combined rows
- aggregate rows per policy/method
- upstream regression evidence for Features 068R through 075
- explicit claim boundaries
- explicit scope evidence

## Claim Boundary

Feature 076 may claim readiness only. It must not claim:

- training
- superiority
- final evaluation
- statistical significance
- full paper reproduction

## Out of Scope

- training
- DRL implementation
- baseline policy rewrites
- proposed-method rewrites
- runtime helper rewrites
- generated artifacts committed to git
- dependency changes
- lock-file changes
- Feature 078+ files

## Acceptance Criteria

- report status is `combined_baseline_proposed_comparative_readiness_ready`
- report `passed=True`
- all 49 rows are present
- all 7 aggregates are present
- every row is action-bound
- compatibility mode is not used
- every row has decision trace evidence
- scope validator passes
- Feature 077 Spec Kit is present under `specs/077-experimental-campaign-readiness/`
- no PR is required for branch-to-branch integration
- no implementation code is added by Feature 077