# Tasks: Baseline Rebuild Sensitivity Audit

**Input**: Design documents from `/specs/022-baseline-rebuild-sensitivity-audit/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md  
**Tests**: Required. This feature is a diagnostic sensitivity audit and must be driven by tests before implementation.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Lock down branch hygiene and forbidden-path guardrails before any audit code is written.

- [X] T001 Add the branch hygiene and scope-guard integration test in `tests/integration/test_baseline_rebuild_sensitivity_audit_scope_guard.py` to reject changes to `src/environment`, `src/policies`, `src/training`, `src/metrics`, dependency files, lockfiles, existing campaign artifacts, plots, and policy behavior

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Prove the source gates, sensitivity inputs, and conservative classification rules are valid before implementation begins.

- [X] T002 [US1] Add source-gate validation tests in `tests/unit/test_baseline_rebuild_sensitivity_audit.py` for the committed Feature 018 differential audit artifact, Feature 019 mechanism repair summary, Feature 020 controlled mechanistic sweeps artifact, and Feature 021 baseline fairness rebuild artifact
- [X] T003 [US1] Add sensitivity-setting tests in `tests/unit/test_baseline_rebuild_sensitivity_audit.py` for the tiny fixed seed set `7, 11, 13`, the supported scenario set `paper_default`, `moderate`, `heavy`, and supported episode lengths `4` and `6`
- [X] T004 [US1] Add existing-baseline inclusion tests in `tests/unit/test_baseline_rebuild_sensitivity_audit.py` to confirm the audit includes all existing baseline policies supported by the current baseline evaluation framework
- [X] T005 [US1] Add shared-environment and fairness-control tests in `tests/unit/test_baseline_rebuild_sensitivity_audit.py` to confirm all baselines use identical workload, topology, deadline, reward, and metric settings within each sensitivity setting
- [X] T006 [US1] Add baseline-signature stability tests in `tests/unit/test_baseline_rebuild_sensitivity_audit.py` for compact signatures derived from completed tasks, dropped tasks, throughput, and average delay
- [X] T007 [US1] Add collapse-stability classification tests in `tests/unit/test_baseline_rebuild_sensitivity_audit.py` for `robust_collapse_reduced`, `fragile_collapse_reduced`, `collapse_unchanged`, `collapse_worsened`, and `inconclusive`
- [X] T008 [US2] Add persistent-instability interpretation tests in `tests/unit/test_baseline_rebuild_sensitivity_audit.py` to ensure fragile and inconclusive results are not automatically classified as bugs
- [X] T009 [US2] Add no-training, no-policy-redesign, no-metric-change, and no-paper-validity disclaimer tests in `tests/unit/test_baseline_rebuild_sensitivity_audit.py`
- [X] T010 [US1] Add constitution-required integration coverage in `tests/integration/test_baseline_rebuild_sensitivity_audit_flow.py` that runs the tiny deterministic audit with one existing baseline policy path through the shared/current environment interface without adding training, neural-network code, DRL, policy redesign, new baseline algorithms, or metric changes
- [X] T011 [US2] Add constitution-required integration coverage in `tests/integration/test_baseline_rebuild_sensitivity_audit_flow.py` that runs the tiny deterministic audit with one test-local learned-policy placeholder/stub through the shared/current environment interface without adding training, neural-network code, DRL, policy redesign, new baseline algorithms, metric changes, or simulator/environment mutation

**Checkpoint**: Gate validation, sensitivity settings, baseline inclusion, fairness controls, and collapse classification are covered before implementation begins.

---

## Phase 3: User Story 1 - Baseline Rebuild Sensitivity Audit (Priority: P1) 🎯 MVP

**Goal**: Rerun the Feature 021 baseline fairness rebuild under tiny controlled variations and classify whether the rebuild conclusion is robust, fragile, worsened, or inconclusive.

**Independent Test**: The tiny audit runs deterministically from the same inputs and produces the same sensitivity classification on repeated runs.

### Implementation for User Story 1

- [X] T012 [US1] Create the isolated audit package scaffold in `src/analysis/baseline_rebuild_sensitivity_audit/__init__.py`
- [X] T013 [US1] Implement the gate loader and validation helpers in `src/analysis/baseline_rebuild_sensitivity_audit/gates.py`
- [X] T014 [US1] Implement the sensitivity-setting definitions in `src/analysis/baseline_rebuild_sensitivity_audit/settings.py`
- [X] T015 [US1] Implement the collapse stability classifier in `src/analysis/baseline_rebuild_sensitivity_audit/classifier.py`
- [X] T016 [US1] Implement the tiny deterministic audit runner in `src/analysis/baseline_rebuild_sensitivity_audit/runner.py`
- [X] T017 [US1] Implement the deterministic JSON and Markdown report writer in `src/analysis/baseline_rebuild_sensitivity_audit/report.py`
- [X] T018 [US1] Add the optional deterministic CSV summary writer in `src/analysis/baseline_rebuild_sensitivity_audit/report.py` only if it is already conventional and deterministic for this analysis class

### Validation for User Story 1

- [X] T019 [US1] Add the integration test in `tests/integration/test_baseline_rebuild_sensitivity_audit_flow.py` that runs the tiny deterministic audit and writes the JSON and Markdown artifacts to a temporary path
- [X] T020 [US1] Add the final diff and scope audit in `tests/integration/test_baseline_rebuild_sensitivity_audit_final_diff.py` to verify no forbidden source paths, dependency files, campaign artifacts, plots, or simulator changes are introduced

**Checkpoint**: The audit runs deterministically, uses the Feature 021 rebuild as the reference point, and stays within diagnostic-only scope.

---

## Phase 4: User Story 2 - Conservative Sensitivity Interpretation (Priority: P2)

**Goal**: Ensure the report clearly states that instability, fragility, or unchanged collapse are valid outcomes and not proof of bug or paper-level failure.

**Independent Test**: The generated report contains the required disclaimers and keeps fragile/inconclusive results as valid, non-forced outcomes.

### Implementation for User Story 2

- [X] T021 [US2] Document the report framing and limitation language in `specs/022-baseline-rebuild-sensitivity-audit/research.md` so the feature remains diagnostic-only and does not claim paper-validity
- [X] T022 [US2] Add quick validation guidance in `specs/022-baseline-rebuild-sensitivity-audit/quickstart.md` with the exact approved interpreter and artifact paths

**Checkpoint**: The report and documentation clearly state the feature is diagnostic only, not a policy redesign or training feature.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1**: No dependencies. Establish the scope guard first.
- **Phase 2**: Depends on Phase 1. Gate validation, sensitivity semantics, and constitution-required integration coverage must exist before implementation.
- **Phase 3**: Depends on Phase 2. The audit can start only after the tiny sensitivity definitions and collapse tests are in place.
- **Phase 4**: Depends on Phase 3. The conservative framing is validated after the audit workflow exists.

### Task Dependencies

- `T001` must complete before any implementation work begins.
- `T002`, `T003`, `T004`, `T005`, `T006`, `T007`, `T008`, `T009`, `T010`, and `T011` must be written before `T012`.
- `T010` is baseline-only read-only coverage.
- `T011` is test-local learned-policy placeholder/stub coverage only and does not authorize training foundation work, DRL, neural-network code, policy redesign, or simulator/environment mutation.
- `T012` must complete before `T013`, `T014`, `T015`, `T016`, `T017`, and `T018`.
- `T017` must complete before `T019` and `T020`.
- `T021` and `T022` must complete before final signoff.

### Within the User Story

- Tests first, then the isolated analysis/audit package implementation.
- Deterministic report writing follows the runner and classification logic.
- Documentation and final diff audit happen after the core audit workflow exists.

## Parallel Opportunities

- None are marked here to avoid fake parallelism. The task list is intentionally serialized around the single diagnostic workflow.

## Implementation Strategy

### MVP First

1. Complete `T001` to lock the scope guard and branch hygiene.
2. Complete `T002`-`T011` so the source gates, baseline set, fairness controls, collapse semantics, and constitution-required integration coverage are covered before implementation.
3. Complete `T012`-`T017` to build the isolated audit workflow.
4. Complete `T018`-`T022` to validate output, scope, and conservative diagnostic framing.

### Incremental Delivery

1. Add the gate and classification tests first.
2. Implement the audit runner and report writer second.
3. Verify the output artifacts third.
4. Tighten the report language and scope guard last.

## Notes

- The feature is diagnostic analysis only.
- No campaign-scale reproduction is allowed.
- No plots are introduced.
- No simulator or environment behavior changes are allowed.
- No policy redesign, new baseline algorithms, or training foundation work is permitted.
- No paper-level validity claim is permitted.

## Acceptance Mapping

- `Gate requirement` is satisfied by `T002` because it validates the prior credibility artifacts before running the audit.
- `Sensitivity requirement` is satisfied by `T003` and `T014` because they define the tiny seed, scenario, and episode-length sensitivity settings.
- `Robustness requirement` is satisfied by `T006` and `T007` because they classify baseline signature stability conservatively.
- `No-policy-redesign requirement` is satisfied by `T008`, `T009`, `T021`, and `T022` because they prohibit policy redesign and require disclaimers that exclude redesign claims.
- `No-training requirement` is satisfied by `T009`, `T010`, and `T011` because they keep the audit out of training foundation work and include the constitution-required integration coverage without adding training.
- `No-paper-validity requirement` is satisfied by `T008`, `T021`, and `T022` because they keep the report diagnostic only and explicitly state the limitation.
