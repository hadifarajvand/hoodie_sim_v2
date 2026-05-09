# Implementation Plan: Paper Mechanism Registry

**Branch**: `016-paper-mechanism-registry` | **Date**: 2026-05-09 | **Spec**: [`spec.md`](./spec.md)
**Input**: Feature specification from `/specs/016-paper-mechanism-registry/spec.md`

## Summary

Build a deterministic, read-only registry that maps the HOODIE paper's mechanism claims to OCR evidence, paper references, implementation status, missing details, and assumption risk. The registry reads `resources/papers/hoodie/ocr/merged.tex` as the authoritative source of paper evidence, may consult sibling OCR artifacts and existing analysis outputs as secondary context, and writes `paper-mechanism-registry.json` and `paper-mechanism-registry.md` to a caller-provided analysis output directory without mutating source artifacts or changing runtime behavior.

## Technical Context

**Language/Version**: Python 3.x  
**Primary Dependencies**: Python standard library only  
**Storage**: Filesystem inputs and caller-provided analysis output directory  
**Testing**: `python -m unittest` through `src/.venvmac/bin/python`  
**Target Platform**: Local development and CI in the existing repository environment  
**Project Type**: analysis tooling / library helper  
**Performance Goals**: Deterministically scan one OCR source plus optional supporting artifacts with bounded serial reads  
**Constraints**: No new dependencies, no simulator reruns, no artifact mutation, no policy changes, no metric formula changes, no lifecycle changes, no training, DRL, TorchRL, LSTM, neural-network, or agent changes  
**Scale/Scope**: HOODIE paper mechanism registry for 25 required mechanism categories plus optional secondary evidence inputs

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

No constitution violations require justification for this feature.

## Project Structure

### Documentation (this feature)

```text
specs/016-paper-mechanism-registry/
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
└── analysis/
    └── paper_mechanism_registry.py

tests/
├── integration/
│   └── test_paper_mechanism_registry_flow.py
└── unit/
    └── test_paper_mechanism_registry.py
```

**Structure Decision**: Keep the registry under `src/analysis/` because it is a read-only extraction layer that consumes paper OCR and committed analysis artifacts, then emits deterministic registry reports into a caller-provided output directory.

## Phase 0: Research Plan

### Unknowns to Resolve

- The exact paper terminology used for mechanism categories, especially where OCR text uses multiple synonyms for the same concept.
- Whether any supporting OCR siblings add trustworthy context beyond the authoritative OCR file.
- How to represent mechanism paper status when the paper is explicit on behavior but ambiguous on units or exact mappings.
- Which project module paths can be mapped confidently without overstating implementation coverage.

### Research Outputs

- `research.md` will document decisions for OCR precedence, evidence extraction, risk classification, and secondary artifact use.
- The research will resolve ambiguous terminology by preference ordering rather than by inventing unsupported mechanism detail.

## Phase 1: Design Plan

### Data Model Outputs

- `data-model.md` will define `MechanismEntry`, `MechanismEvidence`, `MechanismRegistryReport`, and `ProjectMapping` fields and validation rules.

### Contracts

- `contracts/paper-mechanism-registry.md` will describe the registry output contract for downstream readers and reviewers.

### Quickstart

- `quickstart.md` will show how to run the registry builder against the committed OCR source and inspect the generated JSON and Markdown outputs.

### Agent Context Update

- `AGENTS.md` does not require a new plan reference update because the repo root marker already points to the active 016 plan.

## Constitution Re-Check

No new violations are introduced by the design above. The feature remains analysis-only, deterministic, and read-only.

## Complexity Tracking

No constitution violations require special justification.
