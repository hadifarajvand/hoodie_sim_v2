# Implementation Plan: Baseline Revalidation After Runtime Repair

**Branch**: `037-baseline-revalidation` | **Date**: 2026-05-13 | **Spec**: [/Users/hadi/Documents/GitHub/hoodie_sim_v2/specs/037-baseline-revalidation-after-runtime-repair/spec.md](/Users/hadi/Documents/GitHub/hoodie_sim_v2/specs/037-baseline-revalidation-after-runtime-repair/spec.md)
**Input**: Feature specification from `/specs/037-baseline-revalidation-after-runtime-repair/spec.md`

## Summary

Revalidate the existing baseline policies through the repaired `HoodieGymEnvironment` path after Features 032–036, using deterministic seeds, the shared legal-action mask, and a report that records sanity results without claiming paper reproduction or curve matching.

## Technical Context

**Language/Version**: Python 3.x via `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python`  
**Primary Dependencies**: Standard library plus existing repository modules for environment, policies, registries, and evaluation  
**Storage**: File-based reports and validation artifacts under `artifacts/analysis/baseline-revalidation-after-runtime-repair/` and optional `artifacts/evaluation/baseline-revalidation-after-runtime-repair/`  
**Testing**: `unittest` via the approved interpreter  
**Target Platform**: Local repository execution in the approved development environment  
**Project Type**: Simulator / baseline evaluation pipeline  
**Performance Goals**: Keep the revalidation deterministic and bounded; prefer a minimal smoke matrix if an existing runner already supports it for CI-cost control  
**Constraints**: No dependency changes, no training, no neural-network work, no Gymnasium/ns-3/ns-3-gym/TorchRL work, no policy redesign, no runtime-contract mutation, no topology changes, no CPU-capacity changes, no transmission-delay changes, no capacity-sharing changes, no timeout/deadline changes, no reward-equation changes, no curve fitting, no paper reproduction claim, no paper registry rewriting  
**Scale/Scope**: Seven existing baseline policies, seeded revalidation runs, shared environment interface, metrics schema validation, and a baseline sanity report

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

No constitution violations require justification. The feature is limited to baseline sanity revalidation using approved runtime contracts and existing environment interfaces.

## Project Structure

### Documentation (this feature)

```text
specs/037-baseline-revalidation-after-runtime-repair/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md
```

### Source Code (repository root)

```text
src/
├── analysis/baseline_revalidation_after_runtime_repair/
├── environment/
│   ├── gym_adapter.py
│   ├── runtime_model.py
│   ├── deadline_rules.py
│   ├── traffic_config.py
│   └── ...
├── policies/
└── evaluation/

tests/
├── unit/
└── integration/
```

**Structure Decision**: Reuse the existing simulator, baseline policies, and evaluation layers. Add a baseline revalidation analysis package under `src/analysis/baseline_revalidation_after_runtime_repair/` and keep all runtime interaction on the shared `HoodieGymEnvironment` path.

## Complexity Tracking

No constitution violations require a complexity justification.

## Phase 0: Research

### Research Questions

1. Which existing policy registry and scenario/matrix runner entry points can revalidate the seven baseline policies without introducing a separate ad hoc loop?
2. What is the minimal set of deterministic seeds that keeps the revalidation auditable while avoiding unnecessary runtime cost?
3. Which baseline result fields are already stable in the evaluation schema, and which additional runtime-contract markers should be recorded for Feature 037?
4. Does the current infrastructure already support a reduced smoke scenario, and if so, how should the report label it to avoid any paper-scale reproduction implication?

### Research Outcome

See [`research.md`](./research.md) for the decisions, rationale, and alternatives.

## Phase 1: Design & Contracts

**Prerequisite:** `research.md` complete

1. Extract the baseline policy entities, run metadata, and report fields into [`data-model.md`](./data-model.md).
2. Define any feature-local report contract under [`contracts/`](./contracts/) only if the existing evaluation schema needs a stable shape document; otherwise keep the feature internal and skip contracts.
3. Write [`quickstart.md`](./quickstart.md) with the approved interpreter, deterministic seed set, and revalidation/report validation command.
4. Update `AGENTS.md` to point the spec-kit reference at this feature plan.

## Constitution Re-check

Re-check after Phase 1 design:

- No dependency drift
- No environment drift
- No assumptions beyond the approved runtime repair context
- No baseline fairness drift
- No reward timing change
- No runtime-contract mutation from Features 032–036
- No paper reproduction claim
- No artifact schema drift beyond baseline revalidation metadata

## Definition of Done

- [x] Spec matched by plan
- [ ] Research resolved
- [ ] Data model documented
- [ ] Revalidation/report contract documented
- [ ] Quickstart documented
- [ ] Agent context updated
- [ ] Scope guard preserved
- [ ] No runtime contract drift from Features 032–036
