# Phase 1 Full-Campaign Readiness Plan

## Objective
Prepare safe, reproducible full-campaign execution for paper-faithful HOODIE baseline.

## Why Needed
- Bounded 3×50 runs prove mechanics only
- Figure reproduction requires meaningful time series and non-zero task completion metrics

## Scope
- Phase 1 only
- HOODIE baseline only
- No Phase 2/DCQ-MADRL

## Required Readiness Checks
- Config sanity
- Runtime budget
- Artifact directory structure
- Random seed capture
- Memory/time guardrails
- No runtime artifacts committed

## Proposed Outputs
- Campaign JSON/CSV
- Metrics summary Markdown
- Figure-ready data tables
- Config snapshot

## Candidate Validation Before Actual Full Run
- Medium bounded run, e.g., 3 episodes × 200 or 500 slots
- Completion-positive diagnostic
- Ensure completed_task_count > 0 or explain why not

## Full-Campaign Execution Gate
- Only after explicit approval
- No automatic full training

## Risks
- Long runtime
- Unstable or zero-heavy metrics
- Memory/replay growth
- Mismatch with paper figures if environment assumptions differ

## Non-Goals
- Do not run full campaign
- Do not generate figures
- Do not tune hyperparameters
- Do not start Phase 2

## Recommended Next Implementation After This Plan
* Completion-positive diagnostic runner