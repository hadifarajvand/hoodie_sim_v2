# Tasks: Feature 055 - Paper-Default Training Smoke Run

## Setup

- [ ] T001 Confirm the Feature 054 readiness report contract and the Feature 055 smoke report contract in the spec and plan artifacts.
- [ ] T002 Add the Feature 055 `__main__` entrypoint so `python3 -m src.analysis.paper_default_training_smoke_run` runs the analysis package directly.
- [ ] T003 Add the Feature 055 configuration surface for the one-episode, 110-step smoke scope and the Feature 056 routing target.

## Tests

- [ ] T004 Add schema tests for the required top-level Feature 055 report fields and the expected pass-path routing.
- [ ] T005 Add metrics tests for the readiness gate, live trainer usage, replay population, optimizer steps, finite loss, legal actions, checkpoint metadata, and smoke-only guardrails.
- [ ] T006 Add behavior-equivalence tests that reject duplicate named checks and verify deterministic smoke summaries across repeated runs.

## Core

- [ ] T007 Repair the Feature 055 report model so it validates the pass path, the blocked path, and the required routing rules.
- [ ] T008 Repair the Feature 055 report writer so JSON and Markdown artifacts are generated under `artifacts/analysis/paper-default-training-smoke-run/`.
- [ ] T009 Repair the Feature 055 runner so it validates the committed Feature 054 readiness report before any live trainer execution.
- [ ] T010 Repair the Feature 055 runner so it lazily imports and executes the approved live trainer path only when the Feature 054 gate is satisfied.
- [ ] T011 Repair the Feature 055 runner so it records replay, optimizer, loss, checkpoint metadata, legal-action, delayed-reward, and train/eval summaries from the live smoke run.

## Integration

- [ ] T012 Add integration coverage that the analysis package writes both required artifacts.
- [ ] T013 Add integration coverage that the smoke report routes to Feature 056 only on the full pass path.
- [ ] T014 Add integration coverage that the smoke report blocks paper reproduction, baseline comparison, and full campaign claims.

## Polish

- [ ] T015 Update the Feature 055 spec to reflect live trainer smoke execution instead of fixture-first smoke data.
- [ ] T016 Update the Feature 055 plan to match the live smoke architecture and validation scope.
- [ ] T017 Verify the implementation through the approved interpreter and record the generated reports.
