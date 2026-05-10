# Tasks: Baseline Fairness Rebuild

**Input**: Design documents from `/specs/021-baseline-fairness-rebuild/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md  
**Tests**: Required. This feature is a diagnostic fairness rebuild and must be driven by tests before implementation.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Lock down branch hygiene and forbidden-path guardrails before any rebuild code is written.

- [ ] T001 Add the branch hygiene and scope-guard integration test in `tests/integration/test_baseline_fairness_rebuild_scope_guard.py` to reject changes to `src/environment`, `src/policies`, `src/training`, `src/metrics`, dependency files, lockfiles, existing campaign artifacts, plots, and policy behavior

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Prove the source gates and baseline matrix inputs are valid before implementation begins.

- [ ] T002 [US1] Add source-gate validation tests in `tests/unit/test_baseline_fairness_rebuild.py` for the committed Feature 018 differential audit artifact, Feature 019 mechanism repair summary, and Feature 020 controlled mechanistic sweeps artifact
- [ ] T003 [US1] Add baseline inclusion tests in `tests/unit/test_baseline_fairness_rebuild.py` to confirm the rebuild includes all existing baseline policies supported by the current baseline evaluation framework
- [ ] T004 [US1] Add shared-environment and fairness-control tests in `tests/unit/test_baseline_fairness_rebuild.py` to confirm all baselines use identical workload, topology, deadline, reward, and metric settings
- [ ] T005 [US1] Add collapse-signature classification tests in `tests/unit/test_baseline_fairness_rebuild.py` for `collapse_reduced`, `collapse_unchanged`, `collapse_worsened`, and `inconclusive`
- [ ] T006 [US2] Add persistent-collapse interpretation tests in `tests/unit/test_baseline_fairness_rebuild.py` to ensure persistent collapse is not automatically classified as a bug
- [ ] T007 [US2] Add report schema tests in `tests/unit/test_baseline_fairness_rebuild.py` for metadata, source gate status, included policies, scenarios/traces, fairness controls, reused metrics, collapse indicators, anti-collapse assessment, unchanged-collapse explanation, limitations, reproducibility, and overall status
- [ ] T008 [US2] Add no-training, no-policy-redesign, and no-paper-validity disclaimer tests in `tests/unit/test_baseline_fairness_rebuild.py`

**Checkpoint**: Gate validation, baseline inclusion, fairness controls, and collapse classification are covered before implementation begins.

---

## Phase 3: User Story 1 - Baseline Fairness Matrix Rebuild (Priority: P1) 🎯 MVP

**Goal**: Rerun a small fairness matrix using existing baselines only and summarize whether collapse is reduced, unchanged, worsened, or inconclusive.

**Independent Test**: The tiny rebuild runs deterministically from the same inputs and produces the same collapse classification on repeated runs.

### Implementation for User Story 1

- [ ] T009 [US1] Create the isolated rebuild package scaffold in `src/analysis/baseline_fairness_rebuild/__init__.py`
- [ ] T010 [US1] Implement the source-gate loader and validation helpers in `src/analysis/baseline_fairness_rebuild/gates.py`
- [ ] T011 [US1] Implement the collapse classification helpers in `src/analysis/baseline_fairness_rebuild/classify.py`
- [ ] T012 [US1] Implement the tiny deterministic baseline rebuild runner in `src/analysis/baseline_fairness_rebuild/runner.py`
- [ ] T013 [US1] Implement the deterministic JSON and Markdown report writer in `src/analysis/baseline_fairness_rebuild/report.py`
- [ ] T014 [US1] Add the optional deterministic CSV summary writer in `src/analysis/baseline_fairness_rebuild/report.py` only if it is already conventional and deterministic for this analysis class

### Validation for User Story 1

- [ ] T015 [US1] Add the integration test in `tests/integration/test_baseline_fairness_rebuild_flow.py` that runs the tiny deterministic rebuild and writes the JSON and Markdown artifacts to a temporary path
- [ ] T016 [US1] Add the final diff and scope audit in `tests/integration/test_baseline_fairness_rebuild_final_diff.py` to verify no forbidden source paths, dependency files, campaign artifacts, plots, or simulator changes are introduced
- [ ] T017 [US1] Add the quick validation guidance in `specs/021-baseline-fairness-rebuild/quickstart.md` with the exact approved interpreter and artifact paths

**Checkpoint**: The rebuild runs deterministically, uses the existing baseline framework read-only, and stays within diagnostic-only scope.

---

## Phase 4: User Story 2 - Conservative Collapse Interpretation (Priority: P2)

**Goal**: Ensure the report clearly states that persistent collapse may be a mechanism property and not automatically a bug.

**Independent Test**: The generated report contains the required disclaimers and keeps persistent collapse as a valid, non-forced outcome.

### Implementation for User Story 2

- [ ] T018 [US2] Document the report framing and limitation language in `specs/021-baseline-fairness-rebuild/research.md` so the feature remains diagnostic-only and does not claim paper-validity

**Checkpoint**: The report and documentation clearly state the feature is diagnostic only, not a policy redesign or training feature.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1**: No dependencies. Establish the scope guard first.
- **Phase 2**: Depends on Phase 1. Gate validation and fairness semantics must exist before implementation.
- **Phase 3**: Depends on Phase 2. The rebuild can start only after the tiny baseline definitions and collapse tests are in place.
- **Phase 4**: Depends on Phase 3. The conservative framing is validated after the rebuild workflow exists.

### Task Dependencies

- `T001` must complete before any implementation work begins.
- `T002`, `T003`, `T004`, `T005`, `T006`, `T007`, and `T008` must be written before `T009`.
- `T009` must complete before `T010`, `T011`, `T012`, `T013`, and `T014`.
- `T013` must complete before `T015` and `T016`.
- `T017` must complete before final planning/signoff.
- `T018` must complete before final signoff.

### Within the User Story

- Tests first, then the isolated analysis/rebuild package implementation.
- Deterministic report writing follows the runner and classification logic.
- Documentation and final diff audit happen after the core rebuild workflow exists.

## Parallel Opportunities

- None are marked here to avoid fake parallelism. The task list is intentionally serialized around the single diagnostic workflow.

## Implementation Strategy

### MVP First

1. Complete `T001` to lock the scope guard and branch hygiene.
2. Complete `T002`-`T008` so the source gates, baseline set, fairness controls, and collapse semantics are covered before implementation.
3. Complete `T009`-`T013` to build the isolated rebuild workflow.
4. Complete `T014`-`T018` to validate output, scope, and conservative diagnostic framing.

### Incremental Delivery

1. Add the gate and classification tests first.
2. Implement the baseline rebuild runner and report writer second.
3. Verify the output artifacts third.
4. Tighten the report language and scope guard last.

## Notes

- The feature is diagnostic analysis only.
- No baseline campaign-scale reproduction is allowed.
- No plots are introduced.
- No simulator or environment behavior changes are allowed.
- No policy redesign or training foundation work is permitted.
- No paper-level validity claim is permitted.

## Acceptance Mapping

- `CHK026` is satisfied by `T002`, `T003`, and `T004` because they validate the prior credibility artifacts and fairness controls before running the rebuild.
- `CHK027` is satisfied by `T005`, `T007`, `T013`, and `T018` because they classify collapse conservatively without forcing universal improvement.
- `CHK028` is satisfied by `T006` and `T007` because they preserve persistent collapse as a valid non-bug outcome.
- `CHK029` is satisfied by `T008` and `T018` because they prohibit policy redesign and require disclaimers that exclude redesign claims.
- `CHK030` is satisfied by `T008`, `T009`, `T012`, and `T017` because they keep the rebuild out of training foundation work and limit it to baseline evaluation.
