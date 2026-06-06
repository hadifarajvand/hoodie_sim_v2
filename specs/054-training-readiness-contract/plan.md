# Implementation Plan: Training Readiness Contract

**Branch**: `054-training-readiness-contract` | **Date**: 2026-05-25 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/054-training-readiness-contract/spec.md`

## Summary

Build a passive training-readiness contract analysis package that consumes committed JSON reports from Features 048 through 053, verifies the completed diagnostic evidence chain, evaluates the locked training-contract bundle, and emits a go/no-go decision for the next controlled paper-default training smoke run. The feature is evidence-only: it must not start training, optimizer work, replay, target updates, checkpoints, or campaigns.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Standard library analysis package plus committed prior-feature JSON reports  
**Storage**: File-based JSON and Markdown artifacts under `artifacts/analysis/training-readiness-contract/`  
**Testing**: `unittest` via the approved interpreter  
**Target Platform**: Local Linux/macOS development and CI  
**Project Type**: CLI-driven passive analysis package inside a simulator repository  
**Performance Goals**: Produce the report quickly enough for routine evidence review and gating  
**Constraints**: Contract/readiness analysis only; no training, optimizer, replay, target update, checkpoint, campaign, or policy/runtime/dependency drift  
**Scale/Scope**: Single-feature contract gate over committed Feature 048 through 053 artifacts

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Constitution Gate

- [x] Dependency impact checked
- [x] Environment impact checked
- [x] Assumption impact checked
- [x] Fidelity impact checked
- [x] Test impact checked
- [x] Reproducibility impact checked
- [x] Config/schema impact checked
- [x] Public interface impact checked
- [x] Artifact impact checked
- [x] Security/secret impact checked
- [x] Performance budget impact checked
- [x] Baseline fairness impact checked
- [x] Paper-to-code mapping impact checked
- [x] Definition-of-done impact checked

## Project Structure

### Documentation (this feature)

```text
specs/054-training-readiness-contract/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/analysis/training_readiness_contract/
├── __init__.py
├── __main__.py
├── config.py
├── model.py
├── runner.py
└── report.py

tests/
├── integration/
│   ├── test_training_readiness_contract.py
│   ├── test_training_readiness_contract_report.py
│   └── test_training_readiness_contract_scope_guard.py
└── unit/
    ├── test_training_readiness_contract_schema.py
    ├── test_training_readiness_contract_metrics.py
    └── test_training_readiness_contract_behavior_equivalence.py

artifacts/analysis/training-readiness-contract/
```

**Structure Decision**: A single passive analysis package under `src/analysis/training_readiness_contract/` that reads committed Feature 048 through 053 JSON reports and emits training-readiness reports only.

## Phase 0: Outline & Research

Research is limited to the committed prior evidence reports and the already-populated Feature 053 readiness report.

### Decisions

1. Use Feature 053 readiness as the hard prerequisite gate for the training contract.
2. Consume committed Feature 048 through 053 artifacts only; do not regenerate prior outputs.
3. Expose each contract lock as an independent top-level boolean field so the report can identify the first failing family.
4. Treat training_execution_allowed_next as a report-level decision that becomes true only when the evidence chain is ready, all contracts are locked, behavior equivalence passes, and no drift or rewrite is detected.
5. Keep the analysis passive and evidence-only so it cannot launch a smoke run or alter simulator semantics.

### Research Deliverable

`research.md` records the contract boundary decisions, the prerequisite evidence chain, and the reasons placeholder-driven or runtime-driven alternatives were rejected.

## Phase 1: Design & Contracts

**Prerequisites:** `research.md` complete

1. Extract entities and relationships into `data-model.md`.
2. Define the report contract in `contracts/`.
3. Write `quickstart.md` for report generation and validation.

### Design Focus

- Feature 053 readiness gate validation
- Paper-default configuration lock
- Observation, action, legality, reward, timeout, capacity, transmission, queue, metric, seed, and artifact contract locks
- Behavior-equivalence audit with unique check names
- Training-execution-allowed next-step routing

### Report Contract

The Feature 054 report MUST expose these top-level fields:

- `feature_053_readiness_verified`
- `evidence_chain_ready_for_training_contract`
- `paper_default_config_locked`
- `observation_contract_locked`
- `action_contract_locked`
- `legality_contract_locked`
- `reward_contract_locked`
- `timeout_contract_locked`
- `capacity_contract_locked`
- `transmission_contract_locked`
- `queue_contract_locked`
- `metric_contract_locked`
- `seed_contract_locked`
- `artifact_contract_locked`
- `behavior_equivalence_summary`
- `behavior_equivalence_passed`
- `training_execution_allowed_next`
- `remaining_blockers`
- `recommended_next_feature`
- `no_training_started`
- `no_optimizer_step`
- `no_replay_training`
- `no_target_update_execution`
- `no_checkpoint_written`
- `no_campaign_run`
- `no_policy_drift`
- `no_runtime_semantic_changes`
- `no_dependency_drift`
- `no_prior_artifact_rewrite`
- `no_paper_reproduction_claim`
- `final_verdict`

Validation scope:

- Feature 054 validation MUST use Feature 054 tests for current behavior.
- Feature 054 validation MUST use committed-artifact-only checks for prior Features 048 through 053.
- Feature 054 validation MUST avoid any prior-feature test that inspects active worktree dirtiness, active `.specify/feature.json` state, current dirty paths, or prior report regeneration cleanliness from the active worktree.
- Feature 054 validation MUST keep current hygiene rules limited to commit-scope rules such as not staging or committing `.specify/feature.json`, `AGENTS.md`, or unrelated files.

Readiness rule:

- `feature_053_readiness_verified` must be true only when Feature 053 reports `paper_mechanism_alignment_ready = true`, `final_verdict = paper_mechanism_alignment_ready_for_training_contract`, `remaining_blockers = []`, all alignment statuses are `available`, `training_readiness_contract_status = available`, and `behavior_equivalence_passed = true`.
- `evidence_chain_ready_for_training_contract` must be true only when the Feature 053 readiness gate passes and the committed prior Feature 048 through 052 inputs are present and internally consistent.
- `training_execution_allowed_next` may be true only when the Feature 053 readiness gate passes, every contract lock is true, behavior equivalence passes, no runtime/policy/dependency drift is detected, no prior artifacts are rewritten, and no training has already started.
- `behavior_equivalence_passed` MUST equal `behavior_equivalence_summary.passed`.
- Each contract lock field MUST be a boolean and the report MUST not infer a lock from placeholder values.

Validation failure conditions:

- The plan MUST fail if the Feature 053 readiness gate is false.
- The plan MUST fail if any required contract lock field is missing.
- The plan MUST fail if the report fabricates blockers, locks, or readiness states rather than deriving them from committed evidence.
- The plan MUST fail if `training_execution_allowed_next` is true while any contract is unlocked or behavior equivalence fails.
- The plan MUST fail if `remaining_blockers` is empty while training execution is not allowed next.
- The plan MUST fail if `behavior_equivalence_passed` contradicts `behavior_equivalence_summary.passed`.
- The plan MUST fail if `final_verdict` claims smoke-run readiness while `training_execution_allowed_next` is false.
- The plan MUST fail if `recommended_next_feature` routes to Feature 055 while required contract evidence is unavailable.
