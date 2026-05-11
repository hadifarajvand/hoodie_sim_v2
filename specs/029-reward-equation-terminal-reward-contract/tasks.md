# Tasks: Reward Equation and Terminal Reward Contract

## Phase 1: Setup

- [x] T001 Verify current branch is `029-reward-equation-terminal-reward-contract` and record the branch/base commit state in `specs/029-reward-equation-terminal-reward-contract/quickstart.md`
- [x] T002 Verify the branch base is current `main` after the Feature 028 completion tag and record the comparison result in `specs/029-reward-equation-terminal-reward-contract/research.md`
- [x] T003 Verify dependency files are unchanged before implementation and note the approved scope boundaries in `specs/029-reward-equation-terminal-reward-contract/research.md`
- [x] T004 Verify required source artifacts exist at `resources/papers/hoodie/ocr/merged.tex`, `resources/papers/hoodie/recovered/paper-parameter-registry.json`, `artifacts/analysis/offload-lifecycle-instrumentation/instrumentation-summary.json`, and `artifacts/analysis/computation-delay-cpu-unit-validation/unit-validation-report.json`, then record availability in `specs/029-reward-equation-terminal-reward-contract/research.md`

## Phase 2: Foundational

- [x] T005 Parse and extract the raw OCR text for Eq. (20) from `resources/papers/hoodie/ocr/merged.tex` and capture the exact supporting source location in `specs/029-reward-equation-terminal-reward-contract/research.md`
- [x] T006 Normalize Eq. (20) into structured fields `no_task_case`, `success_case`, `drop_case`, `condition_text`, `C_symbol`, and `Phi_n_t_reference` in `specs/029-reward-equation-terminal-reward-contract/data-model.md`
- [x] T007 Extract and normalize Eq. (21), Eq. (22), and Eq. (23) from `resources/papers/hoodie/ocr/merged.tex`, including OCR-noise notes and source offsets, and store the recovered forms in `specs/029-reward-equation-terminal-reward-contract/research.md`
- [x] T008 Extract and normalize Eq. (24) from `resources/papers/hoodie/ocr/merged.tex`, including the discounted objective and per-agent policy interpretation, and store the recovered form in `specs/029-reward-equation-terminal-reward-contract/research.md`
- [x] T009 Cross-check `C = 40` from `resources/papers/hoodie/recovered/paper-parameter-registry.json` and OCR Table 4 evidence, then record the paper-backed value and provenance in `specs/029-reward-equation-terminal-reward-contract/research.md`
- [x] T010 Extract reward aggregation evidence from `resources/papers/hoodie/ocr/merged.tex` and the recovered registry for cumulative reward, 5000 training episodes, 200 validation episodes, and averaging across distributed HOODIE agents, then record what is artifact-backed versus assumption-backed in `specs/029-reward-equation-terminal-reward-contract/research.md`
- [x] T011 Locate the current reward implementation files in `src/environment/reward_timing.py`, `src/environment/gym_adapter.py`, `src/environment/offload_trace_ledger.py`, and `src/environment/offload_trace_schema.py`, and record the runtime entry points in `specs/029-reward-equation-terminal-reward-contract/research.md`
- [x] T012 Locate the terminal lifecycle and trace-linked reward event code in `src/environment/environment.py`, `src/environment/slot_boundaries.py`, `src/environment/runtime_model.py`, and `src/environment/gym_adapter.py`, then record the terminal-event flow in `specs/029-reward-equation-terminal-reward-contract/research.md`
- [x] T013 Inspect `src/training/delayed_reward_training.py` read-only to classify whether any training-side reward mutation would be required; if so, record it as out-of-scope in `specs/029-reward-equation-terminal-reward-contract/research.md`

## Phase 3: User Story 1 - Recover Reward Contract

**Goal**: Build the paper-backed reward recovery record and the contract schema that preserves evidence, normalization, and classification.

**Independent Test Criteria**: The report can show Eq. (20)-(24), `C = 40`, no-task omission, delayed terminal timing, and aggregation classification without inventing unsupported reward semantics.

- [x] T014 [US1] Create the reward recovery evidence model in `src/analysis/reward_equation_terminal_reward_contract/reward_evidence.py` with normalized fields for equations, source references, confidence, and classification
- [x] T015 [US1] Define the reward contract schema in `specs/029-reward-equation-terminal-reward-contract/data-model.md` for `success_reward_formula`, `drop_penalty_formula`, `no_task_reward_policy`, `delay_cost_formula`, `terminal_timing_policy`, `reward_unit_policy`, `aggregation_policy`, and evidence flags
- [x] T016 [US1] Add the contract/report generator scaffold in `src/analysis/reward_equation_terminal_reward_contract/report.py` and `src/analysis/reward_equation_terminal_reward_contract/runner.py` with deterministic ordering for recovered evidence records
- [x] T017 [US1] Add the reward-contract artifact writers for `artifacts/analysis/reward-equation-terminal-reward-contract/reward-contract-report.json` and `artifacts/analysis/reward-equation-terminal-reward-contract/reward-contract-report.md`
- [x] T018 [US1] Document the reward contract interface in `specs/029-reward-equation-terminal-reward-contract/contracts/reward-contract.md` so the final verdict is derived from evidence, not optimism
- [x] T019 [US1] Add targeted tests in `tests/unit/test_reward_equation_terminal_reward_contract_recovery.py` to assert Eq. (20) normalized fields, Eq. (21)-(24) recovery, `C = 40`, and the paper-backed classification of the recovered terms
- [x] T020 [US1] Add targeted tests in `tests/unit/test_reward_equation_terminal_reward_contract_aggregation.py` to assert that cumulative reward, per-agent averaging, and exact reduction order are classified with the correct evidence status

## Phase 4: User Story 2 - Validate Terminal Reward Timing and Sign

**Goal**: Verify runtime reward emission timing, sign, and trace linkage without changing training logic.

**Independent Test Criteria**: Terminal rewards are emitted only after completion/drop lifecycle events, successful completion is negative delay cost, dropped tasks receive `-C`, and no-task behavior does not pollute numeric aggregation.

- [x] T021 [US2] Map the current runtime reward behavior in `src/environment/gym_adapter.py`, `src/environment/reward_timing.py`, `src/environment/environment.py`, `src/environment/slot_boundaries.py`, and `src/environment/runtime_model.py` into a runtime behavior record in `specs/029-reward-equation-terminal-reward-contract/research.md`
- [x] T022 [US2] Add the runtime contract fields to `specs/029-reward-equation-terminal-reward-contract/data-model.md` for `runtime_audit`, `terminal_timing_contract`, `delay_cost_contract`, `drop_penalty_contract`, and `no_task_reward_contract`
- [x] T023 [US2] If runtime audit proves terminal-only reward emission is violated, add the minimal repair in `src/environment/reward_timing.py` or `src/environment/gym_adapter.py` only, and keep the reward trace linked to the originating task/action
- [x] T024 [US2] Add regression tests in `tests/integration/test_reward_equation_terminal_reward_contract_timing.py` to prove `selected_action` does not emit reward, `reward_emitted` follows `execution_completed` or `dropped_timeout`, and local/private and offloaded/public completion paths share the same terminal reward path
- [x] T025 [US2] Add regression tests in `tests/unit/test_reward_equation_terminal_reward_contract_sign.py` to prove successful completion emits negative delay cost, dropped/thrown tasks emit `-C`, and no-task behavior is omitted or NaN-classified rather than coerced to numeric zero

## Phase 5: User Story 3 - Preserve Honest Reward Boundaries

**Goal**: Keep the report honest about what is paper-backed, runtime-observed, assumption-backed, unrecoverable, and out-of-scope.

**Independent Test Criteria**: The report names unresolved reward semantics honestly, classifies aggregation correctly, and proves no training/dependency drift occurred.

- [x] T026 [US3] Encode the final verdict and evidence classification logic in `src/analysis/reward_equation_terminal_reward_contract/report.py` so the report can emit `paper_matched`, `assumption_backed`, `divergent_runtime_repair_required`, or `blocked_unrecoverable_reward_contract`
- [x] T027 [US3] Add report-generation tests in `tests/integration/test_reward_equation_terminal_reward_contract_report.py` to validate the JSON and Markdown outputs, deterministic ordering, and the required schema fields
- [x] T028 [US3] Add drift-guard tests in `tests/integration/test_reward_equation_terminal_reward_contract_scope_guard.py` to assert no training loop, neural network, TorchRL, Gymnasium, ns-3, ns-3-gym, or dependency files were modified
- [x] T029 [US3] Add validation coverage in `tests/integration/test_reward_equation_terminal_reward_contract_regressions.py` for Features 019, 024, and 026 reward/lifecycle regressions, reusing existing fixture-backed paths only

## Phase 6: Polish & Cross-Cutting Concerns

- [x] T030 Run the feature validation command set with `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python`, including targeted Feature 029 tests, reward/lifecycle regressions, report generation, and JSON parse sanity checks, then record the commands in `specs/029-reward-equation-terminal-reward-contract/quickstart.md`
- [x] T031 Verify the final git diff only touches Feature 029 scoped files, then summarize changed files, generated artifacts, unresolved risks, unrecoverable items, and assumption-backed items in `specs/029-reward-equation-terminal-reward-contract/quickstart.md`

## Dependencies

- T001-T004 must complete before any recovery, audit, or contract work
- T005-T013 must complete before T014-T018 because the contract generator must be grounded in recovered evidence and runtime inspection
- T014-T020 must complete before T026-T027 because the report schema and tests depend on the recovered evidence model
- T021-T025 must complete before T026-T029 because runtime validation and any minimal repair must be proven before final report classification
- T030-T031 are final validation tasks after implementation and test coverage are in place

## Parallel Opportunities

- T005-T010 are ordered recovery tasks and should not be treated as parallel because each normalization step depends on the same OCR evidence block
- T011-T013 are ordered runtime inspections and should not be treated as parallel because they feed the same behavior map
- T019-T020 may be implemented after the evidence model exists, but do not assume they can be developed independently of T014-T018
- T024-T025 may share fixture data, but they still depend on the same runtime timing contract and should only be treated as partially parallel if no shared files are edited concurrently

## Implementation Strategy

1. Recover and normalize the reward equations first.
2. Audit the runtime reward path and terminal trace linkage second.
3. Build the report schema and artifact writers third.
4. Add tests that prove timing, sign, omission, and aggregation classification.
5. Only perform a minimal runtime repair if the audit proves a terminal-only reward violation.
6. Finish with report generation, JSON sanity checks, and diff scope validation.
